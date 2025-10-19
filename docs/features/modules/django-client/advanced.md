---
title: Advanced Topics
sidebar_position: 4
keywords:
  - django client groups
  - django client ci/cd
  - django client archive
  - openapi client groups
description: Advanced topics for Django Client. Groups, CI/CD integration, archiving, and monorepo support.
---

# Advanced Topics

Advanced configuration and usage patterns for production environments.

---

## Groups (API Organization)

Groups allow you to organize large APIs into logical units. Each group generates separate clients.

### Why Use Groups?

**Benefits:**
- ✅ Separate clients for different teams/features
- ✅ Smaller bundle sizes (import only what you need)
- ✅ Clear API boundaries
- ✅ Independent versioning
- ✅ Reduced compilation time

### Basic Configuration

```python
# api/config.py
from django_cfg import OpenAPIClientConfig, OpenAPIGroupConfig

openapi_client = OpenAPIClientConfig(
    enabled=True,
    output_dir="openapi",
    groups=[
        OpenAPIGroupConfig(
            name="core",
            apps=["users", "accounts", "profiles"],
            title="Core API",
            description="User management and authentication",
            version="1.0.0",
        ),
        OpenAPIGroupConfig(
            name="billing",
            apps=["payments", "subscriptions", "invoices"],
            title="Billing API",
            description="Payment processing",
            version="1.0.0",
        ),
        OpenAPIGroupConfig(
            name="content",
            apps=["blog", "cms", "media"],
            title="Content API",
            description="Content management",
            version="1.0.0",
        ),
    ],
)
```

### Output Structure

```
openapi/
├── core/                          # Group: core
│   ├── typescript/
│   │   ├── cfg__accounts/
│   │   ├── cfg__profiles/
│   │   ├── client.ts
│   │   └── index.ts
│   └── python/
│       ├── client.py
│       └── models/
│
├── billing/                       # Group: billing
│   ├── typescript/
│   └── python/
│
├── content/                       # Group: content
│   ├── typescript/
│   └── python/
│
└── archive/                       # Version history
    └── 2025-01-15_10-00-00/
```

### Monorepo Support

Perfect for monorepos with multiple frontends:

```python
groups=[
    # Web application
    OpenAPIGroupConfig(
        name="web",
        apps=["users", "billing", "content"],
        title="Web API",
    ),

    # Mobile application (smaller API surface)
    OpenAPIGroupConfig(
        name="mobile",
        apps=["users", "content"],  # No billing
        title="Mobile API",
    ),

    # Admin panel (internal APIs)
    OpenAPIGroupConfig(
        name="admin",
        apps=["users", "billing", "admin", "analytics"],
        title="Admin API",
    ),
]
```

### Generate Specific Groups

```bash
# Generate all groups
python manage.py generate_api

# Generate specific groups only
python manage.py generate_api --groups core,billing
```

---

## Archive System

Maintains version history of all generated clients.

### Configuration

```python
OpenAPIClientConfig(
    enabled=True,
    # Archive settings
    archive_enabled=True,
    archive_dir="openapi/archive",
    archive_max_versions=10,  # Keep last 10 versions
)
```

### Archive Structure

```
openapi/archive/
├── 2025-01-15_10-00-00/
│   ├── core/
│   │   ├── typescript/
│   │   └── python/
│   └── billing/
│       ├── typescript/
│       └── python/
│
├── 2025-01-15_11-00-00/
│   └── ...
│
└── 2025-01-15_12-00-00/
    └── ...
```

### Use Cases

**1. Compare Changes:**

```bash
# Compare two versions
diff -r openapi/archive/2025-01-15_10-00-00/core/typescript \
        openapi/archive/2025-01-15_11-00-00/core/typescript
```

**2. Rollback:**

```bash
# Rollback to previous version
cp -r openapi/archive/2025-01-15_10-00-00/core/* openapi/core/
```

**3. Track API Evolution:**

```bash
# View history
ls -lt openapi/archive/
```

---

## CI/CD Integration

### GitHub Actions

Automatically generate clients on API changes:

```yaml
# .github/workflows/generate-api-clients.yml
name: Generate API Clients

on:
  push:
    paths:
      - 'backend/**'
      - 'api/**'

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
          git config user.name "GitHub Actions"
          git config user.email "actions@github.com"
          git add openapi/
          git commit -m "chore: update API clients [skip ci]" || exit 0
          git push
```

### GitLab CI

```yaml
# .gitlab-ci.yml
generate-clients:
  stage: build
  image: python:3.12

  script:
    - pip install -r requirements.txt
    - python manage.py generate_api

  artifacts:
    paths:
      - openapi/
    expire_in: 30 days

  only:
    changes:
      - backend/**
      - api/**
```

### Pre-commit Hook

Automatically generate clients before commit:

```bash
# .git/hooks/pre-commit
#!/bin/bash

# Generate API clients
python manage.py generate_api

# Add generated files
git add openapi/

echo "✅ API clients regenerated"
```

---

## Docker Integration

### Build-time Generation

Generate clients during Docker build:

```dockerfile
FROM python:3.12

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy project
COPY . .

# Generate API clients during build
RUN python manage.py spectacular --file openapi.yaml && \
    python manage.py generate_api

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
```

### Multi-stage Build

```dockerfile
# Stage 1: Generate clients
FROM python:3.12 AS generator

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
RUN python manage.py generate_api

# Stage 2: Runtime
FROM python:3.12-slim

WORKDIR /app
COPY --from=generator /app/openapi /app/openapi
COPY . .

CMD ["python", "manage.py", "runserver"]
```

---

## Multiple Environments

Generate different clients for different environments:

```python
# config/dev.py
openapi_client = OpenAPIClientConfig(
    enabled=True,
    output_dir="openapi",
    drf_title="My API (Development)",
    groups=[
        OpenAPIGroupConfig(
            name="all",
            apps=["users", "accounts", "billing", "admin"],  # All APIs
        ),
    ],
)

# config/prod.py
openapi_client = OpenAPIClientConfig(
    enabled=True,
    output_dir="openapi",
    drf_title="My API (Production)",
    groups=[
        OpenAPIGroupConfig(
            name="public",
            apps=["users", "accounts", "billing"],  # No admin
        ),
    ],
)
```

---

## Custom Output Directories

Generate clients to custom locations:

```python
OpenAPIClientConfig(
    groups=[
        OpenAPIGroupConfig(
            name="web",
            apps=["users", "billing"],
            # Custom output for TypeScript
            typescript_output="../../apps/web/src/api/generated",
            # Custom output for Python
            python_output="../../services/api-client",
        ),
    ],
)
```

---

## Workspace Integration (pnpm/yarn/npm workspaces)

For monorepo workspaces:

```json
// package.json (root)
{
  "workspaces": [
    "apps/*",
    "packages/*"
  ]
}
```

Generate to workspace package:

```python
OpenAPIGroupConfig(
    name="shared",
    apps=["users", "billing"],
    typescript_output="../../packages/api-client/src",
)
```

Then use in apps:

```json
// apps/web/package.json
{
  "dependencies": {
    "@mycompany/api-client": "workspace:*"
  }
}
```

---

## Performance Optimization

### Parallel Generation

TypeScript and Python generated concurrently:

```python
# Built-in parallel generation (automatic)
python manage.py generate_api
```

### Incremental Generation (Future)

Only regenerate changed groups:

```bash
# Only regenerate core group
python manage.py generate_api --groups core
```

### Caching

Template caching is enabled by default:

```python
# Jinja2 templates compiled once
jinja_env = Environment(
    cache_size=400  # Cache 400 compiled templates
)
```

---

## Custom Templates (Advanced)

Override default templates:

```python
# custom_generator.py
from django_cfg.modules.django_client.core.generator.typescript import TypeScriptGenerator

class CustomTypeScriptGenerator(TypeScriptGenerator):
    def __init__(self, context, config):
        super().__init__(context, config)
        # Add custom template directory
        self.jinja_env.loader = ChoiceLoader([
            FileSystemLoader('my_templates'),  # Custom first
            FileSystemLoader('default_templates')  # Fallback
        ])
```

---

## Best Practices

### 1. Commit Generated Code

Always commit generated clients to version control:

```bash
git add openapi/
git commit -m "Update API clients"
```

This ensures:
- Frontend and backend stay in sync
- Easy code review of API changes
- No runtime generation needed

### 2. Use Groups for Large APIs

Split large APIs:

```python
groups=[
    OpenAPIGroupConfig(name="core", apps=["users", "auth"]),
    OpenAPIGroupConfig(name="billing", apps=["payments"]),
    OpenAPIGroupConfig(name="content", apps=["blog", "media"]),
]
```

### 3. Automate Generation

Add to CI/CD pipeline:

```yaml
- name: Generate clients
  run: python manage.py generate_api
```

### 4. Archive Old Versions

Enable archiving for version history:

```python
OpenAPIClientConfig(
    archive_enabled=True,
    archive_max_versions=10,
)
```

### 5. Validate Generated Code

Run type checkers:

```bash
# TypeScript
cd frontend && pnpm tsc --noEmit

# Python
cd backend && mypy api_client/
```

---

## Troubleshooting

See **[Troubleshooting](./troubleshooting)** for common issues and solutions.

---

## Next Steps

- **[Troubleshooting](./troubleshooting)** - Common issues
- **[Examples](./examples)** - Usage examples
- **[Overview](./overview)** - Feature overview
