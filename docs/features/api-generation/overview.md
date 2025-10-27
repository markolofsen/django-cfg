---
title: API Client Generation Overview
sidebar_position: 1
keywords:
  - django-cfg api generation
  - django api client
  - type-safe api clients
  - typescript client generator
  - python client generator
  - grpc client generator
  - protocol buffers generator
description: Auto-generate type-safe TypeScript, Python, Go, and Protocol Buffer clients from Django REST Framework. Built for Next.js, React, React Native, modern Python backends, and gRPC services.
---

import { TechArticleSchema } from '@site/src/components/Schema';

<TechArticleSchema
  headline="API Client Generation with Django-CFG"
  description="Automatically generate type-safe TypeScript and Python clients from your Django REST Framework API using Django-CFG's integrated client generator"
  keywords={['django api client generator', 'django-cfg client', 'type-safe api clients', 'django typescript client', 'auto-generate api client']}
/>

# API Client Generation

Django-CFG includes **integrated API client generation** that automatically creates type-safe **TypeScript**, **Python**, **Go**, and **Protocol Buffer/gRPC** clients from your Django REST Framework API using OpenAPI specifications.

## What is API Client Generation?

The API client generator is a zero-config system built into Django-CFG that eliminates the manual work of creating and maintaining API clients. It uses the **[django_client module](/features/modules/django-client/overview)** to generate fully-typed clients with authentication, error handling, and complete type safety.

:::tip Built-in Integration
API client generation is **pre-configured** in Django-CFG. Simply enable it in your configuration and run the management command to generate clients for your API.
:::

## Key Features

### 🎯 Type-Safe Code Generation

Generate fully typed clients with:

- **TypeScript**: Interfaces, Zod schemas, typed fetch functions, SWR hooks
- **Python**: Pydantic 2 models, async/await client, type hints
- **Go**: Structs, interfaces, typed HTTP client
- **Protocol Buffers**: Proto3 messages, gRPC service definitions

### 🏗️ Group-Based Organization

Organize your API into logical **groups** based on functionality:

```python
groups=[
    OpenAPIGroupConfig(
        name="core",
        apps=["users", "accounts"],
        title="Core API",
        description="User management and authentication"
    ),
    OpenAPIGroupConfig(
        name="billing",
        apps=["payments", "subscriptions"],
        title="Billing API",
        description="Payment processing and subscriptions"
    )
]
```

Each group gets its own:
- OpenAPI schema
- Generated TypeScript client
- Generated Python client
- Generated Go client
- Generated Protocol Buffer definitions
- API documentation (Swagger/Redoc)

### ⚙️ Auto-Generated Clients

For each group, the generator creates:

**TypeScript Client:**
```typescript
import { getUsers, createUser } from '@/api/generated/_utils/fetchers/users'
import { useUsers } from '@/api/generated/_utils/hooks/users'

// Next.js Server Component
const users = await getUsers({ page: 1 })

// React Client Component
const { data, error } = useUsers({ page: 1 })
```

**Python Client:**
```python
from api_client import APIClient

client = APIClient(base_url="https://api.example.com")

# Fully async with Pydantic 2 models
users = await client.users.list(page=1)
```

**gRPC Client (Protocol Buffers):**
```python
import grpc
from profiles.api__profiles import service_pb2, service_pb2_grpc

# Create gRPC channel
channel = grpc.insecure_channel('localhost:50051')
stub = service_pb2_grpc.ProfilesServiceStub(channel)

# Make gRPC call with type-safe proto messages
request = service_pb2.ProfilesProfilesListRequest(page=1, page_size=10)
response = stub.ProfilesProfilesList(request)
```

## Why Use API Client Generation?

### ⛔ Without API Client Generation

Manual API client development requires:
1. Manually writing type definitions
2. Keeping types in sync with backend
3. Writing fetch/request logic
4. Handling errors and validation
5. Maintaining multiple clients across projects
6. Repeating this on every API change

**Time investment:** Weeks to months for enterprise setup

### ✅ With Django-CFG API Client Generation

```bash
# One command to generate everything
python manage.py generate_api
```

**Time investment:** Seconds! 🚀

:::tip Performance
Generation is optimized for large APIs. A typical API with 300 operations generates in ~3 seconds.
:::

## What Gets Generated?

### TypeScript Output

```
frontend/src/api/generated/
├── core/                          # Group name
│   ├── client.ts                  # Main API client
│   ├── models.ts                  # TypeScript interfaces
│   ├── enums.ts                   # Enum definitions
│   └── _utils/
│       ├── fetchers/              # Typed fetch functions
│       │   ├── users.ts
│       │   └── accounts.ts
│       ├── hooks/                 # SWR hooks (React)
│       │   ├── users.ts
│       │   └── accounts.ts
│       └── schemas/               # Zod validation schemas
│           ├── User.schema.ts
│           └── UserRequest.schema.ts
│
├── billing/                       # Another group
│   └── ...
│
└── index.ts                       # Main entry point
```

### Python Output

```
backend/api_client/
├── core/                          # Group name
│   ├── __init__.py
│   ├── client.py                  # Main async client
│   ├── models/                    # Pydantic models
│   │   ├── users.py
│   │   └── accounts.py
│   └── subclients/                # Sub-clients by tag
│       ├── users.py
│       └── accounts.py
│
├── billing/                       # Another group
│   └── ...
│
└── index.py                       # Main entry point
```

### Protocol Buffers Output

```
openapi/clients/proto/
├── core/                          # Group name
│   ├── users/
│   │   ├── messages.proto         # Message definitions (models, enums)
│   │   ├── service.proto          # gRPC service definitions
│   │   ├── messages_pb2.py        # Compiled Python messages
│   │   ├── messages_pb2_grpc.py   # gRPC stubs (empty)
│   │   ├── service_pb2.py         # Request/Response messages
│   │   └── service_pb2_grpc.py    # gRPC client & server stubs
│   │
│   ├── accounts/
│   │   └── ...                    # Same structure
│   │
│   └── README.md                  # Compilation instructions
│
├── billing/                       # Another group
│   └── ...
│
└── README.md                      # Root compilation guide
```

:::info Compilation Required
Proto files must be compiled with `protoc` before use. Each group includes a README.md with language-specific compilation commands for Python, Go, TypeScript, and other languages.
:::

## Generated Features

✅ **Type-safe API calls** - Full TypeScript/Python/Go/Proto types
✅ **Authentication** - Bearer tokens, API keys, custom headers
✅ **Error handling** - Proper error types and validation
✅ **Async support** - Both sync and async methods
✅ **Enum generation** - Real Enum classes (not strings)
✅ **Request/Response split** - Separate UserRequest vs User models
✅ **File uploads** - Multipart FormData handling
✅ **Pagination** - Built-in pagination support
✅ **Validation** - Zod schemas for runtime validation
✅ **React integration** - SWR hooks for data fetching

## Quick Start

### 1. Configure Django-CFG

```python
# api/config.py
from django_cfg import DjangoConfig, OpenAPIClientConfig, OpenAPIGroupConfig

class MyProjectConfig(DjangoConfig):
    openapi_client: OpenAPIClientConfig = OpenAPIClientConfig(
        enabled=True,
        generate_package_files=True,
        generate_zod_schemas=True,
        generate_fetchers=True,
        generate_swr_hooks=True,
        api_prefix="api",
        output_dir="openapi",
        drf_title="My API",
        drf_description="My API documentation",
        drf_version="1.0.0",
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

### 2. Generate Clients

```bash
# Generate all clients from groups configuration
python manage.py generate_api

# Or generate individual clients
python manage.py generate_ts_client --openapi-schema openapi.yaml --output frontend/src/api
python manage.py generate_python_client --openapi-schema openapi.yaml --output backend/api_client
```

### 3. Use Generated Clients

**TypeScript (Next.js Server Component):**
```typescript
import { getUsers } from '@/api/generated/_utils/fetchers/users'

export default async function UsersPage() {
  const users = await getUsers({ page: 1 })
  return <div>{users.count} users</div>
}
```

**Python:**
```python
from api_client import APIClient

async def main():
    client = APIClient(base_url="https://api.example.com")
    users = await client.users.list(page=1)
```

## Configuration with Groups

Groups allow you to organize large APIs into logical sections. Each group can include multiple Django apps and generates separate clients:

```python
openapi_client: OpenAPIClientConfig = OpenAPIClientConfig(
    enabled=True,
    # ... other settings ...
    groups=[
        # Core functionality
        OpenAPIGroupConfig(
            name="core",
            apps=["users", "accounts", "profiles"],
            title="Core API",
            description="User management and authentication",
            version="1.0.0",
        ),

        # E-commerce
        OpenAPIGroupConfig(
            name="shop",
            apps=["products", "orders", "cart"],
            title="Shop API",
            description="E-commerce functionality",
            version="1.0.0",
        ),

        # Content management
        OpenAPIGroupConfig(
            name="content",
            apps=["blog", "cms", "media"],
            title="Content API",
            description="Content management system",
            version="1.0.0",
        ),
    ],
)
```

Each group generates:
- `/openapi/core/` - Core API clients
- `/openapi/shop/` - Shop API clients
- `/openapi/content/` - Content API clients

## Integration with Django-CFG

### Automatic URL Integration

Django-CFG automatically integrates API generation URLs:

```python
# api/urls.py
from django.urls import path, include
from django_cfg import add_django_cfg_urls

urlpatterns = [
    path("admin/", admin.site.urls),
]

# Automatically adds OpenAPI schema endpoints
urlpatterns = add_django_cfg_urls(urlpatterns)
```

This adds:
- `/schema/{group}/schema/` - OpenAPI schema
- `/schema/{group}/swagger/` - Swagger UI
- `/schema/{group}/redoc/` - Redoc documentation

### Built-in drf-spectacular Integration

Django-CFG automatically configures `drf-spectacular` based on your `openapi_client` configuration:

```python
# Automatic configuration from openapi_client settings
SPECTACULAR_SETTINGS = {
    'TITLE': config.openapi_client.drf_title,
    'DESCRIPTION': config.openapi_client.drf_description,
    'VERSION': config.openapi_client.drf_version,
    # ... other settings auto-configured
}
```

## Supported Frameworks

### TypeScript/JavaScript

- ✅ Next.js 13+ (App Router, Pages Router, Server Components)
- ✅ React 18+ (with SWR hooks)
- ✅ React Native (with fetch API)
- ✅ Node.js (backend services)
- ✅ Remix, Astro, and other modern frameworks

### Python

- ✅ Django (async views)
- ✅ FastAPI (as HTTP client)
- ✅ Flask (async with asyncio)
- ✅ Celery (background tasks)
- ✅ pytest (test fixtures)

## Best Practices

### 1. Version Control Generated Code

Always commit generated code to version control:

```bash
git add frontend/src/api/generated
git add backend/api_client
git commit -m "Update API clients"
```

### 2. Use Groups for Large APIs

Organize APIs into logical groups (5-10 apps per group recommended):

```python
groups=[
    OpenAPIGroupConfig(name="core", apps=["users", "auth", "profiles"]),
    OpenAPIGroupConfig(name="billing", apps=["payments", "subscriptions"]),
    OpenAPIGroupConfig(name="content", apps=["blog", "cms", "media"]),
]
```

### 3. Follow Naming Conventions

- **Operation IDs**: Use `{tag}_{action}` format
- **Models**: Use PascalCase
- **Groups**: Use lowercase, descriptive names

### 4. Enable All Type Safety Features

```python
OpenAPIClientConfig(
    generate_zod_schemas=True,        # Runtime validation
    generate_package_files=True,      # Proper TypeScript setup
    generate_fetchers=True,           # Universal fetch functions
    generate_swr_hooks=True,          # React integration
)
```

## Next Steps

- **[Group Configuration](./groups)** - Configure API groups
- **[CLI Usage](./cli-usage)** - Generation commands
- **[Generated Clients](./generated-clients)** - Using generated clients
- **[Django Client Module](/features/modules/django-client/overview)** - Deep dive into the generator

:::tip Quick Start
If you're ready to start generating clients, head to the [Django Client Getting Started Guide](/features/modules/django-client/getting-started) for a step-by-step tutorial.
:::
