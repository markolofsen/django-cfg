# 🚀 Django CFG CLI

Powerful command-line interface for django-cfg - a production-ready Django configuration framework with automatic project setup and configuration.

## 📦 Installation

### Requirements

- **Python 3.12+** - Modern Python features and performance improvements
- **Django 4.2+** - Latest stable Django version
- **Poetry** (recommended) or **pip** - Package management

### Install

```bash
pip install django-cfg
# or
poetry add django-cfg
```

> ⚠️ **Python Version Check**: django-cfg automatically checks your Python version and provides helpful upgrade instructions if you're using Python < 3.12.

## 🎯 Commands

### `django-cfg create-project`

Creates a new Django project with full automatic setup:

- ✅ **Automatic structure creation** - `db/`, `cache/` directories
- ✅ **Dependency installation** - Poetry or pip
- ✅ **Run migrations** - ready database
- ✅ **Template cleaning** - no local development dependencies
- ✅ **Production-ready** - everything configured out of the box

#### Basic Usage

```bash
# Full automatic installation
django-cfg create-project "My Awesome Project"

# Create in specific directory
django-cfg create-project "My Project" --path ./projects/

# Use pip instead of Poetry
django-cfg create-project "My Project" --use-pip
```

#### Installation Control

```bash
# Skip dependency installation
django-cfg create-project "My Project" --no-deps

# Skip automatic setup (directories, migrations)
django-cfg create-project "My Project" --no-setup

# Overwrite existing directory
django-cfg create-project "My Project" --force

# Full control - only create files
django-cfg create-project "My Project" --no-deps --no-setup
```

#### What Happens Automatically

1. **Template extraction** from archive with local-dev blocks cleaning
2. **Structure creation**:
   - `db/` - for SQLite database
   - `cache/` - for caching
   - `.gitignore` - proper exclusions
   - `README.md` - project documentation
3. **Dependency installation** via Poetry or pip
4. **Run migrations** via `poetry run cli migrator` or `manage.py migrate`
5. **Ready project** for development

### `django-cfg info`

Shows information about django-cfg and system:

```bash
# Basic information
django-cfg info

# Detailed information
django-cfg info --verbose
```

**Displays:**
- 📦 Package version and Python
- 📋 Project template status
- 🔧 Core dependencies (django, pydantic, click)
- 🌐 Service integrations (Twilio, SendGrid, OpenAI, Telegram)
- 🎨 Admin & UI (django-unfold, constance)
- 📊 API & documentation (DRF, drf-spectacular)
- ⚡ Background tasks (dramatiq, redis)
- 🛠️ Development tools (ngrok)

## 🏗️ Generated Project Structure

```
my_awesome_project/
├── 📁 api/                    # django-cfg configuration
│   ├── config.py              # Main configuration
│   ├── environment/           # Environment settings
│   │   ├── config.dev.yaml    # Development
│   │   ├── config.prod.yaml   # Production
│   │   └── config.test.yaml   # Testing
│   ├── settings.py            # Generated Django settings
│   └── urls.py                # Root URLs
├── 📁 apps/                   # Django applications
│   ├── blog/                  # Blog example
│   ├── profiles/              # User profiles
│   └── shop/                  # E-commerce example
├── 📁 core/                   # Utilities and management commands
├── 📁 db/                     # SQLite database (auto-created)
├── 📁 cache/                  # Cache files (auto-created)
├── 📁 docker/                 # Docker configuration
├── 📁 static/                 # Static files
├── 📁 templates/              # Django templates
├── 📄 manage.py               # Django management
├── 📄 cli.py                  # Extended CLI
├── 📄 pyproject.toml          # Poetry config (cleaned from local-dev)
├── 📄 requirements.txt        # pip dependencies
├── 📄 package.json            # npm scripts
├── 📄 .gitignore              # Git exclusions
└── 📄 README.md               # Project documentation
```

## ⚙️ Quick Start

### 1. Create Project

```bash
django-cfg create-project "My Blog"
```

**Output:**
```
📋 Using template archive: django_sample.zip
📂 Extracting template from archive...
✅ Extracted 339 files from template
✅ Project 'My Blog' created successfully!
📁 Location: /current/dir/my_blog

🔧 Setting up project structure...
📁 Created database directory: db/
📁 Created cache directory: cache/

📦 Installing dependencies with Poetry...
✅ Dependencies installed successfully

🔄 Running initial project setup...
🔄 Running initial migrations...
✅ Initial migrations completed successfully
✅ Project is ready to use!
```

### 2. Navigate to Project

```bash
cd my_blog
```

### 3. Configure Settings

```bash
# Copy and edit configuration
cp api/environment/config.dev.yaml api/environment/config.local.yaml
# Edit config.local.yaml with your settings
```

### 4. Create Superuser

```bash
poetry run python manage.py createsuperuser
```

### 5. Run Server

```bash
poetry run cli runserver
# or
poetry run python manage.py runserver
```

## 🔧 Configuration

Edit `api/environment/config.local.yaml`:

```yaml
# Basic settings
debug: true
secret_key: "your-secret-key-here"

# Database
database:
  default:
    engine: "sqlite"
    name: "db/db.sqlite3"

# API keys
api_keys:
  twilio:
    account_sid: "ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
    auth_token: "your_twilio_auth_token"
    verify_service_sid: "VAxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
  sendgrid_api_key: "SG.your_sendgrid_api_key"
  openai_api_key: "sk-your_openai_api_key"

# Email settings
email:
  default_from: "noreply@yourapp.com"
  backend: "sendgrid"

# Telegram bot
telegram:
  bot_token: "your_telegram_bot_token"
  chat_id: 123456789

# Redis (optional)
redis:
  default:
    host: "localhost"
    port: 6379
    db: 0
```

## 📱 Service Usage

### Twilio OTP

```python
from django_cfg import send_sms_otp, send_whatsapp_otp, send_email_otp, verify_otp

# SMS OTP
success, message = send_sms_otp("+1234567890")

# WhatsApp OTP with SMS fallback
success, message = send_whatsapp_otp("+1234567890", fallback_to_sms=True)

# Email OTP
success, message, code = send_email_otp("user@example.com")

# Verify OTP
is_valid, result = verify_otp("+1234567890", "123456")
```

### Telegram Notifications

```python
from django_cfg import send_telegram_message

send_telegram_message("New user registered!")
```

## 🐳 Docker Deployment

```bash
# Build and run
docker-compose up -d

# Production with nginx
docker-compose -f docker-compose.yml -f docker-compose.nginx.yml up -d
```

## 🛠️ Management Commands

### Poetry Commands

```bash
# Install dependencies
poetry install

# Activate environment
poetry shell

# Run server
poetry run cli runserver

# Run with ngrok
poetry run cli runserver-ngrok

# Migrations
poetry run cli migrator

# Background tasks
poetry run cli rundramatiq
```

### npm Scripts

```bash
# Development
npm run dev

# Development with ngrok
npm run dev:ngrok

# Migrations
npm run migrate

# Generate OpenAPI clients
npm run generate

# Background tasks
npm run tasks:worker
npm run tasks:status
npm run tasks:clear
```

## 🎯 Usage Examples

### Creating Different Project Types

```bash
# Blog
django-cfg create-project "My Blog"

# E-commerce
django-cfg create-project "My Shop"

# API-only project
django-cfg create-project "My API"

# Corporate application
django-cfg create-project "Corporate App"
```

### Different Installation Methods

```bash
# Full automatic installation (recommended)
django-cfg create-project "My Project"

# pip only
django-cfg create-project "My Project" --use-pip

# No automatic setup
django-cfg create-project "My Project" --no-setup

# Files only, no dependencies
django-cfg create-project "My Project" --no-deps --no-setup

# Specific directory
django-cfg create-project "My Project" --path ~/projects/

# Overwrite existing
django-cfg create-project "My Project" --force
```

## 🔍 Useful Commands

```bash
# System information
django-cfg info --verbose

# Command help
django-cfg --help
django-cfg create-project --help

# Version
django-cfg --version

# Project structure
npm run tree

# Task status
npm run tasks:status

# Clear cache
python manage.py clear_cache
```

## 🌟 Django-CFG Features

### 🔧 Configuration
- **Type-safe settings** with Pydantic v2
- **YAML configurations** for different environments
- **Automatic validation** of settings
- **Environment variables** with fallback

### 📱 Integrations
- **Twilio** - SMS, WhatsApp, Email OTP
- **SendGrid** - email services
- **Telegram Bot** - notifications and alerts
- **OpenAI** - AI integration
- **Redis** - caching and sessions

### 🎨 UI/UX
- **Django Unfold** - modern admin interface
- **Django Constance** - real-time settings
- **Automatic documentation** OpenAPI/Swagger
- **JWT authentication** out of the box

### ⚡ Performance
- **Dramatiq** - background tasks
- **Redis** - caching
- **Multi-database** with automatic routing
- **Optimized settings** for production

### 🐳 Deployment
- **Docker** ready configurations
- **Nginx** settings
- **Environment** management
- **Ready deployment scripts**

## 🐛 Troubleshooting

### Template Not Found

```bash
# Check installation
django-cfg info --verbose

# Reinstall
pip uninstall django-cfg
pip install django-cfg
```

### Permission Errors

```bash
# Force overwrite
django-cfg create-project "My Project" --force

# Or remove directory manually
rm -rf my_project/
django-cfg create-project "My Project"
```

### Dependency Installation Errors

```bash
# Create without dependencies
django-cfg create-project "My Project" --no-deps

# Install manually
cd my_project/
poetry install  # or pip install -r requirements.txt
```

### Migration Errors

```bash
# Create without auto-setup
django-cfg create-project "My Project" --no-setup

# Run migrations manually
cd my_project/
poetry run cli migrator
# or
python manage.py migrate
```

## 🤝 CLI Development

### Adding New Commands

1. Create command file in `src/django_cfg/cli/commands/`:

```python
# src/django_cfg/cli/commands/my_command.py
import click
from ..utils import get_package_info

@click.command()
@click.option("--option", help="Command option")
def my_command(option: str):
    """My custom command description."""
    click.echo(f"Running my command with option: {option}")
```

2. Register in `src/django_cfg/cli/main.py`:

```python
from .commands.my_command import my_command

cli.add_command(my_command)
```

### Using Utilities

```python
from ..utils import (
    get_package_info,
    find_template_archive, 
    get_template_info,
    check_dependencies,
    validate_project_name
)

# Package information
info = get_package_info()
print(f"Version: {info['version']}")

# Find template archive
archive = find_template_archive()
if archive:
    print(f"Template found: {archive}")

# Check dependencies
deps = check_dependencies({"django": "django"})
print(f"Django installed: {deps['django']}")
```

## 📚 Documentation

- **Django CFG**: https://djangocfg.com
- **GitHub**: https://github.com/markolofsen/django-cfg
- **PyPI**: https://pypi.org/project/django-cfg/
- **Examples**: https://github.com/markolofsen/django-cfg/tree/main/examples

## 📄 License

MIT License - see LICENSE file for details.

---

**Powered by django-cfg** 🚀 - Production-ready Django configuration with automatic setup