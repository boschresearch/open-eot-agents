# Copyright (c) 2021 - for information on the respective copyright owner see the NOTICE file and/or the repository https://github.com/boschresearch/open-eot-agents.
#
# SPDX-License-Identifier: Apache-2.0

from typing import Optional, cast

from aea.configurations.base import PublicId
from aea.crypto.ledger_apis import LedgerApis
from aea.helpers.transaction.base import TransactionDigest
from aea.protocols.base import Message
from aea.skills.base import Handler

from packages.fetchai.connections.ledger.base import (
    CONNECTION_ID as LEDGER_CONNECTION_PUBLIC_ID,
)
from packages.fetchai.protocols.default.message import DefaultMessage
from packages.fetchai.protocols.fipa.message import FipaMessage
from packages.fetchai.protocols.ledger_api.message import LedgerApiMessage
from packages.fetchai.protocols.contract_api.message import ContractApiMessage
from packages.fetchai.protocols.signing.message import SigningMessage
from packages.bosch.skills.fipa_negotiation.dialogues import (
    DefaultDialogues,
    FipaDialogue,
    FipaDialogues,
    LedgerApiDialogue,
    LedgerApiDialogues,
    ContractApiDialogue,
    ContractApiDialogues,
    SigningDialogue,
    SigningDialogues,
)
from packages.bosch.skills.fipa_negotiation.strategy import GenericStrategy


LEDGER_API_ADDRESS = str(LEDGER_CONNECTION_PUBLIC_ID)


class GenericFipaHandler(Handler):
    """This class implements a FIPA handler."""

    SUPPORTED_PROTOCOL = FipaMessage.protocol_id  # type: Optional[PublicId]

    def setup(self) -> None:
        """Implement the setup for the handler."""

    def handle(self, message: Message) -> None:
        """
        Implement the reaction to a message.

        :param message: the message
        :return: None
        """
        fipa_msg = cast(FipaMessage, message)

        # recover dialogue
        fipa_dialogues = cast(FipaDialogues, self.context.fipa_dialogues)
        fipa_dialogue = cast(FipaDialogue, fipa_dialogues.update(fipa_msg))
        if fipa_dialogue is None:
            self._handle_unidentified_dialogue(fipa_msg)
            return

        # handle message
        if fipa_msg.performative == FipaMessage.Performative.CFP:
            self._handle_cfp(fipa_msg, fipa_dialogue)
        elif fipa_msg.performative == FipaMessage.Performative.DECLINE:
            self._handle_decline(fipa_msg, fipa_dialogue, fipa_dialogues)
        elif fipa_msg.performative == FipaMessage.Performative.ACCEPT:
            self._handle_accept(fipa_msg, fipa_dialogue)
        elif fipa_msg.performative == FipaMessage.Performative.INFORM:
            self._handle_inform(fipa_msg, fipa_dialogue)
        else:
            self._handle_invalid(fipa_msg, fipa_dialogue)

    def teardown(self) -> None:
        """
        Implement the handler teardown.

        :return: None
        """
    def _handle_unidentified_dialogue(self, fipa_msg: FipaMessage) -> None:
        """
        Handle an unidentified dialogue.

        :param fipa_msg: the message
        """
        self.context.logger.info(
            "received invalid fipa message={}, unidentified dialogue.".format(fipa_msg)
        )
        default_dialogues = cast(DefaultDialogues, self.context.default_dialogues)
        default_msg, _ = default_dialogues.create(
            counterparty=fipa_msg.sender,
            performative=DefaultMessage.Performative.ERROR,
            error_code=DefaultMessage.ErrorCode.INVALID_DIALOGUE,
            error_msg="Invalid dialogue.",
            error_data={"fipa_message": fipa_msg.encode()},
        )
        self.context.outbox.put_message(message=default_msg)
        
    def _handle_cfp(self, fipa_msg: FipaMessage, fipa_dialogue: FipaDialogue) -> None:
        """
        Handle the CFP.

        If the CFP matches the supplied services then send a PROPOSE, otherwise send a DECLINE.

        :param fipa_msg: the message
        :param fipa_dialogue: the dialogue object
        :return: None
        """
        self.context.logger.info(
            "received CFP from sender={}".format(fipa_msg.sender[-5:])
        )
        strategy = cast(GenericStrategy, self.context.strategy)
        if strategy.is_matching_supply(fipa_msg.query):
            proposal, terms, data_for_sale = strategy.generate_proposal_terms_and_data(
                fipa_msg.query, fipa_msg.sender
            )
            fipa_dialogue.data_for_sale = data_for_sale
            fipa_dialogue.terms = terms
            self.context.logger.info(
                "sending a PROPOSE with proposal={} to sender={}".format(
                    proposal.values, fipa_msg.sender[-5:]
                )
            )
            proposal_msg = fipa_dialogue.reply(
                performative=FipaMessage.Performative.PROPOSE,
                target_message=fipa_msg,
                proposal=proposal,
            )
            self.context.outbox.put_message(message=proposal_msg)
        else:
            self.context.logger.info(
                "declined the CFP from sender={}".format(fipa_msg.sender[-5:])
            )
            decline_msg = fipa_dialogue.reply(
                performative=FipaMessage.Performative.DECLINE, target_message=fipa_msg,
            )
            self.context.outbox.put_message(message=decline_msg)
        
    def _handle_decline(
        self,
        fipa_msg: FipaMessage,
        fipa_dialogue: FipaDialogue,
        fipa_dialogues: FipaDialogues,
    ) -> None:
        """
        Handle the DECLINE.

        Close the dialogue.

        :param fipa_msg: the message
        :param fipa_dialogue: the dialogue object
        :return: None
        """
        self.context.logger.info(
            "received DECLINE from sender={}".format(fipa_msg.sender[-5:])
        )
        fipa_dialogues.dialogue_stats.add_dialogue_endstate(
            FipaDialogue.EndState.DECLINED_PROPOSE, fipa_dialogue.is_self_initiated
        )
    
    def _handle_accept(
        self, fipa_msg: FipaMessage, fipa_dialogue: FipaDialogue
    ) -> None:
        """
        Handle the ACCEPT.

        Respond with a MATCH_ACCEPT_W_INFORM which contains the address to send the funds to.

        :param fipa_msg: the message
        :param fipa_dialogue: the dialogue object
        :return: None
        """
        self.context.logger.info(
            "received ACCEPT from sender={}".format(fipa_msg.sender[-5:])
        )
        info = {"address": fipa_dialogue.terms.sender_address}
        match_accept_msg = fipa_dialogue.reply(
            performative=FipaMessage.Performative.MATCH_ACCEPT_W_INFORM,
            target_message=fipa_msg,
            info=info,
        )
        self.context.logger.info(
            "sending MATCH_ACCEPT_W_INFORM to sender={} with info={}".format(
                fipa_msg.sender[-5:], info,
            )
        )
        self.context.outbox.put_message(message=match_accept_msg)
    
    def _handle_inform(
        self, fipa_msg: FipaMessage, fipa_dialogue: FipaDialogue
    ) -> None:
        """
        Handle the INFORM.

        If the INFORM message contains the transaction_digest then verify that it is settled, otherwise do nothing.
        If the transaction is settled, send the data, otherwise do nothing.

        :param fipa_msg: the message
        :param fipa_dialogue: the dialogue object
        :return: None
        """
        self.context.logger.info(
            "received INFORM from sender={}".format(fipa_msg.sender[-5:])
        )

        strategy = cast(GenericStrategy, self.context.strategy)
        if strategy.is_ledger_tx and "transaction_digest" in fipa_msg.info.keys():
            self.context.logger.info(
                "checking whether transaction={} has been received ...".format(
                    fipa_msg.info["transaction_digest"]
                )
            )
            ledger_api_dialogues = cast(
                LedgerApiDialogues, self.context.ledger_api_dialogues
            )
            ledger_api_msg, ledger_api_dialogue = ledger_api_dialogues.create(
                counterparty=LEDGER_API_ADDRESS,
                performative=LedgerApiMessage.Performative.GET_TRANSACTION_RECEIPT,
                transaction_digest=TransactionDigest(
                    fipa_dialogue.terms.ledger_id, fipa_msg.info["transaction_digest"]
                ),
            )
            ledger_api_dialogue = cast(LedgerApiDialogue, ledger_api_dialogue)
            ledger_api_dialogue.associated_fipa_dialogue = fipa_dialogue
            self.context.outbox.put_message(message=ledger_api_msg)
        elif strategy.is_ledger_tx:
            self.context.logger.warning(
                "did not receive transaction digest from sender={}.".format(
                    fipa_msg.sender[-5:]
                )
            )
        elif not strategy.is_ledger_tx and "Done" in fipa_msg.info.keys():
            inform_msg = fipa_dialogue.reply(
                performative=FipaMessage.Performative.INFORM,
                target_message=fipa_msg,
                info=fipa_dialogue.data_for_sale,
            )
            self.context.outbox.put_message(message=inform_msg)
            fipa_dialogues = cast(FipaDialogues, self.context.fipa_dialogues)
            fipa_dialogues.dialogue_stats.add_dialogue_endstate(
                FipaDialogue.EndState.SUCCESSFUL, fipa_dialogue.is_self_initiated
            )
            self.context.logger.info(
                "transaction confirmed, sending data={} to buyer={}.".format(
                    fipa_dialogue.data_for_sale, fipa_msg.sender[-5:],
                )
            )
        else:
            self.context.logger.warning(
                "did not receive transaction confirmation from sender={}.".format(
                    fipa_msg.sender[-5:]
                )
            )
    
    def _handle_invalid(
        self, fipa_msg: FipaMessage, fipa_dialogue: FipaDialogue
    ) -> None:
        """
        Handle a fipa message of invalid performative.

        :param fipa_msg: the message
        :param fipa_dialogue: the dialogue object
        :return: None
        """
        self.context.logger.warning(
            "cannot handle fipa message of performative={} in dialogue={}.".format(
                fipa_msg.performative, fipa_dialogue
            )
        )


class GenericLedgerApiHandler(Handler):
    """Implement the ledger handler."""

    SUPPORTED_PROTOCOL = LedgerApiMessage.protocol_id  # type: Optional[PublicId]

    def setup(self) -> None:
        """Implement the setup for the handler."""

    def handle(self, message: Message) -> None:
        """
        Implement the reaction to a message.

        :param message: the message
        :return: None
        """
        ledger_api_msg = cast(LedgerApiMessage, message)

        # recover dialogue
        ledger_api_dialogues = cast(
            LedgerApiDialogues, self.context.ledger_api_dialogues
        )
        ledger_api_dialogue = cast(
            Optional[LedgerApiDialogue], ledger_api_dialogues.update(ledger_api_msg)
        )
        if ledger_api_dialogue is None:
            self._handle_unidentified_dialogue(ledger_api_msg)
            return

        # handle message
        if ledger_api_msg.performative is LedgerApiMessage.Performative.BALANCE:
            self._handle_balance(ledger_api_msg)
        elif ledger_api_msg.performative is LedgerApiMessage.Performative.TRANSACTION_DIGEST:
            self._handle_transaction_digest(ledger_api_msg)    
        elif ledger_api_msg.performative is LedgerApiMessage.Performative.TRANSACTION_RECEIPT:
            self._handle_transaction_receipt(ledger_api_msg, ledger_api_dialogue)
        elif ledger_api_msg.performative == LedgerApiMessage.Performative.ERROR:
            self._handle_error(ledger_api_msg, ledger_api_dialogue)
        else:
            self._handle_invalid(ledger_api_msg, ledger_api_dialogue)

    def teardown(self) -> None:
        """
        Implement the handler teardown.

        :return: None
        """

    def _handle_unidentified_dialogue(self, ledger_api_msg: LedgerApiMessage) -> None:
        """
        Handle an unidentified dialogue.

        :param msg: the message
        """
        self.context.logger.info(
            "received invalid ledger_api message={}, unidentified dialogue.".format(
                ledger_api_msg
            )
        )

    def _handle_balance(self, ledger_api_msg: LedgerApiMessage) -> None:
        """
        Handle a message of balance performative.

        :param ledger_api_message: the ledger api message
        """
        self.context.logger.info(
            "starting balance on {} ledger={}.".format(
                ledger_api_msg.ledger_id, ledger_api_msg.balance,
            )
        )

    def _handle_transaction_digest(self, ledger_api_msg: LedgerApiMessage) -> None:
        """
        Handle a message of transaction_digest performative.

        :param ledger_api_message: the ledger api message
        """
        #TODO: Error while trying to retriebe the ledger_id: ledger_id is not set while included within message! 
        self.context.logger.info("received transaction_digest from {}.".format(ledger_api_msg.sender))

    def _handle_transaction_receipt(
        self, ledger_api_msg: LedgerApiMessage, ledger_api_dialogue: LedgerApiDialogue
    ) -> None:
        """
        Handle a message of balance performative.

        :param ledger_api_message: the ledger api message
        :param ledger_api_dialogue: the ledger api dialogue
        """
        fipa_dialogue = ledger_api_dialogue.associated_fipa_dialogue
        is_settled = LedgerApis.is_transaction_settled(
            fipa_dialogue.terms.ledger_id, ledger_api_msg.transaction_receipt.receipt
        )
        is_valid = LedgerApis.is_transaction_valid(
            fipa_dialogue.terms.ledger_id,
            ledger_api_msg.transaction_receipt.transaction,
            fipa_dialogue.terms.sender_address,
            fipa_dialogue.terms.counterparty_address,
            fipa_dialogue.terms.nonce,
            fipa_dialogue.terms.counterparty_payable_amount,
        )
        if is_settled and is_valid:
            last_message = cast(
                Optional[FipaMessage], fipa_dialogue.last_incoming_message
            )
            if last_message is None:
                raise ValueError("Cannot retrieve last fipa message.")
            inform_msg = fipa_dialogue.reply(
                performative=FipaMessage.Performative.INFORM,
                target_message=last_message,
                info=fipa_dialogue.data_for_sale,
            )
            self.context.outbox.put_message(message=inform_msg)
            fipa_dialogues = cast(FipaDialogues, self.context.fipa_dialogues)
            fipa_dialogues.dialogue_stats.add_dialogue_endstate(
                FipaDialogue.EndState.SUCCESSFUL, fipa_dialogue.is_self_initiated
            )
            self.context.logger.info(
                "transaction confirmed, sending data={} to buyer={}.".format(
                    fipa_dialogue.data_for_sale, last_message.sender[-5:],
                )
            )
        else:
            self.context.logger.info(
                "transaction_receipt={} not settled or not valid, aborting".format(
                    ledger_api_msg.transaction_receipt
                )
            )

    def _handle_error(
        self, ledger_api_msg: LedgerApiMessage, ledger_api_dialogue: LedgerApiDialogue
    ) -> None:
        """
        Handle a message of error performative.

        :param ledger_api_message: the ledger api message
        :param ledger_api_dialogue: the ledger api dialogue
        """
        self.context.logger.info(
            "received ledger_api error message={} in dialogue={}.".format(
                ledger_api_msg, ledger_api_dialogue
            )
        )

    def _handle_invalid(
        self, ledger_api_msg: LedgerApiMessage, ledger_api_dialogue: LedgerApiDialogue
    ) -> None:
        """
        Handle a message of invalid performative.

        :param ledger_api_message: the ledger api message
        :param ledger_api_dialogue: the ledger api dialogue
        """
        self.context.logger.warning(
            "cannot handle ledger_api message of performative={} in dialogue={}.".format(
                ledger_api_msg.performative, ledger_api_dialogue,
            )
        )


class ContractApiHandler(Handler):
    """Implement the contract api handler."""

    SUPPORTED_PROTOCOL = ContractApiMessage.protocol_id  # type: Optional[PublicId]

    def setup(self) -> None:
        """Implement the setup for the handler."""
        #uncomment following statement only if strategy object is used here!
        #self.strategy = cast(GenericStrategy, self.context.strategy)

    def handle(self, message: Message) -> None:
        """
        Implement the reaction to a message.

        :param message: the message
        :return: None
        """
        contract_api_msg = cast(ContractApiMessage, message)

        # recover dialogue
        contract_api_dialogues = cast(
            ContractApiDialogues, self.context.contract_api_dialogues
        )
        contract_api_dialogue = cast(
            Optional[ContractApiDialogue],
            contract_api_dialogues.update(contract_api_msg),
        )
        if contract_api_dialogue is None:
            self._handle_unidentified_dialogue(contract_api_msg)
            return

        # handle message
        if (contract_api_msg.performative is ContractApiMessage.Performative.RAW_TRANSACTION):
            self._handle_raw_transaction(contract_api_msg, contract_api_dialogue)
        elif contract_api_msg.performative == ContractApiMessage.Performative.ERROR:
            self._handle_error(contract_api_msg, contract_api_dialogue)
        #elif contract_api_msg.performative == ContractApiMessage.Performative.STATE:
        #    self._handle_state(contract_api_msg, contract_api_dialogue)
        else:
            self._handle_invalid(contract_api_msg, contract_api_dialogue)

    def teardown(self) -> None:
        """
        Implement the handler teardown.

        :return: None
        """
        pass

    def _handle_unidentified_dialogue(
        self, contract_api_msg: ContractApiMessage
    ) -> None:
        """
        Handle an unidentified dialogue.

        :param msg: the message
        """
        self.context.logger.info(
            "received invalid contract_api message={}, unidentified dialogue.".format(
                contract_api_msg
            )
        )

    def _handle_raw_transaction(
        self,
        contract_api_msg: ContractApiMessage,
        contract_api_dialogue: ContractApiDialogue,
    ) -> None:
        """
        Handle a message of get_raw_transaction performative.

        :param contract_api_message: the ledger api message
        :param contract_api_dialogue: the ledger api dialogue
        """
        self.context.logger.info("received raw transaction={}".format(contract_api_msg))
        signing_dialogues = cast(SigningDialogues, self.context.signing_dialogues)
        signing_msg, signing_dialogue = signing_dialogues.create(
            counterparty=self.context.decision_maker_address,
            performative=SigningMessage.Performative.SIGN_TRANSACTION,
            raw_transaction=contract_api_msg.raw_transaction,
            terms=contract_api_dialogue.terms,
        )
        signing_dialogue = cast(SigningDialogue, signing_dialogue)
        signing_dialogue.associated_contract_api_dialogue = contract_api_dialogue
        self.context.decision_maker_message_queue.put_nowait(signing_msg)
        self.context.logger.info(
            "proposing the transaction to the decision maker. Waiting for confirmation ..."
        )

    def _handle_error(
        self,
        contract_api_msg: ContractApiMessage,
        contract_api_dialogue: ContractApiDialogue,
    ) -> None:
        """
        Handle a message of error performative.

        :param contract_api_message: the ledger api message
        :param contract_api_dialogue: the ledger api dialogue
        """
        self.context.logger.info(
            "received ledger_api error message={} in dialogue={}.".format(
                contract_api_msg, contract_api_dialogue
            )
        )
            
    def _handle_invalid(
        self,
        contract_api_msg: ContractApiMessage,
        contract_api_dialogue: ContractApiDialogue,
    ) -> None:
        """
        Handle a message of invalid performative.

        :param contract_api_message: the ledger api message
        :param contract_api_dialogue: the ledger api dialogue
        """
        self.context.logger.warning(
            "cannot handle contract_api message of performative={} in dialogue={}.".format(
                contract_api_msg.performative, contract_api_dialogue,
            )
        )


class SigningHandler(Handler):
    """Implement the transaction handler."""

    SUPPORTED_PROTOCOL = SigningMessage.protocol_id  # type: Optional[PublicId]

    def setup(self) -> None:
        """Implement the setup for the signing handler."""
        pass

    def handle(self, message: Message) -> None:
        """
        Implement the reaction to a message.

        :param message: the message
        :return: None
        """
        signing_msg = cast(SigningMessage, message)

        # recover dialogue
        signing_dialogues = cast(SigningDialogues, self.context.signing_dialogues)
        signing_dialogue = cast(
            Optional[SigningDialogue], signing_dialogues.update(signing_msg)
        )
        if signing_dialogue is None:
            self._handle_unidentified_dialogue(signing_msg)
            return

        # handle message
        if signing_msg.performative is SigningMessage.Performative.SIGNED_TRANSACTION:
            self._handle_signed_transaction(signing_msg, signing_dialogue)
        elif signing_msg.performative is SigningMessage.Performative.ERROR:
            self._handle_error(signing_msg, signing_dialogue)
        else:
            self._handle_invalid(signing_msg, signing_dialogue)

    def teardown(self) -> None:
        """
        Implement the signing handler teardown.

        :return: None
        """
        pass

    def _handle_unidentified_dialogue(self, signing_msg: SigningMessage) -> None:
        """
        Handle an unidentified dialogue.

        :param msg: the message
        """
        self.context.logger.info(
            "received invalid signing message={}, unidentified dialogue.".format(
                signing_msg
            )
        )

    def _handle_signed_transaction(
        self, signing_msg: SigningMessage, signing_dialogue: SigningDialogue
    ) -> None:
        """
        Handle a signed transaction message.

        :param signing_msg: the signing message
        :param signing_dialogue: the dialogue
        :return: None
        """
        self.context.logger.info("transaction signing was successful.")
        ledger_api_dialogues = cast(
            LedgerApiDialogues, self.context.ledger_api_dialogues
        )
        ledger_api_msg, ledger_api_dialogue = ledger_api_dialogues.create(
            counterparty=LEDGER_API_ADDRESS,
            performative=LedgerApiMessage.Performative.SEND_SIGNED_TRANSACTION,
            signed_transaction=signing_msg.signed_transaction,
        )
        ledger_api_dialogue = cast(LedgerApiDialogue, ledger_api_dialogue)
        ledger_api_dialogue.associated_signing_dialogue = signing_dialogue
        self.context.outbox.put_message(message=ledger_api_msg)
        self.context.logger.info("sending transaction to ledger.")

    def _handle_error(
        self, signing_msg: SigningMessage, signing_dialogue: SigningDialogue
    ) -> None:
        """
        Handle an error message.

        :param signing_msg: the signing message
        :param signing_dialogue: the dialogue
        :return: None
        """
        self.context.logger.info(
            "transaction signing was not successful. Error_code={} in dialogue={}".format(
                signing_msg.error_code, signing_dialogue
            )
        )

    def _handle_invalid(
        self, signing_msg: SigningMessage, signing_dialogue: SigningDialogue
    ) -> None:
        """
        Handle an invalid message.

        :param signing_msg: the signing message
        :param signing_dialogue: the dialogue
        :return: None
        """
        self.context.logger.warning(
            "cannot handle signing message of performative={} in dialogue={}.".format(
                signing_msg.performative, signing_dialogue
            )
        )




