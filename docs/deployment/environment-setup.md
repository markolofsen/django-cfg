---
title: Environment Setup
description: Environment configuration principles for Django-CFG with YAML configs and environment variable overrides.
sidebar_label: Environment Setup
sidebar_position: 1
keywords:
  - django-cfg environment
  - environment configuration
  - yaml configuration
---

# 🌍 Environment Setup

Django-CFG uses YAML configuration files with environment variable overrides for flexible deployment across different environments.

---

## Core Principles

### Single Source of Truth
One YAML file per environment contains all configuration:

```
api/environment/
├── config.dev.yaml         # Development (local)
├── config.prod.yaml        # Production
├── config.dev.docker.yaml  # Development (Docker)
└── config.prod.docker.yaml # Production (Docker)
```

### Priority System

Configuration loading follows this priority (highest wins):

```
1. Environment variables (highest priority)
2. YAML file values
3. Default values (lowest priority)
```

### Environment Detection

Automatic detection based on environment variables:

```bash
# Development (default)
IS_DEV=true

# Production
IS_PROD=true

# Testing
IS_TEST=true
# or: pytest (auto-detected)
```

---

## Configuration Structure

### Development Config

```yaml
# config.dev.yaml

# === Core Settings ===
secret_key: "dev-secret-key-at-least-50-chars-xxxxxxxxxxxxxxxxxxxxxxx"
debug: false

# === Database ===
database:
  url: ${DATABASE_URL:-postgresql://postgres:postgres@postgres:5432/djangocfg}

# === Application URLs ===
app:
  name: "My App"
  domain: ${DOMAIN:-localhost}
  api_url: ${API_URL:-http://localhost:8000}
  site_url: ${SITE_URL:-http://localhost:3000}

# === Security Domains ===
# Optional in development - Django-CFG auto-configures:
# - CORS open for all localhost ports
# - Docker IPs work automatically
# security_domains:
#   - "staging.example.com"

# === Email ===
email:
  backend: "console"  # Prints to console
  default_from: "noreply@localhost.dev"

# === Cache ===
redis_url: ${REDIS_URL:-redis://redis:6379/0}

# === API Keys ===
api_keys:
  openai: ""      # Set via OPENAI_API_KEY env var
  sendgrid: ""    # Set via SENDGRID_API_KEY env var
```

### Production Config

```yaml
# config.prod.yaml

# === Core Settings ===
secret_key: ${SECRET_KEY}  # REQUIRED from environment
debug: false

# === Database ===
database:
  url: ${DATABASE_URL}

# === Application URLs ===
app:
  name: ${APP_NAME:-My App}
  domain: ${DOMAIN:-example.com}
  api_url: ${API_URL:-https://api.example.com}
  site_url: ${SITE_URL:-https://example.com}

# === Security Domains ===
# REQUIRED in production!
security_domains:
  - "example.com"
  - "api.example.com"
  - "www.example.com"

# === Email ===
email:
  backend: "smtp"
  host: "smtp.example.com"
  port: 587
  username: ${EMAIL_USERNAME}
  password: ${EMAIL_PASSWORD}
  use_tls: true
  default_from: "My App <noreply@example.com>"

# === Cache ===
redis_url: ${REDIS_URL:-redis://localhost:6379/1}

# === API Keys ===
api_keys:
  openai: ${OPENAI_API_KEY}
  sendgrid: ${SENDGRID_API_KEY}
```

### Docker Configs

Docker versions are identical but use Docker service names:

```yaml
# config.dev.docker.yaml (identical to config.dev.yaml)
# Just copy config.dev.yaml for Docker

# config.prod.docker.yaml (identical to config.prod.yaml)
# Just copy config.prod.yaml for Docker
```

Docker service names (postgres, redis) work automatically due to Docker networking.

---

## Environment Variables

### Standard Variables

Django-CFG supports standard environment variables:

```bash
# Core
SECRET_KEY=your-secret-key-here
DEBUG=true
DATABASE_URL=postgresql://user:pass@host:5432/db
REDIS_URL=redis://localhost:6379/0

# API Keys
OPENAI_API_KEY=sk-...
SENDGRID_API_KEY=SG...
```

### Nested Configuration Override

Use `__` (double underscore) to override nested config:

```bash
# email.host
EMAIL__HOST=smtp.gmail.com

# email.port
EMAIL__PORT=587

# api_keys.openai
API_KEYS__OPENAI=sk-...

# app.domain
APP__DOMAIN=example.com
```

**Pattern:** `SECTION__FIELD=value` maps to `section.field = value`

---

## Loading Configuration

### Automatic Loading

Django-CFG automatically loads the correct config:

```python
# api/environment/loader.py
from pydantic_yaml import parse_yaml_file_as

# Environment detection
IS_DEV = os.environ.get("IS_DEV", "").lower() in ("true", "1", "yes")
IS_PROD = os.environ.get("IS_PROD", "").lower() in ("true", "1", "yes")
IS_TEST = "test" in sys.argv  # Auto-detect pytest

# Config file selection with Docker priority
if IS_PROD:
    # Check Docker config first, fallback to regular
    config_file = "config.prod.docker.yaml" if exists("config.prod.docker.yaml") else "config.prod.yaml"
elif IS_TEST:
    config_file = "config.test.yaml"
else:
    # Check Docker config first, fallback to regular
    config_file = "config.dev.docker.yaml" if exists("config.dev.docker.yaml") else "config.dev.yaml"

# Load YAML config
env = parse_yaml_file_as(EnvironmentConfig, config_file)

# Override with environment variables (double underscore pattern)
for env_key, env_value in os.environ.items():
    if '__' in env_key:
        # EMAIL__HOST -> env.email.host
        parts = env_key.lower().split('__')
        obj = env
        for part in parts[:-1]:
            obj = getattr(obj, part)
        setattr(obj, parts[-1], convert_type(env_value))

print(f"✅ Loaded config: {config_file}")
```

### Using Configuration

```python
# api/config.py
from django_cfg import DjangoConfig
from .environment import env

class MyDjangoConfig(DjangoConfig):
    project_name: str = env.app.name
    secret_key: str = env.secret_key
    debug: bool = env.debug
    security_domains: list[str] = env.security_domains or []

    # Database from environment config
    databases = {
        "default": {
            "url": env.database.url
        }
    }

# Generate Django settings
settings = MyDjangoConfig().to_settings()
```

---

## Environment-Specific Behavior

### Development

**Automatic configuration:**
- `security_domains: []` → CORS open, localhost any port allowed
- `email.backend: console` → Emails printed to console
- `debug: true` → Verbose logging, detailed errors
- Relaxed security settings

### Production

**Automatic configuration:**
- `security_domains` → REQUIRED, strict CORS/CSRF
- `email.backend: smtp` → Real email sending
- `debug: false` → Structured logging, minimal output
- Strict security (HTTPS, HSTS, secure cookies)

### Docker

**Automatic features:**
- Service name resolution (postgres, redis)
- Health check endpoints enabled
- Private IP ranges allowed for internal calls
- Container-aware resource monitoring

---

## Best Practices

### 1. Never Commit Secrets

```bash
# .gitignore
.env
.env.*
config.prod.yaml  # If it contains secrets
secrets/
```

### 2. Use Environment Variables for Secrets

```yaml
# Good - loads from environment
secret_key: ${SECRET_KEY}
database_url: ${DATABASE_URL}
api_keys:
  openai: ${OPENAI_API_KEY}

# Bad - hardcoded secrets
secret_key: "my-secret-key-12345"
api_keys:
  openai: "sk-hardcoded-key"
```

### 3. Provide Defaults for Non-Secrets

```yaml
# Good - has fallback
database_url: ${DATABASE_URL:-postgresql://localhost:5432/mydb}
redis_url: ${REDIS_URL:-redis://localhost:6379/0}

# Bad - no fallback, crashes if not set
database_url: ${DATABASE_URL}
```

### 4. Document Required Variables

```yaml
# === Required Environment Variables ===
# Production deployment requires:
# - SECRET_KEY: Django secret key (50+ chars)
# - DATABASE_URL: PostgreSQL connection string
# - REDIS_URL: Redis connection string
# - OPENAI_API_KEY: OpenAI API key (if using AI features)

secret_key: ${SECRET_KEY}
database_url: ${DATABASE_URL}
```

---

## Docker Deployment

For Docker deployment, see **[Docker Guide →](/guides/docker/overview)**

### Quick Reference

Docker configs are identical to regular configs:

```bash
# Copy configs for Docker
cp config.dev.yaml config.dev.docker.yaml
cp config.prod.yaml config.prod.docker.yaml

# Use Docker service names (postgres, redis)
# Everything else works the same!
```

---

## Troubleshooting

### Config File Not Found

```bash
# Check file exists
ls api/environment/config.*.yaml

# Check environment variable
echo $IS_PROD  # Should be "true" or "1"
echo $IS_DEV   # Should be "true" or "1"
```

### Environment Variables Not Applied

```bash
# Check variable format
EMAIL__HOST=smtp.gmail.com  # ✅ Correct (double underscore)
EMAIL_HOST=smtp.gmail.com   # ❌ Wrong (single underscore)

# Test override
python manage.py shell
>>> from api.environment import env
>>> print(env.email.host)  # Should show overridden value
```

### Secret Key Error

```bash
# Generate secure key
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"

# Set in environment
export SECRET_KEY="generated-key-here"

# Or in YAML (development only)
secret_key: "dev-key-at-least-50-characters-long-xxxxxxxxxxxxxxxxxxxxx"
```

---

## See Also

- **[Docker Guide](/guides/docker/overview)** - Docker deployment
- **[Security Settings](/deployment/security)** - Security domains and CORS
- **[Monitoring](/deployment/monitoring)** - Health checks and logging
- **[Configuration Reference](/fundamentals/configuration)** - Full config options

---

TAGS: environment, configuration, yaml, env-vars, deployment
DEPENDS_ON: [django-cfg, yaml, pydantic]
USED_BY: [deployment, docker, production]
