---
title: Docker Configuration Strategy
description: Master Django-CFG configuration in Docker with environment variables and pydantic-settings. Modern, simple, and production-ready.
sidebar_label: Configuration
sidebar_position: 3
keywords:
  - django-cfg docker configuration
  - docker environment variables
  - django docker secrets
  - __ notation configuration
  - pydantic-settings docker
---

# Docker Configuration Strategy

> **📚 Part of**: [Docker Guide](./overview) - Return to Docker overview

Learn Django-CFG's modern configuration approach: **environment variables** with **pydantic-settings** for type-safe, production-ready Docker deployments.

---

## Overview

Django-CFG uses **pydantic-settings** for automatic configuration loading from:
- **Environment variables** - Docker, K8s, CI/CD
- **.env files** - Local development only
- **Code defaults** - Fallback values

:::tip[Key Benefit]
The **universal `__` notation** allows you to configure ANY setting via environment variables, with automatic type conversion and validation. No YAML files, no rebuilds needed.
:::

---

## Configuration Priority

**Settings load in this order (highest priority first)**:

1. **System environment variables** - Docker Compose, K8s, etc.
2. **.env file** - Local development only (gitignored)
3. **Code defaults** - Pydantic Field definitions

```mermaid
graph LR
    A[Docker ENV<br/>EMAIL__HOST] --> B{Set?}
    B -->|Yes| E[Use Value]
    B -->|No| C[.env File]
    C --> D{Set?}
    D -->|Yes| E
    D -->|No| F[Code Default]
    F --> E

    style A fill:#e1f5e1
    style C fill:#fff4e1
    style F fill:#f0f0f0
```

---

## Universal `__` Notation

### How It Works

Any configuration value can be set using `SECTION__FIELD` format:

```bash
# Simple fields
EMAIL__HOST="mail.example.com"
EMAIL__PORT=465
EMAIL__PASSWORD="your-password-here"

# Nested sections
API_KEYS__OPENAI="sk-proj-your-key-here"
API_KEYS__CLOUDFLARE="your-cloudflare-key"

# Deep nesting
PAYMENTS_API_KEYS__NOWPAYMENTS_API_KEY="TV383SB-..."
```

### Type Conversion

Pydantic automatically converts values based on field types:

| Type | Example Input | Converted Value |
|------|--------------|-----------------|
| `bool` | `true`, `1`, `yes` | `True` |
| `bool` | `false`, `0`, `no` | `False` |
| `int` | `465` | `465` |
| `float` | `3.14` | `3.14` |
| `str` | `mail.example.com` | `"mail.example.com"` |

```bash
# Boolean examples
EMAIL__USE_SSL=true          # → True
EMAIL__USE_TLS=false         # → False

# Integer examples
EMAIL__PORT=465              # → 465 (int)
DATABASE__POOL_SIZE=20       # → 20 (int)

# String examples
EMAIL__HOST="mail.example.com"  # → "mail.example.com" (str)
```

---

## File Structure

```
docker/
├── .env                            # Development ENV vars (gitignored!)
├── .env.example                    # Template (in git)
├── .dockerignore                   # Excludes sensitive files
└── .gitignore                      # Ignores .env

projects/django/api/environment/
├── loader.py                       # Pydantic settings loader
├── .env                            # Local dev config (gitignored!)
└── .env.example                    # Template (in git)
```

### File Protection

#### `.dockerignore` (in `/docker/`)
```dockerignore
# Prevent secrets from entering Docker build context
.env
.env.*
!.env.example

# Don't copy poetry.lock
poetry.lock
```

#### `.gitignore` (in `/docker/`)
```gitignore
# Persistent volumes
/volumes/*

# Environment files (contains secrets - DO NOT COMMIT)
.env
.env.local
.env.*.local
```

#### `.gitignore` (in `/projects/django/api/environment/`)
```gitignore
# Environment file with secrets
.env
.env.local
```

---

## Configuration Files

### Development `.env` File

**Location**: `docker/.env` or `api/environment/.env`

```bash title="docker/.env"
# ═══════════════════════════════════════════════════════════
# Django-CFG Docker Environment Configuration
# ═══════════════════════════════════════════════════════════
# IMPORTANT: This file is gitignored! Never commit it!
# Copy from .env.example and fill in your values
# ═══════════════════════════════════════════════════════════

# === Environment Mode ===
IS_DEV=true

# === Core Django Settings ===
SECRET_KEY="django-cfg-dev-key-change-in-production-min-50-chars"
DEBUG=true

# === Database ===
DATABASE__URL="postgresql://postgres:postgres@postgres:5432/djangocfg"

# === Cache ===
REDIS_URL="redis://redis:6379/0"

# === Email Configuration ===
EMAIL__BACKEND="console"
EMAIL__HOST="localhost"
EMAIL__PORT=587
EMAIL__USE_TLS=true
EMAIL__DEFAULT_FROM="My App <noreply@localhost.dev>"

# === API Keys ===
API_KEYS__OPENAI="sk-proj-your-dev-key-here"
API_KEYS__OPENROUTER="sk-or-v1-your-dev-key-here"
API_KEYS__CLOUDFLARE="your-cloudflare-key"

# === Telegram ===
TELEGRAM__BOT_TOKEN="123456789:ABCdefGHIjklMNOpqrsTUVwxyz"
TELEGRAM__CHAT_ID=-123456789

# === Twilio (optional) ===
# TWILIO__ACCOUNT_SID="ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
# TWILIO__AUTH_TOKEN="your-auth-token-here"

# === Payments (optional) ===
# PAYMENTS_API_KEYS__NOWPAYMENTS_API_KEY="TV383SB-..."
# PAYMENTS_API_KEYS__NOWPAYMENTS_IPN_SECRET="your-ipn-secret"
# PAYMENTS_API_KEYS__NOWPAYMENTS_SANDBOX_MODE=true
```

### Example Template (`.env.example`)

**Location**: `docker/.env.example` (committed to git)

```bash title="docker/.env.example"
# Django-CFG Docker Environment - Example
# Copy this file to .env and fill in your values

# === Environment Mode ===
IS_DEV=true

# === Core Settings ===
SECRET_KEY="your-secret-key-minimum-50-characters-long"
DEBUG=true

# === Database ===
DATABASE__URL="postgresql://postgres:postgres@postgres:5432/djangocfg"

# === Cache ===
REDIS_URL="redis://redis:6379/0"

# === Email ===
EMAIL__BACKEND="console"
EMAIL__HOST="smtp.example.com"
EMAIL__PORT=587
EMAIL__USERNAME="your-email@example.com"
EMAIL__PASSWORD="your-password"
EMAIL__USE_TLS=true

# === API Keys ===
API_KEYS__OPENAI="your-openai-key"
API_KEYS__OPENROUTER="your-openrouter-key"

# === Telegram ===
TELEGRAM__BOT_TOKEN="your-bot-token"
TELEGRAM__CHAT_ID=0
```

### Docker Compose Integration

```yaml title="docker-compose.yml"
version: '3.8'

services:
  django:
    build: .
    env_file:
      - .env  # Loads environment variables from file
    environment:
      # Or set directly (overrides .env file)
      DATABASE__URL: "postgresql://postgres:postgres@postgres:5432/db"
      REDIS_URL: "redis://redis:6379/0"

  postgres:
    image: postgres:16
    environment:
      POSTGRES_DB: djangocfg
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres

  redis:
    image: redis:7-alpine
```

---

## Configuration Workflows

### Local Development (Without Docker)

**How it works:**
1. Create `.env` file in `api/environment/`
2. Run `python manage.py runserver`
3. Pydantic-settings automatically loads from `.env` file
4. System ENV variables override `.env` values

**Setup:**

```bash
# Copy example
cp api/environment/.env.example api/environment/.env

# Edit with your credentials
vim api/environment/.env

# Run development server
python manage.py runserver
```

### Docker Development

**How it works:**
1. Create `.env` file in `docker/` directory
2. Docker Compose loads it via `env_file:`
3. Pydantic-settings reads environment variables
4. No rebuilds needed - just restart!

**Setup:**

```bash
# Copy example
cp docker/.env.example docker/.env

# Edit with your credentials
vim docker/.env

# Start Docker services
docker compose up -d

# Restart to apply changes
docker compose restart django
```

**Benefits:**
- ✅ **No secrets in git** - `.env` is gitignored
- ✅ **No rebuilds needed** - Just restart container
- ✅ **Universal syntax** - Works for any config value
- ✅ **Type-safe** - Automatic validation via Pydantic

### Docker Production

**How it works:**
1. Set environment variables in Docker/K8s
2. Never use `.env` files in production
3. Use secrets managers (AWS Secrets Manager, Vault, etc.)

**Docker Compose production:**

```yaml
version: '3.8'

services:
  django:
    build: .
    environment:
      # Set from external sources
      IS_PROD: "true"
      SECRET_KEY: "${SECRET_KEY}"  # From host environment
      DATABASE__URL: "${DATABASE_URL}"
      EMAIL__PASSWORD: "${EMAIL_PASSWORD}"
      API_KEYS__OPENAI: "${OPENAI_API_KEY}"
```

**Kubernetes production:**

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
        - name: API_KEYS__OPENAI
          valueFrom:
            secretKeyRef:
              name: django-secrets
              key: openai-api-key
```

---

## Configuration Categories

### Use Environment Variables For:

✅ **All sensitive credentials**
```bash
API_KEYS__OPENAI="sk-proj-your-key"
EMAIL__PASSWORD="your-smtp-password"
TELEGRAM__BOT_TOKEN="your-bot-token"
```

✅ **Infrastructure URLs**
```bash
DATABASE__URL="postgresql://user:pass@host:5432/db"
REDIS_URL="redis://redis:6379/0"
```

✅ **Email credentials**
```bash
EMAIL__HOST="mail.example.com"
EMAIL__PORT=465
EMAIL__USERNAME="hello@example.com"
EMAIL__PASSWORD="your-password"
```

✅ **Third-party services**
```bash
TELEGRAM__BOT_TOKEN="123456789:ABC..."
TWILIO__AUTH_TOKEN="your-auth-token"
PAYMENTS_API_KEYS__NOWPAYMENTS_API_KEY="TV383SB-..."
```

✅ **Environment-specific values**
```bash
# Development
API_KEYS__STRIPE="sk_test_..."
DEBUG=true

# Production
API_KEYS__STRIPE="sk_live_..."
DEBUG=false
```

### Use Code Defaults For:

✅ **Development defaults**
```python
class DatabaseConfig(BaseSettings):
    url: str = Field(default="sqlite:///db/default.sqlite3")
```

✅ **Safe fallbacks**
```python
class EmailConfig(BaseSettings):
    backend: str = Field(default="console")
    port: int = Field(default=587)
```

✅ **Feature flags**
```python
class FeatureConfig(BaseSettings):
    enable_ai: bool = Field(default=True)
    enable_payments: bool = Field(default=False)
```

---

## Adding New Credentials

### Step 1: Add Field to Pydantic Model

```python
# api/environment/loader.py
class ApiKeysConfig(BaseSettings):
    """API keys configuration."""

    openai: str = Field(default="")
    openrouter: str = Field(default="")
    your_new_api: str = Field(default="")  # Add here

    model_config = SettingsConfigDict(
        env_prefix="API_KEYS__",
        env_nested_delimiter="__",
    )
```

### Step 2: Add to `.env`

```bash
# docker/.env
API_KEYS__YOUR_NEW_API="your-actual-api-key-here"
```

### Step 3: Restart Container (No Rebuild!)

```bash
docker compose restart django
```

:::tip[Fast Updates]
**No rebuild needed!** Configuration changes only require a restart:

```bash
# Old way (slow): Rebuild entire image
docker compose build django --no-cache  # ❌ 5+ minutes

# New way (fast): Just restart
docker compose restart django  # ✅ 10 seconds
```
:::

---

## Examples

### Complete `.env` for Docker Development

```bash title="docker/.env"
# === Environment Mode ===
IS_DEV=true

# === Core Django Settings ===
SECRET_KEY="django-cfg-dev-key-change-in-production-min-50-chars"
DEBUG=true

# === Database (Docker service name) ===
DATABASE__URL="postgresql://postgres:postgres@postgres:5432/djangocfg"

# === Cache (Docker service name) ===
REDIS_URL="redis://redis:6379/0"

# === Email Configuration ===
EMAIL__BACKEND="smtp"
EMAIL__HOST="mail.spacemail.com"
EMAIL__PORT=465
EMAIL__USERNAME="hello@example.com"
EMAIL__PASSWORD="your-smtp-password"
EMAIL__USE_TLS=false
EMAIL__USE_SSL=true
EMAIL__DEFAULT_FROM="My App <hello@example.com>"

# === API Keys ===
API_KEYS__OPENAI="sk-proj-your-dev-key-here"
API_KEYS__OPENROUTER="sk-or-v1-your-dev-key-here"
API_KEYS__CLOUDFLARE="your-cloudflare-key"
API_KEYS__NGROK="your-ngrok-token"

# === Telegram ===
TELEGRAM__BOT_TOKEN="123456789:ABCdefGHIjklMNOpqrsTUVwxyz"
TELEGRAM__CHAT_ID=-123456789

# === Twilio ===
TWILIO__ACCOUNT_SID="ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
TWILIO__AUTH_TOKEN="your-auth-token-here"
TWILIO__WHATSAPP_FROM="+1234567890"
TWILIO__SMS_FROM="+1234567890"

# === Payments ===
PAYMENTS_API_KEYS__NOWPAYMENTS_API_KEY="TV383SB-..."
PAYMENTS_API_KEYS__NOWPAYMENTS_IPN_SECRET="your-ipn-secret"
PAYMENTS_API_KEYS__NOWPAYMENTS_SANDBOX_MODE=true
```

### Docker Compose with `.env`

```yaml title="docker-compose.yml"
version: '3.8'

services:
  django:
    build:
      context: ../projects/django
      dockerfile: ../../docker/Dockerfile
    env_file:
      - .env  # Loads all variables from .env file
    ports:
      - "8000:8000"
    depends_on:
      - postgres
      - redis
    volumes:
      - ../projects/django:/app

  postgres:
    image: postgres:16
    environment:
      POSTGRES_DB: djangocfg
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data

volumes:
  postgres_data:
  redis_data:
```

---

## Environment Detection

Pydantic-settings automatically detects the environment:

```python
# From loader.py
class EnvironmentMode(BaseSettings):
    is_test: bool = Field(default=False)
    is_dev: bool = Field(default=False)
    is_prod: bool = Field(default=False)

    @model_validator(mode="after")
    def set_default_env(self):
        if not any([self.is_test, self.is_dev, self.is_prod]):
            self.is_dev = True
        return self
```

**Set in `.env`:**

```bash
# docker/.env
IS_DEV=true   # Development mode
# IS_PROD=true  # Production mode
# IS_TEST=true  # Testing mode
```

---

## Security Best Practices

### ✅ DO

**Use `.env` for development only**
```bash
# docker/.env (gitignored!)
API_KEYS__STRIPE="sk_test_your-dev-key"
EMAIL__PASSWORD="your-dev-password"
```

**Keep `.env` out of git**
```bash
# Already in .gitignore
.env
.env.local
.env.*.local
```

**Use `__` notation for clean variables**
```bash
EMAIL__HOST="mail.example.com"
API_KEYS__OPENAI="sk-proj-..."
DATABASE__URL="postgresql://..."
```

**Use different keys per environment**
```bash
# Development
API_KEYS__STRIPE="sk_test_..."

# Production
API_KEYS__STRIPE="sk_live_..."
```

**Use secrets managers in production**
- AWS Secrets Manager
- HashiCorp Vault
- Kubernetes Secrets
- Docker Secrets

**Create `.env.example` for team**
```bash
# Copy .env and replace values with placeholders
cp .env .env.example
# Replace: sk-proj-abc123 → your-openai-key-here
```

### ❌ DON'T

**Don't commit `.env` to git**
```bash
# ❌ BAD
git add docker/.env  # Contains secrets!
```

**Don't use production keys in development**
```bash
# ❌ BAD - Production key in dev
API_KEYS__STRIPE="sk_live_..."  # Should be sk_test_...
```

**Don't hardcode secrets in code**
```python
# ❌ BAD - Password in code
EMAIL_PASSWORD = "actual-password-here"  # Use ENV variable!
```

**Don't use same keys across environments**
```
Development: ✅ sk_test_...
Production:  ❌ sk_test_...  # Should be sk_live_...
```

**Don't share `.env` via insecure channels**
- ❌ Email or Slack
- ✅ Use password manager
- ✅ Use secure file transfer

---

## Migration from YAML

### Old Way (❌)

```yaml title="config.dev.docker.yaml"
# Committed to git or gitignored with credentials
api_keys:
  openai: "sk-proj-KEY-HERE"

email:
  host: "mail.example.com"
  password: "password-here"
```

### New Way (✅)

```bash title=".env (gitignored)"
# Simple ENV variables
API_KEYS__OPENAI="sk-proj-KEY-HERE"
EMAIL__HOST="mail.example.com"
EMAIL__PASSWORD="password-here"
```

### Migration Steps

**1. Create `.env`:**
```bash
cd docker
cp .env.example .env
```

**2. Move credentials from YAML to `.env`:**
```bash
# Old YAML:
api_keys:
  openai: "sk-proj-abc123"
email:
  host: "mail.example.com"
  password: "secret"

# New .env:
API_KEYS__OPENAI="sk-proj-abc123"
EMAIL__HOST="mail.example.com"
EMAIL__PASSWORD="secret"
```

**3. Update `.gitignore`:**
```gitignore
# Remove
config.*.docker.yaml
config.*.ignore.yaml

# Keep
.env
.env.*
```

**4. Restart services:**
```bash
docker compose restart django
```

---

## Troubleshooting

### Check Environment Variables in Container

```bash
docker exec django env | grep "__"
# Should show all your SECTION__FIELD variables
```

### Test Specific Value

```bash
docker exec django python -c "
from api.environment import env
print('OpenAI Key:', env.api_keys.openai[:20] if env.api_keys.openai else 'Not set')
print('Email Host:', env.email.host)
print('Database URL:', env.database.url)
"
```

### View Loaded Configuration

```bash
docker exec django python manage.py shell
>>> from api.environment import env
>>> print(f"Environment: {env.env.env_mode}")
>>> print(f"Debug: {env.debug}")
>>> print(f"Database: {env.database.url}")
>>> print(f"Email Host: {env.email.host}")
```

### Config Not Updating After Changes

**Problem:** Made changes to `.env` but config hasn't updated

**Solution:** Restart container (no rebuild needed!)
```bash
docker compose restart django
```

### Wrong Environment Detected

**Check environment variable:**
```bash
docker exec django env | grep "IS_"
# Should show IS_DEV=true or IS_PROD=true
```

**Set explicitly in docker-compose.yml:**
```yaml
services:
  django:
    environment:
      IS_DEV: "true"  # Force development mode
```

### Variables Not Loading

**Check `.env` file location:**
```bash
ls -la docker/.env
# Should exist and be readable
```

**Check docker-compose.yml:**
```yaml
services:
  django:
    env_file:
      - .env  # ✅ Correct path
      # - ../api/environment/.env  # ❌ Wrong path
```

**Verify variable format:**
```bash
# ✅ Correct (double underscore)
EMAIL__HOST="mail.example.com"

# ❌ Wrong (single underscore)
EMAIL_HOST="mail.example.com"
```

---

## Summary

### Configuration Loading Order:
1. **System ENV variables** - Docker Compose, K8s (highest priority)
2. **.env file** - Development only
3. **Code defaults** - Pydantic Field definitions (lowest priority)

### Key Benefits:
- ✅ **No secrets in git** - `.env` is gitignored
- ✅ **No image rebuilds** - Just restart to pick up changes
- ✅ **Universal syntax** - `SECTION__FIELD` works for everything
- ✅ **Type-safe** - Automatic validation via Pydantic
- ✅ **Simple** - One configuration method for all environments
- ✅ **12-factor app** - Environment-based configuration

### Quick Reference:
```bash
# Add new credential
echo 'API_KEYS__NEW_SERVICE="your-key-here"' >> docker/.env

# Restart to apply
docker compose restart django

# Verify it loaded
docker exec django python -c "from api.environment import env; print(env.api_keys.new_service)"
```

---

## Next Steps

**Set up development environment:**
[Development Setup →](./development)

**Deploy to production:**
[Production Guide →](./production)

**Troubleshoot issues:**
[Troubleshooting →](./troubleshooting)

---

## See Also

### Docker Guides
- **[Docker Overview](./overview)** - Complete Docker guide
- **[Development Setup](./development)** - Local environment
- **[Production Setup](./production)** - Deploy to production
- **[Build Optimization](./build-optimization)** - Performance tips
- **[Troubleshooting](./troubleshooting)** - Quick fixes

### Configuration
- **[Configuration Overview](/fundamentals/configuration/environment)** - Core concepts
- **[Database Configuration](/fundamentals/configuration/database)** - PostgreSQL
- **[Cache Configuration](/fundamentals/configuration/cache)** - Redis
- **[Environment Setup](/deployment/environment-setup)** - Detailed ENV guide

### Security
- **[Security Settings](/deployment/security)** - Production security
- **[Environment Setup](/deployment/environment-setup)** - Secrets management

---

**Last Updated**: 2025-10-21
**Django-CFG Version**: 1.4.52
**Configuration System**: Pydantic-settings with ENV variables

---

TAGS: docker, configuration, environment-variables, secrets, pydantic-settings
DEPENDS_ON: [docker, pydantic-settings]
USED_BY: [development, production, docker-setup]
