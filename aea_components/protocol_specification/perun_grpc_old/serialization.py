# Copyright (c) 2022 - for information on the respective copyright owner see the NOTICE file and/or the repository https://github.com/boschresearch/open-eot-agents.
#
# SPDX-License-Identifier: Apache-2.0

# -*- coding: utf-8 -*-

"""Serialization module for perun_grpc protocol."""

# pylint: disable=too-many-statements,too-many-locals,no-member,too-few-public-methods,redefined-builtin
from typing import Any, Dict, cast

from aea.mail.base_pb2 import DialogueMessage
from aea.mail.base_pb2 import Message as ProtobufMessage
from aea.protocols.base import Message, Serializer

from packages.bosch.protocols.perun_grpc import perun_grpc_pb2
from packages.bosch.protocols.perun_grpc.message import PerunGrpcMessage


class PerunGrpcSerializer(Serializer):
    """Serialization for the 'perun_grpc' protocol."""

    @staticmethod
    def encode(msg: Message) -> bytes:
        """
        Encode a 'PerunGrpc' message into bytes.

        :param msg: the message object.
        :return: the bytes.
        """
        msg = cast(PerunGrpcMessage, msg)
        message_pb = ProtobufMessage()
        dialogue_message_pb = DialogueMessage()
        perun_grpc_msg = perun_grpc_pb2.PerunGrpcMessage()

        dialogue_message_pb.message_id = msg.message_id
        dialogue_reference = msg.dialogue_reference
        dialogue_message_pb.dialogue_starter_reference = dialogue_reference[0]
        dialogue_message_pb.dialogue_responder_reference = dialogue_reference[1]
        dialogue_message_pb.target = msg.target

        performative_id = msg.performative
        if performative_id == PerunGrpcMessage.Performative.REQUEST:
            performative = perun_grpc_pb2.PerunGrpcMessage.Request_Performative()  # type: ignore
            type = msg.type
            performative.type = type
            content = msg.content
            performative.content = content
            perun_grpc_msg.request.CopyFrom(performative)
        elif performative_id == PerunGrpcMessage.Performative.RESPONSE:
            performative = perun_grpc_pb2.PerunGrpcMessage.Response_Performative()  # type: ignore
            type = msg.type
            performative.type = type
            content = msg.content
            performative.content = content
            perun_grpc_msg.response.CopyFrom(performative)
        else:
            raise ValueError("Performative not valid: {}".format(performative_id))

        dialogue_message_pb.content = perun_grpc_msg.SerializeToString()

        message_pb.dialogue_message.CopyFrom(dialogue_message_pb)
        message_bytes = message_pb.SerializeToString()
        return message_bytes

    @staticmethod
    def decode(obj: bytes) -> Message:
        """
        Decode bytes into a 'PerunGrpc' message.

        :param obj: the bytes object.
        :return: the 'PerunGrpc' message.
        """
        message_pb = ProtobufMessage()
        perun_grpc_pb = perun_grpc_pb2.PerunGrpcMessage()
        message_pb.ParseFromString(obj)
        message_id = message_pb.dialogue_message.message_id
        dialogue_reference = (
            message_pb.dialogue_message.dialogue_starter_reference,
            message_pb.dialogue_message.dialogue_responder_reference,
        )
        target = message_pb.dialogue_message.target

        perun_grpc_pb.ParseFromString(message_pb.dialogue_message.content)
        performative = perun_grpc_pb.WhichOneof("performative")
        performative_id = PerunGrpcMessage.Performative(str(performative))
        performative_content = dict()  # type: Dict[str, Any]
        if performative_id == PerunGrpcMessage.Performative.REQUEST:
            type = perun_grpc_pb.request.type
            performative_content["type"] = type
            content = perun_grpc_pb.request.content
            performative_content["content"] = content
        elif performative_id == PerunGrpcMessage.Performative.RESPONSE:
            type = perun_grpc_pb.response.type
            performative_content["type"] = type
            content = perun_grpc_pb.response.content
            performative_content["content"] = content
        else:
            raise ValueError("Performative not valid: {}.".format(performative_id))

        return PerunGrpcMessage(
            message_id=message_id,
            dialogue_reference=dialogue_reference,
            target=target,
            performative=performative,
            **performative_content
        )
