---
title: Environment Configuration
description: Modern environment configuration with pydantic-settings. Type-safe, simple, and production-ready.
sidebar_label: Environment
sidebar_position: 3
keywords:
  - django environment variables
  - django-cfg env
  - django .env configuration
  - pydantic environment settings
  - pydantic-settings
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# 🌍 Environment Configuration

## Overview

Django-CFG uses **pydantic-settings** for modern, type-safe environment configuration. Configuration is loaded from environment variables and `.env` files automatically.

:::info[Simple & Clean]
No YAML files, no complex loaders. Just **ENV variables**, **.env files**, and **defaults in code**.
:::

## Configuration Priority

```mermaid
graph LR
    A[System ENV Variables] -->|Highest| D[Final Config]
    B[.env File] -->|Medium| D
    C[Code Defaults] -->|Lowest| D

    style A fill:#e1f5e1
    style B fill:#fff4e1
    style C fill:#f0f0f0
```

**Priority order (highest to lowest):**
1. 🥇 **System environment variables** (Docker, K8s, CI/CD)
2. 🥈 **.env file** (local development)
3. 🥉 **Default values in code** (fallback)

---

## Environment Detection

### Setting Environment Mode

Set **ONE** of these environment variables:

```bash
# Development (default if nothing set)
IS_DEV=true

# Production
IS_PROD=true

# Testing (auto-detected from pytest)
IS_TEST=true
```

:::tip[Auto-detection]
If no environment variable is set, **development mode** is used by default.
:::

### Environment Mode API

<Tabs groupId="env-usage">
  <TabItem value="basic" label="Basic Usage" default>

```python
from api.environment import env

# Check environment mode
if env.env.is_prod:
    print("Running in production!")

if env.env.is_dev:
    print("Running in development!")

if env.env.is_test:
    print("Running tests!")

# Get environment name
print(env.env.env_mode)  # "development", "production", or "test"
```

  </TabItem>
  <TabItem value="settings" label="In Django Settings">

```python
from api.environment import env

# Use in settings.py
DEBUG = env.debug if env.env.is_dev else False

ALLOWED_HOSTS = ['*'] if env.env.is_dev else env.security_domains

# Different database per environment
DATABASES = {
    "default": DatabaseConfig.from_url(
        url=env.database.url
    ).to_django_dict()
}
```

  </TabItem>
</Tabs>

---

## Configuration Structure

### Environment Loader

```python
# api/environment/loader.py

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

class DatabaseConfig(BaseSettings):
    """Database configuration"""

    url: str = Field(
        default="sqlite:///db/default.sqlite3",
        description="Database connection URL"
    )

    model_config = SettingsConfigDict(
        env_prefix="DATABASE__",
        env_nested_delimiter="__",
    )

class EmailConfig(BaseSettings):
    """Email configuration"""

    backend: str = Field(default="console")
    host: str = Field(default="localhost")
    port: int = Field(default=587)
    username: str | None = Field(default=None)
    password: str | None = Field(default=None)
    use_tls: bool = Field(default=True)

    model_config = SettingsConfigDict(
        env_prefix="EMAIL__",
        env_nested_delimiter="__",
    )

class EnvironmentConfig(BaseSettings):
    """Complete environment configuration"""

    # Core Django settings
    secret_key: str = Field(
        default="django-cfg-dev-key-change-in-production-min-50-chars"
    )
    debug: bool = Field(default=True)

    # Nested configs
    database: DatabaseConfig = Field(default_factory=DatabaseConfig)
    email: EmailConfig = Field(default_factory=EmailConfig)

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_nested_delimiter="__",
        case_sensitive=False,
        extra="ignore",
    )

# Global instance
env = EnvironmentConfig()
```

---

## Using Environment Variables

### ENV Variable Notation

Use **double underscore (`__`)** to access nested configurations:

```bash
# Flat config
DEBUG=true
SECRET_KEY="my-secret-key-min-50-chars-for-production-use"

# Nested config: email.host
EMAIL__HOST=smtp.gmail.com
EMAIL__PORT=587
EMAIL__USE_TLS=true

# Nested config: database.url
DATABASE__URL=postgresql://user:pass@localhost:5432/mydb

# Nested config: api_keys.openai
API_KEYS__OPENAI=sk-proj-xxx
```

### .env File Example

```bash title="api/environment/.env"
# === Environment Mode ===
IS_DEV=true

# === Core Django Settings ===
SECRET_KEY="your-secret-key-minimum-50-characters-long"
DEBUG=true

# === Database ===
DATABASE__URL="postgresql://postgres:postgres@localhost:5432/djangocfg"

# === Email Configuration ===
EMAIL__BACKEND="smtp"
EMAIL__HOST="smtp.gmail.com"
EMAIL__PORT=587
EMAIL__USERNAME="your-email@example.com"
EMAIL__PASSWORD="your-password"
EMAIL__USE_TLS=true

# === Cache ===
REDIS_URL="redis://localhost:6379/0"

# === API Keys ===
API_KEYS__OPENROUTER="sk-or-xxx"
API_KEYS__OPENAI="sk-proj-xxx"
```

---

## Environment-Specific Defaults

You can set different defaults in code based on environment:

<Tabs groupId="env-defaults">
  <TabItem value="database" label="Database" default>

```python
class DatabaseConfig(BaseSettings):
    url: str = Field(
        # SQLite for dev, override for prod
        default="sqlite:///db/default.sqlite3"
    )

    model_config = SettingsConfigDict(
        env_prefix="DATABASE__",
        env_nested_delimiter="__",
    )
```

**Production override:**
```bash
DATABASE__URL="postgresql://prod-user:pass@db.example.com:5432/prod_db"
```

  </TabItem>
  <TabItem value="email" label="Email">

```python
class EmailConfig(BaseSettings):
    backend: str = Field(
        # Console backend for dev (prints to terminal)
        default="console"
    )

    model_config = SettingsConfigDict(
        env_prefix="EMAIL__",
        env_nested_delimiter="__",
    )
```

**Production override:**
```bash
EMAIL__BACKEND="smtp"
EMAIL__HOST="smtp.sendgrid.net"
```

  </TabItem>
  <TabItem value="security" label="Security">

```python
class EnvironmentConfig(BaseSettings):
    secret_key: str = Field(
        # Dev key (never use in production!)
        default="django-cfg-dev-key-change-in-production-min-50-chars"
    )
    debug: bool = Field(default=True)
```

**Production override:**
```bash
SECRET_KEY="prod-secret-key-from-secrets-manager-min-50-chars"
DEBUG=false
```

  </TabItem>
</Tabs>

---

## Docker & Production

### Docker Compose

```yaml title="docker-compose.yml"
services:
  django:
    environment:
      # Environment mode
      IS_PROD: "true"

      # Core settings
      DEBUG: "false"
      SECRET_KEY: "${SECRET_KEY}"

      # Database
      DATABASE__URL: "postgresql://user:pass@postgres:5432/db"

      # Cache
      REDIS_URL: "redis://redis:6379/0"

      # Email
      EMAIL__BACKEND: "smtp"
      EMAIL__HOST: "smtp.example.com"
```

### Kubernetes ConfigMap

```yaml title="k8s-configmap.yaml"
apiVersion: v1
kind: ConfigMap
metadata:
  name: django-config
data:
  IS_PROD: "true"
  DEBUG: "false"
  DATABASE__URL: "postgresql://user:pass@postgres:5432/db"
  REDIS_URL: "redis://redis:6379/0"
```

### Secrets Management

:::warning[Never commit secrets]
Use **environment variables** or **secrets managers** for sensitive data:
- Kubernetes Secrets
- AWS Secrets Manager
- HashiCorp Vault
- .env file (add to .gitignore!)
:::

```python
# api/environment/.env (gitignored!)
SECRET_KEY="prod-key-from-secrets-manager"
DATABASE__URL="postgresql://user:pass@prod-db.aws.com:5432/db"
EMAIL__PASSWORD="email-password-from-vault"
API_KEYS__OPENAI="sk-proj-xxx-from-secrets"
```

---

## Validation

Pydantic validates types automatically:

```python
# ✅ Valid
EMAIL__PORT=587  # Converted to int

# ❌ Invalid - raises ValidationError
EMAIL__PORT=abc  # Not a number!

# ✅ Valid
DEBUG=true       # Converted to bool

# ❌ Invalid
SECRET_KEY="short"  # Less than 50 chars
```

### Custom Validators

```python
from pydantic import field_validator

class EnvironmentConfig(BaseSettings):
    secret_key: str

    @field_validator("secret_key")
    def validate_secret_key(cls, v):
        if len(v) < 50:
            raise ValueError("SECRET_KEY must be at least 50 characters")
        if "django-insecure" in v:
            raise ValueError("Insecure secret key detected!")
        return v
```

---

## Migration from YAML

:::info[Migrating from old YAML configs?]
Old approach used `config.dev.yaml`, `config.prod.yaml`, etc.

**New approach:** Everything via ENV variables!
:::

### Before (YAML)

```yaml title="config.prod.yaml"
secret_key: "my-secret-key"
debug: false
database:
  url: "postgresql://user:pass@localhost:5432/db"
email:
  backend: "smtp"
  host: "smtp.example.com"
```

### After (ENV)

```bash title=".env"
SECRET_KEY="my-secret-key"
DEBUG=false
DATABASE__URL="postgresql://user:pass@localhost:5432/db"
EMAIL__BACKEND="smtp"
EMAIL__HOST="smtp.example.com"
```

**Benefits:**
- ✅ Simpler - one configuration method
- ✅ 12-factor app compliant
- ✅ Works everywhere (Docker, K8s, CI/CD)
- ✅ No file management overhead

---

## Best Practices

### 1. Use .env for Local Development

```bash
# api/environment/.env (gitignored)
IS_DEV=true
DATABASE__URL="postgresql://localhost:5432/dev_db"
DEBUG=true
```

### 2. Use System ENV for Production

```bash
# Set in Docker/K8s/CI
export IS_PROD=true
export SECRET_KEY="prod-secret-from-vault"
export DATABASE__URL="postgresql://prod-db:5432/db"
```

### 3. Keep Defaults Safe

```python
# Good defaults for development
class EnvironmentConfig(BaseSettings):
    debug: bool = Field(default=True)
    database: DatabaseConfig = Field(
        default_factory=lambda: DatabaseConfig(
            url="sqlite:///db/dev.sqlite3"
        )
    )
```

### 4. Validate in Production

```python
from api.environment import env

# Validate critical settings
if env.env.is_prod:
    assert len(env.secret_key) >= 50, "Production secret key too short!"
    assert not env.debug, "DEBUG must be False in production!"
    assert "sqlite" not in env.database.url.lower(), "Use PostgreSQL in production!"
```

---

## Troubleshooting

### Environment not detected correctly

```python
from api.environment import env

# Check what was detected
print(f"Environment: {env.env.env_mode}")
print(f"IS_DEV: {env.env.is_dev}")
print(f"IS_PROD: {env.env.is_prod}")
print(f"IS_TEST: {env.env.is_test}")
```

### ENV variables not loading

1. Check `.env` file location (should be in `api/environment/`)
2. Verify variable naming (use `__` for nesting)
3. Check for typos (case-insensitive but must match structure)

### Type conversion errors

```python
# Wrong
EMAIL__PORT=abc  # ❌ Not a number

# Correct
EMAIL__PORT=587  # ✅ Valid integer
```

---

## Related

- [Database Configuration](/fundamentals/configuration/database)
- [Email Configuration](/fundamentals/configuration/email)
- [Docker Configuration](/guides/docker/configuration)
- [Production Deployment](/deployment/overview)
