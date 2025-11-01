---
title: JWT Authentication
description: Secure gRPC services with JWT token authentication
sidebar_label: Authentication
sidebar_position: 6
keywords:
  - grpc authentication
  - grpc jwt
  - grpc security
  - django grpc auth
---

# gRPC JWT Authentication

Secure your gRPC services with JWT token authentication integrated with Django's user system.

## 🎯 Overview

Django-CFG provides built-in JWT authentication for gRPC services:

- ✅ **Django Integration** - Works with Django User model
- ✅ **JWT Standard** - RFC 7519 compliant
- ✅ **Flexible** - Public and protected methods
- ✅ **Automatic** - No manual token verification needed
- ✅ **Request Context** - User available in all methods

## 🔐 How It Works

```mermaid
sequenceDiagram
    participant Client
    participant gRPC as gRPC Server
    participant Auth as JWT Auth Interceptor
    participant DB as Database
    participant Service as gRPC Service

    Client->>gRPC: Call with JWT token<br/>Authorization: Bearer <token>

    gRPC->>Auth: Extract token from metadata
    Auth->>Auth: Decode & verify JWT
    Auth->>Auth: Check expiration

    Auth->>DB: Load User from token.user_id
    DB-->>Auth: User object

    Auth->>Service: Set user in context
    Note over Service: self.get_user() returns User

    Service->>Service: Process request
    Service-->>Client: Response
```

## ⚙️ Configuration

### 1. Enable JWT Authentication

```python
# api/config.py
from django_cfg import GRPCConfig, GRPCAuthConfig

grpc: GRPCConfig = GRPCConfig(
    enabled=True,
    auth=GRPCAuthConfig(
        enabled=True,              # Enable JWT auth
        require_auth=False,        # Don't require for ALL methods
        jwt_algorithm="HS256",     # JWT signing algorithm
    ),
)
```

### 2. Configuration Options

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `enabled` | `bool` | `False` | Enable JWT authentication |
| `require_auth` | `bool` | `False` | Require auth for all methods |
| `jwt_algorithm` | `str` | `"HS256"` | JWT signing algorithm |

**JWT algorithms:**
- `"HS256"` - HMAC with SHA-256 (symmetric, uses Django SECRET_KEY)
- `"RS256"` - RSA with SHA-256 (asymmetric, requires public/private keys)
- `"ES256"` - ECDSA with SHA-256 (asymmetric)

## 🔑 Obtaining JWT Tokens

### 1. Using Django-CFG Accounts

If you have `enable_accounts=True`, use the built-in endpoints:

```bash
# Login with OTP
curl -X POST http://localhost:8000/cfg/accounts/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "admin123",
    "otp_code": "123456"
  }'
```

Response:
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user": {
    "id": 1,
    "username": "admin",
    "email": "admin@example.com"
  }
}
```

### 2. Using Django REST Framework

```python
# views.py
from rest_framework_simplejwt.views import TokenObtainPairView

urlpatterns = [
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
]
```

```bash
curl -X POST http://localhost:8000/api/token/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "admin123"
  }'
```

### 3. Manual Token Generation

```python
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()
user = User.objects.get(username='admin')

# Generate tokens
refresh = RefreshToken.for_user(user)
access_token = str(refresh.access_token)
refresh_token = str(refresh)

print(f"Access Token: {access_token}")
print(f"Refresh Token: {refresh_token}")
```

## 📡 Using JWT Tokens in gRPC

### 1. Add Token to Metadata

Include JWT token in gRPC metadata as `Authorization: Bearer <token>`:

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

<Tabs>
  <TabItem value="python" label="Python" default>

```python
import grpc
from apps.users import user_pb2, user_pb2_grpc

# Connect to gRPC server
channel = grpc.insecure_channel('localhost:50051')
stub = user_pb2_grpc.UserServiceStub(channel)

# JWT token
token = "eyJ0eXAiOiJKV1QiLCJhbGc..."

# Create metadata with token
metadata = [
    ('authorization', f'Bearer {token}'),
]

# Call with authentication
request = user_pb2.GetUserRequest(user_id=1)
response = stub.GetUser(request, metadata=metadata)

print(f"User: {response.username}")
```

  </TabItem>
  <TabItem value="go" label="Go">

```go
package main

import (
    "context"
    "google.golang.org/grpc"
    "google.golang.org/grpc/metadata"
)

func main() {
    conn, _ := grpc.Dial("localhost:50051", grpc.WithInsecure())
    defer conn.Close()

    client := pb.NewUserServiceClient(conn)

    // Create context with JWT token
    token := "eyJ0eXAiOiJKV1QiLCJhbGc..."
    ctx := metadata.AppendToOutgoingContext(
        context.Background(),
        "authorization", "Bearer "+token,
    )

    // Call with authentication
    response, _ := client.GetUser(ctx, &pb.GetUserRequest{
        UserId: 1,
    })

    fmt.Printf("User: %s\n", response.Username)
}
```

  </TabItem>
  <TabItem value="javascript" label="JavaScript">

```javascript
const grpc = require('@grpc/grpc-js');
const protoLoader = require('@grpc/proto-loader');

// Load proto
const packageDefinition = protoLoader.loadSync('user.proto');
const proto = grpc.loadPackageDefinition(packageDefinition);

// Create client
const client = new proto.api.users.UserService(
  'localhost:50051',
  grpc.credentials.createInsecure()
);

// JWT token
const token = 'eyJ0eXAiOiJKV1QiLCJhbGc...';

// Create metadata
const metadata = new grpc.Metadata();
metadata.add('authorization', `Bearer ${token}`);

// Call with authentication
client.getUser(
  { user_id: 1 },
  metadata,
  (error, response) => {
    if (!error) {
      console.log('User:', response.username);
    }
  }
);
```

  </TabItem>
  <TabItem value="curl" label="grpcurl">

```bash
# With grpcurl
grpcurl -plaintext \
  -H 'Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc...' \
  -d '{"user_id": 1}' \
  localhost:50051 api.users.UserService/GetUser
```

  </TabItem>
</Tabs>

## 🔒 Service-Level Authentication

### 1. Public Methods (No Auth Required)

Use `BaseService` for optional authentication:

```python
from django_cfg.apps.grpc.services import BaseService

class UserService(BaseService):
    def GetUser(self, request, context):
        """Public method - no auth required."""
        # Optional: Get user if token provided
        user = self.get_user(context)

        if user:
            # User is authenticated
            print(f"Authenticated as: {user.username}")
        else:
            # Anonymous request
            print("Anonymous request")

        # Continue processing...
```

### 2. Protected Methods (Auth Optional but Checked)

Check authentication in specific methods:

```python
from django_cfg.apps.grpc.services import BaseService

class ProductService(BaseService):
    def GetProduct(self, request, context):
        """Public method."""
        # No auth check - anyone can view

        product = Product.objects.get(id=request.product_id)
        return product_pb2.Product(...)

    def UpdateProduct(self, request, context):
        """Protected method - requires auth."""
        # Require authentication
        user = self.require_user(context)

        # Check permission
        if not user.has_perm('products.change_product'):
            self.abort_permission_denied(context, "No permission")

        # Update product...
```

### 3. Auth Required Service (All Methods)

Use `AuthRequiredService` to require auth for ALL methods:

```python
from django_cfg.apps.grpc.services import AuthRequiredService

class AccountService(AuthRequiredService):
    """All methods require authentication."""

    def GetProfile(self, request, context):
        # self.user is ALWAYS set and authenticated
        user = self.user

        return account_pb2.Profile(
            id=user.id,
            username=user.username,
        )

    def UpdateProfile(self, request, context):
        # User guaranteed to be authenticated
        self.user.bio = request.bio
        self.user.save()

        return account_pb2.Profile(...)
```

## 🎯 Permission Checking

### 1. Check Django Permissions

```python
def UpdateUser(self, request, context):
    user = self.require_user(context)

    # Check if user has permission
    if not self.check_permission(context, 'users.change_user'):
        self.abort_permission_denied(context, "No permission to update users")

    # Update user...
```

### 2. Require Staff Access

```python
def ListAllUsers(self, request, context):
    # Require staff access
    self.require_staff(context)

    # User is guaranteed to be staff here
    users = User.objects.all()
    # ...
```

### 3. Require Superuser Access

```python
def DeleteUser(self, request, context):
    # Require superuser access
    self.require_superuser(context)

    # User is guaranteed to be superuser here
    User.objects.get(id=request.user_id).delete()
    # ...
```

### 4. Custom Permission Logic

```python
def UpdateOrder(self, request, context):
    user = self.require_user(context)
    order = Order.objects.get(id=request.order_id)

    # Custom permission: only order owner or staff can update
    if order.user != user and not user.is_staff:
        self.abort_permission_denied(
            context,
            "You can only update your own orders"
        )

    # Update order...
```

## 🔐 JWT Token Structure

### Token Payload

Django-CFG JWT tokens contain:

```json
{
  "token_type": "access",
  "exp": 1735747200,        // Expiration timestamp
  "iat": 1735660800,        // Issued at timestamp
  "jti": "a1b2c3d4...",     // Token ID
  "user_id": 1              // Django User ID
}
```

### Verification Process

1. **Extract** token from `Authorization` metadata
2. **Decode** JWT using Django SECRET_KEY
3. **Verify** signature and expiration
4. **Load** User from `user_id` in token
5. **Set** user in gRPC context

## 🛡️ Security Best Practices

### 1. Use HTTPS/TLS in Production

```python
# Production: Use secure channel with TLS
import grpc

# Client side
credentials = grpc.ssl_channel_credentials()
channel = grpc.secure_channel('api.example.com:50051', credentials)
```

### 2. Short Token Expiration

```python
# settings.py
from datetime import timedelta

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=15),   # Short expiration
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
}
```

### 3. Use Refresh Tokens

Implement token refresh flow:

```python
# Refresh access token
curl -X POST http://localhost:8000/api/token/refresh/ \
  -H "Content-Type: application/json" \
  -d '{"refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."}'
```

### 4. Validate Token on Every Request

Django-CFG automatically validates tokens on every request:
- ✅ Signature verification
- ✅ Expiration check
- ✅ User existence check

### 5. Use Strong Algorithms

```python
# Production: Use asymmetric signing
auth=GRPCAuthConfig(
    jwt_algorithm="RS256",  # RSA signature
)
```

## 🧪 Testing with Authentication

### Unit Tests

```python
from django.test import TestCase
from rest_framework_simplejwt.tokens import RefreshToken

class UserServiceTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
        )

        # Generate JWT token
        refresh = RefreshToken.for_user(self.user)
        self.access_token = str(refresh.access_token)

    def test_authenticated_request(self):
        # Create metadata with token
        metadata = [
            ('authorization', f'Bearer {self.access_token}'),
        ]

        # Make authenticated request
        request = user_pb2.GetProfileRequest()
        context = MockContext(metadata=metadata)

        response = self.service.GetProfile(request, context)

        self.assertEqual(response.username, 'testuser')
```

## 🚨 Error Handling

### Unauthenticated Requests

```python
# Request without token or invalid token
# Returns: UNAUTHENTICATED status code

try:
    response = stub.GetProfile(request)
except grpc.RpcError as e:
    if e.code() == grpc.StatusCode.UNAUTHENTICATED:
        print("Authentication required")
        # Redirect to login or refresh token
```

### Expired Tokens

```python
# Token has expired
# Returns: UNAUTHENTICATED status code with details

try:
    response = stub.GetProfile(request, metadata=metadata)
except grpc.RpcError as e:
    if e.code() == grpc.StatusCode.UNAUTHENTICATED:
        if "expired" in e.details().lower():
            print("Token expired - please refresh")
            # Refresh access token using refresh token
```

### Insufficient Permissions

```python
# User doesn't have required permission
# Returns: PERMISSION_DENIED status code

try:
    response = stub.DeleteUser(request, metadata=metadata)
except grpc.RpcError as e:
    if e.code() == grpc.StatusCode.PERMISSION_DENIED:
        print("You don't have permission for this action")
```

## 📚 Related Documentation

- **[Backend Guide](./backend-guide.md)** - Using auth in services
- **[Setup Guide](./setup.md)** - Authentication configuration
- **[Architecture](./architecture.md)** - Auth interceptor flow
- **[Monitoring](./monitoring.md)** - Track authenticated requests

---

**Next:** Learn about [service discovery](./discovery.md) or explore [monitoring](./monitoring.md).
