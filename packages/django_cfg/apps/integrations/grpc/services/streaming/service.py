"""
Universal bidirectional streaming service for gRPC.

This module provides a generic, type-safe implementation of bidirectional gRPC streaming.
It extracts the common pattern used across signals and trading_bots services.

**Key Features**:
- Generic over TMessage (input) and TCommand (output) types
- Type-safe callbacks via Protocol types
- Pydantic v2 configuration with validation
- Automatic ping/keepalive handling
- Proper concurrent input/output processing
- Critical `await asyncio.sleep(0)` for event loop yielding
- Connection lifecycle management

**Usage Example**:
```python
from .types import MessageProcessor, ClientIdExtractor, PingMessageCreator
from .config import BidirectionalStreamingConfig, ConfigPresets

# Define your callbacks
async def process_messages(
    client_id: str,
    message: SignalCommand,
    output_queue: asyncio.Queue[SignalMessage]
) -> None:
    # Your business logic
    response = await handle_signal(message)
    await output_queue.put(response)

def extract_client_id(message: SignalCommand) -> str:
    return message.client_id

def create_ping() -> SignalMessage:
    return SignalMessage(is_ping=True)

# Create service instance
service = BidirectionalStreamingService(
    config=ConfigPresets.PRODUCTION,
    message_processor=process_messages,
    client_id_extractor=extract_client_id,
    ping_message_creator=create_ping,
)

# Use in gRPC servicer
async def BidirectionalStream(self, request_iterator, context):
    async for response in service.handle_stream(request_iterator, context):
        yield response
```

Created: 2025-11-07
Status: %%PRODUCTION%%
Phase: Phase 1 - Universal Components
"""

from typing import Generic, Optional, AsyncIterator, Dict
import asyncio
import logging
import time

import grpc

from .types import (
    TMessage,
    TCommand,
    MessageProcessor,
    ClientIdExtractor,
    PingMessageCreator,
    ConnectionCallback,
    ErrorHandler,
)
from .config import BidirectionalStreamingConfig, StreamingMode, PingStrategy

# Import setup_streaming_logger for auto-created logger
from django_cfg.apps.integrations.grpc.utils.streaming_logger import setup_streaming_logger


# Module-level logger (fallback only)
logger = logging.getLogger(__name__)


# ============================================================================
# Main Service Class
# ============================================================================

class BidirectionalStreamingService(Generic[TMessage, TCommand]):
    """
    Universal bidirectional streaming service with type-safe callbacks.

    This service handles the complex concurrent streaming pattern used in
    signals and trading_bots services, making it reusable across projects.

    **Type Parameters**:
        TMessage: Type of incoming messages from client
        TCommand: Type of outgoing commands to client

    **Architecture**:
    ```
    ┌─────────────────────────────────────────────────────────────┐
    │  BidirectionalStreamingService                               │
    │                                                              │
    │  ┌─────────────────┐        ┌──────────────────┐           │
    │  │  Input Task     │───────>│  output_queue    │           │
    │  │  (processes     │        │  (asyncio.Queue) │           │
    │  │   messages)     │        └──────────────────┘           │
    │  └─────────────────┘                │                       │
    │          │                           │                       │
    │          │ await asyncio.sleep(0)   │                       │
    │          │ (CRITICAL!)               │                       │
    │          │                           ▼                       │
    │          │                  ┌──────────────────┐            │
    │          │                  │  Output Loop     │            │
    │          │                  │  (yields to      │            │
    │          └──────────────────│   client)        │            │
    │                             └──────────────────┘            │
    └─────────────────────────────────────────────────────────────┘
    ```

    **Concurrency Model**:
    - Input task runs concurrently, processing incoming messages
    - Output loop yields commands from queue back to client
    - `await asyncio.sleep(0)` ensures output loop can yield promptly
    - Ping messages sent on timeout to keep connection alive

    **Parameters**:
        config: Pydantic configuration model
        message_processor: Callback to process each incoming message
        client_id_extractor: Callback to extract client ID from message
        ping_message_creator: Callback to create ping messages
        on_connect: Optional callback when client connects
        on_disconnect: Optional callback when client disconnects
        on_error: Optional callback on errors
    """

    def __init__(
        self,
        config: BidirectionalStreamingConfig,
        message_processor: MessageProcessor[TMessage, TCommand],
        client_id_extractor: ClientIdExtractor[TMessage],
        ping_message_creator: PingMessageCreator[TCommand],
        on_connect: Optional[ConnectionCallback] = None,
        on_disconnect: Optional[ConnectionCallback] = None,
        on_error: Optional[ErrorHandler] = None,
        logger: Optional[logging.Logger] = None,
    ):
        """
        Initialize bidirectional streaming service.

        Args:
            config: Pydantic configuration (frozen, validated)
            message_processor: Process incoming messages
            client_id_extractor: Extract client ID from messages
            ping_message_creator: Create ping messages
            on_connect: Optional connection callback
            on_disconnect: Optional disconnection callback
            on_error: Optional error callback
            logger: Optional logger instance (auto-created if None)
        """
        self.config = config
        self.message_processor = message_processor
        self.client_id_extractor = client_id_extractor
        self.ping_message_creator = ping_message_creator
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

        # Active connections tracking
        self._active_connections: Dict[str, asyncio.Queue[TCommand]] = {}

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

        **Flow**:
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
            output_queue = asyncio.Queue(maxsize=self.config.max_queue_size)

            # Start background task to process incoming messages
            # This runs concurrently with output streaming below
            input_task = asyncio.create_task(
                self._process_input_stream(
                    request_iterator,
                    output_queue,
                    context,
                )
            )

            # Main output loop: yield commands from queue
            async for command in self._output_loop(output_queue, context):
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
                    self.logger.error(f"Input task error: {e}", exc_info=True)
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
                self.logger.error(f"Client {client_id} stream error: {e}", exc_info=True)

            if self.on_error and client_id:
                await self.on_error(client_id, e)

            await context.abort(grpc.StatusCode.INTERNAL, f"Server error: {e}")

        finally:
            # Cleanup connection
            if client_id and client_id in self._active_connections:
                del self._active_connections[client_id]
                if self.config.enable_logging:
                    self.logger.info(f"Client {client_id} disconnected")

                if self.on_disconnect:
                    await self.on_disconnect(client_id)

    # ------------------------------------------------------------------------
    # Output Loop
    # ------------------------------------------------------------------------

    async def _output_loop(
        self,
        output_queue: asyncio.Queue[TCommand],
        context: grpc.aio.ServicerContext,
    ) -> AsyncIterator[TCommand]:
        """
        Main output loop that yields commands to client.

        **Logic**:
        - Wait for commands in queue with timeout
        - If timeout and ping enabled -> send ping
        - Yield commands to client
        - Stop when context cancelled or sentinel received

        Args:
            output_queue: Queue containing commands to send
            context: gRPC service context

        Yields:
            Commands to send to client
        """
        ping_sequence = 0
        last_message_time = time.time()
        consecutive_errors = 0

        try:
            while not context.cancelled():
                try:
                    # Determine timeout based on ping strategy
                    timeout = self._get_output_timeout(last_message_time)

                    # Wait for command with timeout
                    command = await asyncio.wait_for(
                        output_queue.get(),
                        timeout=timeout,
                    )

                    # Check for shutdown sentinel (None)
                    if command is None:
                        if self.config.enable_logging:
                            self.logger.info("Received shutdown sentinel")
                        break

                    # Yield command to client
                    yield command
                    last_message_time = time.time()
                    consecutive_errors = 0  # Reset error counter

                    if self.config.enable_logging:
                        self.logger.debug("Sent command to client")

                except asyncio.TimeoutError:
                    # Timeout - send ping if enabled
                    if self.config.is_ping_enabled():
                        ping_sequence += 1
                        ping_command = self.ping_message_creator()
                        yield ping_command
                        last_message_time = time.time()

                        if self.config.enable_logging:
                            self.logger.debug(f"Sent PING #{ping_sequence}")

                except Exception as e:
                    consecutive_errors += 1
                    if self.config.enable_logging:
                        self.logger.error(f"Output loop error: {e}", exc_info=True)

                    # Check if max consecutive errors exceeded
                    if (
                        self.config.max_consecutive_errors > 0
                        and consecutive_errors >= self.config.max_consecutive_errors
                    ):
                        if self.config.enable_logging:
                            self.logger.error(
                                f"Max consecutive errors ({self.config.max_consecutive_errors}) exceeded"
                            )
                        break

        except asyncio.CancelledError:
            if self.config.enable_logging:
                self.logger.info("Output loop cancelled")
            raise

    def _get_output_timeout(self, last_message_time: float) -> Optional[float]:
        """
        Calculate output queue timeout based on ping strategy.

        Args:
            last_message_time: Timestamp of last sent message

        Returns:
            Timeout in seconds, or None for no timeout
        """
        if self.config.ping_strategy == PingStrategy.DISABLED:
            # No timeout when ping disabled (wait indefinitely)
            return None

        elif self.config.ping_strategy == PingStrategy.INTERVAL:
            # Fixed interval timeout
            return self.config.ping_interval

        elif self.config.ping_strategy == PingStrategy.ON_IDLE:
            # Timeout based on time since last message
            elapsed = time.time() - last_message_time
            remaining = self.config.ping_interval - elapsed
            return max(remaining, 0.1)  # At least 0.1s

        return self.config.ping_interval  # Fallback

    # ------------------------------------------------------------------------
    # Input Processing
    # ------------------------------------------------------------------------

    async def _process_input_stream(
        self,
        request_iterator: AsyncIterator[TMessage],
        output_queue: asyncio.Queue[TCommand],
        context: grpc.aio.ServicerContext,
    ) -> None:
        """
        Process incoming messages from client.

        **Flow**:
        1. Iterate over incoming messages
        2. Extract client ID from first message
        3. Call on_connect callback
        4. Process each message via message_processor
        5. **CRITICAL**: `await asyncio.sleep(0)` to yield event loop

        Args:
            request_iterator: Stream of incoming messages
            output_queue: Queue for outgoing commands
            context: gRPC service context

        Raises:
            Exception: Any processing errors
        """
        client_id: Optional[str] = None
        is_first_message = True

        try:
            # Choose iteration mode based on config
            if self.config.streaming_mode == StreamingMode.ASYNC_FOR:
                await self._process_async_for(
                    request_iterator,
                    output_queue,
                    context,
                )
            else:  # StreamingMode.ANEXT
                await self._process_anext(
                    request_iterator,
                    output_queue,
                    context,
                )

        except asyncio.CancelledError:
            if self.config.enable_logging:
                self.logger.info(f"Input stream cancelled for client {client_id}")
            raise

        except Exception as e:
            if self.config.enable_logging:
                self.logger.error(f"Input stream error for client {client_id}: {e}", exc_info=True)
            raise

    async def _process_async_for(
        self,
        request_iterator: AsyncIterator[TMessage],
        output_queue: asyncio.Queue[TCommand],
        context: grpc.aio.ServicerContext,
    ) -> None:
        """Process input stream using async for iteration."""
        client_id: Optional[str] = None
        is_first_message = True

        async for message in request_iterator:
            # Extract client ID from first message
            if is_first_message:
                client_id = self.client_id_extractor(message)
                self._active_connections[client_id] = output_queue
                is_first_message = False

                if self.config.enable_logging:
                    self.logger.info(f"Client {client_id} connected")

                if self.on_connect:
                    await self.on_connect(client_id)

            # Process message
            await self.message_processor(client_id, message, output_queue)

            # ⚠️ CRITICAL: Yield to event loop!
            # Without this, the next message read blocks output loop from yielding.
            # This is the key pattern that makes bidirectional streaming work correctly.
            if self.config.should_yield_event_loop():
                await asyncio.sleep(0)

    async def _process_anext(
        self,
        request_iterator: AsyncIterator[TMessage],
        output_queue: asyncio.Queue[TCommand],
        context: grpc.aio.ServicerContext,
    ) -> None:
        """Process input stream using anext() calls."""
        client_id: Optional[str] = None
        is_first_message = True

        while not context.cancelled():
            try:
                # Get next message with optional timeout
                if self.config.connection_timeout:
                    message = await asyncio.wait_for(
                        anext(request_iterator),
                        timeout=self.config.connection_timeout,
                    )
                else:
                    message = await anext(request_iterator)

                # Extract client ID from first message
                if is_first_message:
                    client_id = self.client_id_extractor(message)
                    self._active_connections[client_id] = output_queue
                    is_first_message = False

                    if self.config.enable_logging:
                        self.logger.info(f"Client {client_id} connected")

                    if self.on_connect:
                        await self.on_connect(client_id)

                # Process message
                await self.message_processor(client_id, message, output_queue)

                # ⚠️ CRITICAL: Yield to event loop!
                if self.config.should_yield_event_loop():
                    await asyncio.sleep(0)

            except StopAsyncIteration:
                # Stream ended normally
                if self.config.enable_logging:
                    self.logger.info(f"Client {client_id} stream ended")
                break

            except asyncio.TimeoutError:
                if self.config.enable_logging:
                    self.logger.warning(f"Client {client_id} connection timeout")
                break

    # ------------------------------------------------------------------------
    # Connection Management
    # ------------------------------------------------------------------------

    def get_active_connections(self) -> Dict[str, asyncio.Queue[TCommand]]:
        """
        Get all active connections.

        Returns:
            Dict mapping client_id to output_queue
        """
        return self._active_connections.copy()

    def is_client_connected(self, client_id: str) -> bool:
        """
        Check if client is currently connected.

        Args:
            client_id: Client identifier

        Returns:
            True if client has active connection
        """
        return client_id in self._active_connections

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
            asyncio.TimeoutError: If enqueue times out and no default handler
        """
        if client_id not in self._active_connections:
            if self.config.enable_logging:
                self.logger.warning(f"Client {client_id} not connected")
            return False

        queue = self._active_connections[client_id]
        timeout = timeout or self.config.queue_timeout

        try:
            await asyncio.wait_for(queue.put(command), timeout=timeout)
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

        for client_id in list(self._active_connections.keys()):
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
        if client_id in self._active_connections:
            queue = self._active_connections[client_id]
            await queue.put(None)  # Sentinel for shutdown


# ============================================================================
# Exports
# ============================================================================

__all__ = [
    'BidirectionalStreamingService',
]
