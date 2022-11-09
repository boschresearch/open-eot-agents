# Copyright (c) 2022 - for information on the respective copyright owner see the NOTICE file and/or the repository https://github.com/boschresearch/open-eot-agents.
#
# SPDX-License-Identifier: Apache-2.0

"""This package contains a scaffold of a behaviour."""

from ast import Not
from typing import Any, Dict, cast
from aea.skills.behaviours import OneShotBehaviour, TickerBehaviour
from packages.bosch.skills.perun.dialogues import PerunDialogues
from packages.bosch.protocols.perun_grpc.message import PerunGrpcMessage
from packages.bosch.protocols.perun_grpc.grpc_message import CloseSessionReq, GetPeerIdReq, OpenSessionReq
from packages.bosch.skills.perun.session import PerunSession, PerunSessions

PERUN_CONNECTION_ID = "bosch/perun_node:0.1.0"


class PerunOpenSessionBehaviour(OneShotBehaviour):
    """This class scaffolds a behaviour."""

    def __init__(self, **kwargs: Any) -> None:
        self.perun_connection: str = cast(str, kwargs.pop("connection", PERUN_CONNECTION_ID))
        self.perun_scf: str = cast(str, kwargs.pop("scf", None))
        super().__init__(**kwargs)

    def setup(self) -> None:
        """Implement the setup."""
        self.context.logger.info("Setup of PerunOpenSessionBehaviour...")

    def act(self) -> None:
        """Implement the act."""
        # Open the session
        self.context.logger.info("Creating request to open perun session with config file {}".format(self.perun_scf))
        perun_dialogues = cast(
            PerunDialogues, self.context.perun_dialogues
        )
        perun_sessions = cast(PerunSessions, self.context.perun_sessions)
        open_session_request = OpenSessionReq(config_file=self.perun_scf)
        message, dialogue = perun_dialogues.create(
            counterparty=self.perun_connection, performative=PerunGrpcMessage.Performative.REQUEST,
            type=open_session_request.__class__.__name__, content=bytes(open_session_request))
        self.context.logger.debug("Open session message to be send {}".format(message))
        self.context.outbox.put_message(message=message)

    def teardown(self) -> None:
        """Implement the task teardown."""
        self.context.logger.info("Teardown of PerunOpenSessionBehaviour...")


class PerunCloseSessionBehaviour(OneShotBehaviour):

    def __init__(self, **kwargs: Any) -> None:
        self.perun_connection: str = cast(str, kwargs.pop("connection", PERUN_CONNECTION_ID))
        self.perun_session_id: str = cast(str, kwargs.pop("session_id", None))
        self.perun_force_close: str = cast(str, kwargs.pop("force_close", True))
        super().__init__(**kwargs)

    def setup(self) -> None:
        """Implement the setup."""
        self.context.logger.info("Setup of PerunCloseSessionBehaviour...")
        if self.perun_session_id is None:
            raise ValueError("No session id is given to close!")

    def act(self) -> None:
        self.context.logger.info("Creating request to close session with session_id {}".format(
            self.perun_session_id))
        perun_dialogues = cast(
            PerunDialogues, self.context.perun_dialogues
        )
        close_session_request = CloseSessionReq(self.perun_session_id, self.perun_force_close)
        message, dialogue = perun_dialogues.create(
            counterparty=self.perun_connection, performative=PerunGrpcMessage.Performative.REQUEST,
            type=close_session_request.__class__.__name__, content=bytes(close_session_request))
        self.context.logger.debug("Close session message to be send {}".format(message))
        self.context.outbox.put_message(message=message)

    def teardown(self) -> None:
        """Implement the task teardown."""
        self.context.logger.info("Teardown of PerunCloseSessionBehaviour...")


class PerunGetPeerIdBehaviour(OneShotBehaviour):

    def __init__(self, **kwargs: Any) -> None:
        self.perun_alias: str = cast(str, kwargs.pop("alias", None))
        self.perun_session_id: str = cast(str, kwargs.pop("session_id", None))
        super().__init__(**kwargs)

    def setup(self) -> None:
        """Implement the setup."""
        self.context.logger.info("Setup of PerunGetPeerIdBehaviour...")
        if self.perun_alias is None or self.perun_session_id is None:
            raise ValueError("No alias or session id is given to retrieve the corresponding PeerId!")

    def act(self) -> None:
        self.context.logger.info("Creating request to get PeerId for alias {} for session_id {}".format(
            self.perun_alias, self.perun_session_id))
        perun_dialogues = cast(
            PerunDialogues, self.context.perun_dialogues
        )
        get_peer_id_request = GetPeerIdReq(alias=self.perun_alias, session_id=self.perun_session_id)
        message, dialogue = perun_dialogues.create(
            counterparty=PERUN_CONNECTION_ID, performative=PerunGrpcMessage.Performative.REQUEST,
            type=get_peer_id_request.__class__.__name__, content=bytes(get_peer_id_request))
        self.context.logger.debug("Get peer ID message to be send {}".format(message))
        self.context.outbox.put_message(message=message)

    def teardown(self) -> None:
        """Implement the task teardown."""
        self.context.logger.info("Teardown of PerunGetPeerIdBehaviour...")


class PerunAliceBehaviour(TickerBehaviour):

    BOB = "bob"
    ALIAS_BOB = "alias_{}".format(BOB)

    def __init__(self, **kwargs: Any):
        """Initialize the search behaviour."""
        act_interval = cast(
            float, kwargs.pop("act_interval", 5)
        )
        self.perun_scf: str = cast(str, kwargs.pop("scf", None))
        self._done = False
        super().__init__(tick_interval=act_interval, **kwargs)

    def setup(self) -> None:
        """Implement the setup for the behaviour."""
        self.context.logger.info("Setup of PerunAliceBehaviour...")
        if self.perun_scf is None:
            raise ValueError("No session config file is given for Alice!")

    def act(self) -> None:
        self.context.logger.debug("Act of PerunAliceBehaviour...")
        if not self._done:
            perun_sessions = cast(PerunSessions, self.context.perun_sessions)
            session_id = self._get_key_for_session_config(self.perun_scf, perun_sessions.sessions)
            if not self.perun_scf is None and session_id is None:
                self.context.logger.info("Alice is opening session...")
                self.context.new_behaviours.put(PerunOpenSessionBehaviour(
                    name="alice_open_session", skill_context=self.context, scf=self.perun_scf))
            elif not session_id is None and not self.BOB in perun_sessions.sessions.get(session_id).peer_ids.keys():
                self.context.logger.info("Alice is getting PeerId alias of {}".format(self.BOB))
                self.context.new_behaviours.put(PerunGetPeerIdBehaviour(
                    name=self.ALIAS_BOB, skill_context=self.context, alias=self.BOB, session_id=session_id))
            elif not session_id is None and self.BOB in perun_sessions.sessions.get(session_id).peer_ids.keys():
                self.context.logger.info("Alice is closing session id {} for config {}".format(
                    session_id, self.perun_scf))
                self.context.new_behaviours.put(PerunCloseSessionBehaviour(
                    name="alice_close_session", skill_context=self.context, session_id=session_id))
                self._done = True

    def _get_key_for_session_config(self, scf: str, sessions: Dict[str, PerunSession]) -> str:
        if len(sessions.keys()):
            for k, v in sessions.items():
                if v.config_file == scf:
                    return k
        return None

    def teardown(self) -> None:
        self.context.logger.info("Teardown of PerunAliceBehaviour...")
