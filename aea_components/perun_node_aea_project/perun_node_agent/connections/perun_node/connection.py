# -*- coding: utf-8 -*-
# Copyright (c) 2022 - for information on the respective copyright owner see the NOTICE file and/or the repository https://github.com/boschresearch/open-eot-agents.
#
# SPDX-License-Identifier: Apache-2.0

import logging
import janus
from typing import Any, Optional, cast

from grpclib.client import Channel
from aea.common import Address
from aea.configurations.base import PublicId
from aea.connections.base import Connection, ConnectionStates
from aea.mail.base import Envelope, Message
from aea.protocols.dialogue.base import Dialogue as BaseDialogue

from packages.bosch.connections.perun_node.session import PerunSession
from packages.bosch.protocols.perun_grpc.dialogues import PerunGrpcDialogue, PerunGrpcDialogues
from packages.bosch.protocols.perun_grpc.message import PerunGrpcMessage
from packages.bosch.protocols.perun_grpc.grpc_message import *

CONNECTION_ID = PublicId.from_str("bosch/perun_node:0.1.0")

CONFIG_HOST = "host"
CONFIG_PORT = "port"

_default_logger = logging.getLogger("packages.bosch.connections.perun_node")


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
        self.logger = _default_logger
        self.host = cast(str, self.configuration.config.get(CONFIG_HOST))
        self.port = cast(str, self.configuration.config.get(CONFIG_PORT))
        self._in_queue = None
        self._dialogues = PerunNodeDialogues()
        self._perun_session = None

    async def connect(self) -> None:
        """
        Set up the connection.

        In the implementation, remember to update 'connection_status' accordingly.
        """
        if (
            self.host is None or self.port is None
        ):  # pragma: nocover
            raise ValueError("host and port must be set!")
        self._channel = Channel(host=self.host, port=self.port)
        self._payment_api_stub = PaymentApiStub(channel=self._channel)
        self.state = ConnectionStates.connected
        self._in_queue: janus.Queue[Envelope] = janus.Queue()
        self._perun_session = PerunSession(self._payment_api_stub, self._in_queue)
        _default_logger.info("Node connected to {}:{}".format(self.host, self.port))

    async def disconnect(self) -> None:
        """
        Tear down the connection.

        In the implementation, remember to update 'connection_status' accordingly.
        """
        if self._channel == None:
            raise ValueError("Channel is not set or already closed!")
        self._channel.close()
        self.state = ConnectionStates.disconnected
        self._in_queue.close()
        await self._in_queue.wait_closed()
        _default_logger.info("Node {}:{} disonnected.".format(self.host, self.port))

    async def send(self, envelope: Envelope) -> None:
        """
        Send an envelope.

        :param envelope: the envelope to send.
        """
        message = cast(PerunGrpcMessage, envelope.message)
        _default_logger.info("Sending message to perun node {}".format(message))
        if (
            message.performative != PerunGrpcMessage.Performative.REQUEST
        ):  # pragma: nocover
            self.logger.warning(
                "The PerunGrpcMessage performative must be a REQUEST. Envelop dropped."
            )
            return
        if self._payment_api_stub == None:
            raise ValueError("Pament stub is not set...")
        dialogue = cast(Optional[PerunGrpcDialogue], self._dialogues.update(message))
        if not dialogue:
            self.logger.warning("Could not create PerunGrpcDialogue for message={}".format(message))
            return
        if message.type == 'OpenSessionReq':
            await self._perun_session.open_session(message, dialogue)
        elif message.type == 'CloseSessionReq':
            await self._perun_session.close_session(message, dialogue)

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
