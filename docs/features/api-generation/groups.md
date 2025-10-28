---
title: Group Configuration
sidebar_position: 3
keywords:
  - django-cfg groups
  - api groups
  - openapi groups
description: Configure API generation groups for organizing large APIs. Manage multiple API clients with group-specific settings and separate OpenAPI schemas.
---

# Group Configuration

Groups organize your Django REST Framework API into logical sections for different features, teams, or microservices. Django-CFG's API client generator creates separate clients for each group.

## Understanding Groups

A **group** is a collection of Django apps that share:
- Related functionality
- Common domain logic
- Target audience or purpose
- Similar access patterns

Each group gets:
- **Separate OpenAPI schema** - Independent API documentation
- **Generated TypeScript client** - Type-safe frontend client
- **Generated Python client** - Async backend client
- **API documentation** - Swagger UI and Redoc

## Configuration

### Basic Group

Configure groups in your Django-CFG configuration:

```python
# api/config.py
from django_cfg import DjangoConfig, OpenAPIClientConfig, OpenAPIGroupConfig

class MyProjectConfig(DjangoConfig):
    openapi_client: OpenAPIClientConfig = OpenAPIClientConfig(
        enabled=True,
        groups=[
            OpenAPIGroupConfig(
                name="core",
                apps=["users", "accounts"],
                title="Core API",
                description="User management and authentication",
                version="1.0.0",
            ),
        ],
    )
```

### Multiple Groups

Organize large APIs into logical groups:

```python
openapi_client: OpenAPIClientConfig = OpenAPIClientConfig(
    enabled=True,
    generate_package_files=True,
    generate_zod_schemas=True,
    generate_fetchers=True,
    generate_swr_hooks=True,
    output_dir="openapi",
    groups=[
        # Core functionality
        OpenAPIGroupConfig(
            name="core",
            apps=["users", "accounts", "profiles"],
            title="Core API",
            description="User management, authentication, and profiles",
            version="1.0.0",
        ),

        # E-commerce
        OpenAPIGroupConfig(
            name="shop",
            apps=["products", "orders", "cart", "inventory"],
            title="Shop API",
            description="E-commerce and order management",
            version="1.0.0",
        ),

        # Content management
        OpenAPIGroupConfig(
            name="content",
            apps=["blog", "cms", "media", "comments"],
            title="Content API",
            description="Content management and publishing",
            version="1.0.0",
        ),

        # Analytics and reporting
        OpenAPIGroupConfig(
            name="analytics",
            apps=["stats", "reports", "dashboards"],
            title="Analytics API",
            description="Business intelligence and reporting",
            version="1.0.0",
        ),
    ],
)
```

## OpenAPIGroupConfig Parameters

```python
OpenAPIGroupConfig(
    name: str,                    # Group name (lowercase, no spaces)
    apps: List[str],              # Django apps to include
    title: str,                   # Human-readable title
    description: str,             # Group description
    version: str = "1.0.0",       # API version
)
```

### Parameter Details

**`name`** - Unique group identifier
- Used in URLs (`/schema/{name}/`)
- Used in file paths (`openapi/{name}/`)
- Lowercase, no spaces (use underscores or hyphens)
- Examples: `"core"`, `"shop"`, `"analytics"`

**`apps`** - Django app labels
- List of Django app names to include
- Use app labels, not full Python paths
- Example: `["users", "accounts"]` not `["myproject.users"]`

**`title`** - Display name
- Used in OpenAPI schema
- Shown in Swagger UI and Redoc
- Human-readable, can have spaces
- Example: `"Core API"`, `"Shop & Orders"`

**`description`** - Group description
- Detailed explanation of group purpose
- Shown in API documentation
- Can be multiline
- Example: `"User management, authentication, and profiles"`

**`version`** - API version
- Semantic versioning recommended
- Default: `"1.0.0"`
- Used for API evolution

## Generated Structure

### Output Directory

Each group generates its own directory structure:

```
openapi/
├── core/                       # Group: core
│   ├── typescript/
│   │   ├── client.ts
│   │   ├── models.ts
│   │   ├── enums.ts
│   │   └── _utils/
│   │       ├── fetchers/
│   │       ├── hooks/
│   │       └── schemas/
│   └── python/
│       ├── __init__.py
│       ├── client.py
│       ├── models/
│       └── subclients/
│
├── shop/                       # Group: shop
│   ├── typescript/
│   └── python/
│
└── content/                    # Group: content
    ├── typescript/
    └── python/
```

### OpenAPI Schemas

Each group gets its own OpenAPI schema URL:

```
/schema/core/schema/         # OpenAPI JSON
/schema/shop/schema/         # OpenAPI JSON
/schema/content/schema/      # OpenAPI JSON
```

## Examples

### Microservices Architecture

Split API by service boundaries:

```python
groups=[
    OpenAPIGroupConfig(
        name="auth",
        apps=["authentication", "permissions", "oauth"],
        title="Authentication Service",
        description="User authentication and authorization"
    ),
    OpenAPIGroupConfig(
        name="user",
        apps=["users", "profiles", "preferences"],
        title="User Service",
        description="User management and profiles"
    ),
    OpenAPIGroupConfig(
        name="order",
        apps=["orders", "payments", "shipping"],
        title="Order Service",
        description="Order processing and fulfillment"
    ),
]
```

### Team-Based Organization

Split API by team ownership:

```python
groups=[
    OpenAPIGroupConfig(
        name="platform",
        apps=["accounts", "billing", "admin"],
        title="Platform API",
        description="Core platform features (Platform Team)"
    ),
    OpenAPIGroupConfig(
        name="marketplace",
        apps=["products", "sellers", "reviews"],
        title="Marketplace API",
        description="Marketplace features (Marketplace Team)"
    ),
    OpenAPIGroupConfig(
        name="messaging",
        apps=["chat", "notifications", "inbox"],
        title="Messaging API",
        description="Messaging and notifications (Messaging Team)"
    ),
]
```

### Client Type Organization

Split API by client application:

```python
groups=[
    OpenAPIGroupConfig(
        name="web",
        apps=["dashboard", "settings", "analytics"],
        title="Web Application API",
        description="Web dashboard and admin panel"
    ),
    OpenAPIGroupConfig(
        name="mobile",
        apps=["feed", "camera", "social", "maps"],
        title="Mobile App API",
        description="iOS and Android mobile apps"
    ),
    OpenAPIGroupConfig(
        name="public",
        apps=["docs", "blog", "marketing"],
        title="Public API",
        description="Public-facing website and documentation"
    ),
]
```

### Versioned APIs

Maintain multiple API versions:

```python
groups=[
    OpenAPIGroupConfig(
        name="v1",
        apps=["api.v1.users", "api.v1.products"],
        title="API v1 (Legacy)",
        description="Legacy API - deprecated",
        version="1.0.0"
    ),
    OpenAPIGroupConfig(
        name="v2",
        apps=["api.v2.users", "api.v2.products", "api.v2.orders"],
        title="API v2 (Current)",
        description="Current stable API",
        version="2.0.0"
    ),
    OpenAPIGroupConfig(
        name="v3",
        apps=["api.v3.users", "api.v3.products"],
        title="API v3 (Beta)",
        description="Next generation API (beta)",
        version="3.0.0-beta"
    ),
]
```

## Group Discovery

### Automatic App Discovery

Groups automatically discover ViewSets and APIViews from included apps:

```python
# users/api/views.py
from rest_framework import viewsets
from .models import User
from .serializers import UserSerializer

class UserViewSet(viewsets.ModelViewSet):
    """User management endpoints"""
    queryset = User.objects.all()
    serializer_class = UserSerializer
```

When `"users"` is added to a group, all ViewSet endpoints are automatically included.

### URL Patterns

Ensure apps are properly registered in URL configuration:

```python
# users/urls.py
from rest_framework.routers import DefaultRouter
from .api.views import UserViewSet

router = DefaultRouter()
router.register('users', UserViewSet)

urlpatterns = router.urls
```

```python
# Main urls.py
from django.urls import path, include

urlpatterns = [
    path('api/users/', include('users.urls')),
]
```

## Best Practices

### 1. Group Naming

Use clear, descriptive names:

✅ **Good:**
- `core` - Core functionality
- `shop` - E-commerce features
- `analytics` - Reporting and analytics
- `admin` - Admin panel
- `mobile` - Mobile app

❌ **Bad:**
- `group1`, `group2` - Not descriptive
- `api_a`, `api_b` - Unclear purpose
- `test`, `dev` - Environment names

### 2. Group Size

Aim for 5-10 apps per group:

✅ **Good:**
```python
OpenAPIGroupConfig(
    name="core",
    apps=["users", "auth", "profiles", "settings", "notifications"]
)
```

❌ **Too Large:**
```python
OpenAPIGroupConfig(
    name="everything",
    apps=["users", "auth", "profiles", "products", "orders", "shipping",
          "payments", "blog", "cms", "chat", "notifications", "analytics"]
    # 12 apps - too many, split into multiple groups
)
```

❌ **Too Small:**
```python
OpenAPIGroupConfig(name="users", apps=["users"])
OpenAPIGroupConfig(name="auth", apps=["auth"])
OpenAPIGroupConfig(name="profiles", apps=["profiles"])
# These should be combined into one "core" group
```

### 3. Logical Grouping

Group by domain logic, not technical layers:

✅ **Good (Domain-Driven):**
```python
groups=[
    OpenAPIGroupConfig(name="shop", apps=["products", "cart", "orders"]),
    OpenAPIGroupConfig(name="billing", apps=["payments", "invoices", "subscriptions"]),
]
```

❌ **Bad (Technical Layers):**
```python
groups=[
    OpenAPIGroupConfig(name="models", apps=["products", "users", "orders"]),
    OpenAPIGroupConfig(name="views", apps=["api_views", "admin_views"]),
]
```

### 4. Independent Groups

Keep groups independent with minimal cross-dependencies:

✅ **Good:**
- Core group (users, auth) - standalone
- Shop group (products, orders) - uses core
- Analytics group (reports, stats) - reads from all

❌ **Bad:**
- Group A depends on Group B
- Group B depends on Group C
- Group C depends on Group A
(Circular dependencies make it hard to maintain)

## Troubleshooting

### Group Not Generating

**Check app is installed** in `INSTALLED_APPS`:
```python
INSTALLED_APPS = [
    # ...
    'users',
    'accounts',
]
```

**Verify URLs are registered:**
```bash
python manage.py show_urls | grep users
```

**Run schema validation:**
```bash
python manage.py spectacular --format openapi --validate --file openapi.yaml
```

### Empty Schema

**Add ViewSets or APIViews** to your app:
```python
from rest_framework import viewsets

class MyViewSet(viewsets.ModelViewSet):
    queryset = MyModel.objects.all()
    serializer_class = MySerializer
```

**Use DRF decorators** for function-based views:
```python
from rest_framework.decorators import api_view

@api_view(['GET', 'POST'])
def my_endpoint(request):
    pass
```

### Multiple Apps in One Group

Merge related apps:

```python
OpenAPIGroupConfig(
    name="billing",
    apps=[
        "billing.api",
        "payments.api",
        "subscriptions.api",
        "invoices.api"
    ],
    title="Billing & Payments",
    description="Complete billing system"
)
```

## Integration with Django-CFG

### Automatic URL Configuration

Django-CFG automatically adds OpenAPI URLs for all groups:

```python
# api/urls.py
from django_cfg import add_django_cfg_urls

urlpatterns = [
    path("admin/", admin.site.urls),
]

# Adds /schema/{group}/ URLs automatically
urlpatterns = add_django_cfg_urls(urlpatterns)
```

### drf-spectacular Configuration

Django-CFG automatically configures `drf-spectacular` for each group based on your `openapi_client` settings:

```python
# Automatic configuration from openapi_client settings
SPECTACULAR_SETTINGS = {
    'TITLE': config.openapi_client.drf_title,
    'DESCRIPTION': config.openapi_client.drf_description,
    'VERSION': config.openapi_client.drf_version,
    # ... other settings auto-configured
}
```

## Next Steps

- **[CLI Usage](./cli-usage)** - Generate clients for your groups
- **[Generated Clients](./generated-clients)** - Use generated clients
- **[Django Client Module](/features/modules/django-client/overview)** - Deep dive

:::tip Group Testing
Access `/schema/{group}/schema/` to download your group's OpenAPI schema before generating clients.
:::
