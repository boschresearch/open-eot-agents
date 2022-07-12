# Copyright (c) 2021 - for information on the respective copyright owner see the NOTICE file and/or the repository https://github.com/boschresearch/open-eot-agents.
#
# SPDX-License-Identifier: Apache-2.0

from typing import Any, List, Optional, Set, cast

from aea.protocols.dialogue.base import DialogueLabel
from aea.skills.behaviours import TickerBehaviour

from packages.fetchai.connections.ledger.base import (
    CONNECTION_ID as LEDGER_CONNECTION_PUBLIC_ID,
)
from packages.fetchai.protocols.ledger_api.message import LedgerApiMessage
from packages.fetchai.protocols.contract_api.message import ContractApiMessage
from packages.bosch.skills.fipa_negotiation_purchasing.dialogues import (
    FipaDialogue,
    LedgerApiDialogue,
    LedgerApiDialogues,
    ContractApiDialogues,
)
from packages.bosch.skills.fipa_negotiation_purchasing.strategy import GenericStrategy


DEFAULT_MAX_PROCESSING = 120
DEFAULT_TX_INTERVAL = 2.0
DEFAULT_SEARCH_INTERVAL = 5.0
LEDGER_API_ADDRESS = str(LEDGER_CONNECTION_PUBLIC_ID)


class GenericSearchBehaviour(TickerBehaviour):
    """This class implements a search behaviour."""

    def __init__(self, **kwargs: Any):
        """Initialize the search behaviour."""
        search_interval = cast(
            float, kwargs.pop("search_interval", DEFAULT_SEARCH_INTERVAL)
        )
        super().__init__(tick_interval=search_interval, **kwargs)

    def setup(self) -> None:
        """Implement the setup for the behaviour."""
        strategy = cast(GenericStrategy, self.context.strategy)
        if strategy.is_ledger_tx:
            ledger_api_dialogues = cast(
                LedgerApiDialogues, self.context.ledger_api_dialogues
            )
            ledger_api_msg, _ = ledger_api_dialogues.create(
                counterparty=LEDGER_API_ADDRESS,
                performative=LedgerApiMessage.Performative.GET_BALANCE,
                ledger_id=strategy.ledger_id,
                address=cast(str, self.context.agent_addresses.get(strategy.ledger_id)),
            )
            self.context.outbox.put_message(message=ledger_api_msg)

    def act(self) -> None:
        """
        Implement the act.

        :return: None
        """
        strategy = cast(GenericStrategy, self.context.strategy)
        if strategy.is_searching:
            self._get_services_endpoints()

    def teardown(self) -> None:
        """
        Implement the task teardown.

        :return: None
        """

    def _get_services_endpoints(self) -> None:
        """
        Gets service endpoints from service directory contract.

        :return: a list of endpoints
        """
        strategy = cast(GenericStrategy, self.context.strategy)
        # TODO: change smart contract to allow for getting the endpoints of all requested services!
        services = strategy.get_services()
        # TODO: remove the following line after fixing the issue above!
        service = services["search_service_1"]
        if strategy.is_ledger_tx:
            contract_api_dialogues = cast(
                ContractApiDialogues, self.context.contract_api_dialogues
            )
            contract_api_msg, contract_api_dialogue = contract_api_dialogues.create(
                counterparty=LEDGER_API_ADDRESS,
                # TODO: tried to use GET_RAW_MESSAGE instead but it turns out to be difficult
                # as it expects a byte string as return value by the contract
                performative=ContractApiMessage.Performative.GET_STATE,
                ledger_id=strategy.ledger_id,
                contract_id=strategy.contract_id,
                contract_address=strategy.contract_address,
                callable="getServiceEndpoints",  # TODO: should be named to getServicesEndpoints within contract.py and solidity code!
                kwargs=ContractApiMessage.Kwargs(
                    {
                        "deployer_address": self.context.agent_address,  # TODO: should be set to a third party deployer address!
                        "topic": service,  # TODO: should be changed to "topics: services"
                    }
                )
            )
            # TODO: the following line is only used for testing issues!
            print(contract_api_msg)
            contract_api_dialogue.terms = strategy.get_contract_terms()
            self.context.outbox.put_message(message=contract_api_msg)
            self.context.logger.info("Getting service endpoints from contract...")


class GenericTransactionBehaviour(TickerBehaviour):
    """A behaviour to sequentially submit transactions to the blockchain."""

    def __init__(self, **kwargs: Any):
        """Initialize the transaction behaviour."""
        tx_interval = cast(
            float, kwargs.pop("transaction_interval", DEFAULT_TX_INTERVAL)
        )
        self.max_processing = cast(
            float, kwargs.pop("max_processing", DEFAULT_MAX_PROCESSING)
        )
        self.processing_time = 0.0
        self.waiting: List[FipaDialogue] = []
        self.processing: Optional[LedgerApiDialogue] = None
        self.timedout: Set[DialogueLabel] = set()
        super().__init__(tick_interval=tx_interval, **kwargs)

    def setup(self) -> None:
        """Setup behaviour."""

    def act(self) -> None:
        """
        Implement the act.

        :return: None
        """
        if self.processing is not None:
            if self.processing_time <= self.max_processing:
                # already processing
                self.processing_time += self.tick_interval
                return
            self._timeout_processing()
        if len(self.waiting) == 0:
            # nothing to process
            return
        self._start_processing()

    def _start_processing(self) -> None:
        """Process the next transaction."""
        fipa_dialogue = self.waiting.pop(0)
        self.context.logger.info(
            f"Processing transaction, {len(self.waiting)} transactions remaining"
        )
        ledger_api_dialogues = cast(
            LedgerApiDialogues, self.context.ledger_api_dialogues
        )
        ledger_api_msg, ledger_api_dialogue = ledger_api_dialogues.create(
            counterparty=LEDGER_API_ADDRESS,
            performative=LedgerApiMessage.Performative.GET_RAW_TRANSACTION,
            terms=fipa_dialogue.terms,
        )
        ledger_api_dialogue = cast(LedgerApiDialogue, ledger_api_dialogue)
        ledger_api_dialogue.associated_fipa_dialogue = fipa_dialogue
        self.processing_time = 0.0
        self.processing = ledger_api_dialogue
        self.context.logger.info(
            f"requesting transfer transaction from ledger api for message={ledger_api_msg}..."
        )
        self.context.outbox.put_message(message=ledger_api_msg)

    def teardown(self) -> None:
        """Teardown behaviour."""

    def _timeout_processing(self) -> None:
        """Timeout processing."""
        if self.processing is None:
            return
        self.timedout.add(self.processing.dialogue_label)
        self.waiting.append(self.processing.associated_fipa_dialogue)
        self.processing_time = 0.0
        self.processing = None

    def finish_processing(self, ledger_api_dialogue: LedgerApiDialogue) -> None:
        """
        Finish processing.

        :param ledger_api_dialogue: the ledger api dialogue
        """
        if self.processing == ledger_api_dialogue:
            self.processing_time = 0.0
            self.processing = None
            return
        if ledger_api_dialogue.dialogue_label not in self.timedout:
            raise ValueError(
                f"Non-matching dialogues in transaction behaviour: {self.processing} and {ledger_api_dialogue}"
            )
        self.timedout.remove(ledger_api_dialogue.dialogue_label)
        self.context.logger.debug(
            f"Timeout dialogue in transaction processing: {ledger_api_dialogue}"
        )
        # don't reset, as another might be processing

    def failed_processing(self, ledger_api_dialogue: LedgerApiDialogue) -> None:
        """
        Failed processing.

        Currently, we retry processing indefinitely.

        :param ledger_api_dialogue: the ledger api dialogue
        """
        self.finish_processing(ledger_api_dialogue)
        self.waiting.append(ledger_api_dialogue.associated_fipa_dialogue)
