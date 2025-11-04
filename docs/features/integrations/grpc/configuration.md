---
title: Configuration
description: Complete configuration reference for Django-CFG gRPC integration
sidebar_label: Configuration
sidebar_position: 4
keywords:
  - grpc configuration
  - grpc settings
  - grpc config
---

# gRPC Configuration

Complete reference for configuring Django-CFG gRPC integration.

## 📋 Configuration Structure

```python
# api/config.py
from typing import Optional
from django_cfg import (
    DjangoConfig,
    GRPCConfig,
    GRPCServerConfig,
    GRPCAuthConfig,
    GRPCProtoConfig,
)

class MyConfig(DjangoConfig):
    grpc: Optional[GRPCConfig] = GRPCConfig(
        enabled=True,
        server=GRPCServerConfig(...),
        auth=GRPCAuthConfig(...),
        proto=GRPCProtoConfig(...),
        auto_register_apps=True,
        enabled_apps=[...],
    )
```

## ⚙️ GRPCConfig

Main gRPC configuration container.

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `enabled` | `bool` | `False` | Enable/disable gRPC server |
| `server` | `GRPCServerConfig` | - | Server configuration |
| `auth` | `GRPCAuthConfig` | - | Authentication configuration |
| `proto` | `GRPCProtoConfig` | - | Protocol Buffer configuration |
| `auto_register_apps` | `bool` | `True` | Auto-discover services |
| `enabled_apps` | `list[str]` | `[]` | Apps to scan for services |

### Example

```python
grpc: GRPCConfig = GRPCConfig(
    enabled=True,
    auto_register_apps=True,
    enabled_apps=["apps.users", "apps.products", "apps.orders"],
)
```

## 🎯 Simplified Configuration (Flatten Fields)

For simpler configs, you can use **flatten fields** instead of nested config objects:

### Traditional (Nested):
```python
grpc = GRPCConfig(
    enabled=True,
    server=GRPCServerConfig(
        host="[::]",
        port=50051,
    ),
    proto=GRPCProtoConfig(
        package_prefix="api",
        output_dir="protos",
    ),
    enabled_apps=["apps.crypto"],
)
```

### Simplified (Flatten):
```python
grpc = GRPCConfig(
    enabled=True,
    enabled_apps=["apps.crypto"],
    # Server fields (flatten)
    host="[::]",          # Instead of server=GRPCServerConfig(host=...)
    port=50051,
    # Proto fields (flatten)
    package_prefix="api", # Instead of proto=GRPCProtoConfig(package_prefix=...)
    # Environment integration
    public_url=env.grpc_url,
)
```

**Benefits:**
- Less boilerplate code
- No need to import nested config classes
- Cleaner configuration
- Same functionality

**When to use nested:** When you need to organize complex configs or reuse config objects.
**When to use flatten:** For simple configs (recommended for most cases).

## 🖥️ GRPCServerConfig

gRPC server settings.

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `host` | `str` | `"[::]"` | Server host address |
| `port` | `int` | `50051` | Server port |
| `max_workers` | `int` | `10` | Thread pool size |
| `enable_reflection` | `bool` | `True` | Enable server reflection |
| `enable_health_check` | `bool` | `True` | Enable health check service |

### Host Options

```python
# All interfaces (IPv6) - Recommended
host="[::]"

# All interfaces (IPv4)
host="0.0.0.0"

# Localhost only
host="127.0.0.1"

# Specific IP
host="192.168.1.100"
```

### Worker Threads

```python
# Low traffic (development)
max_workers=5

# Medium traffic
max_workers=10

# High traffic (production)
max_workers=20

# Very high traffic
max_workers=50
```

**Rule of thumb:** Start with 10, increase if you see thread starvation.

### Reflection

```python
# Development: Enable for grpcurl testing
enable_reflection=True

# Production: Disable to hide service schema
enable_reflection=False
```

### Health Check

```python
# Always recommended for production
enable_health_check=True

# For load balancers
# GET /grpc.health.v1.Health/Check
```

### Complete Example

```python
server=GRPCServerConfig(
    host="[::]",              # All interfaces
    port=50051,               # Standard port
    max_workers=20,           # 20 concurrent requests
    enable_reflection=True,   # Enable grpcurl
    enable_health_check=True, # Enable health checks
)
```

## 🔐 GRPCAuthConfig

Authentication configuration (supports both API keys and JWT).

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `enabled` | `bool` | `False` | Enable authentication |
| `require_auth` | `bool` | `False` | Require auth for all methods |
| **API Key Settings** | | | |
| `api_key_header` | `str` | `"x-api-key"` | Header name for API key |
| `accept_django_secret_key` | `bool` | `True` | Accept Django SECRET_KEY as valid API key (for dev/internal use) |
| **General** | | | |
| `public_methods` | `list[str]` | `[]` | Public methods (no auth required) |

### Authentication Modes

**Mode 1: Disabled (Development)**
```python
auth=GRPCAuthConfig(
    enabled=False,  # No authentication
)
```

**Mode 2: Optional Auth (Recommended)**
```python
auth=GRPCAuthConfig(
    enabled=True,
    require_auth=False,  # Some methods can be public
    api_key_header="x-api-key",
    accept_django_secret_key=True,  # Allow SECRET_KEY for dev
)

# In service:
# - Use self.get_user(context) for optional auth
# - Use self.require_user(context) for protected methods
# - Access context.api_key to check which API key was used
```

**Mode 3: Required Auth (Strict - Production)**
```python
auth=GRPCAuthConfig(
    enabled=True,
    require_auth=True,  # All methods require API key
    api_key_header="x-api-key",
    accept_django_secret_key=False,  # Production: only DB keys
    public_methods=[    # Except these
        "/grpc.health.v1.Health/Check",
    ],
)
```

### Public Methods

```python
auth=GRPCAuthConfig(
    enabled=True,
    require_auth=False,
    public_methods=[
        # Health check (always public)
        "/grpc.health.v1.Health/Check",
        "/grpc.health.v1.Health/Watch",

        # Your public methods
        "/api.users.UserService/GetUser",
        "/api.products.ProductService/ListProducts",
    ],
)
```

### Complete Example

```python
# Production configuration with API keys
auth=GRPCAuthConfig(
    enabled=True,
    require_auth=True,  # Strict auth in production
    # API key configuration
    api_key_header="x-api-key",
    accept_django_secret_key=False,  # Disable SECRET_KEY in production
    # Public methods
    public_methods=[
        "/grpc.health.v1.Health/Check",
        "/grpc.health.v1.Health/Watch",
    ],
)
```

### API Key Settings

**Custom Header Name**
```python
auth=GRPCAuthConfig(
    api_key_header="x-custom-api-key",  # Change header name
)
```

**Disable SECRET_KEY (Production)**
```python
auth=GRPCAuthConfig(
    accept_django_secret_key=False,  # Only accept keys from database
)
```

**Enable SECRET_KEY (Development)**
```python
auth=GRPCAuthConfig(
    accept_django_secret_key=True,  # Allow using settings.SECRET_KEY
)

# Usage:
# grpcurl -H "x-api-key: $(python manage.py shell -c 'from django.conf import settings; print(settings.SECRET_KEY)')" ...
```

## 📄 GRPCProtoConfig

Protocol Buffer generation settings.

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `auto_generate` | `bool` | `False` | Auto-generate proto files |
| `output_dir` | `str` | `"protos"` | Proto output directory |
| `package_prefix` | `str` | `"api"` | Package prefix |

### Example

```python
proto=GRPCProtoConfig(
    auto_generate=True,
    output_dir="protos",
    package_prefix="api",
)

# Generates:
# protos/api/users.proto
# protos/api/products.proto
```

## 🎯 Environment-Specific Configs

### Development

```python
class DevelopmentConfig(DjangoConfig):
    DEBUG = True

    grpc: GRPCConfig = GRPCConfig(
        enabled=True,
        server=GRPCServerConfig(
            host="127.0.0.1",         # Localhost only
            port=50051,
            max_workers=5,            # Low workers
            enable_reflection=True,   # Enable for testing
            enable_health_check=True,
        ),
        auth=GRPCAuthConfig(
            enabled=True,  # Enable auth even in dev
            require_auth=False,
            api_key_header="x-api-key",
            accept_django_secret_key=True,  # Allow SECRET_KEY for convenience
            # JWT disabled for simpler dev workflow
        ),
        enabled_apps=["apps.users"],  # Limited apps
    )
```

### Production

```python
class ProductionConfig(DjangoConfig):
    DEBUG = False

    grpc: GRPCConfig = GRPCConfig(
        enabled=True,
        server=GRPCServerConfig(
            host="[::]",              # All interfaces
            port=50051,
            max_workers=20,           # Higher workers
            enable_reflection=False,  # Disable in production
            enable_health_check=True, # Keep health checks
        ),
        auth=GRPCAuthConfig(
            enabled=True,             # Enable auth
            require_auth=True,        # Require by default
            # API key configuration
            api_key_header="x-api-key",
            accept_django_secret_key=False,  # Disable SECRET_KEY in production
            public_methods=[
                "/grpc.health.v1.Health/Check",
            ],
        ),
        enabled_apps=[
            "apps.users",
            "apps.products",
            "apps.orders",
            "apps.payments",
        ],
    )
```

### Testing

```python
class TestingConfig(DjangoConfig):
    TESTING = True

    grpc: GRPCConfig = GRPCConfig(
        enabled=True,
        server=GRPCServerConfig(
            host="127.0.0.1",
            port=50052,              # Different port
            max_workers=1,           # Single worker for tests
            enable_reflection=True,
            enable_health_check=False,  # Not needed in tests
        ),
        auth=GRPCAuthConfig(
            enabled=False,  # Simplify testing
        ),
    )
```

## 🌍 Environment Variables

Override config with environment variables:

```bash
# .env file
GRPC_ENABLED=true
GRPC_HOST=0.0.0.0
GRPC_PORT=50051
GRPC_MAX_WORKERS=20
GRPC_ENABLE_REFLECTION=false
GRPC_AUTH_ENABLED=true
GRPC_REQUIRE_AUTH=true
GRPC_API_KEY_HEADER=x-api-key
GRPC_ACCEPT_SECRET_KEY=false
```

In config:

```python
import os

grpc: GRPCConfig = GRPCConfig(
    enabled=os.getenv("GRPC_ENABLED", "true").lower() == "true",
    server=GRPCServerConfig(
        host=os.getenv("GRPC_HOST", "[::]"),
        port=int(os.getenv("GRPC_PORT", "50051")),
        max_workers=int(os.getenv("GRPC_MAX_WORKERS", "10")),
        enable_reflection=os.getenv("GRPC_ENABLE_REFLECTION", "true").lower() == "true",
    ),
    auth=GRPCAuthConfig(
        enabled=os.getenv("GRPC_AUTH_ENABLED", "false").lower() == "true",
        require_auth=os.getenv("GRPC_REQUIRE_AUTH", "false").lower() == "true",
        api_key_header=os.getenv("GRPC_API_KEY_HEADER", "x-api-key"),
        accept_django_secret_key=os.getenv("GRPC_ACCEPT_SECRET_KEY", "true").lower() == "true",
    ),
)
```

## 📊 Service Discovery

### Auto-Discovery Locations

Services are discovered from these locations (in order):

1. `app/grpc_services.py`
2. `app/grpc_handlers.py`
3. `app/services/grpc.py`
4. `app/handlers/grpc.py`
5. `app/api/grpc.py`

### Enabled Apps

```python
grpc: GRPCConfig = GRPCConfig(
    auto_register_apps=True,
    enabled_apps=[
        # Full app paths
        "apps.users",
        "apps.products",

        # Core Django apps (if they have gRPC services)
        "django.contrib.auth",

        # Third-party apps
        "mylib.grpc_app",
    ],
)
```

### Manual Registration

If auto-discovery doesn't work, register manually:

```python
# api/grpc_handlers.py
def register_handlers(server):
    from apps.users.grpc_services import UserService
    from apps.users import user_pb2_grpc

    user_pb2_grpc.add_UserServiceServicer_to_server(
        UserService(),
        server
    )
```

Then in config:

```python
grpc: GRPCConfig = GRPCConfig(
    handlers_hook="api.grpc_handlers.register_handlers",
)
```

## 🚀 Command-Line Options

Override config when starting server:

```bash
# Custom host and port
python manage.py rungrpc --host 0.0.0.0 --port 50052

# More workers
python manage.py rungrpc --workers 20

# Verbose output
python manage.py rungrpc --verbosity 3

# Combined
python manage.py rungrpc \
  --host 0.0.0.0 \
  --port 50052 \
  --workers 20 \
  --verbosity 2
```

## 🎛️ Advanced Configuration

### Custom Interceptors

:::danger Interceptor Order Matters!
Interceptors execute in the order listed. **Authentication interceptors MUST come first** to set `context.user` and `context.api_key` before logging interceptors use them.

**Correct order:**
1. `ApiKeyAuthInterceptor` - Sets context.api_key and context.user
2. `RequestLoggerInterceptor` - Logs request with api_key info
3. `LoggingInterceptor` (dev mode)
4. `MetricsInterceptor` (dev mode)
5. Custom interceptors

**Wrong order causes:** API keys not tracked in logs, user info missing.
:::

```python
# In your config or settings
GRPC_INTERCEPTORS = [
    # 1. Auth FIRST (sets context.api_key and context.user)
    'django_cfg.apps.integrations.grpc.auth.ApiKeyAuthInterceptor',
    # 2. Request logger (uses context.api_key from auth)
    'django_cfg.apps.integrations.grpc.interceptors.RequestLoggerInterceptor',
    # 3. Your custom interceptors
    'myapp.interceptors.CustomInterceptor',
]
```

### Connection Timeouts

```python
# Client-side (in proto definition or client config)
# For long-running operations
deadline = 300  # 5 minutes

# Server-side (in service)
context.set_deadline(time.time() + 300)
```

### Request Size Limits

```python
# In server options
options = [
    ('grpc.max_send_message_length', 50 * 1024 * 1024),    # 50MB
    ('grpc.max_receive_message_length', 50 * 1024 * 1024), # 50MB
]

server = grpc.server(
    futures.ThreadPoolExecutor(max_workers=10),
    interceptors=interceptors,
    options=options,
)
```

## 📚 Configuration Checklist

### Development ✅
- [ ] `enabled=True`
- [ ] `host="127.0.0.1"` (localhost)
- [ ] `enable_reflection=True` (for grpcurl)
- [ ] `auth.enabled=False` (easy testing)
- [ ] `max_workers=5` (low)

### Production ✅
- [ ] `enabled=True`
- [ ] `host="[::]"` (all interfaces)
- [ ] `enable_reflection=False` (security)
- [ ] `auth.enabled=True` (security)
- [ ] `auth.require_auth=True` (strict)
- [ ] `max_workers=20+` (high throughput)
- [ ] Environment variables for secrets
- [ ] Health check enabled
- [ ] Monitoring/logging enabled

## 📖 Related Documentation

- **[Getting Started](./getting-started.md)** - Build your first service
- **[Authentication](./authentication.md)** - API keys and JWT authentication
- **[Concepts](./concepts.md)** - Understanding architecture
- **[FAQ](./faq.md)** - Common questions

---

**Configuration Tip:** Start with defaults, measure performance, then tune based on actual traffic patterns. For production, always use API keys or JWT authentication with `require_auth=True`.
