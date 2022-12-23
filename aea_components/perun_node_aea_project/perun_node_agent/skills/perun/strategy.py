# Copyright (c) 2022 - for information on the respective copyright owner see the NOTICE file and/or the repository https://github.com/boschresearch/open-eot-agents.
#
# SPDX-License-Identifier: Apache-2.0

import logging
from typing import Any, cast
from aea.skills.base import Model
from packages.bosch.protocols.perun_grpc.grpc_message import (
    BalInfo, SubPayChProposalsRespNotify, SubPayChUpdatesRespNotify)
from packages.bosch.skills.perun.session import *


class PayChannelStrategy(Model):

    def __init__(self, **kwargs: Any) -> None:
        """
        Initialize PayChannelStrategy.

        :return: None
        """
        self._max_balance = float(kwargs.pop('max_balance', 4))
        Model.__init__(self, **kwargs)
        self._logger = logging.getLogger("packages.bosch.skills.perun.strategy")

    def is_proposal_valid(self, proposal: SubPayChProposalsRespNotify, max_balance: float = None) -> bool:
        """
        Checks if proposal is valid.

        Valid is a proposal containing self and initial balance < max_balance.

        :return: bool
        """
        self._logger.debug("Checking if proposal is acceptable: {}".format(proposal))
        if not self.is_bal_info_valid(proposal.opening_bal_info):
            self._logger.debug("proposal is not acceptable: {}".format(proposal))
            return False
        else:
            balance = 0
            if max_balance == None and self._max_balance is not None:
                balance = self._max_balance
            else:
                balance = max_balance
            # check for initial balance lower than given max_balance
            if not self.check_balances_max(balance, proposal.opening_bal_info, "self"):
                self._logger.debug("max balance {} is not acceptable for {}".format(balance, proposal.opening_bal_info))
                return False
        self._logger.debug("proposal is acceptable: {}".format(proposal))
        return True

    def check_for_part(self, bal_info: BalInfo, alias: str) -> bool:
        for part in bal_info.parts:
            if part == alias:
                return True
        return False

    def check_balances_max(self, max_balance: float, bal_info: BalInfo, alias: str) -> bool:
        index = self.get_index_for_alias_in_balinfo(alias, bal_info)
        for bal_info_bal in bal_info.bals:
            if float(bal_info_bal.bal[index]) > max_balance:
                return False
        return True

    def is_bal_info_valid(self, bal_info: BalInfo) -> bool:
        """
        1. Lengths of Parts list and Balance list are equal.

        2. All entries in Parts list are unique.

        3. Parts list has an entry "self", that represents the user of the session.

        4. No amount in Balance must be negative.

        :return: bool
        """
        if not self.check_for_part(bal_info, "self"):
            return False
        for bal_info_bal in bal_info.bals:
            # length of balances must correspond to length of contained parts / alias
            if len(bal_info.parts) != len(bal_info_bal.bal):
                return False
            # checking for negative balance amount
            for bal in bal_info_bal.bal:
                if float(bal) < 0:
                    return False
        # set contains only unique entries, therefore it can be used to check for uniqueness
        unique_set = set(bal_info.parts)
        # len of parts and unique set must be the same
        if len(bal_info.parts) != len(unique_set):
            return False
        return True

    def get_index_for_alias_in_balinfo(self, alias: str, bal_info: BalInfo) -> int:
        index: int = 0
        for ii in range(len(bal_info.parts) + 1):
            if bal_info.parts[ii] == alias:
                index = ii
                return ii

    def is_ch_upd_valid(self, update: SubPayChUpdatesRespNotify, session: PerunSession) -> bool:
        """
        Checks if a channel update is valid with own channel strategy.

        Default implementation will only accept updates by retrieving tokens
        and is focusing on ETH as only currency and if version number is increased.

        :return: bool
        """
        channel = session.channels[update.proposed_pay_ch_info.ch_id]
        index_prop = self.get_index_for_alias_in_balinfo("self", update.proposed_pay_ch_info.bal_info)
        index_old = self.get_index_for_alias_in_balinfo("self", channel.bal_info)
        # expecting only one entry for eth
        bal_prop = update.proposed_pay_ch_info.bal_info.bals[0].bal[index_prop]
        bal_old = channel.bal_info.bals[0].bal[index_old]
        self._logger.debug(
            "is_ch_upd_valid is checking proposed bal {} and old bal {}".format(bal_prop, bal_old))
        if float(bal_prop) > float(bal_old) and int(update.proposed_pay_ch_info.version) > int(channel.version):
            return True
        return False

    def is_ch_upd_final_valid(self, update: SubPayChUpdatesRespNotify, session: PerunSession) -> bool:
        """
        Checks if a final channel update is valid with own channel strategy.

        Default implementation is checking if balances are equal and version number is increased for final state.
        Expecting ETH as only currency.

        :return: bool
        """
        channel = session.channels[update.proposed_pay_ch_info.ch_id]
        if int(update.proposed_pay_ch_info.version) <= int(channel.version):
            return False
        for ii in range(len(update.proposed_pay_ch_info.bal_info.parts)):
            if float(channel.bal_info.bals[0].bal[ii]) != float(update.proposed_pay_ch_info.bal_info.bals[0].bal[ii]):
                return False
        return True
