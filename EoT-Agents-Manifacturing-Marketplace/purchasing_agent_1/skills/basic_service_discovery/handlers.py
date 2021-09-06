# Copyright (c) 2021 - for information on the respective copyright owner see the NOTICE file and/or the repository https://github.com/boschresearch/open-eot-agents.
#
# SPDX-License-Identifier: Apache-2.0

import pprint
from typing import Optional, cast

from aea.configurations.base import PublicId
from aea.crypto.ledger_apis import LedgerApis
from aea.protocols.base import Message
from aea.skills.base import Handler

from packages.fetchai.connections.ledger.base import (
    CONNECTION_ID as LEDGER_CONNECTION_PUBLIC_ID,
)
from packages.fetchai.protocols.default.message import DefaultMessage
from packages.fetchai.protocols.ledger_api.message import LedgerApiMessage
from packages.fetchai.protocols.contract_api.message import ContractApiMessage
from packages.bosch.skills.basic_service_discovery.dialogues import (
    DefaultDialogues,
    LedgerApiDialogue,
    LedgerApiDialogues,
    ContractApiDialogue,
    ContractApiDialogues,
)
from packages.bosch.skills.basic_service_discovery.strategy import GenericStrategy


LEDGER_API_ADDRESS = str(LEDGER_CONNECTION_PUBLIC_ID)


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
        strategy = cast(GenericStrategy, self.context.strategy)
        if ledger_api_msg.balance > 0:
            self.context.logger.info(
                "starting balance on {} ledger={}.".format(
                    strategy.ledger_id, ledger_api_msg.balance,
                )
            )
            strategy.balance = ledger_api_msg.balance
            strategy.is_searching = True
        else:
            self.context.logger.warning(
                f"you have no starting balance on {strategy.ledger_id} ledger! Stopping skill {self.skill_id}."
            )
            self.context.is_active = False

    def _handle_error(
        self, ledger_api_msg: LedgerApiMessage, ledger_api_dialogue: LedgerApiDialogue
    ) -> None:
        """
        Handle a message of error performative.

        :param ledger_api_message: the ledger api message
        :param ledger_api_dialogue: the ledger api dialogue
        """
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
        if contract_api_msg.performative is ContractApiMessage.Performative.STATE:
            self._handle_state(contract_api_msg, contract_api_dialogue)
        elif contract_api_msg.performative is ContractApiMessage.Performative.ERROR:
            self._handle_error(contract_api_msg, contract_api_dialogue)
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

    def _handle_state(
        self,
        contract_api_msg: ContractApiMessage,
        contract_api_dialogue: ContractApiDialogue,
    ) -> None:
        """
        Handle a message of get_raw_message performative.

        :param contract_api_message: the contract api message
        :param contract_api_dialogue: the contract api dialogue
        """
        strategy = cast(GenericStrategy, self.context.strategy)
        self.context.logger.info("received state={}".format(contract_api_msg))
        #TODO: define better data structure with services and endpoints! 
        if (len(contract_api_msg.state.body['topic']["3D_printing_service"]) == 0):
            self.context.logger.info("No endpoints found for requested services, continue searching...")  
            strategy.is_searching = True
        else:
            strategy.is_searching = False
            selling_agent_address = contract_api_msg.state.body['topic']["3D_printing_service"][0]
            self.context.logger.info("found agents={}.".format(selling_agent_address))              
            #TODO: Fipa negotiation starts here: send fipa CFP message to agents with selling_agent_address ...

    def _handle_error(
        self,
        contract_api_msg: ContractApiMessage,
        contract_api_dialogue: ContractApiDialogue,
    ) -> None:
        """
        Handle a message of error performative.

        :param contract_api_message: the contract api message
        :param contract_api_dialogue: the contract api dialogue
        """
        self.context.logger.info(
            "received ledger_api error message={} in dialogue={}.".format(
                contract_api_msg, contract_api_dialogue
            )
        )

    # def _handle_state(
    #     self,
    #     contract_api_msg: ContractApiMessage,
    #     contract_api_dialogue: ContractApiDialogue,
    # ) -> None:
    #     """
    #     Handle a message of STATE performative.
    #     Check if requested topic is supported by strategy - send CFT.

    #     :param contract_api_message: the ledger api message
    #     :param contract_api_dialogue: the ledger api dialogue
    #     """
    #     self.context.logger.info(
    #         "received ledger_api state message={} in dialogue={}.".format(
    #             contract_api_msg, contract_api_dialogue
    #         )
    #     )
    #     topics = contract_api_msg.state.body['topic']
    #     quoting_dialogues = cast(StandardQuotingDialogues, self.context.quoting_dialogues)
    #     for topic in self.strategy.supportedTopics:
    #         if topic in topics:
    #             consumer_agent_address = contract_api_msg.state.body['topic'][topic][0]
    #             self.context.logger.info(
    #             "sending CFT to agent={}".format(consumer_agent_address)
    #             )
    #             cft_msg, _ = quoting_dialogues.create(
    #                 counterparty=consumer_agent_address,
    #                 performative=StandardQuotingMessage.Performative.CFT
    #             )
    #             self.context.outbox.put_message(message=cft_msg)
            
    def _handle_invalid(
        self,
        contract_api_msg: ContractApiMessage,
        contract_api_dialogue: ContractApiDialogue,
    ) -> None:
        """
        Handle a message of invalid performative.

        :param contract_api_message: the contract api message
        :param contract_api_dialogue: the contract api dialogue
        """
        self.context.logger.warning(
            "cannot handle contract_api message of performative={} in dialogue={}.".format(
                contract_api_msg.performative, contract_api_dialogue,
            )
        )