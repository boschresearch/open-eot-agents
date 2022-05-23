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
    Query,
)
from aea.helpers.transaction.base import Terms
from aea.skills.base import Model
from packages.bosch.contracts.service_directory.contract import ServiceDirectory


DEFAULT_IS_LEDGER_TX = True
DEFAULT_CONTRACT_ADDRESS = "0x0"
DEFAULT_DEPLOYER_ADDRESS = "0x0"
DEFAULT_MAX_NEGOTIATIONS = 2
DEFAULT_SEARCH_SERVICE_1 = {"id": "3D_printing_service", "max_tx_fee": 1, "max_unit_price": 10, "min_quantity": 1, "max_quantity": 4,
        "search_query": {
        "constraint_type": "==",
        "search_key": "seller_service",
        "search_value": "3D_printing_service",}}
DEFAULT_SEARCH_SERVICE_2 = {"id": "3DX_printing_service", "max_tx_fee": 1, "max_unit_price": 20, "min_quantity": 1, "max_quantity": 3,
        "search_query": {
        "constraint_type": "==",
        "search_key": "seller_service",
        "search_value": "3DX_printing_service",}}


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
        currency_id = kwargs.pop("currency_id", None)
        
        self._max_negotiations = kwargs.pop("max_negotiations", DEFAULT_MAX_NEGOTIATIONS)

        self._search_service_1 = kwargs.pop("search_service_1", DEFAULT_SEARCH_SERVICE_1)
        self._search_service_2 = kwargs.pop("search_service_2", DEFAULT_SEARCH_SERVICE_2)

        super().__init__(**kwargs)
        self._ledger_id = (
            ledger_id if ledger_id is not None else self.context.default_ledger_id
        )
        if currency_id is None:
            currency_id = self.context.currency_denominations.get(self._ledger_id, None)
            enforce(
                currency_id is not None,
                f"Currency denomination for ledger_id={self._ledger_id} not specified.",
            )
        self._currency_id = currency_id
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

    @property
    def max_negotiations(self) -> int:
        """Get the maximum number of negotiations the agent can start."""
        return self._max_negotiations

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
    
    def get_service_query(self) -> Query:
        """
        Get the service query of the agent.

        :return: the query
        """
        service_key_filter = Constraint(
            self._search_service_1["search_query"]["search_key"],
            ConstraintType(
                self._search_service_1["search_query"]["constraint_type"],
                self._search_service_1["search_query"]["search_value"],
            ),
        )
        query = Query([service_key_filter], model=SIMPLE_SERVICE_MODEL)
        return query

    def is_acceptable_proposal(self, proposal: Description) -> bool:
        """
        Check whether it is an acceptable proposal.

        :return: whether it is acceptable
        """
        result = (
            all(
                [
                    key in proposal.values
                    for key in [
                        "ledger_id",
                        "currency_id",
                        "price",
                        "service_id",
                        "quantity",
                        "tx_nonce",
                    ]
                ]
            )
            and proposal.values["ledger_id"] == self.ledger_id
            and proposal.values["price"] > 0
            and proposal.values["quantity"] >= self._search_service_1["min_quantity"]
            and proposal.values["quantity"] <= self._search_service_1["max_quantity"]
            and proposal.values["price"]
            <= proposal.values["quantity"] * self._search_service_1["max_unit_price"]
            and proposal.values["currency_id"] == self._currency_id
            and proposal.values["service_id"] == self._search_service_1["id"]
            and isinstance(proposal.values["tx_nonce"], str)
            and proposal.values["tx_nonce"] != ""
        )
        return result

    def is_affordable_proposal(self, proposal: Description) -> bool:
        """
        Check whether it is an affordable proposal.

        :return: whether it is affordable
        """
        if self.is_ledger_tx:
            payable = proposal.values.get("price", 0) + self._search_service_1["max_tx_fee"]
            result = self.balance >= payable
        else:
            result = True
        return result
    
    def terms_from_proposal(
        self, proposal: Description, counterparty_address: Address
    ) -> Terms:
        """
        Get the terms from a proposal.

        :param proposal: the proposal
        :return: terms
        """
        buyer_address = self.context.agent_addresses[proposal.values["ledger_id"]]
        terms = Terms(
            ledger_id=proposal.values["ledger_id"],
            sender_address=buyer_address,
            counterparty_address=counterparty_address,
            amount_by_currency_id={
                proposal.values["currency_id"]: -proposal.values["price"]
            },
            quantities_by_good_id={
                proposal.values["service_id"]: proposal.values["quantity"]
            },
            is_sender_payable_tx_fee=True,
            nonce=proposal.values["tx_nonce"],
            fee_by_currency_id={proposal.values["currency_id"]: self._search_service_1["max_tx_fee"]},
        )
        return terms
    
    #TODO: Check if this could be used in current use-case!
    def get_acceptable_counterparties(
        self, counterparties: Tuple[str, ...]
    ) -> Tuple[str, ...]:
        """
        Process counterparties and drop unacceptable ones.

        :return: list of counterparties
        """
        valid_counterparties: List[str] = []
        for idx, counterparty in enumerate(counterparties):
            if idx < self.max_negotiations:
                valid_counterparties.append(counterparty)
        return tuple(valid_counterparties)
    
    def successful_trade_with_counterparty(
        self, counterparty: str, data: Dict[str, str]
    ) -> None:
        """
        Do something on successful trade.

        :param counterparty: the counterparty address
        :param data: the data
        :return: False
        """
        self.context.logger.info("trade with sender={} was sucessful!".format(counterparty))