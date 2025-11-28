# Crypto gRPC Service - Complete Guide

This is a complete demonstration of gRPC integration with django-cfg, showing best practices for building production-ready gRPC services in Django.

## 📋 Table of Contents

1. [Quick Start](#quick-start)
2. [Architecture](#architecture)
3. [Service API](#service-api)
4. [Setup & Configuration](#setup--configuration)
5. [Usage Examples](#usage-examples)
6. [Testing](#testing)
7. [Best Practices](#best-practices)

## 🚀 Quick Start

### 1. Generate Proto Files

```bash
# Generate Python code from .proto files
python manage.py generate_proto

# This creates files in generated/:
# - crypto_service_pb2.py
# - crypto_service_pb2_grpc.py
```

### 2. Start gRPC Server

```bash
# Start Django gRPC server (default port: 50051)
python manage.py rungrpc

# Or specify port:
python manage.py rungrpc --port 50052
```

### 3. Test with Client

```python
from apps.crypto.grpc_services.client import CryptoClient

# Create client
client = CryptoClient('localhost:50051')

# Get Bitcoin info
btc = client.get_coin(symbol='BTC')
print(f"BTC Price: ${btc.current_price_usd}")

# List top coins
top_10 = client.list_top_coins(10)
for coin in top_10:
    print(f"#{coin.rank} {coin.symbol}: ${coin.current_price_usd}")
```

### 4. Test with grpcurl (CLI)

```bash
# List services
grpcurl -plaintext localhost:50051 list

# Get coin by symbol
grpcurl -plaintext -d '{"symbol": "BTC"}' \
  localhost:50051 crypto.CryptoService/GetCoin

# List top coins
grpcurl -plaintext -d '{"limit": 10}' \
  localhost:50051 crypto.CryptoService/GetTopCoins
```

## 🏗️ Architecture

### File Structure

```
apps/crypto/
├── grpc_services/              # gRPC service implementation
│   ├── __init__.py            # Package exports
│   ├── crypto_service.py      # Main service (auto-discovered)
│   ├── converters.py          # Protobuf ↔ Django ORM
│   └── client.py              # Example Python client
├── models/                     # Django models
│   ├── coin.py                # Cryptocurrency model
│   └── wallet.py              # User wallet model
└── @docs/grpc/                # Documentation
    ├── README.md              # This file
    ├── EXAMPLES.md            # Usage examples
    └── API.md                 # API reference

proto/                          # Proto definitions
└── crypto_service.proto       # Service definition

generated/                      # Generated code (git-ignored)
├── crypto_service_pb2.py
└── crypto_service_pb2_grpc.py
```

### Service Auto-Discovery

The service is automatically discovered by django-cfg:

1. **Configuration** (`api/config.py`):
   ```python
   grpc: GRPCConfig = GRPCConfig(
       enabled=True,
       auto_register_apps=True,
       enabled_apps=["crypto"],  # App label for discovery
   )
   ```

2. **Discovery Process**:
   - Scans `apps.crypto.grpc_services` module
   - Finds `grpc_handlers(server)` function
   - Automatically registers `CryptoService`

3. **No Manual Registration**:
   - No need to manually add services to server
   - Just create `grpc_services/` with `grpc_handlers()`
   - Django-cfg handles the rest!

### Data Flow

```
┌─────────────┐         gRPC          ┌──────────────┐
│   Client    │ ◄────────────────────► │ CryptoService│
│  (Python/   │     Proto Messages     │  (Django)    │
│   Go/Rust)  │                        │              │
└─────────────┘                        └──────┬───────┘
                                              │
                                    ┌─────────▼────────┐
                                    │  Converters      │
                                    │  (Protobuf ↔     │
                                    │   Django ORM)    │
                                    └─────────┬────────┘
                                              │
                                    ┌─────────▼────────┐
                                    │  Django Models   │
                                    │  - Coin          │
                                    │  - Wallet        │
                                    └──────────────────┘
```

## 📡 Service API

### Coin Operations

| Method | Description | Request | Response |
|--------|-------------|---------|----------|
| `GetCoin` | Get single coin | `GetCoinRequest` | `CoinResponse` |
| `ListCoins` | List with pagination | `ListCoinsRequest` | `ListCoinsResponse` |
| `SearchCoins` | Search by name/symbol | `SearchCoinsRequest` | `ListCoinsResponse` |
| `GetTopCoins` | Top by market cap | `GetTopCoinsRequest` | `ListCoinsResponse` |
| `StreamPrices` | Real-time prices 🌊 | `StreamPricesRequest` | `stream PriceUpdate` |

### Wallet Operations

| Method | Description | Request | Response |
|--------|-------------|---------|----------|
| `GetWallet` | Get user wallet | `GetWalletRequest` | `WalletResponse` |
| `ListWallets` | List all wallets | `ListWalletsRequest` | `ListWalletsResponse` |
| `GetPortfolio` | Portfolio summary | `GetPortfolioRequest` | `PortfolioResponse` |
| `Deposit` | Add funds | `DepositRequest` | `WalletResponse` |
| `Withdraw` | Remove funds | `WithdrawRequest` | `WalletResponse` |
| `Transfer` | Transfer between users | `TransferRequest` | `TransferResponse` |

### Market Statistics

| Method | Description | Request | Response |
|--------|-------------|---------|----------|
| `GetMarketStats` | Overall market data | `Empty` | `MarketStatsResponse` |
| `GetTrendingCoins` | Gainers/losers | `GetTrendingCoinsRequest` | `TrendingCoinsResponse` |

🌊 = Server-side streaming

## ⚙️ Setup & Configuration

### 1. Install Dependencies

```bash
# Install gRPC dependencies
pip install django-cfg[grpc]

# Or manually:
pip install grpcio grpcio-tools grpcio-reflection
```

### 2. Configure Django Settings

In `api/config.py`:

```python
from django_cfg import GRPCConfig, GRPCServerConfig, GRPCAuthConfig

class MyConfig(DjangoConfig):
    grpc: GRPCConfig = GRPCConfig(
        enabled=True,

        # Server configuration
        server=GRPCServerConfig(
            host="[::]",              # Listen on all interfaces
            port=50051,               # Default gRPC port
            max_workers=10,           # Thread pool size
            enable_reflection=True,   # grpcurl support
            enable_health_check=True, # Health check endpoint
        ),

        # Authentication (optional)
        auth=GRPCAuthConfig(
            enabled=True,
            require_auth=False,       # Public methods allowed
            jwt_algorithm="HS256",
        ),

        # Proto generation
        proto=GRPCProtoConfig(
            auto_generate=True,       # Auto-gen on runserver
            output_dir="generated",   # Output directory
            package_prefix="api",     # Package name prefix
        ),

        # Auto-discovery
        auto_register_apps=True,
        enabled_apps=["crypto"],      # Apps to scan
    )
```

### 3. Create Proto File

Place in `proto/crypto_service.proto`:

```protobuf
syntax = "proto3";

package crypto;

service CryptoService {
  rpc GetCoin(GetCoinRequest) returns (CoinResponse);
  // ... other methods
}
```

See [crypto_service.proto](../../../proto/crypto_service.proto) for complete definition.

### 4. Implement Service

Create `apps/crypto/grpc_services/crypto_service.py`:

```python
from django_cfg.apps.integrations.grpc.services import BaseService
from generated import crypto_service_pb2_grpc

class CryptoService(BaseService, crypto_service_pb2_grpc.CryptoServiceServicer):
    def GetCoin(self, request, context):
        # Your implementation
        pass

def grpc_handlers(server):
    """Auto-discovered by django-cfg"""
    if server is not None:
        crypto_service_pb2_grpc.add_CryptoServiceServicer_to_server(
            CryptoService(), server
        )
    return [(CryptoService, crypto_service_pb2_grpc.add_CryptoServiceServicer_to_server)]
```

## 💡 Usage Examples

### Python Client

```python
from apps.crypto.grpc_services.client import CryptoClient

# Context manager (auto-closes connection)
with CryptoClient('localhost:50051') as client:
    # Get coin
    btc = client.get_coin(symbol='BTC')
    print(f"BTC: ${btc.current_price_usd}")

    # Search coins
    results = client.search_coins('bitcoin')

    # Get portfolio
    portfolio = client.get_portfolio(user_id=1)
    print(f"Total: ${portfolio.total_value_usd}")

    # Stream prices (blocking)
    for update in client.stream_prices(['BTC', 'ETH'], interval=5):
        print(f"{update.symbol}: ${update.price_usd}")
```

### Go Client

```go
package main

import (
    "context"
    "log"
    pb "your-module/generated"
    "google.golang.org/grpc"
)

func main() {
    conn, _ := grpc.Dial("localhost:50051", grpc.WithInsecure())
    defer conn.Close()

    client := pb.NewCryptoServiceClient(conn)

    // Get Bitcoin
    resp, _ := client.GetCoin(context.Background(), &pb.GetCoinRequest{
        Symbol: "BTC",
    })

    log.Printf("BTC Price: $%s", resp.Coin.CurrentPriceUsd)
}
```

### Rust Client

```rust
use tonic::transport::Channel;
use crypto_service::crypto_service_client::CryptoServiceClient;

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    let channel = Channel::from_static("http://localhost:50051")
        .connect()
        .await?;

    let mut client = CryptoServiceClient::new(channel);

    // Get Bitcoin
    let request = tonic::Request::new(GetCoinRequest {
        symbol: "BTC".to_string(),
        ..Default::default()
    });

    let response = client.get_coin(request).await?;
    println!("BTC Price: ${}", response.get_ref().coin.as_ref().unwrap().current_price_usd);

    Ok(())
}
```

### cURL via grpcurl

```bash
# Get coin
grpcurl -plaintext -d '{"symbol": "BTC"}' \
  localhost:50051 crypto.CryptoService/GetCoin

# Deposit funds
grpcurl -plaintext -d '{
  "user_id": 1,
  "symbol": "BTC",
  "amount": "0.5",
  "transaction_id": "tx123"
}' localhost:50051 crypto.CryptoService/Deposit

# Get portfolio
grpcurl -plaintext -d '{"user_id": 1}' \
  localhost:50051 crypto.CryptoService/GetPortfolio
```

## 🧪 Testing

### Unit Tests

```python
import grpc
from django.test import TestCase
from apps.crypto.models import Coin, Wallet
from apps.crypto.grpc_services.crypto_service import CryptoService
from generated import crypto_service_pb2

class CryptoServiceTest(TestCase):
    def setUp(self):
        self.service = CryptoService()
        self.context = grpc.ServicerContext()  # Mock context

        # Create test data
        self.btc = Coin.objects.create(
            symbol='BTC',
            name='Bitcoin',
            slug='bitcoin',
            current_price_usd=50000
        )

    def test_get_coin(self):
        request = crypto_service_pb2.GetCoinRequest(symbol='BTC')
        response = self.service.GetCoin(request, self.context)

        self.assertTrue(response.success)
        self.assertEqual(response.coin.symbol, 'BTC')
```

### Integration Tests

```bash
# Start test server
python manage.py rungrpc --settings=api.settings_test

# Run client tests
python -m apps.crypto.grpc_services.client
```

## ✨ Best Practices

### 1. Use Strings for Decimals

**Problem**: Protobuf doesn't have native Decimal type.

**Solution**: Use strings for precise financial data:

```protobuf
message Coin {
  string current_price_usd = 10;  // Not double!
  string balance = 20;            // Precise balance
}
```

```python
# In converter
def decimal_to_string(value: Decimal) -> str:
    return str(value) if value else "0"

def string_to_decimal(value: str) -> Decimal:
    return Decimal(value) if value else Decimal('0')
```

### 2. Select Related for Performance

Always use `select_related()` for foreign keys:

```python
# ❌ Bad - N+1 queries
wallet = Wallet.objects.get(id=1)
coin_name = wallet.coin.name  # Extra query!

# ✅ Good - Single query
wallet = Wallet.objects.select_related('coin').get(id=1)
coin_name = wallet.coin.name  # No extra query
```

### 3. Handle Errors Properly

Use BaseService error helpers:

```python
class CryptoService(BaseService):
    def GetCoin(self, request, context):
        try:
            coin = Coin.objects.get(symbol=request.symbol)
        except Coin.DoesNotExist:
            self.abort_not_found(context, f"Coin not found: {request.symbol}")
        except Exception as e:
            self.abort_internal(context, f"Error: {str(e)}")
```

### 4. Use Atomic Transactions

For wallet operations:

```python
from django.db import transaction

def Transfer(self, request, context):
    with transaction.atomic():
        from_wallet = Wallet.objects.select_for_update().get(...)
        to_wallet = Wallet.objects.select_for_update().get(...)

        # Check balance
        if from_wallet.balance < amount:
            self.abort_invalid_argument(context, "Insufficient balance")

        # Execute transfer
        from_wallet.balance -= amount
        to_wallet.balance += amount

        from_wallet.save()
        to_wallet.save()
```

### 5. Add Logging

Log important operations:

```python
import logging

logger = logging.getLogger(__name__)

def GetCoin(self, request, context):
    logger.info(f"📊 GetCoin: {request.symbol}")
    # ... implementation
    logger.info(f"✅ GetCoin successful: {coin.symbol}")
```

### 6. Reserve Proto Fields

Use `reserved` for future compatibility:

```protobuf
message Coin {
  int32 id = 1;
  string symbol = 2;

  reserved 3 to 9;  // Reserve for future fields

  string current_price_usd = 10;

  reserved 11 to 19;
}
```

### 7. Denormalize When Appropriate

Include commonly needed data:

```python
# Wallet includes coin symbol (denormalized)
def wallet_to_protobuf(wallet):
    return Wallet(
        id=wallet.id,
        symbol=wallet.coin.symbol,  # Denormalized for convenience
        coin_name=wallet.coin.name,  # Client doesn't need separate call
        balance=str(wallet.balance),
    )
```

## 📚 Additional Resources

- [Full API Reference](./API.md)
- [More Examples](./EXAMPLES.md)
- [Proto Definition](../../../proto/crypto_service.proto)
- [Django-CFG gRPC Docs](https://docs.djangocfg.com/grpc)

## 🤝 Contributing

To add new RPC methods:

1. Update `proto/crypto_service.proto`
2. Run `python manage.py generate_proto`
3. Implement method in `CryptoService`
4. Add converter if needed
5. Add client method
6. Update documentation
7. Add tests

## 📄 License

This demo is part of django-cfg and follows the same license.
