# Command Response Registry

**Module**: `django_cfg.apps.integrations.grpc.services.streaming.response_registry`
**Status**: ✅ Production Ready
**Created**: 2025-11-12

## Purpose

Universal registry for implementing synchronous RPC-style command execution over bidirectional gRPC streams using existing CommandAck messages.

## Problem Solved

In bidirectional streaming, commands are sent asynchronously (fire-and-forget). To get immediate feedback about command execution, we need to wait for CommandAck response. This registry provides a clean way to correlate responses with commands using Future objects.

## Architecture

```
API Layer
   ↓ Send command with command_id
   ↓ Register Future in registry
   ↓
Streaming Connection → Bot
   ↓ Bot processes command
   ↓ Bot sends CommandAck back
   ↓
CommandAck Handler → Resolve Future
   ↓
API Layer receives CommandAck → Return to user
```

## Usage

### 1. In Command Sender (API/ViewSet)

```python
from django_cfg.apps.integrations.grpc.services.streaming import response_registry
from django_cfg.apps.integrations.grpc.services.commands.helpers import CommandBuilder

# Create command
command = CommandBuilder.create(pb2.Command, Converter)
command.start.CopyFrom(pb2.StartCommand())

# Register future BEFORE sending
future = await response_registry.register_command(
    command.command_id,
    timeout=5.0
)

# Send command
await client.send_command(command)

# Wait for response
try:
    ack = await asyncio.wait_for(future, timeout=5.0)
    print(f"Success: {ack.success}, Message: {ack.message}")
except asyncio.TimeoutError:
    print("Timeout waiting for response")
```

### 2. In CommandAck Handler

```python
from django_cfg.apps.integrations.grpc.services.streaming import response_registry

async def handle_command_ack(client_id, command_ack):
    # Resolve pending command
    await response_registry.resolve_command(
        command_ack.command_id,
        command_ack
    )
```

### 3. Wrapper Method (Recommended)

```python
class MyStreamingCommandClient(StreamingCommandClient):
    async def send_command_and_wait(self, command, timeout=5.0):
        """Send command and wait for response."""
        future = await response_registry.register_command(
            command.command_id,
            timeout=timeout
        )

        try:
            success = await self._send_command(command)
            if not success:
                await response_registry.cancel_command(
                    command.command_id,
                    "Client not connected"
                )
                raise ClientNotConnectedError()

            return await asyncio.wait_for(future, timeout=timeout)

        except asyncio.TimeoutError:
            await response_registry.cancel_command(
                command.command_id,
                "Timeout"
            )
            raise CommandTimeoutError()
```

## API Reference

### CommandResponseRegistry

#### Methods

**`register_command(command_id: str, timeout: float = 5.0) -> asyncio.Future`**

Register command for awaiting response.

- **Args**:
  - `command_id`: Unique command identifier
  - `timeout`: Timeout in seconds (for tracking only)
- **Returns**: Future that will be resolved with response
- **Raises**: None

**`resolve_command(command_id: str, response_data: Any) -> bool`**

Resolve pending command with response data.

- **Args**:
  - `command_id`: Command identifier
  - `response_data`: Response object (CommandAck protobuf or dict)
- **Returns**: True if resolved, False if not found
- **Thread-safe**: Yes (uses asyncio.Lock)

**`cancel_command(command_id: str, reason: str = "Cancelled") -> bool`**

Cancel pending command.

- **Args**:
  - `command_id`: Command identifier
  - `reason`: Cancellation reason
- **Returns**: True if cancelled, False if not found

**`get_pending_count() -> int`**

Get number of pending commands.

**`get_pending_commands() -> list[str]`**

Get list of pending command IDs.

**`cleanup_expired() -> int`**

Cleanup expired commands (timeout exceeded).

- **Returns**: Number of commands cleaned up
- **Usage**: Call periodically in background task

## Global Instance

```python
from django_cfg.apps.integrations.grpc.services.streaming import response_registry

# Singleton instance ready to use
await response_registry.register_command("cmd-123", timeout=5.0)
```

## Thread Safety

✅ **Thread-safe**: All methods use `asyncio.Lock` for concurrent access protection.

## Best Practices

1. **Always register BEFORE sending command**
   ```python
   future = await response_registry.register_command(cmd_id)  # First
   await client.send_command(command)  # Then
   ```

2. **Always cleanup on errors**
   ```python
   try:
       ack = await asyncio.wait_for(future, timeout=5.0)
   except asyncio.TimeoutError:
       await response_registry.cancel_command(cmd_id, "Timeout")
       raise
   ```

3. **Use wrapper methods** - Encapsulate registry logic in command client methods

4. **Set appropriate timeouts** - Different commands need different timeouts:
   - Start/Stop: 5s
   - Restart: 10s
   - Long operations: 30s+

5. **Periodic cleanup** (optional):
   ```python
   # In background task
   async def cleanup_expired_commands():
       while True:
           await asyncio.sleep(60)
           count = await response_registry.cleanup_expired()
           if count:
               logger.warning(f"Cleaned up {count} expired commands")
   ```

## Integration with BidirectionalStreamingService

This registry is designed to work seamlessly with `BidirectionalStreamingService`:

```python
from django_cfg.apps.integrations.grpc.services.streaming import (
    BidirectionalStreamingService,
    response_registry,
)

# In CommandAck handler
async def handle_command_ack(client_id, ack, output_queue):
    # Resolve registry
    await response_registry.resolve_command(ack.command_id, ack)

    # Continue with other logic
    await output_queue.put(response_message)
```

## Advantages

✅ **No proto changes** - Uses existing CommandAck messages
✅ **Universal** - Works with any streaming service
✅ **Type-safe** - Future resolved with actual protobuf
✅ **Timeout protection** - Automatic cleanup on timeout
✅ **Clean API** - Simple register/resolve pattern
✅ **Thread-safe** - Concurrent access protection

## Example: Trading Bots

See `apps/trading_bots/grpc/services/commands/base_client.py` for real-world implementation.

---

**Created for**: django-cfg universal gRPC components
**Used by**: stockapis trading_bots, future projects
