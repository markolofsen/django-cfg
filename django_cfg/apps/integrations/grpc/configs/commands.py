"""
Command Client Configuration.

This module provides configuration for the command execution client,
which handles both same-process (queue-based) and cross-process (gRPC RPC)
command execution.

Usage:
    from django_cfg.apps.integrations.grpc.configs.commands import CommandClientConfig

    config = CommandClientConfig(
        queue_timeout=10.0,
        call_timeout=30.0,
    )
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from .constants import (
    GRPC_CONNECT_TIMEOUT,
    GRPC_DEFAULT_HOST,
    GRPC_DEFAULT_PORT,
    GRPC_QUEUE_TIMEOUT,
    GRPC_RPC_CALL_TIMEOUT,
)


@dataclass
class CommandClientConfig:
    """
    Configuration for command client execution.

    The command client supports two execution modes:
    1. Same-process mode: Uses an async queue for communication
    2. Cross-process mode: Uses gRPC RPC for remote execution

    Attributes:
        queue_timeout: Timeout for same-process queue operations (seconds)
        connect_timeout: Timeout for establishing gRPC connection (seconds)
        call_timeout: Timeout for gRPC RPC calls (seconds)
        grpc_host: gRPC server host for cross-process mode
        grpc_port: gRPC server port for cross-process mode

    Example:
        # Default configuration
        config = CommandClientConfig()

        # Custom timeouts
        config = CommandClientConfig(
            queue_timeout=10.0,
            call_timeout=30.0,
        )

        # Custom gRPC endpoint
        config = CommandClientConfig(
            grpc_host="grpc-server.internal",
            grpc_port=50052,
        )
    """

    queue_timeout: float = field(default=GRPC_QUEUE_TIMEOUT)
    """Timeout for same-process queue operations in seconds."""

    connect_timeout: float = field(default=GRPC_CONNECT_TIMEOUT)
    """Timeout for establishing gRPC connection in seconds."""

    call_timeout: float = field(default=GRPC_RPC_CALL_TIMEOUT)
    """Timeout for gRPC RPC calls in seconds."""

    grpc_host: str = field(default=GRPC_DEFAULT_HOST)
    """gRPC server host for cross-process mode."""

    grpc_port: Optional[int] = field(default=None)
    """gRPC server port for cross-process mode (None = auto-detect)."""

    def __post_init__(self):
        """Set default port if not provided."""
        if self.grpc_port is None:
            self.grpc_port = GRPC_DEFAULT_PORT

    @property
    def grpc_address(self) -> str:
        """Get formatted gRPC address."""
        return f"{self.grpc_host}:{self.grpc_port}"

    def with_overrides(
        self,
        queue_timeout: Optional[float] = None,
        connect_timeout: Optional[float] = None,
        call_timeout: Optional[float] = None,
        grpc_host: Optional[str] = None,
        grpc_port: Optional[int] = None,
    ) -> "CommandClientConfig":
        """
        Create a new config with specified overrides.

        Args:
            queue_timeout: Override queue timeout
            connect_timeout: Override connect timeout
            call_timeout: Override call timeout
            grpc_host: Override gRPC host
            grpc_port: Override gRPC port

        Returns:
            New CommandClientConfig with overrides applied

        Example:
            base_config = CommandClientConfig()
            custom = base_config.with_overrides(call_timeout=60.0)
        """
        return CommandClientConfig(
            queue_timeout=queue_timeout if queue_timeout is not None else self.queue_timeout,
            connect_timeout=connect_timeout if connect_timeout is not None else self.connect_timeout,
            call_timeout=call_timeout if call_timeout is not None else self.call_timeout,
            grpc_host=grpc_host if grpc_host is not None else self.grpc_host,
            grpc_port=grpc_port if grpc_port is not None else self.grpc_port,
        )


# Backward-compatible alias
# Note: This class was originally in services/commands/base.py
# It has been moved here for centralization. The old location
# will re-export this with a deprecation warning.
