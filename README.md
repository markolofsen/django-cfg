# 🚀 Django-CFG: Developer-First Django Configuration

[![Python Version](https://img.shields.io/pypi/pyversions/django-cfg.svg)](https://pypi.org/project/django-cfg/)
[![Django Version](https://img.shields.io/pypi/djversions/django-cfg.svg)](https://pypi.org/project/django-cfg/)
[![License](https://img.shields.io/pypi/l/django-cfg.svg)](https://github.com/carapis/django-cfg/blob/main/LICENSE)
[![PyPI Version](https://img.shields.io/pypi/v/django-cfg.svg)](https://pypi.org/project/django-cfg/)
[![Test Coverage](https://img.shields.io/codecov/c/github/carapis/django-cfg.svg)](https://codecov.io/gh/carapis/django-cfg)

**Transform your Django configuration from 100+ lines of boilerplate to 10 lines of type-safe, intelligent configuration.**

Django-CFG is a revolutionary Django configuration system that provides developer-first experience through Pydantic v2 models, intelligent automation, and zero boilerplate configuration.

## ✨ Key Features

- 🎯 **90% Less Boilerplate** - Reduce settings.py from 100+ lines to <10 lines
- 🔒 **100% Type Safety** - All configuration through Pydantic v2 models  
- 🚫 **Zero Raw Dicts** - No more error-prone dictionary configurations
- 🧠 **Smart Defaults** - Environment-aware defaults (Redis for prod, Memory for dev)
- 💡 **IDE Support** - Full autocomplete and validation in your IDE
- 📦 **Easy Migration** - Gradual migration from existing Django projects

## 🚀 Quick Start

### Installation

```bash
# Basic installation
pip install django-cfg

# Full installation with all integrations
pip install django-cfg[full]
```

### Before (Traditional Django)

```python
# settings.py - 100+ lines of boilerplate 😢
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-key')
DEBUG = os.environ.get('DEBUG', 'False') == 'True'
ALLOWED_HOSTS = ['localhost', '127.0.0.1']

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'myapp',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DATABASE_NAME', 'mydb'),
        'USER': os.environ.get('DATABASE_USER', 'postgres'),
        'PASSWORD': os.environ.get('DATABASE_PASSWORD', ''),
        'HOST': os.environ.get('DATABASE_HOST', 'localhost'),
        'PORT': os.environ.get('DATABASE_PORT', '5432'),
    }
}

# ... 50+ more lines
```

### After (Django-CFG)

```python
# config.py - Clean, type-safe configuration 🎉
from django_cfg import DjangoConfig, DatabaseConnection

class MyProjectConfig(DjangoConfig):
    project_name: str = "My Project"
    project_apps: list = ["myapp"]
    
    secret_key: str = "${SECRET_KEY:dev-key}"
    debug: bool = "${DEBUG:False}"
    
    databases: dict = {
        "default": DatabaseConnection(
            engine="django.db.backends.postgresql",
            name="${DATABASE_NAME:mydb}",
            user="${DATABASE_USER:postgres}",
            password="${DATABASE_PASSWORD:}",
        )
    }

config = MyProjectConfig()
```

```python
# settings.py - Just 3 lines! 🔥
from myproject.config import config
globals().update(config.get_all_settings())
```

## 💡 What You Get Automatically

✅ **All standard Django apps and middleware configured**  
✅ **Environment detection (dev/prod/test/staging)**  
✅ **Smart cache backend selection (Redis for prod, Memory for dev)**  
✅ **Security settings based on your domains**  
✅ **Complete type safety and validation**  
✅ **IDE autocomplete for all configuration options**

## 🏗️ Advanced Examples

### Multi-Database E-commerce Platform

```python
from django_cfg import DjangoConfig, DatabaseConnection, DatabaseRoutingRule, CacheBackend

class EcommerceConfig(DjangoConfig):
    project_name: str = "E-commerce Platform"
    project_apps: list = ["products", "orders", "payments", "analytics"]
    
    # Multi-database setup
    databases: dict = {
        "default": DatabaseConnection(
            engine="django.db.backends.postgresql",
            name="${DATABASE_URL:ecommerce_main}",
        ),
        "products": DatabaseConnection(
            engine="django.db.backends.postgresql", 
            name="${DATABASE_URL_PRODUCTS:ecommerce_products}",
        ),
        "analytics": DatabaseConnection(
            engine="django.db.backends.postgresql",
            name="${DATABASE_URL_ANALYTICS:ecommerce_analytics}",
        ),
    }
    
    # Smart database routing
    database_routing: list = [
        DatabaseRoutingRule(
            apps=["products"],
            database="products",
            operations=["read", "write", "migrate"],
        ),
        DatabaseRoutingRule(
            apps=["analytics"],
            database="analytics", 
            operations=["read", "write"],
            migrate_to="default",
        ),
    ]
    
    # Multi-cache setup
    cache_default: CacheBackend = CacheBackend(
        redis_url="${REDIS_URL:redis://localhost:6379/1}",
        timeout=300,
    )
    
    cache_sessions: CacheBackend = CacheBackend(
        redis_url="${REDIS_URL:redis://localhost:6379/2}",
        timeout=86400,  # 24 hours
    )

config = EcommerceConfig()
```

### API-First Microservice

```python
from django_cfg import DjangoConfig, RevolutionConfig, APIZone

class UserServiceConfig(DjangoConfig):
    project_name: str = "User Service"
    project_apps: list = ["users", "profiles", "authentication"]
    
    # API-first configuration
    revolution: RevolutionConfig = RevolutionConfig(
        api_prefix="api/v1",
        zones={
            "public": APIZone(
                name="public",
                apps=["users"],
                public=True,
                auth_required=False,
            ),
            "admin": APIZone(
                name="admin", 
                apps=["profiles", "authentication"],
                public=False,
                auth_required=True,
            ),
        }
    )

config = UserServiceConfig()
```

## 🔧 Environment Intelligence

Django-CFG automatically detects your environment and applies appropriate settings:

| Environment | Cache Backend | Email Backend | Database SSL | Debug Mode |
|-------------|---------------|---------------|--------------|------------|
| **Development** | Memory Cache | Console | Optional | True |
| **Testing** | Dummy Cache | In-Memory | Disabled | False |
| **Staging** | Redis | SMTP | Required | False |
| **Production** | Redis | SMTP | Required | False |

## 📊 Performance

Django-CFG is designed for performance:

- ⚡ **<100ms** configuration loading for complex setups
- 🧠 **<10MB** memory usage for typical configurations  
- 🔄 **Lazy loading** - only generates settings when needed
- 💾 **Caching** - settings cached after first generation

## 🔄 Migration Guide

Migrating from traditional Django is easy:

### Step 1: Install django-cfg
```bash
pip install django-cfg
```

### Step 2: Create config.py
```python
from django_cfg import DjangoConfig, DatabaseConnection

class MyProjectConfig(DjangoConfig):
    project_name: str = "My Project"
    project_apps: list = ["myapp"]  # Your existing apps
    
    secret_key: str = "${SECRET_KEY}"
    debug: bool = "${DEBUG:False}"
    
    databases: dict = {
        "default": DatabaseConnection(
            engine="django.db.backends.postgresql",
            name="${DATABASE_NAME}",
            # ... your existing database config
        )
    }

config = MyProjectConfig()
```

### Step 3: Update settings.py
```python
from myproject.config import config
globals().update(config.get_all_settings())
```

### Step 4: Test and iterate
```bash
python manage.py check
python manage.py runserver
```

## 🧪 Testing

Django-CFG includes comprehensive testing utilities:

```python
# Test your configuration
def test_my_config():
    config = MyProjectConfig()
    settings = config.get_all_settings()
    
    assert "SECRET_KEY" in settings
    assert settings["DEBUG"] is False
    assert "myapp" in settings["INSTALLED_APPS"]
```

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### Development Setup

```bash
git clone https://github.com/unrealos/django-cfg.git
cd django-cfg
poetry install
poetry run pytest
```

## 📚 Documentation

- **[Full Documentation](https://django-cfg.readthedocs.io)**
- **[API Reference](https://django-cfg.readthedocs.io/en/latest/api/)**
- **[Migration Guide](https://django-cfg.readthedocs.io/en/latest/migration/)**
- **[Examples](https://django-cfg.readthedocs.io/en/latest/examples/)**

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Django** - The web framework for perfectionists with deadlines
- **Pydantic** - Data validation using Python type hints
- **FastAPI** - Inspiration for developer-first experience

---

**Made with ❤️ by the UnrealOS Team**

*Django-CFG: Because configuration should be simple, safe, and powerful.*
