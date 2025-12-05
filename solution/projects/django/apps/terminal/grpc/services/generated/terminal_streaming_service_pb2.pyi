import datetime

from google.protobuf import timestamp_pb2 as _timestamp_pb2
import common_pb2 as _common_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ElectronMessage(_message.Message):
    __slots__ = ("session_id", "message_id", "timestamp", "register", "heartbeat", "output", "command_complete", "status", "error", "ack")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_ID_FIELD_NUMBER: _ClassVar[int]
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    REGISTER_FIELD_NUMBER: _ClassVar[int]
    HEARTBEAT_FIELD_NUMBER: _ClassVar[int]
    OUTPUT_FIELD_NUMBER: _ClassVar[int]
    COMMAND_COMPLETE_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    ACK_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    message_id: str
    timestamp: _timestamp_pb2.Timestamp
    register: RegisterRequest
    heartbeat: HeartbeatUpdate
    output: TerminalOutput
    command_complete: CommandComplete
    status: StatusUpdate
    error: ErrorReport
    ack: CommandAck
    def __init__(self, session_id: _Optional[str] = ..., message_id: _Optional[str] = ..., timestamp: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., register: _Optional[_Union[RegisterRequest, _Mapping]] = ..., heartbeat: _Optional[_Union[HeartbeatUpdate, _Mapping]] = ..., output: _Optional[_Union[TerminalOutput, _Mapping]] = ..., command_complete: _Optional[_Union[CommandComplete, _Mapping]] = ..., status: _Optional[_Union[StatusUpdate, _Mapping]] = ..., error: _Optional[_Union[ErrorReport, _Mapping]] = ..., ack: _Optional[_Union[CommandAck, _Mapping]] = ...) -> None: ...

class RegisterRequest(_message.Message):
    __slots__ = ("version", "hostname", "platform", "supported_shells", "initial_size")
    VERSION_FIELD_NUMBER: _ClassVar[int]
    HOSTNAME_FIELD_NUMBER: _ClassVar[int]
    PLATFORM_FIELD_NUMBER: _ClassVar[int]
    SUPPORTED_SHELLS_FIELD_NUMBER: _ClassVar[int]
    INITIAL_SIZE_FIELD_NUMBER: _ClassVar[int]
    version: str
    hostname: str
    platform: str
    supported_shells: _containers.RepeatedScalarFieldContainer[str]
    initial_size: _common_pb2.TerminalSize
    def __init__(self, version: _Optional[str] = ..., hostname: _Optional[str] = ..., platform: _Optional[str] = ..., supported_shells: _Optional[_Iterable[str]] = ..., initial_size: _Optional[_Union[_common_pb2.TerminalSize, _Mapping]] = ...) -> None: ...

class HeartbeatUpdate(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class TerminalOutput(_message.Message):
    __slots__ = ("data", "is_stderr", "sequence")
    DATA_FIELD_NUMBER: _ClassVar[int]
    IS_STDERR_FIELD_NUMBER: _ClassVar[int]
    SEQUENCE_FIELD_NUMBER: _ClassVar[int]
    data: bytes
    is_stderr: bool
    sequence: int
    def __init__(self, data: _Optional[bytes] = ..., is_stderr: bool = ..., sequence: _Optional[int] = ...) -> None: ...

class CommandComplete(_message.Message):
    __slots__ = ("command_id", "exit_code", "duration_ms")
    COMMAND_ID_FIELD_NUMBER: _ClassVar[int]
    EXIT_CODE_FIELD_NUMBER: _ClassVar[int]
    DURATION_MS_FIELD_NUMBER: _ClassVar[int]
    command_id: str
    exit_code: int
    duration_ms: int
    def __init__(self, command_id: _Optional[str] = ..., exit_code: _Optional[int] = ..., duration_ms: _Optional[int] = ...) -> None: ...

class StatusUpdate(_message.Message):
    __slots__ = ("old_status", "new_status", "reason", "working_directory")
    OLD_STATUS_FIELD_NUMBER: _ClassVar[int]
    NEW_STATUS_FIELD_NUMBER: _ClassVar[int]
    REASON_FIELD_NUMBER: _ClassVar[int]
    WORKING_DIRECTORY_FIELD_NUMBER: _ClassVar[int]
    old_status: _common_pb2.SessionStatus
    new_status: _common_pb2.SessionStatus
    reason: str
    working_directory: str
    def __init__(self, old_status: _Optional[_Union[_common_pb2.SessionStatus, str]] = ..., new_status: _Optional[_Union[_common_pb2.SessionStatus, str]] = ..., reason: _Optional[str] = ..., working_directory: _Optional[str] = ...) -> None: ...

class ErrorReport(_message.Message):
    __slots__ = ("error_code", "message", "stack_trace", "is_fatal")
    ERROR_CODE_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    STACK_TRACE_FIELD_NUMBER: _ClassVar[int]
    IS_FATAL_FIELD_NUMBER: _ClassVar[int]
    error_code: str
    message: str
    stack_trace: str
    is_fatal: bool
    def __init__(self, error_code: _Optional[str] = ..., message: _Optional[str] = ..., stack_trace: _Optional[str] = ..., is_fatal: bool = ...) -> None: ...

class CommandAck(_message.Message):
    __slots__ = ("command_id", "success", "message")
    COMMAND_ID_FIELD_NUMBER: _ClassVar[int]
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    command_id: str
    success: bool
    message: str
    def __init__(self, command_id: _Optional[str] = ..., success: bool = ..., message: _Optional[str] = ...) -> None: ...

class DjangoMessage(_message.Message):
    __slots__ = ("command_id", "timestamp", "input", "resize", "start_session", "close_session", "signal", "cancel", "ping", "config_update")
    COMMAND_ID_FIELD_NUMBER: _ClassVar[int]
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    INPUT_FIELD_NUMBER: _ClassVar[int]
    RESIZE_FIELD_NUMBER: _ClassVar[int]
    START_SESSION_FIELD_NUMBER: _ClassVar[int]
    CLOSE_SESSION_FIELD_NUMBER: _ClassVar[int]
    SIGNAL_FIELD_NUMBER: _ClassVar[int]
    CANCEL_FIELD_NUMBER: _ClassVar[int]
    PING_FIELD_NUMBER: _ClassVar[int]
    CONFIG_UPDATE_FIELD_NUMBER: _ClassVar[int]
    command_id: str
    timestamp: _timestamp_pb2.Timestamp
    input: TerminalInput
    resize: ResizeCommand
    start_session: StartSessionCommand
    close_session: CloseSessionCommand
    signal: SignalCommand
    cancel: CancelCommand
    ping: PingCommand
    config_update: ConfigUpdateCommand
    def __init__(self, command_id: _Optional[str] = ..., timestamp: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., input: _Optional[_Union[TerminalInput, _Mapping]] = ..., resize: _Optional[_Union[ResizeCommand, _Mapping]] = ..., start_session: _Optional[_Union[StartSessionCommand, _Mapping]] = ..., close_session: _Optional[_Union[CloseSessionCommand, _Mapping]] = ..., signal: _Optional[_Union[SignalCommand, _Mapping]] = ..., cancel: _Optional[_Union[CancelCommand, _Mapping]] = ..., ping: _Optional[_Union[PingCommand, _Mapping]] = ..., config_update: _Optional[_Union[ConfigUpdateCommand, _Mapping]] = ...) -> None: ...

class TerminalInput(_message.Message):
    __slots__ = ("data", "sequence")
    DATA_FIELD_NUMBER: _ClassVar[int]
    SEQUENCE_FIELD_NUMBER: _ClassVar[int]
    data: bytes
    sequence: int
    def __init__(self, data: _Optional[bytes] = ..., sequence: _Optional[int] = ...) -> None: ...

class ResizeCommand(_message.Message):
    __slots__ = ("size",)
    SIZE_FIELD_NUMBER: _ClassVar[int]
    size: _common_pb2.TerminalSize
    def __init__(self, size: _Optional[_Union[_common_pb2.TerminalSize, _Mapping]] = ...) -> None: ...

class StartSessionCommand(_message.Message):
    __slots__ = ("config",)
    CONFIG_FIELD_NUMBER: _ClassVar[int]
    config: _common_pb2.SessionConfig
    def __init__(self, config: _Optional[_Union[_common_pb2.SessionConfig, _Mapping]] = ...) -> None: ...

class CloseSessionCommand(_message.Message):
    __slots__ = ("reason", "force")
    REASON_FIELD_NUMBER: _ClassVar[int]
    FORCE_FIELD_NUMBER: _ClassVar[int]
    reason: str
    force: bool
    def __init__(self, reason: _Optional[str] = ..., force: bool = ...) -> None: ...

class SignalCommand(_message.Message):
    __slots__ = ("signal",)
    SIGNAL_FIELD_NUMBER: _ClassVar[int]
    signal: int
    def __init__(self, signal: _Optional[int] = ...) -> None: ...

class CancelCommand(_message.Message):
    __slots__ = ("command_id",)
    COMMAND_ID_FIELD_NUMBER: _ClassVar[int]
    command_id: str
    def __init__(self, command_id: _Optional[str] = ...) -> None: ...

class PingCommand(_message.Message):
    __slots__ = ("sequence",)
    SEQUENCE_FIELD_NUMBER: _ClassVar[int]
    sequence: int
    def __init__(self, sequence: _Optional[int] = ...) -> None: ...

class ConfigUpdateCommand(_message.Message):
    __slots__ = ("config",)
    CONFIG_FIELD_NUMBER: _ClassVar[int]
    config: _common_pb2.SessionConfig
    def __init__(self, config: _Optional[_Union[_common_pb2.SessionConfig, _Mapping]] = ...) -> None: ...

class CreateSessionRequest(_message.Message):
    __slots__ = ("user_id", "name", "config")
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    CONFIG_FIELD_NUMBER: _ClassVar[int]
    user_id: str
    name: str
    config: _common_pb2.SessionConfig
    def __init__(self, user_id: _Optional[str] = ..., name: _Optional[str] = ..., config: _Optional[_Union[_common_pb2.SessionConfig, _Mapping]] = ...) -> None: ...

class CreateSessionResponse(_message.Message):
    __slots__ = ("success", "session_id", "error")
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    success: bool
    session_id: str
    error: str
    def __init__(self, success: bool = ..., session_id: _Optional[str] = ..., error: _Optional[str] = ...) -> None: ...

class CloseSessionRequest(_message.Message):
    __slots__ = ("session_id", "reason", "force")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    REASON_FIELD_NUMBER: _ClassVar[int]
    FORCE_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    reason: str
    force: bool
    def __init__(self, session_id: _Optional[str] = ..., reason: _Optional[str] = ..., force: bool = ...) -> None: ...

class CloseSessionResponse(_message.Message):
    __slots__ = ("success", "error")
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    success: bool
    error: str
    def __init__(self, success: bool = ..., error: _Optional[str] = ...) -> None: ...

class GetSessionStatusRequest(_message.Message):
    __slots__ = ("session_id",)
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    def __init__(self, session_id: _Optional[str] = ...) -> None: ...

class GetSessionStatusResponse(_message.Message):
    __slots__ = ("exists", "status", "electron_hostname", "connected_at", "last_heartbeat_at", "commands_count")
    EXISTS_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    ELECTRON_HOSTNAME_FIELD_NUMBER: _ClassVar[int]
    CONNECTED_AT_FIELD_NUMBER: _ClassVar[int]
    LAST_HEARTBEAT_AT_FIELD_NUMBER: _ClassVar[int]
    COMMANDS_COUNT_FIELD_NUMBER: _ClassVar[int]
    exists: bool
    status: _common_pb2.SessionStatus
    electron_hostname: str
    connected_at: _timestamp_pb2.Timestamp
    last_heartbeat_at: _timestamp_pb2.Timestamp
    commands_count: int
    def __init__(self, exists: bool = ..., status: _Optional[_Union[_common_pb2.SessionStatus, str]] = ..., electron_hostname: _Optional[str] = ..., connected_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., last_heartbeat_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., commands_count: _Optional[int] = ...) -> None: ...

class SendInputRequest(_message.Message):
    __slots__ = ("session_id", "data")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    DATA_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    data: bytes
    def __init__(self, session_id: _Optional[str] = ..., data: _Optional[bytes] = ...) -> None: ...

class SendInputResponse(_message.Message):
    __slots__ = ("success", "error")
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    success: bool
    error: str
    def __init__(self, success: bool = ..., error: _Optional[str] = ...) -> None: ...

class SendResizeRequest(_message.Message):
    __slots__ = ("session_id", "cols", "rows")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    COLS_FIELD_NUMBER: _ClassVar[int]
    ROWS_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    cols: int
    rows: int
    def __init__(self, session_id: _Optional[str] = ..., cols: _Optional[int] = ..., rows: _Optional[int] = ...) -> None: ...

class SendResizeResponse(_message.Message):
    __slots__ = ("success", "error")
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    success: bool
    error: str
    def __init__(self, success: bool = ..., error: _Optional[str] = ...) -> None: ...

class SendSignalRequest(_message.Message):
    __slots__ = ("session_id", "signal")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    SIGNAL_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    signal: int
    def __init__(self, session_id: _Optional[str] = ..., signal: _Optional[int] = ...) -> None: ...

class SendSignalResponse(_message.Message):
    __slots__ = ("success", "error")
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    success: bool
    error: str
    def __init__(self, success: bool = ..., error: _Optional[str] = ...) -> None: ...

class HealthCheckRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class HealthCheckResponse(_message.Message):
    __slots__ = ("healthy", "version", "active_sessions", "connected_clients")
    HEALTHY_FIELD_NUMBER: _ClassVar[int]
    VERSION_FIELD_NUMBER: _ClassVar[int]
    ACTIVE_SESSIONS_FIELD_NUMBER: _ClassVar[int]
    CONNECTED_CLIENTS_FIELD_NUMBER: _ClassVar[int]
    healthy: bool
    version: str
    active_sessions: int
    connected_clients: int
    def __init__(self, healthy: bool = ..., version: _Optional[str] = ..., active_sessions: _Optional[int] = ..., connected_clients: _Optional[int] = ...) -> None: ...
