# 🚀 Django Config Toolkit

**Ultimate Django configuration with Pydantic 2, Unfold Admin, Django Revolution & More**

[![PyPI version](https://badge.fury.io/py/django-cfg.svg)](https://badge.fury.io/py/django-cfg)
[![Python versions](https://img.shields.io/pypi/pyversions/django-cfg.svg)](https://pypi.org/project/django-cfg/)
[![Django versions](https://img.shields.io/badge/django-4.0%2B-blue.svg)](https://www.djangoproject.com/)

A complete Django configuration solution that transforms complex settings into **type-safe**, **validated**, and **developer-friendly** code with full support for modern Django tools.

## ✨ Features

### 🔧 Core Features
- 🔥 **One-line Django settings** - Replace complex settings with one import
- 🛡️ **Type-safe configuration** - 100% type safety with Pydantic 2
- 🌍 **Smart environment detection** - Auto-detects .env files and environment
- ⚡ **Amazing performance** - <50ms initialization, instant runtime access
- 🎯 **Smart defaults** - Production-ready defaults for Django

### 🎨 Extended Integrations
- 🎨 **Unfold Admin** - Complete admin dashboard with callbacks
- 🚀 **Django Revolution** - API zones and TypeScript client generation
- ⚙️ **Constance** - Dynamic settings management via admin
- 📝 **Structured Logging** - Advanced logging with rotation and levels
- 🗄️ **Database Routing** - Multi-database support with smart routing
- 📊 **Dashboard Components** - Ready-to-use admin dashboard widgets

## 🚀 Quick Start

### Installation

```bash
pip install django-cfg
```

### Django Settings (One Line!)

```python
# settings.py
from django_cfg import ConfigToolkit

# 🔥 ONE LINE - Replace your entire Django settings!
globals().update(ConfigToolkit.get_django_settings())

# That's it! All configs loaded automatically:
# ✅ Core Django settings
# ✅ Unfold admin (if installed)
# ✅ Django Revolution (if installed)
# ✅ Constance (if installed)
# ✅ Advanced logging
# ✅ Database routing
```

### Environment Variables

```bash
# .env
DEBUG=true
SECRET_KEY=your-super-secret-key-change-this-in-production
DATABASE_URL=postgresql://user:password@localhost:5432/mydb

# 🎨 Unfold Admin
UNFOLD__SITE_TITLE=My Amazing Admin
UNFOLD__SITE_HEADER=Control Panel
UNFOLD__DASHBOARD_ENABLED=true

# 🚀 Django Revolution
REVOLUTION__ENABLED=true
REVOLUTION__API_PREFIX=api/v1
REVOLUTION__GENERATE_CLIENTS=true

# ⚙️ Constance Dynamic Settings
CONSTANCE__BACKEND=database
CONSTANCE__ADMIN_INTERFACE_ENABLED=true

# 🗄️ Multiple Databases
READ_REPLICA_URL=postgresql://user:password@localhost:5432/replica
CACHE_DB_URL=postgresql://user:password@localhost:5432/cache
```

### Type-Safe Access Anywhere

```python
from django_cfg import ConfigToolkit

# 🔧 Core settings
print(f"Debug: {ConfigToolkit.debug}")
print(f"Environment: {ConfigToolkit.environment}")
print(f"Database: {ConfigToolkit.database_url}")

# 🎨 Unfold settings
if ConfigToolkit.unfold_enabled:
    print(f"Admin title: {ConfigToolkit.site_title}")

# 🚀 Revolution settings
if ConfigToolkit.revolution_enabled:
    print(f"API prefix: {ConfigToolkit.api_prefix}")

# ⚙️ Constance settings
if ConfigToolkit.constance_enabled:
    print(f"Backend: {ConfigToolkit.constance_backend}")

# 📝 Logging settings
print(f"Log level: {ConfigToolkit.log_level}")
```

## 📦 Configuration Models

### 🔧 Core Models
- **EnvironmentConfig** - Environment variables and paths
- **DatabaseConfig** - Database settings with multi-DB routing
- **SecurityConfig** - CORS, CSRF, SSL, and security headers
- **APIConfig** - Django REST Framework configuration
- **CacheConfig** - Redis/Memory cache configuration
- **EmailConfig** - SMTP/Email backend configuration

### 🎨 Extended Models (Auto-loaded if dependencies available)
- **UnfoldConfig** - Complete Unfold admin dashboard
- **RevolutionConfig** - Django Revolution API zones and client generation
- **ConstanceConfig** - Dynamic settings via database/redis
- **LoggingConfig** - Structured logging with handlers and rotation

## 🎨 Unfold Admin Integration

### Automatic Configuration

```python
# No code needed! Auto-configured if `unfold` is installed:
# ✅ Beautiful admin dashboard
# ✅ Custom navigation and sidebar
# ✅ Dashboard callbacks with metrics
# ✅ Environment indicators
# ✅ Search functionality
# ✅ Badge notifications
```

### Custom Dashboard

```python
# Custom unfold configuration
from django_cfg import UnfoldConfig

unfold = UnfoldConfig(
    site_title="CarAPIS Admin",
    site_header="Automotive Data Platform", 
    site_subheader="Manage your car data",
    dashboard_enabled=True,
    dashboard_callback="myapp.callbacks.custom_dashboard"
)
```

### Built-in Dashboard Components

The toolkit provides ready-to-use dashboard callbacks:

- **System Overview** - User counts, session stats
- **Environment Info** - Current environment, debug status
- **Permission Management** - User permissions and groups
- **Search Integration** - Search across users and models
- **Health Badges** - System status indicators

## 🚀 Django Revolution Integration

### Automatic API Zones

```python
# Auto-configured zones if `django_revolution` is installed:
# ✅ Public API zone (accounts, billing, products)
# ✅ Internal API zone (services, mailer) 
# ✅ Admin API zone (admin tools)
# ✅ TypeScript client generation
# ✅ API documentation
```

### Custom API Zones

```python
from django_cfg import RevolutionConfig

revolution = RevolutionConfig()

# Add custom zones
revolution.add_zone(
    name="v2", 
    apps=["myapp.v2"],
    title="API v2",
    public=True,
    auth_required=False,
    version="v2"
)

# Configure monorepo support
revolution.add_monorepo(
    name="frontend",
    path="../../frontend",
    api_package_path="packages/api/src"
)

# Generate clients
revolution.client_languages = ["typescript", "python", "dart"]
```

## ⚙️ Constance Dynamic Settings

### Automatic Configuration

```python
# Auto-configured if `constance` is installed:
# ✅ Database backend
# ✅ Admin interface
# ✅ Common settings (site name, maintenance mode, etc.)
# ✅ Organized fieldsets
```

### Custom Settings

```python
from django_cfg import ConstanceConfig

constance = ConstanceConfig()

# Add dynamic settings
constance.add_config_field(
    name="MAX_UPLOAD_SIZE",
    default=10485760,  # 10MB
    help_text="Maximum file upload size in bytes",
    field_type="int"
)

constance.add_config_field(
    name="MAINTENANCE_MODE",
    default=False,
    help_text="Enable maintenance mode",
    field_type="bool"
)
```

## 🗄️ Multi-Database Routing

### Smart Database Routing

```bash
# .env - Configure multiple databases
DATABASE_URL=postgresql://user:pass@localhost/main
READ_REPLICA_URL=postgresql://user:pass@localhost/replica
CACHE_DB_URL=postgresql://user:pass@localhost/cache
ANALYTICS_DB_URL=postgresql://user:pass@localhost/analytics
```

Automatic routing rules applied:
- `analytics`, `reports` apps → `read_replica`
- `cache`, `sessions` apps → `cache_db`
- `data_analytics`, `metrics` apps → `analytics_db`
- All other apps → `default`

### Custom Routing

```python
from django_config_toolkit import DatabaseConfig

db_config = DatabaseConfig()
routing_rules = db_config.get_database_routing_rules()

# Add custom routing
routing_rules['myapp'] = 'analytics_db'
```

## 📝 Advanced Logging

### Auto-Configuration

```python
# Automatic logging setup:
# ✅ Console and file handlers
# ✅ Rotating file logs (10MB, 5 backups)
# ✅ Separate error logs
# ✅ Django server logs
# ✅ Formatted with timestamps
```

### Custom Logging

```python
from django_cfg import LoggingConfig, LoggerConfig

logging_config = LoggingConfig(
    root_level="DEBUG",
    file_enabled=True,
    rotating_enabled=True,
    max_file_size=20971520,  # 20MB
    backup_count=10
)

# Add custom logger
logging_config.custom_loggers.append(LoggerConfig(
    name="myapp.api",
    level="INFO", 
    handlers=["file", "console"],
    propagate=False
))
```

## 🛠️ Advanced Usage

### Production Optimization

```python
# Automatic production configuration:
if ConfigToolkit.is_production:
    # ✅ DEBUG = False
    # ✅ SECURE_SSL_REDIRECT = True
    # ✅ Security headers enabled
    # ✅ ALLOWED_HOSTS configured
    # ✅ Unfold optimized for production
    # ✅ Logging optimized
    # ✅ Database routing optimized
```

### Environment-Specific Settings

```python
# Different .env files for different environments
# .env.development
DEBUG=true
UNFOLD__THEME=dark

# .env.production  
DEBUG=false
UNFOLD__THEME=light
SECURITY__SSL_REDIRECT=true
```

### Custom Configuration

```python
from django_cfg import ConfigToolkit
from django_config_toolkit.models import UnfoldConfig, RevolutionConfig

# Get toolkit instance
toolkit = ConfigToolkit()

# Access any config
if toolkit._unfold_config:
    print(f"Unfold site title: {toolkit._unfold_config.site_title}")

if toolkit._revolution_config:
    zones = toolkit._revolution_config.zones
    print(f"API zones configured: {list(zones.keys())}")

# Custom validation
if not toolkit.database_url.startswith('postgresql://'):
    raise ValueError("PostgreSQL required in production")
```

### Testing Configuration

```python
# tests/test_config.py
from django_cfg import ConfigToolkit

def test_config_validation():
    """Test configuration is valid."""
    toolkit = ConfigToolkit()
    
    # Test core config
    assert toolkit.secret_key
    assert toolkit.database_url
    
    # Test extended features
    if toolkit.unfold_enabled:
        assert toolkit.site_title
    
    if toolkit.revolution_enabled:
        assert toolkit.api_prefix

def test_database_connection():
    """Test database connectivity."""
    toolkit = ConfigToolkit()
    assert toolkit._db_config.test_connection()
```

## 🔧 Environment Variables Reference

### Core Settings
```bash
# Environment
DEBUG=true
ENVIRONMENT=development
SECRET_KEY=your-secret-key

# Database
DATABASE_URL=postgresql://user:pass@host:port/db
READ_REPLICA_URL=postgresql://user:pass@host:port/replica
CACHE_DB_URL=postgresql://user:pass@host:port/cache

# Security
SECURITY__CORS_ENABLED=true
SECURITY__CSRF_ENABLED=true
SECURITY__SSL_REDIRECT=false

# API
API__RATE_LIMIT_ENABLED=true
API__PAGE_SIZE=25
API__DOCS_ENABLED=true

# Cache
CACHE__BACKEND=redis
REDIS_URL=redis://localhost:6379/0

# Email
EMAIL__BACKEND=smtp
EMAIL__HOST=smtp.gmail.com
EMAIL__PORT=587
```

### Extended Settings
```bash
# Unfold Admin
UNFOLD__SITE_TITLE=My Admin
UNFOLD__SITE_HEADER=Administration
UNFOLD__DASHBOARD_ENABLED=true
UNFOLD__THEME=auto

# Django Revolution
REVOLUTION__ENABLED=true
REVOLUTION__API_PREFIX=api
REVOLUTION__GENERATE_CLIENTS=true
REVOLUTION__CLIENT_LANGUAGES=typescript,python

# Constance
CONSTANCE__BACKEND=database
CONSTANCE__ADMIN_INTERFACE_ENABLED=true

# Logging
LOGGING__ROOT_LEVEL=INFO
LOGGING__FILE_ENABLED=true
LOGGING__ROTATING_ENABLED=true
LOGGING__MAX_FILE_SIZE=10485760
```

## 📚 API Reference

### ConfigToolkit Properties

```python
# Core properties
ConfigToolkit.debug: bool
ConfigToolkit.environment: str
ConfigToolkit.secret_key: str
ConfigToolkit.database_url: str
ConfigToolkit.is_production: bool

# Security properties  
ConfigToolkit.cors_enabled: bool
ConfigToolkit.csrf_enabled: bool
ConfigToolkit.ssl_enabled: bool

# API properties
ConfigToolkit.api_page_size: int
ConfigToolkit.api_rate_limit_enabled: bool
ConfigToolkit.api_docs_enabled: bool

# Extended properties
ConfigToolkit.unfold_enabled: bool
ConfigToolkit.site_title: str
ConfigToolkit.revolution_enabled: bool
ConfigToolkit.api_prefix: str
ConfigToolkit.constance_enabled: bool
ConfigToolkit.logging_enabled: bool
ConfigToolkit.log_level: str
```

### Utility Methods

```python
# Validation
ConfigToolkit.validate_config() -> bool
ConfigToolkit.show_config() -> None

# Environment helpers
ConfigToolkit.create_env_examples() -> None
ConfigToolkit.get_django_settings() -> Dict[str, Any]
```

## 🤝 Contributing

We love contributions! Here's how to get started:

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Make your changes
4. Add tests for your changes
5. Run tests: `pytest`
6. Commit your changes: `git commit -m 'Add amazing feature'`
7. Push to the branch: `git push origin feature/amazing-feature`
8. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- 📖 [Documentation](https://github.com/your-org/django-config-toolkit)
- 🐛 [Issue Tracker](https://github.com/your-org/django-config-toolkit/issues)
- 💬 [Discussions](https://github.com/your-org/django-config-toolkit/discussions)

## 🏆 Credits

Built with ❤️ by the Django community.

- **Pydantic 2** for amazing validation
- **Django** for the best web framework
- **Unfold** for beautiful admin interface
- **Django Revolution** for API generation

---

**Made your Django configuration awesome? ⭐ Star this repo!**