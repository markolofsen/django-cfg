# Bidirectional Streaming Pattern

**Complete guide to add bidirectional streaming to crypto gRPC service**

## 🎯 Why Bidirectional Streaming?

Current crypto service has:
- ✅ Unary RPC (GetCoin, ListCoins, etc.)
- ✅ Server-side streaming (StreamPrices)

Add bidirectional streaming for:
- 🔄 **Real-time client updates** - Wallets, transactions from external clients
- 📡 **Command & Control** - Send commands to connected clients
- 💓 **Heartbeat monitoring** - Know when clients disconnect
- 🎯 **CommandAck tracking** - Wait for client confirmation

## 📚 Learn from Production Examples

### Start Here: `/apps/signals/grpc`

**Simpler, cleaner implementation**
- telegram-spy → Django
- Provider registration
- Signal reports
- Basic commands (pause/resume/ping)

```bash
# Study this first!
cd /apps/signals/grpc
cat services/server.py
cat services/handlers/__init__.py
cat services/proto/signal_streaming_service.proto
```

### Advanced: `/apps/trading_bots/grpc`

**More complex, production-hardened**
- Trading bots → Django
- Complex execution reports
- Position management
- Advanced commands (start/stop/restart/config)
- Singleton pattern for shared registry

```bash
# Study after signals
cd /apps/trading_bots/grpc
cat services/server.py
cat services/handlers/__init__.py
```

## 🚀 Implementation Checklist

### Phase 1: Proto Files (30 min)

- [ ] Copy `common.proto` from `/apps/signals/grpc/services/proto/`
- [ ] Create `crypto_streaming.proto` (see ARCHITECTURE_GUIDE.md)
- [ ] Run `generate_proto.sh`
- [ ] Verify generated files in `generated/`

### Phase 2: Configuration (10 min)

- [ ] Create `services/config.py` with `CryptoStreamingConfig`
- [ ] Set Centrifugo channels
- [ ] Configure heartbeat/ping intervals

### Phase 3: Callbacks (20 min)

- [ ] Create `services/callbacks.py`
- [ ] Implement `extract_client_id()`
- [ ] Implement `extract_heartbeat()`
- [ ] Implement `extract_command_ack()`
- [ ] Implement `create_ping_command()`
- [ ] Implement `process_client_message()`

### Phase 4: Handlers (30 min)

- [ ] Create `services/handlers/registration.py`
- [ ] Create `services/handlers/wallet_update.py`
- [ ] Create `services/handlers/transaction.py`
- [ ] Create `services/handlers/status.py`
- [ ] Update `services/handlers/__init__.py` with `grpc_handlers()`

### Phase 5: Server (15 min)

- [ ] Create new `CryptoStreamingService` class
- [ ] Use `BidirectionalStreamingService` as delegate
- [ ] Implement `ConnectClient()` RPC
- [ ] Implement `SendCommandToClient()` RPC
- [ ] Implement `ExecuteCommandSync()` RPC

### Phase 6: Commands (30 min)

- [ ] Create `services/commands/base_client.py`
- [ ] Create `services/commands/pause.py`
- [ ] Create `services/commands/resume.py`
- [ ] Create `services/commands/ping.py`
- [ ] Create `services/commands/sync_wallets.py`

### Phase 7: Tests (45 min)

- [ ] Copy `run_tests.sh` from `/apps/signals/grpc/tests/`
- [ ] Create `test_client_registration.py`
- [ ] Create `test_client_commands.py`
- [ ] Create `test_centrifugo_integration.py`
- [ ] Run and verify tests pass

### Phase 8: Examples (20 min)

- [ ] Create `examples/simple_client_test.py`
- [ ] Test registration
- [ ] Test sending wallet updates
- [ ] Test receiving commands

## 📂 File Creation Order

```bash
# 1. Proto (do first!)
cd apps/crypto/grpc/services/proto
cp /apps/signals/grpc/services/proto/common.proto ./
nano crypto_streaming.proto  # Use ARCHITECTURE_GUIDE.md template
bash generate_proto.sh

# 2. Config & Callbacks
cd ..
nano config.py          # CryptoStreamingConfig
nano callbacks.py       # All callback functions

# 3. Handlers
cd handlers
nano registration.py    # handle_registration()
nano wallet_update.py   # handle_wallet_update()
nano transaction.py     # handle_transaction()
nano status.py          # handle_status_update()
nano error.py           # handle_error_report()
nano log.py             # handle_log_entry()
nano __init__.py        # grpc_handlers() + exports

# 4. Server
cd ..
nano server.py          # CryptoStreamingService

# 5. Commands
cd commands
nano base_client.py     # CryptoStreamingCommandClient
nano pause.py
nano resume.py
nano ping.py
nano sync_wallets.py
nano __init__.py        # StreamingCommandClient + exports

# 6. Tests
cd ../../tests
cp /apps/signals/grpc/tests/run_tests.sh ./
nano test_client_registration.py
nano test_client_commands.py
nano test_centrifugo_integration.py

# 7. Examples
cd ../examples
nano simple_client_test.py
```

## 🎓 Key Patterns to Copy

### Pattern 1: BidirectionalStreamingService Delegation

```python
# From signals/server.py
class CryptoStreamingService(pb2_grpc.CryptoStreamingServiceServicer):
    def __init__(self):
        self._streaming_service = BidirectionalStreamingService(
            config=CryptoStreamingConfig,
            message_processor=partial(process_client_message, converter=self._converter),
            client_id_extractor=extract_client_id,
            # ... more callbacks
        )

    async def ConnectClient(self, request_iterator, context):
        async for command in self._streaming_service.handle_stream(request_iterator, context):
            yield command
```

### Pattern 2: Handler Separation

```python
# From signals/handlers/signal.py
async def handle_signal_report(
    provider_id: str,
    report: pb2.SignalReport,
    converter: SignalProtobufConverter,
    metadata: Optional[Dict[str, Any]]
):
    """Pure async function - no class, no state."""
    from apps.signals.models import Signal  # Late import!

    signal_data = await converter.signal_report_to_signal_data_async(
        provider_id=provider_id,
        provider_info=metadata,
        report=report
    )

    signal = await Signal.objects.acreate(**signal_data)
    # ... Centrifugo publish handled by BidirectionalStreamingService!
```

### Pattern 3: grpc_handlers() Hook

```python
# From signals/handlers/__init__.py
def grpc_handlers(server):
    """Auto-discovered by ServiceDiscovery."""
    from ..server import CryptoStreamingService
    from ..generated import crypto_streaming_pb2_grpc

    if server is not None:
        servicer = CryptoStreamingService()
        crypto_streaming_pb2_grpc.add_CryptoStreamingServiceServicer_to_server(servicer, server)

    return [(CryptoStreamingService, crypto_streaming_pb2_grpc.add_CryptoStreamingServiceServicer_to_server)]
```

### Pattern 4: Command Client

```python
# From signals/commands/base_client.py
class CryptoStreamingCommandClient(StreamingCommandClient[pb2.DjangoCommand]):
    stub_class = pb2_grpc.CryptoStreamingServiceStub
    request_class = pb2.SendCommandRequest
    rpc_method_name = "SendCommandToClient"
    client_id_field = "client_id"

    def __init__(self, client_id: str, model=None, **kwargs):
        super().__init__(client_id=client_id, **kwargs)
        self.client = self.model = model
```

### Pattern 5: Test Infrastructure

```python
# From signals/tests/test_provider_registration.py
async def main():
    provider_id = str(uuid.uuid4())

    async with grpc.aio.insecure_channel('localhost:50051') as channel:
        stub = pb2_grpc.CryptoStreamingServiceStub(channel)
        stream = stub.ConnectClient()

        # Send registration
        msg = pb2.ClientMessage(
            client_id=provider_id,
            message_id=str(uuid.uuid4()),
            timestamp=current_timestamp()
        )
        msg.register.CopyFrom(pb2.ClientRegistration(
            client_name="test-client",
            client_type="wallet-sync",
            version="1.0.0"
        ))

        await stream.write(msg)
        await stream.done_writing()

        # Wait for commands
        command = await stream.read()
        assert command is not None
```

## ⚠️ Common Mistakes

### ❌ Mistake 1: Django Models at Module Level

```python
# BAD - crashes on startup
from apps.crypto.models import Wallet

def grpc_handlers(server):
    # ...
```

**Fix:** Import inside functions
```python
# GOOD
def handle_wallet_update(...):
    from apps.crypto.models import Wallet
    # ...
```

### ❌ Mistake 2: Not Using Partial for Converter

```python
# BAD - converter not available in callback
self._streaming_service = BidirectionalStreamingService(
    message_processor=process_client_message,  # Missing converter!
)
```

**Fix:** Use `functools.partial`
```python
# GOOD
from functools import partial

self._streaming_service = BidirectionalStreamingService(
    message_processor=partial(process_client_message, converter=self._converter),
)
```

### ❌ Mistake 3: Forgetting grpc_handlers()

```python
# BAD - service not discovered
# handlers/__init__.py has no grpc_handlers() function
```

**Fix:** Add discovery hook
```python
# GOOD
def grpc_handlers(server):
    """Auto-discovered by ServiceDiscovery."""
    # ...
```

### ❌ Mistake 4: Reinventing Streaming Logic

```python
# BAD - 200 lines of complex streaming code
async def ConnectClient(self, request_iterator, context):
    clients = {}
    queues = {}
    # ... complex logic ...
```

**Fix:** Delegate to BidirectionalStreamingService
```python
# GOOD - 2 lines
async def ConnectClient(self, request_iterator, context):
    async for command in self._streaming_service.handle_stream(request_iterator, context):
        yield command
```

## 🔥 Pro Tips

### Tip 1: Copy Files, Then Adapt

```bash
# Don't write from scratch - copy working code!
cp /apps/signals/grpc/services/handlers/registration.py \
   apps/crypto/grpc/services/handlers/

# Then adapt for crypto
nano apps/crypto/grpc/services/handlers/registration.py
```

### Tip 2: Use signals Tests as Template

```bash
# Copy test structure
cp /apps/signals/grpc/tests/run_tests.sh \
   apps/crypto/grpc/tests/

cp /apps/signals/grpc/tests/test_provider_registration.py \
   apps/crypto/grpc/tests/test_client_registration.py

# Adapt for crypto
nano apps/crypto/grpc/tests/test_client_registration.py
# Change: provider → client
# Change: SignalProviderMessage → ClientMessage
# Change: provider_id → client_id
```

### Tip 3: Test Incrementally

```bash
# Don't wait until everything is done!

# 1. Test proto generation
cd services/proto && bash generate_proto.sh

# 2. Test import
poetry run python -c "from apps.crypto.grpc.services.generated import crypto_streaming_pb2"

# 3. Test server startup
poetry run python manage.py rungrpc

# 4. Test registration
poetry run python apps/crypto/grpc/tests/test_client_registration.py
```

### Tip 4: Use Logging Liberally

```python
# Add logger.info() everywhere during development
logger.info(f"Processing {message_type} from {client_id[:8]}...")
logger.info(f"Created wallet update: {wallet_id}")
logger.info(f"Command sent to {client_id[:8]}: {command_type}")
```

### Tip 5: Read the Source

```bash
# When stuck, read django-cfg source
cd .venv/lib/python3.12/site-packages/django_cfg/apps/integrations/grpc/services/

cat streaming/core/service.py  # BidirectionalStreamingService
cat streaming/core/input_processor.py  # Message processing
cat commands/base.py  # StreamingCommandClient
```

## 📞 Next Steps

1. ✅ Read [ARCHITECTURE_GUIDE.md](./ARCHITECTURE_GUIDE.md)
2. ✅ Read [QUICKSTART.md](./QUICKSTART.md)
3. ✅ Study `/apps/signals/grpc`
4. ✅ Copy proto files
5. ✅ Follow checklist above
6. ✅ Test incrementally
7. ✅ Read django-cfg source when stuck

## 🎯 Success Criteria

Your implementation is complete when:

- [ ] `poetry run python manage.py rungrpc` starts without errors
- [ ] `apps/crypto/grpc/tests/run_tests.sh` passes all tests
- [ ] Client can connect and register
- [ ] Client can send wallet updates
- [ ] Client receives commands (ping/pause/resume)
- [ ] Client sends CommandAck back
- [ ] Centrifugo publishes to WebSocket channels
- [ ] ViewSet can send commands via REST API

---

**Time to implement:** 3-4 hours (first time), 1-2 hours (with experience)
**Difficulty:** Intermediate
**Prerequisites:** Understanding of gRPC, async Python, Django ORM
**Based on:** Production code from `/apps/signals` and `/apps/trading_bots`
