---
title: Configuration Guide
description: Learn configuration in Django-CFG. Step-by-step guide with environment variables, pydantic-settings, and production-ready patterns.
sidebar_label: Configuration
sidebar_position: 3
keywords:
  - django-cfg configuration
  - django configuration
  - pydantic-settings
  - environment variables
---

import { TechArticleSchema } from '@site/src/components/Schema';
import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

<TechArticleSchema
  headline="Django-CFG Configuration Guide: Type-Safe Environment Configuration with Pydantic"
  description="Comprehensive guide to configuring Django-CFG with environment variables and type-safe Pydantic models for production-ready Django applications"
  keywords={['django-cfg configuration', 'environment variables django', 'pydantic configuration', 'pydantic-settings', 'type-safe django settings']}
/>

# Configuration Guide

:::tip[Simple & Modern]
Django-CFG uses **pydantic-settings** for type-safe environment configuration. No YAML files, no complex loaders. Just **ENV variables**, **.env files**, and **defaults in code**.
:::

## Configuration Flow

```mermaid
graph TB
    subgraph "1. Environment Detection"
        SYS_ENV[System ENV<br/>Variables]
        DOTENV[.env File]
    end

    subgraph "2. Pydantic Loading"
        LOADER[pydantic-settings<br/>BaseSettings]
        MODELS[Type-Safe Models<br/>DatabaseConfig, EmailConfig]
        VALIDATE[Validation]
    end

    subgraph "3. Django Integration"
        ENV_OBJ[env object]
        CONFIG[DjangoConfig]
        DJANGO[Django Settings]
    end

    SYS_ENV -->|Highest Priority| LOADER
    DOTENV -->|Medium Priority| LOADER

    LOADER --> MODELS
    MODELS --> VALIDATE
    VALIDATE --> ENV_OBJ
    ENV_OBJ --> CONFIG
    CONFIG --> DJANGO
```

## Overview

Django-CFG uses **pydantic-settings** to load configuration from environment variables and .env files. This provides type-safe configuration with automatic validation.

**Key benefits:**
- ✅ Simple - one configuration method for all environments
- ✅ [Type-safe loader](/fundamentals/core/type-safety) with Pydantic models
- ✅ Single import point via environment module
- ✅ 12-factor app compliant
- ✅ Works everywhere (Docker, K8s, CI/CD)

:::warning[Security First]
Never commit secrets to version control. Use environment variables or secrets managers for sensitive data.
:::

## Quick Start

### 1. Create Environment Module

```
project/
├── config.py          # Main DjangoConfig class
├── settings.py        # Django settings
└── environment/       # Environment configuration
    ├── __init__.py    # Exports `env` instance
    ├── loader.py      # Pydantic models with BaseSettings
    ├── .env           # Local development config (gitignored!)
    └── .env.example   # Template for team
```

### 2. Create Pydantic Models (loader.py)

```python
# environment/loader.py
from pathlib import Path
from typing import Optional
from pydantic import Field, computed_field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class DatabaseConfig(BaseSettings):
    """Database connection configuration."""

    url: str = Field(
        default="sqlite:///db/default.sqlite3",
        description="Database connection URL"
    )

    model_config = SettingsConfigDict(
        env_prefix="DATABASE__",
        env_nested_delimiter="__",
    )


class EmailConfig(BaseSettings):
    """Email configuration."""

    backend: str = Field(default="console")
    host: str = Field(default="localhost")
    port: int = Field(default=587)
    username: Optional[str] = Field(default=None)
    password: Optional[str] = Field(default=None)
    use_tls: bool = Field(default=True)
    use_ssl: bool = Field(default=False)
    default_from: str = Field(default="noreply@example.com")

    model_config = SettingsConfigDict(
        env_prefix="EMAIL__",
        env_nested_delimiter="__",
    )


class TelegramConfig(BaseSettings):
    """Telegram bot configuration."""

    bot_token: str = Field(default="")
    chat_id: int = Field(default=0)

    model_config = SettingsConfigDict(
        env_prefix="TELEGRAM__",
        env_nested_delimiter="__",
    )


class ApiKeysConfig(BaseSettings):
    """API keys configuration."""

    openrouter: str = Field(default="")
    openai: str = Field(default="")

    model_config = SettingsConfigDict(
        env_prefix="API_KEYS__",
        env_nested_delimiter="__",
    )


class AppConfig(BaseSettings):
    """Application configuration."""

    name: str = Field(default="My Project")
    logo_url: str = Field(default="")
    domain: str = Field(default="localhost")
    api_url: str = Field(default="http://localhost:8000")
    site_url: str = Field(default="http://localhost:3000")

    model_config = SettingsConfigDict(
        env_prefix="APP__",
        env_nested_delimiter="__",
    )


class EnvironmentMode(BaseSettings):
    """Environment mode detection via ENV variables."""

    is_test: bool = Field(default=False)
    is_dev: bool = Field(default=False)
    is_prod: bool = Field(default=False)

    @model_validator(mode="after")
    def set_default_env(self):
        """Default to development if no environment is set."""
        if not any([self.is_test, self.is_dev, self.is_prod]):
            self.is_dev = True
        return self

    @computed_field
    @property
    def env_mode(self) -> str:
        """Get current environment mode as string."""
        if self.is_test:
            return "test"
        elif self.is_prod:
            return "production"
        return "development"

    model_config = SettingsConfigDict(
        env_nested_delimiter="__",
    )


class EnvironmentConfig(BaseSettings):
    """Complete environment configuration."""

    # Core Django settings
    secret_key: str = Field(
        default="django-cfg-dev-key-change-in-production-min-50-chars"
    )
    debug: bool = Field(default=True)

    # Admin Configuration
    admin_emails: Optional[list[str]] = Field(default=None)

    # Configuration sections (nested configs)
    database: DatabaseConfig = Field(default_factory=DatabaseConfig)
    email: EmailConfig = Field(default_factory=EmailConfig)
    telegram: TelegramConfig = Field(default_factory=TelegramConfig)
    api_keys: ApiKeysConfig = Field(default_factory=ApiKeysConfig)
    app: AppConfig = Field(default_factory=AppConfig)
    env: EnvironmentMode = Field(default_factory=EnvironmentMode)

    # Cache
    redis_url: Optional[str] = Field(default=None)

    # Security domains
    security_domains: Optional[list[str]] = Field(
        default=["localhost", "127.0.0.1"],
        description="Allowed security domains"
    )

    model_config = SettingsConfigDict(
        env_file=str(Path(__file__).parent / ".env"),
        env_file_encoding="utf-8",
        env_nested_delimiter="__",
        case_sensitive=False,
        extra="ignore",
    )


# Global environment configuration instance
# Auto-loads from: ENV variables > .env file > defaults
env = EnvironmentConfig()
```

### 3. Export env Instance (__init__.py)

```python
# environment/__init__.py
from .loader import (
    EnvironmentConfig,
    env,
    DatabaseConfig,
    EmailConfig,
    TelegramConfig,
    AppConfig,
    EnvironmentMode,
)

__all__ = [
    "EnvironmentConfig",
    "env",
    "DatabaseConfig",
    "EmailConfig",
    "TelegramConfig",
    "AppConfig",
    "EnvironmentMode",
]
```

### 4. Create .env File

<Tabs>
  <TabItem value="dev" label="Development (.env)" default>

```bash title="environment/.env"
# === Environment Mode ===
IS_DEV=true

# === Core Django Settings ===
SECRET_KEY="django-cfg-dev-secret-key-change-in-production-min-50-chars"
DEBUG=true

# === Database ===
# SQLite (default):
# DATABASE__URL="sqlite:///db/default.sqlite3"
# PostgreSQL (recommended for dev):
DATABASE__URL="postgresql://postgres:postgres@localhost:5432/djangocfg"

# === Cache ===
REDIS_URL="redis://localhost:6379/0"

# === Email Configuration ===
EMAIL__BACKEND="console"
EMAIL__DEFAULT_FROM="My Project <noreply@localhost.dev>"

# === Telegram (optional) ===
# TELEGRAM__BOT_TOKEN="your-bot-token"
# TELEGRAM__CHAT_ID=0

# === API Keys (optional) ===
# API_KEYS__OPENROUTER="sk-or-xxx"
# API_KEYS__OPENAI="sk-proj-xxx"

# === Application URLs (optional - has defaults) ===
# APP__NAME="My Project"
# APP__API_URL="http://localhost:8000"
# APP__SITE_URL="http://localhost:3000"
```

:::info[Development Setup]
Development configuration uses:
- **PostgreSQL** or **SQLite** databases (your choice)
- **Console** email backend (emails print to console)
- **Localhost** domains for CORS
- All secrets in `.env` file (gitignored)
:::

  </TabItem>
  <TabItem value="prod" label="Production (ENV)">

```bash title="Production Environment Variables"
# Set in Docker/K8s/CI - NEVER in .env file!

# === Environment Mode ===
IS_PROD=true

# === Core Django Settings ===
SECRET_KEY="production-secret-key-from-secrets-manager-min-50-chars"
DEBUG=false

# === Database ===
DATABASE__URL="postgresql://prod-user:prod-pass@db.example.com:5432/prod_db"

# === Cache ===
REDIS_URL="redis://redis:6379/1"

# === Email Configuration ===
EMAIL__BACKEND="smtp"
EMAIL__HOST="smtp.sendgrid.net"
EMAIL__PORT=587
EMAIL__USERNAME="apikey"
EMAIL__PASSWORD="SG.xxxxxxxxxxxx"
EMAIL__USE_TLS=true
EMAIL__DEFAULT_FROM="My Project <noreply@myapp.com>"

# === Application URLs ===
APP__NAME="My Project"
APP__DOMAIN="myapp.com"
APP__API_URL="https://api.myapp.com"
APP__SITE_URL="https://myapp.com"

# === Security Domains ===
SECURITY_DOMAINS="myapp.com,api.myapp.com,admin.myapp.com"

# === Telegram ===
TELEGRAM__BOT_TOKEN="1234567890:ABCdefGHIjklMNOpqrsTUVwxyz"
TELEGRAM__CHAT_ID=-1001234567890

# === API Keys ===
API_KEYS__OPENROUTER="sk-or-xxx"
API_KEYS__OPENAI="sk-proj-xxx"
```

:::danger[Production Secrets]
**Critical:** Production configuration must use environment variables for all secrets:
- Set in Docker environment variables
- Use Kubernetes Secrets
- Use AWS Secrets Manager / HashiCorp Vault
- **NEVER** commit to git!
:::

  </TabItem>
  <TabItem value="example" label=".env.example">

```bash title="environment/.env.example"
# Django-CFG Environment Variables - Example
# Copy this file to .env and fill in your values
# Priority: ENV variables > .env file > defaults in code

# === Environment Mode ===
# IS_DEV=true
# IS_PROD=false
# IS_TEST=false

# === Core Django Settings ===
# SECRET_KEY="your-secret-key-minimum-50-characters-long"
# DEBUG=true

# === Database ===
DATABASE__URL="postgresql://postgres:postgres@localhost:5432/djangocfg"

# === Cache (optional) ===
# REDIS_URL="redis://localhost:6379/0"

# === Email Configuration ===
EMAIL__BACKEND="smtp"
EMAIL__HOST="smtp.example.com"
EMAIL__PORT=587
EMAIL__USERNAME="your-email@example.com"
EMAIL__PASSWORD="your-password"
EMAIL__USE_TLS=true
EMAIL__DEFAULT_FROM="noreply@example.com"

# === Telegram (optional) ===
TELEGRAM__BOT_TOKEN="your-telegram-bot-token"
TELEGRAM__CHAT_ID=0

# === API Keys (optional) ===
API_KEYS__OPENROUTER="your-openrouter-api-key"
API_KEYS__OPENAI="your-openai-api-key"

# === Application URLs (optional) ===
# APP__DOMAIN="localhost"
# APP__API_URL="http://localhost:8000"
# APP__SITE_URL="http://localhost:3000"

# === Admin Configuration (optional) ===
# ADMIN_EMAILS="admin@example.com,admin2@example.com"

# === Security Domains (optional) ===
# SECURITY_DOMAINS="localhost,127.0.0.1,example.com"
```

:::tip[Team Onboarding]
Commit `.env.example` to git as a template for your team. Each developer copies it to `.env` and fills in their values.
:::

  </TabItem>
</Tabs>

### 5. Use in config.py

```python
# config.py
from typing import Dict
from django_cfg import DjangoConfig, DatabaseConfig, EmailConfig, TelegramConfig

# Import environment configuration
from .environment import env


class MyProjectConfig(DjangoConfig):
    """Project configuration using environment variables."""

    # Core settings from ENV
    secret_key: str = env.secret_key
    debug: bool = env.debug
    env_mode: str = env.env.env_mode

    # Project info
    project_name: str = env.app.name
    project_logo: str = env.app.logo_url

    # URLs from ENV
    site_url: str = env.app.site_url
    api_url: str = env.app.api_url

    # Security domains from ENV
    security_domains: list[str] = env.security_domains or []

    # Database from ENV URL
    databases: Dict[str, DatabaseConfig] = {
        "default": DatabaseConfig.from_url(url=env.database.url),
    }

    # Email from ENV
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

    # Telegram from ENV
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

Uses: Defaults + `.env` file

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

Uses: System ENV variables (no .env file!)

:::warning[Production Checklist]
Before deploying to production:
- ✅ Set `IS_PROD=true`
- ✅ Configure all environment variables
- ✅ Set `DEBUG=false`
- ✅ Use PostgreSQL (not SQLite)
- ✅ Set up reverse proxy for SSL/TLS
- ✅ Configure `SECURITY_DOMAINS`
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

Uses: Defaults optimized for testing

:::tip[CI/CD Integration]
Most CI/CD systems work seamlessly with environment variables. Set `IS_TEST=true` in your CI config.
:::

  </TabItem>
</Tabs>

## ENV Variable Notation

Use **double underscore (`__`)** to access nested configurations:

```bash
# Flat config
DEBUG=true
SECRET_KEY="my-secret-key"

# Nested: email.host
EMAIL__HOST=smtp.gmail.com

# Nested: database.url
DATABASE__URL=postgresql://user:pass@localhost:5432/db

# Nested: api_keys.openai
API_KEYS__OPENAI=sk-proj-xxx
```

## DatabaseConfig.from_url()

Django-CFG provides `from_url()` to create database configurations from URLs:

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
Follow these patterns to ensure secure, maintainable configuration.
:::

<details>
  <summary>1. Never Commit Secrets</summary>

**❌ Wrong - Secrets in .env committed to git:**
```bash title=".env (INSECURE - committed to git)"
SECRET_KEY="actual-secret-key-abc123"  # ❌ NEVER DO THIS
DATABASE__URL="postgresql://user:realpassword@db.com/prod"  # ❌ EXPOSED
```

**✅ Correct - Use .gitignore:**
```bash title=".gitignore"
# Ignore .env file with secrets
.env
.env.local
environment/.env

# Keep .env.example for team
!.env.example
!environment/.env.example
```

**✅ Correct - Production uses system ENV:**
```bash
# Set in Docker/K8s - never in files
export SECRET_KEY="from-secrets-manager"
export DATABASE__URL="postgresql://..."
```

:::danger[Secret Exposure Risk]
Secrets committed to git can be:
- Leaked through GitHub/GitLab search
- Found in git history (even after deletion)
- Exposed in forks and mirrors
:::

</details>

<details>
  <summary>2. Use .env for Development Only</summary>

```bash
# Development (local) - use .env file
.env  # gitignored, safe for local secrets

# Production - use system ENV variables
Docker environment variables
Kubernetes Secrets
AWS Secrets Manager
HashiCorp Vault
```

**Never use .env files in production!**

</details>

<details>
  <summary>3. Validate Configuration Early</summary>

```python
# Pydantic validates automatically at startup
from api.environment import env

# This will fail fast if invalid
print(env.database.url)  # ✅ Validated

# Add custom validation if needed
if env.env.is_prod:
    assert len(env.secret_key) >= 50, "Secret key too short!"
    assert not env.debug, "DEBUG must be False in production!"
```

:::info[Fail-Fast Validation]
Pydantic validates configuration at startup, catching errors **before** they reach production.
:::

</details>

<details>
  <summary>4. Environment-Specific Defaults</summary>

```python
# Good defaults in code
class DatabaseConfig(BaseSettings):
    url: str = Field(
        # SQLite for dev, override for prod
        default="sqlite:///db/default.sqlite3"
    )

class EmailConfig(BaseSettings):
    backend: str = Field(
        # Console for dev, override for prod
        default="console"
    )
```

**Benefits:**
- Minimal configuration needed for development
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
python manage.py check

# Show current configuration
python manage.py show_config

# Check Django settings
python manage.py check_settings
```

## Troubleshooting

### ENV Variables Not Loading

**Check:**
1. `.env` file location (should be in `environment/` folder)
2. Variable naming (use `__` for nesting)
3. Case sensitivity (should be case-insensitive)

```python
# Debug what's loaded
from api.environment import env

print(f"Database URL: {env.database.url}")
print(f"Environment: {env.env.env_mode}")
```

### Pydantic Validation Error

```
pydantic_core.ValidationError: 1 validation error for EnvironmentConfig
email.port
  Input should be a valid integer [type=int_type]
```

**Solution:** Check type in .env file:
```bash
# ❌ Wrong
EMAIL__PORT=abc

# ✅ Correct
EMAIL__PORT=587
```

### Database URL Parse Error

```
ValueError: Invalid database URL format
```

**Solution:** Check URL format:
```bash
# ✅ Correct formats:
DATABASE__URL="postgresql://user:pass@localhost:5432/db"
DATABASE__URL="mysql://root:pass@127.0.0.1:3306/db"
DATABASE__URL="sqlite:///db.sqlite3"  # 3 slashes!
```

## Next Steps

- [Multi-Database Setup](/guides/multi-database) - Advanced database routing
- [Production Deployment](/guides/docker/overview) - Production configuration
- [Environment Management](/fundamentals/configuration/environment) - Detailed environment guide

TAGS: configuration, pydantic-settings, environment, django-cfg
DEPENDS_ON: [installation, intro]
USED_BY: [first-project, multi-database]
