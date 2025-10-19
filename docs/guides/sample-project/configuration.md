---
title: Configuration Setup
description: Complete guide to type-safe configuration management in the Django-CFG sample project
sidebar_label: Configuration
sidebar_position: 3
---

# Configuration Setup

The Django-CFG sample project demonstrates best practices for configuration management using Pydantic v2 for type-safe settings. This guide covers the complete configuration architecture.

## Configuration Architecture

The sample project uses a layered configuration approach:

1. **Type-safe Configuration** (`api/config.py`) - Main configuration class
2. **Environment Files** (`api/environment/*.yaml`) - Environment-specific settings
3. **Environment Variables** - Runtime overrides
4. **Configuration Loader** (`api/environment/loader.py`) - Loads and merges configs

## Main Configuration (api/config.py)

The heart of the project is the type-safe configuration class:

```python
from django_cfg import (
    DjangoConfig, env,
    DatabaseConfig, EmailConfig, TwilioConfig,
    TelegramConfig, UnfoldConfig, DRFConfig
)
from typing import Dict

class SampleProjectConfig(DjangoConfig):
    """Complete Django-CFG sample configuration."""

    # Project metadata
    project_name: str = "Django CFG Sample"
    debug: bool = env.debug
    secret_key: str = env.secret_key

    # Multi-database configuration
    databases: Dict[str, DatabaseConfig] = {
        "default": DatabaseConfig(
            engine="django.db.backends.sqlite3",
            name="db/db.sqlite3",
            # Main database for users, sessions, admin
        ),
        "blog_db": DatabaseConfig(
            engine="django.db.backends.sqlite3",
            name="db/blog.sqlite3",
            # Routed database for blog app
            apps=["apps.blog"],
            operations=["read", "write"],
            migrate_to="default",  # Migrations go to main DB
        ),
        "shop_db": DatabaseConfig(
            engine="django.db.backends.sqlite3",
            name="db/shop.sqlite3",
            # Routed database for shop app
            apps=["apps.shop"],
            operations=["read", "write", "migrate"],
        )
    }

    # Email configuration
    email: EmailConfig = EmailConfig(
        backend="sendgrid" if env.is_prod else "console",
        sendgrid_api_key=env.email.sendgrid_api_key,
        from_email="noreply@djangocfg.com",
        from_name="Django-CFG Sample"
    )

    # Twilio integration
    twilio: TwilioConfig = TwilioConfig(
        account_sid=env.twilio.account_sid,
        auth_token=env.twilio.auth_token,
        verify_service_sid=env.twilio.verify_service_sid,
        phone_number=env.twilio.phone_number
    )

    # Telegram notifications
    telegram: TelegramConfig = TelegramConfig(
        bot_token=env.telegram.bot_token,
        chat_id=env.telegram.chat_id,
        enabled=env.is_prod
    )

    # Modern admin interface
    unfold: UnfoldConfig = UnfoldConfig(
        site_title="Django-CFG Sample Admin",
        site_header="Django-CFG Sample",
        dashboard_callback="api.config.dashboard_callback",
        navigation=[
            {
                "title": "Content Management",
                "items": [
                    {"title": "Blog Posts", "link": "/admin/blog/post/"},
                    {"title": "Comments", "link": "/admin/blog/comment/"},
                ]
            },
            {
                "title": "E-Commerce",
                "items": [
                    {"title": "Products", "link": "/admin/shop/product/"},
                    {"title": "Orders", "link": "/admin/shop/order/"},
                ]
            },
            {
                "title": "User Management",
                "items": [
                    {"title": "Users", "link": "/admin/auth/user/"},
                    {"title": "Profiles", "link": "/admin/profiles/profile/"},
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

Basic project information:

```python
project_name: str = "Django CFG Sample"
debug: bool = env.debug  # From environment
secret_key: str = env.secret_key  # From environment
```

#### Database Configuration

Multi-database setup with routing:

```python
databases: Dict[str, DatabaseConfig] = {
    "default": DatabaseConfig(
        engine="django.db.backends.sqlite3",
        name="db/db.sqlite3",
    ),
    "blog_db": DatabaseConfig(
        engine="django.db.backends.sqlite3",
        name="db/blog.sqlite3",
        apps=["apps.blog"],  # Apps using this database
        operations=["read", "write"],  # Allowed operations
        migrate_to="default",  # Where migrations are stored
    ),
}
```

See [Multi-Database Setup](./multi-database) for detailed routing configuration.

#### Service Configurations

Email, SMS, and notification services:

```python
# Email (SendGrid or console)
email: EmailConfig = EmailConfig(
    backend="sendgrid" if env.is_prod else "console",
    sendgrid_api_key=env.email.sendgrid_api_key,
    from_email="noreply@djangocfg.com",
)

# SMS (Twilio)
twilio: TwilioConfig = TwilioConfig(
    account_sid=env.twilio.account_sid,
    auth_token=env.twilio.auth_token,
)

# Notifications (Telegram)
telegram: TelegramConfig = TelegramConfig(
    bot_token=env.telegram.bot_token,
    enabled=env.is_prod,
)
```

See [Service Integrations](./service-integrations) for service setup details.

#### Admin Interface Configuration

Unfold theme customization:

```python
unfold: UnfoldConfig = UnfoldConfig(
    site_title="Django-CFG Sample Admin",
    site_header="Django-CFG Sample",
    dashboard_callback="api.config.dashboard_callback",
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

### Development Configuration (config.dev.yaml)

Development-specific settings optimized for local development:

```yaml
# Development configuration
secret_key: "django-cfg-sample-dev-key-change-in-production"
debug: true
is_prod: false

# Database URLs
database:
  url: "sqlite:///db/db.sqlite3"
  url_blog: "sqlite:///db/blog.sqlite3"
  url_shop: "sqlite:///db/shop.sqlite3"

# Application settings
app:
  name: "Django CFG Sample"
  domain: "localhost:8000"

security_domains: ["localhost", "127.0.0.1"]

# Email configuration (development)
email:
  sendgrid_api_key: ""  # Empty for console backend

# Twilio configuration (optional in dev)
twilio:
  account_sid: ""
  auth_token: ""
  verify_service_sid: ""
  phone_number: ""

# Telegram configuration (optional in dev)
telegram:
  bot_token: ""
  chat_id: ""

# Cache configuration
cache:
  backend: "django.core.cache.backends.locmem.LocMemCache"
  location: "sample-cache"

# Static files
static:
  url: "/static/"
  root: "static/"

# Media files
media:
  url: "/media/"
  root: "media/"

# Logging
logging:
  level: "DEBUG"
  format: "verbose"
```

### Production Configuration (config.prod.yaml)

Production-ready settings with security hardening:

```yaml
# Production configuration
secret_key: "<from-yaml-config>"  # Set via environment/config.yaml
debug: false
is_prod: true

# Database configuration (PostgreSQL)
database:
  url: "postgresql://${DB_USER}:${DB_PASSWORD}@${DB_HOST}:${DB_PORT}/${DB_NAME}"

# Application settings
app:
  name: "Django CFG Sample"
  domain: "<from-yaml-config>"  # Set via environment/config.yaml

security_domains: ["<from-yaml-config>", "www.${DOMAIN}"]

# Email configuration (SendGrid)
email:
  sendgrid_api_key: "<from-yaml-config>"  # Set via environment/config.yaml
  from_email: "noreply@${DOMAIN}"

# Twilio configuration
twilio:
  account_sid: "<from-yaml-config>"
  auth_token: "<from-yaml-config>"
  verify_service_sid: "<from-yaml-config>"

# Telegram configuration
telegram:
  bot_token: "<from-yaml-config>"
  chat_id: "<from-yaml-config>"

# Cache configuration (Redis)
cache:
  backend: "django_redis.cache.RedisCache"
  location: "redis://redis:6379/1"

# Static files (served by nginx)
static:
  url: "/static/"
  root: "/app/static/"

# Media files (served by nginx)
media:
  url: "/media/"
  root: "/app/media/"

# Security settings
# Note: SSL/TLS handled by reverse proxy (nginx, Cloudflare, etc.)
# secure_ssl_redirect not needed - Django-CFG defaults to reverse proxy mode
security:
  session_cookie_secure: true
  csrf_cookie_secure: true
  secure_browser_xss_filter: true
  secure_content_type_nosniff: true

# Logging
logging:
  level: "INFO"
  format: "json"
```

### Test Configuration (config.test.yaml)

Optimized for fast test execution:

```yaml
# Test configuration
debug: true
is_prod: false

# In-memory database for fast tests
database:
  url: "sqlite:///:memory:"

# Disable external services
email:
  backend: "locmem"
  sendgrid_api_key: ""

twilio:
  account_sid: ""
  auth_token: ""

telegram:
  bot_token: ""
  enabled: false

# Simple cache
cache:
  backend: "django.core.cache.backends.locmem.LocMemCache"
  location: "test-cache"

# Logging
logging:
  level: "WARNING"
```

## Configuration Loader

The loader merges configuration from multiple sources:

```python
# api/environment/loader.py
import os
import yaml
from pathlib import Path
from typing import Dict, Any

def load_environment_config() -> Dict[str, Any]:
    """Load configuration from environment-specific YAML file."""

    # Determine environment
    env = os.getenv("DJANGO_ENV", "dev")

    # Load config file
    config_file = Path(__file__).parent / f"config.{env}.yaml"

    if not config_file.exists():
        raise FileNotFoundError(f"Config file not found: {config_file}")

    with open(config_file, 'r') as f:
        config = yaml.safe_load(f)

    # Override with environment variables
    config = apply_environment_overrides(config)

    return config

def apply_environment_overrides(config: Dict[str, Any]) -> Dict[str, Any]:
    """Override config values with environment variables."""

    # Example: Override secret key
    if secret_key := os.getenv("SECRET_KEY"):
        config["secret_key"] = secret_key

    # Example: Override database URL
    if db_url := os.getenv("DATABASE_URL"):
        config["database"]["url"] = db_url

    # Override SendGrid API key
    if sendgrid_key := os.getenv("SENDGRID_API_KEY"):
        config["email"]["sendgrid_api_key"] = sendgrid_key

    return config
```

## Environment Variables

Override configuration at runtime:

```bash
# Basic settings
export SECRET_KEY="production-secret-key"
export DEBUG=false
export DJANGO_ENV=prod

# Database
export DATABASE_URL="postgresql://user:pass@localhost/db"

# Email
export SENDGRID_API_KEY="SG.xxxxxxxxxxxxx"

# Twilio
export TWILIO_ACCOUNT_SID="ACxxxxxxxxxxxxx"
export TWILIO_AUTH_TOKEN="your-auth-token"

# Telegram
export TELEGRAM_BOT_TOKEN="123456:ABC-DEF"
export TELEGRAM_CHAT_ID="@your-channel"
```

## Dashboard Callback Configuration

Custom dashboard metrics function:

```python
# api/config.py

def dashboard_callback(request, context):
    """Custom dashboard with real-time metrics."""
    from apps.blog.models import Post
    from apps.shop.models import Product, Order
    from django.contrib.auth import get_user_model
    from django.utils import timezone
    from datetime import timedelta

    User = get_user_model()

    # Calculate metrics
    total_users = User.objects.count()
    total_posts = Post.objects.count()
    total_products = Product.objects.count()
    recent_orders = Order.objects.filter(
        created_at__gte=timezone.now() - timedelta(days=7)
    ).count()

    # Add custom cards to dashboard
    custom_cards = [
        {
            "title": "Total Users",
            "value": str(total_users),
            "description": "Registered users",
            "icon": "people"
        },
        {
            "title": "Blog Posts",
            "value": str(total_posts),
            "description": "Published articles",
            "icon": "article"
        },
        {
            "title": "Products",
            "value": str(total_products),
            "description": "Available products",
            "icon": "inventory"
        },
        {
            "title": "Orders (7d)",
            "value": str(recent_orders),
            "description": "Recent orders",
            "icon": "shopping_cart"
        }
    ]

    context["cards"].extend(custom_cards)
    return context
```

## Configuration Best Practices

### 1. Use Type-Safe Configuration

Always define configuration in type-safe classes:

```python
# ✅ Good: Type-safe with validation
class MyConfig(DjangoConfig):
    email: EmailConfig = EmailConfig(
        backend="sendgrid",
        sendgrid_api_key=env.email.sendgrid_api_key
    )

# ❌ Bad: Raw dictionary
settings = {
    "email_backend": "sendgrid",
    "sendgrid_key": "xxx"
}
```

### 2. Environment-Specific Settings

Keep environment-specific settings in YAML files:

```python
# ✅ Good: Environment-specific files
# config.dev.yaml - Development
# config.prod.yaml - Production
# config.test.yaml - Testing

# ❌ Bad: Inline conditions
if DEBUG:
    EMAIL_BACKEND = 'console'
else:
    EMAIL_BACKEND = 'sendgrid'
```

### 3. Sensitive Data Management

Never commit sensitive data to version control:

```yaml
# ✅ Good: Use environment variables
email:
  sendgrid_api_key: "<from-yaml-config>"  # Loaded from secure source

# ❌ Bad: Hard-coded secrets
email:
  sendgrid_api_key: "SG.xxxxxxxxxxxxx"  # Never commit this!
```

### 4. Configuration Documentation

Document all configuration options:

```python
class MyConfig(DjangoConfig):
    """Project configuration.

    Attributes:
        project_name: Display name for the project
        debug: Enable debug mode (development only)
        databases: Multi-database configuration with routing
        email: Email service configuration (SendGrid or console)
    """
    project_name: str
    debug: bool
    databases: Dict[str, DatabaseConfig]
    email: EmailConfig
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
email_backend = config.email.backend
twilio_sid = config.twilio.account_sid

# Access database configs
databases = config.databases
```

## Configuration Commands

Check your configuration:

```bash
# Show all configuration
poetry run cli show-config

# Show specific section
poetry run cli show-config --section databases
poetry run cli show-config --section email

# Validate configuration
poetry run cli validate-config
```

## Related Topics

- [Multi-Database Setup](./multi-database) - Database routing configuration
- [Admin Interface](./admin-interface) - Admin customization settings
- [Service Integrations](./service-integrations) - Service configuration details
- [Deployment Guide](./deployment) - Production configuration

Proper configuration management is essential for maintainable Django-CFG applications!
