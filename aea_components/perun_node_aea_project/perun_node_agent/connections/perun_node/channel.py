# -*- coding: utf-8 -*-
# Copyright (c) 2022 - for information on the respective copyright owner see the NOTICE file and/or the repository https://github.com/boschresearch/open-eot-agents.
#
# SPDX-License-Identifier: Apache-2.0

import asyncio
import asyncstdlib
import aiostream
import betterproto
import logging
import janus
from threading import Event
from typing import cast, List, AsyncIterator
from grpclib.client import Channel

from aea.mail.base import Envelope
from aea.protocols.base import Address
from packages.bosch.protocols.perun_grpc.dialogues import PerunGrpcDialogues

from packages.bosch.protocols.perun_grpc.grpc_message import (
    ErrorCode, PaymentApiStub, PayChInfo, SubPayChProposalsReq, SubPayChProposalsResp, SubpayChUpdatesReq,
    SubPayChUpdatesResp, SubPayChUpdatesRespNotifyChUpdateType)
from packages.bosch.protocols.perun_grpc.message import PerunGrpcMessage


class EventIterator(AsyncIterator):
    # constructor, define some state

    def __init__(self, event: asyncio.Event):
        self._event = event

    # create an instance of the iterator
    def __aiter__(self):
        return self

    # return the next awaitable
    async def __anext__(self):
        await asyncio.sleep(3)
        if not self._event.is_set():
            return False
        else:
            return True
        # check for no further items
        # await self._event.wait()

    async def __aexit__(self):
        try:
            pass
            print("Exit from the Context Manager...")
        finally:
            print("This line is not executed")


class ChannelProposalListener():

    def __init__(
            self, payment_api_stub: PaymentApiStub, in_queue: janus.Queue[Envelope],
            session_id: str, dialogues: PerunGrpcDialogues, counterparty: Address, agent_name: str):
        # Thread.__init__(self)
        self._logger = logging.getLogger(__name__)
        #self._channel = Channel(host='127.0.0.1', port=50001)
        #self._payment_api_stub = PaymentApiStub(channel=self._channel)
        #self._payment_api_stub = payment_api_stub
        self._in_queue = in_queue
        self._session_id = session_id
        self._dialogues = dialogues
        self._counterparty = counterparty
        self._agent_name = agent_name

    def run(self):
        self._logger.debug(
            "[{}] Starting handle_sub_pay_ch_proposals in own ChannelProposalListener for session_id {}".format(
                self._agent_name, self._session_id))
        asyncio.run(self.handle_sub_pay_ch_proposals())

    async def shutdown(self) -> None:
        self._logger.debug(
            "[{}] Shutdown called for ChannelProposalListener for session id {}".format(
                self._agent_name, self._session_id))
        # asyncio.get_event_loop().call_soon_threadsafe(self._shutdown.set)
        self._shutdown.set()

    async def handle_sub_pay_ch_proposals(self) -> None:
        self._logger.info("[{}] Start listening to channel proposals for session {}".format(
            self._agent_name, self._session_id))
        try:
            self._channel = Channel(host='127.0.0.1', port=50001)
            self._payment_api_stub = PaymentApiStub(channel=self._channel)
            req = SubPayChProposalsReq(self._session_id)
            self._shutdown = Event()
            iter = EventIterator(self._shutdown)
            proposal = self._payment_api_stub.sub_pay_ch_proposals(req)
            async with aiostream.stream.merge(iter, proposal).stream() as streamer:
                async for stream_proposal in streamer:
                    # check if shutdown is set and end task
                    if self._shutdown.is_set():
                        break
                    elif not stream_proposal is False:
                        self._logger.info("[{}] Got proposal for session_id {} from stream: {}".format(
                            self._agent_name, self._session_id, stream_proposal))
                        proposal = cast(SubPayChProposalsResp, stream_proposal)
                        message, dialogue = self._dialogues.create(
                            counterparty=self._counterparty, performative=PerunGrpcMessage.Performative.PAYCHRESP,
                            session_id=self._session_id, type=proposal.__class__.__name__, content=bytes(proposal))
                        envelope = Envelope(to=message.to, sender=message.sender, message=message)
                        self._logger.debug("[{}] handle_sub_pay_ch_proposals is sending {}".format(
                            self._agent_name, envelope))
                        await self._in_queue.async_q.put(envelope)
                        # check for error
                        if betterproto.which_one_of(proposal, "response")[0] == "error":
                            # Incorrect session ID is 201
                            # Subscription already exists is 202
                            if proposal.error.code == ErrorCode.ErrResourceNotFound or proposal.error.code == ErrorCode.ErrResourceExists:
                                # -> end listener
                                self._logger.error("[{}] Retrieved error {} {}. Ending listener for given session_id {}".format(
                                    self._agent_name, proposal.error.code, proposal.error.message, self._session_id))
                                break
        except Exception as e:
            self._logger.error("[{}] {}".format(self._agent_name, e))
        finally:
            self._logger.info("[{}] Ended listening to channel proposals for session {}".format(
                self._agent_name, self._session_id))


class ChannelUpdateListener():

    def __init__(
            self, payment_api_stub: PaymentApiStub, in_queue: janus.Queue[Envelope],
            session_id: str, channel_id: str, dialogues: PerunGrpcDialogues, counterparty: Address, agent_name: str):
        # Thread.__init__(self)
        self._logger = logging.getLogger(__name__)
        self._payment_api_stub = payment_api_stub
        self._in_queue = in_queue
        self._session_id = session_id
        self._channel_id = channel_id
        self._dialogues = dialogues
        self._counterparty = counterparty
        self._agent_name = agent_name
        #self._shutdown = asyncio.Event()

    def run(self):
        self._logger.debug(
            "[{}] Starting handle_sub_pay_ch_updates in own ChannelUpdateListener for session_id {} and channel id {}".format(
                self._agent_name, self._session_id, self._channel_id))
        asyncio.run(self.handle_sub_pay_ch_updates())

    async def shutdown(self) -> None:
        self._logger.debug(
            "[{}] Shutdown called for ChannelUpdateListener for session id {} and channel id {}".format(
                self._agent_name, self._session_id, self._channel_id))
        self._shutdown.set()

    async def handle_sub_pay_ch_updates(self) -> None:
        try:
            self._logger.info(
                "[{}] Start listening to channel updates for session {} and channel_id {}".format(
                    self._agent_name, self._session_id, self._channel_id))
            req = SubpayChUpdatesReq(self._session_id, self._channel_id)
            self._shutdown = Event()
            iter = EventIterator(self._shutdown)
            ch_upd_resp = self._payment_api_stub.sub_pay_ch_updates(req)
            # merging shutdown and response stream to be able to end loop by setting shutdown event
            async with aiostream.stream.merge(iter, ch_upd_resp).stream() as streamer:
                async for stream_update in streamer:
                    # check if shutdown is set and end task
                    if self._shutdown.is_set():
                        break
                    elif not stream_update is False:
                        self._logger.info("[{}] Got channel update for session_id {} and channel_id {}: {}".format(
                            self._agent_name, self._session_id, self._channel_id, stream_update))
                        update = cast(SubPayChUpdatesResp, stream_update)
                        message, dialogue = self._dialogues.create(
                            counterparty=self._counterparty, performative=PerunGrpcMessage.Performative.PAYCHRESP,
                            session_id=self._session_id, type=update.__class__.__name__,
                            content=bytes(update))
                        envelope = Envelope(to=message.to, sender=message.sender, message=message)
                        self._logger.debug("[{}] handle_sub_pay_ch_updates is sending {}".format(
                            self._agent_name, envelope))
                        await self._in_queue.async_q.put(envelope)
                        # check for error and handle it
                        if betterproto.which_one_of(update, "response")[0] == "error":
                            # 201 ResourceType: "session" when session ID is not known.
                            # 201 ResourceType: "channel" when channel ID is not known.
                            # 202 ResourceType: "updatesSub" when a subscription already exists.
                            # listener can be closed by using break
                            if update.error.code == ErrorCode.ErrResourceNotFound or \
                                    update.error.code == ErrorCode.ErrResourceExists:
                                self._logger.error(
                                    "[{}] Retrieved error {} in channel update for session id {} and channel {}, ending listener.".format(
                                        self._agent_name, update.error.code, self._session_id, self._channel_id))
                                break
                        else:
                            # no error, so check for closed state and then close listener by using break
                            if update.notify.type != None and update.notify.type == SubPayChUpdatesRespNotifyChUpdateType.closed:
                                self._logger.info(
                                    "[{}] Retrieved closed, stop listener for session id {} and channel {}".format(
                                        self._agent_name, self._session_id, self._channel_id))
                                break
        finally:
            self._logger.info(
                "[{}] Ended listening to channel updates for session {} and channel {}".format(
                    self._agent_name, self._session_id, self._channel_id))
