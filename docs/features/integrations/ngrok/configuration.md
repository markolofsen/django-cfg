---
title: Ngrok Configuration Reference
description: Django-CFG configuration feature guide. Production-ready ngrok configuration reference with built-in validation, type safety, and seamless Django integration.
sidebar_label: Configuration
sidebar_position: 2
keywords:
  - django-cfg configuration
  - django configuration
  - configuration django-cfg
---

# Ngrok Configuration Reference

Complete reference for configuring ngrok integration in Django-CFG.

## Basic Configuration

```python
from django_cfg import DjangoConfig, NgrokConfig

class MyConfig(DjangoConfig):
    project_name: str = "My Project"

    # Enable ngrok for webhook development
    ngrok: NgrokConfig = NgrokConfig(
        enabled=True,  # Enable ngrok (only in DEBUG=True)
        auto_start=True,  # Auto-start with runserver_ngrok
        webhook_path="/api/webhooks/",  # Path for webhook URLs
        update_api_url=True  # Automatically update api_url
    )

config = MyConfig()
```

### NgrokConfig Fields

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `enabled` | `bool` | `False` | Enable ngrok integration (only works when `DEBUG=True`) |
| `auto_start` | `bool` | `True` | Automatically start tunnel when using `runserver_ngrok` |
| `webhook_path` | `str` | `"/webhooks/"` | Default path for webhook URLs |
| `update_api_url` | `bool` | `True` | Automatically update `api_url` with tunnel URL |
| `auth` | `NgrokAuthConfig` | `None` | Authentication configuration |
| `tunnel` | `NgrokTunnelConfig` | `None` | Tunnel-specific settings |

---

## Advanced Configuration

### With Authentication

For advanced ngrok features like custom domains, you need an auth token:

```python
from django_cfg import NgrokConfig, NgrokAuthConfig

ngrok: NgrokConfig = NgrokConfig(
    enabled=True,

    # Authentication
    auth=NgrokAuthConfig(
        authtoken_from_env=True  # Load from NGROK_AUTHTOKEN env var
    )
)
```

**Or provide token directly:**

```python
ngrok: NgrokConfig = NgrokConfig(
    enabled=True,

    auth=NgrokAuthConfig(
        authtoken="your_ngrok_token_here"  # Not recommended for production
    )
)
```

### NgrokAuthConfig Fields

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `authtoken` | `str` | `None` | Ngrok auth token (get from [ngrok.com](https://ngrok.com)) |
| `authtoken_from_env` | `bool` | `False` | Load auth token from `NGROK_AUTHTOKEN` environment variable |

---

### With Custom Tunnel Settings

Advanced tunnel configuration for paid ngrok plans:

```python
from django_cfg import NgrokConfig, NgrokTunnelConfig

ngrok: NgrokConfig = NgrokConfig(
    enabled=True,

    # Tunnel settings
    tunnel=NgrokTunnelConfig(
        domain="myapp.ngrok.io",  # Custom domain (paid plan)
        basic_auth=["admin:secret"],  # Password protect tunnel
        compression=True,  # Enable gzip compression
        bind_tls=True,  # Force HTTPS
    )
)
```

### NgrokTunnelConfig Fields

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `domain` | `str` | `None` | Custom ngrok domain (requires paid plan) |
| `basic_auth` | `List[str]` | `None` | Basic auth credentials (format: `["user:pass"]`) |
| `compression` | `bool` | `False` | Enable gzip compression |
| `bind_tls` | `bool` | `True` | Force HTTPS connections |
| `inspect` | `bool` | `True` | Enable ngrok web interface |

---

## Environment Variables

### Set by Django-CFG

When you run `python manage.py runserver_ngrok`, Django-CFG automatically sets these environment variables:

| Variable | Example | Description |
|----------|---------|-------------|
| `NGROK_URL` | `https://abc123.ngrok.io` | Full tunnel URL |
| `NGROK_HOST` | `abc123.ngrok.io` | Tunnel hostname |
| `NGROK_SCHEME` | `https` | Protocol scheme |

**Usage in code:**

```python
import os

# Get tunnel URL
ngrok_url = os.environ.get('NGROK_URL')  # "https://abc123.ngrok.io"

# Build webhook URL
webhook_url = f"{ngrok_url}/api/webhooks/stripe/"
```

### Required Environment Variables

For advanced ngrok features:

```bash
# Ngrok auth token (optional, for paid features)
export NGROK_AUTHTOKEN="your_ngrok_token"
```

---

## Configuration Examples

### Example 1: Development Only

```python
from django_cfg import DjangoConfig, NgrokConfig
from .environment import env

class MyConfig(DjangoConfig):
    # Ngrok only in development
    ngrok: NgrokConfig = NgrokConfig(
        enabled=(env.environment == "development"),
        webhook_path="/api/webhooks/"
    )
```

### Example 2: With Custom Domain

```python
from django_cfg import NgrokConfig, NgrokAuthConfig, NgrokTunnelConfig

ngrok: NgrokConfig = NgrokConfig(
    enabled=True,

    auth=NgrokAuthConfig(
        authtoken_from_env=True  # Load from NGROK_AUTHTOKEN
    ),

    tunnel=NgrokTunnelConfig(
        domain="myapp.ngrok.io",  # Custom domain
        compression=True
    )
)
```

### Example 3: With Password Protection

```python
ngrok: NgrokConfig = NgrokConfig(
    enabled=True,

    tunnel=NgrokTunnelConfig(
        # Protect tunnel with basic auth
        basic_auth=["admin:supersecret"],
        bind_tls=True  # Force HTTPS
    )
)
```

### Example 4: Environment-Specific

```python
from .environment import env

class MyConfig(DjangoConfig):
    # Different settings per environment
    ngrok: NgrokConfig = NgrokConfig(
        enabled=(env.environment == "development"),
        webhook_path=(
            "/webhooks/"  # Development
            if env.environment == "development"
            else None  # Production
        )
    )

    # Use ngrok URL in dev, real URL in prod
    api_url: str = (
        "https://api.myapp.com"
        if env.environment == "production"
        else "http://localhost:8000"
    )
```

---

## Configuration Best Practices

### 1. Use Environment Variables

```python
# ✅ CORRECT - load from environment
ngrok: NgrokConfig = NgrokConfig(
    enabled=True,
    auth=NgrokAuthConfig(
        authtoken_from_env=True  # From NGROK_AUTHTOKEN
    )
)

# ❌ WRONG - hardcode token
ngrok: NgrokConfig = NgrokConfig(
    enabled=True,
    auth=NgrokAuthConfig(
        authtoken="hardcoded-token"  # Security risk!
    )
)
```

### 2. Development Only

```python
# ✅ CORRECT - automatically disabled in production
ngrok: NgrokConfig = NgrokConfig(
    enabled=True  # Only works when DEBUG=True
)

# Even better - explicit environment check
from .environment import env

ngrok: NgrokConfig = NgrokConfig(
    enabled=(env.environment == "development")
)
```

### 3. Type-Safe Configuration

```python
# ✅ CORRECT - use Pydantic models
from django_cfg import NgrokConfig

ngrok: NgrokConfig = NgrokConfig(
    enabled=True,
    webhook_path="/api/webhooks/"  # Type-checked!
)

# ❌ WRONG - raw Django settings
# NGROK_ENABLED = True
# NGROK_WEBHOOK_PATH = "/api/webhooks/"  # No validation!
```

---

## Validations

Django-CFG automatically validates your ngrok configuration:

```python
# ❌ This will raise ValidationError
ngrok: NgrokConfig = NgrokConfig(
    enabled=True,
    tunnel=NgrokTunnelConfig(
        domain="invalid domain with spaces"  # ValidationError!
    )
)

# ✅ Correct configuration
ngrok: NgrokConfig = NgrokConfig(
    enabled=True,
    tunnel=NgrokTunnelConfig(
        domain="myapp.ngrok.io"  # Valid!
    )
)
```

---

## Next Steps

- **[Implementation](./implementation)** - Learn how to get tunnel URLs in code
- **[Webhook Examples](./webhook-examples)** - See practical webhook integration examples
- **[Payments Panel](./payments-panel)** - Use built-in webhook admin panel
- **[Troubleshooting](./troubleshooting)** - Common configuration issues

## See Also

### Ngrok Integration

**Core Documentation:**
- [**Ngrok Overview**](./overview) - Ngrok integration introduction
- [**Implementation Guide**](./implementation) - Getting tunnel URLs in code
- [**Webhook Examples**](./webhook-examples) - Real-world webhook integrations
- [**Payments Panel**](./payments-panel) - Built-in webhook admin panel
- [**Troubleshooting**](./troubleshooting) - Common configuration issues

### Configuration & Setup

**Configuration:**
- [**Configuration Models**](/fundamentals/configuration) - Complete DjangoConfig reference
- [**Type-Safe Configuration**](/fundamentals/core/type-safety) - Pydantic validation
- [**Environment Variables**](/fundamentals/configuration/environment) - Ngrok auth token and secrets
- [**Environment Detection**](/fundamentals/configuration/environment) - Dev-only ngrok

**Getting Started:**
- [**Installation**](/getting-started/installation) - Install Django-CFG with ngrok
- [**Configuration Guide**](/getting-started/configuration) - YAML configuration setup
- [**First Project**](/getting-started/first-project) - Quick start tutorial

### Payment & Webhook Features

**Payment Integration:**
- [**Payments App**](/features/built-in-apps/payments/overview) - Payment webhook processing
- [**Payments Configuration**](/features/built-in-apps/payments/configuration) - Payment setup
- [**Payment Examples**](/features/built-in-apps/payments/examples) - Real payment flows

**Related Integrations:**
- [**ReArq Integration**](/features/integrations/rearq/overview) - Async webhooks
- [**Integrations Overview**](/features/integrations/overview) - All integrations

### Tools & Development

**CLI & Management:**
- [**CLI Tools**](/cli/introduction) - Ngrok CLI commands
- [**Development Commands**](/cli/commands/development) - runserver_ngrok
- [**Troubleshooting**](/guides/troubleshooting) - Debug issues

**Examples:**
- [**Sample Project**](/guides/sample-project/overview) - Production example
- [**Examples Guide**](/guides/examples) - More patterns
