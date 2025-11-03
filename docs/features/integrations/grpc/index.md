---
title: gRPC Integration
description: Production-ready gRPC server with Django ORM, JWT auth, and automatic service discovery
sidebar_label: Overview
sidebar_position: 1
keywords:
  - django grpc
  - grpc python
  - grpc server
  - protocol buffers
---

# gRPC Integration

:::tip[Production-Ready gRPC Server]
Build high-performance gRPC APIs with full Django integration - ORM, authentication, admin interface, and automatic service discovery.
:::

## 🎯 What is This?

Django-CFG provides a **complete gRPC server** that integrates seamlessly with Django:

- ✅ **Auto-Discovery** - Services automatically registered from Django apps
- ✅ **Django Integration** - Full ORM, auth, admin, signals access
- ✅ **JWT Authentication** - Built-in token-based authentication
- ✅ **Request Logging** - All requests logged to database
- ✅ **Production-Ready** - Interceptors, error handling, monitoring
- ✅ **Developer-Friendly** - Base classes, helpers, zero configuration

## 🚀 Quick Start

### 1. Install

```bash
pip install django-cfg[grpc]
```

### 2. Enable in Config

```python
# api/config.py
from django_cfg import DjangoConfig, GRPCConfig, GRPCServerConfig

class MyConfig(DjangoConfig):
    grpc = GRPCConfig(
        enabled=True,
        server=GRPCServerConfig(
            host="[::]",
            port=50051,
        ),
        enabled_apps=["apps.users", "apps.products"],
    )
```

### 3. Create Service

```python
# apps/users/grpc_services.py
from django_cfg.apps.integrations.grpc.services import BaseService
from django.contrib.auth import get_user_model

User = get_user_model()

class UserService(BaseService):
    def GetUser(self, request, context):
        user = User.objects.get(id=request.user_id)
        return UserResponse(
            id=user.id,
            username=user.username,
            email=user.email,
        )
```

### 4. Start Server

```bash
python manage.py rungrpc
```

Output:
```
🚀 Starting gRPC server...
📡 Server running at [::]:50051
✅ Registered 1 service: api.users.UserService
```

### 5. Test

```bash
grpcurl -plaintext -d '{"user_id": 1}' \
  localhost:50051 api.users.UserService/GetUser
```

**That's it!** Your gRPC service is running. 🎉

## 🏗️ Architecture

```mermaid
graph TB
    subgraph "Clients"
        Python["Python Client"]
        Go["Go Client"]
        JS["JavaScript Client"]
    end

    subgraph "Django-CFG gRPC Server"
        Server["gRPC Server<br/>(Port 50051)"]

        subgraph "Interceptors"
            Logger["Request Logger"]
            Auth["JWT Auth"]
            Error["Error Handler"]
        end

        subgraph "Services"
            Auto["Auto-Discovery"]
            User["UserService"]
            Product["ProductService"]
        end
    end

    subgraph "Django"
        ORM["Django ORM"]
        Admin["Admin Interface"]
    end

    Python --> Server
    Go --> Server
    JS --> Server

    Server --> Logger --> Auth --> Error
    Error --> Auto --> User
    Auto --> Product

    User --> ORM
    Product --> ORM
    Logger -.->|Logs| Admin

    style Server fill:#e3f2fd
    style User fill:#e8f5e9
    style ORM fill:#f3e5f5
```

## 🎯 Key Features

### Auto-Discovery

Services are automatically discovered from your Django apps:

```python
# No registration needed! Just create the file:
# apps/users/grpc_services.py

class UserService(BaseService):
    def GetUser(self, request, context):
        # Automatically discovered and registered
        pass
```

**Discovery locations:**
- `app/grpc_services.py` ✅
- `app/grpc_handlers.py` ✅
- `app/services/grpc.py` ✅

### Django Integration

Full access to Django features:

```python
class OrderService(BaseService):
    def CreateOrder(self, request, context):
        # Django ORM
        user = self.require_user(context)  # From JWT token
        order = Order.objects.create(user=user)

        # Django signals
        order_created.send(sender=Order, instance=order)

        # Django cache
        cache.set(f'order:{order.id}', order, 300)

        return OrderResponse(...)
```

### JWT Authentication

Built-in JWT authentication with Django users:

```python
class UserService(BaseService):
    def UpdateProfile(self, request, context):
        # Require authentication
        user = self.require_user(context)

        # Check permissions
        if not user.has_perm('users.change_profile'):
            self.abort_permission_denied(context, "No access")

        # Update profile
        user.bio = request.bio
        user.save()
        return UserResponse(...)
```

Call with token:
```bash
grpcurl -H "Authorization: Bearer <token>" \
  localhost:50051 api.users.UserService/UpdateProfile
```

### Request Logging

All requests automatically logged to database:

```python
# View in Django Admin
/admin/integrations/grpc/grpcrequestlog/

# Query programmatically
from django_cfg.apps.integrations.grpc.models import GRPCRequestLog

stats = GRPCRequestLog.objects.get_statistics(hours=24)
# {
#     "total": 1543,
#     "successful": 1489,
#     "success_rate": 96.5,
#     "avg_duration_ms": 125.3
# }
```

### Base Service Classes

Three base classes for common patterns:

```python
# Flexible authentication
from django_cfg.apps.integrations.grpc.services import BaseService

class MyService(BaseService):
    pass

# Read-only operations
from django_cfg.apps.integrations.grpc.services import ReadOnlyService

class CatalogService(ReadOnlyService):
    pass

# All methods require auth
from django_cfg.apps.integrations.grpc.services import AuthRequiredService

class AccountService(AuthRequiredService):
    pass
```

### Dynamic Invocation (Phase 4)

Test services without proto files using reflection:

```python
from django_cfg.apps.integrations.grpc.services.grpc_client import DynamicGRPCClient

client = DynamicGRPCClient("localhost", 50051)

# Discover services
services = client.list_services()

# Invoke method
response = client.invoke_method(
    "api.users.UserService",
    "GetUser",
    {"user_id": 1}
)
```

## 🔄 Request Flow

```mermaid
sequenceDiagram
    participant C as Client
    participant S as Server
    participant L as Logger
    participant A as Auth
    participant SV as Service
    participant DB as Database

    C->>S: gRPC Request
    S->>L: 1. Log request start
    L->>DB: Create log entry
    S->>A: 2. Verify JWT
    A->>DB: Load user
    A->>SV: 3. Call service
    SV->>DB: 4. Query data
    DB-->>SV: Data
    SV-->>L: 5. Response
    L->>DB: Update log (duration, status)
    L-->>C: Response
```

## 📚 Documentation

### Core Guides
- **[Getting Started](./getting-started.md)** - Build your first service (10 min)
- **[Concepts](./concepts.md)** - Architecture and design patterns
- **[Configuration](./configuration.md)** - Complete configuration reference

### Advanced Topics
- **[Dynamic Invocation](./dynamic-invocation.md)** - Test without proto files
- **[FAQ](./faq.md)** - Common questions and troubleshooting

## 💡 Why Django-CFG gRPC?

### vs. Plain gRPC

| Feature | Plain gRPC | Django-CFG gRPC |
|---------|------------|-----------------|
| Service Registration | Manual | ✅ Automatic |
| Django ORM | Manual setup | ✅ Built-in |
| Authentication | DIY | ✅ JWT included |
| Request Logging | DIY | ✅ Automatic |
| Admin Interface | None | ✅ Built-in |
| Error Handling | Manual | ✅ Automatic |

### vs. REST

| Aspect | REST | gRPC |
|--------|------|------|
| Performance | Good | ✅ Excellent |
| Binary Protocol | No | ✅ Yes (smaller, faster) |
| Streaming | Limited | ✅ Bidirectional |
| Type Safety | Optional | ✅ Built-in (protobuf) |
| Browser Support | ✅ Native | Limited (grpc-web) |
| Public APIs | ✅ Better | Good |

**Use gRPC for:**
- Microservices communication
- Mobile app backends
- Real-time systems
- High-performance APIs

**Use REST for:**
- Public APIs
- Browser-based apps
- Simple CRUD

---

**Ready to start?** Check out the [Getting Started Guide](./getting-started.md) and build your first gRPC service in 10 minutes! 🚀
