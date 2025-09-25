# 🚀 Django CFG Sample Project

**Complete demonstration of `django_cfg` features and capabilities - a modern approach to Django project configuration.**

> 🎯 **Ready to run!** Email: `admin@example.com` | Password: `admin123`

## ✨ What This Project Demonstrates

### 🔧 **Type-Safe Configuration**
- **Pydantic v2 models** for 100% type safety
- **Environment-aware** smart defaults
- **Zero raw dictionaries** - everything is typed
- **Comprehensive validation** with helpful error messages

### 🗄️ **Database Management**
- **Multiple databases** with automatic routing
- **Simplified routing** - no separate routing rules
- **Connection string parsing** and validation
- **Migration routing** with `migrate_to` option

### 🎨 **Admin Interface**
- **Unfold theme** with beautiful modern UI
- **Custom navigation** and sidebar configuration
- **Dashboard callbacks** with real-time metrics
- **Quick actions** with automatic URL resolution

### ⚙️ **Dynamic Settings**
- **Constance integration** for runtime configuration
- **Automatic admin registration** with Unfold styling
- **Grouped fieldsets** for better organization
- **Type-safe field definitions**

### 🔌 **API Configuration**
- **Django REST Framework** auto-configuration
- **Spectacular (OpenAPI)** documentation
- **Authentication & permissions** setup
- **Pagination** and filtering

### 🌐 **Service Integrations**
- **Email configuration** with multiple backends
- **Telegram notifications** (optional)
- **Cache backends** with automatic setup
- **Static/media files** handling

### 🔗 **URL Management**
- **Automatic URL integration** with `add_django_cfg_urls()`
- **Health check endpoints** built-in
- **Management commands** web interface
- **Debug information** in development

## 📁 Project Structure

```
django_sample/
├── apps/                          # Django applications
│   ├── blog/                     # 📝 Blog with posts and comments
│   ├── shop/                     # 🛒 E-commerce with products and orders  
│   └── users/                    # 👥 Custom user model
├── api/                          # 🔌 DRF API endpoints
│   ├── config.py                 # 🔥 Main configuration (Pydantic)
│   ├── settings.py               # ⚙️ Django settings (auto-generated)
│   ├── urls.py                   # 🔗 URL configuration
│   └── environment/              # 🌍 YAML environment configurations
│       ├── config.dev.yaml       # 🛠️ Development settings
│       ├── config.prod.yaml      # 🚀 Production settings
│       └── loader.py             # 📥 Configuration loader
├── manage.py                     # 🎛️ Django management
├── pyproject.toml               # 📋 Poetry dependencies
├── requirements.txt             # 📋 Pip dependencies
├── db/                          # 🗄️ Database directory
│   ├── db.sqlite3               # 🗄️ Main database
│   ├── blog.sqlite3             # 📝 Blog database (routed)
│   └── shop.sqlite3             # 🛒 Shop database (routed)
└── README.md                    # 📖 This file
```

## 🚀 Quick Start

### 1. Install Dependencies
```bash
cd django_sample/
poetry install
```

### 2. Run Migrations
```bash
# Using Django CFG smart migrator (recommended)
poetry run migrator --auto

# Or specific database
poetry run migrate --database blog_db

# Or traditional way
poetry run python manage.py migrate
```

### 3. Create Superuser (already created!)
```bash
# Already created: admin@example.com / admin123
# Or create your own with enhanced CLI:
poetry run superuser --email your@email.com

# Or traditional way:
poetry run python manage.py createsuperuser
```

### 4. Start Development Server
```bash
# Using enhanced CLI (recommended)
poetry run runserver --port 8000

# Or with custom host/port
poetry run runserver --host 0.0.0.0 --port 3000

# Or traditional way
poetry run python manage.py runserver
```

### 5. 🎯 Explore Features

- **🎨 Admin Interface**: http://127.0.0.1:8000/admin/ (`admin@example.com` / `admin123`)
- **📚 API Documentation**: http://127.0.0.1:8000/api/schema/swagger-ui/
- **💚 Health Check**: http://127.0.0.1:8000/cfg/status/
- **⚡ Management Commands**: http://127.0.0.1:8000/cfg/commands/
- **⚙️ Constance Settings**: http://127.0.0.1:8000/admin/constance/config/

## ⚡ Enhanced CLI with Click

This project includes a powerful CLI built with Click for better UX:

### 🎯 **Main CLI Interface**
```bash
# Show all available commands with help
poetry run cli --help

# Run specific commands with options
poetry run cli runserver --port 3000 --host 0.0.0.0
poetry run cli migrate --database blog_db
poetry run cli show-config --format json
```

### 🚀 **Individual Command Shortcuts**
```bash
# Standard Django commands with enhanced options
poetry run runserver --port 8080 --host 0.0.0.0
poetry run migrate --database blog_db --fake
poetry run makemigrations --dry-run apps.blog
poetry run createsuperuser --email admin@test.com
poetry run collectstatic --noinput --clear

# Django CFG enhanced commands
poetry run migrator --auto --database shop_db
poetry run show-config --format json --include-secrets
poetry run validate-config --show-details --check-connections
poetry run show-urls --format table
poetry run superuser --email admin@example.com
poetry run test-email --to test@example.com
poetry run test-telegram --message "Hello from CLI!"
```

### 💡 **Click Features**
- **🔍 Auto-completion** and validation for all options
- **📚 Built-in help** for every command (`--help`)
- **🎨 Colored output** and better formatting
- **⚡ Type safety** with parameter validation
- **🔧 Flexible options** with sensible defaults

### 📖 **Examples**
```bash
# Get help for any command
poetry run cli migrate --help
poetry run runserver --help

# Use advanced options
poetry run cli show-config --format json --include-secrets
poetry run cli migrator --database blog_db
poetry run cli test-email --to admin@example.com
```

## 🎯 Key Features Demonstrated

### 🔧 Type-Safe Configuration
```python
# api/config.py - Everything is typed and validated!
class SampleProjectConfig(DjangoConfig):
    project_name: str = "Django CFG Sample"
    debug: bool = env.debug
    
    databases: Dict[str, DatabaseConfig] = {
        "default": DatabaseConfig(
            engine="django.db.backends.sqlite3",
            **env.database.parse_url(env.database.url),
        ),
        "blog_db": DatabaseConfig(
            engine="django.db.backends.sqlite3",
            **env.database.parse_url(env.database.url_blog),
            # Routing built-in!
            apps=["apps.blog"],
            operations=["read", "write"],
            migrate_to="default",
        )
    }
```

### ⚙️ Automatic Django Settings
```python
# api/settings.py - One line replaces hundreds!
from api.config import config
locals().update(config.get_all_settings())
```

### 🔗 Smart URL Integration
```python
# api/urls.py - Automatic integration
from django_cfg import add_django_cfg_urls

urlpatterns = [
    path("admin/", admin.site.urls),
    path("blog/", include("apps.blog.urls")),
    # ... your URLs
]

# Automatically adds health checks, commands, etc.
urlpatterns = add_django_cfg_urls(urlpatterns)
```

### 🌍 YAML Environment Configuration
```yaml
# api/environment/config.dev.yaml
secret_key: "django-cfg-sample-dev-key-change-in-production"
debug: true

database:
  url: "sqlite:///db.sqlite3"
  url_blog: "sqlite:///blog.sqlite3"
  url_shop: "sqlite:///shop.sqlite3"

app:
  name: "Django CFG Sample"
  domain: "localhost"
```

## 🔧 Configuration Highlights

### 🗄️ Multiple Databases with Routing
- **`default`**: Main application data (users, sessions, admin)
- **`blog_db`**: Blog posts and comments (routed automatically)
- **`shop_db`**: Products and orders (with migration routing)

### 🎨 Unfold Admin Theme
- **Modern UI** with dark/light theme support
- **Custom navigation** organized by functionality groups
- **Dashboard metrics** with real-time data from callbacks
- **Quick actions** with automatic URL resolution

### ⚙️ Constance Dynamic Settings
- **Runtime configuration** without code changes or restarts
- **Grouped fieldsets** for better organization
- **Type validation** for all field types
- **Unfold integration** for beautiful admin interface

### 🔌 DRF API
- **Auto-configured** REST framework with sensible defaults
- **OpenAPI documentation** with Spectacular integration
- **JWT authentication** with token blacklisting
- **Pagination** and filtering built-in

## 🎨 Customization Examples

### Adding New Apps
```python
# 1. Create app
python manage.py startapp myapp

# 2. Add to api/config.py
project_apps: List[str] = [
    "apps.users",
    "apps.blog", 
    "apps.shop",
    "apps.myapp",  # Add here
]
```

### Database Routing
```python
# Route specific apps to dedicated databases
databases = {
    "analytics_db": DatabaseConfig(
        engine="django.db.backends.postgresql",
        name="analytics_data",
        apps=["apps.analytics"],  # Route this app
        operations=["read", "write", "migrate"],
        migrate_to="default",  # Migrations go to main DB
    )
}
```

### Custom Dashboard Metrics
```python
# api/config.py
def dashboard_callback(request, context):
    from apps.blog.models import Post
    from apps.shop.models import Order
    
    custom_cards = [
        StatCard(
            title="Blog Posts",
            value=str(Post.objects.count()),
            description="Total published posts",
            icon="article"
        ),
        StatCard(
            title="Orders Today", 
            value=str(Order.objects.filter(
                created_at__date=timezone.now().date()
            ).count()),
            description="Orders placed today",
            icon="shopping_cart"
        )
    ]
    
    context["cards"].extend([card.model_dump() for card in custom_cards])
    return context
```

## 🧪 Testing & Validation

```bash
# Run all tests
poetry run python manage.py test

# Check Django configuration
poetry run python manage.py check

# Validate django_cfg settings
poetry run python manage.py shell -c "from api.config import config; print('✅ Configuration valid!')"

# Check database connections
poetry run python manage.py dbshell --database=blog_db
```

## 🚀 Deployment

### Environment Variables
```bash
# Set environment for production
export IS_PROD=true
export DEBUG=false

# Or use .env file
echo "IS_PROD=true" > .env
echo "DEBUG=false" >> .env
```

### Production Settings
The project automatically switches to `config.prod.yaml` when `IS_PROD=true`.

## 📚 Learn More

- **Django CFG**: Modern Django configuration management
- **Unfold Theme**: https://github.com/unfoldadmin/django-unfold
- **Django REST Framework**: https://www.django-rest-framework.org/
- **Constance**: https://github.com/jazzband/django-constance
- **Pydantic**: https://docs.pydantic.dev/

## 🤝 Contributing

This sample project demonstrates django_cfg capabilities. 

Found a bug or have a suggestion? Please open an issue!

## 📄 License

MIT License - see LICENSE file for details.
