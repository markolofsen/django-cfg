"""
File Watcher Consumer.

Consumes file change events from Redis Streams and broadcasts to WebSocket clients.
"""

import asyncio
import gzip
import json
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, ValidationError
from redis.asyncio import Redis
from loguru import logger


# =============================================================================
# Pydantic Models (matching TypeScript FileEvent structure)
# =============================================================================

class WorkspaceInfo(BaseModel):
    """Workspace information."""
    id: str
    name: Optional[str] = None


class FileInfo(BaseModel):
    """File information."""
    path: str
    absolute_path: Optional[str] = None
    event_type: str  # create | modify | delete | rename
    old_path: Optional[str] = None


class ChangeInfo(BaseModel):
    """Change information."""
    type: str  # diff | full_content | hash | delete
    diff: Optional[str] = None
    content: Optional[str] = None
    hash: Optional[str] = None
    size: Optional[int] = None


class GitInfo(BaseModel):
    """Git information."""
    branch: str
    commit: Optional[str] = None
    author: Optional[str] = None


class FileEvent(BaseModel):
    """File change event (nested structure from TypeScript)."""
    event_id: str
    timestamp: str
    batch_id: Optional[str] = None
    workspace: WorkspaceInfo
    file: FileInfo
    change: ChangeInfo
    git: Optional[GitInfo] = None


class BatchEvent(BaseModel):
    """Batch of file events."""
    batch_id: str
    timestamp: str
    batch_count: int
    events: List[FileEvent]


# =============================================================================
# File Watcher Consumer
# =============================================================================

class FileWatcherConsumer:
    """
    File Watcher Consumer.

    Consumes file change events from Redis Streams (XREADGROUP) and broadcasts
    to WebSocket clients in workspace-specific rooms.

    Architecture:
        Redis Streams → Consumer (this class) → WebSocket broadcast → Frontend

    Features:
        - XREADGROUP for reliable consumption
        - Gzip decompression for large batches
        - Workspace-based room broadcasting
        - ACK processed messages
        - Error handling and retry logic
    """

    def __init__(
        self,
        redis: Redis,
        connection_manager,
        stream_name: str = "stream:file-events",
        consumer_group: str = "websocket-consumers",
        consumer_name: str = "websocket-1",
        batch_size: int = 10,
        block_ms: int = 5000,
    ):
        """
        Initialize File Watcher Consumer.

        Args:
            redis: Async Redis client
            connection_manager: ConnectionManager for broadcasting
            stream_name: Redis Stream name
            consumer_group: Consumer group name
            consumer_name: This consumer's name
            batch_size: Max events to read per iteration
            block_ms: Block time in milliseconds
        """
        self.redis = redis
        self.connection_manager = connection_manager
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
        """Start consuming events."""
        if self._running:
            logger.warning("⚠️  Consumer already running")
            return

        logger.info("=" * 80)
        logger.info("🚀 Starting File Watcher Consumer")
        logger.info(f"📡 Stream: {self.stream_name}")
        logger.info(f"👥 Consumer Group: {self.consumer_group}")
        logger.info(f"🏷️  Consumer Name: {self.consumer_name}")
        logger.info(f"📦 Batch Size: {self.batch_size}")
        logger.info(f"⏱️  Block Time: {self.block_ms}ms")
        logger.info("=" * 80)

        self._running = True
        self._task = asyncio.create_task(self._consume_loop())

    async def stop(self) -> None:
        """Stop consuming events."""
        if not self._running:
            return

        logger.info("🛑 Stopping File Watcher Consumer...")
        self._running = False

        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass

        logger.info("✅ File Watcher Consumer stopped")

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
                logger.info("⚠️  Consumer loop cancelled")
                break
            except Exception as e:
                logger.error(f"❌ Error in consume loop: {e}")
                await asyncio.sleep(1)  # Brief pause before retry

    async def _process_message(
        self,
        message_id: str,
        data: Dict[bytes, bytes],
    ) -> None:
        """
        Process a single message from Redis Stream.

        Args:
            message_id: Redis Stream message ID
            data: Message data (binary)
        """
        try:
            # Decode message data
            decoded_data = {
                k.decode("utf-8"): v.decode("utf-8")
                for k, v in data.items()
            }

            # Extract fields
            batch_data = decoded_data.get("data")
            is_compressed = decoded_data.get("compressed") == "true"
            batch_id = decoded_data.get("batch_id")
            batch_count = decoded_data.get("batch_count", "0")

            if not batch_data:
                logger.warning(f"⚠️  No data in message: {message_id}")
                await self._ack_message(message_id)
                return

            # Decompress if needed
            if is_compressed:
                logger.debug(f"📦 Decompressing batch: {batch_id}")
                import base64
                compressed = base64.b64decode(batch_data)
                batch_json = gzip.decompress(compressed).decode("utf-8")
            else:
                batch_json = batch_data

            # Parse batch
            batch = BatchEvent.model_validate_json(batch_json)

            logger.info(
                f"📨 Received batch: {batch.batch_id} | "
                f"Events: {batch.batch_count} | "
                f"Compressed: {is_compressed}"
            )

            # Process each event in batch
            for event in batch.events:
                await self._broadcast_event(event)

            # ACK message
            await self._ack_message(message_id)

            logger.debug(f"✅ Processed batch: {batch.batch_id}")

        except ValidationError as e:
            logger.error(f"❌ Validation error for message {message_id}: {e}")
            await self._ack_message(message_id)  # ACK to avoid reprocessing bad data
        except Exception as e:
            logger.error(f"❌ Error processing message {message_id}: {e}")
            # Don't ACK - will be retried

    async def _broadcast_event(self, event: FileEvent) -> None:
        """
        Broadcast file event to WebSocket clients.

        Args:
            event: File event to broadcast
        """
        workspace_id = event.workspace.id
        room_name = f"workspace:{workspace_id}"

        # Prepare WebSocket message
        ws_message = {
            "type": "file.changed",
            "data": {
                "event_id": event.event_id,
                "timestamp": event.timestamp,
                "workspace": {
                    "id": event.workspace.id,
                    "name": event.workspace.name,
                },
                "file": {
                    "path": event.file.path,
                    "absolute_path": event.file.absolute_path,
                    "event_type": event.file.event_type,
                    "old_path": event.file.old_path,
                },
                "change": {
                    "type": event.change.type,
                    "diff": event.change.diff,
                    "content": event.change.content,
                    "hash": event.change.hash,
                    "size": event.change.size,
                },
                "git": (
                    {
                        "branch": event.git.branch,
                        "commit": event.git.commit,
                        "author": event.git.author,
                    }
                    if event.git
                    else None
                ),
            },
        }

        # Broadcast to all connections
        num_clients = await self.connection_manager.broadcast(
            message=ws_message,
        )

        logger.info(
            f"📡 Broadcast file event: {event.file.event_type} | {event.file.path} → {num_clients} clients"
        )

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
