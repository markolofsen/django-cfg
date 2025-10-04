"""
django-ipc - Type-safe RPC layer with Redis IPC

Lightweight RPC library for Django-CFG ecosystem:
- Type-safe Pydantic 2 models
- Redis-based IPC (Streams + Lists + Pub/Sub)
- Bridge for WebSocket servers
- Structured logging with rotation
- No Django dependency
"""

__version__ = "1.0.4"
__author__ = "Django-CFG Team"
__email__ = "info@djangocfg.com"

# Import models for easy access
from .models import (
    # Base models
    BaseRPCMessage,
    BaseRPCRequest,
    BaseRPCResponse,
    # RPC models
    RPCRequest,
    RPCResponse,
    EchoParams,
    EchoResult,
    # Notification models
    NotificationPriority,
    NotificationRequest,
    NotificationResponse,
    BatchNotificationRequest,
    BatchNotificationResponse,
    # Broadcast models
    BroadcastTarget,
    BroadcastRequest,
    BroadcastResponse,
    RoomJoinRequest,
    RoomLeaveRequest,
    # Error models
    RPCErrorCode,
    RPCError,
    ValidationErrorDetail,
    RPCValidationError,
    TimeoutError,
    UserNotConnectedError,
    RateLimitError,
    # Connection models
    ConnectionInfo,
    ConnectionStateUpdate,
)

# Import logger for easy access
from .logger import (
    RPCLogger,
    LoggerConfig,
    LogRotationConfig,
    LogLevel,
    LoggingMiddleware,
    auto_log_rpc,
)

__all__ = [
    # Version
    "__version__",
    # Base models
    "BaseRPCMessage",
    "BaseRPCRequest",
    "BaseRPCResponse",
    # RPC models
    "RPCRequest",
    "RPCResponse",
    "EchoParams",
    "EchoResult",
    # Notification models
    "NotificationPriority",
    "NotificationRequest",
    "NotificationResponse",
    "BatchNotificationRequest",
    "BatchNotificationResponse",
    # Broadcast models
    "BroadcastTarget",
    "BroadcastRequest",
    "BroadcastResponse",
    "RoomJoinRequest",
    "RoomLeaveRequest",
    # Error models
    "RPCErrorCode",
    "RPCError",
    "ValidationErrorDetail",
    "RPCValidationError",
    "TimeoutError",
    "UserNotConnectedError",
    "RateLimitError",
    # Connection models
    "ConnectionInfo",
    "ConnectionStateUpdate",
    # Logger
    "RPCLogger",
    "LoggerConfig",
    "LogRotationConfig",
    "LogLevel",
    "LoggingMiddleware",
    "auto_log_rpc",
]
