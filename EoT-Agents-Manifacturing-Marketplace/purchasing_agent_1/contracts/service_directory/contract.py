# Copyright (c) 2021 - for information on the respective copyright owner see the NOTICE file and/or the repository https://github.com/boschresearch/open-eot-agents.
#
# SPDX-License-Identifier: Apache-2.0

"""This module contains the service-directory contract definition."""

import json
import logging
import random
from typing import Any, Dict, List, Optional, cast

from aea.common import Address
from aea.configurations.base import PublicId
from aea.contracts.base import Contract
from aea.crypto.base import LedgerApi
from aea_ledger_ethereum.ethereum import EthereumApi


class ServiceDirectory(Contract):
    """The contract class as interface to a smart contract."""
    
    PUBLIC_ID = PublicId.from_str("bosch/service_directory:0.1.0")

    def getServiceEndpoints(
        cls,
        ledger_api: LedgerApi,
        contract_address: Address,
        deployer_address: Address,
        topic,
        data: Optional[bytes] = b"",
        gas: int = 300000,
    ) -> Dict[str, Any]:
        """
        Get the service endpoints.

        :param ledger_api: the ledger API
        :param contract_address: the address of the contract
        :param deployer_address: the address of the deployer
        :param topic: the service topic to add
        :param data: the data to include in the transaction
        :param gas: the gas to be used
        :return: the service endpoint
        """
        if ledger_api.identifier == EthereumApi.identifier:
            nonce = ledger_api.api.eth.getTransactionCount(deployer_address)
            instance = cls.get_instance(ledger_api, contract_address)
            endpoints = instance.functions.getServiceEndpoints(topic).call()
            result = {topic: endpoints}
            return {"topic": result}