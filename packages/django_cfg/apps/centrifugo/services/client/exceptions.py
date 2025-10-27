"""
Custom Exceptions for Centrifugo Client.

Provides specific exception types for better error handling and debugging.
Mirrors legacy WebSocket solution exception patterns for easy migration.
"""

from typing import Optional


class CentrifugoBaseException(Exception):
    """
    Base exception for all Centrifugo-related errors.

    All custom Centrifugo exceptions inherit from this class.
    """

    def __init__(self, message: str):
        """
        Initialize base Centrifugo exception.

        Args:
            message: Error message
        """
        self.message = message
        super().__init__(message)


class CentrifugoTimeoutError(CentrifugoBaseException):
    """
    Publish call timed out waiting for ACK.

    Raised when ACK timeout is exceeded.

    Example:
        >>> try:
        ...     result = client.publish_with_ack(
        ...         channel="user#123",
        ...         data={"msg": "test"},
        ...         ack_timeout=5
        ...     )
        ... except CentrifugoTimeoutError as e:
        ...     print(f"Timeout: {e.message}")
        ...     print(f"Channel: {e.channel}")
    """

    def __init__(self, message: str, channel: str, timeout_seconds: int):
        """
        Initialize timeout error.

        Args:
            message: Error message
            channel: Channel that timed out
            timeout_seconds: Timeout duration that was exceeded
        """
        super().__init__(message)
        self.channel = channel
        self.timeout_seconds = timeout_seconds

    def __str__(self) -> str:
        """String representation."""
        return f"Centrifugo timeout on channel '{self.channel}' after {self.timeout_seconds}s: {self.message}"


class CentrifugoPublishError(CentrifugoBaseException):
    """
    Failed to publish message to Centrifugo.

    Raised when wrapper returns error or HTTP request fails.

    Example:
        >>> try:
        ...     result = client.publish(channel="test", data={})
        ... except CentrifugoPublishError as e:
        ...     print(f"Publish failed: {e.message}")
        ...     print(f"Status code: {e.status_code}")
    """

    def __init__(
        self,
        message: str,
        channel: Optional[str] = None,
        status_code: Optional[int] = None,
        response_data: Optional[dict] = None,
    ):
        """
        Initialize publish error.

        Args:
            message: Error message
            channel: Channel that failed
            status_code: HTTP status code from wrapper
            response_data: Response data from wrapper
        """
        super().__init__(message)
        self.channel = channel
        self.status_code = status_code
        self.response_data = response_data

    def __str__(self) -> str:
        """String representation."""
        parts = [f"Centrifugo publish error: {self.message}"]
        if self.channel:
            parts.append(f"(channel: {self.channel})")
        if self.status_code:
            parts.append(f"(HTTP {self.status_code})")
        return " ".join(parts)


class CentrifugoConnectionError(CentrifugoBaseException):
    """
    Failed to connect to wrapper.

    Raised when HTTP connection to wrapper fails.

    Example:
        >>> try:
        ...     client = CentrifugoClient(wrapper_url="http://invalid:8080")
        ...     client.health_check()
        ... except CentrifugoConnectionError as e:
        ...     print(f"Connection failed: {e.message}")
    """

    def __init__(self, message: str, wrapper_url: Optional[str] = None):
        """
        Initialize connection error.

        Args:
            message: Error message
            wrapper_url: Wrapper URL that failed to connect
        """
        super().__init__(message)
        self.wrapper_url = wrapper_url

    def __str__(self) -> str:
        """String representation."""
        if self.wrapper_url:
            return f"Centrifugo connection error to {self.wrapper_url}: {self.message}"
        return f"Centrifugo connection error: {self.message}"


class CentrifugoConfigurationError(CentrifugoBaseException):
    """
    Centrifugo configuration error.

    Raised when Centrifugo client is misconfigured.

    Example:
        >>> try:
        ...     client = get_centrifugo_client()  # No config in settings
        ... except CentrifugoConfigurationError as e:
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
            return f"Centrifugo configuration error (key: {self.config_key}): {self.message}"
        return f"Centrifugo configuration error: {self.message}"


class CentrifugoValidationError(CentrifugoBaseException):
    """
    Data validation error.

    Raised when Pydantic model validation fails.

    Example:
        >>> try:
        ...     client.publish(channel="test", data="invalid")
        ... except CentrifugoValidationError as e:
        ...     print(f"Validation failed: {e.message}")
    """

    def __init__(self, message: str, validation_errors: Optional[list] = None):
        """
        Initialize validation error.

        Args:
            message: Error message
            validation_errors: List of validation errors from Pydantic
        """
        super().__init__(message)
        self.validation_errors = validation_errors or []

    def __str__(self) -> str:
        """String representation."""
        if self.validation_errors:
            errors_str = "; ".join(str(e) for e in self.validation_errors)
            return f"Centrifugo validation error: {self.message} ({errors_str})"
        return f"Centrifugo validation error: {self.message}"


__all__ = [
    "CentrifugoBaseException",
    "CentrifugoTimeoutError",
    "CentrifugoPublishError",
    "CentrifugoConnectionError",
    "CentrifugoConfigurationError",
    "CentrifugoValidationError",
]
