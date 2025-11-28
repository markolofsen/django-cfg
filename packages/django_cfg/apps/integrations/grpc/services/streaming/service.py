"""
Universal bidirectional streaming service for gRPC.
"""

from typing import Generic, Optional, AsyncIterator, Dict
import asyncio
import logging
import traceback

import grpc

from .types import (
    TMessage,
    TCommand,
    MessageProcessor,
    ClientIdExtractor,
    PingMessageCreator,
    CommandAckExtractor,
    HeartbeatExtractor,
    HeartbeatCallback,
    ConnectionCallback,
    ErrorHandler,
)
from .config import BidirectionalStreamingConfig
from .core.connection import ConnectionManager
from .core.registry import ResponseRegistry
from .core.queue import QueueManager
from .processors.input import InputProcessor
from .processors.output import OutputProcessor
from .integrations.centrifugo import CentrifugoPublisher

# Import setup_streaming_logger for auto-created logger
from django_cfg.apps.integrations.grpc.utils.streaming_logger import setup_streaming_logger

# Import Centrifugo publisher (always available in django-cfg)
from django_cfg.apps.integrations.centrifugo.services import get_centrifugo_publisher

# Import Circuit Breaker for resilience
from .integrations.circuit_breaker import CentrifugoCircuitBreaker


class BidirectionalStreamingService(Generic[TMessage, TCommand]):
    """
    Universal bidirectional streaming service with decomposed architecture.

    This service orchestrates all components to provide bidirectional gRPC streaming.

    Type Parameters:
        TMessage: Type of incoming messages from client
        TCommand: Type of outgoing commands to client

    Architecture:
    ```
    BidirectionalStreamingService
    ConnectionManager    - Track active connections
    ResponseRegistry     - Future-based command responses
    InputProcessor       - Process incoming messages
    OutputProcessor      - Process outgoing commands
    CentrifugoPublisher  - Auto-publish to Centrifugo
    ```

    Parameters:
        config: Pydantic configuration model
        message_processor: Callback to process each incoming message
        client_id_extractor: Callback to extract client ID from message
        ping_message_creator: Callback to create ping messages
        on_connect: Optional callback when client connects
        on_disconnect: Optional callback when client disconnects
        on_error: Optional callback on errors
        logger: Optional logger instance (auto-created if None)
    """

    def __init__(
        self,
        config: BidirectionalStreamingConfig,
        message_processor: MessageProcessor[TMessage, TCommand],
        client_id_extractor: ClientIdExtractor[TMessage],
        ping_message_creator: PingMessageCreator[TCommand],
        command_ack_extractor: Optional[CommandAckExtractor[TMessage]] = None,
        heartbeat_extractor: Optional[HeartbeatExtractor[TMessage]] = None,
        heartbeat_callback: Optional[HeartbeatCallback] = None,
        on_connect: Optional[ConnectionCallback] = None,
        on_disconnect: Optional[ConnectionCallback] = None,
        on_error: Optional[ErrorHandler] = None,
        logger: Optional[logging.Logger] = None,
    ):
        """Initialize bidirectional streaming service."""
        self.config = config
        self.message_processor = message_processor
        self.client_id_extractor = client_id_extractor
        self.ping_message_creator = ping_message_creator
        self.command_ack_extractor = command_ack_extractor
        self.heartbeat_extractor = heartbeat_extractor
        self.heartbeat_callback = heartbeat_callback
        self.on_connect = on_connect
        self.on_disconnect = on_disconnect
        self.on_error = on_error

        # Auto-create logger if not provided
        if logger is None:
            logger_name = self.config.logger_name or "grpc_streaming"
            self.logger = setup_streaming_logger(
                name=logger_name,
                level=logging.DEBUG,
                console_level=logging.INFO
            )
        else:
            self.logger = logger

        # Core components
        self.connection_manager = ConnectionManager()
        self.response_registry = ResponseRegistry()
        self.queue_manager = QueueManager[TCommand]()

        # Centrifugo publisher (initialized lazily if needed)
        centrifugo_publisher = None
        if self.config.enable_centrifugo:
            try:
                centrifugo_client = get_centrifugo_publisher()

                centrifugo_publisher = CentrifugoPublisher(
                    centrifugo_publisher=centrifugo_client,
                    channel_prefix=self.config.centrifugo_channel_prefix,
                    circuit_breaker_enabled=self.config.centrifugo_circuit_breaker_enabled,
                    circuit_breaker_threshold=self.config.centrifugo_circuit_breaker_threshold,
                    circuit_breaker_timeout=self.config.centrifugo_circuit_breaker_timeout,
                    enable_logging=self.config.enable_logging,
                )

                if self.config.enable_logging:
                    cb_status = "with circuit breaker" if self.config.centrifugo_circuit_breaker_enabled else "without circuit breaker"
                    self.logger.info(f" Centrifugo auto-publishing enabled ({cb_status})")
            except Exception as e:
                if self.config.enable_logging:
                    self.logger.warning(f"�  Failed to initialize Centrifugo publisher: {e}")

        # Processors
        self.input_processor = InputProcessor(
            extract_client_id=client_id_extractor,
            process_message=message_processor,
            centrifugo_publisher=centrifugo_publisher if self.config.centrifugo_auto_publish_messages else None,
            command_ack_extractor=command_ack_extractor,  # Universal CommandAck handling
            heartbeat_extractor=heartbeat_extractor,      # Universal Heartbeat handling
            heartbeat_callback=heartbeat_callback,
            streaming_mode=self.config.streaming_mode,
            connection_timeout=self.config.connection_timeout,
            yield_event_loop=self.config.should_yield_event_loop(),
            enable_logging=self.config.enable_logging,
        )

        self.output_processor = OutputProcessor(
            ping_message_creator=ping_message_creator,
            centrifugo_publisher=centrifugo_publisher if self.config.centrifugo_auto_publish_commands else None,
            ping_strategy=self.config.ping_strategy,
            ping_interval=self.config.ping_interval,
            max_consecutive_errors=self.config.max_consecutive_errors,
            enable_logging=self.config.enable_logging,
        )

        if self.config.enable_logging:
            self.logger.info(
                f"BidirectionalStreamingService initialized: "
                f"mode={self.config.streaming_mode.value}, "
                f"ping={self.config.ping_strategy.value}, "
                f"interval={self.config.ping_interval}s"
            )

    # ------------------------------------------------------------------------
    # Main Stream Handler
    # ------------------------------------------------------------------------

    async def handle_stream(
        self,
        request_iterator: AsyncIterator[TMessage],
        context: grpc.aio.ServicerContext,
    ) -> AsyncIterator[TCommand]:
        """
        Handle bidirectional gRPC stream.

        This is the main entry point called by gRPC servicer methods.

        Flow:
        1. Create output queue for this connection
        2. Start input task to process messages concurrently
        3. Yield commands from output queue (with ping on timeout)
        4. Handle cancellation and cleanup

        Args:
            request_iterator: Incoming message stream from client
            context: gRPC service context

        Yields:
            Commands to send back to client

        Raises:
            asyncio.CancelledError: On client disconnect
            grpc.RpcError: On gRPC errors
        """
        client_id: Optional[str] = None
        output_queue: Optional[asyncio.Queue[TCommand]] = None
        input_task: Optional[asyncio.Task] = None

        try:
            # Create output queue for this connection
            output_queue = self.queue_manager.create_queue(maxsize=self.config.max_queue_size)

            # Start background task to process incoming messages
            input_task = asyncio.create_task(
                self._process_input_stream(
                    request_iterator,
                    output_queue,
                    context,
                )
            )

            # Main output loop: yield commands from queue
            async for command in self.output_processor.process_queue(
                output_queue=output_queue,
                context=context,
                client_id=self._get_latest_client_id()  # Will be set by input task
            ):
                yield command

            # Output loop finished, wait for input task
            if self.config.enable_logging:
                self.logger.info("Output loop finished, waiting for input task...")

            try:
                await input_task
                if self.config.enable_logging:
                    self.logger.info("Input task completed successfully")
            except Exception as e:
                if self.config.enable_logging:
                    self.logger.error(
                        f"❌ [STREAMING_SERVICE] Input task error:\n"
                        f"   Error: {type(e).__name__}: {e}\n"
                        f"   Traceback:\n{traceback.format_exc()}"
                    )
                if self.on_error and client_id:
                    await self.on_error(client_id, e)

        except asyncio.CancelledError:
            if self.config.enable_logging:
                self.logger.info(f"Client {client_id} stream cancelled")

            # Cancel input task if still running
            if input_task and not input_task.done():
                input_task.cancel()
                try:
                    await input_task
                except asyncio.CancelledError:
                    pass

            raise

        except Exception as e:
            if self.config.enable_logging:
                self.logger.error(
                    f"❌ [STREAMING_SERVICE] Client {client_id} stream error:\n"
                    f"   Error: {type(e).__name__}: {e}\n"
                    f"   Traceback:\n{traceback.format_exc()}"
                )

            if self.on_error and client_id:
                await self.on_error(client_id, e)

            await context.abort(grpc.StatusCode.INTERNAL, f"Server error: {e}")

        finally:
            # Cleanup connection
            if client_id:
                self.connection_manager.unregister(client_id)

                if self.config.enable_logging:
                    self.logger.info(f"Client {client_id[:8]}... disconnected")

                if self.on_disconnect:
                    await self.on_disconnect(client_id)

    # ------------------------------------------------------------------------
    # Input Processing (Delegation to InputProcessor)
    # ------------------------------------------------------------------------

    async def _process_input_stream(
        self,
        request_iterator: AsyncIterator[TMessage],
        output_queue: asyncio.Queue[TCommand],
        context: grpc.aio.ServicerContext,
    ) -> None:
        """Process incoming messages from client (delegates to InputProcessor)."""
        client_id = await self.input_processor.process_stream(
            request_iterator=request_iterator,
            output_queue=output_queue,
            context=context,
            streaming_service=self,
            on_connect=self._on_connect_internal
        )

    async def _on_connect_internal(self, client_id: str) -> None:
        """Internal on_connect handler that registers connection."""
        # This will be called by InputProcessor when client_id is extracted
        # We need to get the output_queue somehow - let's pass it via context
        # For now, we'll use a simpler approach: track connections in input processor
        if self.on_connect:
            await self.on_connect(client_id)

    def _get_latest_client_id(self) -> Optional[str]:
        """Get latest connected client ID."""
        client_ids = self.connection_manager.get_client_ids()
        return client_ids[-1] if client_ids else None

    # ------------------------------------------------------------------------
    # Connection Management API
    # ------------------------------------------------------------------------

    def get_active_connections(self) -> Dict[str, asyncio.Queue[TCommand]]:
        """
        Get all active connections.

        Returns:
            Dict mapping client_id to output_queue
        """
        return {
            client_id: conn.output_queue
            for client_id, conn in self.connection_manager.get_all().items()
        }

    def is_client_connected(self, client_id: str) -> bool:
        """
        Check if client is currently connected.

        Args:
            client_id: Client identifier

        Returns:
            True if client has active connection
        """
        return self.connection_manager.is_connected(client_id)

    async def send_to_client(
        self,
        client_id: str,
        command: TCommand,
        timeout: Optional[float] = None,
    ) -> bool:
        """
        Send command to specific client.

        Args:
            client_id: Target client identifier
            command: Command to send
            timeout: Optional timeout for enqueue (uses config.queue_timeout if None)

        Returns:
            True if sent successfully, False if client not connected or timeout

        Raises:
            asyncio.TimeoutError: If enqueue times out
        """
        conn = self.connection_manager.get(client_id)
        if not conn:
            if self.config.enable_logging:
                self.logger.warning(f"Client {client_id} not connected")
            return False

        timeout = timeout or self.config.queue_timeout

        try:
            await self.queue_manager.put_with_timeout(
                conn.output_queue,
                command,
                timeout=timeout
            )
            return True
        except asyncio.TimeoutError:
            if self.config.enable_logging:
                self.logger.warning(f"Timeout sending to client {client_id}")
            return False
        except Exception as e:
            if self.config.enable_logging:
                self.logger.error(f"Error sending to client {client_id}: {e}")
            return False

    async def broadcast_to_all(
        self,
        command: TCommand,
        exclude: Optional[list[str]] = None,
    ) -> int:
        """
        Broadcast command to all connected clients.

        Args:
            command: Command to broadcast
            exclude: Optional list of client IDs to exclude

        Returns:
            Number of clients successfully sent to
        """
        exclude = exclude or []
        sent_count = 0

        for client_id in self.connection_manager.get_client_ids():
            if client_id not in exclude:
                if await self.send_to_client(client_id, command):
                    sent_count += 1

        return sent_count

    async def disconnect_client(self, client_id: str) -> None:
        """
        Gracefully disconnect a client.

        Sends shutdown sentinel (None) to trigger clean disconnection.

        Args:
            client_id: Client to disconnect
        """
        conn = self.connection_manager.get(client_id)
        if conn:
            await conn.output_queue.put(None)  # Sentinel for shutdown

    # ------------------------------------------------------------------------
    # Response Registry API (for synchronous command execution)
    # ------------------------------------------------------------------------

    async def execute_command_sync(
        self,
        client_id: str,
        command: TCommand,
        timeout: float = 30.0
    ) -> TMessage:
        """
        Execute command synchronously and wait for response.

        Requires the command to have a command_id field and the client
        to send back a CommandAck message with the same command_id.

        Args:
            client_id: Target client
            command: Command to execute
            timeout: Timeout in seconds

        Returns:
            Response message (CommandAck)

        Raises:
            asyncio.TimeoutError: If no response within timeout
            ValueError: If client not connected
        """
        # Extract command_id from command (protobuf-specific)
        if not hasattr(command, 'command_id'):
            raise ValueError("Command must have command_id field for synchronous execution")

        command_id = command.command_id

        # Register command for response
        future = await self.response_registry.register_command(command_id, timeout)

        # Send command to client
        if not await self.send_to_client(client_id, command, timeout=timeout):
            await self.response_registry.cancel_command(command_id, "Failed to send command")
            raise ValueError(f"Failed to send command to client {client_id}")

        # Wait for response
        return await future


# ============================================================================
# Exports
# ============================================================================

__all__ = [
    'BidirectionalStreamingService',
]
