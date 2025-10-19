"""
AI Command Consumer.

Consumes AI commands from Django and routes to CLI manager services.
Replaces the need for a standalone Router service.
"""

import asyncio
from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional
from pydantic import BaseModel, Field, ValidationError
from redis.asyncio import Redis
from loguru import logger


# =============================================================================
# Pydantic Models
# =============================================================================

class AIService(str, Enum):
    """Supported AI CLI services."""
    CLAUDE = "claude"
    CURSOR = "cursor"
    MCP = "mcp"


class AICommand(BaseModel):
    """
    AI command from Django.

    This command is sent from Django when a user requests AI assistance.
    The consumer routes it to the appropriate CLI manager service.
    """
    service: AIService
    session_id: str
    workspace_path: str
    message: str
    context: Optional[Dict[str, Any]] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


# =============================================================================
# AI Command Consumer
# =============================================================================

class AICommandConsumer:
    """
    AI Command Consumer.

    Consumes AI commands from Redis Streams and routes to service-specific streams.
    This eliminates the need for a standalone Router service by integrating
    routing logic directly into django-ipc.

    Architecture:
        Django → stream:ai-commands → AI Command Consumer → stream:{service}-commands → CLI Managers

    Features:
        - XREADGROUP for reliable consumption
        - Pydantic validation for type safety
        - Service-specific stream routing
        - ACK processed messages
        - DLQ (Dead Letter Queue) for invalid commands
        - Error handling and retry logic
    """

    # Service-to-stream mapping
    SERVICE_STREAMS = {
        AIService.CLAUDE: "stream:claude-commands",
        AIService.CURSOR: "stream:cursor-commands",
        AIService.MCP: "stream:mcp-commands",
    }

    def __init__(
        self,
        redis: Redis,
        stream_name: str = "stream:ai-commands",
        consumer_group: str = "websocket-router",
        consumer_name: str = "websocket-1",
        batch_size: int = 10,
        block_ms: int = 1000,
    ):
        """
        Initialize AI Command Consumer.

        Args:
            redis: Async Redis client
            stream_name: Redis Stream name for incoming commands
            consumer_group: Consumer group name
            consumer_name: This consumer's name
            batch_size: Max commands to read per iteration
            block_ms: Block time in milliseconds
        """
        self.redis = redis
        self.stream_name = stream_name
        self.consumer_group = consumer_group
        self.consumer_name = consumer_name
        self.batch_size = batch_size
        self.block_ms = block_ms

        self._running = False
        self._task: Optional[asyncio.Task] = None

    async def initialize(self) -> None:
        """Initialize consumer (create consumer group if needed)."""
        try:
            # Try to create consumer group
            await self.redis.xgroup_create(
                name=self.stream_name,
                groupname=self.consumer_group,
                id="0",
                mkstream=True,
            )
            logger.info(
                f"📦 Created consumer group: {self.consumer_group} "
                f"on stream: {self.stream_name}"
            )
        except Exception as e:
            # Group already exists
            if "BUSYGROUP" in str(e):
                logger.info(
                    f"📦 Consumer group exists: {self.consumer_group} "
                    f"on stream: {self.stream_name}"
                )
            else:
                logger.error(f"❌ Failed to create consumer group: {e}")
                raise

    async def start(self) -> None:
        """Start consuming AI commands."""
        if self._running:
            logger.warning("⚠️  AI Command Consumer already running")
            return

        logger.info("=" * 80)
        logger.info("🚀 Starting AI Command Consumer (Router Replacement)")
        logger.info(f"📡 Stream: {self.stream_name}")
        logger.info(f"👥 Consumer Group: {self.consumer_group}")
        logger.info(f"🏷️  Consumer Name: {self.consumer_name}")
        logger.info(f"📦 Batch Size: {self.batch_size}")
        logger.info(f"⏱️  Block Time: {self.block_ms}ms")
        logger.info("=" * 80)

        self._running = True
        self._task = asyncio.create_task(self._consume_loop())

    async def stop(self) -> None:
        """Stop consuming AI commands."""
        if not self._running:
            return

        logger.info("🛑 Stopping AI Command Consumer...")
        self._running = False

        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass

        logger.info("✅ AI Command Consumer stopped")

    async def _consume_loop(self) -> None:
        """Main consumption loop."""
        while self._running:
            try:
                # XREADGROUP: Read from stream
                messages = await self.redis.xreadgroup(
                    groupname=self.consumer_group,
                    consumername=self.consumer_name,
                    streams={self.stream_name: ">"},
                    count=self.batch_size,
                    block=self.block_ms,
                )

                if not messages:
                    continue

                # Process messages
                for stream_name, stream_messages in messages:
                    for message_id, data in stream_messages:
                        await self._process_message(message_id, data)

            except asyncio.CancelledError:
                logger.info("⚠️  AI Command Consumer loop cancelled")
                break
            except Exception as e:
                logger.error(f"❌ Error in AI command consume loop: {e}")
                await asyncio.sleep(1)  # Brief pause before retry

    async def _process_message(
        self,
        message_id: str,
        data: Dict[bytes, bytes],
    ) -> None:
        """
        Process a single AI command message from Redis Stream.

        Args:
            message_id: Redis Stream message ID
            data: Message data (binary)
        """
        try:
            # Decode payload
            payload_bytes = data.get(b'payload')
            if not payload_bytes:
                logger.warning(f"⚠️  No payload in message: {message_id}")
                await self._ack_message(message_id)
                return

            payload = payload_bytes.decode('utf-8')

            # Validate command
            cmd = AICommand.model_validate_json(payload)

            # Route to service-specific stream
            target_stream = self.SERVICE_STREAMS[cmd.service]

            await self.redis.xadd(
                target_stream,
                {b'payload': payload.encode()},
                maxlen=10000,  # Keep last 10k messages
            )

            # ACK message
            await self._ack_message(message_id)

            logger.info(
                f"✅ Routed {cmd.service.value} command "
                f"{message_id.decode()[:8]}... → {target_stream}"
            )

        except ValidationError as e:
            # Invalid command - send to DLQ and ACK
            logger.error(f"❌ Validation error for message {message_id}: {e}")

            await self._send_to_dlq(message_id, data, str(e))

            # ACK to avoid infinite retry
            await self._ack_message(message_id)

        except Exception as e:
            # Processing error - DON'T ACK (will retry)
            logger.error(f"❌ Error processing AI command {message_id}: {e}")
            # Don't ACK - will be retried

    async def _send_to_dlq(
        self,
        message_id: str,
        data: Dict[bytes, bytes],
        error: str,
    ) -> None:
        """
        Send invalid message to Dead Letter Queue.

        Args:
            message_id: Original message ID
            data: Original message data
            error: Error description
        """
        try:
            dlq_stream = "stream:ai-commands-dlq"

            await self.redis.xadd(
                dlq_stream,
                {
                    b'msg_id': message_id.encode() if isinstance(message_id, str) else message_id,
                    b'error': error.encode(),
                    b'payload': data.get(b'payload', b''),
                    b'timestamp': str(datetime.utcnow()).encode(),
                }
            )

            logger.warning(f"⚠️  Sent invalid command to DLQ: {message_id}")

        except Exception as e:
            logger.error(f"❌ Failed to send to DLQ: {e}")

    async def _ack_message(self, message_id: str) -> None:
        """
        Acknowledge processed message.

        Args:
            message_id: Redis Stream message ID
        """
        try:
            await self.redis.xack(
                self.stream_name,
                self.consumer_group,
                message_id,
            )
            logger.debug(f"✅ ACK: {message_id}")
        except Exception as e:
            logger.error(f"❌ Failed to ACK {message_id}: {e}")
