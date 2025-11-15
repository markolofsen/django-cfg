from google.protobuf import timestamp_pb2 as _timestamp_pb2
from google.protobuf import struct_pb2 as _struct_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ProviderType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    PROVIDER_TYPE_UNSPECIFIED: _ClassVar[ProviderType]
    PROVIDER_TELEGRAM: _ClassVar[ProviderType]
    PROVIDER_API: _ClassVar[ProviderType]
    PROVIDER_WEBHOOK: _ClassVar[ProviderType]
    PROVIDER_BOT: _ClassVar[ProviderType]
    PROVIDER_MANUAL: _ClassVar[ProviderType]

class SignalType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    SIGNAL_TYPE_UNSPECIFIED: _ClassVar[SignalType]
    SIGNAL_BUY: _ClassVar[SignalType]
    SIGNAL_SELL: _ClassVar[SignalType]
    SIGNAL_INFO: _ClassVar[SignalType]

class ProviderStatus(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    PROVIDER_STATUS_UNSPECIFIED: _ClassVar[ProviderStatus]
    PROVIDER_ACTIVE: _ClassVar[ProviderStatus]
    PROVIDER_PAUSED: _ClassVar[ProviderStatus]
    PROVIDER_ERROR: _ClassVar[ProviderStatus]

class ErrorLevel(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    ERROR_LEVEL_UNSPECIFIED: _ClassVar[ErrorLevel]
    ERROR_WARNING: _ClassVar[ErrorLevel]
    ERROR_ERROR: _ClassVar[ErrorLevel]
    ERROR_CRITICAL: _ClassVar[ErrorLevel]

class LogLevel(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    LOG_LEVEL_UNSPECIFIED: _ClassVar[LogLevel]
    LOG_DEBUG: _ClassVar[LogLevel]
    LOG_INFO: _ClassVar[LogLevel]
    LOG_WARNING: _ClassVar[LogLevel]
    LOG_ERROR: _ClassVar[LogLevel]
PROVIDER_TYPE_UNSPECIFIED: ProviderType
PROVIDER_TELEGRAM: ProviderType
PROVIDER_API: ProviderType
PROVIDER_WEBHOOK: ProviderType
PROVIDER_BOT: ProviderType
PROVIDER_MANUAL: ProviderType
SIGNAL_TYPE_UNSPECIFIED: SignalType
SIGNAL_BUY: SignalType
SIGNAL_SELL: SignalType
SIGNAL_INFO: SignalType
PROVIDER_STATUS_UNSPECIFIED: ProviderStatus
PROVIDER_ACTIVE: ProviderStatus
PROVIDER_PAUSED: ProviderStatus
PROVIDER_ERROR: ProviderStatus
ERROR_LEVEL_UNSPECIFIED: ErrorLevel
ERROR_WARNING: ErrorLevel
ERROR_ERROR: ErrorLevel
ERROR_CRITICAL: ErrorLevel
LOG_LEVEL_UNSPECIFIED: LogLevel
LOG_DEBUG: LogLevel
LOG_INFO: LogLevel
LOG_WARNING: LogLevel
LOG_ERROR: LogLevel

class SignalProviderMessage(_message.Message):
    __slots__ = ("provider_id", "message_id", "timestamp", "register", "signal_report", "heartbeat", "status", "command_ack", "error", "log")
    PROVIDER_ID_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_ID_FIELD_NUMBER: _ClassVar[int]
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    REGISTER_FIELD_NUMBER: _ClassVar[int]
    SIGNAL_REPORT_FIELD_NUMBER: _ClassVar[int]
    HEARTBEAT_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    COMMAND_ACK_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    LOG_FIELD_NUMBER: _ClassVar[int]
    provider_id: str
    message_id: str
    timestamp: _timestamp_pb2.Timestamp
    register: RegisterProviderRequest
    signal_report: SignalReport
    heartbeat: HeartbeatUpdate
    status: StatusUpdate
    command_ack: CommandAck
    error: ErrorReport
    log: LogEntry
    def __init__(self, provider_id: _Optional[str] = ..., message_id: _Optional[str] = ..., timestamp: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., register: _Optional[_Union[RegisterProviderRequest, _Mapping]] = ..., signal_report: _Optional[_Union[SignalReport, _Mapping]] = ..., heartbeat: _Optional[_Union[HeartbeatUpdate, _Mapping]] = ..., status: _Optional[_Union[StatusUpdate, _Mapping]] = ..., command_ack: _Optional[_Union[CommandAck, _Mapping]] = ..., error: _Optional[_Union[ErrorReport, _Mapping]] = ..., log: _Optional[_Union[LogEntry, _Mapping]] = ...) -> None: ...

class RegisterProviderRequest(_message.Message):
    __slots__ = ("provider_name", "provider_type", "version", "url", "description", "metadata")
    PROVIDER_NAME_FIELD_NUMBER: _ClassVar[int]
    PROVIDER_TYPE_FIELD_NUMBER: _ClassVar[int]
    VERSION_FIELD_NUMBER: _ClassVar[int]
    URL_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    provider_name: str
    provider_type: ProviderType
    version: str
    url: str
    description: str
    metadata: _struct_pb2.Struct
    def __init__(self, provider_name: _Optional[str] = ..., provider_type: _Optional[_Union[ProviderType, str]] = ..., version: _Optional[str] = ..., url: _Optional[str] = ..., description: _Optional[str] = ..., metadata: _Optional[_Union[_struct_pb2.Struct, _Mapping]] = ...) -> None: ...

class SignalReport(_message.Message):
    __slots__ = ("signal_id", "signal_type", "priority", "content", "signal_date", "target_coin_symbol", "coin_pair", "raw_data", "tags", "confidence")
    SIGNAL_ID_FIELD_NUMBER: _ClassVar[int]
    SIGNAL_TYPE_FIELD_NUMBER: _ClassVar[int]
    PRIORITY_FIELD_NUMBER: _ClassVar[int]
    CONTENT_FIELD_NUMBER: _ClassVar[int]
    SIGNAL_DATE_FIELD_NUMBER: _ClassVar[int]
    TARGET_COIN_SYMBOL_FIELD_NUMBER: _ClassVar[int]
    COIN_PAIR_FIELD_NUMBER: _ClassVar[int]
    RAW_DATA_FIELD_NUMBER: _ClassVar[int]
    TAGS_FIELD_NUMBER: _ClassVar[int]
    CONFIDENCE_FIELD_NUMBER: _ClassVar[int]
    signal_id: str
    signal_type: SignalType
    priority: int
    content: str
    signal_date: _timestamp_pb2.Timestamp
    target_coin_symbol: str
    coin_pair: CoinPair
    raw_data: _struct_pb2.Struct
    tags: _containers.RepeatedScalarFieldContainer[str]
    confidence: float
    def __init__(self, signal_id: _Optional[str] = ..., signal_type: _Optional[_Union[SignalType, str]] = ..., priority: _Optional[int] = ..., content: _Optional[str] = ..., signal_date: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., target_coin_symbol: _Optional[str] = ..., coin_pair: _Optional[_Union[CoinPair, _Mapping]] = ..., raw_data: _Optional[_Union[_struct_pb2.Struct, _Mapping]] = ..., tags: _Optional[_Iterable[str]] = ..., confidence: _Optional[float] = ...) -> None: ...

class CoinPair(_message.Message):
    __slots__ = ("base_symbol", "quote_symbol")
    BASE_SYMBOL_FIELD_NUMBER: _ClassVar[int]
    QUOTE_SYMBOL_FIELD_NUMBER: _ClassVar[int]
    base_symbol: str
    quote_symbol: str
    def __init__(self, base_symbol: _Optional[str] = ..., quote_symbol: _Optional[str] = ...) -> None: ...

class HeartbeatUpdate(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class StatusUpdate(_message.Message):
    __slots__ = ("status", "message")
    STATUS_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    status: ProviderStatus
    message: str
    def __init__(self, status: _Optional[_Union[ProviderStatus, str]] = ..., message: _Optional[str] = ...) -> None: ...

class ErrorReport(_message.Message):
    __slots__ = ("level", "error_code", "message", "context")
    LEVEL_FIELD_NUMBER: _ClassVar[int]
    ERROR_CODE_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    CONTEXT_FIELD_NUMBER: _ClassVar[int]
    level: ErrorLevel
    error_code: str
    message: str
    context: _struct_pb2.Struct
    def __init__(self, level: _Optional[_Union[ErrorLevel, str]] = ..., error_code: _Optional[str] = ..., message: _Optional[str] = ..., context: _Optional[_Union[_struct_pb2.Struct, _Mapping]] = ...) -> None: ...

class LogEntry(_message.Message):
    __slots__ = ("level", "message", "data")
    LEVEL_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    DATA_FIELD_NUMBER: _ClassVar[int]
    level: LogLevel
    message: str
    data: _struct_pb2.Struct
    def __init__(self, level: _Optional[_Union[LogLevel, str]] = ..., message: _Optional[str] = ..., data: _Optional[_Union[_struct_pb2.Struct, _Mapping]] = ...) -> None: ...

class CommandAck(_message.Message):
    __slots__ = ("command_id", "success", "message", "current_status", "error")
    COMMAND_ID_FIELD_NUMBER: _ClassVar[int]
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    CURRENT_STATUS_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    command_id: str
    success: bool
    message: str
    current_status: ProviderStatus
    error: str
    def __init__(self, command_id: _Optional[str] = ..., success: bool = ..., message: _Optional[str] = ..., current_status: _Optional[_Union[ProviderStatus, str]] = ..., error: _Optional[str] = ...) -> None: ...

class DjangoCommand(_message.Message):
    __slots__ = ("command_id", "timestamp", "ack_signal", "request_status", "pause", "resume", "ping")
    COMMAND_ID_FIELD_NUMBER: _ClassVar[int]
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    ACK_SIGNAL_FIELD_NUMBER: _ClassVar[int]
    REQUEST_STATUS_FIELD_NUMBER: _ClassVar[int]
    PAUSE_FIELD_NUMBER: _ClassVar[int]
    RESUME_FIELD_NUMBER: _ClassVar[int]
    PING_FIELD_NUMBER: _ClassVar[int]
    command_id: str
    timestamp: _timestamp_pb2.Timestamp
    ack_signal: AckSignalCommand
    request_status: RequestStatusCommand
    pause: PauseProviderCommand
    resume: ResumeProviderCommand
    ping: PingCommand
    def __init__(self, command_id: _Optional[str] = ..., timestamp: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., ack_signal: _Optional[_Union[AckSignalCommand, _Mapping]] = ..., request_status: _Optional[_Union[RequestStatusCommand, _Mapping]] = ..., pause: _Optional[_Union[PauseProviderCommand, _Mapping]] = ..., resume: _Optional[_Union[ResumeProviderCommand, _Mapping]] = ..., ping: _Optional[_Union[PingCommand, _Mapping]] = ...) -> None: ...

class AckSignalCommand(_message.Message):
    __slots__ = ("signal_id", "accepted", "rejection_reason", "created_signal_id")
    SIGNAL_ID_FIELD_NUMBER: _ClassVar[int]
    ACCEPTED_FIELD_NUMBER: _ClassVar[int]
    REJECTION_REASON_FIELD_NUMBER: _ClassVar[int]
    CREATED_SIGNAL_ID_FIELD_NUMBER: _ClassVar[int]
    signal_id: str
    accepted: bool
    rejection_reason: str
    created_signal_id: str
    def __init__(self, signal_id: _Optional[str] = ..., accepted: bool = ..., rejection_reason: _Optional[str] = ..., created_signal_id: _Optional[str] = ...) -> None: ...

class PauseProviderCommand(_message.Message):
    __slots__ = ("reason",)
    REASON_FIELD_NUMBER: _ClassVar[int]
    reason: str
    def __init__(self, reason: _Optional[str] = ...) -> None: ...

class ResumeProviderCommand(_message.Message):
    __slots__ = ("message",)
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    message: str
    def __init__(self, message: _Optional[str] = ...) -> None: ...

class RequestStatusCommand(_message.Message):
    __slots__ = ("include_stats",)
    INCLUDE_STATS_FIELD_NUMBER: _ClassVar[int]
    include_stats: bool
    def __init__(self, include_stats: bool = ...) -> None: ...

class PingCommand(_message.Message):
    __slots__ = ("sequence",)
    SEQUENCE_FIELD_NUMBER: _ClassVar[int]
    sequence: int
    def __init__(self, sequence: _Optional[int] = ...) -> None: ...

class SendCommandRequest(_message.Message):
    __slots__ = ("provider_id", "command")
    PROVIDER_ID_FIELD_NUMBER: _ClassVar[int]
    COMMAND_FIELD_NUMBER: _ClassVar[int]
    provider_id: str
    command: DjangoCommand
    def __init__(self, provider_id: _Optional[str] = ..., command: _Optional[_Union[DjangoCommand, _Mapping]] = ...) -> None: ...

class SendCommandResponse(_message.Message):
    __slots__ = ("success", "error")
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    success: bool
    error: str
    def __init__(self, success: bool = ..., error: _Optional[str] = ...) -> None: ...
