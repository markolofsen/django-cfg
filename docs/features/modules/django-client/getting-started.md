---
title: Getting Started
sidebar_position: 2
keywords:
  - django client setup
  - django client installation
  - openapi client generator setup
  - type-safe api client
description: Get started with Django Client in 10 minutes. Install, configure, and generate your first type-safe API client.
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# Getting Started

Get up and running with Django Client in **10 minutes**. This guide covers installation, configuration, and generating your first type-safe API client.

##Prerequisites

- **Python 3.10+**
- **Django 4.0+**
- **Django REST Framework 3.14+**
- **drf-spectacular 0.26+**
- **Node.js 18+** (for TypeScript generation)

---

## Installation

### 1. Install Django-CFG

```bash
pip install django-cfg>=1.4.30
```

Django Client is included in Django-CFG - no additional installation needed!

### 2. Install drf-spectacular

```bash
pip install drf-spectacular>=0.26.5
```

### 3. Configure Django Settings

Add to your Django settings:

```python
INSTALLED_APPS = [
    # ...
    'rest_framework',
    'drf_spectacular',
]

REST_FRAMEWORK = {
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
}

SPECTACULAR_SETTINGS = {
    'TITLE': 'My API',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
    'COMPONENT_SPLIT_REQUEST': True,  # ✅ Enable request/response split
}
```

---

## Django-CFG Configuration

Configure Django Client in your Django-CFG configuration file:

```python
# api/config.py
from django_cfg import DjangoConfig, OpenAPIClientConfig, OpenAPIGroupConfig

class MyProjectConfig(DjangoConfig):
    """Your project configuration"""

    # ... other config ...

    # Django Client configuration
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
            OpenAPIGroupConfig(
                name="billing",
                apps=["payments", "subscriptions"],
                title="Billing API",
                description="Payment processing and subscriptions",
                version="1.0.0",
            ),
        ],
    )
```

---

## Generate Your First Client

### Quick Start: Generate All Groups

The simplest approach - generate all clients defined in your configuration:

```bash
python manage.py generate_api
```

This command:
1. Reads groups from your `openapi_client.groups` configuration
2. Generates OpenAPI schemas for each group
3. Creates TypeScript and Python clients for each group
4. Outputs clients to the configured directory

**Output structure:**

```
openapi/
├── core/                          # Group name
│   ├── typescript/
│   │   ├── cfg__accounts/         # Tag folders
│   │   │   ├── client.ts
│   │   │   ├── models.ts
│   │   │   └── _utils/
│   │   │       ├── fetchers/      # Typed fetch functions
│   │   │       ├── hooks/         # SWR hooks
│   │   │       └── schemas/       # Zod schemas
│   │   ├── client.ts
│   │   ├── schema.ts
│   │   ├── enums.ts
│   │   └── index.ts
│   └── python/
│       ├── __init__.py
│       ├── client.py
│       ├── models/
│       └── subclients/
│
├── billing/
│   └── ...
│
└── archive/                       # Version history
    └── 2025-01-15_10-00-00/
```

### Alternative: Generate Single Client

For more control, generate individual clients:

<Tabs>
  <TabItem value="typescript" label="TypeScript" default>

```bash
# 1. Export OpenAPI schema
python manage.py spectacular --format openapi --file openapi.yaml

# 2. Generate TypeScript client
python manage.py generate_ts_client \
  --openapi-schema openapi.yaml \
  --output frontend/src/api/generated
```

**Generated files:**

```
frontend/src/api/generated/
├── cfg__accounts/
│   ├── client.ts
│   ├── models.ts
│   ├── index.ts
│   └── _utils/
│       ├── fetchers/accounts.ts   # ✅ Universal fetch functions
│       ├── hooks/accounts.ts      # ✅ SWR hooks
│       └── schemas/
│           ├── User.schema.ts
│           └── UserRequest.schema.ts
├── cfg__payments/
│   └── ...
├── client.ts                       # Main client
├── schema.ts                       # All Zod schemas
├── enums.ts                        # Enums
├── errors.ts                       # Error handling
├── http.ts                         # HTTP layer
├── api-instance.ts                 # Singleton instance
└── index.ts                        # Exports
```

  </TabItem>
  <TabItem value="python" label="Python">

```bash
# 1. Export OpenAPI schema
python manage.py spectacular --format openapi --file openapi.yaml

# 2. Generate Python client
python manage.py generate_python_client \
  --openapi-schema openapi.yaml \
  --output backend/api_client
```

**Generated files:**

```
backend/api_client/
├── __init__.py
├── client.py                      # Main APIClient
├── models/
│   ├── __init__.py
│   ├── accounts.py                # User, UserRequest models
│   └── payments.py                # Payment models
└── subclients/
    ├── __init__.py
    ├── accounts.py                # client.accounts.*
    └── payments.py                # client.payments.*
```

  </TabItem>
</Tabs>

---

## Using Generated Clients

### TypeScript Usage

<Tabs>
  <TabItem value="nextjs-server" label="Next.js Server Component" default>

```typescript
// app/users/page.tsx
import { getUsers } from '@/api/generated/cfg__accounts/_utils/fetchers/accounts'

export default async function UsersPage() {
  // Type-safe, works in Server Components
  const users = await getUsers({ page: 1, page_size: 20 })

  return (
    <div>
      <h1>Users ({users.count})</h1>
      {users.results.map(user => (
        <div key={user.id}>
          {user.username} - {user.email}
        </div>
      ))}
    </div>
  )
}
```

  </TabItem>
  <TabItem value="nextjs-client" label="Next.js Client Component">

```typescript
'use client'
import { useUsers } from '@/api/generated/cfg__accounts/_utils/hooks/accounts'

export default function UsersTable() {
  // SWR hook with caching and revalidation
  const { data, error, isLoading, mutate } = useUsers({
    page: 1,
    page_size: 20
  })

  if (isLoading) return <Spinner />
  if (error) return <Error error={error} />

  return (
    <div>
      <button onClick={() => mutate()}>Refresh</button>
      <Table data={data.results} />
    </div>
  )
}
```

  </TabItem>
  <TabItem value="react-native" label="React Native">

```typescript
import { getUsers, createUser } from './api/generated/cfg__accounts/_utils/fetchers/accounts'
import { useUsers } from './api/generated/cfg__accounts/_utils/hooks/accounts'

export default function UsersScreen() {
  const { data, error, isLoading } = useUsers({ page: 1 })

  const handleCreateUser = async () => {
    await createUser({
      username: 'newuser',
      email: 'new@example.com',
      password: 'secret123'
    })
  }

  if (isLoading) return <ActivityIndicator />
  return <FlatList data={data.results} />
}
```

  </TabItem>
</Tabs>

### Python Usage

```python
from api_client import APIClient

async def main():
    # Initialize client
    client = APIClient(base_url="https://api.example.com")

    # List users with type-safe parameters
    users = await client.accounts.list(page=1, page_size=20)
    for user in users.results:
        print(f"{user.username} - {user.email}")

    # Create user with validation
    new_user = await client.accounts.create(data={
        "username": "alice",
        "email": "alice@example.com",
        "password": "secret123"
    })
    print(f"Created user: {new_user.id}")

    # Update user
    updated = await client.accounts.partial_update(
        id=new_user.id,
        data={"email": "alice_updated@example.com"}
    )

    # Delete user
    await client.accounts.destroy(id=new_user.id)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
```

---

## Configuration Options

### CLI Options

**TypeScript Generator:**

```bash
python manage.py generate_ts_client \
  --openapi-schema openapi.yaml \
  --output frontend/src/api \
  --generate-fetchers \
  --generate-hooks \
  --generate-zod-schemas \
  --generate-package-files
```

**Python Generator:**

```bash
python manage.py generate_python_client \
  --openapi-schema openapi.yaml \
  --output backend/api_client \
  --async-client
```

### OpenAPIClientConfig Options

```python
OpenAPIClientConfig(
    enabled: bool = True,                      # Enable client generation
    generate_package_files: bool = True,       # Generate package.json, __init__.py
    generate_zod_schemas: bool = True,         # Generate Zod validation schemas
    generate_fetchers: bool = True,            # Generate typed fetch functions
    generate_swr_hooks: bool = True,           # Generate SWR hooks
    api_prefix: str = "api",                   # API URL prefix
    output_dir: str = "openapi",               # Output directory
    drf_title: str = "API",                    # OpenAPI spec title
    drf_description: str = "API docs",         # OpenAPI spec description
    drf_version: str = "1.0.0",                # API version
    groups: List[OpenAPIGroupConfig] = [],     # API groups
)
```

### OpenAPIGroupConfig Options

```python
OpenAPIGroupConfig(
    name: str,                                 # Group name (e.g., "core")
    apps: List[str],                           # Django apps to include
    title: str,                                # Group title
    description: str,                          # Group description
    version: str = "1.0.0",                    # Group version
)
```

---

## Troubleshooting

### TypeScript Errors

**Error: Module not found**

```bash
# Install dependencies in your frontend project
cd frontend
npm install zod swr
```

**Error: Type '...' is not assignable**

- Ensure you're using the latest generated code
- Run `pnpm tsc --noEmit` to check for type errors
- Regenerate clients after OpenAPI schema changes

### Python Errors

**Error: ModuleNotFoundError: No module named 'api_client'**

```bash
# Ensure the generated client directory is in your Python path
export PYTHONPATH="${PYTHONPATH}:/path/to/backend"
```

**Error: ValidationError when calling API**

- Check that request data matches the expected schema
- Use Pydantic models for type safety: `UserRequest.model_validate(data)`

### Generation Errors

**Error: No operations found**

- Ensure Django apps have ViewSets or APIViews
- Check that `drf-spectacular` is properly configured
- Verify OpenAPI schema is valid: `python manage.py spectacular --validate`

---

## Best Practices

### 1. Version Control Generated Code

Always commit generated code to version control:

```bash
git add frontend/src/api/generated
git add backend/api_client
git commit -m "Update API client"
```

### 2. Regenerate After API Changes

After modifying Django models or serializers:

```bash
python manage.py generate_api
```

### 3. Use Groups for Large APIs

Organize large APIs into logical groups:

```python
groups=[
    OpenAPIGroupConfig(name="core", apps=["users", "accounts"]),
    OpenAPIGroupConfig(name="billing", apps=["payments", "subscriptions"]),
    OpenAPIGroupConfig(name="content", apps=["blog", "cms"]),
]
```

### 4. Enable All Type Safety Features

```python
OpenAPIClientConfig(
    generate_zod_schemas=True,        # Runtime validation
    generate_package_files=True,      # Proper TypeScript setup
    generate_fetchers=True,           # Universal fetch functions
    generate_swr_hooks=True,          # React integration
)
```

---

## Next Steps

- **[CLI Commands](./cli-commands)** - Complete CLI reference for generation and validation
- **[Examples](./examples)** - Real-world usage examples
- **[Overview](./overview)** - Detailed feature overview
- **[Configuration Guide](/fundamentals/configuration)** - Advanced configuration options
- **[API Generation Overview](/features/api-generation/overview)** - High-level overview

:::tip Pro Tip
Add `python manage.py generate_api` to your deployment script to ensure clients are always up-to-date.
:::
