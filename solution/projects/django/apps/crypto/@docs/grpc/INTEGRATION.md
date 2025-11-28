# gRPC Integration Guide for Django-CFG

This document explains how the Crypto gRPC service integrates with django-cfg's auto-discovery system.

## How It Works

### 1. Configuration (`api/config.py`)

```python
from django_cfg import GRPCConfig, GRPCServerConfig

class DjangoCfgConfig(DjangoConfig):
    grpc: GRPCConfig = GRPCConfig(
        enabled=True,
        server=GRPCServerConfig(
            host="[::]",
            port=50051,
            max_workers=10,
            enable_reflection=True,
            enable_health_check=True,
        ),
        auto_register_apps=True,        # ← Enable auto-discovery
        enabled_apps=["crypto"],        # ← List apps to scan
    )
```

**Key points:**
- `enabled=True` - Turns on gRPC support
- `auto_register_apps=True` - Enables automatic service discovery
- `enabled_apps=["crypto"]` - Tells django-cfg which apps to scan

### 2. Service Discovery Process

When you run `python manage.py rungrpc`, django-cfg does this:

```python
# 1. Get enabled apps from config
enabled_apps = config.grpc.enabled_apps  # ['crypto']

# 2. For each app, look for these modules:
service_modules = [
    "grpc_services",      # ← We use this one
    "grpc_handlers",
    "services.grpc",
    "handlers.grpc",
    "api.grpc",
]

# 3. Try to import: apps.crypto.grpc_services
module = importlib.import_module('apps.crypto.grpc_services')

# 4. Look for grpc_handlers function
if hasattr(module, 'grpc_handlers'):
    handlers = module.grpc_handlers(None)  # Discovery mode

# 5. Register services
for service_class, add_to_server_func in handlers:
    servicer = service_class()
    add_to_server_func(servicer, server)
```

### 3. Service Module Structure

**Required:** `grpc_handlers()` function in `apps/crypto/grpc_services/__init__.py`:

```python
def grpc_handlers(server):
    """
    This function is auto-discovered by django-cfg.

    Args:
        server: gRPC server instance (None during discovery)

    Returns:
        List of (service_class, add_to_server_func) tuples
    """
    # Import here to avoid circular imports
    from .crypto_service import CryptoService
    from generated import crypto_service_pb2_grpc

    # Register if server provided
    if server is not None:
        crypto_service_pb2_grpc.add_CryptoServiceServicer_to_server(
            CryptoService(),
            server
        )

    # Return for discovery
    return [
        (CryptoService, crypto_service_pb2_grpc.add_CryptoServiceServicer_to_server)
    ]
```

**Key points:**
- Function must be named `grpc_handlers`
- Takes `server` parameter (None during discovery)
- Returns list of tuples: `(ServiceClass, add_to_server_function)`
- Registers service if server is provided

### 4. Service Implementation

**Required:** Service class that inherits from:
1. `BaseService` (django-cfg helper)
2. Generated servicer (from proto)

```python
from django_cfg.apps.integrations.grpc.services import BaseService
from generated import crypto_service_pb2_grpc

class CryptoService(BaseService, crypto_service_pb2_grpc.CryptoServiceServicer):
    """Your service implementation."""

    def GetCoin(self, request, context):
        # BaseService provides helpers:
        # - self.get_user(context)
        # - self.require_user(context)
        # - self.abort_not_found(context, message)
        # - etc.

        try:
            coin = Coin.objects.get(symbol=request.symbol)
            return CoinResponse(
                success=True,
                coin=ProtobufConverter.coin_to_protobuf(coin)
            )
        except Coin.DoesNotExist:
            self.abort_not_found(context, f"Coin {request.symbol} not found")
```

## BaseService Helpers

Django-cfg provides `BaseService` with useful helpers:

### Authentication

```python
def GetWallet(self, request, context):
    # Get authenticated user (optional)
    user = self.get_user(context)

    # Require authenticated user (aborts if not authenticated)
    user = self.require_user(context)

    # Check if user is staff
    if self.check_staff(context):
        # Staff-only logic

    # Require staff (aborts if not staff)
    self.require_staff(context)
```

### Permissions

```python
def DeleteCoin(self, request, context):
    # Check permission
    if self.check_permission(context, 'crypto.delete_coin'):
        # User has permission

    # Require permission (aborts if permission check fails)
    self.require_permission(context, 'crypto.delete_coin')
```

### Error Handling

```python
def GetCoin(self, request, context):
    # Validate input
    if not request.symbol:
        self.abort_invalid_argument(context, "Symbol is required")

    # Handle not found
    try:
        coin = Coin.objects.get(symbol=request.symbol)
    except Coin.DoesNotExist:
        self.abort_not_found(context, f"Coin {request.symbol} not found")

    # Handle other errors
    try:
        # Some operation
        pass
    except Exception as e:
        self.abort_internal(context, f"Internal error: {str(e)}")
```

**Available abort methods:**
- `abort_invalid_argument(context, message)` - Bad request (400)
- `abort_not_found(context, message)` - Not found (404)
- `abort_permission_denied(context, message)` - Forbidden (403)
- `abort_unauthenticated(context, message)` - Unauthorized (401)
- `abort_unimplemented(context, message)` - Not implemented (501)
- `abort_internal(context, message)` - Internal error (500)

### Metadata

```python
def GetCoin(self, request, context):
    # Get request metadata
    user_agent = self.get_metadata(context, 'user-agent')

    # Set response metadata
    self.set_metadata(context, 'x-request-id', request_id)

    # Get peer info
    peer = self.get_peer(context)  # "ipv4:127.0.0.1:12345"
```

## Directory Structure

```
apps/crypto/
├── grpc_services/              # gRPC package
│   ├── __init__.py            # Exports + grpc_handlers()
│   ├── crypto_service.py      # Service implementation
│   ├── converters.py          # Protobuf ↔ Django ORM
│   ├── client.py              # Python client
│   └── test_service.py        # Tests
├── models/
│   ├── coin.py
│   └── wallet.py
└── @docs/grpc/
    ├── README.md              # Complete guide
    ├── QUICKSTART.md          # Quick start
    ├── EXAMPLES.md            # Usage examples
    └── INTEGRATION.md         # This file

proto/                          # Root proto directory
└── crypto_service.proto       # Service definition

generated/                      # Auto-generated
├── crypto_service_pb2.py
└── crypto_service_pb2_grpc.py
```

## Multiple Services Per App

You can register multiple services from one app:

```python
def grpc_handlers(server):
    """Register multiple services."""
    from .coin_service import CoinService
    from .wallet_service import WalletService
    from generated import (
        coin_service_pb2_grpc,
        wallet_service_pb2_grpc,
    )

    if server is not None:
        coin_service_pb2_grpc.add_CoinServiceServicer_to_server(
            CoinService(), server
        )
        wallet_service_pb2_grpc.add_WalletServiceServicer_to_server(
            WalletService(), server
        )

    return [
        (CoinService, coin_service_pb2_grpc.add_CoinServiceServicer_to_server),
        (WalletService, wallet_service_pb2_grpc.add_WalletServiceServicer_to_server),
    ]
```

## Multiple Apps

Register services from multiple apps:

```python
# In api/config.py
grpc: GRPCConfig = GRPCConfig(
    enabled=True,
    auto_register_apps=True,
    enabled_apps=[
        "crypto",        # CryptoService
        "trading",       # TradingService
        "analytics",     # AnalyticsService
    ],
)
```

Each app should have its own `grpc_services/` package with `grpc_handlers()`.

## Custom Service Registration

If you need manual control:

```python
# In api/config.py
grpc: GRPCConfig = GRPCConfig(
    enabled=True,
    auto_register_apps=False,  # Disable auto-discovery
    custom_services={
        'crypto': 'apps.crypto.grpc_services.CryptoService',
        'trading': 'apps.trading.grpc_services.TradingService',
    },
)
```

Or use a custom handler hook:

```python
# In api/urls.py
def grpc_handlers(server):
    """Custom service registration."""
    from apps.crypto.grpc_services import CryptoService
    from generated import crypto_service_pb2_grpc

    crypto_service_pb2_grpc.add_CryptoServiceServicer_to_server(
        CryptoService(), server
    )

# In api/config.py
grpc: GRPCConfig = GRPCConfig(
    enabled=True,
    handlers_hook='api.urls.grpc_handlers',
)
```

## Proto Generation

### Auto-generation

Set `auto_generate=True` to generate on server start:

```python
grpc: GRPCConfig = GRPCConfig(
    enabled=True,
    proto=GRPCProtoConfig(
        auto_generate=True,       # Generate on runserver/rungrpc
        output_dir="generated",   # Output directory
        package_prefix="api",     # Package name
    ),
)
```

### Manual Generation

```bash
# Generate from proto files
python manage.py generate_proto

# Specify custom proto directory
python manage.py generate_proto --proto-dir custom_protos

# Specify custom output directory
python manage.py generate_proto --output-dir custom_generated
```

## Authentication & Authorization

### JWT Authentication

Enable JWT auth in config:

```python
grpc: GRPCConfig = GRPCConfig(
    enabled=True,
    auth=GRPCAuthConfig(
        enabled=True,
        require_auth=True,       # Require auth for all methods
        jwt_algorithm="HS256",
    ),
)
```

Use in service:

```python
def GetWallet(self, request, context):
    # Get authenticated user
    user = self.require_user(context)

    # Get user's wallet
    wallet = Wallet.objects.get(user=user, coin__symbol=request.symbol)
    return WalletResponse(wallet=ProtobufConverter.wallet_to_protobuf(wallet))
```

### Public Methods

Mix public and authenticated methods:

```python
grpc: GRPCConfig = GRPCConfig(
    enabled=True,
    auth=GRPCAuthConfig(
        enabled=True,
        require_auth=False,  # Allow public methods
    ),
)
```

```python
def GetCoin(self, request, context):
    # Public method - no auth required
    coin = Coin.objects.get(symbol=request.symbol)
    return CoinResponse(coin=ProtobufConverter.coin_to_protobuf(coin))

def GetWallet(self, request, context):
    # Private method - require auth
    user = self.require_user(context)
    wallet = Wallet.objects.get(user=user, ...)
    return WalletResponse(...)
```

## Monitoring & Debugging

### Reflection (grpcurl Support)

Enable reflection for CLI debugging:

```python
grpc: GRPCConfig = GRPCConfig(
    enabled=True,
    server=GRPCServerConfig(
        enable_reflection=True,  # ← Enable this
    ),
)
```

Test with grpcurl:

```bash
# List services
grpcurl -plaintext localhost:50051 list

# Describe service
grpcurl -plaintext localhost:50051 describe crypto.CryptoService

# Call method
grpcurl -plaintext -d '{"symbol": "BTC"}' \
  localhost:50051 crypto.CryptoService/GetCoin
```

### Health Check

Enable health check endpoint:

```python
grpc: GRPCConfig = GRPCConfig(
    enabled=True,
    server=GRPCServerConfig(
        enable_health_check=True,  # ← Enable this
    ),
)
```

Check health:

```bash
grpcurl -plaintext localhost:50051 grpc.health.v1.Health/Check
```

### Logging

Configure logging in settings:

```python
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'apps.crypto.grpc_services': {
            'handlers': ['console'],
            'level': 'INFO',
        },
        'grpc.discovery': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
    },
}
```

## Best Practices

### 1. Use App Labels

Use app labels (not full paths) in `enabled_apps`:

```python
# ✅ Good
enabled_apps=["crypto", "trading"]

# ❌ Bad
enabled_apps=["apps.crypto", "apps.trading"]
```

### 2. Lazy Imports

Import heavy dependencies inside `grpc_handlers()`:

```python
def grpc_handlers(server):
    # ✅ Good - import here
    from .crypto_service import CryptoService
    from generated import crypto_service_pb2_grpc

    # ...

# ❌ Bad - import at module level
from .crypto_service import CryptoService  # Might cause circular imports
```

### 3. Select Related

Always use `select_related()` for foreign keys:

```python
# ✅ Good
wallet = Wallet.objects.select_related('coin', 'user').get(id=1)

# ❌ Bad - causes N+1 queries
wallet = Wallet.objects.get(id=1)
coin_name = wallet.coin.name  # Extra query!
```

### 4. Error Handling

Use BaseService helpers for consistent errors:

```python
# ✅ Good
try:
    coin = Coin.objects.get(symbol=request.symbol)
except Coin.DoesNotExist:
    self.abort_not_found(context, f"Coin not found: {request.symbol}")

# ❌ Bad
try:
    coin = Coin.objects.get(symbol=request.symbol)
except Coin.DoesNotExist:
    context.abort(grpc.StatusCode.NOT_FOUND, "Not found")  # Less informative
```

## Troubleshooting

### Service not discovered

Check that:
1. App is in `enabled_apps`
2. `grpc_services/` package exists
3. `grpc_handlers()` function exists
4. Function returns correct format

### Import errors

Make sure proto files are generated:

```bash
python manage.py generate_proto
```

### Circular imports

Use lazy imports in `grpc_handlers()`:

```python
def grpc_handlers(server):
    # Import here, not at module level
    from .crypto_service import CryptoService
    # ...
```

## See Also

- [Complete Guide](./README.md)
- [Quick Start](./QUICKSTART.md)
- [Examples](./EXAMPLES.md)
- [Django-CFG gRPC Docs](https://docs.djangocfg.com/grpc)
