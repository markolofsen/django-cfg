"""
Protocol type definitions for type-safe gRPC bidirectional streaming.

This module defines Protocol types used for generic, reusable gRPC streaming components.
All protocols are fully typed and support generic message/command types.

**Design Goals**:
- 100% type-safe callbacks
- Zero runtime overhead (protocols are compile-time only)
- Compatible with any protobuf message types
- Enables IDE autocomplete and mypy validation

**Usage Example**:
```python
# Define your processor
async def process_signal_message(
    client_id: str,
    message: SignalCommand,
    output_queue: asyncio.Queue[SignalMessage]
) -> None:
    # Your logic here
    await output_queue.put(response)

# Type checker validates signature matches MessageProcessor protocol
service = BidirectionalStreamingService(
    message_processor=process_signal_message,  # ✅ Type-safe
    ...
)
```

Created: 2025-11-07
Status: %%PRODUCTION%%
Phase: Phase 1 - Universal Components
"""

from typing import Protocol, TypeVar, Any
import asyncio


# ============================================================================
# Generic Type Variables
# ============================================================================

TMessage = TypeVar('TMessage', contravariant=True)
"""
Generic type for incoming gRPC messages (commands from client).

**Contravariant**: Allows passing more specific message types where generic is expected.

Example:
    - Protocol expects: Message (base)
    - Can pass: SignalCommand (subclass)
"""

TCommand = TypeVar('TCommand', covariant=True)
"""
Generic type for outgoing gRPC commands (responses to client).

**Covariant**: Allows returning more general command types where specific is expected.

Example:
    - Protocol returns: BotResponse (specific)
    - Can be treated as: Message (base)
"""


# ============================================================================
# Core Processing Protocols
# ============================================================================

class MessageProcessor(Protocol[TMessage, TCommand]):
    """
    Protocol for processing incoming gRPC messages and generating responses.

    This is the core business logic handler that processes each message from the client
    and optionally enqueues response commands.

    **Type Parameters**:
        TMessage: Type of incoming messages (e.g., SignalCommand, BotCommand)
        TCommand: Type of outgoing commands (e.g., SignalMessage, BotResponse)

    **Signature**:
        async def(client_id: str, message: TMessage, output_queue: Queue[TCommand]) -> None

    **Parameters**:
        client_id: Unique identifier for the connected client
        message: Incoming message from client (generic type TMessage)
        output_queue: Queue to enqueue response commands (generic type TCommand)

    **Example Implementation**:
    ```python
    async def process_bot_command(
        client_id: str,
        message: BotCommand,
        output_queue: asyncio.Queue[BotResponse]
    ) -> None:
        logger.info(f"Processing command for {client_id}")

        if message.command_type == CommandType.START:
            response = BotResponse(status="started")
            await output_queue.put(response)
    ```
    """
    async def __call__(
        self,
        client_id: str,
        message: TMessage,
        output_queue: asyncio.Queue[TCommand]
    ) -> None:
        """Process incoming message and optionally enqueue responses."""
        ...


class ClientIdExtractor(Protocol[TMessage]):
    """
    Protocol for extracting client ID from incoming gRPC messages.

    Different services may store client IDs in different message fields.
    This protocol allows type-safe client ID extraction.

    **Type Parameters**:
        TMessage: Type of incoming messages

    **Signature**:
        def(message: TMessage) -> str

    **Example Implementation**:
    ```python
    def extract_bot_client_id(message: BotCommand) -> str:
        return str(message.bot_id)

    def extract_signal_client_id(message: SignalCommand) -> str:
        return message.client_id
    ```
    """
    def __call__(self, message: TMessage) -> str:
        """Extract client ID from message."""
        ...


class PingMessageCreator(Protocol[TCommand]):
    """
    Protocol for creating ping/keepalive messages.

    Bidirectional streams need periodic ping messages to keep connections alive.
    This protocol allows type-safe ping message creation.

    **Type Parameters**:
        TCommand: Type of outgoing commands

    **Signature**:
        def() -> TCommand

    **Example Implementation**:
    ```python
    def create_bot_ping() -> BotResponse:
        return BotResponse(
            message_type=MessageType.PING,
            timestamp=int(time.time())
        )

    def create_signal_ping() -> SignalMessage:
        return SignalMessage(is_ping=True)
    ```
    """
    def __call__(self) -> TCommand:
        """Create a ping message."""
        ...


# ============================================================================
# Connection Management Protocols
# ============================================================================

class ConnectionCallback(Protocol):
    """
    Protocol for connection lifecycle callbacks.

    **Signature**:
        async def(client_id: str) -> None

    **Use Cases**:
        - on_connect: Initialize resources, log connection
        - on_disconnect: Cleanup resources, update database
        - on_error: Handle connection errors

    **Example Implementation**:
    ```python
    async def on_client_connected(client_id: str) -> None:
        logger.info(f"Client {client_id} connected")
        await db.mark_client_active(client_id)

    async def on_client_disconnected(client_id: str) -> None:
        logger.info(f"Client {client_id} disconnected")
        await db.mark_client_inactive(client_id)
    ```
    """
    async def __call__(self, client_id: str) -> None:
        """Handle connection lifecycle event."""
        ...


class ErrorHandler(Protocol):
    """
    Protocol for handling errors during streaming.

    **Signature**:
        async def(client_id: str, error: Exception) -> None

    **Example Implementation**:
    ```python
    async def handle_stream_error(client_id: str, error: Exception) -> None:
        logger.error(f"Error for {client_id}: {error}")

        if isinstance(error, asyncio.CancelledError):
            # Normal cancellation, just log
            pass
        elif isinstance(error, grpc.RpcError):
            # gRPC-specific error handling
            await notify_admin(client_id, error)
        else:
            # Unexpected error, escalate
            raise
    ```
    """
    async def __call__(self, client_id: str, error: Exception) -> None:
        """Handle streaming error."""
        ...


# ============================================================================
# Type Aliases for Common Patterns
# ============================================================================

MessageProcessorType = MessageProcessor[Any, Any]
"""Type alias for MessageProcessor without generic constraints."""

ClientIdExtractorType = ClientIdExtractor[Any]
"""Type alias for ClientIdExtractor without generic constraints."""

PingMessageCreatorType = PingMessageCreator[Any]
"""Type alias for PingMessageCreator without generic constraints."""


# ============================================================================
# Type Guards and Validation
# ============================================================================

def is_valid_message_processor(func: Any) -> bool:
    """
    Runtime check if function matches MessageProcessor protocol.

    **Parameters**:
        func: Function to validate

    **Returns**:
        True if function signature matches protocol

    **Example**:
    ```python
    async def my_processor(client_id: str, msg: Command, queue: Queue) -> None:
        pass

    assert is_valid_message_processor(my_processor)  # ✅
    ```
    """
    if not callable(func):
        return False

    import inspect
    sig = inspect.signature(func)
    params = list(sig.parameters.values())

    return (
        len(params) == 3 and
        params[0].annotation in (str, inspect.Parameter.empty) and
        inspect.iscoroutinefunction(func)
    )


def is_valid_client_id_extractor(func: Any) -> bool:
    """
    Runtime check if function matches ClientIdExtractor protocol.

    **Parameters**:
        func: Function to validate

    **Returns**:
        True if function signature matches protocol

    **Example**:
    ```python
    def extract_id(msg: Command) -> str:
        return msg.client_id

    assert is_valid_client_id_extractor(extract_id)  # ✅
    ```
    """
    if not callable(func):
        return False

    import inspect
    sig = inspect.signature(func)
    params = list(sig.parameters.values())

    return (
        len(params) == 1 and
        sig.return_annotation in (str, inspect.Parameter.empty)
    )


def is_valid_ping_creator(func: Any) -> bool:
    """
    Runtime check if function matches PingMessageCreator protocol.

    **Parameters**:
        func: Function to validate

    **Returns**:
        True if function signature matches protocol

    **Example**:
    ```python
    def create_ping() -> Message:
        return Message(is_ping=True)

    assert is_valid_ping_creator(create_ping)  # ✅
    ```
    """
    if not callable(func):
        return False

    import inspect
    sig = inspect.signature(func)
    params = list(sig.parameters.values())

    return len(params) == 0


# ============================================================================
# Exports
# ============================================================================

__all__ = [
    # Type variables
    'TMessage',
    'TCommand',

    # Core protocols
    'MessageProcessor',
    'ClientIdExtractor',
    'PingMessageCreator',

    # Connection protocols
    'ConnectionCallback',
    'ErrorHandler',

    # Type aliases
    'MessageProcessorType',
    'ClientIdExtractorType',
    'PingMessageCreatorType',

    # Validation
    'is_valid_message_processor',
    'is_valid_client_id_extractor',
    'is_valid_ping_creator',
]
