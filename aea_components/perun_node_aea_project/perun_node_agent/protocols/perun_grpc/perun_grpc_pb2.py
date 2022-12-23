# Copyright (c) 2022 - for information on the respective copyright owner see the NOTICE file and/or the repository https://github.com/boschresearch/open-eot-agents.
#
# SPDX-License-Identifier: Apache-2.0
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database

# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(
    b'\n\x10perun_grpc.proto\x12\x1b\x61\x65\x61.bosch.perun_grpc.v0_1_0"\xa4\x06\n\x10PerunGrpcMessage\x12S\n\x06\x61\x63\x63\x65pt\x18\x05 \x01(\x0b\x32\x41.aea.bosch.perun_grpc.v0_1_0.PerunGrpcMessage.Accept_PerformativeH\x00\x12M\n\x03\x65nd\x18\x06 \x01(\x0b\x32>.aea.bosch.perun_grpc.v0_1_0.PerunGrpcMessage.End_PerformativeH\x00\x12Y\n\tpaychresp\x18\x07 \x01(\x0b\x32\x44.aea.bosch.perun_grpc.v0_1_0.PerunGrpcMessage.Paychresp_PerformativeH\x00\x12S\n\x06reject\x18\x08 \x01(\x0b\x32\x41.aea.bosch.perun_grpc.v0_1_0.PerunGrpcMessage.Reject_PerformativeH\x00\x12U\n\x07request\x18\t \x01(\x0b\x32\x42.aea.bosch.perun_grpc.v0_1_0.PerunGrpcMessage.Request_PerformativeH\x00\x12W\n\x08response\x18\n \x01(\x0b\x32\x43.aea.bosch.perun_grpc.v0_1_0.PerunGrpcMessage.Response_PerformativeH\x00\x1a\x35\n\x14Request_Performative\x12\x0c\n\x04type\x18\x01 \x01(\t\x12\x0f\n\x07\x63ontent\x18\x02 \x01(\x0c\x1a\x36\n\x15Response_Performative\x12\x0c\n\x04type\x18\x01 \x01(\t\x12\x0f\n\x07\x63ontent\x18\x02 \x01(\x0c\x1aK\n\x16Paychresp_Performative\x12\x12\n\nsession_id\x18\x01 \x01(\t\x12\x0c\n\x04type\x18\x02 \x01(\t\x12\x0f\n\x07\x63ontent\x18\x03 \x01(\x0c\x1a\x15\n\x13\x41\x63\x63\x65pt_Performative\x1a\x15\n\x13Reject_Performative\x1a\x12\n\x10\x45nd_PerformativeB\x0e\n\x0cperformativeb\x06proto3'
)


_PERUNGRPCMESSAGE = DESCRIPTOR.message_types_by_name["PerunGrpcMessage"]
_PERUNGRPCMESSAGE_REQUEST_PERFORMATIVE = _PERUNGRPCMESSAGE.nested_types_by_name[
    "Request_Performative"
]
_PERUNGRPCMESSAGE_RESPONSE_PERFORMATIVE = _PERUNGRPCMESSAGE.nested_types_by_name[
    "Response_Performative"
]
_PERUNGRPCMESSAGE_PAYCHRESP_PERFORMATIVE = _PERUNGRPCMESSAGE.nested_types_by_name[
    "Paychresp_Performative"
]
_PERUNGRPCMESSAGE_ACCEPT_PERFORMATIVE = _PERUNGRPCMESSAGE.nested_types_by_name[
    "Accept_Performative"
]
_PERUNGRPCMESSAGE_REJECT_PERFORMATIVE = _PERUNGRPCMESSAGE.nested_types_by_name[
    "Reject_Performative"
]
_PERUNGRPCMESSAGE_END_PERFORMATIVE = _PERUNGRPCMESSAGE.nested_types_by_name[
    "End_Performative"
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
        "Paychresp_Performative": _reflection.GeneratedProtocolMessageType(
            "Paychresp_Performative",
            (_message.Message,),
            {
                "DESCRIPTOR": _PERUNGRPCMESSAGE_PAYCHRESP_PERFORMATIVE,
                "__module__": "perun_grpc_pb2"
                # @@protoc_insertion_point(class_scope:aea.bosch.perun_grpc.v0_1_0.PerunGrpcMessage.Paychresp_Performative)
            },
        ),
        "Accept_Performative": _reflection.GeneratedProtocolMessageType(
            "Accept_Performative",
            (_message.Message,),
            {
                "DESCRIPTOR": _PERUNGRPCMESSAGE_ACCEPT_PERFORMATIVE,
                "__module__": "perun_grpc_pb2"
                # @@protoc_insertion_point(class_scope:aea.bosch.perun_grpc.v0_1_0.PerunGrpcMessage.Accept_Performative)
            },
        ),
        "Reject_Performative": _reflection.GeneratedProtocolMessageType(
            "Reject_Performative",
            (_message.Message,),
            {
                "DESCRIPTOR": _PERUNGRPCMESSAGE_REJECT_PERFORMATIVE,
                "__module__": "perun_grpc_pb2"
                # @@protoc_insertion_point(class_scope:aea.bosch.perun_grpc.v0_1_0.PerunGrpcMessage.Reject_Performative)
            },
        ),
        "End_Performative": _reflection.GeneratedProtocolMessageType(
            "End_Performative",
            (_message.Message,),
            {
                "DESCRIPTOR": _PERUNGRPCMESSAGE_END_PERFORMATIVE,
                "__module__": "perun_grpc_pb2"
                # @@protoc_insertion_point(class_scope:aea.bosch.perun_grpc.v0_1_0.PerunGrpcMessage.End_Performative)
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
_sym_db.RegisterMessage(PerunGrpcMessage.Paychresp_Performative)
_sym_db.RegisterMessage(PerunGrpcMessage.Accept_Performative)
_sym_db.RegisterMessage(PerunGrpcMessage.Reject_Performative)
_sym_db.RegisterMessage(PerunGrpcMessage.End_Performative)

if _descriptor._USE_C_DESCRIPTORS == False:

    DESCRIPTOR._options = None
    _PERUNGRPCMESSAGE._serialized_start = 50
    _PERUNGRPCMESSAGE._serialized_end = 854
    _PERUNGRPCMESSAGE_REQUEST_PERFORMATIVE._serialized_start = 586
    _PERUNGRPCMESSAGE_REQUEST_PERFORMATIVE._serialized_end = 639
    _PERUNGRPCMESSAGE_RESPONSE_PERFORMATIVE._serialized_start = 641
    _PERUNGRPCMESSAGE_RESPONSE_PERFORMATIVE._serialized_end = 695
    _PERUNGRPCMESSAGE_PAYCHRESP_PERFORMATIVE._serialized_start = 697
    _PERUNGRPCMESSAGE_PAYCHRESP_PERFORMATIVE._serialized_end = 772
    _PERUNGRPCMESSAGE_ACCEPT_PERFORMATIVE._serialized_start = 774
    _PERUNGRPCMESSAGE_ACCEPT_PERFORMATIVE._serialized_end = 795
    _PERUNGRPCMESSAGE_REJECT_PERFORMATIVE._serialized_start = 797
    _PERUNGRPCMESSAGE_REJECT_PERFORMATIVE._serialized_end = 818
    _PERUNGRPCMESSAGE_END_PERFORMATIVE._serialized_start = 820
    _PERUNGRPCMESSAGE_END_PERFORMATIVE._serialized_end = 838
# @@protoc_insertion_point(module_scope)
