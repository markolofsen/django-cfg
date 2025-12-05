from google.protobuf import timestamp_pb2 as _timestamp_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class SessionStatus(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    SESSION_STATUS_UNSPECIFIED: _ClassVar[SessionStatus]
    PENDING: _ClassVar[SessionStatus]
    CONNECTED: _ClassVar[SessionStatus]
    DISCONNECTED: _ClassVar[SessionStatus]
    ERROR: _ClassVar[SessionStatus]

class CommandStatus(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    COMMAND_STATUS_UNSPECIFIED: _ClassVar[CommandStatus]
    CMD_PENDING: _ClassVar[CommandStatus]
    CMD_RUNNING: _ClassVar[CommandStatus]
    CMD_SUCCESS: _ClassVar[CommandStatus]
    CMD_FAILED: _ClassVar[CommandStatus]
    CMD_CANCELLED: _ClassVar[CommandStatus]
    CMD_TIMEOUT: _ClassVar[CommandStatus]

class LogLevel(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    LOG_LEVEL_UNSPECIFIED: _ClassVar[LogLevel]
    LOG_DEBUG: _ClassVar[LogLevel]
    LOG_INFO: _ClassVar[LogLevel]
    LOG_WARNING: _ClassVar[LogLevel]
    LOG_ERROR: _ClassVar[LogLevel]
SESSION_STATUS_UNSPECIFIED: SessionStatus
PENDING: SessionStatus
CONNECTED: SessionStatus
DISCONNECTED: SessionStatus
ERROR: SessionStatus
COMMAND_STATUS_UNSPECIFIED: CommandStatus
CMD_PENDING: CommandStatus
CMD_RUNNING: CommandStatus
CMD_SUCCESS: CommandStatus
CMD_FAILED: CommandStatus
CMD_CANCELLED: CommandStatus
CMD_TIMEOUT: CommandStatus
LOG_LEVEL_UNSPECIFIED: LogLevel
LOG_DEBUG: LogLevel
LOG_INFO: LogLevel
LOG_WARNING: LogLevel
LOG_ERROR: LogLevel

class TerminalSize(_message.Message):
    __slots__ = ("rows", "cols", "width", "height")
    ROWS_FIELD_NUMBER: _ClassVar[int]
    COLS_FIELD_NUMBER: _ClassVar[int]
    WIDTH_FIELD_NUMBER: _ClassVar[int]
    HEIGHT_FIELD_NUMBER: _ClassVar[int]
    rows: int
    cols: int
    width: int
    height: int
    def __init__(self, rows: _Optional[int] = ..., cols: _Optional[int] = ..., width: _Optional[int] = ..., height: _Optional[int] = ...) -> None: ...

class SessionConfig(_message.Message):
    __slots__ = ("session_id", "shell", "working_directory", "env", "size")
    class EnvEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    SHELL_FIELD_NUMBER: _ClassVar[int]
    WORKING_DIRECTORY_FIELD_NUMBER: _ClassVar[int]
    ENV_FIELD_NUMBER: _ClassVar[int]
    SIZE_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    shell: str
    working_directory: str
    env: _containers.ScalarMap[str, str]
    size: TerminalSize
    def __init__(self, session_id: _Optional[str] = ..., shell: _Optional[str] = ..., working_directory: _Optional[str] = ..., env: _Optional[_Mapping[str, str]] = ..., size: _Optional[_Union[TerminalSize, _Mapping]] = ...) -> None: ...
