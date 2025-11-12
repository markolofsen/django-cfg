"""
Universal Streaming Command Client - Base Implementation

This module provides a generic, reusable command client for bidirectional gRPC streaming services.

Key Features:
- Dual-mode: Same-process (direct queue) or Cross-process (gRPC RPC)
- Type-safe: Generic[TCommand] for different protobuf types
- Auto-detection: Automatically chooses the right mode
- Minimal coupling: Works with any BidirectionalStreamingService

Usage:
    from your_app.grpc.commands.base import StreamingCommandClient
    from your_app.grpc import your_service_pb2 as pb2

    class YourCommandClient(StreamingCommandClient[pb2.Command]):
        pass

Documentation: See @commands/README.md for complete guide
"""

import asyncio
import logging
from abc import ABC
from dataclasses import dataclass
from typing import Generic, Optional, TypeVar, Any

try:
    import grpc
    GRPC_AVAILABLE = True
except ImportError:
    GRPC_AVAILABLE = False

logger = logging.getLogger(__name__)

# Generic type for protobuf command messages
TCommand = TypeVar('TCommand')


@dataclass
class CommandClientConfig:
    """Configuration for command client behavior."""

    # Queue timeout for same-process mode (seconds)
    queue_timeout: float = 5.0

    # gRPC connection timeout for cross-process mode (seconds)
    connect_timeout: float = 3.0

    # gRPC call timeout (seconds)
    call_timeout: float = 5.0

    # Default gRPC server address
    grpc_host: str = "localhost"

    # Default gRPC server port (can be overridden)
    grpc_port: Optional[int] = None


class StreamingCommandClient(Generic[TCommand], ABC):
    """
    Universal command client for bidirectional streaming services.

    Supports two modes:
    1. Same-process: Direct queue access when streaming_service is provided
    2. Cross-process: gRPC RPC call when streaming_service is None

    Type Parameters:
        TCommand: The protobuf message type for commands

    Example:
        # Same-process mode
        from your_app.grpc.services.registry import get_streaming_service

        service = get_streaming_service("your_service")
        client = YourCommandClient(
            client_id="client-123",
            streaming_service=service
        )

        # Cross-process mode
        client = YourCommandClient(
            client_id="client-123",
            grpc_port=50051
        )
    """

    def __init__(
        self,
        client_id: str,
        streaming_service: Optional[Any] = None,
        config: Optional[CommandClientConfig] = None,
        grpc_port: Optional[int] = None,
        grpc_host: Optional[str] = None,
    ):
        """
        Initialize command client.

        Args:
            client_id: Unique identifier for the client
            streaming_service: BidirectionalStreamingService instance for same-process mode
            config: Configuration object (uses defaults if not provided)
            grpc_port: Override gRPC port for cross-process mode
            grpc_host: Override gRPC host for cross-process mode
        """
        self.client_id = client_id
        self._streaming_service = streaming_service
        self.config = config or CommandClientConfig()

        # Override config with provided values
        if grpc_port is not None:
            self.config.grpc_port = grpc_port
        if grpc_host is not None:
            self.config.grpc_host = grpc_host

        # Determine mode
        self._is_same_process = streaming_service is not None

        logger.debug(
            f"Initialized {self.__class__.__name__} for client_id={client_id}, "
            f"mode={'same-process' if self._is_same_process else 'cross-process'}"
        )

    async def _send_command(self, command: TCommand) -> bool:
        """
        Send command to client (auto-detects mode).

        Args:
            command: Protobuf command message

        Returns:
            True if command was sent successfully, False otherwise

        Raises:
            RuntimeError: If gRPC is not available in cross-process mode
        """
        if self._is_same_process:
            return await self._send_direct(command)
        else:
            return await self._send_via_grpc(command)

    async def _send_direct(self, command: TCommand) -> bool:
        """
        Send command directly via queue (same-process mode).

        Args:
            command: Protobuf command message

        Returns:
            True if command was queued, False if client not connected
        """
        try:
            success = await self._streaming_service.send_to_client(
                client_id=self.client_id,
                command=command,
                timeout=self.config.queue_timeout
            )

            if success:
                logger.debug(f"Command sent to {self.client_id} (same-process)")
            else:
                logger.warning(f"Client {self.client_id} not connected")

            return success

        except asyncio.TimeoutError:
            logger.error(
                f"Timeout sending command to {self.client_id} "
                f"(timeout={self.config.queue_timeout}s)"
            )
            return False
        except Exception as e:
            logger.error(
                f"Error sending command to {self.client_id}: {e}",
                exc_info=True
            )
            return False

    async def _send_via_grpc(self, command: TCommand) -> bool:
        """
        Send command via gRPC RPC (cross-process mode).

        This method should be overridden in subclasses to implement
        the actual gRPC call with service-specific stub and request.

        Args:
            command: Protobuf command message

        Returns:
            True if RPC succeeded, False otherwise

        Raises:
            NotImplementedError: Must be implemented in subclass
            RuntimeError: If gRPC is not available
        """
        raise NotImplementedError(
            f"{self.__class__.__name__} must implement _send_via_grpc() "
            "for cross-process communication. See EXAMPLES.md for reference."
        )

    def is_same_process(self) -> bool:
        """Check if running in same-process mode."""
        return self._is_same_process

    def get_grpc_address(self) -> str:
        """
        Get gRPC server address for cross-process mode.

        Priority order:
        1. self.config.grpc_host/grpc_port (if set via __init__)
        2. DjangoConfig.grpc.server.host/port (auto-detection)
        3. Environment variables GRPC_HOST/GRPC_PORT
        4. Defaults: localhost:50051

        Returns:
            Address string like "localhost:50051" or "grpc.example.com:50051"
        """
        import os

        # Auto-detect from django-cfg config if not explicitly set
        if self.config.grpc_port is None or self.config.grpc_host == "localhost":
            try:
                from django_cfg.core.config import get_current_config
                config = get_current_config()

                if config and hasattr(config, 'grpc') and config.grpc:
                    # Get from config.grpc.server if available
                    if hasattr(config.grpc, 'server') and config.grpc.server:
                        server_cfg = config.grpc.server

                        # Auto-detect port
                        if self.config.grpc_port is None and hasattr(server_cfg, 'port'):
                            self.config.grpc_port = server_cfg.port
                            logger.debug(f"Auto-detected gRPC port from config: {self.config.grpc_port}")

                        # Auto-detect host (if still default "localhost")
                        if self.config.grpc_host == "localhost" and hasattr(server_cfg, 'host'):
                            # Convert [::] (IPv6) to localhost for client connections
                            host = server_cfg.host
                            if host in ("[:]", "[::]", "0.0.0.0"):
                                host = "localhost"
                            self.config.grpc_host = host
                            logger.debug(f"Auto-detected gRPC host from config: {self.config.grpc_host}")

                    # Fallback to config.grpc.port (legacy format)
                    elif self.config.grpc_port is None and hasattr(config.grpc, 'port'):
                        self.config.grpc_port = config.grpc.port
                        logger.debug(f"Auto-detected gRPC port from config.grpc.port: {self.config.grpc_port}")

            except Exception as e:
                logger.debug(f"Auto-detection from config failed: {e}")

        # Fallback to environment variables
        if self.config.grpc_host == "localhost":
            env_host = os.getenv('GRPC_HOST')
            if env_host:
                self.config.grpc_host = env_host
                logger.debug(f"Using GRPC_HOST from environment: {self.config.grpc_host}")

        if self.config.grpc_port is None:
            env_port = os.getenv('GRPC_PORT')
            if env_port:
                try:
                    self.config.grpc_port = int(env_port)
                    logger.debug(f"Using GRPC_PORT from environment: {self.config.grpc_port}")
                except ValueError:
                    logger.warning(f"Invalid GRPC_PORT environment variable: {env_port}")

        # Final fallback to default port
        if self.config.grpc_port is None:
            self.config.grpc_port = 50051
            logger.debug(f"Using default gRPC port: {self.config.grpc_port}")

        return f"{self.config.grpc_host}:{self.config.grpc_port}"


class CommandError(Exception):
    """Base exception for command-related errors."""
    pass


class CommandTimeoutError(CommandError):
    """Raised when command send times out."""
    pass


class ClientNotConnectedError(CommandError):
    """Raised when client is not connected."""
    pass


__all__ = [
    'StreamingCommandClient',
    'CommandClientConfig',
    'CommandError',
    'CommandTimeoutError',
    'ClientNotConnectedError',
    'TCommand',
]
