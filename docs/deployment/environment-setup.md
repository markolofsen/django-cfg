---
title: Environment Setup
description: Environment configuration principles for Django-CFG using pydantic-settings and environment variables.
sidebar_label: Environment Setup
sidebar_position: 1
keywords:
  - django-cfg environment
  - environment configuration
  - pydantic-settings
  - environment variables
---

# 🌍 Environment Setup

Django-CFG uses **pydantic-settings** for type-safe environment configuration. Configuration is loaded from environment variables and `.env` files automatically.

---

## Core Principles

### Single Configuration Method
Environment variables for all environments:

```
Development → .env file (gitignored)
Production  → System ENV (Docker, K8s, CI/CD)
Testing     → Defaults + minimal ENV overrides
```

### Priority System

Configuration loading follows this priority (highest wins):

```
1. System environment variables (highest priority)
2. .env file values
3. Default values in code (lowest priority)
```

### Environment Detection

Automatic detection based on environment variables:

```bash
# Development (default if nothing set)
IS_DEV=true

# Production
IS_PROD=true

# Testing
IS_TEST=true
```

---

## Configuration Structure

### Development Config (.env)

```bash title="api/environment/.env"
# === Environment Mode ===
IS_DEV=true

# === Core Settings ===
SECRET_KEY="dev-secret-key-at-least-50-chars-change-in-production"
DEBUG=true

# === Database ===
DATABASE__URL="postgresql://postgres:postgres@localhost:5432/djangocfg"

# === Application URLs ===
APP__NAME="My App"
APP__DOMAIN="localhost"
APP__API_URL="http://localhost:8000"
APP__SITE_URL="http://localhost:3000"

# === Email ===
EMAIL__BACKEND="console"  # Prints to console
EMAIL__DEFAULT_FROM="My App <noreply@localhost.dev>"

# === Cache ===
REDIS_URL="redis://localhost:6379/0"

# === API Keys (optional) ===
# API_KEYS__OPENAI=""
# API_KEYS__SENDGRID=""
```

**Development benefits:**
- ✅ **Console email backend** (no SMTP setup needed)
- ✅ **Local database** (PostgreSQL or SQLite)
- ✅ **Gitignored** - safe for local secrets
- ✅ **Quick setup** - copy `.env.example`

### Production Config (System ENV)

```bash title="Production Environment Variables"
# Set in Docker/K8s - NEVER in .env file!

# === Environment Mode ===
IS_PROD=true

# === Core Settings ===
SECRET_KEY="production-secret-from-secrets-manager-min-50-chars"
DEBUG=false

# === Database ===
DATABASE__URL="postgresql://prod_user:prod_pass@db.example.com:5432/prod_db"

# === Application URLs ===
APP__NAME="My App"
APP__DOMAIN="example.com"
APP__API_URL="https://api.example.com"
APP__SITE_URL="https://example.com"

# === Security Domains ===
# REQUIRED in production!
SECURITY_DOMAINS="example.com,api.example.com,www.example.com"

# === Email ===
EMAIL__BACKEND="smtp"
EMAIL__HOST="smtp.sendgrid.net"
EMAIL__PORT=587
EMAIL__USERNAME="apikey"
EMAIL__PASSWORD="${SENDGRID_API_KEY}"
EMAIL__USE_TLS=true
EMAIL__DEFAULT_FROM="My App <noreply@example.com>"

# === Cache ===
REDIS_URL="redis://redis:6379/1"

# === API Keys ===
API_KEYS__OPENAI="${OPENAI_API_KEY}"
API_KEYS__SENDGRID="${SENDGRID_API_KEY}"
```

**Production practices:**
- ✅ Use **secrets managers** (AWS Secrets Manager, Vault)
- ✅ Set in **Docker environment** or **K8s Secrets**
- ✅ **Never commit** to version control
- ✅ **Rotate secrets** regularly

### Test Config

```bash title="Test Environment (pytest.ini or CI)"
# === Environment Mode ===
IS_TEST=true

# === Core Settings ===
SECRET_KEY="test-key-for-testing-only-min-50-chars-long"
DEBUG=false

# === Database (in-memory for speed) ===
DATABASE__URL="sqlite:///:memory:"

# === Email (don't send real emails) ===
EMAIL__BACKEND="console"

# === Disable external services ===
API_KEYS__OPENAI=""
REDIS_URL=""
```

**Testing optimizations:**
- ✅ **In-memory SQLite** for fast tests
- ✅ **Console email backend**
- ✅ **Disabled** external services
- ✅ **Minimal** logging

---

## Environment Variables

### Standard Variables

Django-CFG supports standard environment variables:

```bash
# Core
SECRET_KEY="your-secret-key-here"
DEBUG=true
DATABASE__URL="postgresql://user:pass@host:5432/db"
REDIS_URL="redis://localhost:6379/0"

# API Keys
API_KEYS__OPENAI="sk-..."
API_KEYS__SENDGRID="SG..."
```

### Nested Configuration

Use `__` (double underscore) for nested config:

```bash
# email.host
EMAIL__HOST="smtp.gmail.com"

# email.port
EMAIL__PORT=587

# api_keys.openai
API_KEYS__OPENAI="sk-..."

# app.domain
APP__DOMAIN="example.com"
```

**Pattern:** `SECTION__FIELD=value` maps to `section.field = value`

---

## Loading Configuration

### Automatic Loading with Pydantic

Django-CFG automatically loads configuration using pydantic-settings:

```python
# api/environment/loader.py
from pathlib import Path
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class DatabaseConfig(BaseSettings):
    """Database configuration."""
    url: str = Field(default="sqlite:///db/default.sqlite3")

    model_config = SettingsConfigDict(
        env_prefix="DATABASE__",
        env_nested_delimiter="__",
    )


class EmailConfig(BaseSettings):
    """Email configuration."""
    backend: str = Field(default="console")
    host: str = Field(default="localhost")
    port: int = Field(default=587)
    username: str | None = Field(default=None)
    password: str | None = Field(default=None)
    use_tls: bool = Field(default=True)
    default_from: str = Field(default="noreply@example.com")

    model_config = SettingsConfigDict(
        env_prefix="EMAIL__",
        env_nested_delimiter="__",
    )


class EnvironmentConfig(BaseSettings):
    """Complete environment configuration."""
    secret_key: str = Field(
        default="django-cfg-dev-key-change-in-production-min-50-chars"
    )
    debug: bool = Field(default=True)

    database: DatabaseConfig = Field(default_factory=DatabaseConfig)
    email: EmailConfig = Field(default_factory=EmailConfig)

    model_config = SettingsConfigDict(
        env_file=str(Path(__file__).parent / ".env"),
        env_file_encoding="utf-8",
        env_nested_delimiter="__",
        case_sensitive=False,
        extra="ignore",
    )


# Global instance - auto-loads from ENV > .env > defaults
env = EnvironmentConfig()
```

**How it works:**
1. Checks system environment variables (highest priority)
2. Loads `.env` file if exists
3. Uses defaults from Field definitions
4. Validates types automatically with Pydantic

### Using Configuration

```python
# api/config.py
from django_cfg import DjangoConfig, DatabaseConfig
from .environment import env


class MyDjangoConfig(DjangoConfig):
    project_name: str = env.app.name
    secret_key: str = env.secret_key
    debug: bool = env.debug
    security_domains: list[str] = env.security_domains or []

    # Database from environment
    databases = {
        "default": DatabaseConfig.from_url(url=env.database.url)
    }


# Generate Django settings
config = MyDjangoConfig()
```

---

## Environment-Specific Behavior

### Development

**Automatic configuration:**
- `security_domains: ["localhost", "127.0.0.1"]` → CORS open for local dev
- `email.backend: "console"` → Emails printed to console
- `debug: true` → Verbose logging, detailed errors
- Relaxed security settings

**Setup:**
```bash
# Copy .env.example to .env
cp api/environment/.env.example api/environment/.env

# Edit with your values
vim api/environment/.env

# Run development server
python manage.py runserver
```

### Production

**Automatic configuration:**
- `security_domains` → REQUIRED, strict CORS/CSRF
- `email.backend: "smtp"` → Real email sending
- `debug: false` → Structured logging, minimal output
- Strict security (HTTPS, HSTS, secure cookies)

**Setup:**
```bash
# Set environment variables in Docker/K8s
export IS_PROD=true
export SECRET_KEY="from-secrets-manager"
export DATABASE__URL="postgresql://..."

# Or in docker-compose.yml
services:
  django:
    environment:
      IS_PROD: "true"
      SECRET_KEY: "${SECRET_KEY}"
      DATABASE__URL: "${DATABASE_URL}"
```

### Docker

**Automatic features:**
- Service name resolution (postgres, redis)
- Health check endpoints enabled
- Private IP ranges allowed for internal calls
- Container-aware resource monitoring

**Docker Compose example:**
```yaml
# docker-compose.yml
version: '3.8'

services:
  django:
    build: .
    environment:
      # Environment mode
      IS_PROD: "true"

      # Core settings
      SECRET_KEY: "${SECRET_KEY}"
      DEBUG: "false"

      # Database (Docker service name)
      DATABASE__URL: "postgresql://postgres:postgres@postgres:5432/db"

      # Cache (Docker service name)
      REDIS_URL: "redis://redis:6379/0"

      # Email
      EMAIL__BACKEND: "smtp"
      EMAIL__HOST: "${EMAIL_HOST}"
      EMAIL__PORT: "587"
      EMAIL__USERNAME: "${EMAIL_USERNAME}"
      EMAIL__PASSWORD: "${EMAIL_PASSWORD}"

  postgres:
    image: postgres:16
    environment:
      POSTGRES_DB: db
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres

  redis:
    image: redis:7-alpine
```

---

## Best Practices

### 1. Never Commit Secrets

```bash
# .gitignore
.env
.env.*
environment/.env
secrets/
```

**Good:**
```bash
# In .env file (gitignored)
SECRET_KEY="my-secret-key"
DATABASE__URL="postgresql://..."
```

**Bad:**
```python
# Hardcoded in code - NEVER DO THIS!
SECRET_KEY = "hardcoded-secret-key"
DATABASE_URL = "postgresql://hardcoded-pass@..."
```

### 2. Use .env for Development Only

```bash
# Development (local)
.env file → gitignored, safe for local secrets

# Production
System ENV → Docker, K8s, CI/CD
Secrets Manager → AWS Secrets Manager, Vault

# Testing
Defaults → Minimal ENV overrides
```

### 3. Provide Defaults for Development

```python
# Good - has sensible defaults
class DatabaseConfig(BaseSettings):
    url: str = Field(
        default="sqlite:///db/default.sqlite3"  # Dev default
    )

# Override in production
DATABASE__URL="postgresql://prod-db:5432/db"
```

### 4. Validate in Production

```python
from api.environment import env

if env.env.is_prod:
    # Validate critical settings
    assert len(env.secret_key) >= 50, "Secret key too short!"
    assert not env.debug, "DEBUG must be False in production!"
    assert "postgresql" in env.database.url.lower(), "Use PostgreSQL in production!"
    assert env.security_domains, "SECURITY_DOMAINS required in production!"
```

### 5. Document Required Variables

```bash title=".env.example"
# === Required Environment Variables ===
# Production deployment requires:
# - SECRET_KEY: Django secret key (50+ chars)
# - DATABASE__URL: PostgreSQL connection string
# - REDIS_URL: Redis connection string
# - EMAIL__HOST: SMTP server hostname
# - EMAIL__PASSWORD: SMTP password
# - API_KEYS__OPENAI: OpenAI API key (if using AI features)

# === Core Settings ===
SECRET_KEY="your-secret-key-minimum-50-characters-long"
DEBUG=false

# === Database ===
DATABASE__URL="postgresql://user:pass@host:5432/db"
```

---

## Docker Deployment

For complete Docker deployment guide, see **[Docker Guide →](/guides/docker/overview)**

### Quick Reference

**Docker Compose with ENV:**
```yaml
version: '3.8'

services:
  django:
    build: .
    env_file:
      - .env.production  # Load from file
    environment:
      # Or set directly
      IS_PROD: "true"
      DATABASE__URL: "postgresql://postgres@db:5432/prod"
```

**Kubernetes with Secrets:**
```yaml
apiVersion: apps/v1
kind: Deployment
spec:
  template:
    spec:
      containers:
      - name: django
        env:
        - name: IS_PROD
          value: "true"
        - name: SECRET_KEY
          valueFrom:
            secretKeyRef:
              name: django-secrets
              key: secret-key
        - name: DATABASE__URL
          valueFrom:
            secretKeyRef:
              name: django-secrets
              key: database-url
```

---

## Troubleshooting

### Environment Variables Not Loading

**Check:**
```bash
# Verify .env file location
ls api/environment/.env

# Check environment variable
echo $DATABASE__URL

# Test in Python
python manage.py shell
>>> from api.environment import env
>>> print(env.database.url)
```

### Variable Format Errors

```bash
# ✅ Correct (double underscore)
EMAIL__HOST="smtp.gmail.com"

# ❌ Wrong (single underscore)
EMAIL_HOST="smtp.gmail.com"

# ✅ Correct (nested)
API_KEYS__OPENAI="sk-..."

# ❌ Wrong
API_KEYS_OPENAI="sk-..."
```

### Type Conversion Errors

```bash
# ✅ Correct
EMAIL__PORT=587  # Automatically converted to int
DEBUG=true       # Automatically converted to bool

# ❌ Wrong
EMAIL__PORT=abc  # Not a valid integer!
DEBUG=yes        # Use "true" or "false"
```

### Secret Key Error

```bash
# Generate secure key
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"

# Set in .env (development)
SECRET_KEY="generated-key-here-min-50-chars"

# Set in environment (production)
export SECRET_KEY="generated-key-here-min-50-chars"
```

---

## Migration from YAML

:::info[Migrating from YAML configs?]
Old approach used `config.dev.yaml`, `config.prod.yaml`, etc.

**New approach:** Everything via ENV variables!
:::

### Before (YAML)

```yaml title="config.prod.yaml"
secret_key: "${SECRET_KEY}"
debug: false
database:
  url: "${DATABASE_URL}"
email:
  backend: "smtp"
  host: "smtp.example.com"
```

### After (ENV)

```bash title="System ENV or .env"
SECRET_KEY="my-secret-key"
DEBUG=false
DATABASE__URL="postgresql://..."
EMAIL__BACKEND="smtp"
EMAIL__HOST="smtp.example.com"
```

**Benefits:**
- ✅ Simpler - one method for all environments
- ✅ 12-factor app compliant
- ✅ Works everywhere (Docker, K8s, CI/CD)
- ✅ No file management overhead

---

## See Also

- **[Docker Guide](/guides/docker/overview)** - Docker deployment
- **[Security Settings](/deployment/security)** - Security domains and CORS
- **[Monitoring](/deployment/monitoring)** - Health checks and logging
- **[Configuration Reference](/fundamentals/configuration/environment)** - Detailed ENV guide

---

TAGS: environment, configuration, pydantic-settings, env-vars, deployment
DEPENDS_ON: [django-cfg, pydantic-settings]
USED_BY: [deployment, docker, production]
