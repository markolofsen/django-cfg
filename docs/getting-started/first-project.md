---
title: Your First Django-CFG Project
description: Learn first project in Django-CFG. Step-by-step guide to your first django-cfg project with code examples, best practices, and production-ready configuration.
sidebar_label: First Project
sidebar_position: 4
keywords:
  - django-cfg first project
  - django-cfg tutorial
  - create django-cfg project
  - django-cfg example
---

import { HowToSchema } from '@site/src/components/Schema';
import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

<HowToSchema
  name="Create Your First Django-CFG Project"
  description="Step-by-step tutorial to create a production-ready SaaS application with type-safe YAML configuration using Django-CFG"
  steps={[
    { text: 'Create project structure and virtual environment', url: '#1-create-project-structure' },
    { text: 'Create environment configuration module with Pydantic models', url: '#2-create-environment-configuration-module' },
    { text: 'Create type-safe configuration class', url: '#3-create-configuration-class' },
    { text: 'Update settings.py to use Django-CFG', url: '#4-update-settingspy' },
    { text: 'Create your first Django app', url: '#5-create-workspace-app' },
    { text: 'Run migrations and create superuser', url: '#6-run-migrations-and-create-superuser' },
    { text: 'Access your application and admin panel', url: '#7-access-your-application' }
  ]}
/>

# Your First Django-CFG Project

:::tip[What You'll Build]
A complete multi-tenant SaaS application with type-safe YAML configuration, workspace management, and production-ready setup in **under 15 minutes**.
:::

## Project Creation Flow

```mermaid
graph TB
    START[Start] --> STEP1[1. Create Project<br/>Structure]
    STEP1 --> STEP2[2. Create Environment<br/>Module]
    STEP2 --> STEP3[3. Create Config<br/>Class]
    STEP3 --> STEP4[4. Update<br/>settings.py]
    STEP4 --> STEP5[5. Create Django<br/>App]
    STEP5 --> STEP6[6. Run Migrations]
    STEP6 --> STEP7[7. Access<br/>Application]
    STEP7 --> END[SaaS Platform Ready! 🎉]
```

## Goal

Create a Django-based SaaS platform with [type-safe YAML configuration](/getting-started/configuration) using Django-CFG.

## Prerequisites

:::info[Requirements]
Before starting, ensure you have:
- ✅ Python 3.12+ installed ([Installation Guide](/getting-started/installation))
- ✅ Basic Django knowledge
- ✅ Code editor with Python support (VS Code, PyCharm, etc.)
- ✅ Command line/terminal access
:::

## Step-by-Step Tutorial

### 1. Create Project Structure

<Tabs groupId="operating-systems">
  <TabItem value="unix" label="Linux/macOS" default>

```bash
# Create project directory
mkdir saas-platform
cd saas-platform

# Create virtual environment
python3.12 -m venv .venv
source .venv/bin/activate

# Install Django and Django-CFG
pip install django django-cfg

# Create Django project
django-admin startproject core .
```

  </TabItem>
  <TabItem value="windows" label="Windows">

```powershell
# Create project directory
mkdir saas-platform
cd saas-platform

# Create virtual environment
python -m venv .venv
.venv\Scripts\activate

# Install Django and Django-CFG
pip install django django-cfg

# Create Django project
django-admin startproject core .
```

:::warning[Windows PowerShell]
If you get an execution policy error, run:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```
:::

  </TabItem>
</Tabs>

:::tip[Verify Installation]
Check that Django-CFG is installed correctly:
```bash
python -c "import django_cfg; print(django_cfg.__version__)"
```
:::

### 2. Create Environment Configuration Module

Create directory structure:

```
saas-platform/
├── core/
│   ├── __init__.py
│   ├── environment/          # New directory
│   │   ├── __init__.py       # New file
│   │   ├── loader.py         # New file
│   │   └── config.dev.yaml   # New file
│   ├── config.py             # New file
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
└── manage.py
```

**core/environment/__init__.py:**

```python
"""Environment configuration loader."""
from .loader import env

__all__ = ["env"]
```

**core/environment/loader.py:**

```python
"""
Environment configuration with [Pydantic models](/fundamentals/core/type-safety) and YAML loading.

Based on django-cfg libs/django_cfg_opensource/sample/django/api/environment/loader.py
"""
import os
from pathlib import Path
from pydantic import BaseModel, Field, computed_field
from pydantic_yaml import parse_yaml_file_as


# Environment detection
IS_DEV = os.environ.get("IS_DEV", "").lower() in ("true", "1", "yes")
IS_PROD = os.environ.get("IS_PROD", "").lower() in ("true", "1", "yes")
IS_TEST = os.environ.get("IS_TEST", "").lower() in ("true", "1", "yes")

# Default to development
if not any([IS_DEV, IS_PROD, IS_TEST]):
    IS_DEV = True


class DatabaseConfig(BaseSettings):
    """Database configuration."""
    url: str = Field(default="sqlite:///db.sqlite3")

    model_config = SettingsConfigDict(
        env_prefix="DATABASE__",
        env_nested_delimiter="__",
    )


class AppConfig(BaseSettings):
    """Application configuration."""
    name: str = Field(default="SaaS Platform")
    site_url: str = Field(default="http://localhost:3000")
    api_url: str = Field(default="http://localhost:8000")

    model_config = SettingsConfigDict(
        env_prefix="APP__",
        env_nested_delimiter="__",
    )


class EnvironmentMode(BaseSettings):
    """Environment mode detection."""
    is_test: bool = Field(default=False)
    is_dev: bool = Field(default=False)
    is_prod: bool = Field(default=False)

    @model_validator(mode="after")
    def set_default_env(self):
        """Set development as default if no env specified."""
        if not any([self.is_test, self.is_dev, self.is_prod]):
            self.is_dev = True
        return self

    @computed_field
    @property
    def env_mode(self) -> str:
        """Get environment mode string."""
        if self.is_test:
            return "test"
        elif self.is_dev:
            return "development"
        elif self.is_prod:
            return "production"
        return "development"


class EnvironmentConfig(BaseSettings):
    """Complete environment configuration."""

    # Core settings
    secret_key: str = Field(
        default="dev-secret-key-at-least-fifty-characters-long-for-django-security"
    )
    debug: bool = Field(default=True)

    # Configuration sections
    database: DatabaseConfig = Field(default_factory=DatabaseConfig)
    app: AppConfig = Field(default_factory=AppConfig)
    env: EnvironmentMode = Field(default_factory=EnvironmentMode)

    # Security
    security_domains: list[str] | None = None

    model_config = SettingsConfigDict(
        env_file=str(Path(__file__).parent / ".env"),
        env_file_encoding="utf-8",
        env_nested_delimiter="__",
        case_sensitive=False,
        extra="ignore",
    )


# Global environment configuration instance
# Auto-loads from ENV > .env > defaults
env = EnvironmentConfig()
```

**core/environment/.env:**

```bash
# Development configuration
SECRET_KEY="dev-secret-key-at-least-fifty-characters-long-for-django-security"
DEBUG=true

# Application
APP__NAME="SaaS Platform"
APP__SITE_URL="http://localhost:3000"
APP__API_URL="http://localhost:8000"

# Database
DATABASE__URL="sqlite:///db.sqlite3"

# Security domains - optional in development
# Django-CFG auto-configures for dev convenience:
# - CORS fully open (CORS_ALLOW_ALL_ORIGINS=True)
# - Docker IPs work automatically
# - localhost any port
# SECURITY_DOMAINS="localhost,127.0.0.1"
```

### 3. Create Configuration Class

**core/config.py:**

```python
"""
SaaS Platform configuration using Django-CFG.
"""
from django_cfg import DjangoConfig, DatabaseConfig
from typing import Dict
from .environment import env  # Type-safe ENV loader


class SaaSConfig(DjangoConfig):
    """SaaS platform configuration from environment variables."""

    # From environment
    secret_key: str = env.secret_key
    debug: bool = env.debug
    env_mode: str = env.env.env_mode

    # Project info
    project_name: str = env.app.name
    site_url: str = env.app.site_url
    api_url: str = env.app.api_url

    # Security (optional in development, required in production)
    security_domains: list[str] | None = env.security_domains

    # Database from YAML URL (see /fundamentals/database for multi-database setup)
    databases: Dict[str, DatabaseConfig] = {
        "default": DatabaseConfig.from_url(url=env.database.url)
    }

    # Project apps
    project_apps: list[str] = [
        "core.apps.workspaces",  # Will create this app
    ]


# Create config instance
config = SaaSConfig()
```

### 4. Update settings.py

Replace **core/settings.py** content:

```python
"""
Django settings for SaaS platform.

Uses Django-CFG for type-safe configuration.
"""
from pathlib import Path
from .config import config

# Build paths
BASE_DIR = Path(__file__).resolve().parent.parent

# Import all Django-CFG settings
globals().update(config.get_all_settings())

# Override BASE_DIR (Django-CFG doesn't manage this)
BASE_DIR = BASE_DIR

# Static files
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
```

### 5. Create Workspace App

```bash
# Create workspaces app
python manage.py startapp workspaces core/apps/workspaces

# Create __init__.py in apps directory
mkdir -p core/apps
touch core/apps/__init__.py
```

**core/apps/workspaces/models.py:**

```python
from django.db import models
from django.contrib.auth.models import User


class Workspace(models.Model):
    """Multi-tenant workspace for SaaS platform."""

    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='owned_workspaces')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    # SaaS features
    plan = models.CharField(max_length=50, default='free', choices=[
        ('free', 'Free'),
        ('pro', 'Professional'),
        ('enterprise', 'Enterprise')
    ])
    max_members = models.IntegerField(default=5)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['owner', 'is_active']),
        ]

    def __str__(self):
        return self.name


class WorkspaceMember(models.Model):
    """Workspace membership with roles."""

    workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE, related_name='members')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='workspace_memberships')
    role = models.CharField(max_length=20, default='member', choices=[
        ('owner', 'Owner'),
        ('admin', 'Admin'),
        ('member', 'Member'),
        ('viewer', 'Viewer'),
    ])
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [['workspace', 'user']]
        ordering = ['-joined_at']

    def __str__(self):
        return f"{self.user.username} - {self.workspace.name} ({self.role})"
```

**core/apps/workspaces/admin.py:**

```python
from django.contrib import admin
from .models import Workspace, WorkspaceMember


@admin.register(Workspace)
class WorkspaceAdmin(admin.ModelAdmin):
    list_display = ['name', 'owner', 'plan', 'is_active', 'created_at']
    list_filter = ['plan', 'is_active', 'created_at']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ['created_at', 'updated_at']


@admin.register(WorkspaceMember)
class WorkspaceMemberAdmin(admin.ModelAdmin):
    list_display = ['workspace', 'user', 'role', 'joined_at']
    list_filter = ['role', 'joined_at']
    search_fields = ['workspace__name', 'user__username']
    readonly_fields = ['joined_at']
```

### 6. Run Migrations and Create Superuser

```bash
# Create database tables
python manage.py migrate

# Create admin user
python manage.py createsuperuser
# Enter: username, email, password

# Run development server
python manage.py runserver
```

### 7. Access Your Application

Open browser:
- **Main site:** http://127.0.0.1:8000/
- **Admin panel:** http://127.0.0.1:8000/admin/

Login to admin with created superuser credentials.

## Production Configuration

Create **core/environment/config.prod.yaml:**

```yaml
secret_key: ""  # Set via environment variable or secrets manager
debug: false

app:
  name: "SaaS Platform"
  site_url: "https://platform.example.com"
  api_url: "https://api.platform.example.com"

# REQUIRED in production - Django-CFG auto-normalizes any format
security_domains:
  - "platform.example.com"         # ✅ No protocol
  - "api.platform.example.com"     # ✅ Subdomain

# SSL/TLS: Assumes reverse proxy (nginx, Cloudflare, etc.) handles HTTPS
# No ssl_redirect needed - Django-CFG defaults to reverse proxy mode

database:
  url: "postgresql://user:pass@db.example.com:5432/saas_prod"
```

Deploy with:

```bash
IS_PROD=true python manage.py runserver
```

## Adding Features

### Enable Built-in Apps

Edit **core/config.py:**

```python
class SaaSConfig(DjangoConfig):
    # ... existing config ...

    # Enable built-in features (see /features/built-in-apps/overview for all apps)
    enable_support: bool = True      # Support tickets
    enable_accounts: bool = True     # Extended user management
    enable_newsletter: bool = True   # Email campaigns
    enable_payments: bool = True     # Subscription billing
```

### Add Caching

Update **core/environment/loader.py** (see [Cache Configuration](/fundamentals/configuration/cache) for advanced options):

```python
class EnvironmentConfig(BaseModel):
    # ... existing fields ...

    # Cache
    redis_url: str | None = None
```

Update **core/environment/config.dev.yaml:**

```yaml
# ... existing config ...

redis_url: "redis://localhost:6379/0"
```

Update **core/config.py:**

```python
from django_cfg import DjangoConfig, DatabaseConfig

class SaaSConfig(DjangoConfig):
    # ... existing config ...

    # ✨ Auto Redis cache - just set redis_url!
    redis_url: str | None = env.redis_url
    # Django-CFG automatically creates CacheConfig if redis_url is set
```

## Troubleshooting

See [Troubleshooting Guide](/guides/troubleshooting) for complete solutions.

### Configuration Not Loading

```bash
# Check which config file is loaded
python manage.py shell
>>> from core.environment import env
>>> print(env.env.env_mode)
development
```

### YAML Parse Error

```bash
# Validate YAML syntax
python -c "import yaml; yaml.safe_load(open('core/environment/config.dev.yaml'))"
```

### Pydantic Validation Error

```bash
# Check error details
python manage.py check
```

## Next Steps

- **[Sample Project Guide](/guides/sample-project/overview)** - Complete production-ready example with all features
- **[Examples](/guides/examples)** - Real-world code examples and use cases
- [Configuration Reference](/fundamentals/configuration) - All configuration options
- [Built-in Apps](/features/built-in-apps/overview) - Enable additional features
- [Deployment](/guides/docker/overview) - Deploy to production
- [Multi-Database](/guides/multi-database) - Set up database routing

TAGS: tutorial, first-project, yaml, pydantic, django-cfg, saas, multi-tenant
DEPENDS_ON: [installation, configuration]
USED_BY: [configuration, built-in-apps]
