# Crypto gRPC Service

**Production-ready gRPC service** for cryptocurrency operations with Centrifugo WebSocket integration.

## 🎯 Overview

Modern gRPC service demonstrating django-cfg's auto-discovery and best practices:

- 🪙 **Coin Operations**: Get, list, search, top coins
- 📊 **Real-time Streaming**: Live price updates with WebSocket publishing
- 💰 **Wallet Management**: Deposits, withdrawals, transfers
- 📈 **Portfolio Tracking**: Complete user portfolios
- 📉 **Market Analytics**: Stats, trending coins
- 🌉 **Centrifugo Bridge**: Auto-publish price updates to WebSocket clients

## 🚀 Quick Start

### 1. Generate Proto Files

```bash
cd apps/crypto/grpc/services/proto
./generate_proto.sh
```

### 2. Start gRPC Server

```bash
python manage.py rungrpc
```

### 3. Test Price Streaming

```python
import grpc
from apps.crypto.grpc.services.generated import crypto_service_pb2, crypto_service_pb2_grpc

# Connect to gRPC server
channel = grpc.insecure_channel('localhost:50051')
stub = crypto_service_pb2_grpc.CryptoServiceStub(channel)

# Stream BTC and ETH prices
request = crypto_service_pb2.StreamPricesRequest(
    symbols=['BTC', 'ETH'],
    interval_seconds=1
)

for price_update in stub.StreamPrices(request):
    print(f"{price_update.symbol}: ${price_update.price_usd}")
```

## 📡 Centrifugo Integration

Price updates are automatically published to WebSocket channels:

```javascript
// Frontend: Subscribe to BTC price updates
const subscription = centrifuge.newSubscription('crypto#prices#BTC');

subscription.on('publication', (ctx) => {
  console.log('BTC Price Update:', ctx.data);
  // { symbol: 'BTC', price_usd: '45000.00', change_24h_percent: '2.5', timestamp: '...' }
});

subscription.subscribe();
```

**Available channels:**
- `crypto#prices#{symbol}` - Specific coin price updates
- `crypto#prices#all` - All price updates
- `crypto#market#stats` - Market statistics
- `crypto#wallet#{user_id}` - User wallet updates
- `crypto#portfolio#{user_id}` - Portfolio value updates

## 🏗️ Architecture

```
┌──────────────┐  gRPC Stream   ┌─────────────────┐  WebSocket   ┌──────────┐
│ Price Feed   │ ──────────────> │ Django gRPC     │ ───────────> │ Browser  │
│ (client)     │ <────────────── │ + Centrifugo    │ <─────────── │ (Admin)  │
└──────────────┘                 │ Bridge          │              └──────────┘
                                 └─────────────────┘
                                         ↓
                                   [Database]
                                   [Rate Limiting]
                                   [Circuit Breaker]
```

**Data Flow:**
1. gRPC client requests price streaming
2. Django fetches prices from DB (async ORM)
3. Django publishes to Centrifugo WebSocket
4. Django yields to gRPC client
5. Browser receives real-time updates via WebSocket

## 📚 Structure

```
grpc/
├── __init__.py
├── README.md
├── QUICKSTART.md
├── services/
│   ├── __init__.py
│   ├── server.py              # Main CryptoService
│   ├── channels.py            # Centrifugo channel config
│   ├── config.py              # Service configuration
│   ├── proto/
│   │   ├── __init__.py
│   │   ├── crypto_service.proto
│   │   ├── converters.py      # Protobuf ↔ Django ORM
│   │   └── generate_proto.sh
│   └── generated/
│       ├── __init__.py
│       ├── crypto_service_pb2.py
│       └── crypto_service_pb2_grpc.py
├── @docs/
│   ├── README.md
│   ├── API.md
│   └── EXAMPLES.md
├── examples/
│   ├── simple_client.py
│   └── price_streaming.py
└── tests/
    ├── test_coin_operations.py
    └── test_price_streaming.py
```

## 🎓 Key Features

### 1. Centrifugo Bridge

```python
class CryptoService(
    BaseService,
    crypto_service_pb2_grpc.CryptoServiceServicer,
    CentrifugoBridgeMixin  # ← One-line WebSocket integration
):
    centrifugo_channels = CryptoChannels()
    
    async def StreamPrices(self, request, context):
        for coin in coins:
            # Auto-publish to WebSocket
            await self._centrifugo_client.publish(
                channel=f'crypto#prices#{coin.symbol}',
                data={'price_usd': str(coin.current_price_usd)}
            )
            yield price_update
```

### 2. Type-Safe Channel Configuration

```python
class CryptoChannels(CentrifugoChannels):
    price_update: ChannelConfig = ChannelConfig(
        template='crypto#prices#{symbol}',
        rate_limit=0.5,  # Max 2 updates/sec per coin
        critical=False,
        metadata={'event_type': 'price_update'}
    )
```

### 3. Production-Ready Patterns

- ✅ **Async ORM** - Django 5.2+ async queries
- ✅ **Rate Limiting** - Per-channel throttling
- ✅ **Circuit Breaker** - Graceful Centrifugo degradation
- ✅ **Error Handling** - Proper gRPC status codes
- ✅ **Logging** - Structured logging with emojis

## 📖 API Reference

### Coin Operations

- `GetCoin(symbol)` - Get single coin by symbol
- `ListCoins(page, page_size)` - List all coins with pagination
- `SearchCoins(query)` - Search coins by name/symbol
- `GetTopCoins(limit)` - Get top coins by market cap
- `StreamPrices(symbols, interval)` - Stream real-time prices

### Wallet Operations

- `GetWallet(user_id, symbol)` - Get user wallet
- `ListWallets(user_id)` - List all user wallets
- `GetPortfolio(user_id)` - Get portfolio summary
- `Deposit(user_id, symbol, amount)` - Deposit funds
- `Withdraw(user_id, symbol, amount)` - Withdraw funds
- `Transfer(from_user, to_user, symbol, amount)` - Transfer between wallets

### Market Statistics

- `GetMarketStats()` - Get market statistics
- `GetTrendingCoins()` - Get trending coins

## 🔧 Configuration

### Service Config

```python
# services/config.py
@dataclass
class CryptoServiceConfig:
    enable_centrifugo: bool = True
    price_stream_interval: float = 1.0
    max_concurrent_streams: int = 100
    enable_logging: bool = True
```

### Channel Config

```python
# services/channels.py
class CryptoChannels(CentrifugoChannels):
    price_update: ChannelConfig = ChannelConfig(
        template='crypto#prices#{symbol}',
        rate_limit=0.5,
        critical=False,
    )
    
    wallet_update: ChannelConfig = ChannelConfig(
        template='crypto#wallet#{user_id}',
        rate_limit=None,
        critical=True,  # No rate limit for wallet updates
    )
```

## 🧪 Testing

```bash
# Run all tests
cd apps/crypto/grpc/tests
pytest

# Test specific feature
pytest test_price_streaming.py -v
```

## 📚 Documentation

- **[QUICKSTART.md](./QUICKSTART.md)** - 5-minute setup guide
- **[@docs/README.md](./@docs/README.md)** - Complete documentation
- **[@docs/API.md](./@docs/API.md)** - API reference
- **[@docs/EXAMPLES.md](./@docs/EXAMPLES.md)** - Usage examples

## 🎯 Best Practices

### 1. Decimal Handling

```python
# Use strings for precise financial data
price_usd = ProtobufConverter.decimal_to_string(coin.current_price_usd)
```

### 2. Async ORM

```python
# Django 5.2+ async queries
coins = await Coin.objects.filter(is_active=True).alist()
```

### 3. Error Handling

```python
try:
    # Your logic
except Coin.DoesNotExist:
    self.abort_not_found(context, "Coin not found")
except Exception as e:
    self.abort_internal(context, f"Error: {e}")
```

### 4. Rate Limiting

```python
# Configure per-channel rate limits
price_update: ChannelConfig = ChannelConfig(
    template='crypto#prices#{symbol}',
    rate_limit=0.5,  # Max 2 updates/sec
)
```

## 🚀 Production Deployment

### 1. Enable in Django Config

```python
# config.py
class MyConfig(DjangoConfig):
    grpc: GRPCConfig = GRPCConfig(
        enabled=True,
        enabled_apps=["crypto"],  # ← Enable crypto gRPC
        port=50051,
    )
    
    centrifugo: CentrifugoConfig = CentrifugoConfig(
        enabled=True,
        api_url="http://localhost:8001/api",
    )
```

### 2. Start Services

```bash
# Terminal 1: Django gRPC server
python manage.py rungrpc

# Terminal 2: Centrifugo
centrifugo --config=centrifugo.json

# Terminal 3: Django web server
python manage.py runserver
```

### 3. Monitor

```bash
# Check gRPC health
grpcurl -plaintext localhost:50051 list

# Check Centrifugo
curl http://localhost:8001/api/info
```

## 🤝 Contributing

This is a reference implementation demonstrating:
- Modern gRPC service architecture
- Centrifugo WebSocket integration
- Production-ready patterns
- Django 5.2+ async ORM

Feel free to adapt for your use case!

---

**Created:** 2025-01-08  
**Status:** %%PRODUCTION%%  
**Django-CFG:** Auto-discovery enabled

