---
title: Docker Configuration Strategy
description: Master Django-CFG configuration in Docker with universal __ notation and YAML files. Learn the modern hybrid approach for seamless credential management.
sidebar_label: Configuration
sidebar_position: 3
keywords:
  - django-cfg docker configuration
  - docker environment variables
  - django docker secrets
  - __ notation configuration
  - yaml docker configuration
---

# Docker Configuration Strategy

> **📚 Part of**: [Docker Guide](./overview) - Return to Docker overview

Learn Django-CFG's modern hybrid configuration approach: YAML files for structure + environment variables for credentials.

---

## Overview

Django-CFG uses a layered configuration system that combines:
- **YAML files** - Structure and templates
- **Environment variables** - Universal `SECTION__FIELD` notation for overrides
- **No rebuilds needed** - Just restart to apply credential changes

:::tip[Key Innovation]
The **universal `__` notation** allows you to override ANY config value via environment variables, with automatic type conversion and no image rebuilds needed.
:::

---

## Configuration Priority

**Settings load in this order (highest priority first)**:

1. **Environment variables** - `SECTION__FIELD` notation (e.g., `EMAIL__HOST`)
2. **`.env.secrets`** file - Sensitive credentials (git-ignored)
3. **`config.*.docker.yaml`** - Docker-specific configs (git-ignored)
4. **`config.*.yaml`** - Base templates (in git)
5. **Built-in defaults** - Pydantic model defaults

```mermaid
graph LR
    A[ENV Variables<br/>EMAIL__HOST] --> B{Set?}
    B -->|Yes| H[Use Value]
    B -->|No| C[.env.secrets]
    C --> D{Set?}
    D -->|Yes| H
    D -->|No| E[config.*.docker.yaml]
    E --> F{Set?}
    F -->|Yes| H
    F -->|No| G[config.*.yaml]
    G --> I{Set?}
    I -->|Yes| H
    I -->|No| J[Built-in default]
    J --> H
```

---

## Universal `__` Notation

### How It Works

Any configuration value can be overridden using `SECTION__FIELD` format:

```bash
# Simple section field
EMAIL__HOST=mail.example.com
EMAIL__PORT=465
EMAIL__PASSWORD=your-password-here

# Nested subsections
API_KEYS__OPENAI=sk-proj-your-key-here
API_KEYS__CLOUDFLARE=your-cloudflare-key

# Deep nesting
PAYMENTS_API_KEYS__NOWPAYMENTS_API_KEY=TV383SB-...
```

### Type Conversion

The system automatically converts values based on Pydantic model field types:

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
REDIS__MAX_CONNECTIONS=100   # → 100 (int)

# String examples
EMAIL__HOST=mail.spacemail.com  # → "mail.spacemail.com" (str)
```

---

## File Structure

```
docker/
├── .env                            # Base environment variables (in git)
├── .env.secrets                    # Sensitive credentials (git-ignored!)
├── .dockerignore                   # Excludes .env.secrets and poetry.lock
└── .gitignore                      # Ignores .env.secrets

projects/django/api/environment/
├── loader.py                       # Configuration loader with __ support
├── config.dev.yaml                 # Development template (in git)
├── config.dev.docker.yaml          # Docker dev config (git-ignored!)
├── config.prod.yaml                # Production template (in git)
├── config.prod.docker.yaml         # Docker prod config (git-ignored!)
└── .gitignore                      # Ignores config.*.docker.yaml
```

### File Protection

#### `.dockerignore` (in `/docker/`)
```dockerignore
# Prevent secrets from entering Docker build context
.env.secrets
.env.local
.env.*.local

# Don't copy poetry.lock
poetry.lock
```

#### `.gitignore` (in `/docker/`)
```gitignore
# Persistent volumes
/volumes/*

# Environment secrets (contains real API keys - DO NOT COMMIT)
.env.secrets
.env.local
.env.*.local
```

#### `.gitignore` (in `/projects/django/api/environment/`)
```gitignore
# Ignore Docker-specific configs with credentials
config.*.docker.yaml
```

---

## The `.env.secrets` File

**Location**: `docker/.env.secrets`

This file contains **all sensitive credentials** using the universal `__` notation:

```bash
# ═══════════════════════════════════════════════════════════
# Django-CFG Environment Secrets
# ═══════════════════════════════════════════════════════════
# IMPORTANT: This file is git-ignored! Never commit it!
# Use SECTION__FIELD notation for any config value override
# ═══════════════════════════════════════════════════════════

# Email Configuration
EMAIL__BACKEND=smtp
EMAIL__HOST=mail.spacemail.com
EMAIL__PORT=465
EMAIL__USERNAME=hello@example.com
EMAIL__PASSWORD=your-password-here
EMAIL__USE_TLS=false
EMAIL__USE_SSL=true
EMAIL__DEFAULT_FROM=My App <hello@example.com>

# API Keys
API_KEYS__OPENAI=sk-proj-...
API_KEYS__OPENROUTER=sk-or-v1-...
API_KEYS__CLOUDFLARE=your-key-here
API_KEYS__NGROK=your-ngrok-token
API_KEYS__PERPLEXITY=pplx-...

# Telegram
TELEGRAM__BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz
TELEGRAM__CHAT_ID=-123456789

# Twilio
TWILIO__ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO__AUTH_TOKEN=your-auth-token-here
TWILIO__WHATSAPP_FROM=+1234567890
TWILIO__SMS_FROM=+1234567890
TWILIO__SENDGRID_API_KEY=SG.your-sendgrid-key-here

# Payments
PAYMENTS_API_KEYS__NOWPAYMENTS_API_KEY=TV383SB-...
PAYMENTS_API_KEYS__NOWPAYMENTS_IPN_SECRET=your-ipn-secret
PAYMENTS_API_KEYS__NOWPAYMENTS_SANDBOX_MODE=false
```

### Docker Compose Integration

```yaml
# docker-compose.yaml
services:
  django:
    env_file:
      - .env          # Base config (in git)
      - .env.secrets  # Sensitive credentials (git-ignored)
    environment:
      # Infrastructure URLs (can also be in .env)
      DATABASE_URL: postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@postgres:5432/${POSTGRES_DB}
      REDIS_URL: redis://redis:6379/0
```

---

## Configuration Workflows

### Local Development (Without Docker)

**How it works:**
1. Run `python manage.py runserver` locally
2. Loader checks for `config.dev.docker.yaml` first
3. Falls back to `config.dev.yaml` if not found
4. Environment variables (with `__` notation) override YAML values

**Create Docker-specific config:**

```bash
# Copy template
cp api/environment/config.dev.yaml api/environment/config.dev.docker.yaml

# Edit with your development credentials
vim api/environment/config.dev.docker.yaml
```

**What goes in `config.*.docker.yaml`:**

```yaml
# Full credentials for Docker development
email:
  backend: "smtp"
  host: "mail.spacemail.com"
  port: 465
  username: "hello@example.com"
  password: "your-password-here"
  use_tls: false
  use_ssl: true

api_keys:
  openai: "sk-proj-YOUR-FULL-KEY-HERE"
  cloudflare: "your-cloudflare-key-here"

telegram:
  bot_token: "123456789:ABCdefGHIjklMNOpqrsTUVwxyz"
  chat_id: -123456789
```

:::warning[Security]
**`config.*.docker.yaml` files are gitignored!** They contain full credentials for local development.
:::

### Docker Environment

**How it works:**
1. Base config file (`config.dev.yaml`) is built into image
2. Docker-specific config (`config.dev.docker.yaml`) overrides base if exists
3. `.env.secrets` file provides sensitive credentials via `__` notation
4. Loader auto-detects and prioritizes configs

**Benefits:**
- ✅ **No secrets in git** - `.env.secrets` is gitignored
- ✅ **No rebuilds needed** - Just restart to apply changes
- ✅ **Universal syntax** - Works for any config value
- ✅ **Type-safe** - Automatic conversion based on Pydantic models

---

## Configuration Categories

### Use Environment Variables (`__` notation) For:

✅ **All sensitive credentials**
```bash
API_KEYS__OPENAI=sk-proj-your-key
EMAIL__PASSWORD=your-smtp-password
```

✅ **Email credentials**
```bash
EMAIL__HOST=mail.example.com
EMAIL__PORT=465
EMAIL__USERNAME=hello@example.com
EMAIL__PASSWORD=your-password
```

✅ **Third-party services**
```bash
TELEGRAM__BOT_TOKEN=123456789:ABC...
TWILIO__AUTH_TOKEN=your-auth-token
PAYMENTS_API_KEYS__NOWPAYMENTS_API_KEY=TV383SB-...
```

✅ **Per-environment values**
```bash
# Development
API_KEYS__STRIPE=sk_test_...

# Production
API_KEYS__STRIPE=sk_live_...
```

### Use YAML Files For:

✅ **Structure and templates**
```yaml
# Base configuration shape
email:
  backend: "console"
  host: "localhost"
  port: 587
```

✅ **Non-sensitive defaults**
```yaml
redis:
  max_connections: 50
  timeout: 5
```

✅ **Feature flags**
```yaml
features:
  enable_ai: true
  enable_payments: false
```

✅ **Infrastructure URLs** (can also use env vars)
```yaml
database:
  url: "${DATABASE_URL}"  # From environment
```

---

## Adding New Credentials

### Step 1: Add Field to Pydantic Model

```python
# loader.py
class ApiKeysConfig(BaseModel):
    """API keys configuration."""

    openai: str = ""
    openrouter: str = ""
    your_new_api: str = ""  # Add here
```

### Step 2: Add to `.env.secrets`

```bash
# docker/.env.secrets
API_KEYS__YOUR_NEW_API=your-actual-api-key-here
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

### Base Template (`config.dev.yaml`)

```yaml
# Minimal template with no secrets (in git)
email:
  backend: "console"  # Print emails to console in dev
  host: "localhost"
  port: 587
  use_tls: true

api_keys:
  openai: ""       # Empty - override via ENV
  openrouter: ""
  cloudflare: ""

database:
  url: "${DATABASE_URL}"  # From environment

redis:
  url: "${REDIS_URL}"     # From environment
```

### Docker-Specific Config (`config.dev.docker.yaml`)

```yaml
# Docker development with full credentials (git-ignored!)
email:
  backend: "smtp"
  host: "mail.spacemail.com"
  port: 465
  username: "hello@example.com"
  password: "your-smtp-password-here"
  use_tls: false
  use_ssl: true

api_keys:
  openai: "sk-proj-your-key-here..."
  openrouter: "sk-or-v1-your-key-here..."
  cloudflare: "your-cloudflare-key-here"

telegram:
  bot_token: "123456789:ABCdefGHIjklMNOpqrsTUVwxyz"
  chat_id: -123456789
```

### Environment Variables (`.env.secrets`)

```bash
# Overrides everything (git-ignored!)
EMAIL__HOST=mail.spacemail.com
EMAIL__PASSWORD=actual-password-here
API_KEYS__OPENAI=sk-proj-actual-key-here
```

---

## Environment Detection

The loader automatically detects the environment:

```python
# From loader.py
IS_DEV = os.environ.get("IS_DEV", "").lower() in ("true", "1", "yes")
IS_PROD = os.environ.get("IS_PROD", "").lower() in ("true", "1", "yes")
IS_TEST = os.environ.get("IS_TEST", "").lower() in ("true", "1", "yes")
```

**Set in `.env`:**

```bash
# docker/.env
IS_DEV=true  # Uses config.dev.docker.yaml → config.dev.yaml → defaults
```

**Config file priority:**
1. `config.dev.docker.yaml` (if exists)
2. `config.dev.yaml` (fallback)
3. Built-in defaults

---

## Security Best Practices

### ✅ DO

**Use `.env.secrets` for ALL sensitive credentials**
```bash
# docker/.env.secrets (git-ignored!)
API_KEYS__STRIPE=sk_live_your-production-key
EMAIL__PASSWORD=your-smtp-password
```

**Keep `.env.secrets` out of git**
```bash
# Already in .gitignore
.env.secrets
```

**Use `__` notation for clean variable names**
```bash
EMAIL__HOST=mail.example.com
API_KEYS__OPENAI=sk-proj-...
```

**Rotate API keys regularly**
- Every 90 days minimum
- Immediately if compromised

**Use different keys per environment**
```bash
# Development
API_KEYS__STRIPE=sk_test_...

# Production
API_KEYS__STRIPE=sk_live_...
```

**Document all `__` variables**
```bash
# Create .env.secrets.example
cp .env.secrets .env.secrets.example
# Replace values with placeholders
```

### ❌ DON'T

**Don't commit `.env.secrets` to git**
```bash
# ❌ BAD
git add docker/.env.secrets
```

**Don't put production keys in development configs**
```yaml
# ❌ BAD - Production key in dev
api_keys:
  stripe: "sk_live_..."  # Should be sk_test_...
```

**Don't hardcode secrets in YAML files**
```yaml
# ❌ BAD - Password in template
email:
  password: "actual-password-here"  # Use ENV variable instead!
```

**Don't use same API keys across environments**
```
Development: ✅ sk_test_...
Production:  ❌ sk_test_...  # Should be sk_live_...
```

**Don't share `.env.secrets` via insecure channels**
- Use password manager
- Use secure file transfer
- Never email or Slack

---

## Migration from Old System

### Old Way (❌)

```yaml
# docker/services/django/config.dev.ignore.yaml (committed to git!)
api_keys:
  openai: "sk-proj-KEY-IN-GIT-BAD"
```

### New Way (✅)

```bash
# docker/.env.secrets (git-ignored!)
API_KEYS__OPENAI=sk-proj-KEY-NOT-IN-GIT-GOOD
```

### Migration Steps

**1. Create `.env.secrets`:**
```bash
cd docker
touch .env.secrets
```

**2. Move credentials from YAML to `.env.secrets`:**
```bash
# Old: config.dev.docker.yaml
api_keys:
  openai: "sk-proj-abc123"

# New: .env.secrets
API_KEYS__OPENAI=sk-proj-abc123
```

**3. Update `.gitignore`:**
```gitignore
.env.secrets
config.*.docker.yaml
```

**4. Restart services:**
```bash
docker compose restart django
```

---

## Troubleshooting

### Check Which Config is Loaded

```bash
docker logs django | grep "Loading config file"
# Output: Loading config file: config.dev.docker.yaml (Docker-specific)
```

### Check Environment Variable Overrides

```bash
docker logs django | grep "Environment variables override"
# Output: ✅ Environment variables override YAML: EMAIL__HOST, API_KEYS__OPENAI, ...
```

### Test Specific Value

```bash
docker exec django python -c "
from api.environment.loader import get_environment_config
config = get_environment_config()
print('OpenAI Key:', config.api_keys.openai[:20])
"
```

### Verify `.env.secrets` is Loaded

```bash
docker exec django env | grep "__"
# Should show all your SECTION__FIELD variables
```

### Config Not Updating After Changes

**Problem:** Made changes to `.env.secrets` but config hasn't updated

**Solution:** Just restart (no rebuild needed!)
```bash
docker compose restart django
```

### Wrong Config File Used

**Check loader output:**
```bash
docker logs django | grep "Loading config file"
```

**List available configs:**
```bash
docker exec django ls -la /app/api/environment/
```

---

## Summary

### Configuration Loading Order:
1. **Base YAML** (`config.dev.yaml`) - Templates and structure
2. **Docker YAML** (`config.dev.docker.yaml`) - Docker-specific overrides
3. **`.env.secrets`** - Sensitive credentials via `__` notation
4. **Direct ENV vars** - Runtime overrides

### Key Benefits:
- ✅ **No secrets in git** - `.env.secrets` is gitignored
- ✅ **No image rebuilds** - Just restart to pick up changes
- ✅ **Universal syntax** - `SECTION__FIELD` works for any config
- ✅ **Type-safe** - Automatic conversion based on Pydantic models
- ✅ **Clean separation** - Structure in YAML, secrets in ENV
- ✅ **Team-friendly** - Share YAML templates, keep credentials private

### Quick Reference:
```bash
# Add new credential
echo "API_KEYS__NEW_SERVICE=your-key-here" >> docker/.env.secrets

# Restart to apply
docker compose restart django

# Verify it loaded
docker logs django | grep "API_KEYS__NEW_SERVICE"
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
- **[Configuration Overview](/fundamentals/configuration)** - Core concepts
- **[Database Configuration](/fundamentals/configuration/database)** - PostgreSQL
- **[Cache Configuration](/fundamentals/configuration/cache)** - Redis
- **[Environment Variables](/fundamentals/configuration/environment)** - Env vars

### Security
- **[Security Settings](/deployment/security)** - Production security
- **[Environment Setup](/deployment/environment-setup)** - Secrets management

---

**Last Updated**: 2025-10-14
**Django-CFG Version**: 1.4.41
**Configuration System**: Universal `__` notation + YAML templates

---

TAGS: docker, configuration, yaml, environment-variables, secrets, __ notation
DEPENDS_ON: [docker, pydantic, yaml]
USED_BY: [development, production, docker-setup]
