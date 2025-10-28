---
title: Overview
sidebar_position: 1
keywords:
  - django client generator
  - openapi client generator
  - typescript client generator
  - python client generator
  - type-safe api client
description: Auto-generate production-ready TypeScript, Python, Go, and Protocol Buffer clients from OpenAPI specs. Built for Django REST Framework with drf-spectacular.
---

# Django Client Generator

**Auto-generate type-safe, production-ready API clients from OpenAPI 3.0/3.1 specifications**

The `django_client` module generates TypeScript, Python, Go, and Protocol Buffer clients optimized for Django REST Framework applications. Unlike generic OpenAPI generators, it produces clean, framework-specific code for modern ecosystems.

## What It Generates

The django_client module generates clients for multiple languages and protocols:

- **TypeScript** - Type-safe client with Zod validation, SWR hooks, universal fetchers
- **Python** - Async Pydantic 2 client with full type hints
- **Go** - Typed HTTP client with structs and interfaces
- **Protocol Buffers** - Proto3 definitions for gRPC services

### TypeScript Client Structure

```
frontend/src/api/generated/
├── cfg__accounts/                    # Tag-based folders
│   ├── client.ts                     # API client class
│   ├── models.ts                     # TypeScript interfaces
│   ├── index.ts                      # Exports
│   └── _utils/                       # Universal helpers
│       ├── fetchers/                 # Typed fetch functions
│       │   └── accounts.ts           # Works in Server Components, Client Components, React Native
│       ├── hooks/                    # SWR React hooks
│       │   └── accounts.ts           # Client-side data fetching with caching
│       └── schemas/                  # Zod validation schemas
│           ├── User.schema.ts        # Runtime type validation
│           └── UserRequest.schema.ts
│
├── cfg__payments/
│   └── ...                           # Same structure for each tag
│
├── client.ts                         # Main client
├── schema.ts                         # All Zod schemas
├── enums.ts                          # Enums
├── errors.ts                         # Error handling
├── http.ts                           # HTTP layer
├── logger.ts                         # Logging
├── retry.ts                          # Retry logic
├── storage.ts                        # Storage utilities
└── api-instance.ts                   # Singleton instance
```

### Python Client Structure

```
backend/api_client/
├── __init__.py
├── client.py                         # Main async client
├── models/                           # Pydantic 2 models
│   ├── accounts.py                   # User, UserRequest models
│   └── payments.py                   # Payment models
└── subclients/                       # Sub-clients by tag
    ├── accounts.py                   # client.accounts.*
    └── payments.py                   # client.payments.*
```

### Protocol Buffers Structure

```
openapi/clients/proto/
├── profiles/                         # Group name
│   ├── api__profiles/                # Service folder
│   │   ├── messages.proto            # Message definitions (models, enums)
│   │   ├── service.proto             # gRPC service definitions
│   │   ├── messages_pb2.py           # Compiled Python messages
│   │   ├── messages_pb2_grpc.py      # Empty (no services in messages)
│   │   ├── service_pb2.py            # Request/Response messages
│   │   └── service_pb2_grpc.py       # gRPC client stubs & server servicers
│   └── README.md                      # Compilation guide
│
├── trading/                          # Another group
│   └── api__trading/
│       └── ...                        # Same structure
│
└── cfg/                              # Large group (21 services)
    ├── accounts/
    ├── payments/
    ├── knowbase/
    └── ...                            # One folder per service
```

:::info Compilation Required
Proto files are source files that must be compiled with `protoc` before use. Each group includes a README.md with compilation commands for Python, Go, TypeScript, C++, Java, and more.
:::

---

## Key Features

### 🎯 Universal Fetch Functions

Typed functions that work in **any** JavaScript environment:

```typescript
// Generated: cfg__accounts/_utils/fetchers/accounts.ts
export async function getUsers(
  params?: { page?: number; page_size?: number },
  client?: API
): Promise<PaginatedUserList> {
  const api = client || getAPIInstance()
  const response = await api.accounts.list(params)
  return PaginatedUserListSchema.parse(response)
}
```

**Works in:**
- ✅ Next.js Server Components (async/await)
- ✅ Next.js Client Components
- ✅ React Native mobile apps
- ✅ Node.js backend services
- ✅ Remix loaders/actions

### ⚛️ React SWR Hooks

Client-side hooks with caching and revalidation:

```typescript
// Generated: cfg__accounts/_utils/hooks/accounts.ts
export function useUsers(params?: { page?: number }) {
  return useSWR(
    params ? ['users', params] : 'users',
    () => getUsers(params)
  )
}

// Usage
function UsersTable() {
  const { data, error, isLoading, mutate } = useUsers({ page: 1 })
  // Auto-caching, revalidation, error retry
}
```

### ✅ Zod Validation Schemas

Runtime type validation for all models:

```typescript
// Generated: cfg__accounts/_utils/schemas/User.schema.ts
export const UserSchema = z.object({
  id: z.number(),
  username: z.string().min(1).max(150),
  email: z.email(),
  created_at: z.string()
})

// Runtime validation
const user = UserSchema.parse(apiResponse)  // ✅ Type-safe
```

### 🔄 Request/Response Split

Automatically detects and separates request/response models:

```typescript
// Response model (includes read-only fields)
interface User {
  id: number              // ✅ read-only
  username: string
  email: string
  created_at: string      // ✅ read-only
}

// Request model (excludes read-only fields)
interface UserRequest {
  username: string
  email: string
  password: string        // ✅ write-only
}

// Patch model (all fields optional)
interface PatchedUserRequest {
  username?: string
  email?: string
  password?: string
}
```

### 🏗️ IR Layer (Intermediate Representation)

The core innovation that makes it all work:

```
OpenAPI 3.0/3.1 → Parser → IR Layer → Generators → TypeScript/Python

IR Layer benefits:
✅ Version-agnostic (handles both OpenAPI 3.0 and 3.1)
✅ Language-agnostic (same IR for all generators)
✅ Fully typed with Pydantic 2
✅ Normalizes nullable fields, enums, formats
```

The IR layer decouples parsing from generation, making it easy to add new languages without changing parsers.

### 🎛️ Groups (API Organization)

Organize large APIs into logical groups:

```python
# Django-CFG configuration
openapi_client: OpenAPIClientConfig = OpenAPIClientConfig(
    enabled=True,
    generate_package_files=True,
    generate_zod_schemas=True,
    generate_fetchers=True,
    generate_swr_hooks=True,
    api_prefix="api",
    output_dir="openapi",
    drf_title="My App API",
    drf_description="Complete API documentation",
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
            description="Payment processing",
            version="1.0.0",
        ),
    ],
)
```

**Benefits:**
- Separate clients for different teams/features
- Smaller bundle sizes (import only what you need)
- Clear API boundaries
- Independent versioning

---

## How It Works

### 1. OpenAPI Parsing

```
OpenAPI YAML/JSON → openapi-pydantic → Validated spec
```

Supports both OpenAPI 3.0 and 3.1 with full validation.

### 2. IR Transformation

```
Parsed spec → IR Layer
  ├── IRSchemaObject (type definitions)
  ├── IROperationObject (API operations)
  ├── IRParameterObject (parameters)
  └── IRContext (validation & relationships)
```

The IR layer normalizes OpenAPI into a version-agnostic, language-agnostic representation.

### 3. Code Generation

```
IR Context → Universal Builders → Language Generators

Universal Builders:
  ├── ParamsBuilder (eliminates parameter duplication)
  ├── TypeScriptValidator (validates before compilation)
  └── BaseGenerator (common utilities)

Language Generators:
  ├── TypeScript → fetchers + hooks + schemas
  └── Python → async client + Pydantic models
```

### 4. Validation & Output

```
Generated code → TypeScriptValidator → File system

Validation catches:
  ❌ Required params after optional
  ❌ Required fields in optional objects
  ❌ Invalid type definitions
```

---

## Real-World Example

### Next.js Server Component

```typescript
// app/users/page.tsx
import { getUsers } from '@/api/generated/cfg__accounts/_utils/fetchers/accounts'

export default async function UsersPage() {
  // Type-safe server-side fetching
  const users = await getUsers({ page: 1, page_size: 20 })

  return (
    <div>
      <h1>Users ({users.count})</h1>
      <ul>
        {users.results.map(user => (
          <div key={user.id}>
            {user.username} - {user.email}
          </div>
        ))}
      </ul>
    </div>
  )
}
```

### React Client Component

```typescript
'use client'
import { useUsers } from '@/api/generated/cfg__accounts/_utils/hooks/accounts'

export default function UsersTable() {
  const { data, error, isLoading } = useUsers({ page: 1 })

  if (isLoading) return <Spinner />
  if (error) return <Error error={error} />

  return <Table data={data.results} />
}
```

### Python Async Client

```python
from api_client import APIClient

async def main():
    client = APIClient(base_url="https://api.example.com")

    # List users
    users = await client.accounts.list(page=1, page_size=20)
    for user in users.results:
        print(f"{user.username} - {user.email}")

    # Create user
    new_user = await client.accounts.create(data={
        "username": "alice",
        "email": "alice@example.com",
        "password": "secret123"
    })
```

---

## Why Use This?

### Problem: Generic Generators Don't Fit Django

Generic OpenAPI generators (`openapi-generator`, `swagger-codegen`) produce:
- ❌ Bloated code with unnecessary dependencies
- ❌ Poor TypeScript types (excessive `any` usage)
- ❌ No React integration (no hooks, no SWR)
- ❌ Incompatible with Next.js Server Components
- ❌ No validation or error prevention

### Solution: Purpose-Built for Django + Modern JS

`django_client` is specifically designed for:
- ✅ Django REST Framework + drf-spectacular
- ✅ Next.js 13+ (App Router, Server Components)
- ✅ React with SWR for data fetching
- ✅ React Native mobile apps
- ✅ Pydantic 2 for Python clients
- ✅ Full type safety end-to-end

---

## Advanced Features

### ✅ File Uploads

Type-safe multipart/form-data handling:

```typescript
interface DocumentRequest {
  title: string
  file: File | Blob        // ✅ Binary field
  is_public: boolean
}

await uploadDocument({
  title: "Doc",
  file: fileInput.files[0]  // ✅ Type-checked
})
```

### ✅ Custom Actions (Django ViewSet)

Supports Django `@action` decorator:

```python
# Django
class UserViewSet(viewsets.ModelViewSet):
    @action(detail=False, methods=['get'])
    def active(self, request):
        ...

# Generated TypeScript
await client.users.active()  // ✅ Available

# Generated Python
await client.users.active()  // ✅ Available
```

### ✅ Archive System

Maintains version history of all generated clients:

```
openapi/archive/
├── 2025-01-15_10-00-00/
│   ├── typescript/
│   └── python/
├── 2025-01-15_11-00-00/
│   └── ...
```

**Benefits:**
- Compare changes between versions
- Rollback if needed
- Track API evolution
- Debug client issues

---

## Configuration

### Basic (Django-CFG)

```python
from django_cfg import OpenAPIClientConfig, OpenAPIGroupConfig

openapi_client = OpenAPIClientConfig(
    enabled=True,
    generate_package_files=True,
    generate_zod_schemas=True,
    generate_fetchers=True,
    generate_swr_hooks=True,
    api_prefix="api",
    output_dir="openapi",
    groups=[
        OpenAPIGroupConfig(
            name="core",
            apps=["users", "accounts"],
            title="Core API"
        ),
    ],
)
```

### CLI Commands

```bash
# Generate all groups from Django-CFG
python manage.py generate_api

# Generate single TypeScript client
python manage.py generate_ts_client \
  --openapi-schema openapi.yaml \
  --output frontend/src/api/generated

# Generate single Python client
python manage.py generate_python_client \
  --openapi-schema openapi.yaml \
  --output backend/api_client
```

---

## Performance

Optimized for large APIs:

**Benchmark** (300 operations):
- Parsing: ~500ms
- IR Transformation: ~200ms
- TypeScript Generation: ~1.5s
- Python Generation: ~800ms
- **Total: ~3 seconds**

**Features:**
- ✅ Parallel generation (TypeScript + Python concurrently)
- ✅ Template caching (Jinja2 compiled once)
- ✅ Lazy loading (IR schemas loaded on demand)

---

## Key Concepts

### 1. IR Layer

The **Intermediate Representation** layer is the core innovation:

```python
class IRSchemaObject:
    """Type-safe schema representation"""
    name: str                    # "User"
    type: str                    # "object", "string", "array"
    properties: dict            # Nested properties
    required: list[str]         # Required fields
    nullable: bool              # Normalized from both 3.0 and 3.1

    @property
    def typescript_type(self) -> str:
        """Get TypeScript type"""

    @property
    def python_type(self) -> str:
        """Get Python type"""
```

### 2. Universal Builders

Eliminates code duplication:

**ParamsBuilder** - Handles parameter logic for ALL generators:
```python
builder = ParamsBuilder(context, base)
params = builder.build_params_structure(operation)

# Returns:
# - Function signature
# - API call arguments
# - SWR key
# - Return type
```

**Benefits:**
- ✅ Single source of truth
- ✅ Reduced code by 40%
- ✅ Consistent behavior

### 3. Request/Response Split

Django REST Framework serializers serve both input and output:

```python
# DRF Serializer
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'created_at']
        read_only_fields = ['id', 'created_at']
```

**Generated:**
- `User` (response) - includes `id`, `created_at`
- `UserRequest` (request) - excludes `id`, `created_at`
- `PatchedUserRequest` (patch) - all fields optional

---

## Next Steps

- **[Getting Started](./getting-started)** - Installation and setup (10 minutes)
- **[CLI Commands](./cli-commands)** - Complete CLI reference for generation and validation
- **[Examples](./examples)** - Real-world usage patterns
- **[Configuration Guide](/fundamentals/configuration)** - Advanced configuration

---

## Related Documentation

- **[API Generation Overview](/features/api-generation/overview)** - High-level overview
- **[Group Configuration](/features/api-generation/groups)** - Organizing APIs with groups
- **[CLI Usage](/features/api-generation/cli-usage)** - Management commands
