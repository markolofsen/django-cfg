---
title: Backend Development Guide
description: Learn how to create gRPC services with Django-CFG
sidebar_label: Backend Guide
sidebar_position: 4
keywords:
  - grpc services
  - grpc backend
  - django grpc development
  - grpc tutorial
---

# gRPC Backend Development Guide

Learn how to create gRPC services with Django-CFG's powerful base classes and Django integration.

## 🎯 Quick Start

### 1. Create Your First Service

Create a file `grpc_services.py` in your Django app:

```python
# apps/users/grpc_services.py
from django_cfg.apps.grpc.services import BaseService
from django.contrib.auth import get_user_model
from . import user_pb2  # Generated from .proto file

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
```

### 2. Auto-Discovery

That's it! The service is automatically discovered and registered when you run:

```bash
python manage.py rungrpc
```

Expected output:
```
✅ Registered 1 service:
   - api.users.UserService
```

## 🏗️ Base Service Classes

Django-CFG provides three base service classes:

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

<Tabs>
  <TabItem value="base" label="BaseService" default>

### BaseService

Full-featured base service with Django integration.

**Use when:** You need full Django ORM, authentication, and permission support.

```python
from django_cfg.apps.grpc.services import BaseService

class MyService(BaseService):
    def MyMethod(self, request, context):
        # Get authenticated user (optional)
        user = self.get_user(context)

        # Access Django ORM
        obj = MyModel.objects.get(id=request.id)

        # Abort with gRPC status codes
        self.abort_not_found(context, "Not found")
```

**Features:**
- ✅ Django ORM access
- ✅ Optional user authentication
- ✅ Permission checking
- ✅ Abort helper methods
- ✅ Context utilities

  </TabItem>
  <TabItem value="readonly" label="ReadOnlyService">

### ReadOnlyService

Read-only service for queries and searches.

**Use when:** Service only reads data (no writes/updates).

```python
from django_cfg.apps.grpc.services import ReadOnlyService

class ProductCatalogService(ReadOnlyService):
    def SearchProducts(self, request, context):
        # Only SELECT queries allowed
        products = Product.objects.filter(
            category=request.category,
            active=True
        )

        for product in products:
            yield product_pb2.Product(
                id=product.id,
                name=product.name,
            )
```

**Features:**
- ✅ Django ORM (read-only)
- ✅ No write operations
- ✅ Optimized for queries
- ✅ Streaming support

  </TabItem>
  <TabItem value="auth" label="AuthRequiredService">

### AuthRequiredService

All methods require authentication.

**Use when:** All service methods need authenticated user.

```python
from django_cfg.apps.grpc.services import AuthRequiredService

class AccountService(AuthRequiredService):
    def GetProfile(self, request, context):
        # self.user is always set and authenticated
        user = self.user

        return account_pb2.Profile(
            id=user.id,
            username=user.username,
            email=user.email,
        )

    def UpdateProfile(self, request, context):
        # User is guaranteed to be authenticated
        self.user.bio = request.bio
        self.user.save()

        return account_pb2.Profile(...)
```

**Features:**
- ✅ User always authenticated
- ✅ `self.user` property available
- ✅ Auto-reject unauthenticated requests
- ✅ Simplified code (no auth checks needed)

  </TabItem>
</Tabs>

## 🔧 BaseService API Reference

### User Authentication

#### get_user(context) → User | None

Get authenticated user from JWT token (optional).

```python
def MyMethod(self, request, context):
    user = self.get_user(context)

    if user:
        # User is authenticated
        print(f"User: {user.username}")
    else:
        # Anonymous request
        print("Anonymous user")
```

#### require_user(context) → User

Require authenticated user (aborts if not authenticated).

```python
def MyMethod(self, request, context):
    # Aborts with UNAUTHENTICATED if no user
    user = self.require_user(context)

    # User is guaranteed to be authenticated here
    print(f"User: {user.username}")
```

### Permission Checking

#### check_permission(context, permission: str) → bool

Check if user has permission.

```python
def MyMethod(self, request, context):
    user = self.require_user(context)

    # Check permission (returns bool)
    has_perm = self.check_permission(context, "users.change_user")

    if not has_perm:
        self.abort_permission_denied(context, "No permission")
```

#### require_staff(context)

Require user to be staff.

```python
def AdminMethod(self, request, context):
    # Aborts with PERMISSION_DENIED if not staff
    self.require_staff(context)

    # User is guaranteed to be staff here
```

#### require_superuser(context)

Require user to be superuser.

```python
def SuperAdminMethod(self, request, context):
    # Aborts with PERMISSION_DENIED if not superuser
    self.require_superuser(context)

    # User is guaranteed to be superuser here
```

### Abort Methods

Helper methods to abort requests with gRPC status codes:

#### abort_not_found(context, message)

Abort with `NOT_FOUND` status.

```python
try:
    user = User.objects.get(id=request.user_id)
except User.DoesNotExist:
    self.abort_not_found(context, "User not found")
```

#### abort_permission_denied(context, message)

Abort with `PERMISSION_DENIED` status.

```python
if not user.has_perm("orders.create_order"):
    self.abort_permission_denied(context, "Cannot create orders")
```

#### abort_invalid_argument(context, message)

Abort with `INVALID_ARGUMENT` status.

```python
if request.quantity <= 0:
    self.abort_invalid_argument(context, "Quantity must be positive")
```

#### abort_unauthenticated(context, message)

Abort with `UNAUTHENTICATED` status.

```python
if not self.get_user(context):
    self.abort_unauthenticated(context, "Authentication required")
```

#### abort_already_exists(context, message)

Abort with `ALREADY_EXISTS` status.

```python
if User.objects.filter(username=request.username).exists():
    self.abort_already_exists(context, "Username already taken")
```

#### abort_internal(context, message)

Abort with `INTERNAL` status.

```python
try:
    # Some operation
    pass
except Exception as e:
    self.abort_internal(context, f"Internal error: {e}")
```

## 📝 Complete Examples

### Example 1: User Management Service

```python
# apps/users/grpc_services.py
from django_cfg.apps.grpc.services import BaseService
from django.contrib.auth import get_user_model
from django.db import transaction
from . import user_pb2

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
                is_active=user.is_active,
            )
        except User.DoesNotExist:
            self.abort_not_found(context, f"User {request.user_id} not found")

    def UpdateProfile(self, request, context):
        """Update user profile (requires authentication)."""
        # Get authenticated user
        user = self.require_user(context)

        # Update fields
        user.first_name = request.first_name
        user.last_name = request.last_name
        user.bio = request.bio
        user.save()

        return user_pb2.User(
            id=user.id,
            username=user.username,
            first_name=user.first_name,
            last_name=user.last_name,
            bio=user.bio,
        )

    def DeleteUser(self, request, context):
        """Delete user (requires staff permission)."""
        # Require staff access
        self.require_staff(context)

        try:
            user = User.objects.get(id=request.user_id)
            user.delete()

            return user_pb2.DeleteUserResponse(success=True)
        except User.DoesNotExist:
            self.abort_not_found(context, "User not found")

    def ListUsers(self, request, context):
        """List users (streaming response)."""
        # Require authentication
        self.require_user(context)

        # Stream users
        users = User.objects.filter(is_active=True)

        for user in users:
            yield user_pb2.User(
                id=user.id,
                username=user.username,
                email=user.email,
            )
```

### Example 2: Product Catalog Service

```python
# apps/products/grpc_services.py
from django_cfg.apps.grpc.services import ReadOnlyService
from .models import Product, Category
from . import product_pb2

class ProductCatalogService(ReadOnlyService):
    """Product catalog search service (read-only)."""

    def GetProduct(self, request, context):
        """Get product by ID."""
        try:
            product = Product.objects.select_related('category').get(
                id=request.product_id
            )

            return product_pb2.Product(
                id=product.id,
                name=product.name,
                description=product.description,
                price=str(product.price),
                category=product_pb2.Category(
                    id=product.category.id,
                    name=product.category.name,
                ),
            )
        except Product.DoesNotExist:
            self.abort_not_found(context, "Product not found")

    def SearchProducts(self, request, context):
        """Search products (streaming response)."""
        # Build query
        products = Product.objects.filter(active=True)

        if request.category_id:
            products = products.filter(category_id=request.category_id)

        if request.min_price:
            products = products.filter(price__gte=request.min_price)

        if request.max_price:
            products = products.filter(price__lte=request.max_price)

        if request.search_query:
            products = products.filter(
                Q(name__icontains=request.search_query) |
                Q(description__icontains=request.search_query)
            )

        # Optimize query
        products = products.select_related('category').prefetch_related('tags')

        # Stream results
        for product in products[:100]:  # Limit to 100
            yield product_pb2.Product(
                id=product.id,
                name=product.name,
                price=str(product.price),
            )
```

### Example 3: Order Management Service

```python
# apps/orders/grpc_services.py
from django_cfg.apps.grpc.services import AuthRequiredService
from django.db import transaction
from .models import Order, OrderItem
from apps.products.models import Product
from . import order_pb2

class OrderService(AuthRequiredService):
    """Order management service (authentication required)."""

    def CreateOrder(self, request, context):
        """Create a new order."""
        # self.user is always set (AuthRequiredService)
        user = self.user

        # Validate items
        if not request.items:
            self.abort_invalid_argument(context, "Order must have items")

        # Create order in transaction
        with transaction.atomic():
            # Create order
            order = Order.objects.create(
                user=user,
                status='pending',
            )

            # Add items
            total_price = 0
            for item in request.items:
                try:
                    product = Product.objects.get(id=item.product_id)
                except Product.DoesNotExist:
                    self.abort_not_found(context, f"Product {item.product_id} not found")

                # Create order item
                OrderItem.objects.create(
                    order=order,
                    product=product,
                    quantity=item.quantity,
                    price=product.price,
                )

                total_price += product.price * item.quantity

            # Update order total
            order.total = total_price
            order.save()

        return order_pb2.Order(
            id=order.id,
            status=order.status,
            total=str(order.total),
            created_at=order.created_at.isoformat(),
        )

    def GetOrder(self, request, context):
        """Get order by ID."""
        try:
            # Only allow user to view their own orders
            order = Order.objects.select_related('user').prefetch_related(
                'items__product'
            ).get(
                id=request.order_id,
                user=self.user
            )

            # Build response
            items = [
                order_pb2.OrderItem(
                    product_id=item.product.id,
                    product_name=item.product.name,
                    quantity=item.quantity,
                    price=str(item.price),
                )
                for item in order.items.all()
            ]

            return order_pb2.Order(
                id=order.id,
                status=order.status,
                total=str(order.total),
                items=items,
                created_at=order.created_at.isoformat(),
            )
        except Order.DoesNotExist:
            self.abort_not_found(context, "Order not found")

    def CancelOrder(self, request, context):
        """Cancel an order."""
        try:
            order = Order.objects.get(
                id=request.order_id,
                user=self.user
            )

            # Check if cancellable
            if order.status not in ['pending', 'processing']:
                self.abort_invalid_argument(
                    context,
                    f"Cannot cancel order with status {order.status}"
                )

            # Cancel order
            order.status = 'cancelled'
            order.save()

            return order_pb2.Order(
                id=order.id,
                status=order.status,
            )
        except Order.DoesNotExist:
            self.abort_not_found(context, "Order not found")
```

## 🔄 Streaming Support

### Server-Side Streaming

Stream multiple responses:

```python
def ListProducts(self, request, context):
    """Stream product list."""
    products = Product.objects.all()

    for product in products:
        yield product_pb2.Product(
            id=product.id,
            name=product.name,
        )
```

### Client-Side Streaming

Receive stream of requests:

```python
def BatchCreateUsers(self, request_iterator, context):
    """Create multiple users from stream."""
    created_count = 0

    for user_request in request_iterator:
        User.objects.create(
            username=user_request.username,
            email=user_request.email,
        )
        created_count += 1

    return user_pb2.BatchCreateResponse(
        created_count=created_count
    )
```

### Bidirectional Streaming

Stream requests and responses:

```python
def Chat(self, request_iterator, context):
    """Bidirectional chat streaming."""
    for message in request_iterator:
        # Process message
        response = process_message(message)

        # Stream response
        yield chat_pb2.ChatMessage(
            text=response,
            timestamp=timezone.now().isoformat(),
        )
```

## 🎯 Best Practices

### 1. Use Select Related / Prefetch Related

Optimize database queries:

```python
def GetUser(self, request, context):
    # ❌ Bad: N+1 query
    user = User.objects.get(id=request.user_id)
    profile = user.profile  # Extra query!

    # ✅ Good: Single query
    user = User.objects.select_related('profile').get(
        id=request.user_id
    )
```

### 2. Use Transactions

Wrap writes in transactions:

```python
def CreateOrder(self, request, context):
    # ✅ Use transaction for multiple writes
    with transaction.atomic():
        order = Order.objects.create(...)
        OrderItem.objects.create(...)
        # All or nothing
```

### 3. Validate Early

Validate requests before database operations:

```python
def CreateProduct(self, request, context):
    # ✅ Validate first
    if not request.name:
        self.abort_invalid_argument(context, "Name required")

    if request.price <= 0:
        self.abort_invalid_argument(context, "Price must be positive")

    # Then create
    product = Product.objects.create(...)
```

### 4. Handle Exceptions

Catch and convert exceptions properly:

```python
def MyMethod(self, request, context):
    try:
        # Business logic
        obj = MyModel.objects.get(id=request.id)
    except MyModel.DoesNotExist:
        self.abort_not_found(context, "Not found")
    except ValidationError as e:
        self.abort_invalid_argument(context, str(e))
    except Exception as e:
        logger.exception("Unexpected error")
        self.abort_internal(context, "Internal error")
```

### 5. Use Proper Status Codes

Choose appropriate gRPC status codes:

```python
# User not authenticated
self.abort_unauthenticated(context, "Login required")

# User doesn't have permission
self.abort_permission_denied(context, "No access")

# Invalid request data
self.abort_invalid_argument(context, "Invalid data")

# Resource not found
self.abort_not_found(context, "Not found")

# Resource already exists
self.abort_already_exists(context, "Already exists")

# Internal server error
self.abort_internal(context, "Server error")
```

## 🧪 Testing gRPC Services

### Unit Testing

```python
# apps/users/tests/test_grpc_services.py
from django.test import TestCase
from django.contrib.auth import get_user_model
from apps.users.grpc_services import UserService
from apps.users import user_pb2

User = get_user_model()

class UserServiceTestCase(TestCase):
    def setUp(self):
        self.service = UserService()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
        )

    def test_get_user(self):
        """Test GetUser method."""
        request = user_pb2.GetUserRequest(user_id=self.user.id)
        context = MockContext()

        response = self.service.GetUser(request, context)

        self.assertEqual(response.id, self.user.id)
        self.assertEqual(response.username, 'testuser')

    def test_get_user_not_found(self):
        """Test GetUser with non-existent user."""
        request = user_pb2.GetUserRequest(user_id=9999)
        context = MockContext()

        with self.assertRaises(grpc.RpcError):
            self.service.GetUser(request, context)
```

## 📚 Related Documentation

- **[Architecture](./architecture.md)** - Service architecture
- **[Setup Guide](./setup.md)** - Configuration
- **[Authentication](./authentication.md)** - JWT auth
- **[Monitoring](./monitoring.md)** - Request logging

---

**Next:** Learn about [interceptors](./interceptors.md) or explore [authentication](./authentication.md).
