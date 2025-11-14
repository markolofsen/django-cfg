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

from ..streaming.core.registry import ResponseRegistry

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

    Class Attributes (for cross-process mode):
        stub_class: gRPC stub class (e.g., YourServiceStub)
        request_class: Request message class (e.g., SendCommandRequest)
        rpc_method_name: RPC method name (e.g., "SendCommandToClient")
        client_id_field: Field name for client_id in request (default: "client_id")
        command_field: Field name for command in request (default: "command")

    Example:
        # Same-process mode
        from your_app.grpc.services.registry import get_streaming_service

        service = get_streaming_service("your_service")
        client = YourCommandClient(
            client_id="client-123",
            streaming_service=service
        )

        # Cross-process mode (with class attributes)
        class YourCommandClient(StreamingCommandClient[pb2.Command]):
            stub_class = pb2_grpc.YourServiceStub
            request_class = pb2.SendCommandRequest
            rpc_method_name = "SendCommandToClient"

        client = YourCommandClient(
            client_id="client-123",
            grpc_port=50051
        )
    """

    # Class attributes for default gRPC implementation
    stub_class: Optional[type] = None
    request_class: Optional[type] = None
    rpc_method_name: Optional[str] = None
    client_id_field: str = "client_id"
    command_field: str = "command"

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

        # Response registry for synchronous command execution (RPC-style)
        # Use service's registry in same-process mode, create own in cross-process
        if self._is_same_process and hasattr(streaming_service, 'response_registry'):
            self._response_registry = streaming_service.response_registry
            logger.info(
                f"✅ Client {client_id[:8]}... using SERVICE registry: {id(self._response_registry)} "
                f"(streaming_service={id(streaming_service)})"
            )
        else:
            # Cross-process mode: sync execution not typically needed (use RPC)
            # But create registry anyway for consistency
            self._response_registry = ResponseRegistry()
            logger.warning(
                f"⚠️  Client {client_id[:8]}... created NEW registry: {id(self._response_registry)} "
                f"(same_process={self._is_same_process}, "
                f"streaming_service={streaming_service}, "
                f"has_registry={hasattr(streaming_service, 'response_registry') if streaming_service else 'N/A'})"
            )

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

        Default implementation uses class attributes (stub_class, request_class, rpc_method_name).
        Subclasses can either:
        1. Set class attributes (recommended for standard patterns)
        2. Override this method (for custom logic)

        Args:
            command: Protobuf command message

        Returns:
            True if RPC succeeded, False otherwise

        Raises:
            NotImplementedError: If class attributes not set and not overridden
            RuntimeError: If gRPC is not available
        """
        # Check if class attributes are defined
        if not all([self.stub_class, self.request_class, self.rpc_method_name]):
            raise NotImplementedError(
                f"{self.__class__.__name__} must either:\n"
                f"1. Set class attributes: stub_class, request_class, rpc_method_name\n"
                f"2. Override _send_via_grpc() method\n"
                f"See EXAMPLES.md for reference."
            )

        if not GRPC_AVAILABLE:
            raise RuntimeError("grpcio not installed. Install with: pip install grpcio")

        try:
            # Create gRPC channel with standard options
            async with grpc.aio.insecure_channel(
                self.get_grpc_address(),
                options=[
                    ('grpc.keepalive_time_ms', 10000),
                    ('grpc.keepalive_timeout_ms', 5000),
                    ('grpc.max_receive_message_length', 100 * 1024 * 1024),  # 100MB
                ]
            ) as channel:
                # Create stub instance
                stub = self.stub_class(channel)

                # Build request message dynamically
                request_kwargs = {
                    self.client_id_field: self.client_id,
                    self.command_field: command,
                }
                request = self.request_class(**request_kwargs)

                # Call RPC method by name
                rpc_method = getattr(stub, self.rpc_method_name)
                response = await rpc_method(request, timeout=self.config.call_timeout)

                # Assume response has 'success' field
                if hasattr(response, 'success'):
                    success = response.success
                    if success:
                        logger.debug(f"Command sent to {self.client_id} via gRPC")
                    else:
                        message = getattr(response, 'message', 'Unknown error')
                        logger.warning(f"Command failed for {self.client_id}: {message}")
                    return success
                else:
                    # If no success field, assume success
                    logger.debug(f"Command sent to {self.client_id} via gRPC")
                    return True

        except grpc.RpcError as e:
            logger.error(
                f"gRPC error sending command to {self.client_id}: "
                f"{e.code()} - {e.details()}",
                exc_info=True
            )
            return False
        except Exception as e:
            logger.error(
                f"Error sending command to {self.client_id}: {e}",
                exc_info=True
            )
            return False

    async def send_command_and_wait(
        self,
        command: TCommand,
        timeout: float = 5.0,
        command_id_field: str = "command_id"
    ):
        """
        Send command and wait for response synchronously (RPC-style).

        This method provides RPC-style synchronous command execution:
        1. Register future in response_registry with command_id
        2. Send command to client via streaming connection
        3. Wait for response with timeout
        4. Return response to caller

        Args:
            command: Protobuf command message
            timeout: Timeout in seconds to wait for response (default: 5.0)
            command_id_field: Field name for command ID in protobuf (default: "command_id")

        Returns:
            Response protobuf with execution result

        Raises:
            CommandError: If command doesn't have command_id field or it's empty
            ClientNotConnectedError: If client is not connected
            CommandTimeoutError: If response not received within timeout

        Example:
            >>> from django_cfg.apps.integrations.grpc.services.commands.helpers import CommandBuilder
            >>>
            >>> client = YourCommandClient(client_id, streaming_service=service)
            >>> command = CommandBuilder.create(pb2.Command, YourConverter)
            >>> command.start.CopyFrom(pb2.StartCommand())
            >>>
            >>> response = await client.send_command_and_wait(command, timeout=10.0)
            >>> print(f"Response: {response}")
        """
        # Extract command_id from command
        if not hasattr(command, command_id_field):
            raise CommandError(
                f"Command must have '{command_id_field}' field. "
                f"Use CommandBuilder.create() or set command_id_field parameter."
            )

        command_id = getattr(command, command_id_field)
        if not command_id:
            raise CommandError(
                f"Command {command_id_field} must be set (use CommandBuilder.create)"
            )

        # Register future in response registry
        future = await self._response_registry.register_command(command_id, timeout=timeout)

        try:
            # Send command to client
            success = await self._send_command(command)

            if not success:
                # Cancel future and cleanup
                await self._response_registry.cancel_command(command_id, "Client not connected")
                raise ClientNotConnectedError(f"Client {self.client_id} not connected")

            logger.info(f"⏳ Waiting for response to command {command_id} (timeout: {timeout}s)")

            # Wait for response
            try:
                response = await asyncio.wait_for(future, timeout=timeout)
                logger.info(f"✅ Received response to command {command_id}")
                return response

            except asyncio.TimeoutError:
                # Cleanup expired command
                await self._response_registry.cancel_command(command_id, "Timeout")
                raise CommandTimeoutError(
                    f"Command {command_id} timeout after {timeout}s (client: {self.client_id})"
                )

        except (ClientNotConnectedError, CommandTimeoutError):
            # Re-raise expected exceptions
            raise

        except Exception as e:
            # Unexpected error - cleanup and wrap
            await self._response_registry.cancel_command(command_id, f"Error: {e}")
            raise CommandError(f"Failed to send command {command_id}: {e}") from e

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
