"""
Error Models for WebSocket RPC.

Pydantic 2 models for structured error handling in RPC layer.
Provides machine-readable error codes and detailed error information.

File size: ~250 lines
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, Any
from enum import Enum


class RPCErrorCode(str, Enum):
    """
    Standard RPC error codes.

    Machine-readable error codes for consistent error handling.
    """

    # Client errors (4xx-like)
    TIMEOUT = "timeout"
    METHOD_NOT_FOUND = "method_not_found"
    INVALID_PARAMS = "invalid_params"
    VALIDATION_ERROR = "validation_error"
    UNAUTHORIZED = "unauthorized"
    RATE_LIMIT_EXCEEDED = "rate_limit_exceeded"

    # Server errors (5xx-like)
    INTERNAL_ERROR = "internal_error"
    SERVICE_UNAVAILABLE = "service_unavailable"

    # Resource errors
    USER_NOT_CONNECTED = "user_not_connected"
    ROOM_NOT_FOUND = "room_not_found"
    RESOURCE_NOT_FOUND = "resource_not_found"

    # Connection errors
    CONNECTION_ERROR = "connection_error"
    REDIS_ERROR = "redis_error"


class RPCError(BaseModel):
    """
    Structured RPC error information.

    Provides complete error context for debugging and recovery.

    Example:
        >>> error = RPCError(
        ...     code=RPCErrorCode.USER_NOT_CONNECTED,
        ...     message="User 'user_123' is not connected",
        ...     details={"user_id": "user_123", "last_seen": "2025-01-10T10:30:00Z"},
        ...     retryable=True,
        ...     retry_after=5
        ... )
    """

    model_config = ConfigDict(validate_assignment=True, extra="forbid")

    code: RPCErrorCode = Field(
        ...,
        description="Machine-readable error code",
    )

    message: str = Field(
        ...,
        min_length=1,
        max_length=500,
        description="Human-readable error message",
    )

    details: Optional[dict[str, Any]] = Field(
        default=None,
        description="Additional error details for debugging",
    )

    retryable: bool = Field(
        default=False,
        description="Whether operation can be retried",
    )

    retry_after: Optional[int] = Field(
        default=None,
        ge=0,
        le=3600,
        description="Seconds to wait before retry (if retryable)",
    )

    def __str__(self) -> str:
        """String representation of error."""
        return f"[{self.code.value}] {self.message}"


class ValidationErrorDetail(BaseModel):
    """
    Pydantic validation error detail.

    Provides field-level validation error information.

    Example:
        >>> detail = ValidationErrorDetail(
        ...     field="email",
        ...     error="value is not a valid email address",
        ...     input_value="invalid-email"
        ... )
    """

    model_config = ConfigDict(validate_assignment=True)

    field: str = Field(
        ...,
        min_length=1,
        max_length=200,
        description="Field name that failed validation",
    )

    error: str = Field(
        ...,
        min_length=1,
        max_length=500,
        description="Error message for this field",
    )

    input_value: Optional[Any] = Field(
        default=None,
        description="Invalid input value (if available)",
    )


class RPCValidationError(RPCError):
    """
    Validation error with field-level details.

    Extends RPCError with specific validation error information.

    Example:
        >>> error = RPCValidationError(
        ...     code=RPCErrorCode.VALIDATION_ERROR,
        ...     message="Request validation failed",
        ...     validation_errors=[
        ...         ValidationErrorDetail(
        ...             field="user_id",
        ...             error="field required",
        ...             input_value=None
        ...         ),
        ...         ValidationErrorDetail(
        ...             field="message",
        ...             error="ensure this value has at most 2000 characters",
        ...             input_value="very long message..."
        ...         )
        ...     ]
        ... )
    """

    code: RPCErrorCode = Field(
        default=RPCErrorCode.VALIDATION_ERROR,
        frozen=True,
    )

    validation_errors: list[ValidationErrorDetail] = Field(
        ...,
        min_length=1,
        description="List of field validation errors",
    )


class TimeoutError(RPCError):
    """
    Timeout error.

    Raised when RPC call exceeds timeout duration.

    Example:
        >>> error = TimeoutError(
        ...     code=RPCErrorCode.TIMEOUT,
        ...     message="RPC call timed out after 30 seconds",
        ...     timeout_seconds=30,
        ...     retryable=True,
        ...     retry_after=5
        ... )
    """

    code: RPCErrorCode = Field(
        default=RPCErrorCode.TIMEOUT,
        frozen=True,
    )

    timeout_seconds: int = Field(
        ...,
        ge=0,
        description="Timeout duration that was exceeded",
    )

    retryable: bool = Field(
        default=True,
        frozen=True,
    )


class UserNotConnectedError(RPCError):
    """
    User not connected error.

    Raised when trying to send message to disconnected user.

    Example:
        >>> error = UserNotConnectedError(
        ...     code=RPCErrorCode.USER_NOT_CONNECTED,
        ...     message="User is not connected",
        ...     user_id="user_123"
        ... )
    """

    code: RPCErrorCode = Field(
        default=RPCErrorCode.USER_NOT_CONNECTED,
        frozen=True,
    )

    user_id: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="User ID that is not connected",
    )


class RateLimitError(RPCError):
    """
    Rate limit exceeded error.

    Raised when too many requests are made in short time.

    Example:
        >>> error = RateLimitError(
        ...     code=RPCErrorCode.RATE_LIMIT_EXCEEDED,
        ...     message="Rate limit exceeded: 100 requests per minute",
        ...     limit=100,
        ...     window_seconds=60,
        ...     retry_after=45,
        ...     retryable=True
        ... )
    """

    code: RPCErrorCode = Field(
        default=RPCErrorCode.RATE_LIMIT_EXCEEDED,
        frozen=True,
    )

    limit: int = Field(
        ...,
        ge=1,
        description="Rate limit threshold",
    )

    window_seconds: int = Field(
        ...,
        ge=1,
        description="Rate limit window in seconds",
    )

    retryable: bool = Field(
        default=True,
        frozen=True,
    )


__all__ = [
    "RPCErrorCode",
    "RPCError",
    "ValidationErrorDetail",
    "RPCValidationError",
    "TimeoutError",
    "UserNotConnectedError",
    "RateLimitError",
]
