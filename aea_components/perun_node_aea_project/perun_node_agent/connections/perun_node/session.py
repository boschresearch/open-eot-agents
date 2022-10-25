# -*- coding: utf-8 -*-
# Copyright (c) 2022 - for information on the respective copyright owner see the NOTICE file and/or the repository https://github.com/boschresearch/open-eot-agents.
#
# SPDX-License-Identifier: Apache-2.0

import logging
import betterproto
import janus

from aea.mail.base import Envelope
from packages.bosch.protocols.perun_grpc.dialogues import PerunGrpcDialogue

from packages.bosch.protocols.perun_grpc.grpc_message import CloseSessionReq, OpenSessionReq, PaymentApiStub
from packages.bosch.protocols.perun_grpc.message import PerunGrpcMessage


class PerunSession():

    def __init__(self, payment_api_stub: PaymentApiStub, in_queue: janus.Queue[Envelope]) -> None:
        self._logger = logging.getLogger(__name__)
        self._payment_api_stub = payment_api_stub
        self._in_queue = in_queue

    async def open_session(self, message: PerunGrpcMessage, dialogue: PerunGrpcDialogue) -> None:
        self._logger.debug("Open session called with message {}".format(message))
        req = OpenSessionReq().parse(message.content)
        resp = await self._payment_api_stub.open_session(req)
        if betterproto.which_one_of(resp, "response")[1] != None:
            resMess = dialogue.reply(
                performative=PerunGrpcMessage.Performative.RESPONSE,
                target_message=message,
                content=bytes(betterproto.which_one_of(resp, "response")[1]),
                type=betterproto.which_one_of(resp, "response")[1].__class__.__name__)
            envelope = Envelope(to=resMess.to, sender=resMess.sender, message=resMess)
            if self._in_queue is not None:
                await self._in_queue.async_q.put(envelope)

    async def close_session(self, message: PerunGrpcMessage, dialogue: PerunGrpcDialogue) -> None:
        self._logger.debug("Close session called with message {}".format(message))
        req = CloseSessionReq().parse(message.content)
        resp = await self._payment_api_stub.close_session(req)
        if betterproto.which_one_of(resp, "response")[1] != None:
            resMess = dialogue.reply(
                performative=PerunGrpcMessage.Performative.RESPONSE,
                target_message=message,
                content=bytes(betterproto.which_one_of(resp, "response")[1]),
                type=betterproto.which_one_of(resp, "response")[1].__class__.__name__)
            envelope = Envelope(to=resMess.to, sender=resMess.sender, message=resMess)
            if self._in_queue is not None:
                await self._in_queue.async_q.put(envelope)
