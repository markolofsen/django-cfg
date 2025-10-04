"""
Notification Models for WebSocket RPC.

Pydantic 2 models for user notifications via WebSocket.
Supports individual and batch notifications with priority levels.

File size: ~350 lines
"""

from pydantic import BaseModel, Field, field_validator, ConfigDict, model_validator
from typing import Optional, Any
from datetime import datetime, timezone
from enum import Enum


class NotificationPriority(str, Enum):
    """
    Notification priority levels.

    Determines how notifications are displayed and processed.
    """

    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


class NotificationRequest(BaseModel):
    """
    Request to send notification to user via WebSocket.

    Type-safe notification with validation for user targeting,
    content, and optional metadata.

    Example:
        >>> request = NotificationRequest(
        ...     user_id="user_123",
        ...     notification_type="order_update",
        ...     title="Order Confirmed",
        ...     message="Your order #12345 has been confirmed",
        ...     priority=NotificationPriority.HIGH,
        ...     data={"order_id": "12345", "status": "confirmed"}
        ... )
    """

    model_config = ConfigDict(
        validate_assignment=True,
        extra="ignore",  # Allow extra fields for backward compatibility
        str_strip_whitespace=True,
    )

    user_id: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Target user ID",
        examples=["user_123", "550e8400-e29b-41d4-a716-446655440000"],
    )

    type: str = Field(
        ...,
        min_length=1,
        max_length=50,
        pattern=r"^[a-z_]+$",
        description="Notification type (snake_case)",
        examples=["order_update", "message_received", "system_alert"],
    )

    title: str = Field(
        ...,
        min_length=1,
        max_length=200,
        description="Notification title",
    )

    message: str = Field(
        ...,
        min_length=1,
        max_length=2000,
        description="Notification message content",
    )

    priority: NotificationPriority = Field(
        default=NotificationPriority.NORMAL,
        description="Notification priority level",
    )

    data: Optional[dict[str, Any]] = Field(
        default=None,
        description="Additional structured data (must have valid keys)",
    )

    expires_at: Optional[datetime] = Field(
        default=None,
        description="Notification expiration time (UTC)",
    )

    @field_validator("data")
    @classmethod
    def validate_data_keys(cls, v: Optional[dict[str, Any]]) -> Optional[dict[str, Any]]:
        """
        Ensure data keys are valid Python identifiers.

        Args:
            v: Data dictionary to validate

        Returns:
            Validated data dictionary

        Raises:
            ValueError: If any key is not a valid identifier

        Example:
            >>> # Valid
            >>> NotificationRequest(..., data={"order_id": 123, "status": "ok"})
            >>> # Invalid (raises ValueError)
            >>> NotificationRequest(..., data={"123-invalid": "value"})
        """
        if v is None:
            return v

        import re
        pattern = re.compile(r"^[a-zA-Z_][a-zA-Z0-9_]*$")

        for key in v.keys():
            if not pattern.match(key):
                raise ValueError(
                    f"Invalid data key '{key}'. Must be valid Python identifier "
                    f"(start with letter/underscore, contain only alphanumeric/underscore)."
                )

        return v

    @field_validator("expires_at")
    @classmethod
    def validate_expires_at(cls, v: Optional[datetime]) -> Optional[datetime]:
        """
        Ensure expiration is in the future.

        Args:
            v: Expiration datetime to validate

        Returns:
            Validated expiration datetime

        Raises:
            ValueError: If expiration is in the past
        """
        if v is not None and v <= datetime.now(timezone.utc):
            raise ValueError("expires_at must be in the future")

        return v


class NotificationResponse(BaseModel):
    """
    Response from sending notification.

    Indicates whether notification was delivered and connection status.

    Example:
        >>> response = NotificationResponse(
        ...     user_id="user_123",
        ...     delivered=True,
        ...     connections=2
        ... )
    """

    model_config = ConfigDict(validate_assignment=True)

    user_id: str = Field(
        ...,
        description="Target user ID",
    )

    delivered: bool = Field(
        ...,
        description="Whether notification was delivered to at least one connection",
    )

    connections: int = Field(
        ...,
        ge=0,
        description="Number of connections that received notification",
    )

    error: Optional[str] = Field(
        default=None,
        description="Error message if delivery failed",
    )

    queued_for_later: bool = Field(
        default=False,
        description="Whether notification was queued for offline delivery",
    )


class BatchNotificationRequest(BaseModel):
    """
    Send multiple notifications to multiple users.

    Each notification can have different content for different users.

    Example:
        >>> batch = BatchNotificationRequest(
        ...     notifications=[
        ...         NotificationRequest(
        ...             user_id="user_1",
        ...             type="order_update",
        ...             title="Order Confirmed",
        ...             message="Your order #12345 has been confirmed"
        ...         ),
        ...         NotificationRequest(
        ...             user_id="user_2",
        ...             type="message",
        ...             title="New Message",
        ...             message="You have a new message from Alice"
        ...         ),
        ...     ]
        ... )
    """

    model_config = ConfigDict(validate_assignment=True, extra="ignore")

    notifications: list[NotificationRequest] = Field(
        ...,
        min_length=1,
        max_length=1000,
        description="List of notifications to send (max 1000)",
    )

    @field_validator("notifications")
    @classmethod
    def validate_unique_user_ids(cls, v: list[NotificationRequest]) -> list[NotificationRequest]:
        """
        Ensure user IDs are unique in batch.

        Args:
            v: List of notification requests

        Returns:
            Validated list of notification requests

        Raises:
            ValueError: If duplicate user IDs found
        """
        user_ids = [notif.user_id for notif in v]
        if len(user_ids) != len(set(user_ids)):
            raise ValueError("Duplicate user_ids found in batch (each user can only receive one notification per batch)")

        return v


class BatchNotificationResponse(BaseModel):
    """
    Response from batch notification.

    Summary of delivery results for all users.

    Example:
        >>> response = BatchNotificationResponse(
        ...     total=100,
        ...     delivered=85,
        ...     failed=15,
        ...     results=[
        ...         {"user_id": "user_1", "delivered": True, "connections": 2},
        ...         {"user_id": "user_2", "delivered": False, "connections": 0},
        ...         # ...
        ...     ]
        ... )
    """

    model_config = ConfigDict(validate_assignment=True)

    total: int = Field(
        ...,
        ge=0,
        description="Total users targeted",
    )

    delivered: int = Field(
        ...,
        ge=0,
        description="Successfully delivered",
    )

    failed: int = Field(
        ...,
        ge=0,
        description="Failed deliveries",
    )

    results: list[dict] = Field(
        ...,
        description="Per-user results (list of NotificationResponse dicts)",
    )


__all__ = [
    "NotificationPriority",
    "NotificationRequest",
    "NotificationResponse",
    "BatchNotificationRequest",
    "BatchNotificationResponse",
]
