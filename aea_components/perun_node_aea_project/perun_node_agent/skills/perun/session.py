# Copyright (c) 2022 - for information on the respective copyright owner see the NOTICE file and/or the repository https://github.com/boschresearch/open-eot-agents.
#
# SPDX-License-Identifier: Apache-2.0

from typing import Any, Dict, List, Optional
from aea.skills.base import Model

from packages.bosch.protocols.perun_grpc.grpc_message import PayChInfo, PeerId


class PerunSession():
    """This class represents data belonging to one Perun Session."""

    def __init__(self, **kwargs: Any) -> None:
        self._config_file = kwargs.pop("config_file", None)
        self._is_open = kwargs.pop("is_open", False)
        self._peer_ids: Optional[Dict[str, PeerId]] = {}
        self._restored_chs: List["PayChInfo"] = kwargs.pop("restored_chs", [])

    @property
    def config_file(self) -> str:
        """Get the config file for the session."""
        return self._config_file

    @property
    def is_open(self) -> bool:
        """Get the open state of the session."""
        return self._is_open

    @is_open.setter
    def is_open(self, state: bool) -> bool:
        """Set the state of the session."""
        self._is_open = state

    @property
    def peer_ids(self) -> Dict[str, PeerId]:
        """Get the loaded peer ids of the session."""
        return self._peer_ids

    @property
    def restored_chs(self) -> List["PayChInfo"]:
        """Get the loaded peer ids of the session."""
        return self._restored_chs


class PerunSessions(Model):
    """This class contains data belonging to Perun Sessions."""

    def __init__(self, **kwargs) -> None:
        """
        Initialize sessions.

        :return: None
        """
        Model.__init__(self, **kwargs)
        self._sessions: Optional[Dict[str, PerunSession]] = {}

    @property
    def sessions(self) -> Dict[str, PerunSession]:
        """
        Get the current sessions.
        Key of one session is the session_id to be loaded from node.
        """
        return self._sessions
