# 🚀 Django-CFG: The Configuration Revolution

[![Python Version](https://img.shields.io/pypi/pyversions/django-cfg.svg)](https://pypi.org/project/django-cfg/)
[![Django Version](https://img.shields.io/pypi/djversions/django-cfg.svg)](https://pypi.org/project/django-cfg/)
[![License](https://img.shields.io/pypi/l/django-cfg.svg)](https://github.com/markolofsen/django-cfg/blob/main/LICENSE)
[![PyPI Version](https://img.shields.io/pypi/v/django-cfg.svg)](https://pypi.org/project/django-cfg/)

> **Transform your Django development from chaos to zen in minutes, not months.**

Django-CFG is the production-ready configuration framework that eliminates Django's biggest pain points. Say goodbye to 500-line `settings.py` files and hello to type-safe, YAML-powered, intelligent configuration that just works.

**🎯 [See it in action →](https://github.com/markolofsen/django-cfg/tree/main/django_sample)** Complete sample project with blog, shop, newsletter campaigns, lead management, multi-database routing, and beautiful admin interface.

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
- **Type-safe configuration** with Pydantic validation
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
- ✅ Built-in support ticket system with chat interface
- ✅ Newsletter campaigns with email tracking & analytics
- ✅ Lead management system with CRM integration
- ✅ Auto-generated API documentation
- ✅ Environment-aware configuration
- ✅ Type-safe settings with full IDE support
- ✅ Production-ready security defaults

---

## 🏆 Feature Comparison

| Feature | Traditional Django | Django-CFG |
|---------|-------------------|-------------|
| **📝 Configuration** | 500+ lines of settings hell | **Type-safe & organized** |
| **🔒 Type Safety** | Pray and hope | **100% validated** |
| **🎨 Admin Interface** | Ugly 2010 design | **Modern Unfold + Tailwind** |
| **📊 Dashboard** | Basic admin index | **Real-time metrics & widgets** |
| **🗄️ Multi-Database** | Manual routing nightmare | **Smart auto-routing** |
| **⚡ Commands** | Terminal only | **Beautiful web interface** |
| **📚 API Docs** | Hours of manual setup | **Auto-generated OpenAPI** |
| **📦 Client Generation** | Write clients manually | **Auto TS/Python clients** |
| **🎫 Support System** | Build from scratch | **Built-in tickets & chat** |
| **👤 User Management** | Basic User model | **OTP auth & profiles** |
| **📧 Notifications** | Manual SMTP/webhooks | **Email & Telegram & LLM** |
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

### 🎫 **Built-in Support System**
Complete ticket management with modern chat interface, email notifications, and admin integration.

### 👤 **Advanced User Management**
Built-in accounts system with OTP authentication, user profiles, activity tracking, and registration sources.

### 📧 **Built-in Modules**
Email, Telegram, LLM integration, Support ticket system, Newsletter campaigns, Lead management, and advanced User management ready out of the box.

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
| **`translate_content`** | Translate JSON with LLM and smart caching | `python manage.py translate_content --target-lang es` |
| **`support_stats`** | Display support ticket statistics | `python manage.py support_stats --format json` |
| **`test_newsletter`** | Test newsletter sending functionality | `python manage.py test_newsletter --email test@example.com` |
| **`newsletter_stats`** | Display newsletter campaign statistics | `python manage.py newsletter_stats --format json` |
| **`leads_stats`** | Display lead conversion statistics | `python manage.py leads_stats --format json` |
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

## 🎫 Built-in Support System

Django-CFG includes a complete support ticket system with modern chat interface:

### Features
- **🎯 Ticket Management** - Create, assign, and track support tickets
- **💬 Chat Interface** - Beautiful Tailwind CSS chat UI for conversations  
- **📧 Email Integration** - Automatic notifications for ticket updates
- **👥 User Management** - Support for both staff and customer interactions
- **📊 Dashboard Integration** - Real-time metrics in Unfold admin
- **🔗 API Ready** - RESTful API endpoints for all support operations

### Quick Setup
```python
from django_cfg import DjangoConfig

class MyConfig(DjangoConfig):
    project_name: str = "My App"
    enable_support: bool = True  # That's it!

config = MyConfig()
```

### Automatic Integration
- ✅ **Admin Interface** - Support section in sidebar with tickets & messages
- ✅ **Dashboard Cards** - Live ticket statistics and quick actions  
- ✅ **API Endpoints** - `/api/support/` zone with full CRUD operations
- ✅ **Email Templates** - Beautiful HTML emails with your branding
- ✅ **Chat Interface** - Modern `/support/chat/{ticket_uuid}/` pages

### Disable Support (Optional)
```python
enable_support: bool = False  # Removes from admin, API, and dashboard
```

---

## 📧 Built-in Newsletter System

Django-CFG includes a complete newsletter and email marketing system with tracking and analytics:

### Features
- **📬 Newsletter Management** - Create, schedule, and manage email newsletters
- **👥 Subscription Management** - User subscriptions with double opt-in and unsubscribe
- **📊 Email Tracking** - Open rates, click tracking, and engagement analytics
- **🎯 Campaign System** - Organize newsletters into campaigns with templates
- **📈 Bulk Email** - Send to thousands of subscribers with delivery tracking
- **🔗 API Ready** - RESTful API endpoints for all newsletter operations
- **📱 Email Templates** - Beautiful responsive HTML templates with tracking pixels

### Quick Setup
```python
from django_cfg import DjangoConfig

class MyConfig(DjangoConfig):
    project_name: str = "My App"
    enable_newsletter: bool = True  # That's it!

config = MyConfig()
```

### Automatic Integration
- ✅ **Admin Interface** - Newsletter section with campaigns, subscriptions & email logs
- ✅ **Dashboard Cards** - Live newsletter statistics and recent campaigns
- ✅ **API Endpoints** - `/api/newsletter/` zone with full CRUD operations
- ✅ **Email Templates** - Responsive HTML emails with your branding and tracking
- ✅ **Tracking System** - Automatic open/click tracking with UUID-based security
- ✅ **Subscription Forms** - Ready-to-use subscription and unsubscribe endpoints

### Email Tracking Features
```python
from django_cfg.apps.newsletter.services.email_service import NewsletterEmailService

# Send newsletter with tracking
service = NewsletterEmailService()
result = service.send_newsletter_email(
    newsletter=newsletter,
    subject="Monthly Update",
    email_title="Our Latest News",
    main_text="Check out what's new this month!",
    button_text="Read More",
    button_url="https://example.com/news",
    send_to_all=True  # Send to all subscribers
)
```

### Disable Newsletter (Optional)
```python
enable_newsletter: bool = False  # Removes from admin, API, and dashboard
```

---

## 🎯 Built-in Lead Management System

Django-CFG includes a comprehensive lead collection and CRM system for capturing and managing potential customers:

### Features
- **📝 Lead Capture** - Collect leads from contact forms, landing pages, and API
- **🏷️ Lead Sources** - Track where leads came from (web, mobile, ads, referrals)
- **📊 Lead Scoring** - Automatic scoring based on engagement and profile data
- **🔄 Status Management** - Lead lifecycle from new to converted or closed
- **📧 Email Integration** - Automatic notifications for new leads and status changes
- **📱 API Ready** - RESTful API endpoints for all lead operations
- **🎯 CRM Integration** - Ready for integration with external CRM systems

### Quick Setup
```python
from django_cfg import DjangoConfig

class MyConfig(DjangoConfig):
    project_name: str = "My App"
    enable_leads: bool = True  # That's it!

config = MyConfig()
```

### Automatic Integration
- ✅ **Admin Interface** - Leads section with lead management and source tracking
- ✅ **Dashboard Cards** - Live lead statistics and conversion metrics
- ✅ **API Endpoints** - `/api/leads/` zone with full CRUD operations
- ✅ **Contact Forms** - Ready-to-use lead capture forms and endpoints
- ✅ **Email Notifications** - Automatic alerts for new leads and status changes
- ✅ **Source Tracking** - Automatic detection of lead sources and campaigns

### Lead Capture Example
```python
from django_cfg.apps.leads.models import Lead, LeadSource

# Create lead from contact form
lead = Lead.objects.create(
    name="John Doe",
    email="john@example.com",
    phone="+1234567890",
    message="Interested in your services",
    source=LeadSource.objects.get(name="Website Contact Form"),
    status=Lead.LeadStatus.NEW
)
```

### Disable Leads (Optional)
```python
enable_leads: bool = False  # Removes from admin, API, and dashboard
```

---

## 👤 Built-in User Management System

Django-CFG includes a comprehensive user management system with OTP authentication, profiles, and activity tracking:

### Features
- **🔐 OTP Authentication** - Secure one-time password authentication via email
- **👥 Custom User Model** - Extended user model with profiles and metadata
- **📊 Activity Tracking** - Complete audit trail of user actions and logins
- **🔗 Registration Sources** - Track where users came from (web, mobile, API, etc.)
- **📧 Email Integration** - Beautiful welcome emails and OTP notifications
- **🛡️ Security Features** - Failed attempt tracking, account lockouts, and audit logs
- **📱 API Ready** - RESTful API endpoints for all user operations

### Quick Setup
```python
from django_cfg import DjangoConfig

class MyConfig(DjangoConfig):
    project_name: str = "My App"
    enable_accounts: bool = True  # That's it!
    # auth_user_model is automatically set to django_cfg_accounts.CustomUser

config = MyConfig()
```

### Automatic Integration
- ✅ **Custom User Model** - Automatically sets `AUTH_USER_MODEL` to `django_cfg_accounts.CustomUser`
- ✅ **Admin Interface** - "Users & Access" section with users, groups, and registration sources
- ✅ **Dashboard Integration** - User statistics and recent activity widgets
- ✅ **API Endpoints** - `/api/accounts/` zone with authentication, profiles, and OTP
- ✅ **Email Templates** - Welcome emails and OTP verification with your branding
- ✅ **Migration Safety** - Smart migration ordering to avoid conflicts

### OTP Authentication Flow
```python
from django_cfg.apps.accounts.services.otp_service import OTPService

# Request OTP for user
success, error = OTPService.request_otp("user@example.com")

# Verify OTP code
user = OTPService.verify_otp("user@example.com", "123456")
```

### Custom User Model Features
- **Extended Profile** - Additional fields for user metadata
- **Activity Tracking** - Automatic logging of user actions
- **Registration Sources** - Track user acquisition channels
- **Security Audit** - Failed login attempts and security events

### Disable Accounts (Optional)
```python
enable_accounts: bool = False  # Uses Django's default User model
```

---

## 🤖 Built-in LLM Integration

Django-CFG includes a powerful LLM module for AI-powered features like translation, content generation, and smart automation:

### Features
- **🌍 Smart Translation** - JSON translation with intelligent caching by language pairs
- **💬 LLM Client** - OpenAI/OpenRouter integration with dynamic pricing and cost tracking
- **⚡ Smart Caching** - Text-level caching that sends only uncached content to LLM
- **🔧 Direct Injection** - No configuration needed, just inject `LLMClient` where needed
- **📊 Cost Tracking** - Real-time cost calculation with dynamic model pricing
- **🛡️ Production Ready** - Built-in error handling, retries, and fallbacks

### Quick Usage
```python
from django_cfg.modules.django_llm import LLMClient, DjangoTranslator

# Direct LLM usage
client = LLMClient(provider="openrouter", api_key="your-key")
response = client.chat_completion([{"role": "user", "content": "Hello!"}])

# Smart JSON translation with caching
translator = DjangoTranslator(client=client)
translated = translator.translate_json(
    data={"greeting": "Hello", "message": "Welcome to our app"},
    target_language="es"
)
# Result: {"greeting": "Hola", "message": "Bienvenido a nuestra aplicación"}
```

### Management Command
```bash
# Translate JSON content with smart caching
python manage.py translate_content --target-lang es --json '{"title": "Hello World"}'
```

### Key Benefits
- **Zero Configuration** - Works out of the box with environment variables
- **Smart Caching** - Dramatically reduces LLM costs with intelligent text-level caching
- **Language Detection** - Automatic source language detection for better translations
- **Cost Optimization** - Only sends uncached texts to LLM, reuses cached translations

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
    
    # === Built-in Modules ===
    enable_support: bool = True     # Automatic tickets, chat interface, email notifications
    enable_accounts: bool = True    # Advanced user management with OTP authentication
    enable_newsletter: bool = True  # Email marketing, campaigns, tracking & analytics
    enable_leads: bool = True       # Lead capture, CRM integration, source tracking
    
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

**Result:** Your 500-line `settings.py` is now organized, fully type-safe, and production-ready! 🎉

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
