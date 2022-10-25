# Copyright (c) 2022 - for information on the respective copyright owner see the NOTICE file and/or the repository https://github.com/boschresearch/open-eot-agents.
#
# SPDX-License-Identifier: Apache-2.0

"""This package contains a scaffold of a handler."""

from typing import Optional, cast

from aea.configurations.base import PublicId
from aea.protocols.base import Message
from aea.skills.base import Handler

from packages.bosch.protocols.perun_grpc.message import PerunGrpcMessage
from packages.bosch.protocols.perun_grpc.grpc_message import *
from packages.bosch.skills.perun.dialogues import PerunDialogue, PerunDialogues


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
        elif perun_msg.performative is PerunGrpcMessage.Performative.RESPONSE:
            if perun_msg.type == 'OpenSessionRespMsgSuccess':
                self._handle_open_session_resp(perun_msg, perun_dialogue)
            elif perun_msg.type == 'CloseSessionRespMsgSuccess':
                self._handle_close_session_resp(perun_msg, perun_dialogue)
            else:
                self.context.logger.warning(
                    "cannot handle perun message of performative={} in dialogue={}.".format(
                        perun_msg.performative, perun_dialogue
                    )
                )

    def _handle_open_session_resp(self, perun_msg: PerunGrpcMessage, perun_dialogue: PerunDialogue) -> None:
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
            self.context.shared_state.update({osr.config_file: response.session_id})
        else:
            self.context.logger.error("No corresponding request {} found for response {}".format(request, response))

    def _handle_close_session_resp(self, perun_msg: PerunGrpcMessage, perun_dialogue: PerunDialogue) -> None:
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
                key = [k for k, v in self.context.shared_state.items() if v == csr.session_id][0]
                del self.context.shared_state[key]
                self.context.logger.info("Removed session_id {} from shared state with config file {}".format(
                    csr.session_id, key))
            except IndexError as error:
                self.context.logger.error("No key find in shared_state for session_id {}".format(csr.session_id))
        else:
            self.context.logger.error("No corresponding request {} found for response {}".format(request, response))

    def teardown(self) -> None:
        """Implement the handler teardown."""
        self.context.logger.info("Teardown of PerunHandler...")
