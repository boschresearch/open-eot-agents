# Copyright (c) 2022 - for information on the respective copyright owner see the NOTICE file and/or the repository https://github.com/boschresearch/open-eot-agents.
#
# SPDX-License-Identifier: Apache-2.0

"""
This module contains the classes required for perun_grpc dialogue management.

- PerunGrpcDialogue: The dialogue class maintains state of a dialogue and manages it.
- PerunGrpcDialogues: The dialogues class keeps track of all dialogues.
"""

from abc import ABC
from typing import Callable, Dict, FrozenSet, Type, cast

from aea.common import Address
from aea.protocols.base import Message
from aea.protocols.dialogue.base import Dialogue, DialogueLabel, Dialogues

from packages.bosch.protocols.perun_grpc.message import PerunGrpcMessage


class PerunGrpcDialogue(Dialogue):
    """The perun_grpc dialogue class maintains state of a dialogue and manages it."""

    INITIAL_PERFORMATIVES: FrozenSet[Message.Performative] = frozenset(
        {PerunGrpcMessage.Performative.REQUEST}
    )
    TERMINAL_PERFORMATIVES: FrozenSet[Message.Performative] = frozenset(
        {PerunGrpcMessage.Performative.RESPONSE}
    )
    VALID_REPLIES: Dict[Message.Performative, FrozenSet[Message.Performative]] = {
        PerunGrpcMessage.Performative.REQUEST: frozenset(
            {PerunGrpcMessage.Performative.RESPONSE}
        ),
        PerunGrpcMessage.Performative.RESPONSE: frozenset(),
    }

    class Role(Dialogue.Role):
        """This class defines the agent's role in a perun_grpc dialogue."""

        CLIENT = "client"
        SERVER = "server"

    class EndState(Dialogue.EndState):
        """This class defines the end states of a perun_grpc dialogue."""

        SUCCESSFUL = 0

    def __init__(
        self,
        dialogue_label: DialogueLabel,
        self_address: Address,
        role: Dialogue.Role,
        message_class: Type[PerunGrpcMessage] = PerunGrpcMessage,
    ) -> None:
        """
        Initialize a dialogue.

        :param dialogue_label: the identifier of the dialogue
        :param self_address: the address of the entity for whom this dialogue is maintained
        :param role: the role of the agent this dialogue is maintained for
        :param message_class: the message class used
        """
        Dialogue.__init__(
            self,
            dialogue_label=dialogue_label,
            message_class=message_class,
            self_address=self_address,
            role=role,
        )


class PerunGrpcDialogues(Dialogues, ABC):
    """This class keeps track of all perun_grpc dialogues."""

    END_STATES = frozenset({PerunGrpcDialogue.EndState.SUCCESSFUL})

    _keep_terminal_state_dialogues = False

    def __init__(
        self,
        self_address: Address,
        role_from_first_message: Callable[[Message, Address], Dialogue.Role],
        dialogue_class: Type[PerunGrpcDialogue] = PerunGrpcDialogue,
    ) -> None:
        """
        Initialize dialogues.

        :param self_address: the address of the entity for whom dialogues are maintained
        :param dialogue_class: the dialogue class used
        :param role_from_first_message: the callable determining role from first message
        """
        Dialogues.__init__(
            self,
            self_address=self_address,
            end_states=cast(FrozenSet[Dialogue.EndState], self.END_STATES),
            message_class=PerunGrpcMessage,
            dialogue_class=dialogue_class,
            role_from_first_message=role_from_first_message,
        )
