# Crypto gRPC Architecture Guide

**Based on best practices from `signals` and `trading_bots` gRPC implementations**

## 📋 Table of Contents

1. [Overview](#overview)
2. [Directory Structure](#directory-structure)
3. [Key Components](#key-components)
4. [Implementation Steps](#implementation-steps)
5. [Patterns and Best Practices](#patterns-and-best-practices)

## Overview

This guide demonstrates how to implement a production-ready gRPC service with:

- ✅ **Bidirectional Streaming** - Real-time two-way communication
- ✅ **Handler Separation** - Clean code organization
- ✅ **Command System** - Send commands to connected clients
- ✅ **Centrifugo Integration** - Auto-publish to WebSocket channels
- ✅ **Universal Patterns** - Heartbeat, CommandAck, error handling
- ✅ **Service Discovery** - Auto-registration via `grpc_handlers()`

## Directory Structure

```
apps/crypto/grpc/
├── __init__.py
├── README.md
├── ARCHITECTURE_GUIDE.md
│
├── examples/                     # Usage examples
│   ├── __init__.py
│   └── simple_client_test.py     # Example client
│
├── services/
│   ├── __init__.py
│   ├── server.py                 # Main gRPC service
│   ├── config.py                 # BidirectionalStreamingConfig
│   ├── callbacks.py              # Extract/transform functions
│   │
│   ├── proto/                    # Protobuf definitions
│   │   ├── __init__.py
│   │   ├── common.proto          # Common messages (reusable)
│   │   ├── crypto_streaming.proto # Main service definition
│   │   ├── converters.py         # Proto ↔ Django conversions
│   │   └── generate_proto.sh    # Codegen script
│   │
│   ├── generated/                # Auto-generated (don't edit!)
│   │   ├── __init__.py
│   │   ├── common_pb2.py
│   │   ├── common_pb2.pyi
│   │   ├── common_pb2_grpc.py
│   │   ├── crypto_streaming_pb2.py
│   │   ├── crypto_streaming_pb2.pyi
│   │   └── crypto_streaming_pb2_grpc.py
│   │
│   ├── handlers/                 # Message handlers
│   │   ├── __init__.py           # grpc_handlers() for discovery
│   │   ├── registration.py       # Handle client registration
│   │   ├── wallet_update.py      # Handle wallet updates
│   │   ├── transaction.py        # Handle transactions
│   │   ├── status.py             # Handle status updates
│   │   ├── error.py              # Handle error reports
│   │   └── log.py                # Handle log entries
│   │
│   └── commands/                 # Commands to send to clients
│       ├── __init__.py           # StreamingCommandClient
│       ├── base_client.py        # CryptoStreamingCommandClient
│       ├── pause.py              # Pause client
│       ├── resume.py             # Resume client
│       ├── ping.py               # Ping/pong
│       ├── sync_wallets.py       # Request wallet sync
│       └── request_status.py     # Request status
│
└── tests/                        # Test infrastructure
    ├── __init__.py
    ├── run_tests.sh              # Test runner script
    ├── test_client_registration.py
    ├── test_client_commands.py
    ├── test_centrifugo_integration.py
    └── results/                  # Test results (JSON + logs)
```

## Key Components

### 1. Proto Files (`services/proto/`)

#### `common.proto` - Reusable Messages

```protobuf
syntax = "proto3";
package crypto;

import "google/protobuf/timestamp.proto";

// Common status enum
enum ClientStatus {
  CLIENT_STATUS_UNKNOWN = 0;
  CLIENT_STATUS_ACTIVE = 1;
  CLIENT_STATUS_PAUSED = 2;
  CLIENT_STATUS_ERROR = 3;
  CLIENT_STATUS_STOPPED = 4;
}

// Command acknowledgment
message CommandAck {
  string command_id = 1;
  bool success = 2;
  string message = 3;
  string error = 4;
  ClientStatus current_status = 5;
  google.protobuf.Timestamp timestamp = 6;
}
```

#### `crypto_streaming.proto` - Main Service

```protobuf
syntax = "proto3";
package crypto;

import "google/protobuf/timestamp.proto";
import "common.proto";

// ============================================================================
// Crypto Streaming Service
// ============================================================================

service CryptoStreamingService {
  // Bidirectional streaming RPC
  rpc ConnectClient(stream ClientMessage) returns (stream DjangoCommand);

  // Send command to specific client
  rpc SendCommandToClient(SendCommandRequest) returns (SendCommandResponse);

  // Execute command synchronously (wait for CommandAck)
  rpc ExecuteCommandSync(SendCommandRequest) returns (CommandAck);
}

// ============================================================================
// Client → Django Messages
// ============================================================================

message ClientMessage {
  string client_id = 1;       // Unique client UUID
  string message_id = 2;       // Message tracking UUID
  google.protobuf.Timestamp timestamp = 3;

  oneof payload {
    ClientRegistration register = 10;
    WalletUpdate wallet_update = 11;
    TransactionReport transaction = 12;
    StatusUpdate status = 13;
    HeartbeatUpdate heartbeat = 14;
    ErrorReport error = 15;
    LogEntry log = 16;
    CommandAck command_ack = 17;
  }
}

message ClientRegistration {
  string client_name = 1;
  string client_type = 2;
  string version = 3;
  string api_url = 4;
}

message WalletUpdate {
  string wallet_id = 1;
  string symbol = 2;
  string balance_available = 3;
  string balance_locked = 4;
  google.protobuf.Timestamp last_sync = 5;
}

message TransactionReport {
  string transaction_id = 1;
  string type = 2;              // "deposit", "withdrawal", "transfer"
  string symbol = 3;
  string amount = 4;
  string status = 5;
  string details = 6;
}

message StatusUpdate {
  ClientStatus status = 1;
  string details = 2;
}

message HeartbeatUpdate {
  // Empty message - presence is enough
}

message ErrorReport {
  string severity = 1;
  string message = 2;
  string traceback = 3;
}

message LogEntry {
  string level = 1;
  string message = 2;
  string extra_data = 3;
}

// ============================================================================
// Django → Client Commands
// ============================================================================

message DjangoCommand {
  string command_id = 1;
  google.protobuf.Timestamp timestamp = 2;

  oneof command {
    PingCommand ping = 10;
    PauseClientCommand pause = 11;
    ResumeClientCommand resume = 12;
    SyncWalletsCommand sync_wallets = 13;
    RequestStatusCommand request_status = 14;
  }
}

message PingCommand {
  int32 sequence = 1;
}

message PauseClientCommand {
  string reason = 1;
}

message ResumeClientCommand {
  string message = 1;
}

message SyncWalletsCommand {
  repeated string symbols = 1;  // Empty = sync all
}

message RequestStatusCommand {
  bool include_stats = 1;
}

// ============================================================================
// Command Send/Receive
// ============================================================================

message SendCommandRequest {
  string client_id = 1;
  DjangoCommand command = 2;
}

message SendCommandResponse {
  bool success = 1;
  string error = 2;
}
```

### 2. Config (`services/config.py`)

```python
"""Crypto streaming service configuration."""
from django_cfg.apps.integrations.grpc.services.streaming import StreamingConfig


class CryptoStreamingConfig(StreamingConfig):
    """
    Configuration for CryptoStreamingService.

    Extends universal StreamingConfig from django-cfg.
    """

    # Service identification
    service_name = "crypto"

    # Centrifugo auto-publishing
    centrifugo_auto_publish_messages = True
    centrifugo_channel_pattern = "crypto:{client_id}:updates"
    centrifugo_publish_all_channel = "crypto:all"

    # Heartbeat configuration
    heartbeat_interval = 30  # seconds
    heartbeat_timeout = 90   # 3x interval

    # Ping configuration
    enable_ping = True
    ping_interval = 60  # seconds

    # Client management
    client_disconnect_grace = 5  # seconds
```

### 3. Callbacks (`services/callbacks.py`)

```python
"""Callback functions for CryptoStreamingService."""
import logging
from typing import Optional, Dict, Any
from google.protobuf.message import Message

from .generated import crypto_streaming_pb2 as pb2
from .proto.converters import CryptoProtobufConverter

logger = logging.getLogger(__name__)


# ============================================================================
# Client ID Extraction
# ============================================================================

def extract_client_id(message: pb2.ClientMessage) -> Optional[str]:
    """Extract client_id from ClientMessage."""
    return message.client_id if message.client_id else None


# ============================================================================
# Heartbeat Extraction
# ============================================================================

def extract_heartbeat(message: pb2.ClientMessage) -> Optional[Message]:
    """
    Extract HeartbeatUpdate from ClientMessage.

    Returns HeartbeatUpdate message or None.
    """
    if message.HasField('heartbeat'):
        return message.heartbeat
    return None


def handle_heartbeat_universal(client_id: str, heartbeat: Message, metadata: Dict[str, Any]):
    """
    Universal heartbeat handler.

    Called by BidirectionalStreamingService when heartbeat received.
    """
    logger.debug(f"💓 Heartbeat from {client_id[:8]}...")


# ============================================================================
# CommandAck Extraction
# ============================================================================

def extract_command_ack(message: pb2.ClientMessage) -> Optional[pb2.CommandAck]:
    """Extract CommandAck from ClientMessage."""
    if message.HasField('command_ack'):
        return message.command_ack
    return None


# ============================================================================
# Ping Command Creation
# ============================================================================

def create_ping_command(converter: CryptoProtobufConverter) -> pb2.DjangoCommand:
    """
    Create ping command for health check.

    Called by BidirectionalStreamingService during ping cycle.
    """
    command = pb2.DjangoCommand()
    command.command_id = converter.generate_uuid()
    converter.set_timestamp(command)
    command.ping.CopyFrom(pb2.PingCommand(sequence=1))
    return command


# ============================================================================
# Message Processing
# ============================================================================

async def process_client_message(
    client_id: str,
    message: pb2.ClientMessage,
    output_queue,
    converter: CryptoProtobufConverter,
    streaming_service=None
):
    """
    Process client message and dispatch to handlers.

    Called by BidirectionalStreamingService for each incoming message.
    """
    # Import handlers here to avoid circular imports
    from .handlers import (
        handle_registration,
        handle_wallet_update,
        handle_transaction,
        handle_status_update,
        handle_error_report,
        handle_log_entry,
    )

    # Determine message type
    message_type = message.WhichOneof('payload')

    if not message_type:
        logger.warning(f"Empty message from {client_id[:8]}...")
        return

    # Get client metadata from streaming service
    metadata = None
    if streaming_service:
        connections = streaming_service.get_active_connections()
        metadata = connections.get(client_id, {})

    # Dispatch to appropriate handler
    try:
        if message_type == 'register':
            await handle_registration(client_id, message.register, converter)

        elif message_type == 'wallet_update':
            await handle_wallet_update(client_id, message.wallet_update, converter, metadata)

        elif message_type == 'transaction':
            await handle_transaction(client_id, message.transaction, converter, metadata)

        elif message_type == 'status':
            await handle_status_update(client_id, message.status, converter, metadata)

        elif message_type == 'error':
            await handle_error_report(client_id, message.error, converter)

        elif message_type == 'log':
            await handle_log_entry(client_id, message.log, converter)

        elif message_type == 'heartbeat':
            # Handled universally by BidirectionalStreamingService
            pass

        elif message_type == 'command_ack':
            # Handled universally by BidirectionalStreamingService
            pass

        else:
            logger.warning(f"Unknown message type: {message_type}")

    except Exception as e:
        logger.exception(f"Error processing {message_type} from {client_id[:8]}: {e}")
```

### 4. Server (`services/server.py`)

```python
"""
Crypto Streaming gRPC Server.

Minimal service using BidirectionalStreamingService from django-cfg.
"""
import logging
from typing import AsyncIterator
from functools import partial

import grpc
from django_cfg.apps.integrations.grpc.services.streaming import BidirectionalStreamingService

from .generated import crypto_streaming_pb2 as pb2
from .generated import crypto_streaming_pb2_grpc as pb2_grpc
from .proto.converters import CryptoProtobufConverter
from .config import CryptoStreamingConfig
from .callbacks import (
    extract_client_id,
    extract_heartbeat,
    extract_command_ack,
    handle_heartbeat_universal,
    create_ping_command,
    process_client_message,
)

logger = logging.getLogger(__name__)


class CryptoStreamingService(pb2_grpc.CryptoStreamingServiceServicer):
    """
    Crypto streaming gRPC service.

    Delegates all bidirectional streaming logic to BidirectionalStreamingService.
    """

    def __init__(self):
        """Initialize service with BidirectionalStreamingService."""
        super().__init__()

        # Converter for protobuf ↔ Django model transformations
        self._converter = CryptoProtobufConverter()

        # Create BidirectionalStreamingService with callbacks
        self._streaming_service = BidirectionalStreamingService(
            config=CryptoStreamingConfig,
            message_processor=partial(
                process_client_message,
                converter=self._converter,
            ),
            client_id_extractor=extract_client_id,
            ping_message_creator=partial(create_ping_command, self._converter),
            command_ack_extractor=extract_command_ack,
            heartbeat_extractor=extract_heartbeat,
            heartbeat_callback=handle_heartbeat_universal,
        )

        # Use logger from streaming service
        self.logger = self._streaming_service.logger

        self.logger.info(
            f"CryptoStreamingService initialized "
            f"(Centrifugo auto-publish: {CryptoStreamingConfig.centrifugo_auto_publish_messages})"
        )

    async def ConnectClient(
        self,
        request_iterator: AsyncIterator[pb2.ClientMessage],
        context: grpc.aio.ServicerContext
    ) -> AsyncIterator[pb2.DjangoCommand]:
        """
        Main bidirectional streaming RPC.

        Delegates to BidirectionalStreamingService.
        """
        async for command in self._streaming_service.handle_stream(request_iterator, context):
            yield command

    async def SendCommandToClient(
        self,
        request: pb2.SendCommandRequest,
        context: grpc.aio.ServicerContext
    ) -> pb2.SendCommandResponse:
        """Send command to active client connection."""
        client_id = request.client_id

        success = await self._streaming_service.send_to_client(
            client_id=client_id,
            command=request.command
        )

        if success:
            return pb2.SendCommandResponse(success=True)
        else:
            return pb2.SendCommandResponse(
                success=False,
                error=f"Client {client_id} not connected"
            )

    async def ExecuteCommandSync(
        self,
        request: pb2.SendCommandRequest,
        context: grpc.aio.ServicerContext
    ) -> pb2.CommandAck:
        """
        Execute command synchronously and wait for CommandAck.

        Used by management commands and ASGI for synchronous command execution.
        """
        client_id = request.client_id
        command = request.command

        try:
            ack = await self._streaming_service.send_command_and_wait(
                client_id=client_id,
                command=command,
                timeout=15.0  # Server timeout for CommandAck
            )
            return ack

        except Exception as e:
            # Return error CommandAck
            error_ack = pb2.CommandAck()
            error_ack.command_id = command.command_id
            error_ack.success = False
            error_ack.error = str(type(e).__name__)
            error_ack.message = str(e)
            return error_ack

    def get_active_clients(self):
        """Get list of active client IDs."""
        return self._streaming_service.get_active_clients()

    def is_client_connected(self, client_id: str) -> bool:
        """Check if specific client is connected."""
        return self._streaming_service.is_client_connected(client_id)
```

### 5. Handlers (`services/handlers/__init__.py`)

```python
"""
Crypto client message handlers.

Each handler is a pure async function that processes a specific message type.

This module also provides grpc_handlers() for django-cfg ServiceDiscovery.
"""
import logging

# Handler functions
from .registration import handle_registration
from .wallet_update import handle_wallet_update
from .transaction import handle_transaction
from .status import handle_status_update
from .error import handle_error_report
from .log import handle_log_entry

__all__ = [
    'handle_registration',
    'handle_wallet_update',
    'handle_transaction',
    'handle_status_update',
    'handle_error_report',
    'handle_log_entry',
    'grpc_handlers',  # For ServiceDiscovery
]

logger = logging.getLogger(__name__)


# ============================================================================
# ServiceDiscovery Hook
# ============================================================================

def grpc_handlers(server):
    """
    Auto-discovered by django-cfg ServiceDiscovery.
    Registers CryptoStreamingService to gRPC server.

    IMPORTANT: This function is called EARLY during Django startup,
    so we must delay imports of Django models until the server is actually running.

    NO Django model imports allowed here!
    """
    logger.info("🔧 crypto/grpc_handlers called!")
    logger.info(f"   server = {server}")

    # Import here to avoid circular imports
    from ..server import CryptoStreamingService
    from ..generated import crypto_streaming_pb2_grpc

    if server is not None:
        # Server provided - manually register the service
        logger.info("✅ grpc_handlers called with server - registering CryptoStreamingService")

        servicer = CryptoStreamingService()
        logger.info(f"🔧 Servicer created: {servicer}")

        crypto_streaming_pb2_grpc.add_CryptoStreamingServiceServicer_to_server(servicer, server)

        logger.info("✅ Registered CryptoStreamingService (bidirectional)")
    else:
        # Discovery mode - just return the list for discovery
        logger.info("ℹ️  grpc_handlers called for discovery (server=None)")

    # Return list for ServiceDiscovery.discover_services() compatibility
    result = [(CryptoStreamingService, crypto_streaming_pb2_grpc.add_CryptoStreamingServiceServicer_to_server)]
    return result
```

## Implementation Steps

### Step 1: Proto Files

1. Create `common.proto` with reusable messages
2. Create `crypto_streaming.proto` with service definition
3. Run `generate_proto.sh` to create Python code

### Step 2: Config & Callbacks

1. Create `config.py` with `CryptoStreamingConfig`
2. Create `callbacks.py` with extraction/processing functions

### Step 3: Handlers

1. Create handler for each message type in `handlers/`
2. Update `handlers/__init__.py` with `grpc_handlers()`

### Step 4: Server

1. Create `server.py` with `CryptoStreamingService`
2. Use `BidirectionalStreamingService` as delegation target

### Step 5: Commands

1. Create `base_client.py` with `CryptoStreamingCommandClient`
2. Create command functions in `commands/`

### Step 6: Tests

1. Create `run_tests.sh`
2. Create test files for registration, commands, integration
3. Create `results/` directory for test output

## Patterns and Best Practices

### ✅ Use BidirectionalStreamingService

Delegate all streaming logic to django-cfg's universal implementation:

```python
self._streaming_service = BidirectionalStreamingService(
    config=CryptoStreamingConfig,
    message_processor=partial(process_client_message, converter=self._converter),
    client_id_extractor=extract_client_id,
    ping_message_creator=partial(create_ping_command, self._converter),
    # ... more callbacks
)
```

### ✅ Separate Concerns

- **server.py** - Service definition only
- **handlers/** - Message processing logic
- **commands/** - Command sending logic
- **callbacks.py** - Extract/transform functions
- **proto/** - Protobuf definitions

### ✅ Use Partial for Converter

Pass converter via `functools.partial`:

```python
message_processor=partial(
    process_client_message,
    converter=self._converter,
)
```

### ✅ Import Django Models Late

Never import Django models at module level in handlers/__init__.py:

```python
# ❌ BAD - imports at module level
from apps.crypto.models import Wallet

# ✅ GOOD - imports inside function
def handle_wallet_update(...):
    from apps.crypto.models import Wallet
    # ...
```

### ✅ Use grpc_handlers() for Discovery

Implement `grpc_handlers()` in `handlers/__init__.py` for auto-registration:

```python
def grpc_handlers(server):
    """Auto-discovered by ServiceDiscovery."""
    from ..server import CryptoStreamingService
    from ..generated import crypto_streaming_pb2_grpc

    if server is not None:
        servicer = CryptoStreamingService()
        crypto_streaming_pb2_grpc.add_CryptoStreamingServiceServicer_to_server(servicer, server)

    return [(CryptoStreamingService, crypto_streaming_pb2_grpc.add_CryptoStreamingServiceServicer_to_server)]
```

### ✅ Use StreamingCommandClient Pattern

Create thin adapter extending universal base:

```python
from django_cfg.apps.integrations.grpc.services.commands.base import StreamingCommandClient

class CryptoStreamingCommandClient(StreamingCommandClient[pb2.DjangoCommand]):
    stub_class = pb2_grpc.CryptoStreamingServiceStub
    request_class = pb2.SendCommandRequest
    rpc_method_name = "SendCommandToClient"
    client_id_field = "client_id"
```

### ✅ Centrifugo Auto-Publishing

Enable in config for automatic WebSocket broadcasting:

```python
class CryptoStreamingConfig(StreamingConfig):
    centrifugo_auto_publish_messages = True
    centrifugo_channel_pattern = "crypto:{client_id}:updates"
```

---

**Created**: 2025-11-14
**Based on**: `apps/signals` and `apps/trading_bots` implementations
**Status**: Production-Ready Pattern
