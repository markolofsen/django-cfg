---
title: Getting Started
description: Build your first gRPC service with Django-CFG in 10 minutes
sidebar_label: Getting Started
sidebar_position: 3
keywords:
  - grpc tutorial
  - grpc quickstart
  - grpc getting started
---

# Getting Started with gRPC

Build your first production-ready gRPC service in 10 minutes.

## 📋 Prerequisites

- Django project with django-cfg installed
- Python 3.8+
- Basic understanding of Protocol Buffers

## 🚀 Quick Start

### Step 1: Install gRPC Dependencies

```bash
# Install all gRPC packages at once
pip install django-cfg[grpc]

# Or install manually
pip install grpcio grpcio-tools grpcio-reflection grpcio-health-checking protobuf
```

Verify installation:
```bash
python -c "import grpc; print(f'gRPC {grpc.__version__}')"
# Output: gRPC 1.60.0
```

### Step 2: Enable gRPC in Configuration

```python
# api/config.py
from typing import Optional
from django_cfg import (
    DjangoConfig,
    GRPCConfig,
    GRPCServerConfig,
    GRPCAuthConfig,
)

class MyConfig(DjangoConfig):
    # ... your existing config ...

    # Enable gRPC
    grpc: Optional[GRPCConfig] = GRPCConfig(
        enabled=True,
        server=GRPCServerConfig(
            host="[::]",              # Listen on all interfaces
            port=50051,               # Standard gRPC port
            max_workers=10,           # Thread pool size
            enable_reflection=True,   # Enable for grpcurl/testing
            enable_health_check=True, # Health check endpoint
        ),
        auth=GRPCAuthConfig(
            enabled=False,  # Disable auth for now (development)
            # Or enable API key auth:
            # enabled=True,
            # require_auth=False,
            # accept_django_secret_key=True,  # Allow SECRET_KEY for dev
        ),
        # Auto-discover services from these apps
        auto_register_apps=True,
        enabled_apps=[
            "apps.users",      # Your apps here
            "apps.products",
        ],
    )
```

### Step 3: Run Migrations

```bash
python manage.py migrate
```

This creates the `GRPCRequestLog` table for logging.

### Step 4: Create Your First Service

Create `apps/users/grpc_services.py`:

```python
from django_cfg.apps.integrations.grpc.services import BaseService
from django.contrib.auth import get_user_model
from google.protobuf import empty_pb2
import grpc

User = get_user_model()

# Simple protobuf message classes (or import from generated .proto files)
class UserResponse:
    def __init__(self, id, username, email):
        self.id = id
        self.username = username
        self.email = email

class UserService(BaseService):
    """User management gRPC service."""

    def GetUser(self, request, context):
        """
        Get user by ID.

        Request: { user_id: int }
        Response: { id: int, username: str, email: str }
        """
        try:
            user = User.objects.get(id=request.user_id)

            # Return user data
            response = UserResponse(
                id=user.id,
                username=user.username,
                email=user.email or "",
            )
            return response

        except User.DoesNotExist:
            # Abort with NOT_FOUND status
            self.abort_not_found(context, f"User {request.user_id} not found")

    def ListUsers(self, request, context):
        """
        List all users (streaming response).

        Request: empty or { limit: int }
        Response: stream of User objects
        """
        # Get users
        users = User.objects.filter(is_active=True)

        # Apply limit if provided
        limit = getattr(request, 'limit', 100)
        users = users[:limit]

        # Stream users one by one
        for user in users:
            yield UserResponse(
                id=user.id,
                username=user.username,
                email=user.email or "",
            )

    def CreateUser(self, request, context):
        """
        Create new user (requires authentication).

        Request: { username: str, email: str, password: str }
        Response: { id: int, username: str, email: str }
        """
        # Require authentication (if auth enabled)
        # user = self.require_user(context)

        # Validate
        if not request.username:
            self.abort_invalid_argument(context, "Username is required")

        # Check if exists
        if User.objects.filter(username=request.username).exists():
            self.abort_already_exists(context, "Username already taken")

        # Create user
        user = User.objects.create_user(
            username=request.username,
            email=request.email,
            password=request.password,
        )

        return UserResponse(
            id=user.id,
            username=user.username,
            email=user.email,
        )
```

**That's it!** The service is automatically discovered and registered.

### Step 5: Start gRPC Server

```bash
python manage.py rungrpc
```

Expected output:
```
🚀 Starting gRPC server...
📡 Server running at [::]:50051
🔍 Reflection enabled
❤️  Health check enabled
✅ Registered 1 service:
   - api.users.UserService
```

### Step 6: Test Your Service

**Option 1: Using grpcurl (recommended for testing)**

```bash
# List services
grpcurl -plaintext localhost:50051 list

# Output:
# api.users.UserService
# grpc.health.v1.Health
# grpc.reflection.v1alpha.ServerReflection

# Describe service
grpcurl -plaintext localhost:50051 describe api.users.UserService

# Call GetUser
grpcurl -plaintext -d '{"user_id": 1}' \
  localhost:50051 api.users.UserService/GetUser

# Output (example):
# {
#   "id": 1,
#   "username": "admin",
#   "email": "admin@example.com"
# }
```

**Option 2: Using Python client**

```python
# test_client.py
import grpc
from django_cfg.apps.integrations.grpc.services.grpc_client import DynamicGRPCClient

# Create client
client = DynamicGRPCClient(host="localhost", port=50051)

# Invoke method
response = client.invoke_method(
    service="api.users.UserService",
    method="GetUser",
    request_data={"user_id": 1}
)

print(response)
# {'id': 1, 'username': 'admin', 'email': 'admin@example.com'}
```

**Option 3: Django Admin**

View request logs in Django Admin:
```
http://localhost:8000/admin/integrations/grpc/grpcrequestlog/
```

## 🎯 Add Authentication

### Option 1: API Key Authentication (Recommended)

API keys are perfect for service-to-service communication and CLI tools.

#### Step 1: Enable API Key Auth

```python
# api/config.py
grpc: GRPCConfig = GRPCConfig(
    auth=GRPCAuthConfig(
        enabled=True,
        require_auth=False,  # Optional auth (some methods public)
        api_key_header="x-api-key",
        accept_django_secret_key=True,  # Allow SECRET_KEY for dev/internal
        public_methods=[
            "/grpc.health.v1.Health/Check",
        ],
    ),
)
```

#### Step 2: Create API Key

Via Django Admin:
```
1. Open /admin/integrations/grpc/grpcapikey/
2. Click "Add gRPC API Key"
3. Fill in:
   - Name: "Analytics Service"
   - Description: "Internal analytics microservice"
   - User: Select user to authenticate as
   - Type: Service
   - Expires at: Optional (e.g., 1 year from now)
4. Click "Save"
5. Copy the generated API key from the detail page
```

Or programmatically:
```python
from django_cfg.apps.integrations.grpc.models import GrpcApiKey
from django.contrib.auth import get_user_model

User = get_user_model()
admin_user = User.objects.filter(is_superuser=True).first()

# Create API key
api_key = GrpcApiKey.objects.create_for_user(
    user=admin_user,
    name="Analytics Service",
    description="Internal analytics microservice",
    key_type="service",
    expires_in_days=365,  # Expires in 1 year
)

print(f"API Key: {api_key.key}")
# Save this key securely!
```

#### Step 3: Use API Key

With grpcurl:
```bash
grpcurl -plaintext \
  -H "x-api-key: <your_api_key_here>" \
  -d '{"user_id": 1}' \
  localhost:50051 api.users.UserService/GetUser
```

With Python client:
```python
import grpc

channel = grpc.insecure_channel('localhost:50051')
metadata = [('x-api-key', 'your_api_key_here')]

stub = UserServiceStub(channel)
response = stub.GetUser(request, metadata=metadata)
```

For development/internal use with SECRET_KEY:
```bash
# Use Django SECRET_KEY as API key (convenient for dev)
grpcurl -plaintext \
  -H "x-api-key: $(python manage.py shell -c 'from django.conf import settings; print(settings.SECRET_KEY)')" \
  localhost:50051 api.users.UserService/GetUser
```

#### Step 4: Access User in Service

```python
class UserService(BaseService):
    def UpdateProfile(self, request, context):
        # Get authenticated user (from API key)
        user = self.require_user(context)

        # Get API key used for authentication
        api_key = getattr(context, 'api_key', None)
        if api_key:
            print(f"Request from API key: {api_key.name}")

        # Update profile
        user.bio = request.bio
        user.save()

        return UserResponse(...)
```

#### Step 5: Monitor Usage

View API key usage in Django Admin:
```
/admin/integrations/grpc/grpcapikey/
```

Each API key shows:
- Total request count
- Last used timestamp
- Status (active/expired/revoked)
- Associated request logs

Or programmatically:
```python
from django_cfg.apps.integrations.grpc.models import GrpcApiKey

# Get API key
api_key = GrpcApiKey.objects.get(name="Analytics Service")

print(f"Request count: {api_key.request_count}")
print(f"Last used: {api_key.last_used_at}")
print(f"Is valid: {api_key.is_valid}")

# View requests made with this key
logs = api_key.request_logs.all()[:10]
```

### Option 2: JWT Authentication

JWT is perfect for user-facing applications.

#### Step 1: Enable JWT Auth

```python
# api/config.py
grpc: GRPCConfig = GRPCConfig(
    auth=GRPCAuthConfig(
        enabled=True,           # Enable JWT auth
        require_auth=False,     # Don't require for all methods
        jwt_algorithm="HS256",
    ),
)
```

#### Step 2: Protect Methods

```python
# apps/users/grpc_services.py
class UserService(BaseService):
    def GetUser(self, request, context):
        # Public method - no auth required
        pass

    def UpdateProfile(self, request, context):
        # Protected method - auth required
        user = self.require_user(context)  # Requires JWT token

        user.bio = request.bio
        user.save()

        return UserResponse(...)

    def DeleteUser(self, request, context):
        # Admin only
        self.require_staff(context)  # Requires staff permission

        User.objects.get(id=request.user_id).delete()
        return empty_pb2.Empty()
```

#### Step 3: Get JWT Token

```bash
# Login to get token
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'

# Response:
# {
#   "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
#   "refresh_token": "..."
# }
```

#### Step 4: Call with Authentication

```bash
# grpcurl with token
grpcurl -plaintext \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc..." \
  -d '{"bio": "New bio"}' \
  localhost:50051 api.users.UserService/UpdateProfile
```

### Combining API Key and JWT

You can use both authentication methods simultaneously:

```python
grpc: GRPCConfig = GRPCConfig(
    auth=GRPCAuthConfig(
        enabled=True,
        require_auth=False,
        # API key auth settings
        api_key_header="x-api-key",
        accept_django_secret_key=True,
        # JWT auth settings
        jwt_algorithm="HS256",
    ),
)
```

The auth flow:
1. First checks for API key in `x-api-key` header
2. If found and valid, authenticates as API key's user
3. If not found, checks for JWT in `Authorization` header
4. If found and valid, authenticates as JWT's user
5. If neither, allows anonymous access (if `require_auth=False`)

## 📊 Monitor Requests

### View in Django Admin

All requests are automatically logged:

1. Open Django Admin: `http://localhost:8000/admin/`
2. Go to: **Integrations → gRPC Request Logs**
3. Filter by:
   - Service name
   - Method name
   - Status (success/error)
   - User
   - Date range

### Query Programmatically

```python
from django_cfg.apps.integrations.grpc.models import GRPCRequestLog

# Recent requests
recent = GRPCRequestLog.objects.recent(hours=1)

# Errors only
errors = GRPCRequestLog.objects.filter(status='error')

# Statistics
stats = GRPCRequestLog.objects.get_statistics(hours=24)
print(f"Success rate: {stats['success_rate']}%")
print(f"Avg duration: {stats['avg_duration_ms']}ms")

# Per-service stats
for service in ['UserService', 'ProductService']:
    logs = GRPCRequestLog.objects.by_service(service)
    print(f"{service}: {logs.count()} requests")
```

## 🛠️ Development Tips

### 1. Enable Debug Logging

```python
# settings.py
LOGGING = {
    'loggers': {
        'django_cfg.apps.integrations.grpc': {
            'level': 'DEBUG',
            'handlers': ['console'],
        },
    },
}
```

### 2. Hot Reload in Development

The server automatically reloads when you change code (like Django runserver).

### 3. Use Base Service Helpers

```python
class MyService(BaseService):
    def MyMethod(self, request, context):
        # Helpers available:
        self.get_user(context)           # Optional user
        self.require_user(context)       # Required user
        self.require_staff(context)      # Staff only
        self.require_superuser(context)  # Superuser only
        self.check_permission(context, "app.perm")

        # Abort methods:
        self.abort_not_found(context, "Not found")
        self.abort_permission_denied(context, "No access")
        self.abort_invalid_argument(context, "Bad request")
        self.abort_already_exists(context, "Duplicate")
```

### 4. Test with Different Ports

```bash
# Run on different port
python manage.py rungrpc --port 50052

# Run with more workers
python manage.py rungrpc --workers 20
```

## 🎓 Common Patterns

### Pattern 1: CRUD Service

```python
class ProductService(BaseService):
    def GetProduct(self, request, context):
        # Read
        product = Product.objects.get(id=request.id)
        return product_pb2.Product(...)

    def CreateProduct(self, request, context):
        # Create
        user = self.require_user(context)
        product = Product.objects.create(
            name=request.name,
            price=request.price,
        )
        return product_pb2.Product(...)

    def UpdateProduct(self, request, context):
        # Update
        user = self.require_user(context)
        product = Product.objects.get(id=request.id)
        product.name = request.name
        product.save()
        return product_pb2.Product(...)

    def DeleteProduct(self, request, context):
        # Delete
        self.require_staff(context)
        Product.objects.get(id=request.id).delete()
        return empty_pb2.Empty()
```

### Pattern 2: Streaming Service

```python
class EventService(BaseService):
    def StreamEvents(self, request, context):
        # Server-side streaming
        events = Event.objects.filter(user_id=request.user_id)

        for event in events:
            yield event_pb2.Event(
                id=event.id,
                type=event.type,
                data=event.data,
            )
```

### Pattern 3: Read-Only Service

```python
from django_cfg.apps.integrations.grpc.services import ReadOnlyService

class CatalogService(ReadOnlyService):
    """Read-only catalog browsing."""

    def SearchProducts(self, request, context):
        # Only queries allowed (no writes)
        products = Product.objects.filter(
            category=request.category,
            active=True,
        )[:100]

        for product in products:
            yield product_pb2.Product(...)
```

## 🚨 Common Issues

**Issue: Port already in use**
```bash
# Kill existing process
lsof -ti :50051 | xargs kill -9

# Or use different port
python manage.py rungrpc --port 50052
```

**Issue: Service not found**
- Check file name: `grpc_services.py` (not `grpc_service.py`)
- Check app in `enabled_apps`
- Check class inherits from `BaseService`

**Issue: Import errors**
```python
# Wrong import
from django_cfg.apps.grpc.services import BaseService  # ❌

# Correct import
from django_cfg.apps.integrations.grpc.services import BaseService  # ✅
```

## 📚 Next Steps

Now that you have a working service:

1. **[Concepts](./concepts.md)** - Understand architecture and patterns
2. **[Authentication](./authentication.md)** - Deep dive into API keys and JWT
3. **[Configuration](./configuration.md)** - Explore all config options
4. **[Dynamic Invocation](./dynamic-invocation.md)** - Test without proto files
5. **[FAQ](./faq.md)** - Common questions and solutions

## 💡 Key Takeaways

- ✅ Services are **auto-discovered** from `grpc_services.py`
- ✅ Use **base classes** for common patterns
- ✅ **Django ORM** works out of the box
- ✅ **API key auth** is simple and secure with admin interface
- ✅ **JWT auth** integrates with Django users
- ✅ All requests are **automatically logged** with API key tracking
- ✅ **Server monitoring** tracks uptime and registered services
- ✅ Use **grpcurl** for testing during development

**Congratulations!** You've built your first production-ready gRPC service with Django-CFG. 🎉
