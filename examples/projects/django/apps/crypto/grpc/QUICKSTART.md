# Crypto gRPC Quick Start

**5-minute guide to add bidirectional streaming to crypto app**

Based on production patterns from `/apps/signals` and `/apps/trading_bots`.

## 📋 Prerequisites

- Django-CFG installed
- Proto compiler (`protoc`) installed
- Python gRPC packages installed

## 🚀 Quick Implementation (Copy-Paste Ready!)

### 1. Update Proto Files (2 min)

Update `services/proto/crypto_streaming.proto`:

```bash
cd apps/crypto/grpc/services/proto
cp /apps/signals/grpc/services/proto/common.proto ./
# Edit crypto_streaming.proto (use example from ARCHITECTURE_GUIDE.md)
bash generate_proto.sh
```

###2. Create Config (1 min)

`services/config.py`:

```python
from django_cfg.apps.integrations.grpc.services.streaming import StreamingConfig

class CryptoStreamingConfig(StreamingConfig):
    service_name = "crypto"
    centrifugo_auto_publish_messages = True
    centrifugo_channel_pattern = "crypto:{client_id}:updates"
    heartbeat_interval = 30
    heartbeat_timeout = 90
```

### 3. Create Callbacks (1 min)

`services/callbacks.py`:

```python
from functools import partial
from .generated import crypto_streaming_pb2 as pb2
from .proto.converters import CryptoProtobufConverter

def extract_client_id(message: pb2.ClientMessage):
    return message.client_id if message.client_id else None

def extract_heartbeat(message: pb2.ClientMessage):
    return message.heartbeat if message.HasField('heartbeat') else None

def handle_heartbeat_universal(client_id, heartbeat, metadata):
    pass  # Universal handling in BidirectionalStreamingService

def create_ping_command(converter: CryptoProtobufConverter):
    command = pb2.DjangoCommand()
    command.command_id = converter.generate_uuid()
    converter.set_timestamp(command)
    command.ping.CopyFrom(pb2.PingCommand(sequence=1))
    return command

async def process_client_message(client_id, message, output_queue, converter, streaming_service=None):
    from .handlers import handle_registration, handle_wallet_update
    message_type = message.WhichOneof('payload')

    if message_type == 'register':
        await handle_registration(client_id, message.register, converter)
    elif message_type == 'wallet_update':
        await handle_wallet_update(client_id, message.wallet_update, converter, None)
```

### 4. Update Server (1 min)

`services/server.py`:

```python
from django_cfg.apps.integrations.grpc.services.streaming import BidirectionalStreamingService
from .config import CryptoStreamingConfig
from .callbacks import *

class CryptoStreamingService(pb2_grpc.CryptoStreamingServiceServicer):
    def __init__(self):
        super().__init__()
        self._converter = CryptoProtobufConverter()

        self._streaming_service = BidirectionalStreamingService(
            config=CryptoStreamingConfig,
            message_processor=partial(process_client_message, converter=self._converter),
            client_id_extractor=extract_client_id,
            ping_message_creator=partial(create_ping_command, self._converter),
            heartbeat_extractor=extract_heartbeat,
            heartbeat_callback=handle_heartbeat_universal,
        )

    async def ConnectClient(self, request_iterator, context):
        async for command in self._streaming_service.handle_stream(request_iterator, context):
            yield command
```

### 5. Add grpc_handlers() Hook

`services/handlers/__init__.py`:

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

## ✅ Done! Test It

```bash
# Terminal 1: Start Django gRPC server
poetry run python manage.py rungrpc

# Terminal 2: Test client
poetry run python apps/crypto/grpc/examples/simple_client_test.py
```

## 📚 Next Steps

1. Read full [ARCHITECTURE_GUIDE.md](./ARCHITECTURE_GUIDE.md)
2. Check `/apps/signals/grpc` for complete examples
3. Check `/apps/trading_bots/grpc` for advanced patterns
4. Implement handlers in `services/handlers/`
5. Create commands in `services/commands/`
6. Add tests in `tests/`

## 🔥 Pro Tips

**Copy from signals/trading_bots:**
- ✅ Handler separation pattern
- ✅ Command client pattern
- ✅ Test infrastructure
- ✅ Callback functions

**Common mistakes:**
- ❌ Importing Django models at module level
- ❌ Not using `partial()` for converter
- ❌ Forgetting `grpc_handlers()` in handlers/__init__.py

**Remember:**
- Use `BidirectionalStreamingService` - don't reinvent the wheel!
- Centrifugo auto-publish = WebSocket for free
- Universal heartbeat/CommandAck = less code

---

**Time to implement**: ~5 minutes
**Lines of code**: ~100
**Based on**: Production patterns from signals/trading_bots
