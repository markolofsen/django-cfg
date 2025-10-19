---
title: Configuration Guide
description: Learn configuration in Django-CFG. Step-by-step guide to configuration guide with code examples, best practices, and production-ready configuration.
sidebar_label: Configuration
sidebar_position: 3
keywords:
  - django-cfg configuration
  - django configuration
---

import { TechArticleSchema } from '@site/src/components/Schema';
import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

<TechArticleSchema
  headline="Django-CFG Configuration Guide: Type-Safe YAML Configuration with Pydantic"
  description="Comprehensive guide to configuring Django-CFG with environment-specific YAML files and type-safe Pydantic models for production-ready Django applications"
  keywords={['django-cfg configuration', 'YAML configuration django', 'pydantic configuration', 'environment-specific django config', 'type-safe django settings']}
/>

# Configuration Guide

:::tip[Environment-Specific Configuration]
Django-CFG uses **environment-specific YAML files** with **type-safe Pydantic models** to provide clear separation between development, production, and test environments.
:::

## Configuration Flow

```mermaid
graph TB
    subgraph "1. Environment Detection"
        ENV{Environment<br/>Variable}
    end

    subgraph "2. YAML Loading"
        DEV[config.dev.yaml]
        PROD[config.prod.yaml]
        TEST[config.test.yaml]
    end

    subgraph "3. Type Validation"
        LOADER[Pydantic Loader]
        MODELS[Type-Safe Models<br/>DatabaseConfig, EmailConfig]
        VALIDATE[Validation]
    end

    subgraph "4. Django Integration"
        ENV_OBJ[env object]
        CONFIG[DjangoConfig]
        DJANGO[Django Settings]
    end

    ENV -->|IS_DEV=true| DEV
    ENV -->|IS_PROD=true| PROD
    ENV -->|IS_TEST=true| TEST
    ENV -->|default| DEV

    DEV --> LOADER
    PROD --> LOADER
    TEST --> LOADER

    LOADER --> MODELS
    MODELS --> VALIDATE
    VALIDATE --> ENV_OBJ
    ENV_OBJ --> CONFIG
    CONFIG --> DJANGO
```

## Overview

Django-CFG uses environment-specific YAML configuration files loaded through [Pydantic models](/fundamentals/core/type-safety). This provides type-safe configuration with clear separation between [development, production, and test environments](/fundamentals/configuration/environment).

**Key concepts:**
- ✅ YAML files per environment (config.dev.yaml, config.prod.yaml, config.test.yaml)
- ✅ [Type-safe loader](/fundamentals/core/type-safety) with Pydantic models
- ✅ Single import point via environment module
- ✅ No hardcoded secrets (see [Environment Variables](/fundamentals/configuration/environment))

:::warning[Security First]
Never commit secrets to version control. Always use environment variables or secrets managers for sensitive data in production.
:::

## Basic Setup

### 1. Create Environment Module

```
project/
├── config.py          # Main DjangoConfig class (see /fundamentals/configuration)
├── settings.py        # Django settings
└── environment/       # Environment configuration
    ├── __init__.py    # Exports `env` instance
    ├── loader.py      # YAML loader with Pydantic models
    ├── config.dev.yaml    # Development config
    ├── config.prod.yaml   # Production config (see /guides/production-config)
    └── config.test.yaml   # Test config
```

### 2. Create Pydantic Models (loader.py)

Based on real example from `libs/django_cfg_opensource/sample/django/api/environment/loader.py`:

```python
# environment/loader.py
import os
from pathlib import Path
from pydantic import BaseModel, Field, computed_field
from pydantic_yaml import parse_yaml_file_as

# Environment detection
IS_DEV = os.environ.get("IS_DEV", "").lower() in ("true", "1", "yes")
IS_PROD = os.environ.get("IS_PROD", "").lower() in ("true", "1", "yes")
IS_TEST = os.environ.get("IS_TEST", "").lower() in ("true", "1", "yes")

# Default to development
if not any([IS_DEV, IS_PROD, IS_TEST]):
    IS_DEV = True


class DatabaseConfig(BaseModel):
    """Database connection configuration (see /fundamentals/database for multi-DB setup)."""
    url: str = "sqlite:///db.sqlite3"
    url_blog: str = "sqlite:///blog.sqlite3"  # Example multi-DB
    url_shop: str = "sqlite:///shop.sqlite3"


class EmailConfig(BaseModel):
    """Email configuration (see /features/modules/email/overview for complete email setup)."""
    backend: str = "console"
    host: str = "localhost"
    port: int = 587
    username: str | None = None
    password: str | None = None
    use_tls: bool = True
    use_ssl: bool = False
    default_from: str = "noreply@example.com"


class TelegramConfig(BaseModel):
    """Telegram bot configuration."""
    bot_token: str = ""
    chat_id: int = 0


class ApiKeysConfig(BaseModel):
    """API keys configuration."""
    ngrok: str = ""
    openrouter: str = ""
    openai: str = ""


class AppConfig(BaseModel):
    """Application configuration."""
    name: str = "My Project"
    logo_url: str = ""
    domain: str = "localhost"
    api_url: str = "http://localhost:8000"
    site_url: str = "http://localhost:3000"
    ticket_url: str = "http://localhost:3000/support/ticket/{uuid}"
    otp_url: str = "http://localhost:3000/auth/otp/{code}"


class EnvironmentMode(BaseModel):
    """Environment mode detection."""
    is_test: bool = IS_TEST
    is_dev: bool = IS_DEV
    is_prod: bool = IS_PROD

    @computed_field
    @property
    def env_mode(self) -> str:
        """Get environment mode string."""
        if self.is_test:
            return "test"
        elif self.is_dev:
            return "development"
        elif self.is_prod:
            return "production"
        return "development"


class EnvironmentConfig(BaseModel):
    """Complete environment configuration."""

    # Core Django settings
    secret_key: str = "change-me-in-production"
    debug: bool = True

    # Configuration sections
    database: DatabaseConfig = Field(default_factory=DatabaseConfig)
    email: EmailConfig = Field(default_factory=EmailConfig)
    telegram: TelegramConfig = Field(default_factory=TelegramConfig)
    api_keys: ApiKeysConfig = Field(default_factory=ApiKeysConfig)
    app: AppConfig = Field(default_factory=AppConfig)
    env: EnvironmentMode = Field(default_factory=EnvironmentMode)

    # Security (optional)
    security_domains: list[str] | None = None  # Optional - not needed in dev mode


def get_environment_config() -> EnvironmentConfig:
    """Load environment configuration from YAML file."""

    # Determine which config file to load
    if IS_PROD:
        config_file = "config.prod.yaml"
    elif IS_TEST:
        config_file = "config.test.yaml"
    else:
        config_file = "config.dev.yaml"

    print(f"Loading config: {config_file}")

    # Get config file path
    config_path = Path(__file__).parent / config_file

    if config_path.exists():
        try:
            return parse_yaml_file_as(EnvironmentConfig, config_path)
        except Exception as e:
            print(f"Warning: Failed to load {config_file}: {e}")
            print("Using default configuration")
    else:
        print(f"Warning: {config_file} not found, using defaults")

    # Return default configuration
    return EnvironmentConfig()


# Global environment configuration instance
env = get_environment_config()
```

### 3. Export env Instance (__init__.py)

```python
# environment/__init__.py
from .loader import env

__all__ = ["env"]
```

### 4. Create YAML Configuration Files

<Tabs>
  <TabItem value="dev" label="Development" default>

```yaml title="environment/config.dev.yaml"
# === Core Django Settings ===
secret_key: "dev-secret-key-at-least-fifty-characters-long-for-django"
debug: true

# === Database ===
database:
  url: "sqlite:///db/default.sqlite3"
  url_blog: "sqlite:///db/blog.sqlite3"
  url_shop: "sqlite:///db/shop.sqlite3"

# === Application ===
app:
  name: "My Project"
  logo_url: "https://example.com/logo.png"
  domain: "localhost"
  api_url: "http://localhost:8000"
  site_url: "http://localhost:3000"

# === Security Domains ===
# Optional in development - Django-CFG auto-configures for dev convenience:
# - CORS fully open
# - Docker IPs work automatically
# - localhost any port
# Uncomment only if you need to test production security configuration
# security_domains:
#   - "staging.example.com"

# === Email ===
email:
  backend: "console"  # Console output for development
  host: "localhost"
  port: 587
  use_tls: true
  default_from: "My Project <noreply@localhost.dev>"

# === Telegram ===
telegram:
  bot_token: ""
  chat_id: 0

# === API Keys ===
api_keys:
  ngrok: ""
  openrouter: ""
  openai: ""
```

:::info[Development Setup]
Development configuration uses:
- **SQLite** databases for simplicity
- **Console** email backend (emails print to console)
- **No SSL** redirect for local development
- **Localhost** domains for CORS
:::

  </TabItem>
  <TabItem value="prod" label="Production">

```yaml title="environment/config.prod.yaml"
secret_key: "${SECRET_KEY}"  # Load from environment variable
debug: false

database:
  url: "${DATABASE_URL}"  # PostgreSQL from environment

app:
  name: "My Project"
  domain: "myapp.com"
  api_url: "https://api.myapp.com"
  site_url: "https://myapp.com"

# === Security Domains ===
# REQUIRED in production! Django-CFG auto-normalizes any format
security_domains:
  - "myapp.com"              # ✅ No protocol
  - "https://api.myapp.com"  # ✅ With protocol
  - "admin.myapp.com:8443"   # ✅ With port

email:
  backend: "smtp"
  host: "smtp.sendgrid.net"
  port: 587
  username: "apikey"
  password: "${SENDGRID_API_KEY}"  # From environment
  use_tls: true
  default_from: "My Project <noreply@myapp.com>"

telegram:
  bot_token: "${TELEGRAM_BOT_TOKEN}"  # From environment
  chat_id: "${TELEGRAM_CHAT_ID}"

api_keys:
  openrouter: "${OPENROUTER_API_KEY}"
  openai: "${OPENAI_API_KEY}"
```

:::danger[Production Secrets]
**Critical:** Production configuration must use environment variables for all secrets:
- `${SECRET_KEY}` - Django secret key
- `${DATABASE_URL}` - Database connection string
- `${SENDGRID_API_KEY}` - Email service credentials
- `${TELEGRAM_BOT_TOKEN}` - Bot credentials

Never commit actual secret values to version control!
:::

  </TabItem>
  <TabItem value="test" label="Test">

```yaml title="environment/config.test.yaml"
secret_key: "test-secret-key-for-automated-testing-only"
debug: false  # Test with production settings

database:
  url: "sqlite:///:memory:"  # In-memory database
  url_blog: "sqlite:///:memory:"
  url_shop: "sqlite:///:memory:"

app:
  name: "My Project (Test)"
  domain: "testserver"
  api_url: "http://testserver"
  site_url: "http://testserver"

security_domains:
  - "testserver"

email:
  backend: "console"  # Don't send real emails in tests

telegram:
  bot_token: "test-token"
  chat_id: 0

api_keys:
  ngrok: ""
  openrouter: ""
  openai: ""
```

:::note[Testing Configuration]
Test configuration optimizes for speed:
- **In-memory SQLite** databases
- **Console** email backend
- **Minimal** external dependencies
- **Fast** setup and teardown
:::

  </TabItem>
</Tabs>

### 5. Use in config.py

Based on real example from `libs/django_cfg_opensource/sample/django/api/config.py`:

```python
# config.py
from typing import Dict
from django_cfg import DjangoConfig, DatabaseConfig, EmailConfig, TelegramConfig

# Import environment configuration
from .environment import env


class MyProjectConfig(DjangoConfig):
    """Project configuration using YAML-loaded environment."""

    # Core settings from YAML
    secret_key: str = env.secret_key
    debug: bool = env.debug
    env_mode: str = env.env.env_mode

    # Project info
    project_name: str = env.app.name
    project_logo: str = env.app.logo_url

    # URLs from YAML
    site_url: str = env.app.site_url
    api_url: str = env.app.api_url
    ticket_url: str = env.app.ticket_url
    otp_url: str = env.app.otp_url

    # Security domains from YAML (optional in dev, required in prod)
    security_domains: list[str] = env.security_domains or []

    # Database from YAML URL
    databases: Dict[str, DatabaseConfig] = {
        "default": DatabaseConfig.from_url(url=env.database.url),
        "blog": DatabaseConfig.from_url(
            url=env.database.url_blog,
            apps=["apps.blog"],
            operations=["read", "write", "migrate"],
        ),
    }

    # Email from YAML
    email: EmailConfig | None = (
        EmailConfig(
            host=env.email.host,
            port=env.email.port,
            use_tls=env.email.use_tls,
            username=env.email.username,
            password=env.email.password,
            default_from=env.email.default_from,
        )
        if env.email.host
        else None
    )

    # Telegram from YAML
    telegram: TelegramConfig | None = (
        TelegramConfig(
            bot_token=env.telegram.bot_token,
            chat_id=env.telegram.chat_id,
        )
        if env.telegram.bot_token and env.telegram.chat_id
        else None
    )


# Create configuration instance
config = MyProjectConfig()
```

## Environment Detection

:::info[Automatic Detection]
Django-CFG automatically detects the environment based on `IS_DEV`, `IS_PROD`, and `IS_TEST` environment variables. Defaults to development if none are set.
:::

<Tabs groupId="environment">
  <TabItem value="dev" label="Development" default>

```bash title="Development Mode"
# Development (default - no flag needed)
python manage.py runserver

# Or explicitly:
IS_DEV=true python manage.py runserver

# Docker Compose
docker-compose up
```

Loads: `config.dev.yaml`

  </TabItem>
  <TabItem value="prod" label="Production">

```bash title="Production Mode"
# Set production flag
export IS_PROD=true
python manage.py runserver

# Or inline:
IS_PROD=true gunicorn myproject.wsgi:application

# Docker production
docker run -e IS_PROD=true myapp:latest
```

Loads: `config.prod.yaml`

:::warning[Production Checklist]
Before deploying to production:
- ✅ Set `IS_PROD=true`
- ✅ Configure all environment variables (`SECRET_KEY`, `DATABASE_URL`, etc.)
- ✅ Verify `debug: false` in config.prod.yaml
- ✅ Set up reverse proxy (nginx/Cloudflare) for SSL/TLS
- ✅ Configure `security_domains` with production domains
:::

  </TabItem>
  <TabItem value="test" label="Test">

```bash title="Test Mode"
# Run tests
IS_TEST=true python manage.py test

# With pytest
IS_TEST=true pytest

# CI/CD environment
export IS_TEST=true
pytest --cov=myapp
```

Loads: `config.test.yaml`

:::tip[CI/CD Integration]
Most CI/CD systems automatically set test environment variables. Django-CFG works seamlessly with GitHub Actions, GitLab CI, CircleCI, etc.
:::

  </TabItem>
</Tabs>

## DatabaseConfig.from_url()

Django-CFG provides `from_url()` class method to create database configurations from URLs:

```python
from django_cfg import DatabaseConfig

# Basic usage
db = DatabaseConfig.from_url(url="postgresql://user:pass@localhost/mydb")

# With routing
db = DatabaseConfig.from_url(
    url="postgresql://user:pass@localhost/analytics",
    apps=["analytics", "reports"],
    operations=["read", "write", "migrate"],
    routing_description="Analytics database",
)
```

**Supported URL schemes:**
- `postgresql://` - PostgreSQL
- `mysql://` - MySQL
- `sqlite:///` - SQLite (use 3 slashes)
- Other Django-supported backends

## Best Practices

:::tip[Configuration Best Practices]
Follow these patterns to ensure secure, maintainable configuration across all environments.
:::

<details>
  <summary>1. Never Commit Secrets</summary>

**❌ Wrong - Hardcoded secrets:**
```yaml title="config.prod.yaml (INSECURE)"
secret_key: "actual-secret-key-abc123"  # ❌ NEVER DO THIS
database:
  url: "postgresql://user:realpassword@db.com/prod"  # ❌ EXPOSED
```

**✅ Correct - Environment variables:**
```yaml title="config.prod.yaml (SECURE)"
secret_key: "${SECRET_KEY}"  # ✅ Load from environment
database:
  url: "${DATABASE_URL}"  # ✅ Secure
```

:::danger[Secret Exposure Risk]
Secrets committed to git can be:
- Leaked through GitHub/GitLab search
- Found in git history (even after deletion)
- Exposed in forks and mirrors
- Accessed by anyone with repository access
:::

</details>

<details>
  <summary>2. Use .gitignore Properly</summary>

```bash title=".gitignore"
# Ignore all environment configs except examples
environment/config.*.yaml
!environment/config.dev.example.yaml
!environment/config.test.example.yaml

# Never commit secrets
.env
.env.local
secrets/
```

**Recommended structure:**
- ✅ Commit `config.dev.example.yaml` as template
- ✅ Commit `config.test.example.yaml` for CI/CD
- ❌ Never commit `config.prod.yaml`
- ❌ Never commit `.env` files with real secrets

</details>

<details>
  <summary>3. Validate Configuration Early</summary>

```bash title="Validation Commands"
# Validate Pydantic models and YAML syntax
python manage.py check

# Show loaded configuration (masks secrets)
python manage.py show_config

# Validate Django settings
python manage.py check_settings
```

:::info[Fail-Fast Validation]
Pydantic validates configuration at startup, catching errors **before** they reach production. Invalid YAML or missing required fields cause immediate failures.
:::

</details>

<details>
  <summary>4. Environment-Specific Defaults</summary>

```python title="loader.py"
# Smart defaults based on environment
class EmailConfig(BaseModel):
    backend: str = "console" if IS_DEV else "smtp"
    port: int = 587
    use_tls: bool = not IS_DEV  # TLS in production only

class DatabaseConfig(BaseModel):
    url: str = "sqlite:///:memory:" if IS_TEST else "sqlite:///db.sqlite3"
    pool_size: int = 5 if IS_DEV else 20
```

**Benefits:**
- Minimal YAML configuration needed
- Sensible defaults per environment
- Type-safe with Pydantic validation

</details>

## Integration with Django

### Using in settings.py

```python
# settings.py
from config import config

# Import all Django settings
globals().update(config.get_all_settings())

# Optionally add custom settings
STATIC_URL = '/static/'
MEDIA_URL = '/media/'
```

### Management Commands

```bash
# Validate configuration
python manage.py validate_config

# Show current configuration (from loaded YAML)
python manage.py show_config

# Check Django settings
python manage.py check_settings
```

## Troubleshooting

### YAML File Not Found

```
Warning: config.prod.yaml not found, using defaults
```

**Solution:** Ensure YAML file exists in environment/ directory and environment variable is set correctly.

### Pydantic Validation Error

```
pydantic_core.ValidationError: 1 validation error for EnvironmentConfig
secret_key
  Field required [type=missing, input_value={...}, input_type=dict]
```

**Solution:** Add missing field to YAML file or provide default in loader.py model.

### Database URL Parse Error

```
ValueError: Invalid database URL format
```

**Solution:** Check URL format matches `scheme://user:pass@host:port/database`.

Valid examples:
- `postgresql://postgres:password@localhost:5432/mydb`
- `mysql://root:password@127.0.0.1:3306/mydb`
- `sqlite:///path/to/db.sqlite3` (3 slashes!)

## Next Steps

- [Multi-Database Setup](/guides/multi-database) - Advanced database routing
- [Production Deployment](/guides/docker/overview) - Production configuration
- [Environment Management](/fundamentals/configuration/environment) - Environment detection

TAGS: configuration, yaml, pydantic, environment, django-cfg
DEPENDS_ON: [installation, intro]
USED_BY: [first-project, multi-database]
