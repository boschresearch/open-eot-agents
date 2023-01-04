# -*- coding: utf-8 -*-
# Copyright (c) 2022 - for information on the respective copyright owner see the NOTICE file and/or the repository https://github.com/boschresearch/open-eot-agents.
#
# SPDX-License-Identifier: Apache-2.0

from concurrent.futures import Future, ThreadPoolExecutor
import logging
import janus
from typing import Any, Optional, cast

from grpclib.client import Channel
from aea.common import Address
from aea.configurations.base import PublicId
from aea.connections.base import Connection, ConnectionStates
from aea.mail.base import Envelope, Message
from aea.protocols.dialogue.base import Dialogue as BaseDialogue

from packages.bosch.connections.perun_node.id_provider import DefaultIdProvider
from packages.bosch.connections.perun_node.session import PerunSession
from packages.bosch.protocols.perun_grpc.dialogues import PerunGrpcDialogue, PerunGrpcDialogues
from packages.bosch.protocols.perun_grpc.message import PerunGrpcMessage
from packages.bosch.protocols.perun_grpc.grpc_message import *

CONNECTION_ID = PublicId.from_str("bosch/perun_node:0.1.0")

CONFIG_HOST = "host"
CONFIG_PORT = "port"


class PerunNodeDialogues(PerunGrpcDialogues):

    def __init__(self) -> None:

        def role_from_first_message(  # pylint: disable=unused-argument
            message: Message, receiver_address: Address
        ) -> BaseDialogue.Role:
            """Infer the role of the agent from an incoming/outgoing first message
            :param message: an incoming/outgoing first message
            :param receiver_address: the address of the receiving agent
            :return: The role of the agent
            """
            # The client connection maintains the dialogue on behalf of the server
            return PerunGrpcDialogue.Role.SERVER

        PerunGrpcDialogues.__init__(
            self,
            self_address=str(PerunNodeConnection.connection_id),
            role_from_first_message=role_from_first_message,
            dialogue_class=PerunGrpcDialogue)


class PerunNodeConnection(Connection):
    """Proxy to the functionality of the SDK or API."""

    connection_id = CONNECTION_ID

    def __init__(self, **kwargs: Any) -> None:
        """
        Initialize the connection.

        The configuration must be specified if and only if the following
        parameters are None: connection_id, excluded_protocols or restricted_to_protocols.

        Possible keyword arguments:
        - configuration: the connection configuration.
        - data_dir: directory where to put local files.
        - identity: the identity object held by the agent.
        - crypto_store: the crypto store for encrypted communication.
        - restricted_to_protocols: the set of protocols ids of the only supported protocols for this connection.
        - excluded_protocols: the set of protocols ids that we want to exclude for this connection.

        :param kwargs: keyword arguments passed to component base
        """
        super().__init__(**kwargs)  # pragma: no cover
        self.logger = logging.getLogger("packages.bosch.connections.perun_node.connection")
        self.host = cast(str, self.configuration.config.get(CONFIG_HOST))
        self.port = cast(str, self.configuration.config.get(CONFIG_PORT))
        self._in_queue: janus.Queue[Envelope] = None
        self._dialogues = PerunNodeDialogues()
        self._perun_session = None
        self._executor = None
        self._threads = None

    async def connect(self) -> None:
        """
        Set up the connection.

        In the implementation, remember to update 'connection_status' accordingly.
        """
        if (
            self.host is None or self.port is None
        ):  # pragma: nocover
            raise ValueError("[{}] host and port must be set!".format(self._identity.name))
        if self.state == ConnectionStates.disconnected:
            self.state = ConnectionStates.connecting
            self._channel = Channel(host=self.host, port=self.port)
            self._payment_api_stub = PaymentApiStub(channel=self._channel)
            self.state = ConnectionStates.connected
            self._in_queue = janus.Queue()
            self._executor = ThreadPoolExecutor()
            self._threads = []
            self._perun_session = PerunSession(self._payment_api_stub, self._in_queue,
                                               self._executor, self._threads, self._identity.name)
            self._perun_id_provider = DefaultIdProvider(self._payment_api_stub, self._in_queue, self._identity.name)
            self.state = ConnectionStates.connected
            self.logger.info("[{}] Node connected to {}:{}".format(self._identity.name, self.host, self.port))
        else:
            self.logger.warn("[{}] Connecting not possible as already connected!".format(self._identity.name))

    async def disconnect(self) -> None:
        """
        Tear down the connection.

        In the implementation, remember to update 'connection_status' accordingly.
        """
        if self.state == ConnectionStates.connected:
            self.logger.info("[{}] Disconnecting node {}:{} ...".format(self._identity.name, self.host, self.port))
            if self._channel == None:
                raise ValueError("[{}] Channel is not set or already closed!".format(self._identity.name))
            self.state = ConnectionStates.disconnecting
            self._executor.shutdown(wait=False)
            for thread in self._threads:
                await thread.shutdown()
            self._channel.close()
            self._in_queue.close()
            await self._in_queue.wait_closed()
            self.state = ConnectionStates.disconnected
            self.logger.info("[{}] Node {}:{} disonnected.".format(self._identity.name, self.host, self.port))
        else:
            self.logger.warn("[{}] Disconnecting not possible, as connection is not connected!".format(
                self._identity.name))

    async def send(self, envelope: Envelope) -> None:
        """
        Send an envelope.

        :param envelope: the envelope to send.
        """
        message = cast(PerunGrpcMessage, envelope.message)
        self.logger.info("[{}] Sending message to perun node {}".format(self._identity.name, message))
        if (
            message.performative != PerunGrpcMessage.Performative.REQUEST
            and message.performative != PerunGrpcMessage.Performative.ACCEPT
            and message.performative != PerunGrpcMessage.Performative.REJECT
            and message.performative != PerunGrpcMessage.Performative.END
        ):  # pragma: nocover
            self.logger.warning(
                "[{}] The PerunGrpcMessage performative must be a REQUEST, ACCEPT, REJECT or END. Envelop dropped.".format(self._identity.name)
            )
            return
        if self._payment_api_stub == None:
            raise ValueError("[{}] Pament stub is not set...".format(self._identity.name))
        dialogue = cast(Optional[PerunGrpcDialogue], self._dialogues.update(message))
        if not dialogue:
            self.logger.warning("[{}] Could not create PerunGrpcDialogue for message={}".format(
                self._identity.name, message))
            return
        # end performative is just terminating the dialogue, so nothing to do here
        elif message.performative != PerunGrpcMessage.Performative.END:
            # first checking for accept or reject as here message.type is not set
            if message.performative == PerunGrpcMessage.Performative.ACCEPT or \
                    message.performative == PerunGrpcMessage.Performative.REJECT:
                last_message = cast(PerunGrpcMessage, dialogue.last_outgoing_message)
                # check for pay channel proposal
                if last_message.type == 'SubPayChProposalsResp':
                    await self._perun_session.send_proposal_reply(message, dialogue, self._dialogues)
                # check for pay channel update
                elif last_message.type == 'SubPayChUpdatesResp':
                    await self._perun_session.send_ch_update_reply(message, dialogue, self._dialogues)
            elif message.type == 'OpenSessionReq':
                await self._perun_session.open_session(message, dialogue, self._dialogues)
            elif message.type == 'CloseSessionReq':
                await self._perun_session.close_session(message, dialogue)
            elif message.type == 'AddPeerIdReq':
                await self._perun_id_provider.add_peer_id(message, dialogue)
            elif message.type == 'GetPeerIdReq':
                await self._perun_id_provider.get_peer_id(message, dialogue)

    async def receive(self, *args: Any, **kwargs: Any) -> Optional[Envelope]:
        """
        Receive an envelope. Blocking.

        :param args: arguments to receive
        :param kwargs: keyword arguments to receive
        :return: the envelope received, if present.  # noqa: DAR202
        """
        if self._in_queue is None:
            #    raise ValueError("Node seems not to be connected!")
            return None
        return await self._in_queue.async_q.get()
