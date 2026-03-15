"""
Input message processing for bidirectional streaming.

Handles incoming messages from clients with async iteration support.

Created: 2025-11-14
Status: %%PRODUCTION%%
Phase: Phase 1 - Universal Components (Refactored)
"""

import asyncio
import logging
import traceback
from typing import AsyncIterator, Optional, Any
import grpc

from ..types import (
    TMessage,
    TCommand,
    ClientIdExtractor,
    MessageProcessor,
    CommandAckExtractor,
    HeartbeatExtractor,
    HeartbeatCallback,
)
from ..integrations.centrifugo import CentrifugoPublisher
from ..config import StreamingMode

# Logger will be configured by BidirectionalStreamingService via setup_streaming_logger
logger = logging.getLogger("grpc_streaming.input_processor")


class InputProcessor:
    """
    Processes incoming messages from clients.

    Responsibilities:
    - Extract client_id from each message
    - Auto-resolve CommandAck (for synchronous RPC)
    - Auto-handle Heartbeat (for keepalive + metrics)
    - Route messages to message processor callback
    - Auto-publish to Centrifugo (if configured)
    - Handle errors gracefully
    - Support both async for and anext() iteration modes
    """

    def __init__(
        self,
        extract_client_id: ClientIdExtractor[TMessage],
        process_message: MessageProcessor[TMessage, TCommand],
        centrifugo_publisher: Optional[CentrifugoPublisher] = None,
        command_ack_extractor: Optional[CommandAckExtractor[TMessage]] = None,
        heartbeat_extractor: Optional[HeartbeatExtractor[TMessage]] = None,
        heartbeat_callback: Optional[HeartbeatCallback] = None,
        streaming_mode: StreamingMode = StreamingMode.ASYNC_FOR,
        connection_timeout: Optional[float] = None,
        yield_event_loop: bool = True,
        enable_logging: bool = True
    ):
        """
        Initialize input processor.

        Args:
            extract_client_id: Callback to extract client_id from message
            process_message: Callback to process message (business logic)
            centrifugo_publisher: Optional Centrifugo publisher for auto-publishing
            command_ack_extractor: Optional callback to extract CommandAck from message
            heartbeat_extractor: Optional callback to extract Heartbeat from message
            heartbeat_callback: Optional callback to handle heartbeat (update DB, send ping)
            streaming_mode: ASYNC_FOR or ANEXT iteration mode
            connection_timeout: Timeout for anext() mode (None = no timeout)
            yield_event_loop: Whether to yield event loop with asyncio.sleep(0)
            enable_logging: Enable logging
        """
        self.extract_client_id = extract_client_id
        self.process_message = process_message
        self.centrifugo_publisher = centrifugo_publisher
        self.command_ack_extractor = command_ack_extractor
        self.heartbeat_extractor = heartbeat_extractor
        self.heartbeat_callback = heartbeat_callback
        self.streaming_mode = streaming_mode
        self.connection_timeout = connection_timeout
        self.yield_event_loop = yield_event_loop
        self.enable_logging = enable_logging

    async def process_stream(
        self,
        request_iterator: AsyncIterator[TMessage],
        output_queue: asyncio.Queue[TCommand],
        context: grpc.aio.ServicerContext,
        streaming_service: Optional[Any] = None,
        on_connect: Optional[Any] = None
    ) -> Optional[str]:
        """
        Process incoming message stream.

        Args:
            request_iterator: Async iterator of incoming messages
            output_queue: Queue for outgoing commands
            context: gRPC service context
            streaming_service: Reference to BidirectionalStreamingService (for callbacks)
            on_connect: Optional callback when client connects

        Returns:
            client_id if extracted, None otherwise

        Raises:
            Exception: If critical error occurs during processing
        """
        if self.streaming_mode == StreamingMode.ASYNC_FOR:
            return await self._process_async_for(
                request_iterator,
                output_queue,
                context,
                streaming_service,
                on_connect
            )
        else:  # StreamingMode.ANEXT
            return await self._process_anext(
                request_iterator,
                output_queue,
                context,
                streaming_service,
                on_connect
            )

    async def _process_async_for(
        self,
        request_iterator: AsyncIterator[TMessage],
        output_queue: asyncio.Queue[TCommand],
        context: grpc.aio.ServicerContext,
        streaming_service: Optional[Any] = None,
        on_connect: Optional[Any] = None
    ) -> Optional[str]:
        """Process input stream using async for iteration."""
        client_id: Optional[str] = None
        is_first_message = True

        try:
            if self.enable_logging:
                logger.info("Starting async for loop")

            async for message in request_iterator:
                # DEBUG: Log every received message
                msg_type = message.WhichOneof('payload') if hasattr(message, 'WhichOneof') else 'unknown'
                print(f"\n📥📥📥 [INPUT_PROCESSOR] Received message type={msg_type}", flush=True)
                logger.info(f"📥 [INPUT_PROCESSOR] Received message type={msg_type}")

                # Extract client ID from first message
                if is_first_message:
                    client_id = self.extract_client_id(message)
                    is_first_message = False

                    # Register connection in ConnectionManager
                    if streaming_service and hasattr(streaming_service, 'connection_manager'):
                        streaming_service.connection_manager.register(
                            client_id=client_id,
                            output_queue=output_queue
                        )

                    if self.enable_logging:
                        logger.info(f"Client {client_id[:8]}... connected")

                    if on_connect:
                        await on_connect(client_id)

                # Auto-publish to Centrifugo (Client � Server message)
                if self.centrifugo_publisher:
                    await self.centrifugo_publisher.publish_message(
                        client_id=client_id,
                        message=message
                    )


                # Auto-resolve CommandAck (for synchronous RPC)
                if self.command_ack_extractor and streaming_service:
                    command_ack = self.command_ack_extractor(message)
                    if command_ack and hasattr(command_ack, 'command_id') and command_ack.command_id:
                        # Resolve in ResponseRegistry (only if command_id is not empty)
                        if hasattr(streaming_service, 'response_registry'):
                            await streaming_service.response_registry.resolve_command(
                                command_ack.command_id,
                                command_ack
                            )
                            if self.enable_logging:
                                logger.debug(
                                    f"✅ Auto-resolved CommandAck: {command_ack.command_id} "
                                    f"(client={client_id[:8]}...)"
                                )
                            # CommandAck processed, skip user's message_processor
                            continue

                # Auto-handle Heartbeat (for keepalive)
                if self.heartbeat_extractor and self.heartbeat_callback:
                    heartbeat = self.heartbeat_extractor(message)
                    if heartbeat:
                        # Run in background (non-blocking - DB queries can be slow)
                        asyncio.create_task(
                            self.heartbeat_callback(
                                client_id=client_id,
                                heartbeat=heartbeat,
                                output_queue=output_queue
                            )
                        )
                        if self.enable_logging:
                            logger.debug(
                                f"💓 Auto-handled Heartbeat (client={client_id[:8]}...)"
                            )
                        # Heartbeat processed, skip user's message_processor
                        continue

                # Process message (business logic)
                await self.process_message(
                    client_id=client_id,
                    message=message,
                    output_queue=output_queue,
                    streaming_service=streaming_service
                )

                # � CRITICAL: Yield to event loop!
                # Without this, the next message read blocks output loop from yielding.
                if self.yield_event_loop:
                    await asyncio.sleep(0)

        except asyncio.CancelledError:
            if self.enable_logging:
                logger.info(f"Input stream cancelled for client {client_id}")
            raise

        except Exception as e:
            if self.enable_logging:
                logger.error(
                    f"❌ [INPUT_PROCESSOR] Input stream error for client {client_id}:\n"
                    f"   Error: {type(e).__name__}: {e}\n"
                    f"   Traceback:\n{traceback.format_exc()}"
                )
            raise

        return client_id

    async def _process_anext(
        self,
        request_iterator: AsyncIterator[TMessage],
        output_queue: asyncio.Queue[TCommand],
        context: grpc.aio.ServicerContext,
        streaming_service: Optional[Any] = None,
        on_connect: Optional[Any] = None
    ) -> Optional[str]:
        """Process input stream using anext() calls."""
        client_id: Optional[str] = None
        is_first_message = True

        try:
            # DEBUG: Check context state before loop
            print(f"\n🔍 [INPUT_PROCESSOR] _process_anext starting", flush=True)
            print(f"   context.cancelled()={context.cancelled()}", flush=True)
            print(f"   request_iterator type={type(request_iterator)}", flush=True)
            if self.enable_logging:
                logger.info(f"_process_anext starting, context.cancelled()={context.cancelled()}")

            while not context.cancelled():
                try:
                    # Get next message with optional timeout
                    # NOTE: connection_timeout is for non-blocking read, not for closing connection
                    if self.connection_timeout:
                        message = await asyncio.wait_for(
                            anext(request_iterator),
                            timeout=self.connection_timeout,
                        )
                    else:
                        message = await anext(request_iterator)

                    # Extract client ID from first message
                    if is_first_message:
                        client_id = self.extract_client_id(message)
                        is_first_message = False

                        # Register connection in ConnectionManager
                        if streaming_service and hasattr(streaming_service, 'connection_manager'):
                            streaming_service.connection_manager.register(
                                client_id=client_id,
                                output_queue=output_queue
                            )

                        if self.enable_logging:
                            logger.info(f"Client {client_id[:8]}... connected")

                        if on_connect:
                            await on_connect(client_id)

                    # Auto-publish to Centrifugo (Client � Server message)
                    if self.centrifugo_publisher:
                        await self.centrifugo_publisher.publish_message(
                            client_id=client_id,
                            message=message
                        )

                    # Auto-resolve CommandAck (for synchronous RPC)
                    if self.command_ack_extractor and streaming_service:
                        command_ack = self.command_ack_extractor(message)
                        if command_ack and hasattr(command_ack, 'command_id') and command_ack.command_id:
                            # Resolve in ResponseRegistry (only if command_id is not empty)
                            if hasattr(streaming_service, 'response_registry'):
                                await streaming_service.response_registry.resolve_command(
                                    command_ack.command_id,
                                    command_ack
                                )
                                if self.enable_logging:
                                    logger.debug(
                                        f"✅ Auto-resolved CommandAck: {command_ack.command_id} "
                                        f"(client={client_id[:8]}...)"
                                    )
                                # CommandAck processed, skip user's message_processor
                                continue

                    # Auto-handle Heartbeat (for keepalive)
                    if self.heartbeat_extractor and self.heartbeat_callback:
                        heartbeat = self.heartbeat_extractor(message)
                        if heartbeat:
                            # Run in background (non-blocking - DB queries can be slow)
                            asyncio.create_task(
                                self.heartbeat_callback(
                                    client_id=client_id,
                                    heartbeat=heartbeat,
                                    output_queue=output_queue
                                )
                            )
                            if self.enable_logging:
                                logger.debug(
                                    f"💓 Auto-handled Heartbeat (client={client_id[:8]}...)"
                                )
                            # Heartbeat processed, skip user's message_processor
                            continue

                    # Process message (business logic)
                    await self.process_message(
                        client_id=client_id,
                        message=message,
                        output_queue=output_queue,
                        streaming_service=streaming_service
                    )

                    # � CRITICAL: Yield to event loop!
                    if self.yield_event_loop:
                        await asyncio.sleep(0)

                except StopAsyncIteration:
                    # Stream ended normally
                    print(f"   ⚠️ StopAsyncIteration - stream ended", flush=True)
                    if self.enable_logging:
                        logger.info(f"Client {client_id} stream ended")
                    break

                except asyncio.TimeoutError:
                    # connection_timeout is for non-blocking read, NOT for closing connection.
                    # Just continue the loop to check context.cancelled() and wait for more messages.
                    # The real connection timeout should be handled via ping_timeout in OutputProcessor.
                    continue

            # DEBUG: Log when while loop exits normally (context.cancelled() == True)
            if self.enable_logging:
                logger.info(f"_process_anext while loop exited, context.cancelled()={context.cancelled()}, client_id={client_id}")

        except asyncio.CancelledError:
            print(f"   🚫 CancelledError - input stream cancelled (client_id={client_id})", flush=True)
            if self.enable_logging:
                logger.info(f"Input stream cancelled for client {client_id}")
            raise

        except Exception as e:
            print(f"   ❌ Exception: {type(e).__name__}: {e}", flush=True)
            if self.enable_logging:
                logger.error(
                    f"❌ [INPUT_PROCESSOR] Input stream error (anext) for client {client_id}:\n"
                    f"   Error: {type(e).__name__}: {e}\n"
                    f"   Traceback:\n{traceback.format_exc()}"
                )
            raise

        print(f"   🏁 _process_anext returning, client_id={client_id}", flush=True)
        return client_id


# ============================================================================
# Exports
# ============================================================================

__all__ = [
    'InputProcessor',
]
