---
title: Setup & Configuration
description: Install and configure gRPC in your Django-CFG project
sidebar_label: Setup Guide
sidebar_position: 3
keywords:
  - grpc setup
  - grpc configuration
  - grpc install
  - django grpc setup
---

# gRPC Setup & Configuration

This guide walks you through installing and configuring gRPC in your Django-CFG project.

## 📦 Installation

### 1. Install gRPC Dependencies

Django-CFG requires the following packages for gRPC support:

```bash
# Using pip
pip install grpcio grpcio-tools protobuf djangogrpcframework

# Using poetry
poetry add grpcio grpcio-tools protobuf djangogrpcframework

# Or install django-cfg with grpc extras
pip install django-cfg[grpc]
```

**Packages:**
- `grpcio` - gRPC framework
- `grpcio-tools` - Protocol Buffer compiler
- `protobuf` - Protocol Buffers library
- `djangogrpcframework` - Django integration for gRPC

### 2. Verify Installation

```bash
python -c "import grpc; print(f'gRPC version: {grpc.__version__}')"
```

Expected output:
```
gRPC version: 1.76.0
```

## ⚙️ Configuration

### 1. Enable gRPC in Django Config

Add gRPC configuration to your Django-CFG config file:

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
    # ... other configuration ...

    # === gRPC Configuration ===
    grpc: Optional[GRPCConfig] = GRPCConfig(
        enabled=True,
        server=GRPCServerConfig(
            host="[::]",              # Listen on all interfaces (IPv6)
            port=50051,               # Standard gRPC port
            max_workers=10,           # Thread pool size
            enable_reflection=True,   # Enable server reflection (for grpcurl)
            enable_health_check=True, # Enable health checking protocol
        ),
        auth=GRPCAuthConfig(
            enabled=True,             # Enable JWT authentication
            require_auth=False,       # Don't require auth for all methods
            jwt_algorithm="HS256",    # JWT signing algorithm
        ),
        proto=GRPCProtoConfig(
            auto_generate=True,       # Auto-generate .proto files
            output_dir="protos",      # Output directory for .proto files
            package_prefix="api",     # Package prefix (api.users, api.products)
        ),
        # Service auto-discovery
        auto_register_apps=True,
        enabled_apps=[
            "core",
            "apps.users",
            "apps.products",
            "apps.orders",
        ],
    )
```

### 2. Configuration Reference

#### GRPCConfig

Main gRPC configuration container.

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `enabled` | `bool` | `False` | Enable gRPC integration |
| `server` | `GRPCServerConfig` | - | Server configuration |
| `auth` | `GRPCAuthConfig` | - | Authentication configuration |
| `proto` | `GRPCProtoConfig` | - | Proto generation configuration |
| `auto_register_apps` | `bool` | `True` | Enable service auto-discovery |
| `enabled_apps` | `list[str]` | `[]` | Apps to scan for gRPC services |

#### GRPCServerConfig

gRPC server settings.

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `host` | `str` | `"[::]"` | Server host (IPv4: `"0.0.0.0"`, IPv6: `"[::]"`) |
| `port` | `int` | `50051` | Server port |
| `max_workers` | `int` | `10` | Thread pool size |
| `enable_reflection` | `bool` | `True` | Enable server reflection (allows grpcurl) |
| `enable_health_check` | `bool` | `True` | Enable health check service |

**Host options:**
- `"[::]"` - All interfaces IPv6 (recommended)
- `"0.0.0.0"` - All interfaces IPv4
- `"127.0.0.1"` - Localhost only
- `"192.168.1.100"` - Specific IP

**Worker threads:**
- More workers = more concurrent requests
- But higher memory usage
- Recommended: 10-20 for most apps

#### GRPCAuthConfig

JWT authentication settings.

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `enabled` | `bool` | `False` | Enable JWT authentication |
| `require_auth` | `bool` | `False` | Require auth for all methods (if False, per-service) |
| `jwt_algorithm` | `str` | `"HS256"` | JWT signing algorithm |

**JWT algorithms:**
- `"HS256"` - HMAC with SHA-256 (symmetric)
- `"RS256"` - RSA with SHA-256 (asymmetric)
- `"ES256"` - ECDSA with SHA-256 (asymmetric)

#### GRPCProtoConfig

Protocol Buffer generation settings.

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `auto_generate` | `bool` | `False` | Auto-generate .proto files |
| `output_dir` | `str` | `"protos"` | Output directory |
| `package_prefix` | `str` | `"api"` | Package prefix for services |

## 🗂️ Project Structure

After configuration, your project structure will include:

```
your-project/
├── api/
│   ├── config.py              # Django-CFG configuration (gRPC enabled)
│   ├── settings.py            # Generated Django settings
│   └── urls.py                # URL configuration
├── apps/
│   ├── users/
│   │   ├── models.py
│   │   ├── grpc_services.py   # ✅ gRPC services (auto-discovered)
│   │   └── ...
│   ├── products/
│   │   ├── models.py
│   │   ├── grpc_services.py   # ✅ gRPC services (auto-discovered)
│   │   └── ...
│   └── orders/
│       ├── models.py
│       ├── grpc_services.py   # ✅ gRPC services (auto-discovered)
│       └── ...
├── protos/                     # Generated .proto files (if auto_generate=True)
│   ├── api/
│   │   ├── users.proto
│   │   ├── products.proto
│   │   └── orders.proto
│   └── ...
└── manage.py
```

## 🎯 Service Discovery Patterns

Django-CFG will automatically discover gRPC services from these locations:

### Option 1: Root Level (Recommended)

```
apps/users/
├── models.py
├── admin.py
├── grpc_services.py     # ✅ Discovered automatically
└── ...
```

```python
# apps/users/grpc_services.py
from django_cfg.apps.grpc.services import BaseService

class UserService(BaseService):
    def GetUser(self, request, context):
        # ...
```

### Option 2: Handlers Pattern

```
apps/users/
├── models.py
├── grpc_handlers.py     # ✅ Discovered automatically
└── ...
```

### Option 3: Services Directory

```
apps/users/
├── models.py
├── services/
│   ├── __init__.py
│   ├── grpc.py          # ✅ Discovered automatically
│   └── rest.py
└── ...
```

### Option 4: API Directory

```
apps/users/
├── models.py
├── api/
│   ├── __init__.py
│   ├── grpc.py          # ✅ Discovered automatically
│   └── rest.py
└── ...
```

**Discovery priority:**
1. `grpc_services.py`
2. `grpc_handlers.py`
3. `services/grpc.py`
4. `handlers/grpc.py`
5. `api/grpc.py`

## 🔧 Environment Variables

You can override configuration via environment variables:

```bash
# .env file
GRPC_ENABLED=true
GRPC_HOST=0.0.0.0
GRPC_PORT=50051
GRPC_MAX_WORKERS=20
GRPC_ENABLE_REFLECTION=true
GRPC_ENABLE_HEALTH_CHECK=true
GRPC_AUTH_ENABLED=true
GRPC_REQUIRE_AUTH=false
```

```python
# api/environment.py (YAML config)
grpc:
  enabled: true
  host: "0.0.0.0"
  port: 50051
  max_workers: 20
  enable_reflection: true
  enable_health_check: true
  auth:
    enabled: true
    require_auth: false
```

## ✅ Verify Installation

### 1. Check Django Settings

```bash
python manage.py check
```

Expected output:
```
System check identified no issues (0 silenced).
```

### 2. Verify gRPC App Installed

```bash
python manage.py shell
```

```python
>>> from django.conf import settings
>>> 'django_cfg.apps.grpc' in settings.INSTALLED_APPS
True
```

### 3. Check gRPC URLs

```bash
python manage.py show_urls | grep grpc
```

Expected output:
```
/admin/grpc/grpcrequestlog/          admin:grpc_grpcrequestlog_changelist
/cfg/grpc/monitor/overview/          django_cfg_grpc:monitor-overview
/cfg/grpc/monitor/requests/          django_cfg_grpc:monitor-requests
/cfg/grpc/monitor/services/          django_cfg_grpc:monitor-services
...
```

### 4. Run Migrations

```bash
python manage.py migrate grpc
```

Expected output:
```
Operations to perform:
  Apply all migrations: grpc
Running migrations:
  Applying grpc.0001_initial... OK
```

### 5. Start gRPC Server

```bash
python manage.py rungrpc
```

Expected output:
```
🚀 Starting gRPC server...
📡 Server running at [::]:50051
🔍 Reflection enabled
❤️  Health check enabled
✅ Registered 3 services:
   - api.users.UserService
   - api.products.ProductService
   - api.orders.OrderService
```

### 6. Test with grpcurl

```bash
# List services
grpcurl -plaintext localhost:50051 list

# Expected output:
# api.users.UserService
# api.products.ProductService
# api.orders.OrderService
# grpc.health.v1.Health
# grpc.reflection.v1alpha.ServerReflection

# Describe a service
grpcurl -plaintext localhost:50051 describe api.users.UserService

# Check health
grpcurl -plaintext localhost:50051 grpc.health.v1.Health/Check
```

## 🎨 Configuration Examples

### Development Configuration

```python
# api/config.py (Development)
grpc: Optional[GRPCConfig] = GRPCConfig(
    enabled=True,
    server=GRPCServerConfig(
        host="127.0.0.1",         # Localhost only
        port=50051,
        max_workers=5,            # Lower for dev
        enable_reflection=True,   # Enable for grpcurl
        enable_health_check=True,
    ),
    auth=GRPCAuthConfig(
        enabled=False,            # Disable auth in dev
    ),
    proto=GRPCProtoConfig(
        auto_generate=True,       # Auto-generate protos
        output_dir="protos",
    ),
    auto_register_apps=True,
    enabled_apps=["apps.users", "apps.products"],
)
```

### Production Configuration

```python
# api/config.py (Production)
grpc: Optional[GRPCConfig] = GRPCConfig(
    enabled=True,
    server=GRPCServerConfig(
        host="[::]",              # All interfaces
        port=50051,
        max_workers=20,           # Higher for production
        enable_reflection=False,  # Disable reflection in production
        enable_health_check=True, # Keep health checks
    ),
    auth=GRPCAuthConfig(
        enabled=True,             # Enable auth
        require_auth=True,        # Require auth for all methods
        jwt_algorithm="RS256",    # Use asymmetric signing
    ),
    proto=GRPCProtoConfig(
        auto_generate=False,      # Use pre-generated protos
    ),
    auto_register_apps=True,
    enabled_apps=[
        "apps.users",
        "apps.products",
        "apps.orders",
        "apps.payments",
    ],
)
```

### Microservices Configuration

```python
# api/config.py (Microservices)
grpc: Optional[GRPCConfig] = GRPCConfig(
    enabled=True,
    server=GRPCServerConfig(
        host="0.0.0.0",           # Listen on all interfaces
        port=int(os.getenv("GRPC_PORT", "50051")),
        max_workers=10,
        enable_reflection=True,   # For service discovery
        enable_health_check=True, # For load balancer health checks
    ),
    auth=GRPCAuthConfig(
        enabled=True,
        require_auth=False,       # Some services are public
    ),
    # Only register this microservice's apps
    enabled_apps=["apps.users"],  # User service only
)
```

## 🔒 Security Best Practices

### 1. Use TLS in Production

```python
# Production: Enable TLS
server=GRPCServerConfig(
    host="[::]",
    port=50051,
    # Add TLS certificates
    server_credentials=grpc.ssl_server_credentials(
        [(server_key, server_cert)],
        root_certificates=client_ca_cert,
        require_client_auth=True,
    ),
)
```

### 2. Disable Reflection in Production

```python
server=GRPCServerConfig(
    enable_reflection=False,  # Don't expose service schema
)
```

### 3. Enable Authentication

```python
auth=GRPCAuthConfig(
    enabled=True,
    require_auth=True,  # Require for all methods
)
```

### 4. Rate Limiting

Consider adding rate limiting interceptor for production.

## 📚 Next Steps

Now that gRPC is configured, learn how to:

- **[Create gRPC Services](./backend-guide.md)** - Build your first service
- **[Add Authentication](./authentication.md)** - Secure your services with JWT
- **[Monitor Requests](./monitoring.md)** - View logs and metrics
- **[View Architecture](./architecture.md)** - Understand gRPC design patterns

---

**Next:** Learn how to [create gRPC services](./backend-guide.md).
