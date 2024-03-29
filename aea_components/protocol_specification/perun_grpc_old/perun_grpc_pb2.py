# Copyright (c) 2022 - for information on the respective copyright owner see the NOTICE file and/or the repository https://github.com/boschresearch/open-eot-agents.
#
# SPDX-License-Identifier: Apache-2.0

# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: perun_grpc.proto
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database

# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(
    b'\n\x10perun_grpc.proto\x12\x1b\x61\x65\x61.bosch.perun_grpc.v0_1_0"\xc1\x02\n\x10PerunGrpcMessage\x12U\n\x07request\x18\x05 \x01(\x0b\x32\x42.aea.bosch.perun_grpc.v0_1_0.PerunGrpcMessage.Request_PerformativeH\x00\x12W\n\x08response\x18\x06 \x01(\x0b\x32\x43.aea.bosch.perun_grpc.v0_1_0.PerunGrpcMessage.Response_PerformativeH\x00\x1a\x35\n\x14Request_Performative\x12\x0c\n\x04type\x18\x01 \x01(\t\x12\x0f\n\x07\x63ontent\x18\x02 \x01(\x0c\x1a\x36\n\x15Response_Performative\x12\x0c\n\x04type\x18\x01 \x01(\t\x12\x0f\n\x07\x63ontent\x18\x02 \x01(\x0c\x42\x0e\n\x0cperformativeb\x06proto3'
)


_PERUNGRPCMESSAGE = DESCRIPTOR.message_types_by_name["PerunGrpcMessage"]
_PERUNGRPCMESSAGE_REQUEST_PERFORMATIVE = _PERUNGRPCMESSAGE.nested_types_by_name[
    "Request_Performative"
]
_PERUNGRPCMESSAGE_RESPONSE_PERFORMATIVE = _PERUNGRPCMESSAGE.nested_types_by_name[
    "Response_Performative"
]
PerunGrpcMessage = _reflection.GeneratedProtocolMessageType(
    "PerunGrpcMessage",
    (_message.Message,),
    {
        "Request_Performative": _reflection.GeneratedProtocolMessageType(
            "Request_Performative",
            (_message.Message,),
            {
                "DESCRIPTOR": _PERUNGRPCMESSAGE_REQUEST_PERFORMATIVE,
                "__module__": "perun_grpc_pb2"
                # @@protoc_insertion_point(class_scope:aea.bosch.perun_grpc.v0_1_0.PerunGrpcMessage.Request_Performative)
            },
        ),
        "Response_Performative": _reflection.GeneratedProtocolMessageType(
            "Response_Performative",
            (_message.Message,),
            {
                "DESCRIPTOR": _PERUNGRPCMESSAGE_RESPONSE_PERFORMATIVE,
                "__module__": "perun_grpc_pb2"
                # @@protoc_insertion_point(class_scope:aea.bosch.perun_grpc.v0_1_0.PerunGrpcMessage.Response_Performative)
            },
        ),
        "DESCRIPTOR": _PERUNGRPCMESSAGE,
        "__module__": "perun_grpc_pb2"
        # @@protoc_insertion_point(class_scope:aea.bosch.perun_grpc.v0_1_0.PerunGrpcMessage)
    },
)
_sym_db.RegisterMessage(PerunGrpcMessage)
_sym_db.RegisterMessage(PerunGrpcMessage.Request_Performative)
_sym_db.RegisterMessage(PerunGrpcMessage.Response_Performative)

if _descriptor._USE_C_DESCRIPTORS == False:

    DESCRIPTOR._options = None
    _PERUNGRPCMESSAGE._serialized_start = 50
    _PERUNGRPCMESSAGE._serialized_end = 371
    _PERUNGRPCMESSAGE_REQUEST_PERFORMATIVE._serialized_start = 246
    _PERUNGRPCMESSAGE_REQUEST_PERFORMATIVE._serialized_end = 299
    _PERUNGRPCMESSAGE_RESPONSE_PERFORMATIVE._serialized_start = 301
    _PERUNGRPCMESSAGE_RESPONSE_PERFORMATIVE._serialized_end = 355
# @@protoc_insertion_point(module_scope)
