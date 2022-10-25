# Copyright (c) 2022 - for information on the respective copyright owner see the NOTICE file and/or the repository https://github.com/boschresearch/open-eot-agents.
#
# SPDX-License-Identifier: Apache-2.0

from dataclasses import dataclass
from typing import (
    TYPE_CHECKING,
    AsyncIterator,
    Dict,
    List,
    Optional,
)

import betterproto
import grpclib
from betterproto.grpc.grpclib_server import ServiceBase


if TYPE_CHECKING:
    import grpclib.server
    from betterproto.grpc.grpclib_client import MetadataLike
    from grpclib.metadata import Deadline


class ErrorCategory(betterproto.Enum):
    ParticipantError = 0
    ClientError = 1
    ProtocolError = 2
    InternalError = 3


class ErrorCode(betterproto.Enum):
    DefaultInvalidCode = 0
    """
    Though "0" is an invalid error code, we still define it, becauseproto3
    requires that every enum definition should have 0 mapped toatleast one
    constant.
    """

    ErrPeerRequestTimedOut = 101
    ErrPeerRejected = 102
    ErrPeerNotFunded = 103
    ErrUserResponseTimedOut = 104
    ErrResourceNotFound = 201
    ErrResourceExists = 202
    ErrInvalidArgument = 203
    ErrFailedPreCondition = 204
    ErrInvalidConfig = 205
    ErrInvalidContracts = 206
    ErrTxTimedOut = 301
    ErrChainNotReachable = 302
    ErrUnknownInternal = 401


class SubPayChUpdatesRespNotifyChUpdateType(betterproto.Enum):
    open = 0
    final = 1
    closed = 2


@dataclass(eq=False, repr=False)
class PeerId(betterproto.Message):
    """
    Peer ID represents the data required to identify and communicate with a
    participant in the the off-chain network.
    """

    alias: str = betterproto.string_field(1)
    off_chain_address: str = betterproto.string_field(2)
    comm_address: str = betterproto.string_field(3)
    comm_type: str = betterproto.string_field(4)


@dataclass(eq=False, repr=False)
class BalInfo(betterproto.Message):
    """
    BalInfo represents the balance information of the channel: Currency and the
    channel balance. Balance is represented as two corresponding lists: Parts
    contains the list of aliases of the channel participants and Balance list
    contains the amount held by each channel participant in the give currency.
    A valid BalInfo should meet the following conditions, it should be
    validated when using them.        1. Lengths of Parts list and Balance list
    are equal.    2. All entries in Parts list are unique.        3. Parts list
    has an entry "self", that represents the user of the session.     4. No
    amount in Balance must be negative.
    """

    currencies: List[str] = betterproto.string_field(1)
    parts: List[str] = betterproto.string_field(2)
    bals: List["BalInfoBal"] = betterproto.message_field(3)


@dataclass(eq=False, repr=False)
class BalInfoBal(betterproto.Message):
    bal: List[str] = betterproto.string_field(1)


@dataclass(eq=False, repr=False)
class PayChInfo(betterproto.Message):
    ch_id: str = betterproto.string_field(1)
    bal_info: "BalInfo" = betterproto.message_field(2)
    version: str = betterproto.string_field(3)


@dataclass(eq=False, repr=False)
class Payment(betterproto.Message):
    currency: str = betterproto.string_field(1)
    payee: str = betterproto.string_field(2)
    amount: str = betterproto.string_field(3)


@dataclass(eq=False, repr=False)
class MsgError(betterproto.Message):
    category: "ErrorCategory" = betterproto.enum_field(1)
    code: "ErrorCode" = betterproto.enum_field(2)
    message: str = betterproto.string_field(3)
    err_info_peer_request_timed_out: "ErrInfoPeerRequestTimedOut" = (
        betterproto.message_field(4, group="addInfo")
    )
    err_info_peer_rejected: "ErrInfoPeerRejected" = betterproto.message_field(
        5, group="addInfo"
    )
    err_info_peer_not_funded: "ErrInfoPeerNotFunded" = betterproto.message_field(
        6, group="addInfo"
    )
    err_info_user_response_timed_out: "ErrInfoUserResponseTimedOut" = (
        betterproto.message_field(7, group="addInfo")
    )
    err_info_resource_not_found: "ErrInfoResourceNotFound" = betterproto.message_field(
        8, group="addInfo"
    )
    err_info_resource_exists: "ErrInfoResourceExists" = betterproto.message_field(
        9, group="addInfo"
    )
    err_info_invalid_argument: "ErrInfoInvalidArgument" = betterproto.message_field(
        10, group="addInfo"
    )
    err_info_failed_pre_cond_unclosed_chs: "ErrInfoFailedPreCondUnclosedChs" = (
        betterproto.message_field(11, group="addInfo")
    )
    err_info_invalid_config: "ErrInfoInvalidConfig" = betterproto.message_field(
        13, group="addInfo"
    )
    err_info_invalid_contracts: "ErrInfoInvalidContracts" = betterproto.message_field(
        14, group="addInfo"
    )
    err_info_tx_timed_out: "ErrInfoTxTimedOut" = betterproto.message_field(
        15, group="addInfo"
    )
    err_info_chain_not_reachable: "ErrInfoChainNotReachable" = (
        betterproto.message_field(16, group="addInfo")
    )


@dataclass(eq=False, repr=False)
class ErrInfoPeerRequestTimedOut(betterproto.Message):
    peer_alias: str = betterproto.string_field(1)
    timeout: str = betterproto.string_field(2)


@dataclass(eq=False, repr=False)
class ErrInfoPeerRejected(betterproto.Message):
    peer_alias: str = betterproto.string_field(1)
    reason: str = betterproto.string_field(2)


@dataclass(eq=False, repr=False)
class ErrInfoPeerNotFunded(betterproto.Message):
    peer_alias: str = betterproto.string_field(1)


@dataclass(eq=False, repr=False)
class ErrInfoUserResponseTimedOut(betterproto.Message):
    expiry: int = betterproto.int64_field(1)
    received_at: int = betterproto.int64_field(2)


@dataclass(eq=False, repr=False)
class ErrInfoResourceNotFound(betterproto.Message):
    type: str = betterproto.string_field(1)
    id: str = betterproto.string_field(2)


@dataclass(eq=False, repr=False)
class ErrInfoResourceExists(betterproto.Message):
    type: str = betterproto.string_field(1)
    id: str = betterproto.string_field(2)


@dataclass(eq=False, repr=False)
class ErrInfoInvalidArgument(betterproto.Message):
    name: str = betterproto.string_field(1)
    value: str = betterproto.string_field(2)
    requirement: str = betterproto.string_field(3)


@dataclass(eq=False, repr=False)
class ErrInfoFailedPreCondUnclosedChs(betterproto.Message):
    chs: List["PayChInfo"] = betterproto.message_field(1)


@dataclass(eq=False, repr=False)
class ErrInfoInvalidConfig(betterproto.Message):
    name: str = betterproto.string_field(1)
    value: str = betterproto.string_field(2)


@dataclass(eq=False, repr=False)
class ContractErrInfo(betterproto.Message):
    name: str = betterproto.string_field(1)
    address: str = betterproto.string_field(2)
    error: str = betterproto.string_field(3)


@dataclass(eq=False, repr=False)
class ErrInfoInvalidContracts(betterproto.Message):
    contract_err_infos: List["ContractErrInfo"] = betterproto.message_field(1)


@dataclass(eq=False, repr=False)
class ErrInfoTxTimedOut(betterproto.Message):
    tx_type: str = betterproto.string_field(1)
    tx_id: str = betterproto.string_field(2)
    tx_timeout: str = betterproto.string_field(3)


@dataclass(eq=False, repr=False)
class ErrInfoChainNotReachable(betterproto.Message):
    chain_url: str = betterproto.string_field(1)


@dataclass(eq=False, repr=False)
class GetConfigReq(betterproto.Message):
    pass


@dataclass(eq=False, repr=False)
class GetConfigResp(betterproto.Message):
    chain_address: str = betterproto.string_field(1)
    adjudicator: str = betterproto.string_field(2)
    asset_eth: str = betterproto.string_field(3)
    comm_types: List[str] = betterproto.string_field(4)
    id_provider_types: List[str] = betterproto.string_field(5)


@dataclass(eq=False, repr=False)
class OpenSessionReq(betterproto.Message):
    config_file: str = betterproto.string_field(1)


@dataclass(eq=False, repr=False)
class OpenSessionResp(betterproto.Message):
    msg_success: "OpenSessionRespMsgSuccess" = betterproto.message_field(
        1, group="response"
    )
    error: "MsgError" = betterproto.message_field(2, group="response")


@dataclass(eq=False, repr=False)
class OpenSessionRespMsgSuccess(betterproto.Message):
    session_id: str = betterproto.string_field(1)
    restored_chs: List["PayChInfo"] = betterproto.message_field(2)


@dataclass(eq=False, repr=False)
class TimeReq(betterproto.Message):
    pass


@dataclass(eq=False, repr=False)
class TimeResp(betterproto.Message):
    time: int = betterproto.int64_field(1)


@dataclass(eq=False, repr=False)
class RegisterCurrencyReq(betterproto.Message):
    token_addr: str = betterproto.string_field(1)
    asset_addr: str = betterproto.string_field(2)


@dataclass(eq=False, repr=False)
class RegisterCurrencyResp(betterproto.Message):
    msg_success: "RegisterCurrencyRespMsgSuccess" = betterproto.message_field(
        1, group="response"
    )
    error: "MsgError" = betterproto.message_field(2, group="response")


@dataclass(eq=False, repr=False)
class RegisterCurrencyRespMsgSuccess(betterproto.Message):
    symbol: str = betterproto.string_field(1)


@dataclass(eq=False, repr=False)
class HelpReq(betterproto.Message):
    pass


@dataclass(eq=False, repr=False)
class HelpResp(betterproto.Message):
    apis: List[str] = betterproto.string_field(1)


@dataclass(eq=False, repr=False)
class AddPeerIdReq(betterproto.Message):
    session_id: str = betterproto.string_field(1)
    peer_id: "PeerId" = betterproto.message_field(2)


@dataclass(eq=False, repr=False)
class AddPeerIdResp(betterproto.Message):
    msg_success: "AddPeerIdRespMsgSuccess" = betterproto.message_field(
        1, group="response"
    )
    error: "MsgError" = betterproto.message_field(2, group="response")


@dataclass(eq=False, repr=False)
class AddPeerIdRespMsgSuccess(betterproto.Message):
    success: bool = betterproto.bool_field(1)


@dataclass(eq=False, repr=False)
class GetPeerIdReq(betterproto.Message):
    session_id: str = betterproto.string_field(1)
    alias: str = betterproto.string_field(2)


@dataclass(eq=False, repr=False)
class GetPeerIdResp(betterproto.Message):
    msg_success: "GetPeerIdRespMsgSuccess" = betterproto.message_field(
        1, group="response"
    )
    error: "MsgError" = betterproto.message_field(2, group="response")


@dataclass(eq=False, repr=False)
class GetPeerIdRespMsgSuccess(betterproto.Message):
    peer_id: "PeerId" = betterproto.message_field(1)


@dataclass(eq=False, repr=False)
class OpenPayChReq(betterproto.Message):
    session_id: str = betterproto.string_field(1)
    opening_bal_info: "BalInfo" = betterproto.message_field(2)
    challenge_dur_secs: int = betterproto.uint64_field(3)


@dataclass(eq=False, repr=False)
class OpenPayChResp(betterproto.Message):
    msg_success: "OpenPayChRespMsgSuccess" = betterproto.message_field(
        1, group="response"
    )
    error: "MsgError" = betterproto.message_field(2, group="response")


@dataclass(eq=False, repr=False)
class OpenPayChRespMsgSuccess(betterproto.Message):
    opened_pay_ch_info: "PayChInfo" = betterproto.message_field(1)


@dataclass(eq=False, repr=False)
class GetPayChsInfoReq(betterproto.Message):
    session_id: str = betterproto.string_field(1)


@dataclass(eq=False, repr=False)
class GetPayChsInfoResp(betterproto.Message):
    msg_success: "GetPayChsInfoRespMsgSuccess" = betterproto.message_field(
        1, group="response"
    )
    error: "MsgError" = betterproto.message_field(2, group="response")


@dataclass(eq=False, repr=False)
class GetPayChsInfoRespMsgSuccess(betterproto.Message):
    open_pay_chs_info: List["PayChInfo"] = betterproto.message_field(1)


@dataclass(eq=False, repr=False)
class SubPayChProposalsReq(betterproto.Message):
    session_id: str = betterproto.string_field(1)


@dataclass(eq=False, repr=False)
class SubPayChProposalsResp(betterproto.Message):
    notify: "SubPayChProposalsRespNotify" = betterproto.message_field(
        1, group="response"
    )
    error: "MsgError" = betterproto.message_field(2, group="response")


@dataclass(eq=False, repr=False)
class SubPayChProposalsRespNotify(betterproto.Message):
    proposal_id: str = betterproto.string_field(2)
    opening_bal_info: "BalInfo" = betterproto.message_field(4)
    challenge_dur_secs: int = betterproto.uint64_field(5)
    expiry: int = betterproto.int64_field(6)


@dataclass(eq=False, repr=False)
class UnsubPayChProposalsReq(betterproto.Message):
    session_id: str = betterproto.string_field(1)


@dataclass(eq=False, repr=False)
class UnsubPayChProposalsResp(betterproto.Message):
    msg_success: "UnsubPayChProposalsRespMsgSuccess" = betterproto.message_field(
        1, group="response"
    )
    error: "MsgError" = betterproto.message_field(2, group="response")


@dataclass(eq=False, repr=False)
class UnsubPayChProposalsRespMsgSuccess(betterproto.Message):
    success: bool = betterproto.bool_field(1)


@dataclass(eq=False, repr=False)
class RespondPayChProposalReq(betterproto.Message):
    session_id: str = betterproto.string_field(1)
    proposal_id: str = betterproto.string_field(2)
    accept: bool = betterproto.bool_field(3)


@dataclass(eq=False, repr=False)
class RespondPayChProposalResp(betterproto.Message):
    msg_success: "RespondPayChProposalRespMsgSuccess" = betterproto.message_field(
        1, group="response"
    )
    error: "MsgError" = betterproto.message_field(2, group="response")


@dataclass(eq=False, repr=False)
class RespondPayChProposalRespMsgSuccess(betterproto.Message):
    opened_pay_ch_info: "PayChInfo" = betterproto.message_field(2)


@dataclass(eq=False, repr=False)
class CloseSessionReq(betterproto.Message):
    session_id: str = betterproto.string_field(1)
    force: bool = betterproto.bool_field(2)


@dataclass(eq=False, repr=False)
class CloseSessionResp(betterproto.Message):
    msg_success: "CloseSessionRespMsgSuccess" = betterproto.message_field(
        1, group="response"
    )
    error: "MsgError" = betterproto.message_field(2, group="response")


@dataclass(eq=False, repr=False)
class CloseSessionRespMsgSuccess(betterproto.Message):
    open_pay_chs_info: List["PayChInfo"] = betterproto.message_field(1)


@dataclass(eq=False, repr=False)
class DeployAssetErc20Req(betterproto.Message):
    session_id: str = betterproto.string_field(1)
    token_addr: str = betterproto.string_field(2)


@dataclass(eq=False, repr=False)
class DeployAssetErc20Resp(betterproto.Message):
    msg_success: "DeployAssetErc20RespMsgSuccess" = betterproto.message_field(
        1, group="response"
    )
    error: "MsgError" = betterproto.message_field(2, group="response")


@dataclass(eq=False, repr=False)
class DeployAssetErc20RespMsgSuccess(betterproto.Message):
    asset_addr: str = betterproto.string_field(2)


@dataclass(eq=False, repr=False)
class SendPayChUpdateReq(betterproto.Message):
    session_id: str = betterproto.string_field(1)
    ch_id: str = betterproto.string_field(2)
    payments: List["Payment"] = betterproto.message_field(3)


@dataclass(eq=False, repr=False)
class SendPayChUpdateResp(betterproto.Message):
    msg_success: "SendPayChUpdateRespMsgSuccess" = betterproto.message_field(
        1, group="response"
    )
    error: "MsgError" = betterproto.message_field(2, group="response")


@dataclass(eq=False, repr=False)
class SendPayChUpdateRespMsgSuccess(betterproto.Message):
    updated_pay_ch_info: "PayChInfo" = betterproto.message_field(1)


@dataclass(eq=False, repr=False)
class SubpayChUpdatesReq(betterproto.Message):
    session_id: str = betterproto.string_field(1)
    ch_id: str = betterproto.string_field(2)


@dataclass(eq=False, repr=False)
class SubPayChUpdatesResp(betterproto.Message):
    notify: "SubPayChUpdatesRespNotify" = betterproto.message_field(1, group="response")
    error: "MsgError" = betterproto.message_field(2, group="response")


@dataclass(eq=False, repr=False)
class SubPayChUpdatesRespNotify(betterproto.Message):
    update_id: str = betterproto.string_field(1)
    proposed_pay_ch_info: "PayChInfo" = betterproto.message_field(2)
    type: "SubPayChUpdatesRespNotifyChUpdateType" = betterproto.enum_field(3)
    expiry: int = betterproto.int64_field(4)
    error: "MsgError" = betterproto.message_field(5)


@dataclass(eq=False, repr=False)
class UnsubPayChUpdatesReq(betterproto.Message):
    session_id: str = betterproto.string_field(1)
    ch_id: str = betterproto.string_field(2)


@dataclass(eq=False, repr=False)
class UnsubPayChUpdatesResp(betterproto.Message):
    msg_success: "UnsubPayChUpdatesRespMsgSuccess" = betterproto.message_field(
        1, group="response"
    )
    error: "MsgError" = betterproto.message_field(2, group="response")


@dataclass(eq=False, repr=False)
class UnsubPayChUpdatesRespMsgSuccess(betterproto.Message):
    success: bool = betterproto.bool_field(1)


@dataclass(eq=False, repr=False)
class RespondPayChUpdateReq(betterproto.Message):
    session_id: str = betterproto.string_field(1)
    ch_id: str = betterproto.string_field(2)
    update_id: str = betterproto.string_field(3)
    accept: bool = betterproto.bool_field(4)


@dataclass(eq=False, repr=False)
class RespondPayChUpdateResp(betterproto.Message):
    msg_success: "RespondPayChUpdateRespMsgSuccess" = betterproto.message_field(
        1, group="response"
    )
    error: "MsgError" = betterproto.message_field(2, group="response")


@dataclass(eq=False, repr=False)
class RespondPayChUpdateRespMsgSuccess(betterproto.Message):
    updated_pay_ch_info: "PayChInfo" = betterproto.message_field(1)


@dataclass(eq=False, repr=False)
class GetPayChInfoReq(betterproto.Message):
    session_id: str = betterproto.string_field(1)
    ch_id: str = betterproto.string_field(2)


@dataclass(eq=False, repr=False)
class GetPayChInfoResp(betterproto.Message):
    msg_success: "GetPayChInfoRespMsgSuccess" = betterproto.message_field(
        1, group="response"
    )
    error: "MsgError" = betterproto.message_field(2, group="response")


@dataclass(eq=False, repr=False)
class GetPayChInfoRespMsgSuccess(betterproto.Message):
    pay_ch_info: "PayChInfo" = betterproto.message_field(1)


@dataclass(eq=False, repr=False)
class ClosePayChReq(betterproto.Message):
    session_id: str = betterproto.string_field(1)
    ch_id: str = betterproto.string_field(2)


@dataclass(eq=False, repr=False)
class ClosePayChResp(betterproto.Message):
    msg_success: "ClosePayChRespMsgSuccess" = betterproto.message_field(
        1, group="response"
    )
    error: "MsgError" = betterproto.message_field(2, group="response")


@dataclass(eq=False, repr=False)
class ClosePayChRespMsgSuccess(betterproto.Message):
    closed_pay_ch_info: "PayChInfo" = betterproto.message_field(1)


class PaymentApiStub(betterproto.ServiceStub):
    async def get_config(
        self,
        get_config_req: "GetConfigReq",
        *,
        timeout: Optional[float] = None,
        deadline: Optional["Deadline"] = None,
        metadata: Optional["MetadataLike"] = None
    ) -> "GetConfigResp":
        return await self._unary_unary(
            "/pb.Payment_API/GetConfig",
            get_config_req,
            GetConfigResp,
            timeout=timeout,
            deadline=deadline,
            metadata=metadata,
        )

    async def open_session(
        self,
        open_session_req: "OpenSessionReq",
        *,
        timeout: Optional[float] = None,
        deadline: Optional["Deadline"] = None,
        metadata: Optional["MetadataLike"] = None
    ) -> "OpenSessionResp":
        return await self._unary_unary(
            "/pb.Payment_API/OpenSession",
            open_session_req,
            OpenSessionResp,
            timeout=timeout,
            deadline=deadline,
            metadata=metadata,
        )

    async def time(
        self,
        time_req: "TimeReq",
        *,
        timeout: Optional[float] = None,
        deadline: Optional["Deadline"] = None,
        metadata: Optional["MetadataLike"] = None
    ) -> "TimeResp":
        return await self._unary_unary(
            "/pb.Payment_API/Time",
            time_req,
            TimeResp,
            timeout=timeout,
            deadline=deadline,
            metadata=metadata,
        )

    async def register_currency(
        self,
        register_currency_req: "RegisterCurrencyReq",
        *,
        timeout: Optional[float] = None,
        deadline: Optional["Deadline"] = None,
        metadata: Optional["MetadataLike"] = None
    ) -> "RegisterCurrencyResp":
        return await self._unary_unary(
            "/pb.Payment_API/RegisterCurrency",
            register_currency_req,
            RegisterCurrencyResp,
            timeout=timeout,
            deadline=deadline,
            metadata=metadata,
        )

    async def help(
        self,
        help_req: "HelpReq",
        *,
        timeout: Optional[float] = None,
        deadline: Optional["Deadline"] = None,
        metadata: Optional["MetadataLike"] = None
    ) -> "HelpResp":
        return await self._unary_unary(
            "/pb.Payment_API/Help",
            help_req,
            HelpResp,
            timeout=timeout,
            deadline=deadline,
            metadata=metadata,
        )

    async def add_peer_id(
        self,
        add_peer_id_req: "AddPeerIdReq",
        *,
        timeout: Optional[float] = None,
        deadline: Optional["Deadline"] = None,
        metadata: Optional["MetadataLike"] = None
    ) -> "AddPeerIdResp":
        return await self._unary_unary(
            "/pb.Payment_API/AddPeerID",
            add_peer_id_req,
            AddPeerIdResp,
            timeout=timeout,
            deadline=deadline,
            metadata=metadata,
        )

    async def get_peer_id(
        self,
        get_peer_id_req: "GetPeerIdReq",
        *,
        timeout: Optional[float] = None,
        deadline: Optional["Deadline"] = None,
        metadata: Optional["MetadataLike"] = None
    ) -> "GetPeerIdResp":
        return await self._unary_unary(
            "/pb.Payment_API/GetPeerID",
            get_peer_id_req,
            GetPeerIdResp,
            timeout=timeout,
            deadline=deadline,
            metadata=metadata,
        )

    async def open_pay_ch(
        self,
        open_pay_ch_req: "OpenPayChReq",
        *,
        timeout: Optional[float] = None,
        deadline: Optional["Deadline"] = None,
        metadata: Optional["MetadataLike"] = None
    ) -> "OpenPayChResp":
        return await self._unary_unary(
            "/pb.Payment_API/OpenPayCh",
            open_pay_ch_req,
            OpenPayChResp,
            timeout=timeout,
            deadline=deadline,
            metadata=metadata,
        )

    async def get_pay_chs_info(
        self,
        get_pay_chs_info_req: "GetPayChsInfoReq",
        *,
        timeout: Optional[float] = None,
        deadline: Optional["Deadline"] = None,
        metadata: Optional["MetadataLike"] = None
    ) -> "GetPayChsInfoResp":
        return await self._unary_unary(
            "/pb.Payment_API/GetPayChsInfo",
            get_pay_chs_info_req,
            GetPayChsInfoResp,
            timeout=timeout,
            deadline=deadline,
            metadata=metadata,
        )

    async def sub_pay_ch_proposals(
        self,
        sub_pay_ch_proposals_req: "SubPayChProposalsReq",
        *,
        timeout: Optional[float] = None,
        deadline: Optional["Deadline"] = None,
        metadata: Optional["MetadataLike"] = None
    ) -> AsyncIterator["SubPayChProposalsResp"]:
        async for response in self._unary_stream(
            "/pb.Payment_API/SubPayChProposals",
            sub_pay_ch_proposals_req,
            SubPayChProposalsResp,
            timeout=timeout,
            deadline=deadline,
            metadata=metadata,
        ):
            yield response

    async def unsub_pay_ch_proposals(
        self,
        unsub_pay_ch_proposals_req: "UnsubPayChProposalsReq",
        *,
        timeout: Optional[float] = None,
        deadline: Optional["Deadline"] = None,
        metadata: Optional["MetadataLike"] = None
    ) -> "UnsubPayChProposalsResp":
        return await self._unary_unary(
            "/pb.Payment_API/UnsubPayChProposals",
            unsub_pay_ch_proposals_req,
            UnsubPayChProposalsResp,
            timeout=timeout,
            deadline=deadline,
            metadata=metadata,
        )

    async def respond_pay_ch_proposal(
        self,
        respond_pay_ch_proposal_req: "RespondPayChProposalReq",
        *,
        timeout: Optional[float] = None,
        deadline: Optional["Deadline"] = None,
        metadata: Optional["MetadataLike"] = None
    ) -> "RespondPayChProposalResp":
        return await self._unary_unary(
            "/pb.Payment_API/RespondPayChProposal",
            respond_pay_ch_proposal_req,
            RespondPayChProposalResp,
            timeout=timeout,
            deadline=deadline,
            metadata=metadata,
        )

    async def close_session(
        self,
        close_session_req: "CloseSessionReq",
        *,
        timeout: Optional[float] = None,
        deadline: Optional["Deadline"] = None,
        metadata: Optional["MetadataLike"] = None
    ) -> "CloseSessionResp":
        return await self._unary_unary(
            "/pb.Payment_API/CloseSession",
            close_session_req,
            CloseSessionResp,
            timeout=timeout,
            deadline=deadline,
            metadata=metadata,
        )

    async def deploy_asset_erc20(
        self,
        deploy_asset_erc20_req: "DeployAssetErc20Req",
        *,
        timeout: Optional[float] = None,
        deadline: Optional["Deadline"] = None,
        metadata: Optional["MetadataLike"] = None
    ) -> "DeployAssetErc20Resp":
        return await self._unary_unary(
            "/pb.Payment_API/DeployAssetERC20",
            deploy_asset_erc20_req,
            DeployAssetErc20Resp,
            timeout=timeout,
            deadline=deadline,
            metadata=metadata,
        )

    async def send_pay_ch_update(
        self,
        send_pay_ch_update_req: "SendPayChUpdateReq",
        *,
        timeout: Optional[float] = None,
        deadline: Optional["Deadline"] = None,
        metadata: Optional["MetadataLike"] = None
    ) -> "SendPayChUpdateResp":
        return await self._unary_unary(
            "/pb.Payment_API/SendPayChUpdate",
            send_pay_ch_update_req,
            SendPayChUpdateResp,
            timeout=timeout,
            deadline=deadline,
            metadata=metadata,
        )

    async def sub_pay_ch_updates(
        self,
        subpay_ch_updates_req: "SubpayChUpdatesReq",
        *,
        timeout: Optional[float] = None,
        deadline: Optional["Deadline"] = None,
        metadata: Optional["MetadataLike"] = None
    ) -> AsyncIterator["SubPayChUpdatesResp"]:
        async for response in self._unary_stream(
            "/pb.Payment_API/SubPayChUpdates",
            subpay_ch_updates_req,
            SubPayChUpdatesResp,
            timeout=timeout,
            deadline=deadline,
            metadata=metadata,
        ):
            yield response

    async def unsub_pay_ch_updates(
        self,
        unsub_pay_ch_updates_req: "UnsubPayChUpdatesReq",
        *,
        timeout: Optional[float] = None,
        deadline: Optional["Deadline"] = None,
        metadata: Optional["MetadataLike"] = None
    ) -> "UnsubPayChUpdatesResp":
        return await self._unary_unary(
            "/pb.Payment_API/UnsubPayChUpdates",
            unsub_pay_ch_updates_req,
            UnsubPayChUpdatesResp,
            timeout=timeout,
            deadline=deadline,
            metadata=metadata,
        )

    async def respond_pay_ch_update(
        self,
        respond_pay_ch_update_req: "RespondPayChUpdateReq",
        *,
        timeout: Optional[float] = None,
        deadline: Optional["Deadline"] = None,
        metadata: Optional["MetadataLike"] = None
    ) -> "RespondPayChUpdateResp":
        return await self._unary_unary(
            "/pb.Payment_API/RespondPayChUpdate",
            respond_pay_ch_update_req,
            RespondPayChUpdateResp,
            timeout=timeout,
            deadline=deadline,
            metadata=metadata,
        )

    async def get_pay_ch_info(
        self,
        get_pay_ch_info_req: "GetPayChInfoReq",
        *,
        timeout: Optional[float] = None,
        deadline: Optional["Deadline"] = None,
        metadata: Optional["MetadataLike"] = None
    ) -> "GetPayChInfoResp":
        return await self._unary_unary(
            "/pb.Payment_API/GetPayChInfo",
            get_pay_ch_info_req,
            GetPayChInfoResp,
            timeout=timeout,
            deadline=deadline,
            metadata=metadata,
        )

    async def close_pay_ch(
        self,
        close_pay_ch_req: "ClosePayChReq",
        *,
        timeout: Optional[float] = None,
        deadline: Optional["Deadline"] = None,
        metadata: Optional["MetadataLike"] = None
    ) -> "ClosePayChResp":
        return await self._unary_unary(
            "/pb.Payment_API/ClosePayCh",
            close_pay_ch_req,
            ClosePayChResp,
            timeout=timeout,
            deadline=deadline,
            metadata=metadata,
        )


class PaymentApiBase(ServiceBase):
    async def get_config(self, get_config_req: "GetConfigReq") -> "GetConfigResp":
        raise grpclib.GRPCError(grpclib.const.Status.UNIMPLEMENTED)

    async def open_session(
        self, open_session_req: "OpenSessionReq"
    ) -> "OpenSessionResp":
        raise grpclib.GRPCError(grpclib.const.Status.UNIMPLEMENTED)

    async def time(self, time_req: "TimeReq") -> "TimeResp":
        raise grpclib.GRPCError(grpclib.const.Status.UNIMPLEMENTED)

    async def register_currency(
        self, register_currency_req: "RegisterCurrencyReq"
    ) -> "RegisterCurrencyResp":
        raise grpclib.GRPCError(grpclib.const.Status.UNIMPLEMENTED)

    async def help(self, help_req: "HelpReq") -> "HelpResp":
        raise grpclib.GRPCError(grpclib.const.Status.UNIMPLEMENTED)

    async def add_peer_id(self) -> "AddPeerIdResp":
        raise grpclib.GRPCError(grpclib.const.Status.UNIMPLEMENTED)

    async def get_peer_id(self) -> "GetPeerIdResp":
        raise grpclib.GRPCError(grpclib.const.Status.UNIMPLEMENTED)

    async def open_pay_ch(self, open_pay_ch_req: "OpenPayChReq") -> "OpenPayChResp":
        raise grpclib.GRPCError(grpclib.const.Status.UNIMPLEMENTED)

    async def get_pay_chs_info(
        self, get_pay_chs_info_req: "GetPayChsInfoReq"
    ) -> "GetPayChsInfoResp":
        raise grpclib.GRPCError(grpclib.const.Status.UNIMPLEMENTED)

    async def sub_pay_ch_proposals(
        self, sub_pay_ch_proposals_req: "SubPayChProposalsReq"
    ) -> AsyncIterator["SubPayChProposalsResp"]:
        raise grpclib.GRPCError(grpclib.const.Status.UNIMPLEMENTED)

    async def unsub_pay_ch_proposals(
        self, unsub_pay_ch_proposals_req: "UnsubPayChProposalsReq"
    ) -> "UnsubPayChProposalsResp":
        raise grpclib.GRPCError(grpclib.const.Status.UNIMPLEMENTED)

    async def respond_pay_ch_proposal(
        self, respond_pay_ch_proposal_req: "RespondPayChProposalReq"
    ) -> "RespondPayChProposalResp":
        raise grpclib.GRPCError(grpclib.const.Status.UNIMPLEMENTED)

    async def close_session(
        self, close_session_req: "CloseSessionReq"
    ) -> "CloseSessionResp":
        raise grpclib.GRPCError(grpclib.const.Status.UNIMPLEMENTED)

    async def deploy_asset_erc20(self) -> "DeployAssetErc20Resp":
        raise grpclib.GRPCError(grpclib.const.Status.UNIMPLEMENTED)

    async def send_pay_ch_update(
        self, send_pay_ch_update_req: "SendPayChUpdateReq"
    ) -> "SendPayChUpdateResp":
        raise grpclib.GRPCError(grpclib.const.Status.UNIMPLEMENTED)

    async def sub_pay_ch_updates(
        self, subpay_ch_updates_req: "SubpayChUpdatesReq"
    ) -> AsyncIterator["SubPayChUpdatesResp"]:
        raise grpclib.GRPCError(grpclib.const.Status.UNIMPLEMENTED)

    async def unsub_pay_ch_updates(
        self, unsub_pay_ch_updates_req: "UnsubPayChUpdatesReq"
    ) -> "UnsubPayChUpdatesResp":
        raise grpclib.GRPCError(grpclib.const.Status.UNIMPLEMENTED)

    async def respond_pay_ch_update(
        self, respond_pay_ch_update_req: "RespondPayChUpdateReq"
    ) -> "RespondPayChUpdateResp":
        raise grpclib.GRPCError(grpclib.const.Status.UNIMPLEMENTED)

    async def get_pay_ch_info(
        self, get_pay_ch_info_req: "GetPayChInfoReq"
    ) -> "GetPayChInfoResp":
        raise grpclib.GRPCError(grpclib.const.Status.UNIMPLEMENTED)

    async def close_pay_ch(self, close_pay_ch_req: "ClosePayChReq") -> "ClosePayChResp":
        raise grpclib.GRPCError(grpclib.const.Status.UNIMPLEMENTED)

    async def __rpc_get_config(
        self, stream: "grpclib.server.Stream[GetConfigReq, GetConfigResp]"
    ) -> None:
        request = await stream.recv_message()
        response = await self.get_config(request)
        await stream.send_message(response)

    async def __rpc_open_session(
        self, stream: "grpclib.server.Stream[OpenSessionReq, OpenSessionResp]"
    ) -> None:
        request = await stream.recv_message()
        response = await self.open_session(request)
        await stream.send_message(response)

    async def __rpc_time(
        self, stream: "grpclib.server.Stream[TimeReq, TimeResp]"
    ) -> None:
        request = await stream.recv_message()
        response = await self.time(request)
        await stream.send_message(response)

    async def __rpc_register_currency(
        self, stream: "grpclib.server.Stream[RegisterCurrencyReq, RegisterCurrencyResp]"
    ) -> None:
        request = await stream.recv_message()
        response = await self.register_currency(request)
        await stream.send_message(response)

    async def __rpc_help(
        self, stream: "grpclib.server.Stream[HelpReq, HelpResp]"
    ) -> None:
        request = await stream.recv_message()
        response = await self.help(request)
        await stream.send_message(response)

    async def __rpc_add_peer_id(
        self, stream: "grpclib.server.Stream[AddPeerIdReq, AddPeerIdResp]"
    ) -> None:
        request = await stream.recv_message()
        response = await self.add_peer_id(request)
        await stream.send_message(response)

    async def __rpc_get_peer_id(
        self, stream: "grpclib.server.Stream[GetPeerIdReq, GetPeerIdResp]"
    ) -> None:
        request = await stream.recv_message()
        response = await self.get_peer_id(request)
        await stream.send_message(response)

    async def __rpc_open_pay_ch(
        self, stream: "grpclib.server.Stream[OpenPayChReq, OpenPayChResp]"
    ) -> None:
        request = await stream.recv_message()
        response = await self.open_pay_ch(request)
        await stream.send_message(response)

    async def __rpc_get_pay_chs_info(
        self, stream: "grpclib.server.Stream[GetPayChsInfoReq, GetPayChsInfoResp]"
    ) -> None:
        request = await stream.recv_message()
        response = await self.get_pay_chs_info(request)
        await stream.send_message(response)

    async def __rpc_sub_pay_ch_proposals(
        self,
        stream: "grpclib.server.Stream[SubPayChProposalsReq, SubPayChProposalsResp]",
    ) -> None:
        request = await stream.recv_message()
        await self._call_rpc_handler_server_stream(
            self.sub_pay_ch_proposals,
            stream,
            request,
        )

    async def __rpc_unsub_pay_ch_proposals(
        self,
        stream: "grpclib.server.Stream[UnsubPayChProposalsReq, UnsubPayChProposalsResp]",
    ) -> None:
        request = await stream.recv_message()
        response = await self.unsub_pay_ch_proposals(request)
        await stream.send_message(response)

    async def __rpc_respond_pay_ch_proposal(
        self,
        stream: "grpclib.server.Stream[RespondPayChProposalReq, RespondPayChProposalResp]",
    ) -> None:
        request = await stream.recv_message()
        response = await self.respond_pay_ch_proposal(request)
        await stream.send_message(response)

    async def __rpc_close_session(
        self, stream: "grpclib.server.Stream[CloseSessionReq, CloseSessionResp]"
    ) -> None:
        request = await stream.recv_message()
        response = await self.close_session(request)
        await stream.send_message(response)

    async def __rpc_deploy_asset_erc20(
        self, stream: "grpclib.server.Stream[DeployAssetErc20Req, DeployAssetErc20Resp]"
    ) -> None:
        request = await stream.recv_message()
        response = await self.deploy_asset_erc20(request)
        await stream.send_message(response)

    async def __rpc_send_pay_ch_update(
        self, stream: "grpclib.server.Stream[SendPayChUpdateReq, SendPayChUpdateResp]"
    ) -> None:
        request = await stream.recv_message()
        response = await self.send_pay_ch_update(request)
        await stream.send_message(response)

    async def __rpc_sub_pay_ch_updates(
        self, stream: "grpclib.server.Stream[SubpayChUpdatesReq, SubPayChUpdatesResp]"
    ) -> None:
        request = await stream.recv_message()
        await self._call_rpc_handler_server_stream(
            self.sub_pay_ch_updates,
            stream,
            request,
        )

    async def __rpc_unsub_pay_ch_updates(
        self,
        stream: "grpclib.server.Stream[UnsubPayChUpdatesReq, UnsubPayChUpdatesResp]",
    ) -> None:
        request = await stream.recv_message()
        response = await self.unsub_pay_ch_updates(request)
        await stream.send_message(response)

    async def __rpc_respond_pay_ch_update(
        self,
        stream: "grpclib.server.Stream[RespondPayChUpdateReq, RespondPayChUpdateResp]",
    ) -> None:
        request = await stream.recv_message()
        response = await self.respond_pay_ch_update(request)
        await stream.send_message(response)

    async def __rpc_get_pay_ch_info(
        self, stream: "grpclib.server.Stream[GetPayChInfoReq, GetPayChInfoResp]"
    ) -> None:
        request = await stream.recv_message()
        response = await self.get_pay_ch_info(request)
        await stream.send_message(response)

    async def __rpc_close_pay_ch(
        self, stream: "grpclib.server.Stream[ClosePayChReq, ClosePayChResp]"
    ) -> None:
        request = await stream.recv_message()
        response = await self.close_pay_ch(request)
        await stream.send_message(response)

    def __mapping__(self) -> Dict[str, grpclib.const.Handler]:
        return {
            "/pb.Payment_API/GetConfig": grpclib.const.Handler(
                self.__rpc_get_config,
                grpclib.const.Cardinality.UNARY_UNARY,
                GetConfigReq,
                GetConfigResp,
            ),
            "/pb.Payment_API/OpenSession": grpclib.const.Handler(
                self.__rpc_open_session,
                grpclib.const.Cardinality.UNARY_UNARY,
                OpenSessionReq,
                OpenSessionResp,
            ),
            "/pb.Payment_API/Time": grpclib.const.Handler(
                self.__rpc_time,
                grpclib.const.Cardinality.UNARY_UNARY,
                TimeReq,
                TimeResp,
            ),
            "/pb.Payment_API/RegisterCurrency": grpclib.const.Handler(
                self.__rpc_register_currency,
                grpclib.const.Cardinality.UNARY_UNARY,
                RegisterCurrencyReq,
                RegisterCurrencyResp,
            ),
            "/pb.Payment_API/Help": grpclib.const.Handler(
                self.__rpc_help,
                grpclib.const.Cardinality.UNARY_UNARY,
                HelpReq,
                HelpResp,
            ),
            "/pb.Payment_API/AddPeerID": grpclib.const.Handler(
                self.__rpc_add_peer_id,
                grpclib.const.Cardinality.UNARY_UNARY,
                AddPeerIdReq,
                AddPeerIdResp,
            ),
            "/pb.Payment_API/GetPeerID": grpclib.const.Handler(
                self.__rpc_get_peer_id,
                grpclib.const.Cardinality.UNARY_UNARY,
                GetPeerIdReq,
                GetPeerIdResp,
            ),
            "/pb.Payment_API/OpenPayCh": grpclib.const.Handler(
                self.__rpc_open_pay_ch,
                grpclib.const.Cardinality.UNARY_UNARY,
                OpenPayChReq,
                OpenPayChResp,
            ),
            "/pb.Payment_API/GetPayChsInfo": grpclib.const.Handler(
                self.__rpc_get_pay_chs_info,
                grpclib.const.Cardinality.UNARY_UNARY,
                GetPayChsInfoReq,
                GetPayChsInfoResp,
            ),
            "/pb.Payment_API/SubPayChProposals": grpclib.const.Handler(
                self.__rpc_sub_pay_ch_proposals,
                grpclib.const.Cardinality.UNARY_STREAM,
                SubPayChProposalsReq,
                SubPayChProposalsResp,
            ),
            "/pb.Payment_API/UnsubPayChProposals": grpclib.const.Handler(
                self.__rpc_unsub_pay_ch_proposals,
                grpclib.const.Cardinality.UNARY_UNARY,
                UnsubPayChProposalsReq,
                UnsubPayChProposalsResp,
            ),
            "/pb.Payment_API/RespondPayChProposal": grpclib.const.Handler(
                self.__rpc_respond_pay_ch_proposal,
                grpclib.const.Cardinality.UNARY_UNARY,
                RespondPayChProposalReq,
                RespondPayChProposalResp,
            ),
            "/pb.Payment_API/CloseSession": grpclib.const.Handler(
                self.__rpc_close_session,
                grpclib.const.Cardinality.UNARY_UNARY,
                CloseSessionReq,
                CloseSessionResp,
            ),
            "/pb.Payment_API/DeployAssetERC20": grpclib.const.Handler(
                self.__rpc_deploy_asset_erc20,
                grpclib.const.Cardinality.UNARY_UNARY,
                DeployAssetErc20Req,
                DeployAssetErc20Resp,
            ),
            "/pb.Payment_API/SendPayChUpdate": grpclib.const.Handler(
                self.__rpc_send_pay_ch_update,
                grpclib.const.Cardinality.UNARY_UNARY,
                SendPayChUpdateReq,
                SendPayChUpdateResp,
            ),
            "/pb.Payment_API/SubPayChUpdates": grpclib.const.Handler(
                self.__rpc_sub_pay_ch_updates,
                grpclib.const.Cardinality.UNARY_STREAM,
                SubpayChUpdatesReq,
                SubPayChUpdatesResp,
            ),
            "/pb.Payment_API/UnsubPayChUpdates": grpclib.const.Handler(
                self.__rpc_unsub_pay_ch_updates,
                grpclib.const.Cardinality.UNARY_UNARY,
                UnsubPayChUpdatesReq,
                UnsubPayChUpdatesResp,
            ),
            "/pb.Payment_API/RespondPayChUpdate": grpclib.const.Handler(
                self.__rpc_respond_pay_ch_update,
                grpclib.const.Cardinality.UNARY_UNARY,
                RespondPayChUpdateReq,
                RespondPayChUpdateResp,
            ),
            "/pb.Payment_API/GetPayChInfo": grpclib.const.Handler(
                self.__rpc_get_pay_ch_info,
                grpclib.const.Cardinality.UNARY_UNARY,
                GetPayChInfoReq,
                GetPayChInfoResp,
            ),
            "/pb.Payment_API/ClosePayCh": grpclib.const.Handler(
                self.__rpc_close_pay_ch,
                grpclib.const.Cardinality.UNARY_UNARY,
                ClosePayChReq,
                ClosePayChResp,
            ),
        }
