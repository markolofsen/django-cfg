"""
Custom Exceptions for WebSocket RPC.

Provides specific exception types for better error handling and debugging.

File size: ~150 lines
"""

from typing import Optional
from django_cfg.models.websocket import RPCError


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
        ...     if e.error.retryable:
        ...         print(f"Can retry after {e.error.retry_after}s")
    """

    def __init__(self, error: RPCError):
        """
        Initialize remote error.

        Args:
            error: Structured RPC error from server
        """
        super().__init__(error.message)
        self.error = error

    def __str__(self) -> str:
        """String representation."""
        return f"RPC remote error [{self.error.code.value}]: {self.error.message}"

    @property
    def is_retryable(self) -> bool:
        """Check if error is retryable."""
        return self.error.retryable

    @property
    def retry_after(self) -> Optional[int]:
        """Get retry delay in seconds."""
        return self.error.retry_after


class RPCConnectionError(RPCBaseException):
    """
    Failed to connect to Redis or WebSocket server.

    Raised when Redis connection fails.

    Example:
        >>> try:
        ...     rpc = WebSocketRPCClient(redis_url="redis://invalid:6379")
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
]
