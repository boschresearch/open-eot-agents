# Copyright (c) 2021 - for information on the respective copyright owner see the NOTICE file and/or the repository https://github.com/boschresearch/open-eot-agents.
#
# SPDX-License-Identifier: Apache-2.0

import uuid
from typing import Any, Dict, Optional, Tuple, List

from aea.exceptions import enforce

from aea.helpers.transaction.base import Terms
from aea.skills.base import Model
from packages.bosch.contracts.service_directory.contract import ServiceDirectory

DEFAULT_IS_LEDGER_TX = True
DEFAULT_CONTRACT_ADDRESS = "0x0"
DEFAULT_DEPLOYER_ADDRESS = "0x0"
DEFAULT_SERVICE_1_DATA = {"id": "3D_printing_service", "material_cost": 20, "usage_cost": 10, "machine_cost": 3, "personnel": 4, "cut": 0.1}
DEFAULT_SERVICE_2_DATA = {"id": "3DX_printing_service", "material_cost": 40, "usage_cost": 20, "machine_cost": 4, "personnel": 5, "cut": 0.1}


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

        self._service_1_data = kwargs.pop("service_1_data", DEFAULT_SERVICE_1_DATA)
        self._service_2_data = kwargs.pop("service_2_data", DEFAULT_SERVICE_2_DATA)

        super().__init__(**kwargs)
        self._ledger_id = (
            ledger_id if ledger_id is not None else self.context.default_ledger_id
        )
        enforce(
            self.context.agent_addresses.get(self._ledger_id, None) is not None,
            "Wallet does not contain cryptos for provided ledger id.",)

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
        terms = Terms(
            ledger_id=self.ledger_id,
            sender_address=self.context.agent_address,
            counterparty_address=self.context.agent_address,
            amount_by_currency_id={},
            quantities_by_good_id={},
            nonce="",
        )
        return terms