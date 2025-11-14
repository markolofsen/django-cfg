"""
Type definitions, protocols, and callbacks for bidirectional streaming.

This module defines all the core types and protocols used throughout
the streaming system.

Created: 2025-11-14
Status: %%PRODUCTION%%
Phase: Phase 1 - Universal Components (Refactored)
"""

import asyncio
from typing import TypeVar, Protocol, Callable, Awaitable, Optional, Any
from google.protobuf.message import Message


# ============================================================================
# Type Variables
# ============================================================================

TMessage = TypeVar('TMessage', bound=Message)
"""Type variable for incoming protobuf messages from client."""

TCommand = TypeVar('TCommand', bound=Message)
"""Type variable for outgoing protobuf commands to client."""


# ============================================================================
# Callback Protocols
# ============================================================================

class ClientIdExtractor(Protocol[TMessage]):
    """
    Protocol for extracting client ID from incoming message.

    Used to identify which client sent the message.

    Example:
        def extract_bot_id(message: BotMessage) -> str:
            return message.bot_id
    """

    def __call__(self, message: TMessage) -> str:
        """
        Extract client ID from message.

        Args:
            message: Incoming protobuf message

        Returns:
            Client UUID string
        """
        ...


class PingMessageCreator(Protocol[TCommand]):
    """
    Protocol for creating ping/keepalive messages.

    Used to send periodic keepalive messages to clients.

    Example:
        def create_ping_command(converter: ProtobufConverter) -> DjangoCommand:
            return converter.create_ping_command(sequence=0)
    """

    def __call__(self) -> TCommand:
        """
        Create ping message.

        Returns:
            Ping command protobuf message
        """
        ...


class MessageProcessor(Protocol[TMessage, TCommand]):
    """
    Protocol for processing incoming messages.

    The main business logic handler that processes each incoming message
    and optionally enqueues commands to send back to the client.

    Example:
        async def process_bot_message(
            client_id: str,
            message: BotMessage,
            output_queue: asyncio.Queue[DjangoCommand],
            streaming_service: BidirectionalStreamingService
        ) -> None:
            # Process message and enqueue responses
            await output_queue.put(response_command)
    """

    async def __call__(
        self,
        client_id: str,
        message: TMessage,
        output_queue: asyncio.Queue[TCommand],
        streaming_service: Optional[Any] = None
    ) -> None:
        """
        Process incoming message.

        Args:
            client_id: Client UUID
            message: Incoming protobuf message
            output_queue: Queue for outgoing commands
            streaming_service: Optional reference to streaming service
        """
        ...


class CommandAckExtractor(Protocol[TMessage]):
    """
    Protocol for extracting CommandAck from incoming messages.

    Used to automatically resolve pending commands in ResponseRegistry.
    This enables synchronous RPC-style command execution over bidirectional streams.

    Example:
        def extract_command_ack(message: BotMessage) -> Optional[CommandAck]:
            if message.HasField('command_ack'):
                return message.command_ack
            return None
    """

    def __call__(self, message: TMessage) -> Optional[Message]:
        """
        Extract CommandAck from message.

        Args:
            message: Incoming protobuf message

        Returns:
            CommandAck protobuf message if present, None otherwise
        """
        ...


class HeartbeatExtractor(Protocol[TMessage]):
    """
    Protocol for extracting Heartbeat from incoming messages.

    Used to automatically handle heartbeat updates (last_seen timestamp, metrics, etc).
    This is a standard pattern for keeping connections alive and tracking client health.

    Example:
        def extract_heartbeat(message: BotMessage) -> Optional[HeartbeatUpdate]:
            if message.HasField('heartbeat'):
                return message.heartbeat
            return None
    """

    def __call__(self, message: TMessage) -> Optional[Message]:
        """
        Extract Heartbeat from message.

        Args:
            message: Incoming protobuf message

        Returns:
            Heartbeat protobuf message if present, None otherwise
        """
        ...


class HeartbeatCallback(Protocol):
    """
    Protocol for handling heartbeat updates.

    Universal callback for processing heartbeat messages:
    - Update last_seen/last_heartbeat_at timestamp in database
    - Update metrics (CPU, memory, etc.)
    - Log heartbeat activity
    - Optionally send ping acknowledgment

    Example:
        async def handle_heartbeat(
            client_id: str,
            heartbeat: HeartbeatUpdate,
            output_queue: asyncio.Queue
        ) -> None:
            # Update DB
            await Client.objects.filter(id=client_id).aupdate(
                last_heartbeat_at=timezone.now()
            )
            # Send ping ack
            await output_queue.put(create_ping_command())
    """

    async def __call__(
        self,
        client_id: str,
        heartbeat: Message,
        output_queue: asyncio.Queue
    ) -> None:
        """
        Handle heartbeat update.

        Args:
            client_id: Client UUID
            heartbeat: Heartbeat protobuf message
            output_queue: Queue for sending responses (e.g., ping ack)
        """
        ...


class ConnectionCallback(Protocol):
    """
    Protocol for connection lifecycle callbacks.

    Used for on_connect and on_disconnect handlers.

    Example:
        async def on_connect(client_id: str) -> None:
            print(f"Client {client_id} connected")
            await update_client_status(client_id, "online")
    """

    async def __call__(self, client_id: str) -> None:
        """
        Handle connection event.

        Args:
            client_id: Client UUID
        """
        ...


class ErrorHandler(Protocol):
    """
    Protocol for error handling callbacks.

    Used for on_error handler to process exceptions during streaming.

    Example:
        async def on_error(client_id: str, error: Exception) -> None:
            print(f"Error for {client_id}: {error}")
            await log_error(client_id, error)
    """

    async def __call__(self, client_id: str, error: Exception) -> None:
        """
        Handle error event.

        Args:
            client_id: Client UUID
            error: Exception that occurred
        """
        ...


# ============================================================================
# Connection State
# ============================================================================

class ConnectionInfo:
    """
    Information about an active client connection.

    Stores metadata about the connection for management and debugging.
    """

    def __init__(
        self,
        client_id: str,
        output_queue: asyncio.Queue,
        connected_at: float,
        metadata: Optional[dict] = None
    ):
        self.client_id = client_id
        self.output_queue = output_queue
        self.connected_at = connected_at
        self.metadata = metadata or {}
        self.last_message_at: Optional[float] = None
        self.message_count: int = 0

    def update_activity(self, timestamp: float) -> None:
        """Update last activity timestamp."""
        self.last_message_at = timestamp
        self.message_count += 1

    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        return {
            'client_id': self.client_id,
            'connected_at': self.connected_at,
            'last_message_at': self.last_message_at,
            'message_count': self.message_count,
            'metadata': self.metadata,
        }


# ============================================================================
# Exports
# ============================================================================

__all__ = [
    # Type variables
    'TMessage',
    'TCommand',

    # Protocols
    'ClientIdExtractor',
    'PingMessageCreator',
    'MessageProcessor',
    'CommandAckExtractor',
    'HeartbeatExtractor',
    'HeartbeatCallback',
    'ConnectionCallback',
    'ErrorHandler',

    # Connection state
    'ConnectionInfo',
]
