---
title: Project Structure
description: Deep dive into the Django-CFG sample project folder structure and organization
sidebar_label: Project Structure
sidebar_position: 2
---

# Project Structure

Understanding the project structure is key to working effectively with Django-CFG. This guide provides a detailed explanation of every directory and file in the sample project.

## Complete Project Tree

```
my_django_cfg_demo/
├── 📁 api/                          # Configuration & Settings
│   ├── 🔧 config.py                 # Main Django-CFG configuration
│   ├── ⚙️ settings.py               # Auto-generated Django settings
│   ├── 🔗 urls.py                   # Root URL configuration
│   └── 📁 environment/              # Environment-specific configs
│       ├── 🛠️ config.dev.yaml       # Development settings
│       ├── 🚀 config.prod.yaml      # Production settings
│       ├── 🧪 config.test.yaml      # Testing settings
│       └── 📥 loader.py             # Configuration loader
├── 📁 apps/                         # Django Applications
│   ├── 📝 blog/                     # Blog with posts & comments
│   ├── 🛒 shop/                     # E-commerce with products & orders
│   └── 👥 profiles/                 # User profiles & preferences
├── 📁 core/                         # Core utilities
│   └── 📁 management/commands/      # Custom CLI commands
├── 📁 db/                           # Database files (SQLite)
│   ├── 🗄️ db.sqlite3               # Main database
│   ├── 📝 blog.sqlite3             # Blog database (routed)
│   └── 🛒 shop.sqlite3             # Shop database (routed)
├── 📁 docker/                       # Docker configuration
├── 📁 static/                       # Static files
├── 📁 templates/                    # Django templates
├── 🎛️ manage.py                    # Django management script
├── 📋 pyproject.toml               # Poetry dependencies
├── 📋 requirements.txt             # Pip dependencies
└── 📖 README.md                    # Project documentation
```

## Directory Breakdown

### 📁 api/ - Configuration Hub

The `api/` directory is the heart of your Django-CFG project, containing all configuration and settings.

#### config.py

The main configuration file using Django-CFG's type-safe configuration system. This file defines:
- Project metadata (name, debug mode, secret key)
- Database configurations and routing rules
- Service integrations (email, SMS, notifications)
- Admin interface customization
- API settings and authentication

```python
# api/config.py structure
class SampleProjectConfig(DjangoConfig):
    # Core settings
    project_name: str
    debug: bool
    secret_key: str

    # Multi-database setup
    databases: Dict[str, DatabaseConfig]

    # Service configurations
    email: EmailConfig
    twilio: TwilioConfig
    telegram: TelegramConfig

    # UI and API
    unfold: UnfoldConfig
    drf: DRFConfig
```

See [Configuration Setup](./configuration) for detailed examples.

#### settings.py

Auto-generated Django settings file. This is created by Django-CFG and translates your type-safe `config.py` into standard Django settings.

**Important**: Don't edit this file directly. All changes should be made in `config.py`.

#### urls.py

Root URL configuration that maps URLs to views and includes:
- Admin interface routes
- API endpoints
- Health check endpoints
- Static/media file serving (development)

```python
# api/urls.py
urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('api.api_urls')),
    path('cfg/', include('django_cfg.urls')),
]
```

#### 📁 environment/

Environment-specific configuration files in YAML format.

**config.dev.yaml** - Development settings:
```yaml
debug: true
is_prod: false
database:
  url: "sqlite:///db/db.sqlite3"
email:
  sendgrid_api_key: ""  # Console backend
```

**config.prod.yaml** - Production settings:
```yaml
debug: false
is_prod: true
database:
  url: "postgresql://..."
email:
  sendgrid_api_key: "<from-yaml-config>"
```

**config.test.yaml** - Testing settings:
```yaml
debug: true
is_prod: false
database:
  url: "sqlite:///:memory:"
```

**loader.py** - Configuration loader that reads YAML files and environment variables.

See [Configuration Setup](./configuration) for environment configuration patterns.

### 📁 apps/ - Django Applications

Contains all custom Django applications, following Django's app structure.

#### 📝 blog/

Blog application with posts and comments:

```
blog/
├── models.py          # Post, Comment, Category models
├── admin.py           # Admin interface configuration
├── views.py           # View logic (if any)
├── serializers.py     # DRF serializers for API
├── urls.py            # URL routing for blog
└── migrations/        # Database migrations
```

**Models**:
- `Post` - Blog posts with title, content, status, author
- `Comment` - Comments on posts
- `Category` - Post categories

**Database Routing**: Automatically uses `blog_db` database.

#### 🛒 shop/

E-commerce application with products and orders:

```
shop/
├── models.py          # Product, Order, OrderItem models
├── admin.py           # Admin interface configuration
├── views.py           # View logic
├── serializers.py     # DRF serializers for API
├── urls.py            # URL routing for shop
└── migrations/        # Database migrations
```

**Models**:
- `Product` - Products with name, price, stock
- `Order` - Customer orders
- `OrderItem` - Items within an order

**Database Routing**: Automatically uses `shop_db` database.

#### 👥 profiles/

User profile management:

```
profiles/
├── models.py          # Profile, Preferences models
├── admin.py           # Admin interface configuration
├── views.py           # Profile views
├── serializers.py     # DRF serializers
└── migrations/        # Database migrations
```

**Models**:
- `Profile` - User profile information
- `UserPreferences` - User settings and preferences

**Database Routing**: Uses default database (with users).

### 📁 core/ - Core Utilities

Contains project-wide utilities, helpers, and custom management commands.

```
core/
├── management/
│   └── commands/      # Custom CLI commands
│       ├── seed_data.py
│       └── export_data.py
├── utils.py           # Helper functions
└── middleware.py      # Custom middleware (if any)
```

Custom commands can be run with:
```bash
python manage.py seed_data
python manage.py export_data
```

### 📁 db/ - Database Files

Contains SQLite database files for development. In production, you'll use PostgreSQL or another production database.

```
db/
├── db.sqlite3         # Main database (auth, sessions, profiles)
├── blog.sqlite3       # Blog database (posts, comments)
└── shop.sqlite3       # Shop database (products, orders)
```

**Note**: This directory is gitignored and only exists in development.

See [Multi-Database Setup](./multi-database) for routing and migration strategies.

### 📁 docker/ - Docker Configuration

Docker-related files for containerization and deployment:

```
docker/
├── Dockerfile         # Main application Dockerfile
├── docker-compose.yml # Multi-container setup
├── nginx/
│   ├── nginx.conf    # Nginx configuration
│   └── ssl/          # SSL certificates
└── scripts/
    ├── entrypoint.sh # Container startup script
    └── wait-for-it.sh # Service dependency script
```

See [Deployment Guide](./deployment) for Docker setup details.

### 📁 static/ - Static Files

Static assets served by Django or a web server:

```
static/
├── css/               # Stylesheets
├── js/                # JavaScript files
├── images/            # Images and icons
└── admin/             # Admin interface static files
```

Collected during deployment with:
```bash
python manage.py collectstatic
```

### 📁 templates/ - Django Templates

HTML templates for server-side rendering:

```
templates/
├── base.html          # Base template
├── emails/            # Email templates
│   ├── welcome.html
│   └── order_confirmation.html
└── admin/             # Admin customizations (if any)
```

## Key Files

### manage.py

Django's command-line utility for administrative tasks:

```bash
# Common commands
python manage.py runserver          # Start development server
python manage.py migrate            # Run migrations
python manage.py createsuperuser    # Create admin user
python manage.py shell              # Interactive Python shell
```

### pyproject.toml

Poetry configuration file defining project dependencies:

```toml
[tool.poetry]
name = "my-django-cfg-demo"
version = "0.1.0"

[tool.poetry.dependencies]
python = "^3.11"
django-cfg = "^1.0.0"
# ... other dependencies
```

Manage dependencies with:
```bash
poetry add package-name
poetry install
poetry update
```

### requirements.txt

Pip-compatible requirements file, generated from `pyproject.toml`:

```bash
# Generate requirements.txt
poetry export -f requirements.txt --output requirements.txt
```

Used in Docker and production environments.

### README.md

Project documentation with:
- Setup instructions
- Development guidelines
- Deployment procedures
- Team contact information

## File Organization Best Practices

### 1. Keep Configuration Centralized

All configuration should be in `api/config.py`, not scattered across the project.

```python
# ✅ Good: Centralized configuration
class MyConfig(DjangoConfig):
    email: EmailConfig = EmailConfig(...)

# ❌ Bad: Settings in multiple places
EMAIL_HOST = 'smtp.gmail.com'  # In settings.py
TWILIO_SID = 'xxx'             # In constants.py
```

### 2. Follow Django App Structure

Each app should be self-contained:

```
app_name/
├── models.py          # Data models
├── admin.py           # Admin configuration
├── views.py           # View logic
├── serializers.py     # API serializers
├── urls.py            # URL routing
├── tests.py           # Tests
└── migrations/        # Database migrations
```

### 3. Use Meaningful Directory Names

Choose descriptive names that indicate purpose:

```
# ✅ Good
apps/blog/
apps/shop/
core/utils/

# ❌ Bad
app1/
stuff/
misc/
```

### 4. Separate Configuration from Code

Keep environment-specific settings in YAML files:

```yaml
# config.dev.yaml
debug: true
database:
  url: "sqlite:///db/db.sqlite3"

# config.prod.yaml
debug: false
database:
  url: "postgresql://..."
```

## Navigation Between Components

The sample project components are interconnected:

- **Configuration** → Used by all apps and services
- **Models** → Define data structure, used by views and API
- **Admin** → Manages models through web interface
- **API** → Exposes models via REST endpoints
- **Background Tasks** → Process async operations

To understand how these work together:

1. Start with [Configuration Setup](./configuration)
2. Review [Multi-Database Setup](./multi-database) for data layer
3. Explore [Admin Interface](./admin-interface) for management UI
4. Check [API Documentation](./api-documentation) for REST API
5. Learn [Background Tasks](/features/integrations/rearq/overview) for async processing

## Related Topics

- [Configuration Setup](./configuration) - Detailed configuration guide
- [Multi-Database Setup](./multi-database) - Database routing explained
- [Deployment Guide](./deployment) - Production deployment structure

Understanding the project structure helps you navigate and extend the sample project effectively.
