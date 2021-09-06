# Copyright (c) 2021 - for information on the respective copyright owner see the NOTICE file and/or the repository https://github.com/boschresearch/open-eot-agents.
#
# SPDX-License-Identifier: Apache-2.0

from typing import Any, cast

from aea.skills.behaviours import TickerBehaviour

from packages.fetchai.connections.ledger.base import (
    CONNECTION_ID as LEDGER_CONNECTION_PUBLIC_ID,
)
from packages.fetchai.protocols.ledger_api.message import LedgerApiMessage
from packages.fetchai.protocols.contract_api.message import ContractApiMessage
from packages.bosch.skills.fipa_negotiation.dialogues import (
    LedgerApiDialogues,
    ContractApiDialogues,
)
from packages.bosch.skills.fipa_negotiation.strategy import GenericStrategy


DEFAULT_SERVICES_INTERVAL = 60.0
LEDGER_API_ADDRESS = str(LEDGER_CONNECTION_PUBLIC_ID)


class GenericServiceRegistrationBehaviour(TickerBehaviour):
    """This class implements a behaviour."""

    def __init__(self, **kwargs: Any):
        """Initialise the behaviour."""
        services_interval = kwargs.pop(
            "services_interval", DEFAULT_SERVICES_INTERVAL
        )  # type: int
        super().__init__(tick_interval=services_interval, **kwargs)
        
    def setup(self) -> None:
        """
        Implement the setup.

        :return: None
        """
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
        self._add_services()
        #TODO: the fllowing line should be removed from here as used only for testing issues!
        #self._remove_services()
        
    def act(self) -> None:
        """
        Implement the act.

        :return: None
        """

    def teardown(self) -> None:
        """
        Implement the task teardown.

        :return: None
        """
        #TODO: should be discussed with fetchai:
        #Figure out where to call remove_services()! 
        #cannot call remove services here as agent is down before handling message interaction!
        #self._remove_services()

    def _add_services(self) -> None:
        """
        Adds a service provided by the agent to a service directory contract.

        :return: None
        """
        strategy = cast(GenericStrategy, self.context.strategy)
        services = strategy.get_services()
        if strategy.is_ledger_tx:
            contract_api_dialogues = cast(
                ContractApiDialogues, self.context.contract_api_dialogues
            )
            contract_api_msg, contract_api_dialogue = contract_api_dialogues.create(
                counterparty=LEDGER_API_ADDRESS,
                performative=ContractApiMessage.Performative.GET_RAW_TRANSACTION,
                ledger_id=strategy.ledger_id,
                contract_id=strategy.contract_id,
                contract_address=strategy.contract_address,
                callable="addServices",
                kwargs=ContractApiMessage.Kwargs(
                    {
                        #TODO: should be discussed with fetchai on how to use third party deployed contract:
                        #It seems that the one who is allowed to change 
                        #the contract state must be set to contract deployer!
                        "deployer_address": self.context.agent_address, 
                        "topics": services,
                        "endpoint": self.context.agent_address,
                    }
                )
            )
            #TODO: the following line is only used for testing issues!
            print(contract_api_msg)
            contract_api_dialogue.terms = strategy.get_contract_terms()
            self.context.outbox.put_message(message=contract_api_msg)
            self.context.logger.info("Adding services to contract...")   

    def _remove_services(self) -> None:
        """
        Removes a service provided by the agent from service directory contract.

        :return: None
        """
        strategy = cast(GenericStrategy, self.context.strategy)
        services = strategy.get_services()
        if strategy.is_ledger_tx:
            contract_api_dialogues = cast(
                ContractApiDialogues, self.context.contract_api_dialogues
            )
            contract_api_msg, contract_api_dialogue = contract_api_dialogues.create(
                counterparty=LEDGER_API_ADDRESS,
                performative=ContractApiMessage.Performative.GET_RAW_TRANSACTION,
                ledger_id=strategy.ledger_id,
                contract_id=strategy.contract_id,
                contract_address=strategy.contract_address,
                callable="removeServices",
                kwargs=ContractApiMessage.Kwargs(
                    {
                        #TODO: should be discussed with fetchai on how to use third party deployed contract:
                        #It seems that the one who is allowed to change 
                        #the contract state must be set to contract deployer!
                        "deployer_address": self.context.agent_address,
                        "topics": services,
                    }
                )
            )
            #TODO: the following line is only used for testing issues!
            print(contract_api_msg)
            contract_api_dialogue.terms = strategy.get_contract_terms()
            self.context.outbox.put_message(message=contract_api_msg)
            self.context.logger.info("Removing all services from contract...")