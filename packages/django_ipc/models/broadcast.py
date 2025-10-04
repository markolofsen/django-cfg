"""
Broadcast Models for WebSocket RPC.

Pydantic 2 models for broadcasting messages to multiple users/channels.
Supports global, room-based, and filtered broadcasts.

File size: ~250 lines
"""

from pydantic import BaseModel, Field, ConfigDict, model_validator
from typing import Optional, Any
from enum import Enum


class BroadcastTarget(str, Enum):
    """
    Broadcast target audiences.

    Defines who should receive the broadcast message.
    """

    ALL = "all"  # All connected users
    ROOM = "room"  # Users in specific room/channel
    USER = "user"  # Specific user (all connections)
    USERS = "users"  # Multiple specific users


class BroadcastRequest(BaseModel):
    """
    Request to broadcast message to multiple users.

    Type-safe broadcast with target filtering and message validation.
    """

    model_config = ConfigDict(
        validate_assignment=True,
        extra="ignore",  # Allow extra fields for backward compatibility
        str_strip_whitespace=True,
    )

    target: BroadcastTarget = Field(
        ...,
        description="Target audience for broadcast",
    )

    type: str = Field(
        default="info",
        min_length=1,
        max_length=50,
        pattern=r"^[a-z_]+$",
        description="Message type (snake_case)",
        examples=["info", "warning", "error", "success"],
    )

    title: str = Field(
        ...,
        min_length=1,
        max_length=200,
        description="Broadcast title",
    )

    message: str = Field(
        ...,
        min_length=1,
        max_length=1000,
        description="Broadcast message",
    )

    # Optional targeting parameters
    room: Optional[str] = Field(
        default=None,
        min_length=1,
        max_length=100,
        description="Room name (required if target=ROOM)",
    )

    user_id: Optional[str] = Field(
        default=None,
        min_length=1,
        max_length=100,
        description="User ID (required if target=USER)",
    )

    user_ids: Optional[list[str]] = Field(
        default=None,
        min_length=1,
        max_length=1000,
        description="User IDs (required if target=USERS)",
    )

    data: Optional[dict[str, Any]] = Field(
        default=None,
        description="Additional structured data",
    )

    @model_validator(mode="after")
    def check_target_params(self) -> "BroadcastRequest":
        """Validate target-specific parameters."""
        if self.target == BroadcastTarget.ROOM and not self.room:
            raise ValueError("room is required when target=ROOM")
        if self.target == BroadcastTarget.USER and not self.user_id:
            raise ValueError("user_id is required when target=USER")
        if self.target == BroadcastTarget.USERS and not self.user_ids:
            raise ValueError("user_ids is required when target=USERS")
        return self


class BroadcastResponse(BaseModel):
    """
    Response from broadcasting.

    Indicates delivery status and metrics.

    Example:
        >>> response = BroadcastResponse(
        ...     target=BroadcastTarget.ROOM,
        ...     recipients=5,
        ...     room="game_123"
        ... )
    """

    model_config = ConfigDict(validate_assignment=True)

    target: BroadcastTarget = Field(
        ...,
        description="Target that was broadcast to",
    )

    recipients: int = Field(
        ...,
        ge=0,
        description="Number of connections that received broadcast",
    )

    room: Optional[str] = Field(
        default=None,
        description="Room name (if target was ROOM)",
    )

    user_id: Optional[str] = Field(
        default=None,
        description="User ID (if target was USER)",
    )


class RoomJoinRequest(BaseModel):
    """
    Request to join a room.

    Type-safe room joining with optional notification.

    Example:
        >>> request = RoomJoinRequest(
        ...     room="game_123",
        ...     notify_room=True
        ... )
    """

    model_config = ConfigDict(
        validate_assignment=True,
        extra="ignore",
        str_strip_whitespace=True,
    )

    room: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Room name to join",
    )

    notify_room: bool = Field(
        default=False,
        description="Send join notification to room members",
    )


class RoomLeaveRequest(BaseModel):
    """
    Request to leave a room.

    Type-safe room leaving with optional notification.

    Example:
        >>> request = RoomLeaveRequest(
        ...     room="game_123",
        ...     notify_room=True
        ... )
    """

    model_config = ConfigDict(
        validate_assignment=True,
        extra="ignore",
        str_strip_whitespace=True,
    )

    room: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Room name to leave",
    )

    notify_room: bool = Field(
        default=False,
        description="Send leave notification to room members",
    )


__all__ = [
    "BroadcastTarget",
    "BroadcastRequest",
    "BroadcastResponse",
    "RoomJoinRequest",
    "RoomLeaveRequest",
]
