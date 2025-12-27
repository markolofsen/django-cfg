"""
gRPC Configuration Constants.

All values are retrieved from DjangoConfig.grpc with fallback to defaults.
Uses get_current_config() for type-safe Pydantic configuration.

Usage:
    from django_cfg.apps.integrations.grpc.configs.constants import (
        get_grpc_port,
        get_grpc_host,
        get_rpc_call_timeout,
    )

Configuration is read from:
    1. DjangoConfig.grpc (Pydantic config) - preferred
    2. Hardcoded defaults - fallback
"""

from __future__ import annotations

from functools import lru_cache
from typing import TYPE_CHECKING, Final, Optional

if TYPE_CHECKING:
    from django_cfg.models.api.grpc import GRPCConfig

# =============================================================================
# Default Values (used when config is not available)
# =============================================================================

# Network defaults
_DEFAULT_HOST: Final[str] = "localhost"
_DEFAULT_PORT: Final[int] = 50051
_BIND_HOST_IPV6: Final[str] = "[::]"
_BIND_HOST_IPV4: Final[str] = "0.0.0.0"

# Timeout defaults (seconds)
_DEFAULT_CHANNEL_READY_TIMEOUT: Final[float] = 5.0
_DEFAULT_RPC_CALL_TIMEOUT: Final[float] = 5.0
_DEFAULT_CONNECT_TIMEOUT: Final[float] = 3.0
_DEFAULT_QUEUE_TIMEOUT: Final[float] = 10.0
_DEFAULT_ROUTING_TIMEOUT: Final[float] = 5.0

# Keepalive defaults (milliseconds)
_DEFAULT_KEEPALIVE_TIME_MS: Final[int] = 10000  # 10 seconds (matches Go client)
_DEFAULT_KEEPALIVE_TIMEOUT_MS: Final[int] = 5000  # 5 seconds (matches Go client)
_DEFAULT_MAX_CONNECTION_IDLE_MS: Final[int] = 7200000  # 2 hours

# Message limits
_DEFAULT_MAX_MESSAGE_LENGTH: Final[int] = 4 * 1024 * 1024  # 4MB

# Retry defaults
_DEFAULT_MAX_RETRIES: Final[int] = 3

# Queue defaults
_DEFAULT_QUEUE_SIZE: Final[int] = 1000

# Circuit breaker defaults
_DEFAULT_CB_THRESHOLD: Final[int] = 5
_DEFAULT_CB_TIMEOUT: Final[float] = 60.0

# Error handling
_DEFAULT_MAX_CONSECUTIVE_ERRORS: Final[int] = 3


# =============================================================================
# Config Access
# =============================================================================


def _get_grpc_config() -> Optional["GRPCConfig"]:
    """Get gRPC config from current DjangoConfig."""
    try:
        from django_cfg.core.config import get_current_config

        config = get_current_config()
        if config and hasattr(config, "grpc") and config.grpc:
            return config.grpc
    except Exception:
        pass
    return None


# =============================================================================
# Network Configuration
# =============================================================================


def get_grpc_host() -> str:
    """Get default host for client connections."""
    config = _get_grpc_config()
    if config and config.server:
        return config.server.host
    return _DEFAULT_HOST


def get_grpc_port() -> int:
    """Get default port for gRPC server and client connections."""
    config = _get_grpc_config()
    if config and config.server:
        return config.server.port
    return _DEFAULT_PORT


# Static bind addresses (not configurable)
GRPC_BIND_HOST_IPV6: Final[str] = _BIND_HOST_IPV6
GRPC_BIND_HOST_IPV4: Final[str] = _BIND_HOST_IPV4


# =============================================================================
# Timeout Configuration
# =============================================================================


def get_channel_ready_timeout() -> float:
    """Get timeout for waiting for channel to become ready."""
    return _DEFAULT_CHANNEL_READY_TIMEOUT


def get_rpc_call_timeout() -> float:
    """Get default timeout for RPC calls."""
    return _DEFAULT_RPC_CALL_TIMEOUT


def get_connect_timeout() -> float:
    """Get timeout for establishing connection."""
    return _DEFAULT_CONNECT_TIMEOUT


def get_queue_timeout() -> float:
    """Get timeout for queue operations."""
    return _DEFAULT_QUEUE_TIMEOUT


def get_routing_timeout() -> float:
    """Get timeout for cross-process routing calls."""
    return _DEFAULT_ROUTING_TIMEOUT


# =============================================================================
# Keepalive Configuration
# =============================================================================


def get_keepalive_time_ms() -> int:
    """Get keepalive ping interval in milliseconds."""
    config = _get_grpc_config()
    if config and config.server and config.server.keepalive:
        return config.server.keepalive.time_ms
    return _DEFAULT_KEEPALIVE_TIME_MS


def get_keepalive_timeout_ms() -> int:
    """Get keepalive ping timeout in milliseconds."""
    config = _get_grpc_config()
    if config and config.server and config.server.keepalive:
        return config.server.keepalive.timeout_ms
    return _DEFAULT_KEEPALIVE_TIMEOUT_MS


def get_max_connection_idle_ms() -> int:
    """Get maximum idle connection time in milliseconds."""
    config = _get_grpc_config()
    if config and config.server and config.server.connection_limits:
        return config.server.connection_limits.max_connection_idle_ms
    return _DEFAULT_MAX_CONNECTION_IDLE_MS


def get_keepalive_permit_without_calls() -> bool:
    """Allow keepalive pings even without active calls."""
    config = _get_grpc_config()
    if config and config.server and config.server.keepalive:
        return config.server.keepalive.permit_without_calls
    return True


def get_max_pings_without_data() -> int:
    """Get maximum pings allowed without data."""
    config = _get_grpc_config()
    if config and config.server and config.server.keepalive:
        return config.server.keepalive.max_pings_without_data
    return 0  # Unlimited for streaming


# =============================================================================
# Message Limits
# =============================================================================


def get_max_message_length() -> int:
    """Get maximum message size in bytes."""
    config = _get_grpc_config()
    if config and config.server:
        return config.server.max_send_message_length
    return _DEFAULT_MAX_MESSAGE_LENGTH


def get_max_send_message_length() -> int:
    """Get maximum outbound message size."""
    config = _get_grpc_config()
    if config and config.server:
        return config.server.max_send_message_length
    return _DEFAULT_MAX_MESSAGE_LENGTH


def get_max_receive_message_length() -> int:
    """Get maximum inbound message size."""
    config = _get_grpc_config()
    if config and config.server:
        return config.server.max_receive_message_length
    return _DEFAULT_MAX_MESSAGE_LENGTH


# =============================================================================
# Retry Configuration
# =============================================================================


# Static retry settings (not in Pydantic config yet)
GRPC_ENABLE_RETRIES: Final[bool] = True
GRPC_RETRY_BACKOFF_INITIAL_MS: Final[int] = 100
GRPC_RETRY_BACKOFF_MAX_MS: Final[int] = 1000
GRPC_RETRY_BACKOFF_MULTIPLIER: Final[float] = 2.0


def get_max_retries() -> int:
    """Get maximum number of retry attempts."""
    return _DEFAULT_MAX_RETRIES


# =============================================================================
# Queue Configuration
# =============================================================================


def get_default_queue_size() -> int:
    """Get default queue size for streaming operations."""
    return _DEFAULT_QUEUE_SIZE


# Static queue settings
GRPC_MAX_QUEUE_SIZE: Final[int] = 100000


# =============================================================================
# Streaming Configuration
# =============================================================================

# Static streaming settings
GRPC_DEFAULT_PING_INTERVAL: Final[float] = 5.0
GRPC_DEFAULT_PING_TIMEOUT: Final[float] = 30.0
GRPC_MAX_PING_INTERVAL: Final[float] = 300.0
GRPC_MAX_PING_TIMEOUT: Final[float] = 600.0


# =============================================================================
# Circuit Breaker Configuration
# =============================================================================


def get_circuit_breaker_threshold() -> int:
    """Get number of consecutive failures before circuit opens."""
    return _DEFAULT_CB_THRESHOLD


def get_circuit_breaker_timeout() -> float:
    """Get time in seconds before circuit breaker attempts recovery."""
    return _DEFAULT_CB_TIMEOUT


# Static circuit breaker settings
CIRCUIT_BREAKER_SUCCESS_THRESHOLD: Final[int] = 2


# =============================================================================
# Error Handling
# =============================================================================


def get_max_consecutive_errors() -> int:
    """Get maximum consecutive errors before disconnecting."""
    return _DEFAULT_MAX_CONSECUTIVE_ERRORS


# =============================================================================
# Centrifugo Configuration
# =============================================================================

# Static Centrifugo settings
CENTRIFUGO_MAX_RETRIES: Final[int] = 3
CENTRIFUGO_DEFAULT_CHANNEL_PREFIX: Final[str] = "grpc"


# =============================================================================
# Server Configuration
# =============================================================================

# Static server settings
GRPC_SERVER_MAX_WORKERS: Final[int] = 10
GRPC_HEARTBEAT_INTERVAL: Final[int] = 300


# =============================================================================
# Helper Functions
# =============================================================================


def get_grpc_address(host: str | None = None, port: int | None = None) -> str:
    """
    Get formatted gRPC address string.

    Args:
        host: Host address (defaults to config or localhost)
        port: Port number (defaults to config or 50051)

    Returns:
        Formatted address string like "localhost:50051"
    """
    h = host if host is not None else get_grpc_host()
    p = port if port is not None else get_grpc_port()
    return f"{h}:{p}"


def get_bind_address(host: str | None = None, port: int | None = None) -> str:
    """
    Get formatted bind address for server.

    Args:
        host: Bind host (defaults to GRPC_BIND_HOST_IPV6)
        port: Port number (defaults to config or 50051)

    Returns:
        Formatted bind address like "[::]:50051"
    """
    h = host if host is not None else GRPC_BIND_HOST_IPV6
    p = port if port is not None else get_grpc_port()
    return f"{h}:{p}"


# =============================================================================
# Backward Compatibility Aliases (deprecated, use functions instead)
# =============================================================================

# These are evaluated at import time for backward compat
# New code should use get_* functions instead
GRPC_DEFAULT_HOST: str = _DEFAULT_HOST
GRPC_DEFAULT_PORT: int = _DEFAULT_PORT
GRPC_CHANNEL_READY_TIMEOUT: float = _DEFAULT_CHANNEL_READY_TIMEOUT
GRPC_RPC_CALL_TIMEOUT: float = _DEFAULT_RPC_CALL_TIMEOUT
GRPC_CONNECT_TIMEOUT: float = _DEFAULT_CONNECT_TIMEOUT
GRPC_QUEUE_TIMEOUT: float = _DEFAULT_QUEUE_TIMEOUT
GRPC_ROUTING_TIMEOUT: float = _DEFAULT_ROUTING_TIMEOUT
GRPC_KEEPALIVE_TIME_MS: int = _DEFAULT_KEEPALIVE_TIME_MS
GRPC_KEEPALIVE_TIMEOUT_MS: int = _DEFAULT_KEEPALIVE_TIMEOUT_MS
GRPC_MAX_CONNECTION_IDLE_MS: int = _DEFAULT_MAX_CONNECTION_IDLE_MS
GRPC_KEEPALIVE_PERMIT_WITHOUT_CALLS: bool = True
GRPC_MAX_PINGS_WITHOUT_DATA: int = 0
GRPC_MAX_MESSAGE_LENGTH: int = _DEFAULT_MAX_MESSAGE_LENGTH
GRPC_MAX_SEND_MESSAGE_LENGTH: int = _DEFAULT_MAX_MESSAGE_LENGTH
GRPC_MAX_RECEIVE_MESSAGE_LENGTH: int = _DEFAULT_MAX_MESSAGE_LENGTH
GRPC_MAX_RETRIES: int = _DEFAULT_MAX_RETRIES
GRPC_DEFAULT_QUEUE_SIZE: int = _DEFAULT_QUEUE_SIZE
CIRCUIT_BREAKER_THRESHOLD: int = _DEFAULT_CB_THRESHOLD
CIRCUIT_BREAKER_TIMEOUT: float = _DEFAULT_CB_TIMEOUT
GRPC_MAX_CONSECUTIVE_ERRORS: int = _DEFAULT_MAX_CONSECUTIVE_ERRORS
