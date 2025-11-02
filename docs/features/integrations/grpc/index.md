---
title: gRPC Integration
description: Django-CFG gRPC integration. Production-ready gRPC server with Django ORM, JWT auth, and service auto-discovery.
sidebar_label: Overview
sidebar_position: 1
keywords:
  - django grpc
  - grpc python
  - django grpc server
  - grpc authentication
  - grpc django integration
---

# gRPC Integration

:::tip[Production-Ready gRPC Server]
Django-CFG's **gRPC Integration** provides a complete gRPC server with Django ORM integration, JWT authentication, request logging, and automatic service discovery. Build high-performance APIs with Protocol Buffers while keeping all Django benefits.
:::

## 🎯 What is gRPC?

[gRPC](https://grpc.io/) is Google's high-performance RPC framework using Protocol Buffers. It's designed for building efficient, type-safe APIs with bidirectional streaming support.

Django-CFG provides a **production-ready gRPC integration** that combines gRPC's performance with Django's rich ecosystem:

- ✅ **Django ORM Integration** - Full database access in gRPC services
- ✅ **JWT Authentication** - Secure token-based auth with Django users
- ✅ **Auto-Discovery** - Automatic service registration from Django apps
- ✅ **Request Logging** - Database logging with beautiful admin interface
- ✅ **Interceptors Pipeline** - Logging, metrics, error handling, auth
- ✅ **Base Service Classes** - Ready-to-use base classes with Django patterns
- ✅ **Management Commands** - `rungrpc` command for easy server startup

## 🚀 Quick Start

### 1. Enable gRPC in Configuration

```python
# api/config.py
from django_cfg import (
    DjangoConfig,
    GRPCConfig,
    GRPCServerConfig,
    GRPCAuthConfig,
    GRPCProtoConfig,
)

class MyConfig(DjangoConfig):
    # Enable gRPC integration
    grpc: Optional[GRPCConfig] = GRPCConfig(
        enabled=True,
        server=GRPCServerConfig(
            host="[::]",              # Listen on all interfaces
            port=50051,               # Standard gRPC port
            max_workers=10,           # Thread pool size
            enable_reflection=True,   # Enable grpcurl support
            enable_health_check=True, # Enable health checking
        ),
        auth=GRPCAuthConfig(
            enabled=True,
            require_auth=False,       # Allow public methods
            jwt_algorithm="HS256",
        ),
        proto=GRPCProtoConfig(
            auto_generate=True,
            output_dir="protos",
            package_prefix="api",
        ),
        # Auto-discover services from these apps
        auto_register_apps=True,
        enabled_apps=["core", "apps.users", "apps.products"],
    )
```

### 2. Create a gRPC Service

```python
# apps/users/grpc_services.py
from django_cfg.apps.grpc.services import BaseService
from django.contrib.auth import get_user_model

User = get_user_model()

class UserService(BaseService):
    """User management gRPC service."""

    def GetUser(self, request, context):
        """Get user by ID (public method)."""
        try:
            user = User.objects.get(id=request.user_id)
            return user_pb2.User(
                id=user.id,
                username=user.username,
                email=user.email,
            )
        except User.DoesNotExist:
            self.abort_not_found(context, "User not found")

    def UpdateProfile(self, request, context):
        """Update user profile (requires authentication)."""
        # Get authenticated user from JWT token
        user = self.require_user(context)

        # Update profile
        user.bio = request.bio
        user.save()

        return user_pb2.User(
            id=user.id,
            username=user.username,
            bio=user.bio,
        )
```

### 3. Run gRPC Server

```bash
# Start gRPC server
python manage.py rungrpc

# Or specify custom host/port
python manage.py rungrpc --host 0.0.0.0 --port 50051 --workers 20
```

### 4. Test with grpcurl

```bash
# List available services (requires reflection)
grpcurl -plaintext localhost:50051 list

# Call a method
grpcurl -plaintext -d '{"user_id": 1}' \
  localhost:50051 api.users.UserService/GetUser

# With authentication
grpcurl -plaintext \
  -H 'Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc...' \
  -d '{"bio": "New bio"}' \
  localhost:50051 api.users.UserService/UpdateProfile
```

## 📊 Key Features

### 🔍 Auto-Discovery

Services are automatically discovered from Django apps:

```python
# Django-CFG will automatically find services in these locations:
apps/users/
├── grpc_services.py    # ✅ Discovered
├── grpc_handlers.py    # ✅ Discovered
└── services/
    └── grpc.py         # ✅ Discovered
```

No manual registration needed - just define your service classes!

### 🔐 JWT Authentication

Built-in JWT authentication with Django user integration:

```python
class UserService(BaseService):
    def GetProfile(self, request, context):
        # Automatically extracts user from JWT token
        user = self.require_user(context)

        # Check permissions
        self.check_permission(context, "users.view_profile")

        # Or require staff access
        self.require_staff(context)
```

### 📝 Request Logging

All gRPC requests are automatically logged to the database:

```python
# View logs in Django admin
/admin/grpc/grpcrequestlog/

# Or via REST API
GET /cfg/grpc/monitor/overview/
GET /cfg/grpc/monitor/requests/
GET /cfg/grpc/monitor/services/
GET /cfg/grpc/monitor/timeline/
```

**Tracked metrics:**
- Request ID (UUID)
- Service & method name
- Duration (milliseconds)
- Request/response sizes
- gRPC status code
- Client IP, user agent
- Authenticated user
- Error details

### 🎨 Base Service Classes

Ready-to-use base classes with Django patterns:

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

<Tabs>
  <TabItem value="base" label="BaseService" default>

```python
from django_cfg.apps.grpc.services import BaseService

class MyService(BaseService):
    """Full-featured base service."""

    def MyMethod(self, request, context):
        # Access Django ORM
        obj = MyModel.objects.get(id=request.id)

        # Get authenticated user (optional)
        user = self.get_user(context)

        # Abort with status codes
        self.abort_not_found(context, "Not found")
        self.abort_permission_denied(context, "No access")
        self.abort_invalid_argument(context, "Invalid data")
```

  </TabItem>
  <TabItem value="readonly" label="ReadOnlyService">

```python
from django_cfg.apps.grpc.services import ReadOnlyService

class MyReadOnlyService(ReadOnlyService):
    """Read-only service (no write operations)."""

    def GetData(self, request, context):
        # Only SELECT queries allowed
        return MyModel.objects.filter(active=True)
```

  </TabItem>
  <TabItem value="auth" label="AuthRequiredService">

```python
from django_cfg.apps.grpc.services import AuthRequiredService

class MySecureService(AuthRequiredService):
    """All methods require authentication."""

    def GetPrivateData(self, request, context):
        # User is always present and authenticated
        user = self.user  # Set by base class

        return user.get_private_data()
```

  </TabItem>
</Tabs>

### ⚡ Interceptors Pipeline

Built-in interceptors for common tasks:

1. **RequestLoggerInterceptor** - Logs all requests to database
2. **LoggingInterceptor** - Structured console logging (dev mode)
3. **JWTAuthInterceptor** - JWT token verification
4. **ErrorHandlerInterceptor** - Django exception mapping
5. **MetricsInterceptor** - Performance metrics collection

**Execution order:**
```
Request → Logger → Logging → Auth → Error → Metrics → Service → Response
```

## 🏗️ Architecture Overview

```mermaid
graph TB
    subgraph "Client Layer"
        GrpcClient["gRPC Client<br/>(Python/Go/JS/etc)"]
    end

    subgraph "gRPC Server"
        subgraph "Interceptors Pipeline"
            I1["1️⃣ Request Logger<br/>(DB Logging)"]
            I2["2️⃣ Console Logger<br/>(Dev Mode)"]
            I3["3️⃣ JWT Auth<br/>(User Context)"]
            I4["4️⃣ Error Handler<br/>(Exception Mapping)"]
        end

        subgraph "Service Layer"
            Discovery["Service Discovery<br/>(Auto-register)"]
            BaseService["Base Service Classes<br/>(Django Integration)"]
        end

        subgraph "Business Logic"
            UserService["User Service"]
            ProductService["Product Service"]
            CustomService["Custom Services"]
        end
    end

    subgraph "Django Layer"
        ORM["Django ORM"]
        Auth["Django Auth"]
        Models["Django Models"]
    end

    subgraph "Admin & Monitoring"
        AdminUI["Django Admin<br/>(Request Logs)"]
        MonitorAPI["REST API<br/>(Monitoring)"]
    end

    GrpcClient -->|"gRPC Call"| I1
    I1 --> I2
    I2 --> I3
    I3 --> I4
    I4 --> Discovery
    Discovery --> BaseService
    BaseService --> UserService
    BaseService --> ProductService
    BaseService --> CustomService

    UserService --> ORM
    ProductService --> ORM
    CustomService --> ORM

    BaseService --> Auth
    Auth --> Models
    ORM --> Models

    I1 -.->|"Log to DB"| AdminUI
    I1 -.->|"Metrics"| MonitorAPI

    style I1 fill:#e1f5ff
    style I3 fill:#fff3e0
    style BaseService fill:#f3e5f5
    style AdminUI fill:#e8f5e9
```

## 🔄 Request Flow

```mermaid
sequenceDiagram
    participant Client as gRPC Client
    participant Server as gRPC Server
    participant Logger as Request Logger
    participant Auth as JWT Auth
    participant Service as User Service
    participant ORM as Django ORM
    participant DB as Database

    Client->>Server: GetUser(user_id=1)
    Note over Server: Interceptors Pipeline

    Server->>Logger: Log request start
    Logger->>DB: Create GRPCRequestLog

    Server->>Auth: Extract JWT token
    Auth->>DB: Load User from token
    Auth-->>Server: Set user in context

    Server->>Service: Call GetUser()
    Service->>ORM: User.objects.get(id=1)
    ORM->>DB: SELECT FROM users
    DB-->>ORM: User data
    ORM-->>Service: User instance
    Service-->>Server: User protobuf

    Server->>Logger: Log request complete
    Logger->>DB: Update GRPCRequestLog<br/>(status, duration)

    Server-->>Client: User response

    Note over Client,DB: Total time logged to database
```

## 📖 Integration Highlights

### Django ORM Access

Full Django ORM access in gRPC services:

```python
class ProductService(BaseService):
    def SearchProducts(self, request, context):
        # Use Django ORM with all features
        products = Product.objects.filter(
            category=request.category,
            price__lte=request.max_price,
            active=True
        ).select_related('category').prefetch_related('tags')

        for product in products:
            yield product_pb2.Product(
                id=product.id,
                name=product.name,
                price=str(product.price),
            )
```

### Django Authentication

Seamless integration with Django auth:

```python
class OrderService(BaseService):
    def CreateOrder(self, request, context):
        # Get authenticated user from JWT
        user = self.require_user(context)

        # Check Django permissions
        if not user.has_perm('orders.add_order'):
            self.abort_permission_denied(context, "Cannot create orders")

        # Use Django models
        order = Order.objects.create(
            user=user,
            total=request.total
        )

        return order_pb2.Order(id=order.id)
```

### Automatic Discovery

Services are auto-discovered from Django apps:

```python
# config.py
grpc: GRPCConfig = GRPCConfig(
    enabled=True,
    auto_register_apps=True,
    enabled_apps=["apps.users", "apps.products", "apps.orders"],
)

# Services are automatically found in:
# - apps/users/grpc_services.py
# - apps/products/grpc_services.py
# - apps/orders/grpc_services.py
```

## 📚 Documentation Sections

Explore the complete gRPC integration documentation:

- **[Architecture](./architecture.md)** - Detailed architecture and design patterns
- **[Setup Guide](./setup.md)** - Installation and configuration
- **[Backend Guide](./backend-guide.md)** - Creating gRPC services
- **[Authentication](./authentication.md)** - JWT auth setup and usage
- **[Monitoring](./monitoring.md)** - Request logging and metrics

## 🎯 Use Cases

### High-Performance APIs

Build efficient APIs for:
- **Microservices** - Service-to-service communication
- **Mobile Apps** - Low latency, binary protocol
- **IoT Devices** - Efficient data transfer
- **Real-time Systems** - Bidirectional streaming

### Django Integration

Combine gRPC with Django features:
- **ORM Queries** - Full database access
- **Authentication** - Django users and permissions
- **Admin Interface** - Monitor requests in admin
- **Signals** - Django signals in gRPC services
- **Middleware** - Django middleware patterns

## 🚀 Getting Started

Ready to build your first gRPC service?

1. **[Setup Guide](./setup.md)** - Configure gRPC in your project
2. **[Backend Guide](./backend-guide.md)** - Create your first service
3. **[Authentication](./authentication.md)** - Secure your services with JWT

---

**Next Steps:**
- 📖 Read the [Setup Guide](./setup.md) to configure gRPC
- 🔨 Follow the [Backend Guide](./backend-guide.md) to create services
- 🔍 Explore [Architecture](./architecture.md) for design patterns
