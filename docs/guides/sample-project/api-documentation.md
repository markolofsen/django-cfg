---
title: API Documentation
description: Auto-generated REST API with OpenAPI schema and Swagger UI in Django-CFG
sidebar_label: API Documentation
sidebar_position: 6
---

# API Documentation

The Django-CFG sample project includes a comprehensive REST API with auto-generated OpenAPI documentation. This guide covers API configuration, endpoints, and usage examples.

## API Overview

The sample project provides:
- **Auto-generated OpenAPI schema** - Standard API documentation
- **JWT Authentication** - Secure token-based auth
- **Versioned endpoints** - API versioning support
- **Type-safe serializers** - DRF integration
- **Auto-generated TypeScript clients** - With Zod validation
- **Auto-generated Python clients** - With type hints

## API Configuration

### DRF Spectacular Setup

Configure the API in `api/config.py`:

```python
from django_cfg import DRFConfig

drf: DRFConfig = DRFConfig(
    default_authentication_classes=[
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ],
    default_permission_classes=[
        "rest_framework.permissions.IsAuthenticated",
    ],
    spectacular_settings={
        "TITLE": "Django-CFG Sample API",
        "DESCRIPTION": "Complete API for Django-CFG sample project",
        "VERSION": "1.0.0",
        "SERVE_INCLUDE_SCHEMA": False,
    }
)
```

### Spectacular Settings

Detailed OpenAPI configuration:

```python
spectacular_settings={
    'TITLE': 'Django-CFG Sample API',
    'DESCRIPTION': 'Complete REST API for Django-CFG sample project',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,

    # Authentication
    'COMPONENT_SPLIT_REQUEST': True,
    'COMPONENT_NO_READ_ONLY_REQUIRED': True,

    # Schema customization
    'SCHEMA_PATH_PREFIX': '/api/',
    'DEFAULT_GENERATOR_CLASS': 'drf_spectacular.openapi.AutoSchema',

    # UI customization
    'SWAGGER_UI_SETTINGS': {
        'deepLinking': True,
        'persistAuthorization': True,
        'displayOperationId': True,
    },

    # Security schemes
    'APPEND_COMPONENTS': {
        'securitySchemes': {
            'jwtAuth': {
                'type': 'http',
                'scheme': 'bearer',
                'bearerFormat': 'JWT',
            }
        }
    },
    'SECURITY': [{'jwtAuth': []}],
}
```

See [Configuration](./configuration) for complete DRF setup.

## API Endpoints

### Blog API

Manage blog posts and comments:

```
GET    /api/blog/posts/              # List blog posts
POST   /api/blog/posts/              # Create blog post
GET    /api/blog/posts/{id}/         # Get specific post
PUT    /api/blog/posts/{id}/         # Update post
DELETE /api/blog/posts/{id}/         # Delete post
GET    /api/blog/posts/{id}/comments/ # Get post comments
POST   /api/blog/posts/{id}/comments/ # Add comment
```

### Shop API

E-commerce operations:

```
GET    /api/shop/products/           # List products
POST   /api/shop/products/           # Create product
GET    /api/shop/products/{id}/      # Get specific product
PUT    /api/shop/products/{id}/      # Update product
DELETE /api/shop/products/{id}/      # Delete product
POST   /api/shop/orders/             # Create order
GET    /api/shop/orders/             # List user orders
GET    /api/shop/orders/{id}/        # Get specific order
```

### Authentication API

User authentication and tokens:

```
POST   /api/auth/otp/request/        # Request OTP
POST   /api/auth/otp/verify/         # Verify OTP
POST   /api/auth/token/refresh/      # Refresh JWT token
POST   /api/auth/logout/             # Logout user
```

See [Authentication](./authentication) for OTP flow details.

### Profile API

User profile management:

```
GET    /api/profile/                 # Get user profile
PUT    /api/profile/                 # Update profile
POST   /api/profile/avatar/          # Upload avatar
DELETE /api/profile/avatar/          # Remove avatar
```

### System API

Health checks and monitoring:

```
GET    /api/health/                  # Health check
GET    /api/metrics/                 # System metrics
```

## Accessing API Documentation

### OpenAPI Schema

Download the raw OpenAPI schema:

```
http://127.0.0.1:8000/api/schema/
```

Use this for:
- Client SDK generation
- API testing tools
- Third-party integrations

## API Usage Examples

### Authentication Flow

Complete OTP authentication example:

```python
import requests

BASE_URL = 'http://localhost:8000'

# 1. Request OTP
response = requests.post(f'{BASE_URL}/api/auth/otp/request/', {
    'identifier': 'user@example.com',
    'channel': 'email'
})

print(response.json())
# {"success": true, "message": "OTP sent to email"}

# 2. Verify OTP (user receives code via email)
response = requests.post(f'{BASE_URL}/api/auth/otp/verify/', {
    'identifier': 'user@example.com',
    'otp_code': '123456'
})

tokens = response.json()['tokens']
access_token = tokens['access']
refresh_token = tokens['refresh']

print(f"Access token: {access_token}")
```

### Making Authenticated Requests

Use the JWT token for authenticated API calls:

```python
# Set authorization header
headers = {
    'Authorization': f'Bearer {access_token}',
    'Content-Type': 'application/json'
}

# Create blog post
response = requests.post(
    f'{BASE_URL}/api/blog/posts/',
    headers=headers,
    json={
        'title': 'My API Post',
        'content': 'Created via API!',
        'status': 'published'
    }
)

post = response.json()
print(f"Created post: {post['id']}")

# Get user profile
response = requests.get(
    f'{BASE_URL}/api/profile/',
    headers=headers
)

profile = response.json()
print(f"User: {profile['email']}")
```

### Refreshing Tokens

JWT tokens expire after a set time. Refresh them:

```python
# Refresh access token
response = requests.post(
    f'{BASE_URL}/api/auth/token/refresh/',
    json={'refresh': refresh_token}
)

new_access_token = response.json()['access']

# Update headers with new token
headers['Authorization'] = f'Bearer {new_access_token}'
```

### Creating Orders

E-commerce order creation:

```python
# List available products
response = requests.get(
    f'{BASE_URL}/api/shop/products/',
    headers=headers
)

products = response.json()
product_id = products['results'][0]['id']

# Create order
response = requests.post(
    f'{BASE_URL}/api/shop/orders/',
    headers=headers,
    json={
        'items': [
            {
                'product_id': product_id,
                'quantity': 2
            }
        ]
    }
)

order = response.json()
print(f"Order total: ${order['total']}")
```

### Pagination

Handle paginated results:

```python
def get_all_posts(headers):
    """Fetch all posts with pagination."""
    all_posts = []
    url = f'{BASE_URL}/api/blog/posts/'

    while url:
        response = requests.get(url, headers=headers)
        data = response.json()

        all_posts.extend(data['results'])
        url = data['next']  # Next page URL or None

    return all_posts

posts = get_all_posts(headers)
print(f"Total posts: {len(posts)}")
```

### Filtering and Search

Use query parameters for filtering:

```python
# Filter posts by status
response = requests.get(
    f'{BASE_URL}/api/blog/posts/',
    headers=headers,
    params={'status': 'published'}
)

# Search posts
response = requests.get(
    f'{BASE_URL}/api/blog/posts/',
    headers=headers,
    params={'search': 'django'}
)

# Filter products by price range
response = requests.get(
    f'{BASE_URL}/api/shop/products/',
    headers=headers,
    params={
        'price_min': 10.00,
        'price_max': 50.00
    }
)
```

## API Serializers

### Blog Serializers

```python
# apps/blog/serializers.py
from rest_framework import serializers
from .models import Post, Comment

class PostSerializer(serializers.ModelSerializer):
    author_email = serializers.EmailField(source='author.email', read_only=True)
    comment_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Post
        fields = [
            'id',
            'title',
            'content',
            'status',
            'author',
            'author_email',
            'comment_count',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['author', 'created_at', 'updated_at']

class CommentSerializer(serializers.ModelSerializer):
    author_email = serializers.EmailField(source='author.email', read_only=True)

    class Meta:
        model = Comment
        fields = [
            'id',
            'post',
            'content',
            'author',
            'author_email',
            'created_at'
        ]
        read_only_fields = ['author', 'created_at']
```

### Shop Serializers

```python
# apps/shop/serializers.py
from rest_framework import serializers
from .models import Product, Order, OrderItem

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = [
            'id',
            'name',
            'description',
            'price',
            'stock',
            'created_at'
        ]

class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)

    class Meta:
        model = OrderItem
        fields = ['product', 'product_name', 'quantity', 'price']

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)
    user_email = serializers.EmailField(source='user.email', read_only=True)

    class Meta:
        model = Order
        fields = [
            'id',
            'user',
            'user_email',
            'items',
            'total',
            'status',
            'created_at'
        ]
        read_only_fields = ['user', 'total', 'created_at']

    def create(self, validated_data):
        items_data = validated_data.pop('items')
        order = Order.objects.create(**validated_data)

        for item_data in items_data:
            OrderItem.objects.create(order=order, **item_data)

        return order
```

## API Views

### ViewSets

```python
# apps/blog/views.py
from rest_framework import viewsets, filters
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from .models import Post
from .serializers import PostSerializer

class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'content']
    ordering_fields = ['created_at', 'title']

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def get_queryset(self):
        queryset = super().get_queryset()
        status = self.request.query_params.get('status')
        if status:
            queryset = queryset.filter(status=status)
        return queryset
```

### Custom Actions

```python
from rest_framework.decorators import action
from rest_framework.response import Response

class PostViewSet(viewsets.ModelViewSet):
    # ... existing code ...

    @action(detail=True, methods=['post'])
    def publish(self, request, pk=None):
        """Publish a draft post."""
        post = self.get_object()
        post.status = 'published'
        post.save()
        return Response({'status': 'post published'})

    @action(detail=False, methods=['get'])
    def popular(self, request):
        """Get most popular posts."""
        popular_posts = Post.objects.order_by('-views')[:10]
        serializer = self.get_serializer(popular_posts, many=True)
        return Response(serializer.data)
```

## Error Handling

### API Error Responses

```python
# Standard error format
{
    "error": "error_code",
    "message": "Human-readable error message",
    "details": {
        "field_name": ["Field-specific error"]
    }
}
```

### HTTP Status Codes

- `200 OK` - Request succeeded
- `201 Created` - Resource created
- `204 No Content` - Successful deletion
- `400 Bad Request` - Invalid request data
- `401 Unauthorized` - Authentication required
- `403 Forbidden` - Permission denied
- `404 Not Found` - Resource not found
- `500 Internal Server Error` - Server error

### Handling Errors

```python
try:
    response = requests.post(url, headers=headers, json=data)
    response.raise_for_status()  # Raise exception for 4xx/5xx
    return response.json()
except requests.exceptions.HTTPError as e:
    if e.response.status_code == 401:
        # Refresh token and retry
        refresh_access_token()
        return retry_request()
    elif e.response.status_code == 400:
        # Handle validation errors
        errors = e.response.json()
        print(f"Validation errors: {errors}")
    else:
        # Handle other errors
        print(f"Error: {e}")
```

## Rate Limiting

Configure API rate limits:

```python
# api/config.py
drf: DRFConfig = DRFConfig(
    default_throttle_classes=[
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle',
    ],
    default_throttle_rates={
        'anon': '100/day',
        'user': '1000/day',
    }
)
```

## Best Practices

### 1. Use Meaningful Endpoint Names

```python
# ✅ Good: RESTful, descriptive
/api/blog/posts/
/api/shop/products/
/api/profile/

# ❌ Bad: Vague or non-RESTful
/api/get-posts/
/api/data/
```

### 2. Version Your API

```python
# ✅ Good: Versioned endpoints
/api/v1/posts/
/api/v2/posts/

# ❌ Bad: No versioning
/api/posts/
```

### 3. Document All Endpoints

Use docstrings for auto-documentation:

```python
class PostViewSet(viewsets.ModelViewSet):
    """
    API endpoint for blog posts.

    list: Get all published posts
    create: Create a new post
    retrieve: Get a specific post
    update: Update a post
    destroy: Delete a post
    """
```

### 4. Implement Proper Pagination

```python
# ✅ Good: Paginated results
{
    "count": 100,
    "next": "http://api.example.com/posts/?page=2",
    "previous": null,
    "results": [...]
}

# ❌ Bad: Return all results
[...1000 items...]
```

## Related Topics

- [Authentication](./authentication) - API authentication setup
- [Configuration](./configuration) - DRF configuration details
- [Service Integrations](./service-integrations) - External API integrations

A well-documented API improves developer experience and adoption!
