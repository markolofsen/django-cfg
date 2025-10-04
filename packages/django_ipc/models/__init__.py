"""
WebSocket RPC Models for Django-CFG.

Pydantic 2 models for type-safe WebSocket RPC communication.
All models enforce strict validation and prevent raw dictionary usage.

Example:
    >>> from django_cfg.models.websocket import RPCRequest, NotificationRequest
    >>> request = RPCRequest(
    ...     method="send_notification",
    ...     params=NotificationRequest(user_id="123", message="Hello"),
    ...     reply_to="list:response:abc"
    ... )
"""

from .base import (
    BaseRPCMessage,
    BaseRPCRequest,
    BaseRPCResponse,
)

from .rpc import (
    RPCRequest,
    RPCResponse,
    EchoParams,
    EchoResult,
)

from .notifications import (
    NotificationPriority,
    NotificationRequest,
    NotificationResponse,
    BatchNotificationRequest,
    BatchNotificationResponse,
)

from .broadcast import (
    BroadcastTarget,
    BroadcastRequest,
    BroadcastResponse,
    RoomJoinRequest,
    RoomLeaveRequest,
)

from .errors import (
    RPCErrorCode,
    RPCError,
    ValidationErrorDetail,
    RPCValidationError,
    TimeoutError,
    UserNotConnectedError,
    RateLimitError,
)

from .connections import (
    ConnectionInfo,
    ConnectionStateUpdate,
)

__all__ = [
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
]
