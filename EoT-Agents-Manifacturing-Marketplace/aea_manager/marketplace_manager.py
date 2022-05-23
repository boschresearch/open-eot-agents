# Copyright (c) 2021 - for information on the respective copyright owner see the NOTICE file and/or the repository https://github.com/boschresearch/open-eot-agents.
#
# SPDX-License-Identifier: Apache-2.0

import os.path
from pathlib import Path
from time import time
from typing import List, Optional

from aea.configurations.base import PublicId
from aea.manager import MultiAgentManager


class MarketplaceManager():

    def __init__(self, working_dir: str, registry_path: str, selling_agent_id: PublicId, purchasing_agent_id: PublicId):
        self.REGISTRY_PATH = registry_path
        self.WORKING_DIR = working_dir
        self.SELLING_AGENT_ID = selling_agent_id
        self.PURCHASING_AGENT_ID = purchasing_agent_id
        self.P2P_LOG_FILE = "libp2p_node.log"

    def _init_mam(self):
        self._manager = MultiAgentManager(
            working_dir=self.WORKING_DIR,
            registry_path=self.REGISTRY_PATH
        )
        # maybe set local=True
        self._manager.start_manager()
        self._manager.add_project(public_id=self.SELLING_AGENT_ID)
        self._manager.add_project(public_id=self.PURCHASING_AGENT_ID)

    def add_selling_agent(
            self, name: str, agent_overrides: Optional[dict] = None, component_overrides: Optional[List[dict]] = None):
        self._manager.add_agent(
            public_id=self.SELLING_AGENT_ID, agent_name=name, agent_overrides=agent_overrides,
            component_overrides=component_overrides)

    def add_purchasing_agent(
            self, name: str, agent_overrides: Optional[dict] = None, component_overrides: Optional[List[dict]] = None):
        self._manager.add_agent(public_id=self.PURCHASING_AGENT_ID, agent_name=name, agent_overrides=agent_overrides,
                                component_overrides=component_overrides)

    def run_agent(self, name: str):
        self._manager.start_agent(name)

    def is_libp2p_log_existent(self, agent_name: str) -> bool:
        dir = self._manager.get_data_dir_of_agent(agent_name)
        return os.path.exists(dir + "/" + self.P2P_LOG_FILE)

    def get_agent_libp2p_multiaddrs(self, agent_name: str) -> List[str]:
        LIST_START = "MULTIADDRS_LIST_START"
        LIST_END = "MULTIADDRS_LIST_END"
        multiaddrs = []
        dir = self._manager.get_data_dir_of_agent(agent_name)
        if not self.is_libp2p_log_existent(agent_name):
            raise ValueError("libp2p log file for agent " + agent_name + " is not available!")

        with open(dir + "/" + self.P2P_LOG_FILE, "r") as f:
            lines = f.readlines()

        found = False
        for line in lines:
            if LIST_START in line:
                found = True
                multiaddrs = []
                continue
            if found:
                elem = line.strip()
                if elem != LIST_END and len(elem) != 0:
                    multiaddrs.append(elem)
                else:
                    found = False
        return multiaddrs

    def _shutdown(self):
        if self._manager:
            try:
                self._manager.stop_all_agents()
            finally:
                self._manager.stop_manager()

    def start(self):
        self._init_mam()

    def stop(self):
        self._shutdown()
