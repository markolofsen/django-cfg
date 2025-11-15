# Crypto gRPC Commands

**Send commands to connected crypto clients via bidirectional streaming**

Based on `/apps/signals/grpc/services/commands/` and `/apps/trading_bots/grpc/services/commands/`

## 📋 Overview

Commands allow Django to control connected crypto clients in real-time:
- ⏸️  **Pause** - Temporarily pause wallet sync
- ▶️  **Resume** - Resume paused client
- 🏓 **Ping** - Health check
- 🔄 **Sync Wallets** - Request wallet sync for specific coins
- 📊 **Request Status** - Get client status and stats

## 🚀 Quick Usage

### Fire-and-Forget (Async)

```python
from apps.crypto.grpc.services.commands import StreamingCommandClient

# Create client
client = StreamingCommandClient(client_id="uuid-here")

# Send commands (async, no wait for response)
await client.pause_client(reason="Maintenance")
await client.resume_client()
await client.ping_client()
await client.sync_wallets(symbols=["BTC", "ETH"])
await client.request_status(include_stats=True)
```

### Wait for Response (Sync)

```python
# Send command and wait for CommandAck
ack = await client.pause_client_sync(reason="Maintenance", timeout=10.0)

if ack.success:
    print(f"✅ {ack.message}")
    print(f"Client status: {ack.current_status}")
else:
    print(f"❌ {ack.error}: {ack.message}")
```

## 📚 Available Commands

### 1. Pause Client

```python
# Async (fire-and-forget)
success = await client.pause_client(reason="Manual pause")

# Sync (wait for ack)
ack = await client.pause_client_sync(reason="Manual pause", timeout=5.0)
```

**Use case:** Temporarily stop wallet sync during maintenance.

### 2. Resume Client

```python
# Async
success = await client.resume_client(message="Maintenance complete")

# Sync
ack = await client.resume_client_sync(message="Maintenance complete", timeout=5.0)
```

**Use case:** Resume wallet sync after pause.

### 3. Ping Client

```python
# Async
success = await client.ping_client(sequence=1)

# Sync
ack = await client.ping_client_sync(sequence=1, timeout=5.0)
# Check ack.current_status for client health
```

**Use case:** Health check, connectivity test.

### 4. Sync Wallets

```python
# Sync all wallets
success = await client.sync_wallets()

# Sync specific coins
success = await client.sync_wallets(symbols=["BTC", "ETH", "USDT"])

# Sync with ack
ack = await client.sync_wallets_sync(symbols=["BTC"], timeout=10.0)
```

**Use case:** Trigger wallet balance update on demand.

### 5. Request Status

```python
# Basic status
success = await client.request_status()

# With detailed stats
success = await client.request_status(include_stats=True)

# Sync version
ack = await client.request_status_sync(include_stats=True, timeout=5.0)
# ack.message contains status details
```

**Use case:** Get current client state and statistics.

## 🏗️ Architecture

```
┌─────────────┐  StreamingCommandClient   ┌──────────────┐  gRPC Stream  ┌─────────────┐
│ Django View │ ─────────────────────────> │ gRPC Server  │ ────────────> │ Crypto      │
│ / API       │                            │ (Django)     │               │ Client      │
└─────────────┘                            └──────────────┘               └─────────────┘
                                                  ↓                              │
                                          [BidirectionalStreamingService]       │
                                                  ↓                              │
                                          [Command Queue]                        │
                                                  ↓                              ↓
                                          [Send DjangoCommand] ──────────> [Receive Command]
                                                  ↑                              │
                                          [Wait for CommandAck] <───────── [Send CommandAck]
```

## 🎯 Two Modes

### Async Mode (Fire-and-Forget)

```python
success = await client.pause_client(reason="test")
# Returns: bool (True if sent, False if client not connected)
# Does NOT wait for client response
```

**Pros:**
- Fast (no waiting)
- Non-blocking

**Cons:**
- Don't know if client executed
- No error details from client

**Use when:**
- Fire-and-forget acceptable
- Just need to send command
- Don't care about execution result

### Sync Mode (Wait for Ack)

```python
ack = await client.pause_client_sync(reason="test", timeout=5.0)
# Returns: CommandAck protobuf
# Waits for client to process and send CommandAck back
```

**Pros:**
- Know if client executed successfully
- Get error details if failed
- Get current client status

**Cons:**
- Slower (waits for response)
- Can timeout if client slow

**Use when:**
- Need confirmation
- Need error details
- Need updated client status
- Critical operations

## 💡 Best Practices

### 1. Use Sync for Critical Commands

```python
# ❌ BAD - fire-and-forget for critical operation
await client.sync_wallets(symbols=["BTC"])  # Did it work? Unknown!

# ✅ GOOD - wait for confirmation
ack = await client.sync_wallets_sync(symbols=["BTC"], timeout=10.0)
if not ack.success:
    logger.error(f"Wallet sync failed: {ack.error}")
    raise Exception(f"Failed to sync: {ack.message}")
```

### 2. Handle Timeouts

```python
from django_cfg.apps.integrations.grpc.services.commands.base import CommandTimeoutError

try:
    ack = await client.pause_client_sync(timeout=5.0)
except CommandTimeoutError:
    logger.warning("Client did not respond within 5s")
    # Maybe client is slow or busy - retry with longer timeout
    ack = await client.pause_client_sync(timeout=15.0)
```

### 3. Check Client Connection First

```python
from apps.crypto.grpc.services.commands import get_streaming_service

# Check if client connected
service = get_streaming_service("crypto")
if not service or not service.is_client_connected(client_id):
    return {"error": "Client not connected"}

# Now send command
client = StreamingCommandClient(client_id)
ack = await client.pause_client_sync()
```

### 4. Use in ViewSets

```python
from rest_framework import viewsets
from rest_framework.decorators import action
from apps.crypto.grpc.services.commands import StreamingCommandClient

class ClientViewSet(viewsets.ViewSet):
    @action(detail=True, methods=['post'])
    def pause(self, request, pk=None):
        """Pause crypto client."""
        client_id = pk

        # Create command client
        cmd_client = StreamingCommandClient(client_id)

        # Send sync command
        ack = await cmd_client.pause_client_sync(
            reason=request.data.get('reason', 'Paused via API'),
            timeout=10.0
        )

        return Response({
            'success': ack.success,
            'message': ack.message,
            'status': ack.current_status
        })
```

## 🔧 Implementation Details

### Command Flow

1. **Create Command**
   ```python
   command = CommandBuilder.create(pb2.DjangoCommand, CryptoProtobufConverter)
   command.pause.CopyFrom(pb2.PauseClientCommand(reason="test"))
   ```

2. **Send via gRPC**
   ```python
   await client._send_command(command)
   ```

3. **Client Receives**
   - Client gets command via bidirectional stream
   - Processes command (pause wallet sync, etc.)

4. **Client Sends Ack** (Sync mode only)
   ```python
   # Client code
   ack = pb2.CommandAck(
       command_id=command.command_id,
       success=True,
       message="Paused successfully",
       current_status=pb2.CLIENT_STATUS_PAUSED
   )
   await stream.write(client_message_with_ack)
   ```

5. **Django Receives Ack**
   - BidirectionalStreamingService extracts CommandAck
   - Resolves waiting Future
   - Returns ack to caller

### Cross-Process Support

Commands work across processes:

```
┌────────────┐  HTTP/REST   ┌────────────┐  gRPC RPC    ┌─────────────┐  Stream   ┌────────┐
│ Django Web │ ───────────> │ Django     │ ───────────> │ gRPC Server │ ────────> │ Client │
│ (ASGI)     │              │ gRPC       │              │ (rungrpc)   │           │        │
└────────────┘              │ Client     │              └─────────────┘           └────────┘
                            └────────────┘                     │                       │
                                                               │    CommandAck         │
                                                               │ <──────────────────── │
```

## 🧪 Testing

### Unit Test

```python
import pytest
from apps.crypto.grpc.services.commands import StreamingCommandClient

@pytest.mark.asyncio
async def test_pause_command():
    client = StreamingCommandClient("test-client-id")

    # Mock gRPC channel
    with patch_grpc_channel():
        ack = await client.pause_client_sync(reason="test")

    assert ack.success
    assert "paused" in ack.message.lower()
```

### Integration Test

```bash
# Start gRPC server
poetry run python manage.py rungrpc

# Run test client
poetry run python apps/crypto/grpc/tests/test_client_commands.py
```

## 📖 Reference

**Based on:**
- `/apps/signals/grpc/services/commands/` - Simpler implementation
- `/apps/trading_bots/grpc/services/commands/` - Advanced features

**Key files:**
- `base_client.py` - CryptoStreamingCommandClient adapter
- `pause.py` - Pause command
- `resume.py` - Resume command
- `ping.py` - Ping command
- `sync_wallets.py` - Sync wallets command (crypto-specific)
- `request_status.py` - Request status command

**See also:**
- [ARCHITECTURE_GUIDE.md](../../ARCHITECTURE_GUIDE.md)
- [BIDIRECTIONAL_STREAMING.md](../../BIDIRECTIONAL_STREAMING.md)

---

**Created:** 2025-11-14
**Status:** Production-Ready
**Pattern:** Maximum decomposition (one command = one file)
