"""
Base RPC Message Models.

Foundation classes for all WebSocket RPC messages using Pydantic 2.
Provides common fields, validation, and serialization behavior.

File size: ~150 lines
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime, timezone
from uuid import UUID, uuid4


class BaseRPCMessage(BaseModel):
    """
    Base class for all RPC messages.

    Provides common fields and validation for all message types.
    All RPC messages must include correlation ID and timestamp.

    Example:
        >>> class MyMessage(BaseRPCMessage):
        ...     data: str
        >>> msg = MyMessage(data="test")
        >>> print(msg.correlation_id)  # Auto-generated UUID
    """

    model_config = ConfigDict(
        # Validation settings
        validate_assignment=True,
        validate_default=True,
        extra="forbid",  # Reject unknown fields (security)

        # Behavior settings
        frozen=False,
        str_strip_whitespace=True,
        use_enum_values=True,

        # Serialization settings
        populate_by_name=True,  # Allow alias usage
    )

    correlation_id: UUID = Field(
        default_factory=uuid4,
        description="Unique correlation ID for request/response matching",
        alias="cid",
    )

    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Message creation timestamp (UTC)",
    )

    def get_correlation_id_str(self) -> str:
        """
        Get correlation ID as string.

        Returns:
            String representation of correlation ID

        Example:
            >>> msg = BaseRPCMessage()
            >>> cid = msg.get_correlation_id_str()
            >>> print(cid)  # "550e8400-e29b-41d4-a716-446655440000"
        """
        return str(self.correlation_id)


class BaseRPCRequest(BaseRPCMessage):
    """
    Base class for RPC requests.

    All RPC requests must include method name, reply channel, and timeout.

    Example:
        >>> request = BaseRPCRequest(
        ...     method="echo",
        ...     reply_to="list:response:abc123",
        ...     timeout=30
        ... )
    """

    method: str = Field(
        ...,
        min_length=1,
        max_length=100,
        pattern=r"^[a-zA-Z0-9_\.]+$",
        description="RPC method name (alphanumeric, underscore, dot)",
        examples=["send_notification", "user.get_profile", "echo"],
    )

    reply_to: str = Field(
        ...,
        min_length=1,
        max_length=200,
        description="Redis List key for response delivery",
        examples=["list:response:550e8400-e29b-41d4-a716-446655440000"],
    )

    timeout: int = Field(
        default=30,
        ge=0,
        le=300,
        description="Maximum wait time for response (seconds). Use 0 for fire-and-forget.",
    )


class BaseRPCResponse(BaseRPCMessage):
    """
    Base class for RPC responses.

    All RPC responses must indicate success/failure and may include error details.

    Example:
        >>> # Success response
        >>> response = BaseRPCResponse(
        ...     correlation_id=request.correlation_id,
        ...     success=True
        ... )
        >>>
        >>> # Error response
        >>> response = BaseRPCResponse(
        ...     correlation_id=request.correlation_id,
        ...     success=False,
        ...     error="User not found",
        ...     error_code="user_not_found"
        ... )
    """

    success: bool = Field(
        ...,
        description="Whether RPC call succeeded",
    )

    error: Optional[str] = Field(
        default=None,
        max_length=1000,
        description="Error message if success=False",
    )

    error_code: Optional[str] = Field(
        default=None,
        pattern=r"^[a-z_]+$",
        max_length=50,
        description="Machine-readable error code (snake_case)",
        examples=["timeout", "user_not_found", "validation_error"],
    )


__all__ = [
    "BaseRPCMessage",
    "BaseRPCRequest",
    "BaseRPCResponse",
]
