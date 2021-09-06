# Copyright (c) 2021 - for information on the respective copyright owner see the NOTICE file and/or the repository https://github.com/boschresearch/open-eot-agents.
#
# SPDX-License-Identifier: Apache-2.0

from typing import Any, Dict, List, Tuple

from aea.common import Address
from aea.exceptions import enforce
from aea.helpers.search.generic import SIMPLE_SERVICE_MODEL
from aea.helpers.search.models import (
    Constraint,
    ConstraintType,
    Description,
    Location,
    Query,
)
from aea.helpers.transaction.base import Terms
from aea.skills.base import Model
from packages.bosch.contracts.service_directory.contract import ServiceDirectory


DEFAULT_IS_LEDGER_TX = True
DEFAULT_CONTRACT_ADDRESS = "0x0"
DEFAULT_DEPLOYER_ADDRESS = "0x0"
DEFAULT_SEARCH_SERVICE_1 = {"id": "3D_printing_service", "max_tx_fee": 1, "max_unit_price": 10, "min_quantity": 1}
DEFAULT_SEARCH_SERVICE_2 = {"id": "3D_printing_service", "max_tx_fee": 1, "max_unit_price": 20, "min_quantity": 1}

class GenericStrategy(Model):
    """This class defines a strategy for the agent."""

    def __init__(self, **kwargs: Any) -> None:
        """
        Initialize the strategy of the agent.

        :return: None
        """
        ledger_id = kwargs.pop("ledger_id", None)       
        self._is_ledger_tx = kwargs.pop("is_ledger_tx", DEFAULT_IS_LEDGER_TX)
        self.contract_id = str(ServiceDirectory.PUBLIC_ID)
        self.contract_address = kwargs.pop("contract_address", DEFAULT_CONTRACT_ADDRESS)
        self.deployer_address = kwargs.pop("deployer_address", DEFAULT_DEPLOYER_ADDRESS)

        self._search_service_1 = kwargs.pop("search_service_1", DEFAULT_SEARCH_SERVICE_1)
        self._search_service_2 = kwargs.pop("search_service_2", DEFAULT_SEARCH_SERVICE_2)

        super().__init__(**kwargs)
        self._ledger_id = (
            ledger_id if ledger_id is not None else self.context.default_ledger_id
        )
        
        self._is_searching = False
        self._balance = 0
    
    @property
    def ledger_id(self) -> str:
        """Get the ledger id."""
        return self._ledger_id

    @property
    def is_ledger_tx(self) -> bool:
        """Check whether or not tx are settled on a ledger."""
        return self._is_ledger_tx

    @property
    def is_searching(self) -> bool:
        """Check if the agent is searching."""
        return self._is_searching

    @is_searching.setter
    def is_searching(self, is_searching: bool) -> None:
        """Check if the agent is searching."""
        enforce(isinstance(is_searching, bool), "Can only set bool on is_searching!")
        self._is_searching = is_searching

    @property
    def balance(self) -> int:
        """Get the balance."""
        return self._balance

    @balance.setter
    def balance(self, balance: int) -> None:
        """Set the balance."""
        self._balance = balance

    def get_services(self) -> Dict[str, str]:
        """
        Get the services to be discovered.

        :return: a dictionary of services
        """
        self._services = {"search_service_1": self._search_service_1["id"], "search_service_2": self._search_service_2["id"]}
        return self._services

    def get_contract_terms(self) -> Terms:
        """
        Get the contract terms.

        :return: the terms of the contract
        """
        terms = Terms(
            ledger_id=self.ledger_id,
            sender_address=self.context.agent_address,
            counterparty_address=self.context.agent_address,
            amount_by_currency_id={},
            quantities_by_good_id={},
            nonce="",
        )
        return terms