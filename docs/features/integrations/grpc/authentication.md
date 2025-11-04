---
title: Authentication
description: Securing your gRPC services with API keys
sidebar_label: Authentication
sidebar_position: 5
keywords:
  - grpc authentication
  - api key authentication
  - grpc security
---

# gRPC Authentication

Learn how to secure your gRPC services with API keys.

## 🎯 Overview

Django-CFG gRPC uses **API Key authentication** for secure service access:

| Method | Best For | Management | Lifespan |
|--------|----------|------------|----------|
| **API Keys** | Services, CLI tools, webhooks, all use cases | Django Admin | Long-lived (configurable) |

:::note Historical Note
Django-CFG previously supported JWT authentication for gRPC. As of **v1.5.8**, we've migrated to API Key authentication only for better security and manageability.

**API Keys provide:**
- Centralized management through Django Admin
- Easy revocation without changing secrets
- Per-service key tracking
- Usage statistics and monitoring
- No token expiration complexity
:::

## 🔑 API Key Authentication

### Concept

API keys are long-lived tokens for machine-to-machine communication:
- Create keys in Django Admin
- Each key authenticates as a specific user
- Can be revoked instantly
- Usage is tracked automatically

### Creating Keys

**Via Django Admin:**

1. Go to `/admin/` → **gRPC API Keys**
2. Click "Add gRPC API Key"
3. Fill in name, user, type, expiration
4. Save and copy the generated key

### Using Keys

**With grpcurl:**
```bash
grpcurl -H "x-api-key: YOUR_API_KEY" \
  localhost:50051 api.users.UserService/GetUser
```

**With Python client:**
```python
import grpc

# Add API key to metadata
metadata = [('x-api-key', 'YOUR_API_KEY')]

with grpc.insecure_channel('localhost:50051') as channel:
    stub = UserServiceStub(channel)
    response = stub.GetUser(request, metadata=metadata)
```

**In service:**
```python
class UserService(BaseService):
    def UpdateProfile(self, request, context):
        # Access authenticated user
        user = context.user  # Set by API key auth

        # Also access the API key used
        api_key = context.api_key  # Which key was used

        user.bio = request.bio
        user.save()
        return UserResponse(...)
```

### Development Shortcut

For development, you can use Django's `SECRET_KEY`:

```bash
# Use SECRET_KEY instead of creating API key
grpcurl -H "x-api-key: django-insecure-dev-key..." \
  localhost:50051 api.users.UserService/GetUser
```

:::warning
Only use SECRET_KEY in development! Disable in production via `accept_django_secret_key: False`
:::

## 🔧 Configuration

### API Key Settings

```python
# api/config.py
from django_cfg import DjangoConfig, GRPCConfig, GRPCAuthConfig

class MyConfig(DjangoConfig):
    grpc = GRPCConfig(
        enabled=True,
        enabled_apps=["apps.users"],

        # Authentication settings
        auth=GRPCAuthConfig(
            enabled=True,  # Enable authentication
            require_auth=False,  # Allow anonymous by default

            # API Key settings
            api_key_header="x-api-key",  # Header name
            accept_django_secret_key=True,  # Allow SECRET_KEY (dev only!)

            # Public methods (no auth needed)
            public_methods=[
                "/grpc.health.v1.Health/Check",
            ],
        ),
    )
```

### Authentication Modes

**1. Disabled (Development):**
```python
auth=GRPCAuthConfig(
    enabled=False,  # All methods public
)
```

**2. Optional Auth (Recommended):**
```python
auth=GRPCAuthConfig(
    enabled=True,
    require_auth=False,  # Some methods can be public
    api_key_header="x-api-key",
    accept_django_secret_key=True,  # Allow SECRET_KEY for dev
)
```

**3. Required Auth (Strict):**
```python
auth=GRPCAuthConfig(
    enabled=True,
    require_auth=True,  # All methods require API key
    api_key_header="x-api-key",
    accept_django_secret_key=False,  # Production: only DB keys
    public_methods=[
        "/grpc.health.v1.Health/Check",  # Except health check
    ],
)
```

## 🛡️ Service Authorization

### Public Methods

```python
class UserService(BaseService):
    def GetUser(self, request, context):
        # No auth required - anyone can call
        user = User.objects.get(id=request.user_id)
        return UserResponse(...)
```

### Protected Methods

```python
class UserService(BaseService):
    def UpdateProfile(self, request, context):
        # Require authentication
        user = self.require_user(context)

        user.bio = request.bio
        user.save()
        return UserResponse(...)
```

### Permission Checks

```python
class UserService(BaseService):
    def DeleteUser(self, request, context):
        # Require staff permission
        self.require_staff(context)

        User.objects.get(id=request.user_id).delete()
        return Empty()
```

## 📊 Monitoring

### View Logs

All authenticated requests are logged with:
- Which user made the request
- Which API key was used (if applicable)
- Request duration and status

**Django Admin:**
```
/admin/ → gRPC Request Logs
```

Filter by:
- User
- API Key
- Status (success/error)
- Date range

### Check API Key Usage

**Django Admin:**
```
/admin/ → gRPC API Keys
```

See for each key:
- Total request count
- Last used timestamp
- Status (active/expired/revoked)

## 🔒 Best Practices

### API Keys

✅ **DO:**
- Create separate keys for each service
- Set expiration dates for better security
- Revoke unused keys regularly
- Monitor usage in Django Admin
- Disable `accept_django_secret_key` in production
- Use descriptive names (e.g., "Analytics Service", "Mobile App Backend")
- Track usage statistics regularly

❌ **DON'T:**
- Share keys between services
- Use SECRET_KEY in production
- Hardcode keys in source code
- Leave expired keys active
- Create keys without expiration dates in production

## 📚 Common Patterns

### Service-to-Service Communication

```python
# Service A calls Service B
# 1. Create API key for Service A in Django Admin
# 2. Store key in Service A's environment variables
# 3. Service A includes key in metadata

# Service A (caller)
import os
metadata = [('x-api-key', os.getenv('SERVICE_B_API_KEY'))]
response = service_b_stub.Method(request, metadata=metadata)
```

### CLI Tools

```bash
# Create API key for CLI tool
# 1. Go to Django Admin → gRPC API Keys
# 2. Create key with type "cli"
# 3. Copy key and store securely

# Use in CLI tool
grpcurl -H "x-api-key: YOUR_CLI_API_KEY" \
  localhost:50051 api.users.UserService/GetUser
```

### Webhook Handlers

```python
# Webhook service calling gRPC
# 1. Create API key with type "webhook"
# 2. Configure webhook handler

from django.views.decorators.csrf import csrf_exempt
import grpc

@csrf_exempt
def webhook_handler(request):
    # Parse webhook data
    data = json.loads(request.body)

    # Call gRPC with API key
    metadata = [('x-api-key', settings.WEBHOOK_GRPC_API_KEY)]
    with grpc.insecure_channel('localhost:50051') as channel:
        stub = ServiceStub(channel)
        response = stub.Method(data, metadata=metadata)

    return JsonResponse({'status': 'ok'})
```

### Development Testing

```python
# Use Django SECRET_KEY for quick testing
# (Only works if accept_django_secret_key=True)

from django.conf import settings

metadata = [('x-api-key', settings.SECRET_KEY)]
response = stub.Method(request, metadata=metadata)
```

---

**Next Steps:**
- **[Configuration](./configuration.md)** - Complete auth config reference
- **[Getting Started](./getting-started.md)** - Build authenticated service
- **[FAQ](./faq.md)** - Authentication troubleshooting
