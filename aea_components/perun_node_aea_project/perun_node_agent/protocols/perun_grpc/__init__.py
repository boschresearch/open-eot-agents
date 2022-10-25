# Copyright (c) 2022 - for information on the respective copyright owner see the NOTICE file and/or the repository https://github.com/boschresearch/open-eot-agents.
#
# SPDX-License-Identifier: Apache-2.0

"""
This module contains the support resources for the perun_grpc protocol.

It was created with protocol buffer compiler version `libprotoc 3.19.4` and aea version `1.2.1`.
"""

from packages.bosch.protocols.perun_grpc.message import PerunGrpcMessage
from packages.bosch.protocols.perun_grpc.serialization import PerunGrpcSerializer


PerunGrpcMessage.serializer = PerunGrpcSerializer
