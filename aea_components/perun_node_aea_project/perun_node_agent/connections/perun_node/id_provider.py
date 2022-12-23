# -*- coding: utf-8 -*-
# Copyright (c) 2022 - for information on the respective copyright owner see the NOTICE file and/or the repository https://github.com/boschresearch/open-eot-agents.
#
# SPDX-License-Identifier: Apache-2.0

import logging
import betterproto
import janus

from aea.mail.base import Envelope
from packages.bosch.protocols.perun_grpc.dialogues import PerunGrpcDialogue

from packages.bosch.protocols.perun_grpc.grpc_message import AddPeerIdReq, GetPeerIdReq, PaymentApiStub
from packages.bosch.protocols.perun_grpc.message import PerunGrpcMessage


class DefaultIdProvider():

    def __init__(self, payment_api_stub: PaymentApiStub, in_queue: janus.Queue[Envelope], agent_name: str) -> None:
        self._logger = logging.getLogger(__name__)
        self._payment_api_stub = payment_api_stub
        self._in_queue = in_queue
        self._agent_name = agent_name

    async def add_peer_id(self, message: PerunGrpcMessage, dialogue: PerunGrpcDialogue) -> None:
        self._logger.debug("[{}] Add peer id called with {}".format(self._agent_name, message))
        req = AddPeerIdReq().parse(message.content)
        resp = await self._payment_api_stub.add_peer_id(req)
        if betterproto.which_one_of(resp, "response")[1] != None:
            resMess = dialogue.reply(
                performative=PerunGrpcMessage.Performative.RESPONSE,
                target_message=message,
                content=bytes(betterproto.which_one_of(resp, "response")[1]),
                type=betterproto.which_one_of(resp, "response")[1].__class__.__name__)
            envelope = Envelope(to=resMess.to, sender=resMess.sender, message=resMess)
            if self._in_queue is not None:
                await self._in_queue.async_q.put(envelope)

    async def get_peer_id(self, message: PerunGrpcMessage, dialogue: PerunGrpcDialogue) -> None:
        self._logger.debug("[{}] Get peer id called with {}".format(self._agent_name, message))
        req = GetPeerIdReq().parse(message.content)
        resp = await self._payment_api_stub.get_peer_id(req)
        if betterproto.which_one_of(resp, "response")[1] != None:
            resMess = dialogue.reply(
                performative=PerunGrpcMessage.Performative.RESPONSE,
                target_message=message,
                content=bytes(betterproto.which_one_of(resp, "response")[1]),
                type=betterproto.which_one_of(resp, "response")[1].__class__.__name__)
            envelope = Envelope(to=resMess.to, sender=resMess.sender, message=resMess)
            if self._in_queue is not None:
                await self._in_queue.async_q.put(envelope)
