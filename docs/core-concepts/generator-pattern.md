---
id: generator-pattern
slug: /core-concepts/generator-pattern
sidebar_position: 2
title: Generator Pattern
description: Complete guide to generator pattern in Django-CFG. Learn generator pattern with type-safe configuration, Pydantic validation, and production-ready patterns.
keywords: [generator, pattern, settings, orchestration, django]
---

# Generator Pattern in Django-CFG

The Generator Pattern in Django-CFG is responsible for transforming configuration models into complete Django settings dictionaries. This pattern ensures type-safe, validated, and consistent Django settings generation.

## Overview

Django-CFG uses specialized generator classes to convert Pydantic configuration models into Django-compatible settings. Each generator focuses on a specific aspect of Django configuration.

**Key Benefits:**
- **Separation of Concerns:** Each generator handles one category of settings
- **Type Safety:** Generators work with typed Pydantic models
- **Validation:** Settings validated before generation
- **Extensibility:** Easy to add custom generators
- **Testing:** Each generator independently testable

## Architecture

```
DjangoConfig (Pydantic Model)
        ↓
ConfigService (Facade)
        ↓
SettingsOrchestrator (Coordinator)
        ↓
Specialized Generators (Category-specific)
        ↓
Complete Django Settings Dict
```

## Core Components

### SettingsGenerator (Facade)

The main entry point for settings generation.

**Location:** `django_cfg.core.generation.generation`

```python
from django_cfg import DjangoConfig
from django_cfg.core.generation import SettingsGenerator

config = DjangoConfig(...)
settings = SettingsGenerator.generate(config)
```

**Responsibilities:**
- Provide simple facade API
- Delegate to SettingsOrchestrator
- Validate generated settings

### SettingsOrchestrator

Coordinates all specialized generators.

**Location:** `django_cfg.core.generation.orchestrator`

**Responsibilities:**
- Call generators in correct order
- Handle dependencies between settings
- Merge settings from all generators
- Validate final output
- Handle errors gracefully

**Generation Order:**

1. **Core Settings** - BASE_DIR, DEBUG, SECRET_KEY
2. **Template Settings** - TEMPLATES configuration
3. **Static Settings** - STATIC_URL, STATICFILES
4. **Database Settings** - DATABASES
5. **Cache Settings** - CACHES
6. **Security Settings** - ALLOWED_HOSTS, CORS, SSL
7. **Email Settings** - EMAIL_BACKEND
8. **Logging Settings** - LOGGING
9. **I18n Settings** - LANGUAGE_CODE, TIME_ZONE
10. **Limits Settings** - Upload limits
11. **Session Settings** - SESSION_ENGINE
12. **Third-Party Settings** - Unfold, Constance, etc.
13. **API Settings** - DRF, Spectacular, JWT
14. **Tasks Settings** - Dramatiq

## Specialized Generators

### Core Generators

#### CoreSettingsGenerator

Generates fundamental Django settings.

**Location:** `django_cfg.core.generation.core_generators.settings`

**Generates:**
- `BASE_DIR` - Project root directory
- `SECRET_KEY` - Django secret key
- `DEBUG` - Debug mode flag
- `INSTALLED_APPS` - Application list (via InstalledAppsBuilder)
- `MIDDLEWARE` - Middleware stack (via MiddlewareBuilder)
- `ROOT_URLCONF` - URL configuration
- `WSGI_APPLICATION` - WSGI app path
- `AUTH_USER_MODEL` - Custom user model

**Example Output:**
```python
{
    "BASE_DIR": Path("/path/to/project"),
    "SECRET_KEY": "your-secret-key",
    "DEBUG": False,
    "INSTALLED_APPS": [...],
    "MIDDLEWARE": [...],
    "ROOT_URLCONF": "myproject.urls",
    "WSGI_APPLICATION": "myproject.wsgi.application",
}
```

#### TemplateSettingsGenerator

Generates template configuration.

**Location:** `django_cfg.core.generation.core_generators.templates`

**Generates:**
- `TEMPLATES` - Template backend configuration
- Template directories
- Context processors
- Template options

**Example Output:**
```python
{
    "TEMPLATES": [
        {
            "BACKEND": "django.template.backends.django.DjangoTemplates",
            "DIRS": [BASE_DIR / "templates"],
            "APP_DIRS": True,
            "OPTIONS": {
                "context_processors": [
                    "django.template.context_processors.debug",
                    "django.template.context_processors.request",
                    "django.contrib.auth.context_processors.auth",
                    "django.contrib.messages.context_processors.messages",
                ],
            },
        }
    ]
}
```

#### StaticFilesGenerator

Generates static files configuration.

**Location:** `django_cfg.core.generation.core_generators.static`

**Generates:**
- `STATIC_URL` - Static files URL
- `STATIC_ROOT` - Static files collection directory
- `STATICFILES_DIRS` - Additional static directories
- `STATICFILES_STORAGE` - Storage backend (WhiteNoise)
- `WHITENOISE_*` - WhiteNoise configuration

**Example Output:**
```python
{
    "STATIC_URL": "/static/",
    "STATIC_ROOT": BASE_DIR / "staticfiles",
    "STATICFILES_STORAGE": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    "WHITENOISE_MANIFEST_STRICT": False,
}
```

### Data Generators

#### DatabaseSettingsGenerator

Generates database configuration from DatabaseConfig models.

**Location:** `django_cfg.core.generation.data_generators.database`

**Generates:**
- `DATABASES` - Database connections dictionary
- `DATABASE_ROUTERS` - Database routing (if configured)
- Connection options
- SSL/TLS settings

**Example Input:**
```python
databases = {
    "default": DatabaseConfig(
        engine="django.db.backends.postgresql",
        name="mydb",
        user="postgres",
        password="secret",
        host="localhost",
        port=5432,
    ),
    "analytics": DatabaseConfig(
        engine="django.db.backends.postgresql",
        name="analytics_db",
        migrate_to="default",  # Migrations go to default
    ),
}
```

**Example Output:**
```python
{
    "DATABASES": {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": "mydb",
            "USER": "postgres",
            "PASSWORD": "secret",
            "HOST": "localhost",
            "PORT": 5432,
        },
        "analytics": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": "analytics_db",
            "MIGRATE": False,  # Handled by router
        },
    },
    "DATABASE_ROUTERS": ["django_cfg.routing.DatabaseRouter"],
}
```

#### CacheSettingsGenerator

Generates cache configuration from CacheConfig models.

**Location:** `django_cfg.core.generation.data_generators.cache`

**Generates:**
- `CACHES` - Cache backends dictionary
- Session cache configuration
- Cache key prefixes
- Cache options

**Example Output:**
```python
{
    "CACHES": {
        "default": {
            "BACKEND": "django.core.cache.backends.redis.RedisCache",
            "LOCATION": "redis://localhost:6379/1",
            "OPTIONS": {
                "CLIENT_CLASS": "django_redis.client.DefaultClient",
            },
        },
        "sessions": {
            "BACKEND": "django.core.cache.backends.redis.RedisCache",
            "LOCATION": "redis://localhost:6379/2",
        },
    },
}
```

### Utility Generators

#### SecuritySettingsGenerator

Generates security-related settings.

**Location:** `django_cfg.core.generation.utility_generators.security`

**Generates:**
- `ALLOWED_HOSTS` - (via SecurityBuilder)
- `CORS_*` - CORS configuration
- `SECURE_*` - SSL/TLS settings
- `CSRF_*` - CSRF protection
- `SESSION_COOKIE_*` - Cookie security

**Example Output:**
```python
{
    "ALLOWED_HOSTS": ["example.com", "www.example.com"],
    "CORS_ALLOWED_ORIGINS": [
        "https://example.com",
        "https://www.example.com",
    ],
    "CORS_ALLOW_CREDENTIALS": True,
    "SECURE_SSL_REDIRECT": True,
    "SECURE_HSTS_SECONDS": 31536000,
    "SECURE_HSTS_INCLUDE_SUBDOMAINS": True,
    "SESSION_COOKIE_SECURE": True,
    "CSRF_COOKIE_SECURE": True,
}
```

#### EmailSettingsGenerator

Generates email configuration.

**Location:** `django_cfg.core.generation.utility_generators.email`

**Generates:**
- `EMAIL_BACKEND` - Email backend class
- `EMAIL_HOST` - SMTP server
- `EMAIL_PORT` - SMTP port
- `EMAIL_USE_TLS` - TLS configuration
- `EMAIL_HOST_USER` - SMTP username
- `EMAIL_HOST_PASSWORD` - SMTP password
- `DEFAULT_FROM_EMAIL` - Default sender

#### LoggingSettingsGenerator

Generates logging configuration.

**Location:** `django_cfg.core.generation.utility_generators.logging`

**Generates:**
- `LOGGING` - Complete logging dictionary
- Formatters
- Handlers
- Loggers
- Log levels

#### I18nSettingsGenerator

Generates internationalization settings.

**Location:** `django_cfg.core.generation.utility_generators.i18n`

**Generates:**
- `LANGUAGE_CODE` - Default language
- `TIME_ZONE` - Default timezone
- `USE_I18N` - Enable internationalization
- `USE_L10N` - Enable localization
- `USE_TZ` - Enable timezone support

#### LimitsSettingsGenerator

Generates application limit settings.

**Location:** `django_cfg.core.generation.utility_generators.limits`

**Generates:**
- `DATA_UPLOAD_MAX_MEMORY_SIZE` - Max upload size
- `FILE_UPLOAD_MAX_MEMORY_SIZE` - Max file size
- `DATA_UPLOAD_MAX_NUMBER_FIELDS` - Max form fields
- `FILE_UPLOAD_HANDLERS` - Upload handlers

### Integration Generators

#### SessionSettingsGenerator

Generates session configuration.

**Location:** `django_cfg.core.generation.integration_generators.sessions`

**Generates:**
- `SESSION_ENGINE` - Session backend
- `SESSION_CACHE_ALIAS` - Cache for sessions
- `SESSION_COOKIE_*` - Cookie settings

#### ThirdPartyIntegrationsGenerator

Generates third-party package settings.

**Location:** `django_cfg.core.generation.integration_generators.third_party`

**Generates:**
- `CONSTANCE_*` - django-constance settings
- `UNFOLD` - Unfold admin configuration
- `IMPORT_EXPORT_*` - django-import-export settings

#### APIFrameworksGenerator

Generates API framework settings.

**Location:** `django_cfg.core.generation.integration_generators.api`

**Generates:**
- `REST_FRAMEWORK` - DRF configuration
- `SPECTACULAR_SETTINGS` - drf-spectacular configuration
- `SIMPLE_JWT` - JWT authentication settings

#### TasksSettingsGenerator

Generates background task settings.

**Location:** `django_cfg.core.generation.integration_generators.tasks`

**Generates:**
- `DRAMATIQ_BROKER` - Task broker configuration
- `DRAMATIQ_RESULT_BACKEND` - Result storage
- `DRAMATIQ_TASKS_DATABASE` - Task database

## Creating Custom Generators

You can create custom generators for your own settings:

```python
from typing import Dict, Any, TYPE_CHECKING

if TYPE_CHECKING:
    from django_cfg.core.base.config_model import DjangoConfig


class CustomSettingsGenerator:
    """Generate custom application settings."""

    def __init__(self, config: "DjangoConfig"):
        self.config = config

    def generate(self) -> Dict[str, Any]:
        """
        Generate settings from configuration.

        Returns:
            Dictionary with Django settings
        """
        settings = {}

        # Your custom logic
        if hasattr(self.config, 'custom_feature'):
            settings["CUSTOM_FEATURE_ENABLED"] = self.config.custom_feature

        return settings
```

## Integration Example

Complete flow from config to settings:

```python
from django_cfg import DjangoConfig
from django_cfg.models import DatabaseConfig, CacheConfig

# 1. Define configuration
class MyProjectConfig(DjangoConfig):
    project_name = "My Project"
    secret_key = "your-secret-key"

    databases = {
        "default": DatabaseConfig(
            engine="django.db.backends.postgresql",
            name="mydb",
        )
    }

    cache_default = CacheConfig(
        backend="django.core.cache.backends.redis.RedisCache",
        location="redis://localhost:6379/1",
    )

# 2. Instantiate configuration
config = MyProjectConfig()

# 3. Generate settings (happens automatically in get_all_settings)
settings = config.get_all_settings()

# Behind the scenes:
# - SettingsGenerator.generate(config)
# - SettingsOrchestrator(config).generate()
# - Each specialized generator runs
# - Settings merged and returned
```

## Testing Generators

Generators are designed to be testable:

```python
import pytest
from django_cfg import DjangoConfig
from django_cfg.core.generation.core_generators.settings import CoreSettingsGenerator


def test_core_settings_generator():
    config = DjangoConfig(
        project_name="Test Project",
        secret_key="x" * 50,
        databases={"default": DatabaseConfig(...)},
    )

    generator = CoreSettingsGenerator(config)
    settings = generator.generate()

    assert "SECRET_KEY" in settings
    assert "DEBUG" in settings
    assert "INSTALLED_APPS" in settings
    assert settings["DEBUG"] == config.debug


def test_database_settings_generator():
    config = DjangoConfig(
        project_name="Test",
        secret_key="x" * 50,
        databases={
            "default": DatabaseConfig(
                engine="django.db.backends.sqlite3",
                name=":memory:",
            )
        },
    )

    from django_cfg.core.generation.data_generators.database import DatabaseSettingsGenerator

    generator = DatabaseSettingsGenerator(config)
    settings = generator.generate()

    assert "DATABASES" in settings
    assert "default" in settings["DATABASES"]
    assert settings["DATABASES"]["default"]["ENGINE"] == "django.db.backends.sqlite3"
```

## Best Practices

### 1. Single Responsibility
Each generator should focus on one category:
- ✅ `DatabaseSettingsGenerator` - only database settings
- ❌ Don't mix database + cache in one generator

### 2. No Side Effects
Generators should be pure functions:
```python
# ✅ Good - no side effects
def generate(self) -> Dict[str, Any]:
    return {"SETTING": self.config.value}

# ❌ Bad - side effects
def generate(self) -> Dict[str, Any]:
    self.config.value = "changed"  # Don't modify config!
    logging.info("Generating...")  # Avoid I/O if possible
    return {"SETTING": self.config.value}
```

### 3. Type Safety
Always use type hints:
```python
# ✅ Good
def generate(self) -> Dict[str, Any]:
    settings: Dict[str, Any] = {}
    return settings

# ❌ Bad
def generate(self):
    settings = {}
    return settings
```

### 4. Error Handling
Provide context in errors:
```python
from django_cfg.core.exceptions import ConfigurationError

try:
    value = self.config.required_field
except AttributeError:
    raise ConfigurationError(
        "Required field missing",
        context={"config": self.config.model_dump()},
        suggestions=["Add the required_field to your config"],
    )
```

## See Also

- [Builder Pattern](builder-pattern.md) - How components are built
- [Service Layer](service-layer.md) - How generators are orchestrated
- [Architecture](architecture.md) - Overall system architecture
- [Configuration](../fundamentals/configuration.md) - Configuration models
