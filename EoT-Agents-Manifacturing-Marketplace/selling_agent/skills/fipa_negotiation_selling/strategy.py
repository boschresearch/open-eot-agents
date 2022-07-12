# Copyright (c) 2021 - for information on the respective copyright owner see the NOTICE file and/or the repository https://github.com/boschresearch/open-eot-agents.
#
# SPDX-License-Identifier: Apache-2.0

import uuid
from typing import Any, Dict, Optional, Tuple, List

from aea.common import Address
from aea.crypto.ledger_apis import LedgerApis
from aea.exceptions import enforce
from aea.helpers.search.generic import (
    SIMPLE_SERVICE_MODEL,
)
from aea.helpers.search.models import Description, Location, Query
from aea.helpers.transaction.base import Terms
from aea.skills.base import Model
from packages.bosch.contracts.service_directory.contract import ServiceDirectory

DEFAULT_IS_LEDGER_TX = True
DEFAULT_CONTRACT_ADDRESS = "0x0"
DEFAULT_DEPLOYER_ADDRESS = "0x0"

DEFAULT_SERVICE_1_DATA = {"id": "3D_printing_service", "material_cost": 30, "usage_cost": 20, "machine_cost": 10, "personnel": 4, "cut": 0.1, 
    "service_query": {"key": "seller_service", "value": "3D_printing_service"}, "data_for_sale": {"printing": "3D"}}
DEFAULT_SERVICE_2_DATA = {"id": "3DX_printing_service", "material_cost": 40, "usage_cost": 30, "machine_cost": 20, "personnel": 5, "cut": 0.1,
    "service_query": {"key": "seller_service", "value": "3DX_printing_service"}, "data_for_sale": {"printing": "3DX"}}



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

        #Note: selling agent strategy extended to offer more than one service 
        #see skills.yaml on how to add more services to this agent!
        #for now only one service _service_1_data is considered.
        self._service_1_data = kwargs.pop("service_1_data", DEFAULT_SERVICE_1_DATA)
        self._service_2_data = kwargs.pop("service_2_data", DEFAULT_SERVICE_2_DATA)

        #TODO: extend this to get the service description of more than one service!
        #for now only one service _service_1_data is considered.
        self._simple_service_data = {
            self._service_1_data["service_query"]["key"]: self._service_1_data["service_query"]["value"]
        }
    
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
        enforce(
            self.context.agent_addresses.get(self._ledger_id, None) is not None,
            "Wallet does not contain cryptos for provided ledger id.",
        )

    @property
    def ledger_id(self) -> str:
        """Get the ledger id."""
        return self._ledger_id

    @property
    def is_ledger_tx(self) -> bool:
        """Check whether or not tx are settled on a ledger."""
        return self._is_ledger_tx

    def get_services(self) -> List[str]:
        """
        Get the services to be offered.

        :return: a dictionary of services
        """
        self._services = [self._service_1_data["id"], self._service_2_data["id"]]
        return self._services
    
    def get_contract_terms(self) -> Terms:
        """
        Get the contract terms.

        :return: the terms of the contract
        """
        #Note: Those terms are only used for interaction with the service_discovery smart contract
        #within a contract api message. The fields amount_by_currency_id and quantities_by_good_id 
        #are not relevant but are required within a Terms data structure
        terms = Terms(
            ledger_id=self.ledger_id,
            sender_address=self.context.agent_address,
            counterparty_address=self.context.agent_address,
            amount_by_currency_id={},
            quantities_by_good_id={},
            nonce="",
        )
        return terms

    def is_matching_supply(self, query: Query) -> bool:
        """
        Check if the query matches the supply.

        :param query: the query
        :return: bool indicating whether matches or not
        """
        return query.check(self.get_service_description())
    
    def get_service_description(self) -> Description:
        """
        Get the simple service description.

        :return: a description of the offered services
        """
        #TODO: extend this to check if incoming service query matches 
        #one of the descriptions of the services offered by the selling agent!
        description = Description(
             self._simple_service_data, data_model=SIMPLE_SERVICE_MODEL,
        )
        return description

    def generate_proposal_terms_and_data(  # pylint: disable=unused-argument
        self, query: Query, counterparty_address: Address
    ) -> Tuple[Description, Terms, Dict[str, str]]:
        """
        Generate a proposal matching the query.

        :param query: the query
        :param counterparty_address: the counterparty of the proposal.
        :return: a tuple of proposal, terms and the weather data
        """
        data_for_sale = self._service_1_data["data_for_sale"]
        sale_quantity = len(data_for_sale)
        seller_address = self.context.agent_addresses[self.ledger_id]
        total_price = sale_quantity * self._service_1_data["material_cost"] * self._service_1_data["usage_cost"] * self._service_1_data["machine_cost"]
        if self.is_ledger_tx:
            tx_nonce = LedgerApis.generate_tx_nonce(
                identifier=self.ledger_id,
                seller=seller_address,
                client=counterparty_address,
            )
        else:
            tx_nonce = uuid.uuid4().hex  # pragma: nocover
        proposal = Description(
            {
                "ledger_id": self.ledger_id,
                "price": total_price,
                "currency_id": self._currency_id,
                "service_id": self._service_1_data["id"],
                "quantity": sale_quantity,
                "tx_nonce": tx_nonce,
            }
        )
        terms = Terms(
            ledger_id=self.ledger_id,
            sender_address=seller_address,
            counterparty_address=counterparty_address,
            amount_by_currency_id={self._currency_id: total_price},
            quantities_by_good_id={self._service_1_data["id"]: -sale_quantity},
            is_sender_payable_tx_fee=False,
            nonce=tx_nonce,
            fee_by_currency_id={self._currency_id: 0},
        )
        return proposal, terms, data_for_sale
