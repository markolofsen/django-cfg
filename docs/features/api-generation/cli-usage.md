---
title: CLI Usage
sidebar_position: 2
keywords:
  - django-cfg cli
  - api client generation commands
  - generate api clients
description: Django-CFG management commands for generating type-safe API clients. Command-line interface for creating TypeScript and Python client libraries.
---

# CLI Usage

Django-CFG provides management commands to generate type-safe API clients from your Django REST Framework API. This guide covers all available commands and common workflows.

## Available Commands

### `generate_api`

Generate all API clients defined in your `openapi_client.groups` configuration.

```bash
python manage.py generate_api
```

This command:
1. Reads groups from your Django-CFG configuration
2. Generates OpenAPI schemas for each group
3. Creates TypeScript and Python clients for each group
4. Outputs clients to the configured directory

**Options:**
```bash
python manage.py generate_api [--help]
```

### `generate_ts_client`

Generate a TypeScript client from an OpenAPI schema.

```bash
python manage.py generate_ts_client \
  --openapi-schema path/to/openapi.yaml \
  --output frontend/src/api/generated
```

**Options:**
- `--openapi-schema PATH` - Path to OpenAPI schema file (required)
- `--output PATH` - Output directory for generated client (required)
- `--generate-fetchers` - Generate typed fetch functions
- `--generate-hooks` - Generate SWR hooks for React
- `--generate-zod-schemas` - Generate Zod validation schemas
- `--generate-package-files` - Generate package.json and tsconfig.json

### `generate_python_client`

Generate a Python client from an OpenAPI schema.

```bash
python manage.py generate_python_client \
  --openapi-schema path/to/openapi.yaml \
  --output backend/api_client
```

**Options:**
- `--openapi-schema PATH` - Path to OpenAPI schema file (required)
- `--output PATH` - Output directory for generated client (required)
- `--async-client` - Generate async client (default: True)

### `generate_client` with `--proto`

Generate Protocol Buffer definitions from OpenAPI schema using the unified command:

```bash
python manage.py generate_client \
  --openapi-files path/to/openapi.yaml \
  --output-dir openapi/clients \
  --group profiles \
  --proto --no-python --no-typescript --no-go
```

**Options:**
- `--proto` - Generate Protocol Buffer definitions
- `--no-proto` - Skip Protocol Buffer generation (when generating all clients)
- `--group NAME` - Group name for the generated clients

**Proto-specific features:**
- Generates `messages.proto` and `service.proto` for each service
- Creates README.md with compilation instructions
- Supports all OpenAPI types, enums, arrays, and nested objects
- Handles multipart/form-data as `bytes` fields

### Compiling Proto Files

After generation, compile proto files for your target language:

#### Python (grpcio-tools)
```bash
# Install dependencies
pip install grpcio grpcio-tools

# Compile proto files
cd openapi/clients/proto/profiles
python -m grpc_tools.protoc -I. \
  --python_out=. \
  --grpc_python_out=. \
  api__profiles/*.proto
```

#### Go
```bash
# Install dependencies
go install google.golang.org/protobuf/cmd/protoc-gen-go@latest
go install google.golang.org/grpc/cmd/protoc-gen-go-grpc@latest

# Compile proto files
cd openapi/clients/proto/profiles
protoc -I. \
  --go_out=. \
  --go-grpc_out=. \
  api__profiles/*.proto
```

#### TypeScript (ts-proto)
```bash
# Install dependencies
npm install ts-proto

# Compile proto files
cd openapi/clients/proto/profiles
protoc -I. \
  --plugin=./node_modules/.bin/protoc-gen-ts_proto \
  --ts_proto_out=. \
  api__profiles/*.proto
```

:::tip Auto-Generated README
Each generated proto group includes a README.md with detailed compilation commands for all supported languages.
:::

## Quick Start

### Generate All Clients from Groups

The simplest approach - generate all clients defined in your configuration:

```bash
python manage.py generate_api
```

This uses your `openapi_client.groups` configuration:

```python
# api/config.py
openapi_client: OpenAPIClientConfig = OpenAPIClientConfig(
    enabled=True,
    groups=[
        OpenAPIGroupConfig(name="core", apps=["users", "accounts"]),
        OpenAPIGroupConfig(name="shop", apps=["products", "orders"]),
    ],
)
```

### Generate Single Client

For more control, generate individual clients:

```bash
# 1. Export OpenAPI schema
python manage.py spectacular --format openapi --file openapi.yaml

# 2. Generate TypeScript client
python manage.py generate_ts_client \
  --openapi-schema openapi.yaml \
  --output frontend/src/api/generated \
  --generate-fetchers \
  --generate-hooks \
  --generate-zod-schemas

# 3. Generate Python client
python manage.py generate_python_client \
  --openapi-schema openapi.yaml \
  --output backend/api_client \
  --async-client
```

## Common Workflows

### Development Workflow

During active development, regenerate clients frequently:

```bash
# Quick regeneration
python manage.py generate_api
```

### Frontend-Only Workflow

If you only need TypeScript clients:

```bash
# Export schema
python manage.py spectacular --format openapi --file openapi.yaml

# Generate TypeScript only
python manage.py generate_ts_client \
  --openapi-schema openapi.yaml \
  --output frontend/src/api/generated \
  --generate-fetchers \
  --generate-hooks \
  --generate-zod-schemas \
  --generate-package-files
```

### Backend-Only Workflow

For Python microservices needing to call your API:

```bash
# Export schema
python manage.py spectacular --format openapi --file openapi.yaml

# Generate Python only
python manage.py generate_python_client \
  --openapi-schema openapi.yaml \
  --output services/api_client \
  --async-client
```

### Multi-Group Workflow

Generate separate clients for different API groups:

```bash
# Export schemas for each group
python manage.py spectacular --api-version core --format openapi --file core-api.yaml
python manage.py spectacular --api-version shop --format openapi --file shop-api.yaml

# Generate TypeScript clients
python manage.py generate_ts_client --openapi-schema core-api.yaml --output frontend/src/api/core
python manage.py generate_ts_client --openapi-schema shop-api.yaml --output frontend/src/api/shop

# Generate Python clients
python manage.py generate_python_client --openapi-schema core-api.yaml --output backend/clients/core
python manage.py generate_python_client --openapi-schema shop-api.yaml --output backend/clients/shop
```

## Output Examples

### Successful Generation (TypeScript)

```bash
$ python manage.py generate_ts_client --openapi-schema openapi.yaml --output frontend/src/api

🚀 Generating TypeScript client from openapi.yaml
📁 Output directory: frontend/src/api
✅ TypeScript client generated successfully!
📊 Generated files:
   - client.ts
   - models.ts
   - enums.ts
   - index.ts
   - _utils/fetchers/users.ts
   - _utils/fetchers/products.ts
   - _utils/hooks/users.ts
   - _utils/hooks/products.ts
   - _utils/schemas/User.schema.ts
   - _utils/schemas/Product.schema.ts
📦 Total: 28 files
⏱️  Generation completed in 2.3s
```

### Successful Generation (Python)

```bash
$ python manage.py generate_python_client --openapi-schema openapi.yaml --output backend/api_client

🚀 Generating Python client from openapi.yaml
📁 Output directory: backend/api_client
✅ Python client generated successfully!
📊 Generated files:
   - __init__.py
   - client.py
   - models/users.py
   - models/products.py
   - subclients/users.py
   - subclients/products.py
📦 Total: 19 files
⏱️  Generation completed in 1.8s
```

### Group-Based Generation

```bash
$ python manage.py generate_api

🚀 Generating API clients from groups configuration
📁 Output directory: openapi/
🎯 Groups: core, shop, content

Group: core
  ✅ TypeScript client: openapi/core/typescript/
  ✅ Python client: openapi/core/python/

Group: shop
  ✅ TypeScript client: openapi/shop/typescript/
  ✅ Python client: openapi/shop/python/

Group: content
  ✅ TypeScript client: openapi/content/typescript/
  ✅ Python client: openapi/content/python/

📊 Total: 3 groups, 234 files generated
⏱️  Generation completed in 8.7s
```

## Troubleshooting

### No Operations Found

If generation succeeds but creates empty clients:

**1. Check ViewSets are registered:**
```python
# users/api/views.py
from rest_framework import viewsets

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
```

**2. Verify URL patterns:**
```python
# users/urls.py
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register('users', UserViewSet)
urlpatterns = router.urls
```

**3. Validate OpenAPI schema:**
```bash
python manage.py spectacular --validate --format openapi --file openapi.yaml
```

### TypeScript Compilation Errors

If generated TypeScript has errors:

**1. Install dependencies:**
```bash
cd frontend
npm install zod swr
```

**2. Check TypeScript configuration:**
```json
{
  "compilerOptions": {
    "strict": true,
    "skipLibCheck": true,
    "esModuleInterop": true
  }
}
```

**3. Verify generation options:**
```bash
python manage.py generate_ts_client \
  --openapi-schema openapi.yaml \
  --output frontend/src/api \
  --generate-fetchers \
  --generate-hooks \
  --generate-zod-schemas \
  --generate-package-files  # ← Important for proper TS setup
```

### Python Import Errors

If Python client can't be imported:

**1. Ensure output directory is in Python path:**
```python
import sys
sys.path.append('/path/to/backend')

from api_client import APIClient
```

**2. Install dependencies:**
```bash
pip install pydantic>=2.0 httpx>=0.24
```

**3. Verify __init__.py files exist:**
```bash
ls -la backend/api_client/__init__.py
```

### Schema Generation Fails

Common issues with drf-spectacular:

**1. Install drf-spectacular:**
```bash
pip install drf-spectacular>=0.26.5
```

**2. Configure Django settings:**
```python
INSTALLED_APPS = [
    # ...
    'rest_framework',
    'drf_spectacular',
]

REST_FRAMEWORK = {
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
}
```

**3. Check for validation errors:**
```bash
python manage.py spectacular --validate
```

### Rate Limiting Blocks Schema Generation

If schema endpoints are rate limited:

Add `/schema/` to rate limiting exempt paths in your Django-CFG configuration or middleware.

## Advanced Usage

### Custom Output Directories

Generate clients to custom locations:

```bash
# TypeScript to multiple locations
python manage.py generate_ts_client \
  --openapi-schema openapi.yaml \
  --output packages/api-client/src

# Python to shared package
python manage.py generate_python_client \
  --openapi-schema openapi.yaml \
  --output shared/python-client
```

### CI/CD Integration

Example GitHub Actions workflow:

```yaml
name: Generate API Clients

on:
  push:
    paths:
      - 'api/**'
      - 'config/**'

jobs:
  generate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.12'

      - name: Install dependencies
        run: |
          pip install -r requirements.txt

      - name: Generate API clients
        run: |
          python manage.py generate_api

      - name: Commit generated clients
        run: |
          git config --local user.email "action@github.com"
          git config --local user.name "GitHub Action"
          git add openapi/
          git commit -m "chore: update API clients [skip ci]" || true
          git push
```

### Docker Integration

Generate clients in Docker:

```dockerfile
FROM python:3.12

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

# Generate clients on build
RUN python manage.py generate_api

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
```

### Pre-commit Hook

Auto-generate clients on commit:

```bash
# .git/hooks/pre-commit
#!/bin/bash
python manage.py generate_api
git add openapi/
```

## Best Practices

### 1. Version Control Generated Code

Always commit generated clients:

```bash
git add frontend/src/api/generated
git add backend/api_client
git commit -m "Update API clients"
```

### 2. Regenerate After API Changes

After modifying serializers or views:

```bash
python manage.py generate_api
```

### 3. Use Groups for Organization

Configure logical groups in Django-CFG:

```python
groups=[
    OpenAPIGroupConfig(name="core", apps=["users", "auth"]),
    OpenAPIGroupConfig(name="billing", apps=["payments", "subscriptions"]),
]
```

### 4. Enable All Type Safety Features

For TypeScript clients, enable all features:

```bash
python manage.py generate_ts_client \
  --openapi-schema openapi.yaml \
  --output frontend/src/api \
  --generate-fetchers \
  --generate-hooks \
  --generate-zod-schemas \
  --generate-package-files
```

## Next Steps

- **[Group Configuration](./groups)** - Configure API groups
- **[Generated Clients](./generated-clients)** - Use generated clients
- **[Django Client Module](/features/modules/django-client/overview)** - Deep dive

:::tip Pro Tip
Add `python manage.py generate_api` to your deployment script to ensure clients are always up-to-date.
:::
