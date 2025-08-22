# 🚀 Django-CFG: The Configuration Revolution

[![Python Version](https://img.shields.io/pypi/pyversions/django-cfg.svg)](https://pypi.org/project/django-cfg/)
[![Django Version](https://img.shields.io/pypi/djversions/django-cfg.svg)](https://pypi.org/project/django-cfg/)
[![License](https://img.shields.io/pypi/l/django-cfg.svg)](https://github.com/markolofsen/django-cfg/blob/main/LICENSE)
[![PyPI Version](https://img.shields.io/pypi/v/django-cfg.svg)](https://pypi.org/project/django-cfg/)

> **Transform your Django development from chaos to zen in minutes, not months.**

Django-CFG is the production-ready configuration framework that eliminates Django's biggest pain points. Say goodbye to 500-line `settings.py` files and hello to type-safe, YAML-powered, intelligent configuration that just works.

**🎯 [See it in action →](https://github.com/markolofsen/django-cfg/tree/main/django_sample)** Complete sample project with blog, shop, multi-database routing, and beautiful admin interface.

---

## 🔥 Why Django-CFG Changes Everything

### The Problem with Traditional Django
- **500+ line settings files** that nobody wants to touch
- **Zero type safety** - typos break production
- **Manual everything** - databases, caching, admin, APIs
- **Environment hell** - different configs everywhere
- **Ugly admin interface** stuck in 2010
- **No API documentation** without hours of setup

### The Django-CFG Solution
- **3-line configuration** that handles everything
- **100% type-safe** with full IDE support
- **Smart automation** that knows what you need
- **Environment detection** that just works
- **Beautiful modern admin** with Tailwind CSS
- **Auto-generated API docs** and client libraries

---

## ⚡ Quick Start

### Installation

```bash
# Using Poetry (recommended)
poetry add django-cfg

# Using pip
pip install django-cfg

# Using pipenv
pipenv install django-cfg
```

### Your First Django-CFG Project

**1. Create `config.py`:**
```python
from django_cfg import DjangoConfig

class MyConfig(DjangoConfig):
    project_name: str = "MyAwesomeApp"
    secret_key: str = "your-secret-key"
    debug: bool = True
    project_apps: list[str] = ["accounts", "blog", "shop"]

config = MyConfig()
```

**2. Update `settings.py`:**
```python
from .config import config
globals().update(config.get_all_settings())
```

**3. Run your project:**
```bash
python manage.py runserver
```

**That's it!** 🎉 You now have:
- ✅ Beautiful admin interface with Unfold + Tailwind CSS
- ✅ Auto-generated API documentation
- ✅ Environment-aware configuration
- ✅ Type-safe settings with full IDE support
- ✅ Production-ready security defaults

---

## 🏆 Feature Comparison

| Feature | Traditional Django | Django-CFG |
|---------|-------------------|-------------|
| **📝 Configuration** | 500+ lines of settings hell | **3 lines. Done.** |
| **🔒 Type Safety** | Pray and hope | **100% validated** |
| **🎨 Admin Interface** | Ugly 2010 design | **Modern Unfold + Tailwind** |
| **📊 Dashboard** | Basic admin index | **Real-time metrics & widgets** |
| **🗄️ Multi-Database** | Manual routing nightmare | **Smart auto-routing** |
| **⚡ Commands** | Terminal only | **Beautiful web interface** |
| **📚 API Docs** | Hours of manual setup | **Auto-generated OpenAPI** |
| **📦 Client Generation** | Write clients manually | **Auto TS/Python clients** |
| **🏢 Monorepo** | Complex setup | **Built-in support** |
| **📧 Notifications** | Manual SMTP/webhooks | **Email & Telegram modules** |
| **🚀 Deployment** | Cross fingers | **Production-ready defaults** |
| **💡 IDE Support** | Basic syntax highlighting | **Full IntelliSense paradise** |
| **🐛 Config Errors** | Runtime surprises | **Compile-time validation** |
| **😊 Developer Joy** | Constant frustration | **Pure coding bliss** |

---

## 🎯 Core Features

### 🔒 **Type-Safe Configuration**
Full Pydantic validation with IDE autocomplete and compile-time error checking.

### 🎨 **Beautiful Admin Interface**
Modern Django Unfold admin with Tailwind CSS, dark mode, and custom dashboards.

### 📊 **Real-Time Dashboard**
Live metrics, system health, and custom widgets that update automatically.

### 🗄️ **Smart Multi-Database**
Automatic database routing based on app labels with connection pooling.

### ⚡ **Web Command Interface**
Run Django management commands from a beautiful web interface with real-time logs.

### 📚 **Auto API Documentation**
OpenAPI/Swagger docs generated automatically with zone-based architecture.

### 📦 **Client Generation**
TypeScript and Python API clients generated per zone automatically.

### 🏢 **Monorepo Ready**
Smart integration with modern monorepo architectures and build systems.

### 📧 **Built-in Modules**
Email, Telegram, and SMS notification modules ready out of the box.

### 🌍 **Environment Detection**
Automatic dev/staging/production detection with appropriate defaults.

---

## 🛠️ Management Commands (CLI Tools)

Django-CFG includes powerful management commands for development and operations:

| Command | Description | Example |
|---------|-------------|---------|
| **`check_settings`** | Validate configuration and settings | `python manage.py check_settings` |
| **`create_token`** | Generate API tokens and keys | `python manage.py create_token --user admin` |
| **`generate`** | Generate API clients and documentation | `python manage.py generate --zone client` |
| **`migrator`** | Smart database migrations with routing | `python manage.py migrator --apps blog,shop` |
| **`script`** | Run custom scripts with Django context | `python manage.py script my_script.py` |
| **`show_config`** | Display current configuration | `python manage.py show_config --format yaml` |
| **`show_urls`** | Display all URL patterns | `python manage.py show_urls --zone client` |
| **`superuser`** | Create superuser with smart defaults | `python manage.py superuser --email admin@example.com` |
| **`test_email`** | Test email configuration | `python manage.py test_email --to test@example.com` |
| **`test_telegram`** | Test Telegram bot integration | `python manage.py test_telegram --chat_id 123` |
| **`validate_config`** | Deep validation of all settings | `python manage.py validate_config --strict` |

---

## 🌍 Environment Detection

Django-CFG automatically detects your environment and applies appropriate settings:

| Environment | Detection Method | Cache Backend | Email Backend | Database SSL | Debug Mode |
|-------------|------------------|---------------|---------------|--------------|------------|
| **Development** | `DEBUG=True` or local domains | Memory/Redis | Console | Optional | `True` |
| **Testing** | `pytest` or `test` in command | Dummy Cache | In-Memory | Disabled | `False` |
| **Staging** | `STAGING=True` or staging domains | Redis | SMTP | Required | `False` |
| **Production** | `PRODUCTION=True` or prod domains | Redis | SMTP | Required | `False` |

---

## 📝 Logging System

Comprehensive logging with environment-aware configuration:

```python
# Automatic log configuration based on environment
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': 'django.log',
            'formatter': 'verbose',
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
    },
    'root': {
        'handlers': ['console', 'file'],
        'level': 'INFO',
    },
}
```

**Features:**
- Environment-specific log levels
- Automatic file rotation
- Structured logging with JSON support
- Integration with monitoring systems
- Custom formatters for different outputs

---

## 📚 API Documentation

Django-CFG provides ready-made Redoc/Swagger solutions for each API zone:

### Zone-Based API Architecture
```python
revolution: RevolutionConfig = RevolutionConfig(
    zones={
        "client": ZoneConfig(
            apps=["accounts", "billing"],
            title="Client API",
            public=True,
        ),
        "admin": ZoneConfig(
            apps=["management", "reports"],
            title="Admin API", 
            auth_required=True,
        ),
    }
)
```

### Automatic Documentation URLs
- **`/api/client/docs/`** - Interactive Swagger UI for client zone
- **`/api/client/redoc/`** - Beautiful ReDoc documentation
- **`/api/admin/docs/`** - Admin zone Swagger UI
- **`/api/admin/redoc/`** - Admin zone ReDoc

### Client Generation
```bash
# Generate TypeScript client for client zone
python manage.py generate --zone client --format typescript

# Generate Python client for admin zone  
python manage.py generate --zone admin --format python
```

---

## 🏗️ Real-World Example

Here's a complete production configuration:

```python
from django_cfg import DjangoConfig, DatabaseConnection, UnfoldConfig, RevolutionConfig

class ProductionConfig(DjangoConfig):
    """🚀 Production-ready configuration"""
    
    # === Project Settings ===
    project_name: str = "CarAPIS"
    project_version: str = "2.0.0"
    secret_key: str = env.secret_key
    debug: bool = False
    
    # === Multi-Database Setup ===
    databases: dict[str, DatabaseConnection] = {
        "default": DatabaseConnection(
            engine="django.db.backends.postgresql",
            name="carapis_main",
            user=env.db_user,
            password=env.db_password,
            host=env.db_host,
            port=5432,
            sslmode="require",
        ),
        "analytics": DatabaseConnection(
            engine="django.db.backends.postgresql",
            name="carapis_analytics", 
            user=env.db_user,
            password=env.db_password,
            host=env.db_host,
            routing_apps=["analytics", "reports"],
        ),
    }
    
    # === Beautiful Admin ===
    unfold: UnfoldConfig = UnfoldConfig(
        site_title="CarAPIS Admin",
        site_header="CarAPIS Control Center",
        theme="auto",
        dashboard_callback="api.dashboard.main_callback",
    )
    
    # === Multi-Zone API ===
    revolution: RevolutionConfig = RevolutionConfig(
        api_prefix="api/v2",
        zones={
            "public": ZoneConfig(
                apps=["cars", "search"],
                title="Public API",
                description="Car data and search",
                public=True,
            ),
            "partner": ZoneConfig(
                apps=["integrations", "webhooks"],
                title="Partner API",
                auth_required=True,
                rate_limit="1000/hour",
            ),
        }
    )

config = ProductionConfig()
```

---

## 🧪 Testing

Django-CFG includes comprehensive testing utilities:

```python
def test_configuration():
    """Test your configuration is valid"""
    config = MyConfig()
    settings = config.get_all_settings()
    
    # Validate required settings
    assert "SECRET_KEY" in settings
    assert settings["DEBUG"] is False
    assert "myapp" in settings["INSTALLED_APPS"]
    
    # Test database connections
    assert "default" in settings["DATABASES"]
    assert settings["DATABASES"]["default"]["ENGINE"] == "django.db.backends.postgresql"
    
    # Validate API configuration
    assert "SPECTACULAR_SETTINGS" in settings
    assert settings["SPECTACULAR_SETTINGS"]["TITLE"] == "My API"
```

---

## 🚀 Migration from Traditional Django

### Step 1: Install Django-CFG
```bash
poetry add django-cfg
```

### Step 2: Create Environment Configuration
```yaml
# environment/config.dev.yaml
secret_key: "your-development-secret-key"
debug: true
database:
  url: "postgresql://user:pass@localhost:5432/mydb"
redis_url: "redis://localhost:6379/0"
```

### Step 3: Create Configuration Class
```python
# config.py
from django_cfg import DjangoConfig
from .environment import env

class MyConfig(DjangoConfig):
    project_name: str = "My Project"
    secret_key: str = env.secret_key
    debug: bool = env.debug
    project_apps: list[str] = ["accounts", "blog"]

config = MyConfig()
```

### Step 4: Replace settings.py
```python
# settings.py - Replace everything with this
from .config import config
globals().update(config.get_all_settings())
```

### Step 5: Test & Deploy
```bash
python manage.py check
python manage.py runserver
```

**Result:** Your 500-line `settings.py` is now 3 lines, fully type-safe, and production-ready! 🎉

---

## 🤝 Contributing

We welcome contributions! Here's how to get started:

```bash
git clone https://github.com/markolofsen/django-cfg.git
cd django-cfg
poetry install
poetry run pytest
```

### Development Commands
```bash
# Run tests
poetry run pytest

# Format code
poetry run black .

# Type checking
poetry run mypy .

# Build package
poetry build
```

---

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **Django** - The web framework for perfectionists with deadlines
- **Pydantic** - Data validation using Python type hints
- **Django Unfold** - Beautiful modern admin interface
- **Django Revolution** - API generation and zone management

---

**Made with ❤️ by the UnrealOS Team**

*Django-CFG: Because configuration should be simple, safe, and powerful.*

**🚀 Ready to transform your Django experience? [Get started now!](https://github.com/markolofsen/django-cfg/tree/main/django_sample)**
