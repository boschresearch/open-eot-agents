# Copyright (c) 2022 - for information on the respective copyright owner see the NOTICE file and/or the repository https://github.com/boschresearch/open-eot-agents.
#
# SPDX-License-Identifier: Apache-2.0

from aea.protocols.base import Message
from aea.skills.base import Address, Model
from aea.protocols.dialogue.base import Dialogue as BaseDialogue
from packages.bosch.protocols.perun_grpc.dialogues import PerunGrpcDialogue, PerunGrpcDialogues

PerunDialogue = PerunGrpcDialogue


class PerunDialogues(Model, PerunGrpcDialogues):
    """This class scaffolds a model."""

    def __init__(self, **kwargs) -> None:
        """
        Initialize dialogues.

        :param agent_address: the address of the agent for whom dialogues are maintained
        :return: None
        """
        Model.__init__(self, **kwargs)

        def role_from_first_message(  # pylint: disable=unused-argument
            message: Message, receiver_address: Address
        ) -> BaseDialogue.Role:
            """Infer the role of the agent from an incoming/outgoing first message

            :param message: an incoming/outgoing first message
            :param receiver_address: the address of the receiving agent
            :return: The role of the agent
            """
            return PerunDialogue.Role.CLIENT

        PerunGrpcDialogues.__init__(
            self,
            self_address=str(self.skill_id),
            role_from_first_message=role_from_first_message,
        )
