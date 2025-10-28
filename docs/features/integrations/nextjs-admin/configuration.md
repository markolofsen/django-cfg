---
id: configuration
title: Configuration Reference
description: Complete configuration reference for Next.js admin integration
sidebar_label: Configuration
tags:
  - nextjs
  - admin
  - configuration
---

# Configuration Reference

Complete guide to configuring Next.js admin integration in django-cfg.

## Overview

The `NextJsAdminConfig` model provides type-safe configuration with smart defaults. You only need to specify what differs from the defaults.

```python
from django_cfg import DjangoConfig, NextJsAdminConfig

config = DjangoConfig(
    project_name="My Project",

    nextjs_admin=NextJsAdminConfig(
        project_path="../django_admin",  # Only required field
        # All other fields are optional with smart defaults
    ),
)
```

## Configuration Options

### Required Fields

#### `project_path`

**Type**: `str`
**Required**: Yes
**Description**: Path to your Next.js project (relative or absolute)

```python
# Relative path (recommended)
project_path="../django_admin"

# Absolute path
project_path="/home/user/projects/django_admin"
```

:::tip Best Practice
Use relative paths for better portability across environments.
:::

### Optional Fields

All optional fields have smart defaults that work for most use cases.

#### `api_output_path`

**Type**: `Optional[str]`
**Default**: `"apps/admin/src/api/generated"`
**Description**: Path for generated TypeScript clients (relative to `project_path`)

```python
# Default structure
nextjs_admin=NextJsAdminConfig(
    project_path="../django_admin",
    # Generated clients → ../django_admin/apps/admin/src/api/generated/
)

# Custom structure
nextjs_admin=NextJsAdminConfig(
    project_path="../django_admin",
    api_output_path="src/api/generated",
    # Generated clients → ../django_admin/src/api/generated/
)
```

**When to customize**: If your Next.js project doesn't follow the `apps/admin/` structure.

#### `static_output_path`

**Type**: `Optional[str]`
**Default**: `"out"`
**Description**: Next.js build output directory (relative to `project_path`)

```python
# Default: Static export
nextjs_admin=NextJsAdminConfig(
    project_path="../django_admin",
    # Build output → ../django_admin/out/
)

# Custom: Server mode
nextjs_admin=NextJsAdminConfig(
    project_path="../django_admin",
    static_output_path=".next",
    # Build output → ../django_admin/.next/
)
```

**When to customize**: If using Next.js server mode instead of static export.

:::warning Static Export Required
Currently, only static export mode is supported. Server-side rendering support is planned for future releases.
:::

#### `static_url`

**Type**: `Optional[str]`
**Default**: `"/cfg/admin/"`
**Description**: URL prefix for serving Next.js static files in production

```python
# Default
nextjs_admin=NextJsAdminConfig(
    project_path="../django_admin",
    # Accessible at: /cfg/admin/
)

# Custom URL
nextjs_admin=NextJsAdminConfig(
    project_path="../django_admin",
    static_url="/admin-ui/",
    # Accessible at: /admin-ui/
)
```

**When to customize**: If you want a different URL path for your admin.

:::note URL Format
The URL must start and end with `/`. Django-cfg will automatically format it if you forget.
:::

#### `dev_url`

**Type**: `Optional[str]`
**Default**: `"http://localhost:3001"`
**Description**: Next.js development server URL

```python
# Default port
nextjs_admin=NextJsAdminConfig(
    project_path="../django_admin",
    # Dev server at: http://localhost:3001
)

# Custom port (e.g., if 3001 is taken)
nextjs_admin=NextJsAdminConfig(
    project_path="../django_admin",
    dev_url="http://localhost:3002",
)
```

**When to customize**: If running multiple Next.js apps or port 3001 is unavailable.

:::tip Development Mode
Make sure to update your Next.js dev server port if you change this:
```bash
pnpm dev --port 3002
```
:::

#### `iframe_route`

**Type**: `Optional[str]`
**Default**: `"/private"`
**Description**: Next.js route to display in the iframe

```python
# Default
nextjs_admin=NextJsAdminConfig(
    project_path="../django_admin",
    # Shows: /private in iframe
)

# Custom route
nextjs_admin=NextJsAdminConfig(
    project_path="../django_admin",
    iframe_route="/dashboard",
    # Shows: /dashboard in iframe
)
```

**When to customize**: If your main admin page is at a different route.

#### `iframe_sandbox`

**Type**: `Optional[str]`
**Default**: `"allow-same-origin allow-scripts allow-forms allow-popups allow-modals allow-storage-access-by-user-activation"`
**Description**: HTML5 iframe sandbox attribute for security

```python
# Default (recommended)
nextjs_admin=NextJsAdminConfig(
    project_path="../django_admin",
)

# Custom sandbox (advanced)
nextjs_admin=NextJsAdminConfig(
    project_path="../django_admin",
    iframe_sandbox="allow-same-origin allow-scripts",
)
```

**When to customize**: Only if you need stricter or different security policies.

:::danger Security Warning
Removing `allow-same-origin` will prevent JWT token injection and API calls. Only customize if you know what you're doing.
:::

#### `tab_title`

**Type**: `Optional[str]`
**Default**: `"Next.js Admin"`
**Description**: Title for the Next.js admin tab in Django admin

```python
# Default
nextjs_admin=NextJsAdminConfig(
    project_path="../django_admin",
    # Tab shows: "Next.js Admin"
)

# Custom title
nextjs_admin=NextJsAdminConfig(
    project_path="../django_admin",
    tab_title="Analytics Dashboard",
    # Tab shows: "Analytics Dashboard"
)
```

**When to customize**: For more descriptive or branded tab names.

#### `auto_copy_api`

**Type**: `bool`
**Default**: `True`
**Description**: Automatically copy generated TypeScript clients to Next.js project

```python
# Default (recommended)
nextjs_admin=NextJsAdminConfig(
    project_path="../django_admin",
    auto_copy_api=True,
)

# Disable auto-copy
nextjs_admin=NextJsAdminConfig(
    project_path="../django_admin",
    auto_copy_api=False,
)
```

**When to customize**: If you want to manually manage API client files.

:::tip Recommended
Keep this as `True` for seamless development workflow.
:::

## Configuration Examples

### Minimal Configuration

Most common use case with all defaults:

```python title="api/config.py"
from django_cfg import DjangoConfig, NextJsAdminConfig

config = DjangoConfig(
    project_name="My Project",
    secret_key="your-secret-key",

    nextjs_admin=NextJsAdminConfig(
        project_path="../django_admin",
    ),
)
```

This gives you:
- ✅ API clients at: `apps/admin/src/api/generated/`
- ✅ Build output at: `out/`
- ✅ Dev server at: `http://localhost:3001`
- ✅ Production URL: `/cfg/admin/`
- ✅ iframe shows: `/private`
- ✅ Tab title: "Next.js Admin"
- ✅ Auto-copy API enabled

### Custom Development Port

If port 3001 is taken:

```python title="api/config.py"
config = DjangoConfig(
    project_name="My Project",

    nextjs_admin=NextJsAdminConfig(
        project_path="../django_admin",
        dev_url="http://localhost:3002",
    ),
)
```

Don't forget to update Next.js:

```json title="package.json"
{
  "scripts": {
    "dev": "next dev -p 3002"
  }
}
```

### Custom URL Prefix

For a different production URL:

```python title="api/config.py"
config = DjangoConfig(
    project_name="My Project",

    nextjs_admin=NextJsAdminConfig(
        project_path="../django_admin",
        static_url="/dashboard/",
        tab_title="Analytics Dashboard",
    ),
)
```

Admin accessible at: `http://yourdomain.com/dashboard/`

### Custom Next.js Structure

If your Next.js project has a different structure:

```python title="api/config.py"
config = DjangoConfig(
    project_name="My Project",

    nextjs_admin=NextJsAdminConfig(
        project_path="../my-nextjs-app",
        api_output_path="src/lib/api",
        static_output_path="dist",
    ),
)
```

This assumes:
```
my-nextjs-app/
├── src/
│   └── lib/
│       └── api/         # Generated clients here
└── dist/               # Build output here
```

### Multiple Configurations (Advanced)

For projects with multiple Next.js admins:

```python title="api/config.py"
# This is planned for future releases
# Currently only one Next.js admin is supported

config = DjangoConfig(
    project_name="My Project",

    nextjs_admin=NextJsAdminConfig(
        project_path="../django_admin",
        static_url="/admin/",
        tab_title="Main Admin",
    ),
)
```

:::info Future Feature
Support for multiple Next.js admins is planned. Track progress in [GitHub Issue #XXX](#).
:::

## Accessing Configuration at Runtime

### In Django Code

Access configuration from template tags:

```python
from django_cfg.modules.nextjs_admin.templatetags.nextjs_admin import (
    has_nextjs_admin,
    get_nextjs_admin_config,
)

# Check if Next.js admin is configured
if has_nextjs_admin():
    config = get_nextjs_admin_config()
    print(f"Next.js admin at: {config.get_static_url()}")
```

### In Templates

Use template tags:

```django
{% load nextjs_admin %}

{% has_nextjs_admin as is_enabled %}
{% if is_enabled %}
  <div>
    <h2>{% nextjs_admin_tab_title %}</h2>
    <iframe src="{% nextjs_external_url %}"></iframe>
  </div>
{% endif %}
```

### Available Template Tags

```django
{% load nextjs_admin %}

{# Check if Next.js admin is configured #}
{% has_nextjs_admin as is_enabled %}

{# Get iframe URL #}
{% nextjs_external_url %}
{% nextjs_external_url 'dashboard' %}  {# Custom route #}

{# Get tab title #}
{% nextjs_admin_tab_title %}

{# Get static URL prefix #}
{% nextjs_admin_static_url %}
```

## Validation

Django-cfg validates your configuration at startup:

### Valid Configuration

```python
nextjs_admin=NextJsAdminConfig(
    project_path="../django_admin",  # ✅ Valid
)
```

### Invalid Configurations

```python
# ❌ Empty project_path
nextjs_admin=NextJsAdminConfig(
    project_path="",
)
# Raises: ValueError: project_path cannot be empty

# ❌ Invalid URL format
nextjs_admin=NextJsAdminConfig(
    project_path="../django_admin",
    static_url="admin",  # Missing slashes
)
# Auto-corrected to: "/admin/"
```

## Environment-Specific Configuration

Use environment variables for different configurations:

```python title="api/config.py"
import os

config = DjangoConfig(
    project_name="My Project",

    nextjs_admin=NextJsAdminConfig(
        project_path=os.getenv(
            "NEXTJS_ADMIN_PATH",
            "../django_admin"
        ),
        dev_url=os.getenv(
            "NEXTJS_DEV_URL",
            "http://localhost:3001"
        ),
    ),
)
```

Then use different `.env` files:

```bash title=".env.development"
NEXTJS_ADMIN_PATH=../django_admin
NEXTJS_DEV_URL=http://localhost:3001
```

```bash title=".env.production"
NEXTJS_ADMIN_PATH=/app/django_admin
# dev_url not used in production
```

## Next Steps

- [How It Works](./how-it-works) - Understand the architecture
- [API Generation](./api-generation) - Generate TypeScript clients
- [Deployment](./deployment) - Deploy to production
- [Troubleshooting](./troubleshooting) - Common issues and solutions
