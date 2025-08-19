# 🚀 Django-CFG: Developer-First Django Configuration

[![Python Version](https://img.shields.io/pypi/pyversions/django-cfg.svg)](https://pypi.org/project/django-cfg/)
[![Django Version](https://img.shields.io/pypi/djversions/django-cfg.svg)](https://pypi.org/project/django-cfg/)
[![License](https://img.shields.io/pypi/l/django-cfg.svg)](https://github.com/markolofsen/django-cfg/blob/main/LICENSE)
[![PyPI Version](https://img.shields.io/pypi/v/django-cfg.svg)](https://pypi.org/project/django-cfg/)

**Transform your Django configuration from 100+ lines of boilerplate to clean, type-safe YAML + Python configuration.**

Django-CFG is a revolutionary Django configuration system that provides developer-first experience through Pydantic v2 models, YAML configuration files, intelligent automation, and zero boilerplate.

## ✨ Key Features

- 🎯 **90% Less Boilerplate** - Replace massive `settings.py` with clean config classes
- 🔒 **100% Type Safety** - All configuration through Pydantic v2 models  
- 📄 **YAML Configuration** - Environment-specific settings in readable YAML files
- 🚫 **Zero Raw Dicts** - No more error-prone dictionary configurations
- 🧠 **Smart Defaults** - Environment-aware defaults (Redis for prod, Memory for dev)
- 💡 **IDE Support** - Full autocomplete and validation in your IDE
- 🎨 **Beautiful Admin** - Pre-configured Django Unfold with Tailwind CSS
- 🔄 **API Generation** - Automatic OpenAPI/Swagger with Django Revolution
- 📦 **Easy Migration** - Gradual migration from existing Django projects

## 🚀 Quick Start

### Installation

```bash
pip install django-cfg
```

### Before (Traditional Django - 100+ lines)

```python
# settings.py - Traditional Django configuration 😢
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
    'rest_framework',
    'drf_spectacular',
    'corsheaders',
    'myapp',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
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

CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': os.environ.get('REDIS_URL', 'redis://localhost:6379/1'),
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}

REST_FRAMEWORK = {
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20
}

SPECTACULAR_SETTINGS = {
    'TITLE': 'My API',
    'DESCRIPTION': 'My API description',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
}

# ... 50+ more lines of configuration
```

### After (Django-CFG - Clean & Simple)

#### 1. Environment Configuration (`config.dev.yaml`)

```yaml
# Development Environment Configuration
secret_key: "django-insecure-550e8400-e29b-41d4-a716-446655440000-dev-key"
debug: true

# Database
database:
  url: "postgresql://postgres:postgres@localhost:5432/myapp"
  url_analytics: "postgresql://postgres:postgres@localhost:5432/analytics"

# Application URLs
app:
  name: "MyApp"
  domain: "localhost"
  api_url: "http://localhost:8000"
  site_url: "http://localhost:3000"

# Email
email:
  backend: "smtp"
  host: "smtp.gmail.com"
  port: 587
  username: "hello@myapp.com"
  password: "app-password"
  use_tls: true
  default_from: "MyApp <hello@myapp.com>"

# Telegram Bot
telegram:
  bot_token: "your-bot-token"
  group_id: -123456789

# Cache
redis_url: "redis://localhost:6379/1"
```

#### 2. Application Configuration (`config.py`)

```python
from typing import List, Dict
from django_cfg import (
    DjangoConfig,
    DatabaseConnection,
    DatabaseRoutingRule,
    CacheBackend,
    UnfoldConfig,
    UnfoldTheme,
    RevolutionConfig,
    ZoneConfig,
    EmailConfig,
    TelegramConfig,
)
from .environment import env


class MyAppConfig(DjangoConfig):
    """🚀 Complete production-ready configuration using django_cfg"""

    # === Project Information ===
    project_name: str = "MyApp"
    project_version: str = "1.0.0"
    site_url: str = env.app.site_url
    api_url: str = env.app.api_url

    # === Core Settings (from YAML) ===
    secret_key: str = env.secret_key
    debug: bool = env.debug

    # === Security ===
    security_domains: List[str] = [
        "https://myapp.com",
        "https://api.myapp.com",
        "http://localhost:3000",  # Development
        "http://localhost:8000",
    ]

    # === Custom User Model ===
    auth_user_model: str = "accounts.CustomUser"

    # === Project Apps ===
    project_apps: List[str] = [
        "accounts",
        "products",
        "orders",
        "analytics",
    ]

    # === Multi-Database Setup ===
    databases: Dict[str, DatabaseConnection] = {
        "default": DatabaseConnection(
            engine="django.db.backends.postgresql",
            **env.database.parse_url(env.database.url),
            connect_timeout=10,
            sslmode="prefer",
        ),
        "analytics": DatabaseConnection(
            engine="django.db.backends.postgresql",
            **env.database.parse_url(env.database.url_analytics),
            connect_timeout=10,
            sslmode="prefer",
        ),
    }

    # === Database Routing ===
    database_routing: List[DatabaseRoutingRule] = [
        DatabaseRoutingRule(
            apps=["analytics"],
            database="analytics",
            operations=["read", "write"],
        ),
    ]

    # === Redis Cache ===
    cache_default: CacheBackend = CacheBackend(
        redis_url=env.redis_url,
        timeout=300,
    )

    cache_sessions: CacheBackend = CacheBackend(
        redis_url=env.redis_url.replace("/1", "/2"),
        timeout=1800,  # 30 minutes
    )

    # === Email Configuration ===
    email: EmailConfig = EmailConfig(
        host=env.email.host,
        port=env.email.port,
        username=env.email.username,
        password=env.email.password,
        use_tls=env.email.use_tls,
        default_from_email=env.email.default_from,
    )

    # === Telegram Notifications ===
    telegram: TelegramConfig = TelegramConfig(
        bot_token=env.telegram.bot_token,
        chat_id=env.telegram.group_id,
        parse_mode="HTML",
    )

    # === Beautiful Admin Interface ===
    unfold: UnfoldConfig = UnfoldConfig(
        theme=UnfoldTheme(
            site_title="MyApp Admin",
            site_header="MyApp",
            site_subheader="Management Dashboard",
            theme="auto",  # Auto light/dark theme
            dashboard_callback="myapp.dashboard.main_callback",
        ),
    )

    # === API Configuration with Revolution ===
    revolution: RevolutionConfig = RevolutionConfig(
        api_prefix="api",
        drf_title="MyApp API",
        drf_description="RESTful API with automatic OpenAPI generation",
        drf_version="1.0.0",
        zones={
            "public": ZoneConfig(
                apps=["products"],
                title="Public API",
                description="Public product catalog",
                public=True,
                auth_required=False,
            ),
            "client": ZoneConfig(
                apps=["accounts", "orders"],
                title="Client API",
                description="User accounts and orders",
                public=True,
                auth_required=True,
            ),
            "admin": ZoneConfig(
                apps=["analytics"],
                title="Admin API",
                description="Analytics and reporting",
                public=False,
                auth_required=True,
            ),
        },
    )


# Initialize configuration
config = MyAppConfig()
```

#### 3. Django Settings (`settings.py`) - Just 3 Lines!

```python
"""Ultra-minimal settings powered by django_cfg"""

from .config import config

# Apply ALL Django settings from django_cfg
globals().update(config.get_all_settings())
```

## 💡 What You Get Automatically

✅ **All Django core apps and middleware configured**  
✅ **Environment detection (dev/prod/test/staging)**  
✅ **Smart cache backend selection (Redis/Memory)**  
✅ **Security settings based on your domains**  
✅ **Complete type safety and validation**  
✅ **Beautiful Django Unfold admin with Tailwind CSS**  
✅ **Automatic OpenAPI/Swagger documentation**  
✅ **Multi-database routing**  
✅ **Session management**  
✅ **CORS configuration**  
✅ **Static files with WhiteNoise**  
✅ **Email and Telegram notifications**

## 🏗️ Real-World Production Example

Here's a complete configuration from CarAPIS - a production automotive platform:

```python
class CarAPISConfig(DjangoConfig):
    """🚀 CarAPIS Production Configuration"""

    project_name: str = "CarAPIS"
    project_version: str = "2.0.0"
    
    # === 4 Production Databases ===
    databases: Dict[str, DatabaseConnection] = {
        "default": DatabaseConnection(
            engine="django.db.backends.postgresql",
            **env.database.parse_url(env.database.url),
            connect_timeout=10,
            sslmode="prefer",
        ),
        "cars": DatabaseConnection(
            **env.database.parse_url(env.database.url_cars),
        ),
        "cars_new": DatabaseConnection(
            **env.database.parse_url(env.database.url_cars_new),
        ),
        "cars_server": DatabaseConnection(
            **env.database.parse_url(env.database.url_cars_server),
        ),
    }

    # === Smart Database Routing ===
    database_routing: List[DatabaseRoutingRule] = [
        DatabaseRoutingRule(
            apps=["parsers"],
            database="cars",
            operations=["read", "write"],
        ),
        DatabaseRoutingRule(
            apps=["customs"],
            database="cars_new",
            operations=["read", "write"],
        ),
    ]

    # === Multi-Zone API ===
    revolution: RevolutionConfig = RevolutionConfig(
        api_prefix="apix",
        drf_title="CarAPIS",
        drf_description="Advanced Car Import/Export Platform API",
        zones={
            "client": ZoneConfig(
                apps=["accounts", "billing", "payments"],
                title="Client API",
                public=True,
                auth_required=False,
            ),
            "internal": ZoneConfig(
                apps=["mailer", "services"],
                title="Internal API",
                public=False,
                auth_required=True,
            ),
            "customs": ZoneConfig(
                apps=["data_customs"],
                title="Customs API",
                description="Customs calculations",
                public=True,
            ),
        },
    )

    # === Beautiful Admin Dashboard ===
    unfold: UnfoldConfig = UnfoldConfig(
        theme=UnfoldTheme(
            site_title="CarAPIS Admin",
            site_header="CarAPIS",
            site_subheader="Automotive Data Platform",
            theme="auto",
            dashboard_callback="api.dashboard.callbacks.main_dashboard_callback",
        ),
    )

config = CarAPISConfig()
```

## 🔧 Environment Intelligence

Django-CFG automatically detects your environment and applies appropriate settings:

| Environment | Cache Backend | Email Backend | Database SSL | Debug Mode | Static Files |
|-------------|---------------|---------------|--------------|------------|--------------|
| **Development** | Memory/Redis | Console | Optional | True | Django Dev Server |
| **Testing** | Dummy Cache | In-Memory | Disabled | False | Static Files |
| **Staging** | Redis | SMTP | Required | False | WhiteNoise |
| **Production** | Redis | SMTP | Required | False | WhiteNoise |

## 📊 Built-in Integrations

### 🎨 Django Unfold Admin
Beautiful, modern admin interface with Tailwind CSS, dark mode, and dashboard widgets.

### 🔄 Django Revolution API
Automatic API generation with OpenAPI/Swagger documentation and zone-based architecture.

### 📧 Email & Notifications
SMTP, Telegram bot integration with environment-specific backends.

### 🗄️ Multi-Database Support
Smart database routing with connection pooling and SSL configuration.

### ⚡ Redis Caching
Production-ready caching with separate cache backends for different use cases.

## 🔄 Migration Guide

### Step 1: Install django-cfg
```bash
pip install django-cfg
```

### Step 2: Create YAML configuration
```yaml
# config.dev.yaml
secret_key: "your-secret-key"
debug: true
database:
  url: "postgresql://user:pass@localhost:5432/mydb"
```

### Step 3: Create configuration class
```python
# config.py
from django_cfg import DjangoConfig
from .environment import env

class MyConfig(DjangoConfig):
    project_name: str = "My Project"
    secret_key: str = env.secret_key
    debug: bool = env.debug

config = MyConfig()
```

### Step 4: Update settings.py
```python
# settings.py
from .config import config
globals().update(config.get_all_settings())
```

### Step 5: Test
```bash
python manage.py check
python manage.py runserver
```

## 🧪 Testing

Django-CFG includes comprehensive testing utilities:

```python
def test_my_config():
    config = MyConfig()
    settings = config.get_all_settings()
    
    assert "SECRET_KEY" in settings
    assert settings["DEBUG"] is False
    assert "myapp" in settings["INSTALLED_APPS"]
    assert "SPECTACULAR_SETTINGS" in settings
```

## 📚 Advanced Features

### Environment-Specific Configuration
```yaml
# config.prod.yaml
debug: false
database:
  url: "${DATABASE_URL}"
redis_url: "${REDIS_URL}"

# config.dev.yaml  
debug: true
database:
  url: "postgresql://postgres:postgres@localhost:5432/myapp"
```

### Multi-Environment Support
```python
# Automatic environment detection
IS_DEV = os.environ.get("IS_DEV", "").lower() in ("true", "1", "yes")
IS_PROD = os.environ.get("IS_PROD", "").lower() in ("true", "1", "yes")
IS_TEST = "test" in sys.argv
```

### Custom Dashboard Callbacks
```python
def main_dashboard_callback(request, context):
    """Custom admin dashboard with real-time data"""
    return [
        {
            "title": "System Status",
            "metric": "98.5%",
            "footer": "Uptime last 30 days",
        },
        {
            "title": "Active Users", 
            "metric": "1,234",
            "footer": "Online now",
        },
    ]
```

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md).

### Development Setup

```bash
git clone https://github.com/markolofsen/django-cfg.git
cd django-cfg
poetry install
poetry run pytest
```

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Django** - The web framework for perfectionists with deadlines
- **Pydantic** - Data validation using Python type hints  
- **Django Unfold** - Beautiful admin interface
- **Django Revolution** - API generation and management

---

**Made with ❤️ by the UnrealOS Team**

*Django-CFG: Because configuration should be simple, safe, and powerful.*
