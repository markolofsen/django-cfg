# 🚀 Django CFG Sample Project

Complete demonstration of **django-cfg** features - modern Django configuration with type safety.

> 🎯 **Ready to run!** Quick start in 3 commands!

## ✨ What This Demonstrates

### 🔧 **Type-Safe Configuration**
- **Pydantic v2** models for 100% type safety
- **YAML-based** environment configuration
- **Zero raw dictionaries** - everything is typed
- **Auto-generated** Django settings from one config class

### 🗄️ **Database Management**
- **Multiple databases** with automatic routing
- **Simple routing** - just specify `apps=["app.name"]`
- **Connection string parsing** with validation
- **Separate SQLite files** per database

### 🎨 **Modern Admin**
- **Unfold theme** with beautiful dark/light UI
- **Custom navigation** and dashboard
- **Real-time metrics** with dashboard callbacks
- **Quick actions** with automatic URL resolution

### 🔌 **API & Services**
- **Django REST Framework** auto-configuration
- **OpenAPI/Swagger** documentation with drf-spectacular
- **JWT authentication** with token blacklisting
- **Pagination** and filtering built-in

### ⚙️ **Dynamic Configuration**
- **Constance** for runtime settings
- **Automatic admin** registration
- **Type-safe** field definitions
- **Grouped fieldsets** for organization

## 📁 Project Structure

```
example/django/
├── api/                          # Main configuration
│   ├── config.py                 # 🔥 DjangoConfig (Pydantic)
│   ├── settings.py               # ⚙️ Auto-generated Django settings
│   ├── urls.py                   # 🔗 URL configuration
│   └── environment/              # 🌍 YAML configs
│       ├── config.dev.yaml       # Development
│       ├── config.prod.yaml      # Production
│       └── loader.py             # Config loader
├── apps/                         # Django applications
│   ├── blog/                     # Blog with posts/comments
│   ├── shop/                     # E-commerce
│   └── profiles/                 # User profiles
├── db/                           # SQLite databases
│   ├── default.sqlite3           # Main database
│   ├── blog.sqlite3              # Blog (routed)
│   └── shop.sqlite3              # Shop (routed)
├── Makefile                      # 🛠️ Development commands
└── manage.py                     # Django management
```

## 🚀 Quick Start

### 1. Install Dependencies
```bash
cd example/django/
poetry install --with local
```

### 2. Run Migrations
```bash
make migrate
```

### 3. Start Server
```bash
make dev
# Server runs on http://127.0.0.1:8000
```

### 4. 🎯 Explore Features

- **Admin**: http://127.0.0.1:8000/admin/
- **API Docs**: http://127.0.0.1:8000/api/schema/swagger-ui/
- **Health Check**: http://127.0.0.1:8000/cfg/status/
- **URL Patterns**: `make show-urls`

## 🛠️ Development Commands

```bash
# Development server
make dev              # Start server (auto-kills port 8000)
make dev-ngrok        # Start with ngrok tunnel

# Database
make migrate          # Run migrations
make makemigrations   # Generate migrations

# Testing
make test             # Run tests
make check            # Django system checks

# Utils
make show-urls        # Show all URL patterns
make shell            # Django shell
make manage CMD=...   # Run any manage.py command
```

## 🔧 Key Features

### Type-Safe Configuration
```python
# api/config.py - Everything typed and validated!
class SampleProjectConfig(DjangoConfig):
    project_name: str = "Django CFG Sample"
    debug: bool = env.debug

    # Multiple databases with routing
    databases: Dict[str, DatabaseConfig] = {
        "default": DatabaseConfig.from_url(url=env.database.url),
        "blog_db": DatabaseConfig.from_url(
            url=env.database.url_blog,
            apps=["apps.blog"],  # Auto-routes blog app
            operations=["read", "write", "migrate"],
        )
    }
```

### Auto-Generated Django Settings
```python
# api/settings.py - One line replaces hundreds!
from api.config import config
locals().update(config.get_all_settings())
```

### YAML Environment Configuration
```yaml
# api/environment/config.dev.yaml
secret_key: "dev-secret-key-change-in-production"
debug: true

database:
  url: "sqlite:///db/default.sqlite3"
  url_blog: "sqlite:///db/blog.sqlite3"
  url_shop: "sqlite:///db/shop.sqlite3"

app:
  name: "Django CFG Sample"
  site_url: "http://localhost:8000"
```

## 🎯 Main Configuration File

The entire project is configured in `api/config.py`:

```python
from django_cfg import DjangoConfig, DatabaseConfig, UnfoldConfig
from api.environment import env

class SampleProjectConfig(DjangoConfig):
    # Project info
    project_name: str = env.app.name
    debug: bool = env.debug
    secret_key: str = env.secret_key

    # URLs
    root_urlconf: str = "api.urls"
    wsgi_application: str = "api.wsgi.application"
    site_url: str = env.app.site_url
    api_url: str = env.app.api_url

    # Apps
    project_apps: list[str] = [
        "core",
        "apps.profiles",
        "apps.blog",
        "apps.shop",
    ]

    # Databases with routing
    databases: Dict[str, DatabaseConfig] = {
        "default": DatabaseConfig.from_url(url=env.database.url),
        "blog_db": DatabaseConfig.from_url(
            url=env.database.url_blog,
            apps=["apps.blog"],
            operations=["read", "write", "migrate"],
        ),
        "shop_db": DatabaseConfig.from_url(
            url=env.database.url_shop,
            apps=["apps.shop"],
            operations=["read", "write", "migrate"],
        ),
    }

    # Admin theme, JWT, DRF, Constance, etc.
    # ... (see config.py for full configuration)

# Create instance
config = SampleProjectConfig()
```

## 🗄️ Database Routing

Three separate databases with automatic routing:
- **`default`**: Main application (users, sessions, admin)
- **`blog_db`**: Blog posts and comments (auto-routed)
- **`shop_db`**: Products and orders (auto-routed)

No manual router needed - just specify `apps=["app.name"]` in DatabaseConfig!

## 🧪 Testing

```bash
# Run Django tests
make test

# Check configuration
make check

# Validate settings
poetry run python manage.py shell
>>> from api.config import config
>>> print("✅ Config valid!")
```

## 🚀 Production Deployment

```bash
# Set production environment
export IS_PROD=true
export DEBUG=false

# Or create .env file
echo "IS_PROD=true" > .env
echo "DEBUG=false" >> .env

# Project auto-switches to config.prod.yaml
```

## 📚 Documentation

- **Django-CFG**: Modern Django configuration
- **Example Docs**: See `@docs/` directory for integrations
- **Unfold Admin**: Beautiful admin theme
- **DRF**: REST API framework
- **Pydantic**: Type validation

## 🤝 Need Help?

Check the documentation:
- `@docs/DRAMATIQ_INTEGRATION.md` - Task queues
- `@docs/NGROK_INTEGRATION.md` - Local tunneling
- `@docs/TWILIO_INTEGRATION.md` - SMS/WhatsApp

## 📄 License

MIT License
