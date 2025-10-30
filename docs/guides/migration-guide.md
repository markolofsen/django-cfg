---
title: Migration Guide
description: Django-CFG migration guide guide. Practical tutorial for migration guide with real-world examples, troubleshooting tips, and production patterns.
sidebar_label: Migration Guide
sidebar_position: 5
keywords:
  - migrate to django-cfg
  - django-cfg migration
  - settings.py to django-cfg
  - django configuration migration
---

import { HowToSchema } from '@site/src/components/Schema';

<HowToSchema
  name="Migrate Your Django Project to Django-CFG"
  description="Complete migration guide for converting existing Django projects to Django-CFG with three migration strategies and step-by-step instructions"
  steps={[
    { text: 'Choose migration strategy (Fresh Start, Gradual, or Side-by-Side)', url: '#migration-strategies' },
    { text: 'Install Django-CFG in your project', url: '#step-1-install-django-cfg' },
    { text: 'Create configuration class with type hints', url: '#step-2-create-configuration-class' },
    { text: 'Replace settings.py with Django-CFG imports', url: '#step-4-replace-settings-file' },
    { text: 'Migrate database and custom apps', url: '#step-3-copy-your-apps' },
    { text: 'Test migration with validation commands', url: '#step-6-test-and-verify' }
  ]}
/>

# Migration Guide

Migrate your existing Django project to Django-CFG and unlock type-safe configuration, modern admin interface, and powerful built-in features.

> **⚠️ Note:** This guide uses simplified examples. For production, use YAML-based configuration as shown in [Configuration Guide](/getting-started/configuration) and [First Project](/getting-started/first-project).

## Migration Strategies

Choose the migration approach that best fits your project:

### Option 1: Fresh Start (Recommended)

**Best for:** New features, major refactoring, or when you want all Django-CFG benefits immediately.

**Pros:**
- ✅ Get all Django-CFG features instantly
- ✅ Clean, modern project structure
- ✅ No legacy configuration issues
- ✅ Built-in best practices

**Cons:**
- ⚠️ Requires data migration
- ⚠️ More initial work

### Option 2: Gradual Migration

**Best for:** Large existing projects, production systems, or when you need minimal disruption.

**Pros:**
- ✅ Minimal disruption to existing code
- ✅ Gradual feature adoption
- ✅ Keep existing data and structure
- ✅ Lower risk

**Cons:**
- ⚠️ Slower to get full benefits
- ⚠️ May have configuration conflicts

### Option 3: Side-by-Side Comparison

**Best for:** Learning Django-CFG, evaluating features, or planning a migration.

**Pros:**
- ✅ No risk to existing project
- ✅ Perfect for learning
- ✅ Easy feature comparison
- ✅ Can cherry-pick features

**Cons:**
- ⚠️ Doesn't migrate existing project
- ⚠️ Requires maintaining two codebases

## Option 1: Fresh Start Migration

### Step 1: Create New Django-CFG Project

```bash
# Create new project with Django-CFG
django-cfg create-project "My Migrated Project"
cd my-migrated-project
```

### Step 2: Export Data from Old Project

```bash
# In your old project directory
python manage.py dumpdata --natural-foreign --natural-primary > data_export.json

# Export specific apps (recommended)
python manage.py dumpdata auth.User > users.json
python manage.py dumpdata myapp > myapp_data.json
```

### Step 3: Copy Your Apps

```bash
# Copy your custom apps to new project
cp -r /path/to/old/project/myapp ./
cp -r /path/to/old/project/anotherapp ./
```

### Step 4: Update Configuration

```python
# config.py in new project
from django_cfg import DjangoConfig, DatabaseConfig

class MyConfig(DjangoConfig):
    project_name: str = "My Migrated Project"
    secret_key: str = "<from-yaml-config>"  # Set via environment/config.yaml
    debug: bool = False
    
    # Add your custom apps
    project_apps: list[str] = [
        "myapp",
        "anotherapp",
    ]
    
    # Copy database settings from old project
    databases: dict[str, DatabaseConfig] = {
        "default": DatabaseConfig(
            engine="django.db.backends.postgresql",
            name="<from-yaml-config>"  # Set via environment/config.yaml,
            user="<from-yaml-config>"  # Set via environment/config.yaml,
            password="<from-yaml-config>"  # Set via environment/config.yaml,
            host="<from-yaml-config>"  # Set via environment/config.yaml,
            port=5432,
        )
    }

config = MyConfig()
```

### Step 5: Import Data

```bash
# Run migrations first
python manage.py migrate

# Import your data
python manage.py loaddata users.json
python manage.py loaddata myapp_data.json
```

### Step 6: Test and Verify

```bash
# Validate configuration
python manage.py validate_config

# Test your app
python manage.py runserver

# Check admin interface
python manage.py createsuperuser
# Visit http://localhost:8000/admin/
```

## Option 2: Gradual Migration

### Step 1: Install Django-CFG

```bash
# In your existing project
pip install django-cfg
```

### Step 2: Create Configuration Class

Create `config.py` in your project root:

```python
# config.py
from django_cfg import DjangoConfig
from typing import List

class MyConfig(DjangoConfig):
    """Gradual migration configuration"""
    
    # Copy existing settings with type hints
    project_name: str = "Existing Project"
    secret_key: str = "your-existing-secret-key"  # Copy from old settings
    debug: bool = True  # Copy from old settings
    
    # Copy your INSTALLED_APPS
    project_apps: List[str] = [
        "myapp",
        "anotherapp",
        # ... your existing apps
    ]
    
    # Copy database configuration
    # (Convert your existing DATABASES setting)

config = MyConfig()
```

### Step 3: Backup Current Settings

```bash
# Backup your current settings
cp settings.py settings_backup.py
```

### Step 4: Replace Settings File

```python
# settings.py
from config import config

# Import all Django-CFG generated settings
globals().update(config.get_all_settings())

# Keep any custom settings that Django-CFG doesn't handle
CUSTOM_SETTING = "custom_value"
THIRD_PARTY_SETTING = "third_party_value"

# Temporarily keep old settings that you haven't migrated yet
# TODO: Migrate these to config.py
# OLD_SETTING = "old_value"
```

### Step 5: Test Migration

```bash
# Test that everything still works
python manage.py check
python manage.py runserver
```

### Step 6: Gradual Feature Adoption

Enable Django-CFG features one by one:

```python
# config.py - Add features gradually
from django_cfg import DjangoConfig, UnfoldConfig, SpectacularConfig

class MyConfig(DjangoConfig):
    # ... existing settings ...

    # Week 1: Enable beautiful admin
    unfold: UnfoldConfig | None = UnfoldConfig()

    # Week 2: Enable API documentation
    spectacular: SpectacularConfig | None = SpectacularConfig()

    # Week 3: Enable built-in modules
    enable_support: bool = True
    enable_accounts: bool = True

    # Week 4: Enable advanced features
    enable_newsletter: bool = True
    enable_leads: bool = True
```

### Step 7: Clean Up Old Settings

Remove old settings from `settings.py` as you migrate them to `config.py`:

```python
# settings.py - Keep getting smaller
from config import config
globals().update(config.get_all_settings())

# Only custom settings remain
CUSTOM_MIDDLEWARE = ["myapp.middleware.CustomMiddleware"]
```

## Option 3: Side-by-Side Comparison

### Step 1: Create Reference Project

```bash
# Create Django-CFG project for comparison
mkdir django-cfg-reference
cd django-cfg-reference
django-cfg create-project "Reference Project"
```

### Step 2: Compare Configurations

```python
# Compare your old settings.py with config.py
# Look for patterns and improvements

# Old settings.py (500+ lines)
DEBUG = True
SECRET_KEY = "..."
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        # ... lots of configuration
    }
}
# ... 400+ more lines

# New config.py (50 lines)
class MyConfig(DjangoConfig):
    debug: bool = True
    secret_key: str = "<from-yaml-config>"  # Set via environment/config.yaml
    databases: dict[str, DatabaseConfig] = {
        "default": DatabaseConfig(
            engine="django.db.backends.postgresql",
            name="<from-yaml-config>"  # Set via environment/config.yaml,
            # ... type-safe configuration
        )
    }
```

### Step 3: Feature Comparison

Test Django-CFG features in the reference project:

```bash
# Test admin interface
python manage.py runserver
# Visit http://localhost:8000/admin/

# Test API documentation
# Visit http://localhost:8000/api/docs/

# Test CLI commands
python manage.py info
python manage.py validate_config
```

### Step 4: Plan Migration

Create a migration plan based on your comparison:

```markdown
# Migration Plan

## Phase 1: Core Configuration (Week 1)
- [ ] Convert settings.py to config.py
- [ ] Add type hints to all settings
- [ ] Test basic functionality

## Phase 2: Admin Interface (Week 2)
- [ ] Enable Unfold admin
- [ ] Customize admin interface
- [ ] Train team on new admin

## Phase 3: API Features (Week 3)
- [ ] Enable API documentation
- [ ] Set up API zones
- [ ] Generate API clients

## Phase 4: Built-in Modules (Week 4)
- [ ] Enable support system
- [ ] Enable user management
- [ ] Enable newsletter system
```

## Common Migration Patterns

### From django-environ

```python
# Old (django-environ)
import environ
env = environ.Env()
DEBUG = env.bool('DEBUG', default=False)
SECRET_KEY = env('SECRET_KEY')
DATABASE_URL = env('DATABASE_URL')

# New (Django-CFG)
from django_cfg import DjangoConfig

class MyConfig(DjangoConfig):
    debug: bool = False
    secret_key: str = "<from-yaml-config>"  # Set via environment/config.yaml
    database_url: str = "<from-yaml-config>"  # Set via environment/config.yaml
```

### From python-decouple

```python
# Old (python-decouple)
from decouple import config
DEBUG = config('DEBUG', default=False, cast=bool)
SECRET_KEY = config('SECRET_KEY')
ALLOWED_HOSTS = config('ALLOWED_HOSTS', cast=lambda v: [s.strip() for s in v.split(',')])

# New (Django-CFG)
from django_cfg import DjangoConfig
from typing import List

class MyConfig(DjangoConfig):
    debug: bool = False
    secret_key: str = "<from-yaml-config>"  # Set via environment/config.yaml
    security_domains: List[str] = ["myapp.com"]  # Auto-generates ALLOWED_HOSTS, CORS, SSL
```

### From django-configurations

```python
# Old (django-configurations)
from configurations import Configuration

class Development(Configuration):
    DEBUG = True
    SECRET_KEY = 'dev-key'

# New (Django-CFG)
from django_cfg import DjangoConfig

from .environment import env

class MyConfig(DjangoConfig):
    debug: bool = True
    secret_key: str = env.secret_key  # Loaded from config.yaml
```

### Complex Database Configuration

```python
# Old settings.py
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME'),
        'USER': os.environ.get('DB_USER'),
        'PASSWORD': os.environ.get('DB_PASSWORD'),
        'HOST': os.environ.get('DB_HOST', 'localhost'),
        'PORT': os.environ.get('DB_PORT', '5432'),
        'OPTIONS': {
            'sslmode': 'require',
        },
    },
    'analytics': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('ANALYTICS_DB_NAME'),
        'USER': os.environ.get('ANALYTICS_DB_USER'),
        'PASSWORD': os.environ.get('ANALYTICS_DB_PASSWORD'),
        'HOST': os.environ.get('ANALYTICS_DB_HOST'),
        'PORT': '5432',
    }
}

# New config.py
from django_cfg import DjangoConfig
from django_cfg.models import DatabaseConfig

class MyConfig(DjangoConfig):
    databases: dict[str, DatabaseConfig] = {
        "default": DatabaseConfig(
            engine="django.db.backends.postgresql",
            name="<from-yaml-config>"  # Set via environment/config.yaml,
            user="<from-yaml-config>"  # Set via environment/config.yaml,
            password="<from-yaml-config>"  # Set via environment/config.yaml,
            host="${DB_HOST:localhost}",
            port=5432,
            sslmode="require",
        ),
        "analytics": DatabaseConfig(
            engine="django.db.backends.postgresql",
            name="<from-yaml-config>"  # Set via environment/config.yaml,
            user="<from-yaml-config>"  # Set via environment/config.yaml,
            password="<from-yaml-config>"  # Set via environment/config.yaml,
            host="<from-yaml-config>"  # Set via environment/config.yaml,
            port=5432,
            routing_apps=["analytics", "reports"],
        ),
    }
```

## ⚠️ Migration Gotchas

### 1. Custom Middleware Order

```python
# Django-CFG adds its own middleware
# Make sure your custom middleware is compatible

class MyConfig(DjangoConfig):
    @property
    def middleware(self) -> list:
        middleware = super().middleware
        
        # Add your custom middleware in the right position
        middleware.insert(0, "myapp.middleware.CustomMiddleware")
        
        return middleware
```

### 2. Third-Party App Settings

```python
# Some third-party apps need special settings
# Keep them in settings.py temporarily

# settings.py
from config import config
globals().update(config.get_all_settings())

# Third-party app settings that need special handling
CELERY_BROKER_URL = config.redis_url
CELERY_RESULT_BACKEND = config.redis_url

# TODO: Move to config.py when Django-CFG supports them
```

### 3. Static Files in Production

```python
# Make sure static files work in production
class MyConfig(DjangoConfig):
    # ... other settings ...
    
    @property
    def static_root(self) -> str:
        if self.is_production:
            return "/var/www/static/"
        return super().static_root
```

## 🧪 Testing Your Migration

### 1. Automated Testing

```python
# tests/test_migration.py
from django.test import TestCase
from config import config

class MigrationTest(TestCase):
    def test_configuration_valid(self):
        """Test that configuration is valid"""
        settings = config.get_all_settings()
        
        # Test required settings
        self.assertIn("SECRET_KEY", settings)
        self.assertIn("DATABASES", settings)
        self.assertIn("INSTALLED_APPS", settings)
        
    def test_database_connection(self):
        """Test database connectivity"""
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            self.assertEqual(result[0], 1)
            
    def test_admin_accessible(self):
        """Test admin interface"""
        response = self.client.get("/admin/")
        self.assertEqual(response.status_code, 302)  # Redirect to login
```

### 2. Manual Testing Checklist

```bash
# ✅ Configuration validation
python manage.py validate_config

# ✅ Database connectivity
python manage.py dbshell

# ✅ Admin interface
python manage.py runserver
# Visit http://localhost:8000/admin/

# ✅ API documentation (if enabled)
# Visit http://localhost:8000/api/docs/

# ✅ Static files
python manage.py collectstatic --dry-run

# ✅ Your custom functionality
python manage.py test
```

## Migration Benefits

After migration, you'll have:

| Feature | Before | After |
|---------|--------|-------|
| **Configuration** | 500+ line settings.py | Type-safe config.py |
| **Type Safety** | None | 100% validated |
| **Admin Interface** | Basic Django admin | Modern Unfold admin |
| **API Docs** | Manual setup | Auto-generated |
| **User Management** | Basic User model | OTP auth + profiles |
| **Background Tasks** | Manual Celery setup | Built-in ReArq |
| **Support System** | Build from scratch | Ready-to-use |
| **Newsletter** | Third-party service | Built-in system |
| **Lead Management** | Custom solution | Built-in CRM |
| **Environment Detection** | Manual configuration | Automatic |
| **CLI Tools** | Basic Django commands | Enhanced commands |
| **IDE Support** | Basic | Full IntelliSense |

## Post-Migration Steps

### 1. Team Training

```bash
# Show team the new features
python manage.py info
python manage.py --help

# Demo the admin interface
python manage.py runserver
# Visit http://localhost:8000/admin/
```

### 2. Documentation Updates

Update your project documentation to reflect Django-CFG patterns:

```markdown
# Old README
1. Copy settings.py.example to settings.py
2. Edit 50+ settings manually
3. Hope everything works

# New README
1. Copy .env.example to .env
2. Edit 5 environment variables
3. Everything just works!
```

### 3. CI/CD Updates

```yaml
# .github/workflows/django.yml
- name: Validate Configuration
  run: python manage.py validate_config --strict

- name: Run Enhanced Tests
  run: |
    python manage.py test
    python manage.py check_settings
```

## 🆘 Troubleshooting

### Configuration Errors

```bash
# Debug configuration issues
python manage.py show_config --debug
python manage.py validate_config --verbose
```

### Import Errors

```python
# If you get import errors, check your PYTHONPATH
import sys
sys.path.insert(0, '/path/to/your/project')
```

### Database Issues

```bash
# Check database configuration
python manage.py dbshell
python manage.py migrate --dry-run
```

## See Also

### Migration & Setup

**Getting Started:**
- **[Installation Guide](/getting-started/installation)** - Install Django-CFG
- **[Configuration Guide](/getting-started/configuration)** - Configure your project
- **[First Project](/getting-started/first-project)** - Complete tutorial
- **[Django-CFG vs Alternatives](/getting-started/django-cfg-vs-alternatives)** - Feature comparison

**Migration Resources:**
- **[Troubleshooting](/guides/troubleshooting)** - Common migration issues
- **[Configuration Problems Solved](/guides/django-configuration-problems-solved)** - Real-world fixes
- **[Production Config](/guides/production-config)** - Production migration patterns

### Configuration

**Core Configuration:**
- **[Configuration Models](/fundamentals/configuration)** - Complete config API
- **[Type-Safe Configuration](/fundamentals/core/type-safety)** - Pydantic patterns
- **[Environment Detection](/fundamentals/configuration/environment)** - Multi-environment setup
- **[Environment Variables](/fundamentals/configuration/environment)** - Secrets management

**Infrastructure:**
- **[Database Configuration](/fundamentals/database)** - Multi-database migration
- **[Cache Configuration](/fundamentals/configuration/cache)** - Redis/Memcached setup
- **[Security Settings](/fundamentals/configuration/security)** - CORS, CSRF, SSL migration

### Features & Integration

**Built-in Apps:**
- **[Built-in Apps Overview](/features/built-in-apps/overview)** - Enable production apps
- **[User Management](/features/built-in-apps/user-management/overview)** - Accounts, Support
- **[AI Agents](/ai-agents/introduction)** - AI workflow automation

**Integrations:**
- **[ReArq Integration](/features/integrations/rearq/overview)** - Background tasks
- **[Ngrok Integration](/features/integrations/ngrok/overview)** - Webhook testing
- **[Email Module](/features/modules/email/overview)** - Email configuration

### Tools & Deployment

**CLI Tools:**
- **[CLI Introduction](/cli/introduction)** - Enhanced management commands
- **[Core Commands](/cli/commands/core-commands)** - Essential CLI tools
- **[Custom Commands](/cli/custom-commands)** - Build your own

**Deployment:**
- **[Docker Deployment](/guides/docker/production)** - Containerized deployment
- **[Logging Configuration](/deployment/logging)** - Production logging

Transform your Django project with Django-CFG! 🎯

TAGS: migration, upgrade, existing-project, gradual-migration, fresh-start
DEPENDS_ON: [installation, configuration]
USED_BY: [production-config, deployment]
