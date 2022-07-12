# Copyright (c) 2021 - for information on the respective copyright owner see the NOTICE file and/or the repository https://github.com/boschresearch/open-eot-agents.
#
# SPDX-License-Identifier: Apache-2.0

from typing import Any, List, Optional, Set, cast

from aea.skills.behaviours import TickerBehaviour

from packages.fetchai.connections.ledger.base import (
    CONNECTION_ID as LEDGER_CONNECTION_PUBLIC_ID,
)
from packages.fetchai.protocols.ledger_api.message import LedgerApiMessage
from packages.fetchai.protocols.contract_api.message import ContractApiMessage
from packages.bosch.skills.basic_service_discovery.dialogues import (
    LedgerApiDialogues,
    ContractApiDialogues,
)
from packages.bosch.skills.basic_service_discovery.strategy import GenericStrategy

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

    def _get_services_endpoints(self)-> None:
        """
        Gets service endpoints from service directory contract.

        :return: a list of endpoints
        """
        strategy = cast(GenericStrategy, self.context.strategy)
        #TODO: change smart contract to allow for getting the endpoints of all requested services!
        services = strategy.get_services()
        #TODO: remove the following line after fixing the issue above!
        service = services["search_service_1"]
        #TODO: remove this line as used only to check is_searching = False condition within handler to stop searching!
        #service = "test_service"
        if strategy.is_ledger_tx:
            contract_api_dialogues = cast(
                ContractApiDialogues, self.context.contract_api_dialogues
            )
            contract_api_msg, contract_api_dialogue = contract_api_dialogues.create(
                counterparty=LEDGER_API_ADDRESS,
                #TODO: tried to use GET_RAW_MESSAGE instead but it turns out to be difficult 
                # as it expects a byte string as return value by the contract
                performative=ContractApiMessage.Performative.GET_STATE,  
                ledger_id=strategy.ledger_id,
                contract_id=strategy.contract_id,
                contract_address=strategy.contract_address,
                callable="getServiceEndpoints", #TODO: should be named to getServicesEndpoints within contract.py and solidity code!
                kwargs=ContractApiMessage.Kwargs(
                    {
                        "deployer_address": strategy.deployer_address,
                        "topic": service, #TODO: should be changed to "topics: services"
                    }
                )
            )
            #TODO: the following line is only used for testing issues!
            print(contract_api_msg)
            contract_api_dialogue.terms = strategy.get_contract_terms()
            self.context.outbox.put_message(message=contract_api_msg)
            self.context.logger.info("Getting service endpoints from contract...")