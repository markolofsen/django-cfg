---
title: Configuration Setup
description: Complete guide to type-safe configuration management in the Django-CFG sample project
sidebar_label: Configuration
sidebar_position: 3
---

# Configuration Setup

The Django-CFG sample project demonstrates best practices for configuration management using **pydantic-settings** for type-safe environment-based configuration. This guide covers the complete configuration architecture.

## Configuration Architecture

The sample project uses a simple, modern configuration approach:

1. **Type-safe Configuration** (`api/config.py`) - Main configuration class
2. **Environment Loader** (`api/environment/loader.py`) - Pydantic models with BaseSettings
3. **Environment Variables** - System ENV or `.env` file
4. **Django Integration** - Seamless settings generation

**Priority**: System ENV > .env file > Code defaults

## Main Configuration (api/config.py)

The heart of the project is the type-safe configuration class:

```python
from django_cfg import (
    DjangoConfig,
    DatabaseConfig, EmailConfig,
    TelegramConfig, UnfoldConfig, DRFConfig
)
from typing import Dict
from .environment import env


class SampleProjectConfig(DjangoConfig):
    """Complete Django-CFG sample configuration."""

    # Project metadata
    project_name: str = env.app.name
    debug: bool = env.debug
    secret_key: str = env.secret_key
    env_mode: str = env.env.env_mode

    # Multi-database configuration
    databases: Dict[str, DatabaseConfig] = {
        "default": DatabaseConfig.from_url(
            url=env.database.url,
            # Main database for users, sessions, admin
        ),
    }

    # Email configuration
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

    # Telegram notifications
    telegram: TelegramConfig | None = (
        TelegramConfig(
            bot_token=env.telegram.bot_token,
            chat_id=env.telegram.chat_id,
        )
        if env.telegram.bot_token and env.telegram.chat_id
        else None
    )

    # Modern admin interface
    unfold: UnfoldConfig = UnfoldConfig(
        site_title="Django-CFG Sample Admin",
        site_header="Django-CFG Sample",
        navigation=[
            {
                "title": "Content Management",
                "items": [
                    {"title": "Profiles", "link": "/admin/profiles/profile/"},
                ]
            },
            {
                "title": "User Management",
                "items": [
                    {"title": "Users", "link": "/admin/auth/user/"},
                ]
            }
        ]
    )

    # API configuration
    drf: DRFConfig = DRFConfig(
        default_authentication_classes=[
            "rest_framework_simplejwt.authentication.JWTAuthentication",
        ],
        default_permission_classes=[
            "rest_framework.permissions.IsAuthenticated",
        ],
        spectacular_settings={
            "TITLE": "Django-CFG Sample API",
            "DESCRIPTION": "Complete API for Django-CFG sample project",
            "VERSION": "1.0.0",
            "SERVE_INCLUDE_SCHEMA": False,
        }
    )


# Create global config instance
config = SampleProjectConfig()
```

### Configuration Components

#### Project Metadata

Basic project information loaded from environment:

```python
project_name: str = env.app.name  # From APP__NAME
debug: bool = env.debug  # From DEBUG
secret_key: str = env.secret_key  # From SECRET_KEY
env_mode: str = env.env.env_mode  # "development", "production", or "test"
```

#### Database Configuration

Database setup using environment URL:

```python
databases: Dict[str, DatabaseConfig] = {
    "default": DatabaseConfig.from_url(
        url=env.database.url,  # From DATABASE__URL
    ),
}
```

Set via environment:
```bash
DATABASE__URL="postgresql://user:pass@localhost:5432/djangocfg"
```

See [Multi-Database Setup](./multi-database) for detailed routing configuration.

#### Service Configurations

Email and notification services from environment:

```python
# Email (console for dev, SMTP for prod)
email: EmailConfig | None = (
    EmailConfig(
        host=env.email.host,  # From EMAIL__HOST
        port=env.email.port,  # From EMAIL__PORT
        use_tls=env.email.use_tls,  # From EMAIL__USE_TLS
        username=env.email.username,  # From EMAIL__USERNAME
        password=env.email.password,  # From EMAIL__PASSWORD
    )
    if env.email.host
    else None
)

# Notifications (Telegram)
telegram: TelegramConfig | None = (
    TelegramConfig(
        bot_token=env.telegram.bot_token,  # From TELEGRAM__BOT_TOKEN
        chat_id=env.telegram.chat_id,  # From TELEGRAM__CHAT_ID
    )
    if env.telegram.bot_token
    else None
)
```

Set via environment:
```bash
EMAIL__HOST="smtp.gmail.com"
EMAIL__PORT=587
TELEGRAM__BOT_TOKEN="123456:ABC-DEF"
TELEGRAM__CHAT_ID=-1001234567890
```

See [Service Integrations](./service-integrations) for service setup details.

#### Admin Interface Configuration

Unfold theme customization:

```python
unfold: UnfoldConfig = UnfoldConfig(
    site_title="Django-CFG Sample Admin",
    navigation=[...],
)
```

See [Admin Interface](./admin-interface) for customization options.

#### API Configuration

Django REST Framework settings:

```python
drf: DRFConfig = DRFConfig(
    default_authentication_classes=[
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ],
    spectacular_settings={
        "TITLE": "Django-CFG Sample API",
        "VERSION": "1.0.0",
    }
)
```

See [API Documentation](./api-documentation) for API configuration.

## Environment Configuration

### Development Configuration (.env)

Development-specific settings in `.env` file (gitignored):

```bash title="api/environment/.env"
# === Environment Mode ===
IS_DEV=true

# === Core Django Settings ===
SECRET_KEY="django-cfg-dev-key-change-in-production-min-50-chars"
DEBUG=true

# === Database ===
DATABASE__URL="postgresql://postgres:postgres@localhost:5432/djangocfg"

# === Cache ===
REDIS_URL="redis://localhost:6379/0"

# === Email Configuration ===
EMAIL__BACKEND="console"
EMAIL__DEFAULT_FROM="Django CFG Sample <noreply@localhost.dev>"

# === Telegram (optional) ===
# TELEGRAM__BOT_TOKEN="your-bot-token"
# TELEGRAM__CHAT_ID=0

# === API Keys (optional) ===
# API_KEYS__OPENROUTER="sk-or-xxx"
# API_KEYS__OPENAI="sk-proj-xxx"

# === Application ===
APP__NAME="Django CFG Sample"
APP__API_URL="http://localhost:8000"
APP__SITE_URL="http://localhost:3000"
```

**Benefits for development:**
- ✅ **Console** email backend (prints to terminal)
- ✅ **PostgreSQL** or **SQLite** (your choice)
- ✅ **Local** domains for CORS
- ✅ **Gitignored** - safe for local secrets

### Production Configuration (ENV)

Production uses system environment variables (Docker, K8s, etc.):

```bash title="Production Environment Variables"
# Set in Docker/K8s - NEVER in .env file!

# === Environment Mode ===
IS_PROD=true

# === Core Django Settings ===
SECRET_KEY="production-secret-key-from-secrets-manager-min-50-chars"
DEBUG=false

# === Database ===
DATABASE__URL="postgresql://prod_user:prod_pass@db.example.com:5432/prod_db"

# === Cache ===
REDIS_URL="redis://redis:6379/1"

# === Email Configuration ===
EMAIL__BACKEND="smtp"
EMAIL__HOST="smtp.sendgrid.net"
EMAIL__PORT=587
EMAIL__USERNAME="apikey"
EMAIL__PASSWORD="SG.xxxxxxxxxxxx"
EMAIL__USE_TLS=true
EMAIL__DEFAULT_FROM="Django CFG Sample <noreply@djangocfg.com>"

# === Application ===
APP__NAME="Django CFG Sample"
APP__DOMAIN="djangocfg.com"
APP__API_URL="https://api.djangocfg.com"
APP__SITE_URL="https://djangocfg.com"

# === Security Domains ===
SECURITY_DOMAINS="djangocfg.com,api.djangocfg.com,admin.djangocfg.com"

# === Telegram ===
TELEGRAM__BOT_TOKEN="1234567890:ABCdefGHIjklMNOpqrsTUVwxyz"
TELEGRAM__CHAT_ID=-1001234567890

# === API Keys ===
API_KEYS__OPENROUTER="sk-or-xxx"
API_KEYS__OPENAI="sk-proj-xxx"
```

**Security practices:**
- ✅ Use **secrets managers** (AWS Secrets Manager, Vault)
- ✅ Set in **Docker environment** or **K8s Secrets**
- ✅ **Never commit** to version control
- ✅ Rotate secrets regularly

### Test Configuration

Testing uses defaults optimized for speed:

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
TELEGRAM__BOT_TOKEN=""
API_KEYS__OPENROUTER=""
```

**Optimizations:**
- ✅ **In-memory SQLite** for fast tests
- ✅ **Console** email backend
- ✅ **Disabled** external services
- ✅ **Minimal** logging

## Configuration Loader

The environment loader uses pydantic-settings for automatic loading:

```python
# api/environment/loader.py
from pathlib import Path
from typing import Optional
from pydantic import Field, computed_field, model_validator
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
    username: Optional[str] = Field(default=None)
    password: Optional[str] = Field(default=None)
    use_tls: bool = Field(default=True)
    default_from: str = Field(default="noreply@example.com")

    model_config = SettingsConfigDict(
        env_prefix="EMAIL__",
        env_nested_delimiter="__",
    )


class EnvironmentMode(BaseSettings):
    """Environment mode detection."""
    is_test: bool = Field(default=False)
    is_dev: bool = Field(default=False)
    is_prod: bool = Field(default=False)

    @model_validator(mode="after")
    def set_default_env(self):
        if not any([self.is_test, self.is_dev, self.is_prod]):
            self.is_dev = True
        return self

    @computed_field
    @property
    def env_mode(self) -> str:
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
    secret_key: str = Field(
        default="django-cfg-dev-key-change-in-production-min-50-chars"
    )
    debug: bool = Field(default=True)

    database: DatabaseConfig = Field(default_factory=DatabaseConfig)
    email: EmailConfig = Field(default_factory=EmailConfig)
    env: EnvironmentMode = Field(default_factory=EnvironmentMode)

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

## Environment Variables

### Setting Environment Variables

**Development (local):**
```bash
# In .env file (gitignored)
DATABASE__URL="postgresql://localhost:5432/dev_db"
DEBUG=true
```

**Production (Docker):**
```yaml
# docker-compose.yml
services:
  django:
    environment:
      DATABASE__URL: "postgresql://prod-db:5432/db"
      SECRET_KEY: "${SECRET_KEY}"
      IS_PROD: "true"
```

**Production (Kubernetes):**
```yaml
# k8s-deployment.yaml
env:
  - name: DATABASE__URL
    valueFrom:
      secretKeyRef:
        name: django-secrets
        key: database-url
  - name: SECRET_KEY
    valueFrom:
      secretKeyRef:
        name: django-secrets
        key: secret-key
```

### Variable Naming

Use **double underscore (`__`)** for nested configurations:

```bash
# Top-level
DEBUG=true
SECRET_KEY="my-secret"

# Nested: database.url
DATABASE__URL="postgresql://..."

# Nested: email.host
EMAIL__HOST="smtp.gmail.com"

# Nested: api_keys.openai
API_KEYS__OPENAI="sk-proj-xxx"
```

## Configuration Best Practices

### 1. Use Type-Safe Configuration

Always define configuration in type-safe classes:

```python
# ✅ Good: Type-safe with validation
class MyConfig(DjangoConfig):
    email: EmailConfig = EmailConfig(
        host=env.email.host,
        port=env.email.port,
    )

# ❌ Bad: Raw dictionary
settings = {
    "email_host": "smtp.example.com",
    "email_port": 587
}
```

### 2. Environment-Specific Settings

Use environment variables for all environments:

```python
# ✅ Good: Environment variables
DATABASE__URL="postgresql://..." # Dev, prod, test

# ❌ Bad: Inline conditions
if DEBUG:
    DATABASE = 'sqlite:///db.sqlite3'
else:
    DATABASE = 'postgresql://...'
```

### 3. Sensitive Data Management

Never commit sensitive data:

```bash
# ✅ Good: In .env file (gitignored)
SECRET_KEY="my-secret-key-min-50-chars"
EMAIL__PASSWORD="my-password"

# ✅ Good: In .gitignore
.env
.env.local
environment/.env

# ❌ Bad: Hardcoded in code
SECRET_KEY = "hardcoded-secret"  # Never do this!
```

### 4. Configuration Documentation

Document all configuration options:

```python
class MyConfig(DjangoConfig):
    """Project configuration.

    Environment Variables:
        DEBUG: Enable debug mode (default: True)
        SECRET_KEY: Django secret key (required in production)
        DATABASE__URL: Database connection URL
        EMAIL__HOST: SMTP server hostname

    Example:
        export DEBUG=false
        export SECRET_KEY="prod-secret-key"
        export DATABASE__URL="postgresql://..."
    """
    debug: bool = env.debug
    secret_key: str = env.secret_key
```

## Accessing Configuration

Use the configuration instance throughout your project:

```python
# Import configuration
from api.config import config

# Access settings
project_name = config.project_name
is_debug = config.debug

# Access service configs
email_host = config.email.host if config.email else None
telegram_enabled = config.telegram is not None

# Access database configs
databases = config.databases
```

## Configuration Commands

Check your configuration:

```bash
# Show all configuration
python manage.py show_config

# Validate configuration
python manage.py check

# Check settings
python manage.py check_settings
```

## Migration from YAML

:::info[Migrating from YAML configs?]
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

```bash title=".env or system ENV"
SECRET_KEY="my-secret-key"
DEBUG=false
DATABASE__URL="postgresql://user:pass@localhost:5432/db"
EMAIL__BACKEND="smtp"
EMAIL__HOST="smtp.example.com"
```

**Benefits:**
- ✅ Simpler - one method for all environments
- ✅ 12-factor app compliant
- ✅ Works everywhere (Docker, K8s, CI/CD)
- ✅ No file management

## Related Topics

- [Multi-Database Setup](./multi-database) - Database routing configuration
- [Service Integrations](./service-integrations) - Service configuration details
- [Deployment Guide](./deployment) - Production configuration
- [Environment Configuration](/fundamentals/configuration/environment) - Detailed ENV guide

Proper configuration management is essential for maintainable Django-CFG applications!
