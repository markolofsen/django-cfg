"""
Custom Exceptions for Django-CFG RPC Client.

Provides specific exception types for better error handling and debugging.
Works independently or with django-cfg-rpc models.
"""

from typing import Any, Optional

# Try to import RPCError from django-cfg-rpc if available
try:
    from django_ipc.models.errors import RPCError
    HAS_DJANGO_CFG_RPC = True
except ImportError:
    # Fallback: simple RPCError for basic error handling
    HAS_DJANGO_CFG_RPC = False

    class RPCError:  # type: ignore
        """Minimal RPCError fallback when django-cfg-rpc not installed."""

        def __init__(self, code: str, message: str, retryable: bool = False, retry_after: Optional[int] = None):
            self.code = code
            self.message = message
            self.retryable = retryable
            self.retry_after = retry_after


class RPCBaseException(Exception):
    """
    Base exception for all RPC-related errors.

    All custom RPC exceptions inherit from this class.
    """

    def __init__(self, message: str):
        """
        Initialize base RPC exception.

        Args:
            message: Error message
        """
        self.message = message
        super().__init__(message)


class RPCTimeoutError(RPCBaseException):
    """
    RPC call timed out waiting for response.

    Raised when BLPOP timeout is exceeded.

    Example:
        >>> try:
        ...     result = rpc.call(method="slow", params=..., timeout=5)
        ... except RPCTimeoutError as e:
        ...     print(f"RPC timeout: {e.message}")
        ...     print(f"Timeout duration: {e.timeout_seconds}s")
    """

    def __init__(self, message: str, method: str, timeout_seconds: int):
        """
        Initialize timeout error.

        Args:
            message: Error message
            method: RPC method that timed out
            timeout_seconds: Timeout duration that was exceeded
        """
        super().__init__(message)
        self.method = method
        self.timeout_seconds = timeout_seconds

    def __str__(self) -> str:
        """String representation."""
        return f"RPC timeout on method '{self.method}' after {self.timeout_seconds}s: {self.message}"


class RPCRemoteError(RPCBaseException):
    """
    Remote RPC execution failed.

    Raised when server returns error response.

    Example:
        >>> try:
        ...     result = rpc.call(method="...", params=...)
        ... except RPCRemoteError as e:
        ...     print(f"Remote error: {e.error.code}")
        ...     print(f"Message: {e.error.message}")
        ...     if e.is_retryable:
        ...         print(f"Can retry after {e.retry_after}s")
    """

    def __init__(self, error: Any):
        """
        Initialize remote error.

        Args:
            error: Structured RPC error from server (RPCError or dict)
        """
        # Handle both RPCError objects and dicts
        if isinstance(error, dict):
            message = error.get("message", "Unknown error")
            self.error = RPCError(
                code=error.get("code", "internal_error"),
                message=message,
                retryable=error.get("retryable", False),
                retry_after=error.get("retry_after"),
            )
        else:
            message = error.message if hasattr(error, "message") else str(error)
            self.error = error

        super().__init__(message)

    def __str__(self) -> str:
        """String representation."""
        code = self.error.code if hasattr(self.error, "code") else "unknown"
        return f"RPC remote error [{code}]: {self.message}"

    @property
    def is_retryable(self) -> bool:
        """Check if error is retryable."""
        return getattr(self.error, "retryable", False)

    @property
    def retry_after(self) -> Optional[int]:
        """Get retry delay in seconds."""
        return getattr(self.error, "retry_after", None)


class RPCConnectionError(RPCBaseException):
    """
    Failed to connect to Redis.

    Raised when Redis connection fails.

    Example:
        >>> try:
        ...     rpc = DjangoCfgRPCClient(redis_url="redis://invalid:6379")
        ... except RPCConnectionError as e:
        ...     print(f"Connection failed: {e.message}")
    """

    def __init__(self, message: str, redis_url: Optional[str] = None):
        """
        Initialize connection error.

        Args:
            message: Error message
            redis_url: Redis URL that failed to connect
        """
        super().__init__(message)
        self.redis_url = redis_url

    def __str__(self) -> str:
        """String representation."""
        if self.redis_url:
            return f"RPC connection error to {self.redis_url}: {self.message}"
        return f"RPC connection error: {self.message}"


class RPCConfigurationError(RPCBaseException):
    """
    RPC configuration error.

    Raised when RPC client is misconfigured.

    Example:
        >>> try:
        ...     rpc = get_rpc_client()  # No config in settings
        ... except RPCConfigurationError as e:
        ...     print(f"Configuration error: {e.message}")
    """

    def __init__(self, message: str, config_key: Optional[str] = None):
        """
        Initialize configuration error.

        Args:
            message: Error message
            config_key: Configuration key that is missing/invalid
        """
        super().__init__(message)
        self.config_key = config_key

    def __str__(self) -> str:
        """String representation."""
        if self.config_key:
            return f"RPC configuration error (key: {self.config_key}): {self.message}"
        return f"RPC configuration error: {self.message}"


__all__ = [
    "RPCBaseException",
    "RPCTimeoutError",
    "RPCRemoteError",
    "RPCConnectionError",
    "RPCConfigurationError",
    "HAS_DJANGO_CFG_RPC",
]
