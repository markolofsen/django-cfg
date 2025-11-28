# Crypto gRPC Service - Quick Start Guide

Get started with the Crypto gRPC service in 5 minutes!

## Prerequisites

- Python 3.10+
- Django 4.2+
- django-cfg installed with gRPC support

## Installation

### 1. Install gRPC Dependencies

```bash
# Option 1: Install with django-cfg
pip install django-cfg[grpc]

# Option 2: Install manually
pip install grpcio grpcio-tools grpcio-reflection
```

### 2. Verify Configuration

Check that gRPC is enabled in `api/config.py`:

```python
from django_cfg import GRPCConfig

class YourConfig(DjangoConfig):
    grpc: GRPCConfig = GRPCConfig(
        enabled=True,
        auto_register_apps=True,
        enabled_apps=["crypto"],  # ✅ crypto app is included
    )
```

### 3. Generate Proto Files

```bash
# Generate Python code from .proto files
python manage.py generate_proto

# Expected output:
# ✅ Generated: generated/crypto_service_pb2.py
# ✅ Generated: generated/crypto_service_pb2_grpc.py
```

### 4. Start gRPC Server

```bash
# Start on default port (50051)
python manage.py rungrpc

# Or specify custom port
python manage.py rungrpc --port 50052

# Expected output:
# ✅ gRPC server starting on [::]:50051
# ✅ Registered 1 service(s):
#    - crypto.CryptoService
# ✅ Reflection enabled
# ✅ Server started successfully
```

## Testing

### Test with Python Client

Create `test_client.py`:

```python
from apps.crypto.grpc_services.client import CryptoClient

# Create client
client = CryptoClient('localhost:50051')

# Get Bitcoin info
btc = client.get_coin(symbol='BTC')
print(f"✅ BTC Price: ${btc.current_price_usd}")

# List top 5 coins
print("\n📊 Top 5 Coins:")
for coin in client.list_top_coins(5):
    print(f"   #{coin.rank} {coin.symbol}: ${coin.current_price_usd}")

# Get market stats
stats = client.get_market_stats()
print(f"\n💰 Total Market Cap: ${stats.total_market_cap_usd}")

print("\n✅ All tests passed!")
```

Run it:

```bash
python test_client.py
```

### Test with grpcurl (CLI)

```bash
# Install grpcurl
brew install grpcurl  # macOS
# or
go install github.com/fullstorydev/grpcurl/cmd/grpcurl@latest

# List all services
grpcurl -plaintext localhost:50051 list

# List all methods
grpcurl -plaintext localhost:50051 list crypto.CryptoService

# Get Bitcoin
grpcurl -plaintext -d '{"symbol": "BTC"}' \
  localhost:50051 crypto.CryptoService/GetCoin

# Get top 10 coins
grpcurl -plaintext -d '{"limit": 10}' \
  localhost:50051 crypto.CryptoService/GetTopCoins
```

## Common Use Cases

### 1. Get Coin Information

```python
from apps.crypto.grpc_services.client import CryptoClient

client = CryptoClient()

# By symbol (recommended)
btc = client.get_coin(symbol='BTC')

# By ID
coin = client.get_coin(coin_id=1)

# By slug
eth = client.get_coin(slug='ethereum')
```

### 2. Search Coins

```python
# Search for "bitcoin"
results = client.search_coins('bitcoin', limit=5)

for coin in results:
    print(f"{coin.symbol} - {coin.name}")
```

### 3. Real-time Price Monitoring

```python
# Stream prices for BTC and ETH every 5 seconds
for update in client.stream_prices(['BTC', 'ETH'], interval=5):
    print(f"{update.symbol}: ${update.price_usd}")
```

### 4. Wallet Operations

```python
# Get wallet
wallet = client.get_wallet(user_id=1, symbol='BTC')
print(f"Balance: {wallet.balance} BTC")

# Deposit
wallet = client.deposit(
    user_id=1,
    symbol='BTC',
    amount='0.5',
    transaction_id='tx123'
)

# Get portfolio
portfolio = client.get_portfolio(user_id=1)
print(f"Total: ${portfolio.total_value_usd}")
```

### 5. Market Statistics

```python
# Overall market stats
stats = client.get_market_stats()
print(f"Market Cap: ${stats.total_market_cap_usd}")

# Top gainers
gainers = client.get_trending_coins(
    trending_type=crypto_service_pb2.TOP_GAINERS,
    limit=10
)
```

## Project Structure

```
apps/crypto/
├── grpc_services/           # ← Your gRPC code is here
│   ├── __init__.py
│   ├── crypto_service.py   # Main service implementation
│   ├── converters.py       # Protobuf ↔ Django ORM
│   └── client.py           # Python client example
├── models/
│   ├── coin.py
│   └── wallet.py
└── @docs/grpc/
    ├── README.md           # Complete guide
    ├── QUICKSTART.md       # This file
    └── EXAMPLES.md         # Usage examples

proto/
└── crypto_service.proto    # Service definition

generated/                   # Auto-generated (git-ignored)
├── crypto_service_pb2.py
└── crypto_service_pb2_grpc.py
```

## Next Steps

### Read Documentation

- 📚 [Complete Guide](./README.md) - Full documentation
- 💡 [Examples](./EXAMPLES.md) - Practical examples
- 🔧 [Proto Definition](../../../proto/crypto_service.proto) - Service spec

### Try Advanced Features

- **Server-side Streaming**: Real-time price updates
- **Portfolio Tracking**: Monitor user holdings
- **Market Analysis**: Trending coins, statistics
- **Trading Bots**: Automated trading integration

### Customize

1. **Add New Methods**:
   - Update `proto/crypto_service.proto`
   - Run `python manage.py generate_proto`
   - Implement in `CryptoService`

2. **Add Authentication**:
   ```python
   class CryptoService(BaseService, ...):
       def GetCoin(self, request, context):
           # Require authentication
           user = self.require_user(context)

           # Check permissions
           self.require_permission(context, 'crypto.view_coin')

           # Your logic
           ...
   ```

3. **Add Validation**:
   ```python
   def Deposit(self, request, context):
       # Validate amount
       amount = Decimal(request.amount)
       if amount <= 0:
           self.abort_invalid_argument(context, "Amount must be positive")

       # Your logic
       ...
   ```

## Troubleshooting

### Proto files not found

```bash
# Make sure proto files are generated
python manage.py generate_proto

# Check that files exist
ls generated/crypto_service_pb2.py
```

### Server won't start

```bash
# Check if port is in use
lsof -i :50051

# Try different port
python manage.py rungrpc --port 50052
```

### Connection refused

```bash
# Make sure server is running
python manage.py rungrpc

# Check firewall
# Check that you're connecting to correct host:port
```

### Import errors

```bash
# Reinstall gRPC dependencies
pip install --upgrade grpcio grpcio-tools

# Or install django-cfg with grpc extras
pip install django-cfg[grpc]
```

## Development Workflow

```bash
# 1. Make changes to proto
vim proto/crypto_service.proto

# 2. Regenerate
python manage.py generate_proto

# 3. Implement in service
vim apps/crypto/grpc_services/crypto_service.py

# 4. Test
python test_client.py

# 5. Restart server
python manage.py rungrpc
```

## Production Deployment

### Docker

```dockerfile
FROM python:3.11

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

# Generate proto files
RUN python manage.py generate_proto

# Run gRPC server
CMD ["python", "manage.py", "rungrpc", "--host", "0.0.0.0"]
```

### Docker Compose

```yaml
version: '3.8'

services:
  grpc:
    build: .
    ports:
      - "50051:50051"
    environment:
      - DJANGO_SETTINGS_MODULE=api.settings
    depends_on:
      - db
      - redis

  db:
    image: postgres:15
    environment:
      POSTGRES_DB: crypto_db
      POSTGRES_USER: user
      POSTGRES_PASSWORD: pass

  redis:
    image: redis:7-alpine
```

### Kubernetes

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: crypto-grpc
spec:
  replicas: 3
  selector:
    matchLabels:
      app: crypto-grpc
  template:
    metadata:
      labels:
        app: crypto-grpc
    spec:
      containers:
      - name: grpc-server
        image: your-registry/crypto-grpc:latest
        ports:
        - containerPort: 50051
        env:
        - name: DJANGO_SETTINGS_MODULE
          value: "api.settings"
---
apiVersion: v1
kind: Service
metadata:
  name: crypto-grpc
spec:
  type: LoadBalancer
  ports:
  - port: 50051
    targetPort: 50051
    protocol: TCP
  selector:
    app: crypto-grpc
```

## Support

- 📖 [Full Documentation](./README.md)
- 🐛 [Report Issues](https://github.com/your-org/django-cfg/issues)
- 💬 [Discord Community](https://discord.gg/djangocfg)
- 📧 [Email Support](mailto:support@djangocfg.com)

## License

This demo is part of django-cfg and follows the same license.

---

**Ready to build?** Start with the [examples](./EXAMPLES.md) or dive into the [complete guide](./README.md)!
