# -*- coding: utf-8 -*-
# Copyright (c) 2022 - for information on the respective copyright owner see the NOTICE file and/or the repository https://github.com/boschresearch/open-eot-agents.
#
# SPDX-License-Identifier: Apache-2.0

from concurrent.futures import ThreadPoolExecutor
import logging
import betterproto
import janus
from typing import cast, Optional, List

from aea.mail.base import Envelope
from packages.bosch.connections.perun_node.channel import ChannelProposalListener, ChannelUpdateListener
from packages.bosch.protocols.perun_grpc.dialogues import PerunGrpcDialogue, PerunGrpcDialogues

from packages.bosch.protocols.perun_grpc.grpc_message import (
    CloseSessionReq, OpenSessionReq, OpenSessionRespMsgSuccess, PaymentApiStub, RespondPayChProposalReq,
    RespondPayChUpdateReq, SubPayChProposalsResp, SubPayChUpdatesResp)
from packages.bosch.protocols.perun_grpc.message import PerunGrpcMessage


class PerunSession():

    def __init__(
            self, payment_api_stub: PaymentApiStub, in_queue: janus.Queue[Envelope],
            thread_pool: ThreadPoolExecutor, futures: List, agent_name: str) -> None:
        self._logger = logging.getLogger(__name__)
        self._payment_api_stub = payment_api_stub
        self._in_queue = in_queue
        self._thread_pool = thread_pool
        self._futures = futures
        self._agent_name = agent_name

    async def open_session(self, message: PerunGrpcMessage, dialogue: PerunGrpcDialogue, dialogues: PerunGrpcDialogues) -> None:
        """
        Open a session at target perun node.
        After succesfull session open it will register a listener for channel proposals.

        :param message: PerunGrpcMessage containing OpenSessionReq
        :param dialogue: corresponding PerunGrpcDialogue for the message
        """
        self._logger.debug("[{}] Open session called with message {}".format(self._agent_name, message))
        req = OpenSessionReq().parse(message.content)
        resp = await self._payment_api_stub.open_session(req)
        if betterproto.which_one_of(resp, "response")[1] != None:
            resMess = dialogue.reply(
                performative=PerunGrpcMessage.Performative.RESPONSE,
                target_message=message,
                content=bytes(betterproto.which_one_of(resp, "response")[1]),
                type=betterproto.which_one_of(resp, "response")[1].__class__.__name__)
            envelope = Envelope(to=resMess.to, sender=resMess.sender, message=resMess)
            # register and start listener for channel proposals in case of no error
            if betterproto.which_one_of(resp, "response")[1].__class__.__name__ == 'OpenSessionRespMsgSuccess':
                osr = cast(OpenSessionRespMsgSuccess, betterproto.which_one_of(resp, "response")[1])
                thread = ChannelProposalListener(
                    payment_api_stub=self._payment_api_stub, in_queue=self._in_queue, session_id=osr.session_id,
                    counterparty=resMess.to, dialogues=dialogues, agent_name=self._agent_name)
                # thread.start()
                future = self._thread_pool.submit(thread.run)
                self._futures.append(thread)
                self._logger.debug(
                    "[{}] Thread ChannelProposalListener started for session_id {}".format(
                        self._agent_name, osr.session_id))
            if self._in_queue is not None:
                await self._in_queue.async_q.put(envelope)

    async def close_session(self, message: PerunGrpcMessage, dialogue: PerunGrpcDialogue) -> None:
        self._logger.debug("[{}] Close session called with message {}".format(self._agent_name, message))
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

    async def send_proposal_reply(self, message: PerunGrpcMessage, dialogue: PerunGrpcDialogue, dialogues: PerunGrpcDialogues) -> None:
        self._logger.debug("[{}] Sending proposal reply for message {}".format(self._agent_name, message))
        last_message = cast(Optional[PerunGrpcMessage], dialogue.last_outgoing_message)
        if last_message is not None:
            proposal = SubPayChProposalsResp().parse(last_message.content)
            self._logger.debug("[{}] last proposal is {}".format(self._agent_name, proposal.to_json()))
            status: bool = False
            if message.performative == PerunGrpcMessage.Performative.ACCEPT:
                status = True
            response = await self._payment_api_stub.respond_pay_ch_proposal(RespondPayChProposalReq(session_id=last_message.session_id,
                                                                            proposal_id=proposal.notify.proposal_id, accept=status))
            # sending response to corresponding skill
            self._logger.debug("[{}] got response: {}".format(self._agent_name, response))
            resMess = dialogue.reply(
                performative=PerunGrpcMessage.Performative.PAYCHRESP,
                session_id=last_message.session_id,
                target_message=message,
                content=bytes(response),
                type=response.__class__.__name__)
            envelope = Envelope(to=resMess.to, sender=resMess.sender, message=resMess)
            if betterproto.which_one_of(response, "response")[0] == "msg_success" and status:
                # Open channel listener in case of successfull accept
                thread = ChannelUpdateListener(
                    payment_api_stub=self._payment_api_stub, in_queue=self._in_queue, session_id=last_message.session_id,
                    counterparty=resMess.to, agent_name=self._agent_name, channel_id=response.msg_success.opened_pay_ch_info.ch_id, dialogues=dialogues)
                # thread.start()
                future = self._thread_pool.submit(thread.run)
                self._futures.append(thread)
            if self._in_queue is not None:
                self._logger.debug("[{}] sending respond_pay_ch_proposal {}".format(self._agent_name, envelope))
                await self._in_queue.async_q.put(envelope)

    async def send_ch_update_reply(self, message: PerunGrpcMessage, dialogue: PerunGrpcDialogue, dialogues: PerunGrpcDialogues) -> None:
        self._logger.debug("[{}] Sending channel update reply for message {}".format(self._agent_name, message))
        last_message = cast(Optional[PerunGrpcMessage], dialogue.last_outgoing_message)
        if last_message is not None:
            proposal = SubPayChUpdatesResp().parse(last_message.content)
            status: bool = False
            if message.performative == PerunGrpcMessage.Performative.ACCEPT:
                status = True
            response = await self._payment_api_stub.respond_pay_ch_update(
                RespondPayChUpdateReq(session_id=last_message.session_id,
                                      ch_id=proposal.notify.proposed_pay_ch_info.ch_id,
                                      update_id=proposal.notify.update_id, accept=status))
            # sending response to corresponding skill
            resMess = dialogue.reply(
                performative=PerunGrpcMessage.Performative.PAYCHRESP,
                session_id=last_message.session_id,
                target_message=message,
                content=bytes(response),
                type=response.__class__.__name__)
            envelope = Envelope(to=resMess.to, sender=resMess.sender, message=resMess)
            self._logger.debug("[{}] Got reply for respond_pay_ch_update and sending {}".format(
                self._agent_name, envelope))
            if self._in_queue is not None:
                await self._in_queue.async_q.put(envelope)
