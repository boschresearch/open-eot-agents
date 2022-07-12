# Copyright (c) 2021 - for information on the respective copyright owner see the NOTICE file and/or the repository https://github.com/boschresearch/open-eot-agents.
#
# SPDX-License-Identifier: Apache-2.0

from cgi import print_form
import json
import os.path
import shutil
import sys
import time
from typing import Any, List, Optional
from marketplace_manager import MarketplaceManager
from aea.configurations.base import PublicId

SELLING_AGENT_ID = PublicId.from_str("bosch/selling_agent:0.1.0")
PURCHASING_AGENT_ID = PublicId.from_str("bosch/purchasing_agent:0.1.0")
WORKING_DIR = "./mam"
ETH_KEY_PATH_PREFIX = "../../../keys/eth_priv_key_"
FETCH_KEY_PATH_PREFIX = "../../../keys/fetch_priv_key_"
KEY_PATH_SUFFIX = ".txt"
ETH_ADDRESS = "http://127.0.0.1:8545"
CONTRACT_ADDRESS_FILE = "contract_address.txt"

p2p_public_id = PublicId.from_str("fetchai/p2p_libp2p:0.26.0")
ledger_public_id = PublicId.from_str("fetchai/ledger:0.20.0")
fipa_selling_public_id = PublicId.from_str("bosch/fipa_negotiation_selling:0.1.0")
fipa_purchasing_public_id = PublicId.from_str("bosch/fipa_negotiation_purchasing:0.1.0")

mm: MarketplaceManager
contract_address: str


def add_selling_agent(agent_name: str, id: int, multiaddr: Optional[str] = None) -> str:
    if mm:
        name = agent_name + "_" + str(id)
        agent_overrides = {
            "private_key_paths": {"ethereum": ETH_KEY_PATH_PREFIX + str(id) + KEY_PATH_SUFFIX},
            "connection_private_key_paths": {"fetchai": FETCH_KEY_PATH_PREFIX + str(id) + KEY_PATH_SUFFIX}
        }
        entry_peers: List
        if multiaddr:
            entry_peers = []
        else:
            entry_peers = []

        component_overrides = [{
            **p2p_public_id.json,
            "type": "connection",
            "config": {
                "delegate_uri": "127.0.0.1:" + str(11000 + id),
                "entry_peers": entry_peers,
                "local_uri": "127.0.0.1:" + str(9000 + id),
                "public_uri": "127.0.0.1:" + str(9000 + id),
            }
        }, {
            **ledger_public_id.json,
            "type": "connection",
            "config": {
                "ledger_apis": {
                    "ethereum": {
                        "address": ETH_ADDRESS
                    }
                }
            }
        }, {
            **fipa_selling_public_id.json,
            "type": "skill",
            "models": {
                "strategy": {
                    "args": {
                        "contract_address": contract_address,
                        "deployer_address": '0x9C8c99D1c21cA01437226AbFeB537411C3f70634'
                    }
                }
            }
        }]
        mm.add_selling_agent(
            name=name, agent_overrides=agent_overrides, component_overrides=component_overrides
        )
        mm.run_agent(name)
        return name
    else:
        return None


def add_purchasing_agent(agent_name: str, id: int, multiaddr: Optional[str] = None) -> str:
    if mm:
        name = agent_name + "_" + str(id)
        agent_overrides = {
            "private_key_paths": {"ethereum": ETH_KEY_PATH_PREFIX + str(id) + KEY_PATH_SUFFIX},
            "connection_private_key_paths": {"fetchai": FETCH_KEY_PATH_PREFIX + str(id) + KEY_PATH_SUFFIX}
        }
        entry_peers: List
        if multiaddr:
            entry_peers = [multiaddr]
        else:
            entry_peers = []
        component_overrides = [{
            **p2p_public_id.json,
            "type": "connection",
            "config": {
                "delegate_uri": "127.0.0.1:" + str(11000 + id),
                "entry_peers": entry_peers,
                "local_uri": "127.0.0.1:" + str(9000 + id),
                "public_uri": "127.0.0.1:" + str(9000 + id),
            }
        }, {
            **ledger_public_id.json,
            "type": "connection",
            "config": {
                "ledger_apis": {
                    "ethereum": {
                        "address": ETH_ADDRESS
                    }
                }
            }
        }, {
            **fipa_purchasing_public_id.json,
            "type": "skill",
            "models": {
                "strategy": {
                    "args": {
                        "contract_address": contract_address,
                        "deployer_address": '0x9C8c99D1c21cA01437226AbFeB537411C3f70634'
                    }
                }
            }
        }]
        mm.add_purchasing_agent(
            name=name, agent_overrides=agent_overrides, component_overrides=component_overrides
        )
        mm.run_agent(name)
        return name
    else:
        return None


def run(registry_path: str):
    try:
        global mm
        global contract_address
        with open(CONTRACT_ADDRESS_FILE) as file:
            firstline = file.readline().rstrip()
            if firstline:
                contract_address = firstline
            else:
                raise ValueError("Contract address is missing!")
        if os.path.exists(WORKING_DIR):
            print(WORKING_DIR + " folder already existent, deletion...")
            shutil.rmtree(WORKING_DIR)
        mm = MarketplaceManager(working_dir=WORKING_DIR, registry_path=registry_path,
                                purchasing_agent_id=PURCHASING_AGENT_ID, selling_agent_id=SELLING_AGENT_ID)
        mm.start()
        print("Adding Selling Agent...")
        name_0 = add_selling_agent("SellingAgent", 0)
        # Wait for file with sleep has to be done in main thread to not block other threads to start agent
        while not mm.is_libp2p_log_existent(name_0):
            time.sleep(1.)
        # Currently expecting one entry for address to be joined
        agent_p2p_address = mm.get_agent_libp2p_multiaddrs(name_0)[0]
        print(name_0 + " P2P address is " + agent_p2p_address)
        print("Adding Purchasing Agent...")
        add_purchasing_agent("PurchasingAgent", 3, agent_p2p_address)
        # TODO: Find criteria to stop scenario
        while True:
            time.sleep(1.)
    finally:
        if mm:
            print("Stopping Marketplace Manager...")
            mm.stop()


if __name__ == "__main__":
    if len(sys.argv) == 2 and len(sys.argv[1]) > 2:
        print("AEA Registry path given: " + sys.argv[1])
        sys.exit(run(sys.argv[1]))
    else:
        print("No registry path given as argument!")
