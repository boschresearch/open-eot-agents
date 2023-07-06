# Copyright (c) 2023 - for information on the respective copyright owner see the NOTICE file and/or the repository https://github.com/boschresearch/open-eot-agents.
#
# SPDX-License-Identifier: Apache-2.0

import logging
from typing import Any, Dict, cast, List

from aea.skills.base import Behaviour
from aea.skills.behaviours import FSMBehaviour, OneShotBehaviour, SequenceBehaviour, State
from packages.bosch.protocols.perun_grpc.message import PerunGrpcMessage
from packages.bosch.skills.perun.behaviours import (
    PerunCloseSessionBehaviour, PerunGetPeerIdBehaviour, PerunOpenSessionBehaviour, PerunOpenChannelBehaviour,
    PerunSessions, PerunSession)
from packages.bosch.skills.perun.dialogues import PerunDialogues
from packages.bosch.protocols.perun_grpc.grpc_message import BalInfo, BalInfoBal, ClosePayChReq, OpenPayChReq, PayChInfo, Payment, SendPayChUpdateReq

PERUN_CONNECTION_ID = "bosch/perun_node:0.1.0"


def get_key_for_session_config(scf: str, sessions: Dict[str, PerunSession]) -> str:
    if len(sessions.keys()):
        for k, v in sessions.items():
            if v.config_file == scf:
                return k
    return None


class OpenSessionState(State):

    def __init__(self, event_to_trigger=None, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.logger = logging.getLogger("packages.bosch.skills.perun_alice.OpenSessionState")
        self.event_to_trigger = event_to_trigger
        self.perun_scf: str = cast(str, kwargs.pop("scf", None))
        self._done = False
        self._open_session_behaviour: PerunOpenSessionBehaviour = PerunOpenSessionBehaviour(
            name="alice_open_session", skill_context=self.context, scf=self.perun_scf)
        self.context.new_behaviours.put(self._open_session_behaviour)

    def is_done(self) -> bool:
        return self._done

    def act(self) -> None:
        perun_sessions = cast(PerunSessions, self.context.perun_sessions)
        session_id = get_key_for_session_config(self.perun_scf, perun_sessions.sessions)
        if session_id is not None:
            self.logger.debug(
                "[{}] {}: Session is opened with session-id {}".format(self.context.agent_name, self.name, session_id))
            self._event = self.event_to_trigger
            self._done = True


class GetPeerIdState(State):
    def __init__(self, event_to_trigger=None, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.logger = logging.getLogger("packages.bosch.skills.perun_alice.GetPeerIdState")
        self.event_to_trigger = event_to_trigger
        self._perun_scf: str = cast(str, kwargs.pop("scf", None))
        self._alias_bob: str = cast(str, kwargs.pop("alias_bob", None))
        self.perun_sessions = cast(PerunSessions, self.context.perun_sessions)
        self._get_peer_id_behaviour = None
        self._done = False

    def is_done(self) -> bool:
        return self._done

    def act(self) -> None:
        session_id = get_key_for_session_config(self._perun_scf, self.perun_sessions.sessions)
        if self._get_peer_id_behaviour is None:
            self.logger.debug("[{}] Setting PerunGetPeerIdBehaviour...".format(self.context.agent_name))
            self._get_peer_id_behaviour = PerunGetPeerIdBehaviour(
                name="alice_get_peer_bob", skill_context=self.context, alias=self._alias_bob, session_id=session_id)
            self.context.new_behaviours.put(self._get_peer_id_behaviour)
        elif self._alias_bob in self.perun_sessions.sessions.get(session_id).peer_ids.keys():
            self.logger.debug("[{}] Peer Id is set for {}".format(self.context.agent_name, self._alias_bob))
            self._event = self.event_to_trigger
            self._done = True


class CloseSessionState(State):
    def __init__(self, event_to_trigger=None, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.logger = logging.getLogger("packages.bosch.skills.perun_alice.CloseSessionState")
        self.event_to_trigger = event_to_trigger
        self._perun_scf: str = cast(str, kwargs.pop("scf", None))
        self.perun_sessions = cast(PerunSessions, self.context.perun_sessions)
        self._get_close_session_behaviour = None
        self._done = False

    def is_done(self) -> bool:
        return self._done

    def act(self) -> None:
        session_id = get_key_for_session_config(self._perun_scf, self.perun_sessions.sessions)
        if self._get_close_session_behaviour is None:
            self.logger.debug("[{}] Setting PerunCloseSessionBehaviour...".format(self.context.agent_name))
            self._get_close_session_behaviour = PerunCloseSessionBehaviour(
                name="alice_close_session", skill_context=self.context, session_id=session_id)
            self.context.new_behaviours.put(self._get_close_session_behaviour)
        elif not self.perun_sessions.sessions.get(session_id).is_open:
            self.logger.debug("[{}] Session is closed for scf {}".format(self.context.agent_name, self._perun_scf))
            self._event = self.event_to_trigger
            self._done = True


class OpenChannelState(State):
    def __init__(self, event_to_trigger=None, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.logger = logging.getLogger("packages.bosch.skills.perun_alice.OpenChannelState")
        self.event_to_trigger = event_to_trigger
        self._perun_scf: str = cast(str, kwargs.pop("scf", None))
        self.alias_bob: str = cast(str, kwargs.pop("alias_bob", None))
        self.alice_amount = cast(str, kwargs.pop("alice_amount", None))
        self.bob_amount = cast(str, kwargs.pop("bob_amount", None))
        self.perun_sessions = cast(PerunSessions, self.context.perun_sessions)
        self._open_channel_behaviour = None
        self.request_send = False
        self._done = False

    def is_done(self) -> bool:
        return self._done

    def act(self) -> None:
        session_id = get_key_for_session_config(self._perun_scf, self.perun_sessions.sessions)
        if not self.perun_sessions.sessions[session_id].channels and not self.request_send:
            self.logger.debug("[{}] Open Channel with {} and balance {}:{}".format(
                self.context.agent_name, self.alias_bob, self.alice_amount, self.bob_amount))
            self._open_channel_behaviour = PerunOpenChannelBehaviour(
                name="alice_open_channel_behaviour", skill_context=self.context, session_id=session_id,
                alias_bob=self.alias_bob, alice_amount=self.alice_amount, bob_amount=self.bob_amount)
            self.logger.debug("[{}] Setting OpenChannelBehaviour...".format(self.context.agent_name))
            self.context.new_behaviours.put(self._open_channel_behaviour)
            self.request_send = True
        elif self.perun_sessions.sessions[session_id].channels and self.request_send and self._open_channel_behaviour is not None:
            self.logger.debug("[{}] Channel opened with {}".format(self.context.agent_name, self.alias_bob))
            self._event = self.event_to_trigger
            self._done = True


class SendTokenState(State):
    def __init__(self, event_to_trigger=None, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.logger = logging.getLogger("packages.bosch.skills.perun_alice.SendTokenState")
        self.event_to_trigger = event_to_trigger
        self._perun_scf: str = cast(str, kwargs.pop("scf", None))
        self.value_to_send = cast(int, kwargs.pop("token_to_send", None))
        self.alias_bob: str = cast(str, kwargs.pop("alias_bob", None))
        self.perun_sessions = cast(PerunSessions, self.context.perun_sessions)
        self._done = False
        self._send = False

    def is_done(self) -> bool:
        return self._done

    def act(self) -> None:
        session_id = get_key_for_session_config(self._perun_scf, self.perun_sessions.sessions)
        if not self._send and not self._done:
            self.logger.debug("[{}] Sending token to {}".format(self.context.agent_name, self.alias_bob))
            channel = None
            for k, v in self.perun_sessions.sessions[session_id].channels.items():
                if self.alias_bob in v.bal_info.parts:
                    channel = self.perun_sessions.sessions[session_id].channels[k]
                    break
            if channel is not None:
                perun_dialogues = cast(
                    PerunDialogues, self.context.perun_dialogues
                )
                send_pay_ch_update = SendPayChUpdateReq(session_id=session_id, ch_id=channel.ch_id)
                payment = Payment(currency='ETH', payee=self.alias_bob, amount=str(self.value_to_send))
                send_pay_ch_update = SendPayChUpdateReq(session_id=session_id, ch_id=channel.ch_id, payments=[payment])
                message, self.dialogue = perun_dialogues.create(
                    counterparty=PERUN_CONNECTION_ID, performative=PerunGrpcMessage.Performative.REQUEST,
                    type=send_pay_ch_update.__class__.__name__, content=bytes(send_pay_ch_update))
                self.logger.debug("[{}] payment channel update to be send {}".format(self.context.agent_name, message))
                self.context.outbox.put_message(message=message)
                self._send = True
        else:
            if self.dialogue is not None and self.dialogue.last_message.performative == PerunGrpcMessage.Performative.RESPONSE:
                self.logger.info("[{}] Payment {} send to {}.".format(
                    self.context.agent_name, self.value_to_send, self.alias_bob))
                self._event = self.event_to_trigger
                self._done = True


class CloseChannelState(State):
    def __init__(self, event_to_trigger=None, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.logger = logging.getLogger("packages.bosch.skills.perun_alice.CloseChannelState")
        self.event_to_trigger = event_to_trigger
        self._perun_scf: str = cast(str, kwargs.pop("scf", None))
        self.alias_bob: str = cast(str, kwargs.pop("alias_bob", None))
        self.perun_sessions = cast(PerunSessions, self.context.perun_sessions)
        self.dialogue = None
        self.request_send = False
        self._done = False

    def is_done(self) -> bool:
        return self._done

    def act(self) -> None:
        session_id = get_key_for_session_config(self._perun_scf, self.perun_sessions.sessions)
        if self.dialogue is None and not self.request_send:
            channel = None
            for k, v in self.perun_sessions.sessions[session_id].channels.items():
                if self.alias_bob in v.bal_info.parts:
                    channel = self.perun_sessions.sessions[session_id].channels[k]
                    break
            if channel is not None:
                perun_dialogues = cast(
                    PerunDialogues, self.context.perun_dialogues
                )
                request = ClosePayChReq(session_id=session_id, ch_id=channel.ch_id)
                message, self.dialogue = perun_dialogues.create(
                    counterparty=PERUN_CONNECTION_ID, performative=PerunGrpcMessage.Performative.REQUEST,
                    type=request.__class__.__name__, content=bytes(request))
                self.context.outbox.put_message(message=message)
                self.logger.debug("[{}] Close Channel with id {} from session {}".format(
                    self.context.agent_name, channel.ch_id, session_id))
                self.request_send = True
        elif not self._done:
            self.logger.debug("[{}] Channel closed with {}".format(self.context.agent_name, self.alias_bob))
            self._event = self.event_to_trigger
            self._done = True


class PerunAliceBehaviour(FSMBehaviour):

    BOB = "bob"
    ALIAS_BOB = "alias_{}".format(BOB)

    def __init__(self, **kwargs: Any):
        """Initialize the search behaviour."""
        super().__init__(**kwargs)
        # self._act_interval = cast(
        #    float, kwargs.pop("act_interval", 5)
        # )
        self.perun_scf: str = cast(str, kwargs.pop("scf", None))
        self._done = False

    def setup(self) -> None:
        """Implement the setup for the behaviour."""
        self.context.logger.info("Setup of PerunAliceBehaviour...")
        if self.perun_scf is None:
            raise ValueError("No session config file is given for Alice!")
        open_session_state = OpenSessionState(
            name="open-session-state", skill_context=self.context, scf=self.perun_scf,
            event_to_trigger="session-opened")
        self.register_state(name=open_session_state.name, state=open_session_state, initial=True)
        get_peer_id_state = GetPeerIdState(
            name="get-peer-id-state", alias_bob=self.BOB, skill_context=self.context, scf=self.perun_scf,
            event_to_trigger="peer-id-available")
        self.register_state(name=get_peer_id_state.name, state=get_peer_id_state)
        # Initial balance is set to 10ETH for alice and bob
        open_channel_state = OpenChannelState(
            name="open-channel-state", alias_bob=self.BOB, skill_context=self.context, scf=self.perun_scf,
            alice_amount='10', bob_amount='10', event_to_trigger="channel-opened")
        self.register_state(name=open_channel_state.name, state=open_channel_state)
        send_token_state = SendTokenState(
            name="send-token-state", alias_bob=self.BOB, skill_context=self.context, scf=self.perun_scf,
            token_to_send=1, event_to_trigger="send-token")
        self.register_state(name=send_token_state.name, state=send_token_state)
        send_token_state2 = SendTokenState(
            name="send-token-state2", alias_bob=self.BOB, skill_context=self.context, scf=self.perun_scf,
            token_to_send=1, event_to_trigger="send-token2")
        self.register_state(name=send_token_state2.name, state=send_token_state2)
        close_ch_state = CloseChannelState(
            name="close-ch-state", alias_bob=self.BOB, skill_context=self.context, scf=self.perun_scf,
            event_to_trigger="close-channel")
        self.register_state(name=close_ch_state.name, state=close_ch_state)
        close_session_state = CloseSessionState(
            name="close-session-state", skill_context=self.context, scf=self.perun_scf,
            event_to_trigger="session-closed")
        self.register_final_state(name=close_session_state.name, state=close_session_state)
        self.register_transition(source=open_session_state.name,
                                 destination=get_peer_id_state.name, event="session-opened")
        self.register_transition(source=get_peer_id_state.name,
                                 destination=open_channel_state.name, event="peer-id-available")
        self.register_transition(source=open_channel_state.name,
                                 destination=send_token_state.name, event="channel-opened")
        self.register_transition(source=send_token_state.name,
                                 destination=send_token_state2.name, event="send-token")
        self.register_transition(source=send_token_state2.name,
                                 destination=close_ch_state.name, event="send-token2")
        self.register_transition(source=close_ch_state.name,
                                 destination=close_session_state.name, event="close-channel")

    # def act(self) -> None:
    #    self.context.logger.debug("Act of PerunAliceBehaviour called and setting up environment...")
    #     state_behaviours = FSMBehaviour(name="alice-state-behaviour")
    #     open_session_state = OpenSessionState(
    #         name="open-session-state", skill_context=self.context, scf=self.perun_scf, event="session-opened")
    #     state_behaviours.register_state(name="open-session", state=open_session_state, initial=True)
    #     get_peer_id_state = GetPeerIdState(
    #         name="get_peer_id_state", skill_context=self.context, scf=self.perun_scf, event="peer-id-available")
    #     state_behaviours.register_state(name="get-peer-id", state=get_peer_id_state)
    #     state_behaviours.register_transition(source="open-session", destination="get-peer-id", event="session-opened")
    #     self.context.new_behaviours.put(state_behaviours)
        # behaviours.append(PerunOpenSessionBehaviour(
        #             name="alice_open_session", skill_context=self.context, scf=self.perun_scf))
        # behaviours.append(PerunGetPeerIdBehaviour(
        #             name=self.ALIAS_BOB, skill_context=self.context, alias=self.BOB, session_id=session_id)))

        # sequence_behaviour=SequenceBehaviour(behaviour_sequence = behaviours, name = "perun_alice_sequence")
        # self.context.new_behaviours.put(sequence_behaviour)
        # if not self._done:
        #     perun_sessions = cast(PerunSessions, self.context.perun_sessions)
        #     session_id = self._get_key_for_session_config(self.perun_scf, perun_sessions.sessions)
        #     if not self.perun_scf is None and session_id is None:
        #         self.context.logger.info("Alice is opening session...")
        #         self.context.new_behaviours.put(PerunOpenSessionBehaviour(
        #             name="alice_open_session", skill_context=self.context, scf=self.perun_scf))
        #     elif not session_id is None and not self.BOB in perun_sessions.sessions.get(session_id).peer_ids.keys():
        #         self.context.logger.info("Alice is getting PeerId alias of {}".format(self.BOB))
        #         self.context.new_behaviours.put(PerunGetPeerIdBehaviour(
        #             name=self.ALIAS_BOB, skill_context=self.context, alias=self.BOB, session_id=session_id))
        # elif not session_id is None and self.BOB in perun_sessions.sessions.get(session_id).peer_ids.keys():
        #     self.context.logger.info("Alice is closing session id {} for config {}".format(
        #         session_id, self.perun_scf))
        #     self.context.new_behaviours.put(PerunCloseSessionBehaviour(
        #         name="alice_close_session", skill_context=self.context, session_id=session_id))
        #     self._done = True

    # def _get_key_for_session_config(self, scf: str, sessions: Dict[str, PerunSession]) -> str:
    #     if len(sessions.keys()):
    #         for k, v in sessions.items():
    #             if v.config_file == scf:
    #                 return k
    #     return None

    def teardown(self) -> None:
        self.context.logger.info("Teardown of PerunAliceBehaviour...")
