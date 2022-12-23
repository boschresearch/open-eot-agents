# Copyright (c) 2022 - for information on the respective copyright owner see the NOTICE file and/or the repository https://github.com/boschresearch/open-eot-agents.
#
# SPDX-License-Identifier: Apache-2.0

"""This package contains a scaffold of a handler."""

from typing import Optional, cast

from aea.exceptions import AEAEnforceError
from aea.mail.base import Envelope
from aea.configurations.base import PublicId
from aea.protocols.base import Message
from aea.skills.base import Handler

from packages.bosch.protocols.perun_grpc.message import PerunGrpcMessage
from packages.bosch.protocols.perun_grpc.grpc_message import *
from packages.bosch.skills.perun.dialogues import PerunDialogue, PerunDialogues
from packages.bosch.skills.perun.session import PerunSession, PerunSessions
from packages.bosch.skills.perun.strategy import PayChannelStrategy


class PerunHandler(Handler):
    """This class scaffolds a handler."""

    SUPPORTED_PROTOCOL = PerunGrpcMessage.protocol_id  # type: Optional[PublicId]

    def setup(self) -> None:
        """Implement the setup."""
        self.context.logger.info("Setup of PerunHandler...")

    def handle(self, message: Message) -> None:
        """
        Implement the reaction to an envelope.

        :param message: the message
        """
        perun_msg = cast(PerunGrpcMessage, message)
        self.context.logger.info("Got message to handle {}".format(perun_msg))
        perun_dialogues = cast(
            PerunDialogues, self.context.perun_dialogues
        )
        perun_dialogue = cast(
            Optional[PerunDialogue], perun_dialogues.update(perun_msg)
        )
        if perun_dialogue is None:
            self.context.logger.warning("received invalid perun_msg={}, unidentified dialogue.".format(
                perun_msg))
            return
        if perun_msg.performative is PerunGrpcMessage.Performative.REQUEST:
            self.context.logger.warning(
                "cannot handle perun message of performative={} in dialogue={}.".format(
                    perun_msg.performative, perun_dialogue
                )
            )
        # checking and handling RESPONSE and PAYCHRESP performatives.
        # Ignoring END, as there is nothing to do, as it is just marking the end.
        elif perun_msg.performative is PerunGrpcMessage.Performative.RESPONSE:
            if perun_msg.type == 'OpenSessionRespMsgSuccess':
                self.handle_open_session_resp(perun_msg, perun_dialogue)
            elif perun_msg.type == 'CloseSessionRespMsgSuccess':
                self.handle_close_session_resp(perun_msg, perun_dialogue)
            elif perun_msg.type == 'GetPeerIdRespMsgSuccess':
                self.handle_get_peer_id_resp(perun_msg, perun_dialogue)
            else:
                # TODO: Handle error message
                self.context.logger.warning(
                    "cannot handle perun message of performative={} in dialogue={}.".format(
                        perun_msg.performative, perun_dialogue
                    )
                )
        elif perun_msg.performative is PerunGrpcMessage.Performative.PAYCHRESP:
            if perun_msg.type == 'SubPayChProposalsResp':
                self.handle_pay_ch_prop_resp(perun_msg, perun_dialogue)
            elif perun_msg.type == 'RespondPayChProposalResp':
                self.handle_pay_ch_prop_resp_resp(perun_msg, perun_dialogue)
            elif perun_msg.type == 'SubPayChUpdatesResp':
                self.handle_pay_ch_update(perun_msg, perun_dialogue)
            elif perun_msg.type == 'RespondPayChUpdateResp':
                self.handle_pay_ch_update_resp(perun_msg, perun_dialogue)

    def handle_open_session_resp(self, perun_msg: PerunGrpcMessage, perun_dialogue: PerunDialogue) -> None:
        perun_sessions = cast(PerunSessions, self.context.perun_sessions)
        response = OpenSessionRespMsgSuccess().parse(perun_msg.content)
        request = cast(Optional[PerunGrpcMessage], perun_dialogue.last_outgoing_message)
        if request is None:
            self.context.logger.warning("no request existing for response {}, unidentified dialogue.".format(
                response))
            return
        if request.type == 'OpenSessionReq':
            osr = OpenSessionReq().parse(request.content)
            self.context.logger.info("Got session id {} for config file {}. Adding to shared state."
                                     .format(response.session_id, osr.config_file))
            perun_sessions.sessions.update({response.session_id: PerunSession(
                is_open=True, config_file=osr.config_file, restored_chs=response.restored_chs)})
        else:
            self.context.logger.error("No corresponding request {} found for response {}".format(request, response))

    def handle_close_session_resp(self, perun_msg: PerunGrpcMessage, perun_dialogue: PerunDialogue) -> None:
        perun_sessions = cast(PerunSessions, self.context.perun_sessions)
        response = CloseSessionRespMsgSuccess().parse(perun_msg.content)
        request = cast(Optional[PerunGrpcMessage], perun_dialogue.last_outgoing_message)
        if request is None:
            self.context.logger.warning("no request existing for response {}, unidentified dialogue.".format(
                response))
            return
        if request.type == 'CloseSessionReq':
            csr = CloseSessionReq().parse(request.content)
            self.context.logger.info(
                "Got closing session response for session id {}. Removing from context.".format(csr.session_id))
            try:
                perun_sessions.sessions.get(csr.session_id).is_open = False
                self.context.logger.info(
                    "Set is_open to False for session_id {}".format(
                        csr.session_id))
            except IndexError as error:
                self.context.logger.error("No key find in shared_state for session_id {}".format(csr.session_id))
        else:
            self.context.logger.error("No corresponding request {} found for response {}".format(request, response))

    def handle_get_peer_id_resp(self, perun_msg: PerunGrpcMessage, perun_dialogue: PerunDialogue) -> None:
        perun_sessions = cast(PerunSessions, self.context.perun_sessions)
        response = GetPeerIdRespMsgSuccess().parse(perun_msg.content)
        request = cast(Optional[PerunGrpcMessage], perun_dialogue.last_outgoing_message)
        if request.type == "GetPeerIdReq":
            get_peer_id_req = GetPeerIdReq().parse(request.content)
            self.context.logger.info("Adding PeerId {} for session_id {} and alias {} to shared state.".format(
                response.peer_id, get_peer_id_req.session_id, get_peer_id_req.alias))
            perun_sessions.sessions.get(
                get_peer_id_req.session_id).peer_ids.update(
                {get_peer_id_req.alias: response.peer_id})
        else:
            self.context.logger.error("No corresponding request {} found for response {}".format(request, response))

    def handle_pay_ch_prop_resp(self, perun_msg: PerunGrpcMessage, perun_dialogue: PerunDialogue) -> None:
        proposal = SubPayChProposalsResp().parse(perun_msg.content)
        # check for error in proposal
        if betterproto.which_one_of(proposal, "response")[0] == "error":
            self.context.logger.error("Error retrieved at pay_ch_prop: {}".format(proposal.error))
            # handle error for notif already existent or session id not existent
        else:  # notify is set
            perun_pay_ch_strategy = cast(PayChannelStrategy, self.context.perun_pay_ch_strategy)
            resMess = None
            if perun_pay_ch_strategy.is_proposal_valid(proposal.notify):
                # accepting proposal
                resMess = perun_dialogue.reply(performative=PerunGrpcMessage.Performative.ACCEPT,
                                               target_message=perun_msg)
            else:
                # rejecting proposal
                resMess = perun_dialogue.reply(performative=PerunGrpcMessage.Performative.REJECT,
                                               target_message=perun_msg)
            if resMess is not None:
                self.context.outbox.put_message(resMess)

    def handle_pay_ch_prop_resp_resp(self, perun_msg: PerunGrpcMessage, perun_dialogue: PerunDialogue) -> None:
        perun_sessions = cast(PerunSessions, self.context.perun_sessions)
        response = RespondPayChProposalResp().parse(perun_msg.content)
        last_message = cast(Optional[PerunGrpcMessage], perun_dialogue.last_outgoing_message)
        # if success and last message was accept open corresponding entry in session for payment channel
        if betterproto.which_one_of(response, "response")[0] == "msg_success" and \
                last_message.performative == PerunGrpcMessage.Performative.ACCEPT:
            session = perun_sessions.sessions[perun_msg.session_id]
            session.channels.update({response.msg_success.opened_pay_ch_info.ch_id:
                                    response.msg_success.opened_pay_ch_info})
            self.context.logger.info("Added channel info to session {}: {}".format(
                perun_msg.session_id, response.msg_success.opened_pay_ch_info))

    def handle_pay_ch_update(self, perun_msg: PerunGrpcMessage, perun_dialogue: PerunDialogue) -> None:
        perun_sessions = cast(PerunSessions, self.context.perun_sessions)
        update = SubPayChUpdatesResp().parse(perun_msg.content)
        perun_pay_ch_strategy = cast(PayChannelStrategy, self.context.perun_pay_ch_strategy)
        resMess = None
        if betterproto.which_one_of(update, "response")[0] == "notify":
            # checking if bal_info is technically valid and channel id is existing
            if not perun_pay_ch_strategy.is_bal_info_valid(update.notify.proposed_pay_ch_info.bal_info) and \
                    not update.notify.proposed_pay_ch_info.ch_id in perun_sessions.sessions[perun_msg.session_id].channels:
                self.context.logger("Rejecting proposal as it is not valid: {}".format(perun_msg))
                resMess = perun_dialogue.reply(performative=PerunGrpcMessage.Performative.REJECT,
                                               target_message=perun_msg)
            elif update.notify.type == SubPayChUpdatesRespNotifyChUpdateType.open:
                # storing proposed channel update
                perun_sessions.sessions[perun_msg.session_id].prop_ch_updates.update(
                    {update.notify.proposed_pay_ch_info.ch_id: update.notify})
                # check if update is valid and respond to it
                if perun_pay_ch_strategy.is_ch_upd_valid(update.notify, perun_sessions.sessions[perun_msg.session_id]):
                    resMess = perun_dialogue.reply(performative=PerunGrpcMessage.Performative.ACCEPT,
                                                   target_message=perun_msg)
                else:
                    resMess = perun_dialogue.reply(performative=PerunGrpcMessage.Performative.REJECT,
                                                   target_message=perun_msg)
            elif update.notify.type == SubPayChUpdatesRespNotifyChUpdateType.final:
                perun_sessions.sessions[perun_msg.session_id].prop_ch_updates.update(
                    {update.notify.proposed_pay_ch_info.ch_id: update.notify})
                if perun_pay_ch_strategy.is_ch_upd_final_valid(
                        update.notify, perun_sessions.sessions[perun_msg.session_id]):
                    resMess = perun_dialogue.reply(performative=PerunGrpcMessage.Performative.ACCEPT,
                                                   target_message=perun_msg)
                else:
                    resMess = perun_dialogue.reply(performative=PerunGrpcMessage.Performative.REJECT,
                                                   target_message=perun_msg)
            elif update.notify.type == SubPayChUpdatesRespNotifyChUpdateType.closed:
                # removing channel from session
                perun_sessions.sessions[perun_msg.session_id].channels.pop(update.notify.proposed_pay_ch_info.ch_id)
                # TODO: check if needed?
                # terminating protocol and dialogue
                resMess = perun_dialogue.reply(performative=PerunGrpcMessage.Performative.END,
                                               target_message=perun_msg)
        if resMess is not None:
            self.context.outbox.put_message(resMess)

    def handle_pay_ch_update_resp(self, perun_msg: PerunGrpcMessage, perun_dialogue: PerunDialogue) -> None:
        perun_sessions = cast(PerunSessions, self.context.perun_sessions)
        perun_pay_ch_strategy = cast(PayChannelStrategy, self.context.perun_pay_ch_strategy)
        update = RespondPayChUpdateResp().parse(perun_msg.content)
        # also checking for higher version number
        if perun_pay_ch_strategy.is_bal_info_valid(
                update.msg_success.updated_pay_ch_info.bal_info) and betterproto.which_one_of(
                update, "response")[0] == "msg_success" and int(
                update.msg_success.updated_pay_ch_info.version) > int(
                perun_sessions.sessions[perun_msg.session_id].channels[update.msg_success.updated_pay_ch_info.ch_id].
                version):
            # storing channel update in case of success
            self.context.logger.info("Updating channel state for session {}: {}".format(
                perun_msg.session_id, update.msg_success.updated_pay_ch_info))
            perun_sessions.sessions[perun_msg.session_id].channels.update(
                {update.msg_success.updated_pay_ch_info.ch_id: update.msg_success.updated_pay_ch_info})
            # removing corresponding proposed state if still existent
            last_message = cast(Optional[PerunGrpcMessage], perun_dialogue.last_outgoing_message)
            try:
                if last_message.performative == PerunGrpcMessage.Performative.PAYCHRESP and \
                        last_message.type != None and last_message.type == 'SubPayChUpdatesResp':
                    last_resp = SubPayChUpdatesResp().parse(last_message.content)
                    if update.msg_success.updated_pay_ch_info.ch_id in perun_sessions.sessions[perun_msg.session_id].prop_ch_updates \
                            and last_resp.notify.update_id == \
                            perun_sessions.sessions[perun_msg.session_id].prop_ch_updates[update.msg_success.updated_pay_ch_info.ch_id].update_id:
                        self.context.logger.debug("Removing proposed channel update for session {}: {}".format(
                            perun_msg.session_id, perun_sessions.sessions
                            [perun_msg.session_id].prop_ch_updates
                            [update.msg_success.updated_pay_ch_info.ch_id]))
                        perun_sessions.sessions[perun_msg.session_id].prop_ch_updates.pop(
                            update.msg_success.updated_pay_ch_info.ch_id)
            except AEAEnforceError as exc:
                self.context.logger.warn("{}".format(exc))
            resMess = perun_dialogue.reply(performative=PerunGrpcMessage.Performative.END,
                                           target_message=perun_msg)
            self.context.outbox.put_message(resMess)

    def teardown(self) -> None:
        """Implement the handler teardown."""
        self.context.logger.info("Teardown of PerunHandler...")
