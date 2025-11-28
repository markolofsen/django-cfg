"""
Output command processing for bidirectional streaming.

Handles outgoing commands to clients with ping/keepalive support.

Created: 2025-11-14
Status: %%PRODUCTION%%
Phase: Phase 1 - Universal Components (Refactored)
"""

import asyncio
import time
import logging
import traceback
from typing import AsyncIterator, Optional
import grpc

from ..types import TCommand, PingMessageCreator
from ..integrations.centrifugo import CentrifugoPublisher
from ..config import PingStrategy

# Logger will be configured by BidirectionalStreamingService via setup_streaming_logger
logger = logging.getLogger("grpc_streaming.output_processor")


class OutputProcessor:
    """
    Processes outgoing commands to clients.

    Responsibilities:
    - Yield commands from output queue to client
    - Send ping messages on timeout (keepalive)
    - Auto-publish to Centrifugo (if configured)
    - Handle shutdown sentinel (None)
    - Track consecutive errors
    """

    def __init__(
        self,
        ping_message_creator: PingMessageCreator[TCommand],
        centrifugo_publisher: Optional[CentrifugoPublisher] = None,
        ping_strategy: PingStrategy = PingStrategy.INTERVAL,
        ping_interval: float = 30.0,
        max_consecutive_errors: int = 10,
        enable_logging: bool = True
    ):
        """
        Initialize output processor.

        Args:
            ping_message_creator: Callback to create ping messages
            centrifugo_publisher: Optional Centrifugo publisher for auto-publishing
            ping_strategy: DISABLED, INTERVAL, or ON_IDLE
            ping_interval: Ping interval in seconds
            max_consecutive_errors: Max consecutive errors before stopping
            enable_logging: Enable logging
        """
        self.ping_message_creator = ping_message_creator
        self.centrifugo_publisher = centrifugo_publisher
        self.ping_strategy = ping_strategy
        self.ping_interval = ping_interval
        self.max_consecutive_errors = max_consecutive_errors
        self.enable_logging = enable_logging

    async def process_queue(
        self,
        output_queue: asyncio.Queue[TCommand],
        context: grpc.aio.ServicerContext,
        client_id: Optional[str] = None
    ) -> AsyncIterator[TCommand]:
        """
        Main output loop that yields commands to client.

        Logic:
        - Wait for commands in queue with timeout
        - If timeout and ping enabled � send ping
        - Auto-publish command to Centrifugo (if enabled)
        - Yield commands to client
        - Stop when context cancelled or sentinel received

        Args:
            output_queue: Queue containing commands to send
            context: gRPC service context
            client_id: Optional client ID (for Centrifugo publishing)

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
                        if self.enable_logging:
                            logger.info("Received shutdown sentinel")
                        break

                    # Auto-publish outgoing command to Centrifugo (if enabled and client_id known)
                    if client_id and self.centrifugo_publisher:
                        await self.centrifugo_publisher.publish_command(
                            client_id=client_id,
                            command=command
                        )

                    # Yield command to client
                    yield command
                    last_message_time = time.time()
                    consecutive_errors = 0  # Reset error counter

                    if self.enable_logging:
                        logger.debug("Sent command to client")

                except asyncio.TimeoutError:
                    # Timeout - send ping if enabled
                    if self._is_ping_enabled():
                        ping_sequence += 1
                        ping_command = self.ping_message_creator()
                        yield ping_command
                        last_message_time = time.time()

                        if self.enable_logging:
                            logger.debug(f"Sent PING #{ping_sequence}")

                except Exception as e:
                    consecutive_errors += 1
                    if self.enable_logging:
                        logger.error(
                            f"❌ [OUTPUT_PROCESSOR] Output loop error (attempt {consecutive_errors}):\n"
                            f"   Error: {type(e).__name__}: {e}\n"
                            f"   Traceback:\n{traceback.format_exc()}"
                        )

                    # Check if max consecutive errors exceeded
                    if (
                        self.max_consecutive_errors > 0
                        and consecutive_errors >= self.max_consecutive_errors
                    ):
                        if self.enable_logging:
                            logger.error(
                                f"❌ [OUTPUT_PROCESSOR] Max consecutive errors ({self.max_consecutive_errors}) exceeded - stopping output loop"
                            )
                        break

        except asyncio.CancelledError:
            if self.enable_logging:
                logger.info("Output loop cancelled")
            raise

    def _is_ping_enabled(self) -> bool:
        """Check if ping is enabled."""
        return self.ping_strategy != PingStrategy.DISABLED

    def _get_output_timeout(self, last_message_time: float) -> Optional[float]:
        """
        Calculate output queue timeout based on ping strategy.

        Args:
            last_message_time: Timestamp of last sent message

        Returns:
            Timeout in seconds, or None for no timeout
        """
        if self.ping_strategy == PingStrategy.DISABLED:
            # No timeout when ping disabled (wait indefinitely)
            return None

        elif self.ping_strategy == PingStrategy.INTERVAL:
            # Fixed interval timeout
            return self.ping_interval

        elif self.ping_strategy == PingStrategy.ON_IDLE:
            # Timeout based on time since last message
            elapsed = time.time() - last_message_time
            remaining = self.ping_interval - elapsed
            return max(remaining, 0.1)  # At least 0.1s

        return self.ping_interval  # Fallback


# ============================================================================
# Exports
# ============================================================================

__all__ = [
    'OutputProcessor',
]
