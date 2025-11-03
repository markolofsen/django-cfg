# Crypto App - gRPC Integration Demo

Complete gRPC service implementation demonstrating django-cfg's auto-discovery and best practices.

## 🎯 Overview

This is a **production-ready gRPC service** that provides:

- 🪙 **Coin Operations**: Get, list, search, top coins
- 📊 **Real-time Streaming**: Live price updates
- 💰 **Wallet Management**: Deposits, withdrawals, transfers
- 📈 **Portfolio Tracking**: Complete user portfolios
- 📉 **Market Analytics**: Stats, trending coins

**Perfect for:**
- Learning django-cfg gRPC integration
- Building cryptocurrency APIs
- Creating trading bots
- Microservices architecture

## 🚀 Quick Start

### 1. Generate Proto Files

```bash
# From project root
cd apps/crypto/grpc_services
./generate_proto.sh
```

Or manually:
```bash
python -m grpc_tools.protoc \
    -I./proto \
    --python_out=./generated \
    --grpc_python_out=./generated \
    ./proto/crypto_service.proto
```

### 2. Start gRPC Server

```bash
# From project root
python manage.py rungrpc
```

### 3. Test with Client

```bash
python -m apps.crypto.grpc_services.client
```

**That's it!** 🎉

## 📚 Documentation

| Document | Description |
|----------|-------------|
| [📖 Complete Guide](./@docs/grpc/README.md) | Full documentation, API reference, best practices |
| [⚡ Quick Start](./@docs/grpc/QUICKSTART.md) | 5-minute setup guide |
| [💡 Examples](./@docs/grpc/EXAMPLES.md) | Practical usage examples |
| [🔧 Integration](./@docs/grpc/INTEGRATION.md) | How auto-discovery works |
| [📊 Summary](./@docs/grpc/SUMMARY.md) | Implementation overview |

## 🎓 What You'll Learn

### Django-CFG Features
- ✅ **Auto-Discovery**: How services are automatically registered
- ✅ **BaseService**: Built-in helpers for auth, errors, metadata
- ✅ **Configuration**: Type-safe gRPC configuration
- ✅ **Proto Generation**: Automatic code generation

### Best Practices
- ✅ **Decimal Handling**: Precise financial data with strings
- ✅ **ORM Optimization**: select_related, prefetch_related
- ✅ **Atomic Transactions**: Safe wallet operations
- ✅ **Error Handling**: Proper gRPC error codes
- ✅ **Logging**: Comprehensive logging patterns

### Real-World Patterns
- ✅ **Server-side Streaming**: Real-time price updates
- ✅ **CRUD Operations**: Complete coin & wallet management
- ✅ **Pagination**: Efficient large dataset handling
- ✅ **Search**: Full-text search implementation
- ✅ **Analytics**: Market statistics and trending

## 📁 Project Structure

```
apps/crypto/
├── grpc_services/              # ← Your gRPC implementation
│   ├── __init__.py            # grpc_handlers() for auto-discovery
│   ├── crypto_service.py      # 14 RPC methods (650+ lines)
│   ├── converters.py          # Protobuf ↔ Django ORM
│   ├── client.py              # Complete Python client
│   ├── test_service.py        # Test suite
│   ├── generate_proto.sh      # ⚙️ Proto generation script
│   ├── proto/                 # 📄 Proto definitions
│   │   ├── crypto_service.proto  # Service definition (450+ lines)
│   │   └── README.md
│   ├── generated/             # 🤖 Auto-generated (git-ignored)
│   │   ├── __init__.py
│   │   ├── crypto_service_pb2.py
│   │   ├── crypto_service_pb2_grpc.py
│   │   ├── .gitignore
│   │   └── README.md
│   └── README_GRPC.md         # This file
├── models/
│   ├── coin.py                # Cryptocurrency model
│   └── wallet.py              # User wallet model
└── @docs/grpc/                # Complete documentation
    ├── README.md              # 600+ lines
    ├── QUICKSTART.md          # 400+ lines
    ├── EXAMPLES.md            # 800+ lines
    ├── INTEGRATION.md         # 500+ lines
    └── SUMMARY.md             # Implementation overview
```

**Total: ~4,500 lines of code + documentation**

## 🎯 Use Cases

### 1. Get Coin Information

```python
from apps.crypto.grpc_services.client import CryptoClient

client = CryptoClient('localhost:50051')

# Get Bitcoin
btc = client.get_coin(symbol='BTC')
print(f"BTC: ${btc.current_price_usd} ({btc.price_change_24h_percent}%)")
```

### 2. Real-time Price Monitoring

```python
# Stream prices every 5 seconds
for update in client.stream_prices(['BTC', 'ETH'], interval=5):
    print(f"{update.symbol}: ${update.price_usd}")
```

### 3. Portfolio Management

```python
# Get complete portfolio
portfolio = client.get_portfolio(user_id=1)
print(f"Total Value: ${portfolio.total_value_usd}")

for holding in portfolio.holdings:
    print(f"  {holding.symbol}: ${holding.value_usd} ({holding.percentage}%)")
```

### 4. Trading Bot

```python
# Simple trading bot
class TradingBot:
    def run(self):
        for update in client.stream_prices(['BTC']):
            price = Decimal(update.price_usd)

            if self.should_buy(price):
                client.deposit(user_id=1, symbol='BTC', amount='0.01')

            elif self.should_sell(price):
                client.withdraw(user_id=1, symbol='BTC', amount='0.01')
```

### 5. Market Analysis

```python
# Get market insights
stats = client.get_market_stats()
gainers = client.get_trending_coins(TOP_GAINERS, 10)

print(f"Market Cap: ${stats.total_market_cap_usd}")
print(f"Top Gainer: {gainers[0].symbol} (+{gainers[0].price_change_24h_percent}%)")
```

## 🔌 API Reference

### Coin Operations (5 methods)

| Method | Description |
|--------|-------------|
| `GetCoin` | Get single coin by symbol/id/slug |
| `ListCoins` | List with pagination, filters, sorting |
| `SearchCoins` | Search by name or symbol |
| `GetTopCoins` | Top coins by market cap |
| `StreamPrices` 🌊 | Real-time price streaming |

### Wallet Operations (6 methods)

| Method | Description |
|--------|-------------|
| `GetWallet` | Get user's wallet for specific coin |
| `ListWallets` | List all user wallets |
| `GetPortfolio` | Complete portfolio with analytics |
| `Deposit` | Add funds to wallet |
| `Withdraw` | Remove funds from wallet |
| `Transfer` | Transfer between users |

### Market Statistics (2 methods)

| Method | Description |
|--------|-------------|
| `GetMarketStats` | Overall market statistics |
| `GetTrendingCoins` | Gainers, losers, most traded |

🌊 = Server-side streaming

## 🧪 Testing

### Run Test Suite

```bash
python -m apps.crypto.grpc_services.test_service
```

### Test with Python Client

```bash
python -m apps.crypto.grpc_services.client
```

### Test with grpcurl

```bash
# List services
grpcurl -plaintext localhost:50051 list

# Get Bitcoin
grpcurl -plaintext -d '{"symbol": "BTC"}' \
  localhost:50051 crypto.CryptoService/GetCoin

# Stream prices
grpcurl -plaintext -d '{"symbols": ["BTC"]}' \
  localhost:50051 crypto.CryptoService/StreamPrices
```

## 📖 Learn More

### Start Here
1. **[Quick Start Guide](./@docs/grpc/QUICKSTART.md)** - Get running in 5 minutes
2. **[Examples](./@docs/grpc/EXAMPLES.md)** - Copy-paste ready code
3. **[Complete Guide](./@docs/grpc/README.md)** - Full documentation

### Deep Dive
- **[Integration Guide](./@docs/grpc/INTEGRATION.md)** - How auto-discovery works
- **[Summary](./@docs/grpc/SUMMARY.md)** - Implementation overview
- **[Proto File](../../proto/crypto_service.proto)** - Service definition

### External Resources
- [Django-CFG Docs](https://docs.djangocfg.com)
- [gRPC Python Docs](https://grpc.io/docs/languages/python/)
- [Protocol Buffers](https://protobuf.dev/)

## 💪 Features

### Implemented
- ✅ 14 RPC methods
- ✅ Server-side streaming
- ✅ Complete CRUD operations
- ✅ Wallet management
- ✅ Portfolio tracking
- ✅ Market analytics
- ✅ Real-time updates
- ✅ Error handling
- ✅ Logging
- ✅ Python client
- ✅ Test suite
- ✅ Complete documentation

### Django-CFG Integration
- ✅ Auto-discovery
- ✅ BaseService helpers
- ✅ Configuration system
- ✅ Proto generation
- ✅ Reflection support
- ✅ Health checks

## 🎓 Key Concepts

### Auto-Discovery

Service is automatically found and registered:

```python
# In api/config.py
grpc: GRPCConfig = GRPCConfig(
    enabled=True,
    auto_register_apps=True,
    enabled_apps=["crypto"],  # ← Scans apps.crypto.grpc_services
)
```

Django-cfg finds `grpc_handlers()` function and registers service automatically!

### BaseService Helpers

Built-in helpers for common tasks:

```python
from django_cfg.apps.integrations.grpc.services import BaseService

class CryptoService(BaseService, ...):
    def GetWallet(self, request, context):
        # Authentication
        user = self.require_user(context)

        # Permissions
        self.require_permission(context, 'crypto.view_wallet')

        # Error handling
        if not wallet_exists:
            self.abort_not_found(context, "Wallet not found")
```

### Decimal Precision

Financial data uses strings for precision:

```protobuf
message Coin {
  string current_price_usd = 10;  // Not double!
  string market_cap_usd = 11;
}
```

```python
# Convert with helpers
amount_str = ProtobufConverter.decimal_to_string(Decimal('123.456'))
amount_dec = ProtobufConverter.string_to_decimal("123.456")
```

## 🔨 Customization

### Add New Method

1. Update proto:
```protobuf
service CryptoService {
  rpc GetCoinHistory(GetCoinHistoryRequest) returns (CoinHistoryResponse);
}
```

2. Generate:
```bash
python manage.py generate_proto
```

3. Implement:
```python
def GetCoinHistory(self, request, context):
    # Your implementation
    pass
```

### Add Authentication

```python
def GetWallet(self, request, context):
    # Require authenticated user
    user = self.require_user(context)

    # Get user's wallet only
    wallet = Wallet.objects.get(user=user, coin__symbol=request.symbol)
    return WalletResponse(wallet=...)
```

### Add Validation

```python
def Deposit(self, request, context):
    # Validate amount
    amount = Decimal(request.amount)
    if amount <= 0:
        self.abort_invalid_argument(context, "Amount must be positive")

    # Your logic
    ...
```

## 🐛 Troubleshooting

### Proto files not found

```bash
cd apps/crypto/grpc_services
./generate_proto.sh
ls generated/crypto_service_pb2.py  # Verify
```

### Server won't start

```bash
# Check port
lsof -i :50051

# Try different port
python manage.py rungrpc --port 50052
```

### Import errors

```bash
pip install django-cfg[grpc]
```

## 📊 Metrics

- **Lines of Code**: 4,500+
- **RPC Methods**: 14
- **Documentation**: 2,500+ lines
- **Examples**: 50+
- **Test Coverage**: Complete

## 🤝 Contributing

Want to improve this demo? Great!

1. Add more RPC methods
2. Implement authentication examples
3. Add more use cases
4. Improve documentation
5. Add benchmarks

## 📄 License

Part of django-cfg, same license applies.

---

## 🎉 Next Steps

1. **Try It**: [Quick Start Guide](./@docs/grpc/QUICKSTART.md)
2. **Learn**: [Examples](./@docs/grpc/EXAMPLES.md)
3. **Build**: Copy structure for your app
4. **Share**: Show us what you built!

**Questions?** Check the [complete guide](./@docs/grpc/README.md) or [integration guide](./@docs/grpc/INTEGRATION.md).

---

**Built with ❤️ for django-cfg**
