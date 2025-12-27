"""
gRPC Configuration Constants.

All default values are centralized here with environment variable support.
Import these constants instead of hardcoding values throughout the codebase.

Usage:
    from django_cfg.apps.integrations.grpc.configs.constants import (
        GRPC_DEFAULT_PORT,
        GRPC_DEFAULT_HOST,
        GRPC_RPC_CALL_TIMEOUT,
    )

Environment Variables:
    GRPC_HOST - Default host for client connections
    GRPC_PORT - Default port for server/client
    GRPC_CHANNEL_READY_TIMEOUT - Channel ready timeout (seconds)
    GRPC_RPC_CALL_TIMEOUT - Default RPC call timeout (seconds)
    GRPC_CONNECT_TIMEOUT - Connection timeout (seconds)
    GRPC_QUEUE_TIMEOUT - Queue operation timeout (seconds)
    GRPC_KEEPALIVE_TIME_MS - Keepalive ping interval (milliseconds)
    GRPC_KEEPALIVE_TIMEOUT_MS - Keepalive ping timeout (milliseconds)
    GRPC_MAX_CONNECTION_IDLE_MS - Max idle connection time (milliseconds)
    GRPC_MAX_MESSAGE_LENGTH - Max message size (bytes)
    GRPC_MAX_RETRIES - Maximum retry attempts
    GRPC_QUEUE_SIZE - Default queue size
    GRPC_CB_THRESHOLD - Circuit breaker failure threshold
    GRPC_CB_TIMEOUT - Circuit breaker recovery timeout (seconds)
    GRPC_MAX_CONSECUTIVE_ERRORS - Max consecutive errors before disconnect
"""

from __future__ import annotations

import os
from typing import Final

# =============================================================================
# Network Defaults
# =============================================================================

GRPC_DEFAULT_HOST: Final[str] = os.getenv("GRPC_HOST", "localhost")
"""Default host for client connections."""

GRPC_DEFAULT_PORT: Final[int] = int(os.getenv("GRPC_PORT", "50051"))
"""Default port for gRPC server and client connections."""

GRPC_BIND_HOST_IPV6: Final[str] = "[::]"
"""IPv6 bind address for server (listens on all interfaces)."""

GRPC_BIND_HOST_IPV4: Final[str] = "0.0.0.0"
"""IPv4 bind address for server (listens on all interfaces)."""

# =============================================================================
# Timeout Defaults (seconds)
# =============================================================================

GRPC_CHANNEL_READY_TIMEOUT: Final[float] = float(
    os.getenv("GRPC_CHANNEL_READY_TIMEOUT", "5.0")
)
"""Timeout for waiting for channel to become ready."""

GRPC_RPC_CALL_TIMEOUT: Final[float] = float(
    os.getenv("GRPC_RPC_CALL_TIMEOUT", "5.0")
)
"""Default timeout for RPC calls."""

GRPC_CONNECT_TIMEOUT: Final[float] = float(
    os.getenv("GRPC_CONNECT_TIMEOUT", "3.0")
)
"""Timeout for establishing connection."""

GRPC_QUEUE_TIMEOUT: Final[float] = float(
    os.getenv("GRPC_QUEUE_TIMEOUT", "10.0")
)
"""Timeout for queue operations (same-process commands)."""

GRPC_ROUTING_TIMEOUT: Final[float] = float(
    os.getenv("GRPC_ROUTING_TIMEOUT", "5.0")
)
"""Timeout for cross-process routing calls."""

# =============================================================================
# Keepalive Defaults (milliseconds)
# =============================================================================

GRPC_KEEPALIVE_TIME_MS: Final[int] = int(
    os.getenv("GRPC_KEEPALIVE_TIME_MS", "30000")
)
"""Keepalive ping interval in milliseconds (default: 30 seconds)."""

GRPC_KEEPALIVE_TIMEOUT_MS: Final[int] = int(
    os.getenv("GRPC_KEEPALIVE_TIMEOUT_MS", "10000")
)
"""Keepalive ping timeout in milliseconds (default: 10 seconds)."""

GRPC_MAX_CONNECTION_IDLE_MS: Final[int] = int(
    os.getenv("GRPC_MAX_CONNECTION_IDLE_MS", "7200000")
)
"""Maximum idle connection time in milliseconds (default: 2 hours)."""

GRPC_KEEPALIVE_PERMIT_WITHOUT_CALLS: Final[bool] = True
"""Allow keepalive pings even without active calls."""

GRPC_MAX_PINGS_WITHOUT_DATA: Final[int] = 2
"""Maximum pings allowed without data before connection is considered dead."""

# =============================================================================
# Message Limits
# =============================================================================

GRPC_MAX_MESSAGE_LENGTH: Final[int] = int(
    os.getenv("GRPC_MAX_MESSAGE_LENGTH", str(4 * 1024 * 1024))
)
"""Maximum message size in bytes (default: 4MB)."""

GRPC_MAX_SEND_MESSAGE_LENGTH: Final[int] = GRPC_MAX_MESSAGE_LENGTH
"""Maximum outbound message size (alias for GRPC_MAX_MESSAGE_LENGTH)."""

GRPC_MAX_RECEIVE_MESSAGE_LENGTH: Final[int] = GRPC_MAX_MESSAGE_LENGTH
"""Maximum inbound message size (alias for GRPC_MAX_MESSAGE_LENGTH)."""

# =============================================================================
# Retry Defaults
# =============================================================================

GRPC_ENABLE_RETRIES: Final[bool] = True
"""Enable automatic retries for failed RPC calls."""

GRPC_MAX_RETRIES: Final[int] = int(os.getenv("GRPC_MAX_RETRIES", "3"))
"""Maximum number of retry attempts."""

GRPC_RETRY_BACKOFF_INITIAL_MS: Final[int] = 100
"""Initial backoff delay for retries in milliseconds."""

GRPC_RETRY_BACKOFF_MAX_MS: Final[int] = 1000
"""Maximum backoff delay for retries in milliseconds."""

GRPC_RETRY_BACKOFF_MULTIPLIER: Final[float] = 2.0
"""Multiplier for exponential backoff."""

# =============================================================================
# Queue Defaults
# =============================================================================

GRPC_DEFAULT_QUEUE_SIZE: Final[int] = int(os.getenv("GRPC_QUEUE_SIZE", "1000"))
"""Default queue size for streaming operations."""

GRPC_MAX_QUEUE_SIZE: Final[int] = 100000
"""Maximum allowed queue size."""

# =============================================================================
# Streaming Defaults
# =============================================================================

GRPC_DEFAULT_PING_INTERVAL: Final[float] = 5.0
"""Default ping interval for streaming connections (seconds)."""

GRPC_DEFAULT_PING_TIMEOUT: Final[float] = 30.0
"""Default ping timeout for streaming connections (seconds)."""

GRPC_MAX_PING_INTERVAL: Final[float] = 300.0
"""Maximum allowed ping interval (seconds)."""

GRPC_MAX_PING_TIMEOUT: Final[float] = 600.0
"""Maximum allowed ping timeout (seconds)."""

# =============================================================================
# Circuit Breaker Defaults
# =============================================================================

CIRCUIT_BREAKER_THRESHOLD: Final[int] = int(os.getenv("GRPC_CB_THRESHOLD", "5"))
"""Number of consecutive failures before circuit opens."""

CIRCUIT_BREAKER_TIMEOUT: Final[float] = float(
    os.getenv("GRPC_CB_TIMEOUT", "60.0")
)
"""Time in seconds before circuit breaker attempts recovery."""

CIRCUIT_BREAKER_SUCCESS_THRESHOLD: Final[int] = 2
"""Number of successful calls needed to close circuit."""

# =============================================================================
# Error Handling
# =============================================================================

GRPC_MAX_CONSECUTIVE_ERRORS: Final[int] = int(
    os.getenv("GRPC_MAX_CONSECUTIVE_ERRORS", "3")
)
"""Maximum consecutive errors before disconnecting."""

# =============================================================================
# Centrifugo Defaults
# =============================================================================

CENTRIFUGO_MAX_RETRIES: Final[int] = 3
"""Maximum retry attempts for Centrifugo publishing."""

CENTRIFUGO_DEFAULT_CHANNEL_PREFIX: Final[str] = "grpc"
"""Default channel prefix for Centrifugo."""

# =============================================================================
# Server Defaults
# =============================================================================

GRPC_SERVER_MAX_WORKERS: Final[int] = 10
"""Default maximum worker threads (for sync server)."""

GRPC_HEARTBEAT_INTERVAL: Final[int] = 300
"""Default heartbeat interval in seconds (5 minutes)."""

# =============================================================================
# Helper Functions
# =============================================================================


def get_grpc_address(host: str | None = None, port: int | None = None) -> str:
    """
    Get formatted gRPC address string.

    Args:
        host: Host address (defaults to GRPC_DEFAULT_HOST)
        port: Port number (defaults to GRPC_DEFAULT_PORT)

    Returns:
        Formatted address string like "localhost:50051"
    """
    h = host if host is not None else GRPC_DEFAULT_HOST
    p = port if port is not None else GRPC_DEFAULT_PORT
    return f"{h}:{p}"


def get_bind_address(host: str | None = None, port: int | None = None) -> str:
    """
    Get formatted bind address for server.

    Args:
        host: Bind host (defaults to GRPC_BIND_HOST_IPV6)
        port: Port number (defaults to GRPC_DEFAULT_PORT)

    Returns:
        Formatted bind address like "[::]:50051"
    """
    h = host if host is not None else GRPC_BIND_HOST_IPV6
    p = port if port is not None else GRPC_DEFAULT_PORT
    return f"{h}:{p}"
