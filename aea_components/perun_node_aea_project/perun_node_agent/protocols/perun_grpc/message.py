# Copyright (c) 2022 - for information on the respective copyright owner see the NOTICE file and/or the repository https://github.com/boschresearch/open-eot-agents.
#
# SPDX-License-Identifier: Apache-2.0

# -*- coding: utf-8 -*-

"""This module contains perun_grpc's message definition."""

# pylint: disable=too-many-statements,too-many-locals,no-member,too-few-public-methods,too-many-branches,not-an-iterable,unidiomatic-typecheck,unsubscriptable-object
import logging
from typing import Any, Set, Tuple, cast

from aea.configurations.base import PublicId
from aea.exceptions import AEAEnforceError, enforce
from aea.protocols.base import Message


_default_logger = logging.getLogger("aea.packages.bosch.protocols.perun_grpc.message")

DEFAULT_BODY_SIZE = 4


class PerunGrpcMessage(Message):
    """A protocol for Perun GRPC requests and responses."""

    protocol_id = PublicId.from_str("bosch/perun_grpc:0.1.0")
    protocol_specification_id = PublicId.from_str("bosch/perun_grpc:0.1.0")

    class Performative(Message.Performative):
        """Performatives for the perun_grpc protocol."""

        REQUEST = "request"
        RESPONSE = "response"

        def __str__(self) -> str:
            """Get the string representation."""
            return str(self.value)

    _performatives = {"request", "response"}
    __slots__: Tuple[str, ...] = tuple()

    class _SlotsCls:
        __slots__ = (
            "content",
            "dialogue_reference",
            "message_id",
            "performative",
            "target",
            "type",
        )

    def __init__(
        self,
        performative: Performative,
        dialogue_reference: Tuple[str, str] = ("", ""),
        message_id: int = 1,
        target: int = 0,
        **kwargs: Any,
    ):
        """
        Initialise an instance of PerunGrpcMessage.

        :param message_id: the message id.
        :param dialogue_reference: the dialogue reference.
        :param target: the message target.
        :param performative: the message performative.
        :param **kwargs: extra options.
        """
        super().__init__(
            dialogue_reference=dialogue_reference,
            message_id=message_id,
            target=target,
            performative=PerunGrpcMessage.Performative(performative),
            **kwargs,
        )

    @property
    def valid_performatives(self) -> Set[str]:
        """Get valid performatives."""
        return self._performatives

    @property
    def dialogue_reference(self) -> Tuple[str, str]:
        """Get the dialogue_reference of the message."""
        enforce(self.is_set("dialogue_reference"), "dialogue_reference is not set.")
        return cast(Tuple[str, str], self.get("dialogue_reference"))

    @property
    def message_id(self) -> int:
        """Get the message_id of the message."""
        enforce(self.is_set("message_id"), "message_id is not set.")
        return cast(int, self.get("message_id"))

    @property
    def performative(self) -> Performative:  # type: ignore # noqa: F821
        """Get the performative of the message."""
        enforce(self.is_set("performative"), "performative is not set.")
        return cast(PerunGrpcMessage.Performative, self.get("performative"))

    @property
    def target(self) -> int:
        """Get the target of the message."""
        enforce(self.is_set("target"), "target is not set.")
        return cast(int, self.get("target"))

    @property
    def content(self) -> bytes:
        """Get the 'content' content from the message."""
        enforce(self.is_set("content"), "'content' content is not set.")
        return cast(bytes, self.get("content"))

    @property
    def type(self) -> str:
        """Get the 'type' content from the message."""
        enforce(self.is_set("type"), "'type' content is not set.")
        return cast(str, self.get("type"))

    def _is_consistent(self) -> bool:
        """Check that the message follows the perun_grpc protocol."""
        try:
            enforce(
                isinstance(self.dialogue_reference, tuple),
                "Invalid type for 'dialogue_reference'. Expected 'tuple'. Found '{}'.".format(
                    type(self.dialogue_reference)
                ),
            )
            enforce(
                isinstance(self.dialogue_reference[0], str),
                "Invalid type for 'dialogue_reference[0]'. Expected 'str'. Found '{}'.".format(
                    type(self.dialogue_reference[0])
                ),
            )
            enforce(
                isinstance(self.dialogue_reference[1], str),
                "Invalid type for 'dialogue_reference[1]'. Expected 'str'. Found '{}'.".format(
                    type(self.dialogue_reference[1])
                ),
            )
            enforce(
                type(self.message_id) is int,
                "Invalid type for 'message_id'. Expected 'int'. Found '{}'.".format(
                    type(self.message_id)
                ),
            )
            enforce(
                type(self.target) is int,
                "Invalid type for 'target'. Expected 'int'. Found '{}'.".format(
                    type(self.target)
                ),
            )

            # Light Protocol Rule 2
            # Check correct performative
            enforce(
                isinstance(self.performative, PerunGrpcMessage.Performative),
                "Invalid 'performative'. Expected either of '{}'. Found '{}'.".format(
                    self.valid_performatives, self.performative
                ),
            )

            # Check correct contents
            actual_nb_of_contents = len(self._body) - DEFAULT_BODY_SIZE
            expected_nb_of_contents = 0
            if self.performative == PerunGrpcMessage.Performative.REQUEST:
                expected_nb_of_contents = 2
                enforce(
                    isinstance(self.type, str),
                    "Invalid type for content 'type'. Expected 'str'. Found '{}'.".format(
                        type(self.type)
                    ),
                )
                enforce(
                    isinstance(self.content, bytes),
                    "Invalid type for content 'content'. Expected 'bytes'. Found '{}'.".format(
                        type(self.content)
                    ),
                )
            elif self.performative == PerunGrpcMessage.Performative.RESPONSE:
                expected_nb_of_contents = 2
                enforce(
                    isinstance(self.type, str),
                    "Invalid type for content 'type'. Expected 'str'. Found '{}'.".format(
                        type(self.type)
                    ),
                )
                enforce(
                    isinstance(self.content, bytes),
                    "Invalid type for content 'content'. Expected 'bytes'. Found '{}'.".format(
                        type(self.content)
                    ),
                )

            # Check correct content count
            enforce(
                expected_nb_of_contents == actual_nb_of_contents,
                "Incorrect number of contents. Expected {}. Found {}".format(
                    expected_nb_of_contents, actual_nb_of_contents
                ),
            )

            # Light Protocol Rule 3
            if self.message_id == 1:
                enforce(
                    self.target == 0,
                    "Invalid 'target'. Expected 0 (because 'message_id' is 1). Found {}.".format(
                        self.target
                    ),
                )
        except (AEAEnforceError, ValueError, KeyError) as e:
            _default_logger.error(str(e))
            return False

        return True
