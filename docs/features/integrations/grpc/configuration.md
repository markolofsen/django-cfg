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

JWT authentication configuration.

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `enabled` | `bool` | `False` | Enable JWT authentication |
| `require_auth` | `bool` | `False` | Require auth for all methods |
| `jwt_algorithm` | `str` | `"HS256"` | JWT signing algorithm |
| `jwt_secret_key` | `str` | `settings.SECRET_KEY` | JWT signing key |
| `public_methods` | `list[str]` | `[]` | Public methods (no auth) |

### JWT Algorithms

```python
# Symmetric (uses SECRET_KEY)
jwt_algorithm="HS256"  # HMAC with SHA-256 (most common)

# Asymmetric (requires public/private keys)
jwt_algorithm="RS256"  # RSA with SHA-256
jwt_algorithm="ES256"  # ECDSA with SHA-256
```

### Authentication Modes

**Mode 1: Disabled (Development)**
```python
auth=GRPCAuthConfig(
    enabled=False,  # No authentication
)
```

**Mode 2: Optional (Flexible)**
```python
auth=GRPCAuthConfig(
    enabled=True,
    require_auth=False,  # Some methods public, some protected
)

# In service:
# - Use self.get_user(context) for optional auth
# - Use self.require_user(context) for protected methods
```

**Mode 3: Required (Strict)**
```python
auth=GRPCAuthConfig(
    enabled=True,
    require_auth=True,  # All methods require auth
    public_methods=[    # Except these
        "/grpc.health.v1.Health/Check",
        "/api.users.UserService/GetUser",
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
auth=GRPCAuthConfig(
    enabled=True,
    require_auth=False,
    jwt_algorithm="HS256",
    jwt_secret_key=settings.SECRET_KEY,  # Or env variable
    public_methods=[
        "/grpc.health.v1.Health/Check",
    ],
)
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
            enabled=False,  # Disable auth for easy testing
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
            jwt_algorithm="RS256",    # Asymmetric for production
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

```python
# In your config or settings
GRPC_INTERCEPTORS = [
    'django_cfg.apps.integrations.grpc.interceptors.RequestLoggerInterceptor',
    'django_cfg.apps.integrations.grpc.auth.JWTAuthInterceptor',
    'myapp.interceptors.CustomInterceptor',  # Your custom interceptor
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
- **[Concepts](./concepts.md)** - Understanding architecture
- **[FAQ](./faq.md)** - Common questions

---

**Configuration Tip:** Start with defaults, measure performance, then tune based on actual traffic patterns.
