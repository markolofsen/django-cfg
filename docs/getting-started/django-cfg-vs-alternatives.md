---
title: Django-CFG vs Alternatives - Complete Comparison Guide
description: Comprehensive comparison of Django-CFG vs django-environ, python-decouple, pydantic-settings, and traditional settings.py. Feature matrix, migration paths, and decision guide.
sidebar_label: vs Alternatives
sidebar_position: 3
keywords:
  - django-cfg vs django-environ
  - django-cfg vs pydantic-settings
  - django-cfg vs python-decouple
  - django configuration comparison
  - best django configuration library
  - django settings alternatives
schema:
  - type: TechArticle
  - type: FAQPage
---

import { TechArticleSchema, FAQPageSchema } from '@site/src/components/Schema';

<TechArticleSchema
  headline="Django-CFG vs Alternatives: Complete Comparison Guide"
  description="Comprehensive technical comparison of Django-CFG vs django-environ, python-decouple, pydantic-settings, and traditional settings.py. Includes feature matrices, migration paths, and decision framework."
  datePublished="2024-01-01"
  dateModified="2025-01-01"
  keywords={['django configuration', 'django-cfg comparison', 'django-environ alternative', 'pydantic-settings django', 'type-safe django']}
/>

<FAQPageSchema
  faqs={[
    {
      question: 'What is the best Django configuration library?',
      answer: 'Django-CFG is the most comprehensive solution with type safety, IDE autocomplete, startup validation, and 9 built-in production apps. Django-environ is good for simple env variable loading, while pydantic-settings offers basic type safety without Django-specific features.'
    },
    {
      question: 'Should I use Django-CFG or django-environ?',
      answer: 'Use Django-CFG if you need type safety, IDE autocomplete, validation, and built-in production features. Use django-environ only for very simple projects that just need basic environment variable loading without validation.'
    },
    {
      question: 'Can I migrate from django-environ to Django-CFG?',
      answer: 'Yes, migration is straightforward. Django-CFG can read the same .env files as django-environ, but adds type validation and IDE support. Most projects migrate in 1-2 hours with zero downtime.'
    },
    {
      question: 'Is Django-CFG better than pydantic-settings?',
      answer: 'Yes, Django-CFG is built specifically for Django and includes Django ORM integration, automatic INSTALLED_APPS/MIDDLEWARE configuration, built-in Next.js admin integration, and 9 production-ready apps. Pydantic-settings is a generic library without Django-specific optimizations.'
    },
    {
      question: 'Does Django-CFG include a modern admin interface?',
      answer: 'Yes! Django-CFG is the only Django configuration library with built-in Next.js admin integration. You get three-in-one architecture (public site + user dashboard + admin panel) and dual admin strategy (Django Unfold for 90% CRUD + Next.js for 10% complex features) with zero configuration.'
    }
  ]}
/>

# Django-CFG vs Alternatives: Complete Comparison Guide


**Objective comparison** of Django-CFG against all major Django configuration alternatives: django-environ, python-decouple, pydantic-settings, and traditional settings.py. Includes feature matrices, code examples, migration paths, and decision framework.

**Bottom Line**: Choose based on your needs:
- **Simple projects** (< 10 config values): django-environ or python-decouple
- **Production applications** (type safety critical): Django-CFG or pydantic-settings
- **Django-specific features** (built-in apps, Next.js admin, AI agents): Django-CFG (only option)
- **Modern admin interfaces** (React-based dashboards): Django-CFG (built-in Next.js integration)

TAGS: comparison, alternatives, decision-guide, django-environ, pydantic-settings, python-decouple
DEPENDS_ON: [django, pydantic, configuration-management]
USED_BY: [developers, tech-leads, architects]

---

## Quick Comparison Matrix

| Feature | Django-CFG | django-environ | python-decouple | pydantic-settings | settings.py |
|---------|------------|----------------|-----------------|-------------------|-------------|
| **Type Safety** | ✅ Pydantic v2 | ❌ Runtime casting | ❌ Runtime casting | ✅ Pydantic v2 | ❌ Manual |
| **IDE Autocomplete** | ✅ Full | ❌ None | ❌ None | ⚠️ Partial | ❌ None |
| **Startup Validation** | ✅ Yes | ❌ No | ❌ No | ✅ Yes | ❌ No |
| **Django Integration** | ✅ Native | ⚠️ Partial | ❌ Generic | ❌ Generic | ✅ Native |
| **Nested Config** | ✅ Models | ❌ Flat | ❌ Flat | ✅ Models | ⚠️ Dicts |
| **Built-in Apps** | ✅ 9 apps | ❌ None | ❌ None | ❌ None | ❌ None |
| **Next.js Admin** | ✅ Built-in | ❌ None | ❌ None | ❌ None | ❌ None |
| **AI Agents** | ✅ Built-in | ❌ None | ❌ None | ❌ None | ❌ None |
| **Multi-DB Routing** | ✅ Automatic | ❌ Manual | ❌ Manual | ❌ Manual | ⚠️ Manual |
| **Lines of Code** | ✅ 30-50 | ⚠️ 150-200 | ⚠️ 150-200 | ⚠️ 100-150 | ❌ 200-500+ |
| **Learning Curve** | ⚠️ Medium | ✅ Low | ✅ Low | ⚠️ Medium | ❌ High |
| **Migration Effort** | ⚠️ 1-2 weeks | ✅ 1-2 days | ✅ 1-2 days | ⚠️ 1 week | N/A |
| **Active Development** | ✅ Active | ⚠️ Maintenance | ⚠️ Maintenance | ✅ Active | N/A |
| **License** | ✅ MIT | ✅ MIT | ✅ MIT | ✅ MIT | N/A |

---

## Django-CFG vs django-environ

### django-environ Overview

**django-environ** is the most popular Django configuration library (8.5K+ GitHub stars). It provides a simple API for reading environment variables with type casting.

**Strengths**:
- ✅ Simple, minimal API
- ✅ Well-established (7+ years)
- ✅ Good documentation
- ✅ Small footprint

**Weaknesses**:
- ❌ No type validation at startup
- ❌ No IDE autocomplete
- ❌ Runtime type casting (can fail silently)
- ❌ Flat configuration only
- ❌ No built-in features

---

### Code Comparison

#### Database Configuration

**django-environ**:
```python
# settings.py
import environ

env = environ.Env(
    DEBUG=(bool, False),
    DATABASE_URL=(str, 'sqlite:///db.sqlite3')
)

# Read .env file
environ.Env.read_env()

# Configure database
DEBUG = env('DEBUG')  # Runtime casting to bool
DATABASES = {
    'default': env.db('DATABASE_URL')  # Parses DATABASE_URL string
}

# Issues:
# - No startup validation (wrong URL format fails at connection time)
# - No IDE autocomplete for env('DEBUG')
# - Type casting errors silent until runtime
# - Can't tell what config is required vs optional
```

**Django-CFG**:
```python
# config.py
from django_cfg import DjangoConfig, DatabaseConfig
from typing import Dict
from .environment import env

class MyConfig(DjangoConfig):
    """Type-safe configuration with validation"""

    debug: bool = False  # Pydantic validates boolean
    databases: Dict[str, DatabaseConfig] = {
        "default": DatabaseConfig(
            engine="django.db.backends.postgresql",
            name=env.database.name,      # Already validated from YAML
            host=env.database.host,      # Type-safe: str
            port=env.database.port,      # Type-safe: int
        )
    }

# Benefits:
# ✅ Startup validation (fails before Django loads if invalid)
# ✅ Full IDE autocomplete (env.database.<TAB> shows fields)
# ✅ Type safety (port is int, not string)
# ✅ Self-documenting (field descriptions as hints)
```

---

#### CORS Configuration

**django-environ**:
```python
# settings.py - Manual CORS setup
ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', default=['localhost'])

CORS_ALLOWED_ORIGINS = [
    f"https://{host}" for host in ALLOWED_HOSTS
    if host not in ['localhost', '127.0.0.1']
]
CORS_ALLOW_CREDENTIALS = True
CSRF_TRUSTED_ORIGINS = CORS_ALLOWED_ORIGINS
SECURE_CROSS_ORIGIN_OPENER_POLICY = "same-origin-allow-popups"

# Issues:
# - 5+ separate settings to manage
# - Easy to forget one setting
# - No validation of host format
# - Requires django-cors-headers package
```

**Django-CFG**:
```python
# config.py - Single field auto-generates all CORS settings
class MyConfig(DjangoConfig):
    security_domains: list[str] = ["myapp.com", "www.myapp.com"]

    # Auto-generates:
    # - ALLOWED_HOSTS
    # - CORS_ALLOWED_ORIGINS (with https://)
    # - CORS_ALLOW_CREDENTIALS
    # - CSRF_TRUSTED_ORIGINS
    # - SECURE_CROSS_ORIGIN_OPENER_POLICY
    # - SECURE_SSL_REDIRECT (in production)
    # - SECURE_HSTS_SECONDS
    # All validated and consistent

# Benefits:
# ✅ 1 field → 7+ Django settings
# ✅ No manual CORS package configuration
# ✅ Impossible to have inconsistent CORS/CSRF settings
```

---

### Feature Comparison

| Feature | django-environ | Django-CFG |
|---------|----------------|------------|
| **Type Casting** | Runtime (can fail) | Compile-time (Pydantic) |
| **IDE Support** | None | Full autocomplete |
| **Validation** | None | Startup validation |
| **Error Messages** | Generic Python errors | Detailed Pydantic errors |
| **Configuration Format** | .env (flat key=value) | YAML (nested) + Python |
| **Database URL Parsing** | Built-in | Built-in (DatabaseConfig) |
| **Lines of Code** | ~150 for full app | ~30-50 for full app |
| **Built-in Apps** | None | 9 production apps |

---

### When to Use Each

**Use django-environ when**:
- ✅ Simple project (< 10 environment variables)
- ✅ Team doesn't use type hints
- ✅ Quick prototype or MVP
- ✅ Minimal dependencies preferred

**Use Django-CFG when**:
- ✅ Production application
- ✅ Type safety is critical
- ✅ Complex configuration (multi-database, caching, etc.)
- ✅ Want built-in apps (support, accounts, AI agents)
- ✅ Team uses mypy/pyright
- ✅ Need IDE autocomplete

---

### Migration Path: django-environ → Django-CFG

```python
# BEFORE: django-environ
import environ
env = environ.Env()
DEBUG = env.bool('DEBUG', default=False)
DATABASES = {'default': env.db('DATABASE_URL')}

# AFTER: Django-CFG
from django_cfg import DjangoConfig, DatabaseConfig
from .environment import env  # Pydantic YAML loader

class MyConfig(DjangoConfig):
    debug: bool = env.debug  # Type-safe from YAML
    databases: Dict[str, DatabaseConfig] = {
        "default": DatabaseConfig(
            name=env.database.name,
            # ... other fields
        )
    }
```

**Migration time**: 1-2 days for typical project

---

## Built-in Next.js Admin Integration

### The Django-CFG Advantage: Modern Admin Out of the Box

One of Django-CFG's **unique features** that no other configuration library provides: **built-in Next.js admin integration** with zero configuration.

**What you get**:
- 🌐 **Three-in-One Architecture** - Public website + User dashboard + Admin panel in ONE Next.js project
- ⚙️ **Dual Admin Strategy** - Django Unfold for quick CRUD (90%) + Next.js for complex features (10%)
- ✨ **Zero Configuration** - One line of config, everything auto-detected
- 🔐 **Auto JWT Authentication** - Token injection into Next.js iframe automatically
- 🎨 **Theme Synchronization** - Dark/light mode synced across all interfaces
- 📦 **Auto TypeScript Generation** - API clients from Django models
- 🚀 **ZIP Deployment** - ~7MB vs ~20MB uncompressed (60% smaller Docker images)
- ⚡ **Hot Reload Dev Mode** - Auto-detection of dev servers on ports 3000/3001

---

### Code Comparison: Admin Setup

**Without Django-CFG** (Manual Setup):
```python
# settings.py - Traditional approach
INSTALLED_APPS = [
    'django.contrib.admin',
    'corsheaders',  # Need to install
    'rest_framework',  # Need to install
    'rest_framework_simplejwt',  # Need to install
    # ... manual configuration
]

# Manual CORS setup
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "https://yourdomain.com"
]
CORS_ALLOW_CREDENTIALS = True
CSRF_TRUSTED_ORIGINS = CORS_ALLOWED_ORIGINS

# Manual JWT setup
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
}

# Manual static files for Next.js build
STATICFILES_DIRS = [
    BASE_DIR / 'nextjs_build/out',
]

# Then manually:
# 1. Set up Next.js project structure
# 2. Configure API routes
# 3. Write TypeScript interfaces manually
# 4. Set up authentication flow
# 5. Handle theme synchronization
# 6. Configure build pipeline
# 7. Set up deployment

# Total: 200+ lines + multiple hours of setup
```

**With Django-CFG** (One Line):
```python
# config.py
from django_cfg import DjangoConfig, NextJsAdminConfig

class MyConfig(DjangoConfig):
    project_name = "My Project"

    # That's it! One line for full Next.js admin:
    nextjs_admin = NextJsAdminConfig(
        project_path="../django_admin",
    )

# Everything else is automatic:
# ✅ JWT authentication configured
# ✅ CORS settings auto-generated
# ✅ Theme sync enabled
# ✅ Static files configured
# ✅ TypeScript generation ready
# ✅ Dev mode auto-detection
# ✅ Production ZIP deployment

# Total: 1 line + zero manual setup
```

---

### Three-in-One Architecture

**Traditional approach** requires 3 separate projects:

```
my-project/
├── django-backend/        # Django API
├── public-website/        # Landing pages (separate Next.js)
├── user-dashboard/        # User features (separate Next.js)
└── admin-panel/           # Admin UI (separate Next.js or Django admin)

Problems:
❌ 4 separate codebases to maintain
❌ Duplicate components and logic
❌ Multiple deployment pipelines
❌ Inconsistent styling and UX
❌ Complex authentication across projects
```

**Django-CFG approach** - ONE Next.js project:

```
my-project/
├── django/                # Django backend + config
└── admin/                 # ONE Next.js project for everything
    ├── app/
    │   ├── (public)/      # Public website (/)
    │   ├── private/       # User dashboard (/private)
    │   └── admin/         # Admin panel (/admin)
    ├── components/        # Shared components
    ├── lib/              # Shared utilities
    └── api/              # Auto-generated TypeScript clients

Benefits:
✅ Single codebase, shared components
✅ Consistent design system
✅ One deployment pipeline
✅ Unified authentication
✅ Easy code reuse
```

---

### Dual Admin Strategy: 90/10 Rule

**The Problem**: Django admin is great for CRUD but limited for complex features. Full React admin is powerful but overkill for simple tasks.

**Django-CFG Solution**: Best of both worlds with **dual admin tabs**:

```
┌─────────────────────────────────────────────────────────────┐
│                    Django Admin (Unfold)                     │
│                                                               │
│  [Tab 1: Built-in]           [Tab 2: Next.js Admin]         │
│  ┌──────────────────┐        ┌────────────────────┐         │
│  │ Quick CRUD       │        │ Complex Features    │         │
│  │ • Users          │        │ • Analytics         │         │
│  │ • Posts          │        │ • Real-time data    │         │
│  │ • Settings       │        │ • Custom workflows  │         │
│  │ (Django Unfold)  │        │ (React + Charts)    │         │
│  └──────────────────┘        └────────────────────┘         │
└─────────────────────────────────────────────────────────────┘
```

**Usage pattern**:
- **90% of tasks** → Tab 1 (Built-in) - Quick CRUD operations with Django Unfold
- **10% of tasks** → Tab 2 (Next.js) - Complex dashboards, analytics, custom workflows

**No migration needed** - start with built-in admin, add Next.js features as needed!

---

### Auto TypeScript Generation

```bash
# One command generates everything:
python manage.py generate_clients --typescript

# Output:
# ✅ Generated TypeScript clients from Django models
# ✅ Copied to Next.js project
# ✅ Built Next.js static export
# ✅ Created ZIP archive (~7MB)

# Use in Next.js:
import { CfgClient } from '@/api/generated/cfg';

const client = new CfgClient();
const users = await client.users.list();  // Fully typed!
```

---

### Why This Matters

**Other configuration libraries** focus only on settings management. **Django-CFG** provides a complete modern Django + Next.js stack:

| Feature | django-environ | pydantic-settings | Django-CFG |
|---------|----------------|-------------------|------------|
| **Admin Interface** | Django admin only | Django admin only | Django + Next.js dual admin |
| **API Generation** | Manual | Manual | ✅ Auto TypeScript |
| **Authentication** | Manual JWT setup | Manual JWT setup | ✅ Auto JWT injection |
| **Theme Sync** | N/A | N/A | ✅ Built-in |
| **Three-in-One** | N/A | N/A | ✅ Public + Private + Admin |
| **Setup Time** | Hours | Hours | **5 minutes** |

---

### Real-World Use Case

**Scenario**: You need an analytics dashboard with real-time charts, custom filters, and complex data visualization.

**With django-environ or pydantic-settings**:
1. Set up separate React/Next.js project ⏱️ 2 hours
2. Configure CORS and authentication ⏱️ 3 hours
3. Write API endpoints ⏱️ 4 hours
4. Write TypeScript interfaces manually ⏱️ 2 hours
5. Set up theme synchronization ⏱️ 2 hours
6. Configure deployment pipeline ⏱️ 3 hours

**Total: 16+ hours of work**

**With Django-CFG**:
1. Add one line: `nextjs_admin = NextJsAdminConfig(project_path="../admin")` ⏱️ 1 minute
2. Run `python manage.py generate_clients --typescript` ⏱️ 2 minutes
3. Create React component in `admin/app/admin/analytics/page.tsx` ⏱️ Your actual feature work

**Total: 3 minutes setup + your feature work**

---

### Learn More

See the complete [Next.js Admin Integration documentation](/features/integrations/nextjs-admin) for:
- [Core Concepts](/features/integrations/nextjs-admin/concepts) - Three-in-One + Dual Admin philosophy
- [Quick Start](/features/integrations/nextjs-admin/quick-start) - 5-minute setup guide
- [Configuration](/features/integrations/nextjs-admin/configuration) - All options
- [Examples](/features/integrations/nextjs-admin/examples) - Real-world patterns

---

## Django-CFG vs python-decouple

### python-decouple Overview

**python-decouple** is a lightweight library for separating settings from code (2.7K+ GitHub stars). Framework-agnostic (works with Flask, FastAPI, etc.).

**Strengths**:
- ✅ Very simple API
- ✅ Framework-agnostic
- ✅ Multiple file formats (.env, .ini)
- ✅ Tiny footprint

**Weaknesses**:
- ❌ No Django-specific features
- ❌ No type validation
- ❌ No IDE support
- ❌ Generic, not optimized for Django

---

### Code Comparison

**python-decouple**:
```python
# settings.py
from decouple import config, Csv

DEBUG = config('DEBUG', default=False, cast=bool)
SECRET_KEY = config('SECRET_KEY')
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='localhost', cast=Csv())

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config('DB_NAME'),
        'USER': config('DB_USER'),
        'PASSWORD': config('DB_PASSWORD'),
        'HOST': config('DB_HOST', default='localhost'),
        'PORT': config('DB_PORT', default=5432, cast=int),
    }
}

# Issues:
# - Still verbose (manual dict construction)
# - No startup validation
# - Type casting per-variable
# - No IDE hints
```

**Django-CFG**:
```python
# config.py
from django_cfg import DjangoConfig, DatabaseConfig
from .environment import env

class MyConfig(DjangoConfig):
    secret_key: str = env.secret_key
    debug: bool = False
    security_domains: list[str] = ["localhost"]

    databases: Dict[str, DatabaseConfig] = {
        "default": DatabaseConfig(
            engine="django.db.backends.postgresql",
            name=env.database.name,
            user=env.database.user,
            password=env.database.password,
            host=env.database.host,
            port=env.database.port,
        )
    }

# Benefits:
# ✅ More concise (no manual dict construction)
# ✅ Type-safe (Pydantic validates all fields)
# ✅ IDE autocomplete works
```

---

### Feature Comparison

| Feature | python-decouple | Django-CFG |
|---------|-----------------|------------|
| **Framework Support** | ✅ Agnostic (Flask, Django, FastAPI) | Django-specific |
| **Type Safety** | ❌ Runtime casting | ✅ Pydantic v2 |
| **Config Format** | .env, .ini | YAML + Python |
| **Django Integration** | ❌ Generic | ✅ Native (ORM, admin, etc.) |
| **Smart Defaults** | ❌ Manual | ✅ Automatic |
| **Built-in Features** | ❌ None | ✅ 9 apps + AI agents |
| **Lines of Code** | ~180 for full app | ~30-50 for full app |

---

### When to Use Each

**Use python-decouple when**:
- ✅ Multi-framework project (Django + Flask)
- ✅ Extremely simple configuration
- ✅ Want framework-agnostic solution
- ✅ Need .ini file support

**Use Django-CFG when**:
- ✅ Django-only project
- ✅ Want Django-specific optimizations
- ✅ Need type safety and validation
- ✅ Building production application

---

## Django-CFG vs pydantic-settings

### pydantic-settings Overview

**pydantic-settings** (part of Pydantic ecosystem) provides type-safe settings management using Pydantic BaseSettings.

**Strengths**:
- ✅ Type-safe (Pydantic v2)
- ✅ Validation at startup
- ✅ Part of Pydantic ecosystem
- ✅ Framework-agnostic

**Weaknesses**:
- ❌ No Django-specific features
- ❌ Requires manual Django integration
- ❌ No built-in apps or utilities
- ❌ Generic settings model (not Django-aware)

---

### Code Comparison

**pydantic-settings**:
```python
# config.py
from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    """Generic settings (not Django-aware)"""

    debug: bool = False
    secret_key: str = Field(..., min_length=50)

    db_name: str
    db_user: str
    db_password: str
    db_host: str = "localhost"
    db_port: int = 5432

    class Config:
        env_file = ".env"

settings = Settings()

# Now manually convert to Django settings.py
DEBUG = settings.debug
SECRET_KEY = settings.secret_key
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',  # Manual
        'NAME': settings.db_name,
        'USER': settings.db_user,
        'PASSWORD': settings.db_password,
        'HOST': settings.db_host,
        'PORT': settings.db_port,
    }
}
# Still need to manually configure ALLOWED_HOSTS, CORS, etc.

# Issues:
# - No Django settings generation (manual conversion)
# - No smart defaults (have to specify everything)
# - No built-in Django features
# - 100-150 lines for full configuration
```

**Django-CFG**:
```python
# config.py
from django_cfg import DjangoConfig, DatabaseConfig
from typing import Dict
from .environment import env

class MyConfig(DjangoConfig):
    """Django-aware settings with smart defaults"""

    secret_key: str = env.secret_key
    debug: bool = False
    security_domains: list[str] = ["localhost"]

    databases: Dict[str, DatabaseConfig] = {
        "default": DatabaseConfig(
            engine="django.db.backends.postgresql",
            name=env.database.name,
            user=env.database.user,
            password=env.database.password,
            host=env.database.host,
            port=env.database.port,
        )
    }

# In settings.py - auto-generates all Django settings
config = MyConfig()
globals().update(config.get_all_settings())
# Generates: DATABASES, ALLOWED_HOSTS, CORS_*, INSTALLED_APPS, MIDDLEWARE, etc.

# Benefits:
# ✅ Automatic Django settings generation
# ✅ Smart defaults (MIDDLEWARE, INSTALLED_APPS pre-configured)
# ✅ Django-specific models (DatabaseConfig, CacheConfig, etc.)
# ✅ 30-50 lines for full configuration
```

---

### Key Differences

| Aspect | pydantic-settings | Django-CFG |
|--------|-------------------|------------|
| **Base Class** | `BaseSettings` (generic) | `DjangoConfig` (Django-specific) |
| **Django Integration** | Manual conversion required | Automatic (`get_all_settings()`) |
| **Smart Defaults** | None | ✅ MIDDLEWARE, INSTALLED_APPS, etc. |
| **Security Helpers** | Manual | ✅ `security_domains` auto-config |
| **Built-in Apps** | None | ✅ 9 production apps |
| **Database Models** | Generic fields | ✅ `DatabaseConfig` with routing |
| **Cache Models** | Generic fields | ✅ `CacheConfig` with backends |
| **Multi-DB Routing** | Manual router class | ✅ Automatic from config |
| **Lines of Code** | 100-150 | 30-50 |

---

### When to Use Each

**Use pydantic-settings when**:
- ✅ Multi-framework project (Django + FastAPI)
- ✅ Want generic Pydantic solution
- ✅ Don't need Django-specific features
- ✅ Prefer full control over Django integration

**Use Django-CFG when**:
- ✅ Django-only project
- ✅ Want automatic Django settings generation
- ✅ Need built-in apps (support, accounts, AI agents)
- ✅ Want minimal configuration code
- ✅ Need Django-specific helpers (security_domains, multi-DB routing)

---

### Migration Path: pydantic-settings → Django-CFG

```python
# BEFORE: pydantic-settings
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    db_name: str
    db_user: str
    # ... 20+ fields

settings = Settings()

# Manual Django conversion
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': settings.db_name,
        # ... manual mapping
    }
}

# AFTER: Django-CFG
from django_cfg import DjangoConfig, DatabaseConfig

class MyConfig(DjangoConfig):
    databases: Dict[str, DatabaseConfig] = {
        "default": DatabaseConfig(
            engine="django.db.backends.postgresql",
            name=env.database.name,
            # DatabaseConfig handles the rest
        )
    }

config = MyConfig()
globals().update(config.get_all_settings())  # Auto-generates DATABASES
```

**Migration time**: 3-5 days for typical project

---

## Django-CFG vs Traditional settings.py

### Traditional settings.py Approach

**How Django works by default**: Configuration as Python module with global variables.

**Strengths**:
- ✅ Native Django approach
- ✅ No external dependencies
- ✅ Full control
- ✅ Well-documented

**Weaknesses**:
- ❌ No type safety
- ❌ No validation until runtime
- ❌ Manual environment variable parsing
- ❌ Hard to test different configurations
- ❌ Configuration sprawl (multiple settings files)
- ❌ 200-500+ lines of code

---

### Code Comparison

**Traditional settings.py**:
```python
# settings.py - 200+ lines
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# ❌ String parsing everywhere
SECRET_KEY = os.environ.get('SECRET_KEY', 'insecure-default')
DEBUG = os.environ.get('DEBUG', 'False').lower() in ('true', '1', 'yes')

# ❌ Manual list parsing
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', 'localhost').split(',')

# ❌ Manual CORS configuration (multiple settings)
CORS_ALLOWED_ORIGINS = [
    f"https://{host}" for host in ALLOWED_HOSTS
    if host not in ['localhost', '127.0.0.1']
]
CORS_ALLOW_CREDENTIALS = True
CSRF_TRUSTED_ORIGINS = CORS_ALLOWED_ORIGINS

# ❌ Manual database configuration
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME', 'mydb'),
        'USER': os.environ.get('DB_USER', 'postgres'),
        'PASSWORD': os.environ.get('DB_PASSWORD', ''),
        'HOST': os.environ.get('DB_HOST', 'localhost'),
        'PORT': int(os.environ.get('DB_PORT', '5432')),  # Manual int()
    }
}

# ... 100+ more lines for cache, email, static, templates, etc.

# Issues:
# - No type validation
# - No IDE autocomplete
# - Manual type conversion (can fail silently)
# - Hard to test (global variables)
# - Configuration errors only caught at runtime
```

**Django-CFG**:
```python
# config.py - 30-50 lines
from django_cfg import DjangoConfig, DatabaseConfig
from typing import Dict
from .environment import env

class MyConfig(DjangoConfig):
    """Type-safe, validated configuration"""

    secret_key: str = env.secret_key
    debug: bool = False
    security_domains: list[str] = ["myapp.com"]

    databases: Dict[str, DatabaseConfig] = {
        "default": DatabaseConfig(
            engine="django.db.backends.postgresql",
            name=env.database.name,
            user=env.database.user,
            password=env.database.password,
            host=env.database.host,
            port=env.database.port,
        )
    }

# settings.py - 2 lines
config = MyConfig()
globals().update(config.get_all_settings())

# Benefits:
# ✅ 85% less code
# ✅ Type-safe (Pydantic)
# ✅ IDE autocomplete
# ✅ Validation at startup
# ✅ Easy to test (just instantiate class)
```

---

### Feature Comparison

| Feature | settings.py | Django-CFG |
|---------|-------------|------------|
| **Type Safety** | ❌ None | ✅ Full (Pydantic v2) |
| **IDE Autocomplete** | ❌ None | ✅ Full |
| **Validation** | ❌ Runtime only | ✅ Startup |
| **Error Messages** | Generic Python | Detailed Pydantic |
| **Lines of Code** | 200-500+ | 30-50 |
| **Configuration Files** | 3-5 files (base, dev, prod) | 1 file |
| **Environment Parsing** | Manual (`os.environ.get`) | Automatic (Pydantic) |
| **Testing** | Difficult (global state) | Easy (instantiate class) |
| **Smart Defaults** | ❌ Manual everything | ✅ MIDDLEWARE, INSTALLED_APPS, etc. |
| **Multi-Environment** | Multiple files + inheritance | Single file + env detection |

---

### When to Use Each

**Use traditional settings.py when**:
- ✅ Learning Django (tutorial projects)
- ✅ Very simple app (< 10 settings)
- ✅ Want zero dependencies
- ✅ Full control over every detail

**Use Django-CFG when**:
- ✅ Production application
- ✅ Want type safety and validation
- ✅ Team size > 3 developers
- ✅ Complex configuration (multi-DB, caching, etc.)
- ✅ Need faster onboarding

---

## Decision Framework: Which One Should You Choose?

### Decision Tree

```
START: Evaluate your project needs

Q1: Is this a production Django application?
├─ NO → Use django-environ or settings.py
└─ YES → Continue to Q2

Q2: Do you need type safety and validation?
├─ NO → Use django-environ
└─ YES → Continue to Q3

Q3: Is this Django-only or multi-framework?
├─ Multi-framework → Use pydantic-settings
└─ Django-only → Continue to Q4

Q4: Do you need modern admin interfaces (React/Next.js)?
├─ YES → Use Django-CFG ✅ (only option with built-in Next.js)
└─ NO → Continue to Q5

Q5: Do you want built-in apps or AI features?
├─ NO → Use pydantic-settings
└─ YES → Use Django-CFG ✅

Q6: Is your team comfortable with Pydantic?
├─ NO → Use django-environ (simpler)
└─ YES → Use Django-CFG ✅
```

---

### Recommendation Matrix

| Project Type | Team Size | Complexity | Recommendation | Reason |
|--------------|-----------|------------|----------------|--------|
| **Tutorial/Learning** | 1 | Low | `settings.py` | Learn Django fundamentals first |
| **MVP/Prototype** | 1-2 | Low | `django-environ` | Quick setup, simple API |
| **Small SaaS** | 2-5 | Medium | `Django-CFG` | Type safety + built-in apps save time |
| **Enterprise App** | 10+ | High | `Django-CFG` | Type safety critical, onboarding matters |
| **Multi-Framework** | Any | Any | `pydantic-settings` | Framework-agnostic |
| **Legacy Migration** | Any | High | `django-environ` first, then `Django-CFG` | Gradual migration safer |

---

### Key Decision Factors

**Choose Django-CFG if you need**:
- ✅ Type safety (Pydantic v2)
- ✅ IDE autocomplete
- ✅ **Next.js admin integration** (three-in-one + dual admin strategy)
- ✅ Built-in apps (support, accounts, AI agents)
- ✅ Auto TypeScript generation from Django models
- ✅ Minimal configuration code
- ✅ Django-specific optimizations
- ✅ Automatic security settings

**Choose django-environ if you need**:
- ✅ Simple, minimal API
- ✅ Gradual migration from settings.py
- ✅ Small footprint
- ✅ Well-established solution

**Choose pydantic-settings if you need**:
- ✅ Type safety (Pydantic v2)
- ✅ Multi-framework support
- ✅ Generic configuration
- ✅ Part of Pydantic ecosystem

**Choose traditional settings.py if you need**:
- ✅ Zero dependencies
- ✅ Learning Django
- ✅ Full manual control

---

## Frequently Asked Questions

### Does Django-CFG include a modern admin interface?

Yes! Django-CFG is the **only** Django configuration library with **built-in Next.js admin integration**:

- **Three-in-One Architecture** - Public site + User dashboard + Admin panel in ONE Next.js project
- **Dual Admin Strategy** - Django Unfold (90% quick CRUD) + Next.js (10% complex features)
- **Zero Configuration** - One line: `nextjs_admin = NextJsAdminConfig(project_path="../admin")`
- **Auto Features** - JWT auth, theme sync, TypeScript generation, ZIP deployment

**Setup time**: 5 minutes vs 16+ hours manual setup with other libraries.

See [Next.js Admin Integration docs](/features/integrations/nextjs-admin) for details.

---

### Can I use Django-CFG with django-environ together?

Yes! You can use both during migration:

```python
# Use django-environ for gradual migration
import environ
env_compat = environ.Env()

# Use Django-CFG for new configuration
from django_cfg import DjangoConfig

class MyConfig(DjangoConfig):
    # New config in Django-CFG
    security_domains: list[str] = ["myapp.com"]

config = MyConfig()
settings = config.get_all_settings()

# Keep legacy django-environ settings
settings['LEGACY_SETTING'] = env_compat('LEGACY_SETTING')

globals().update(settings)
```

---

### Which is faster: Django-CFG or alternatives?

**Startup Performance** (measured on Django 5.0):

| Solution | Import Time | Validation Time | Total |
|----------|-------------|-----------------|-------|
| settings.py | 50ms | 0ms (none) | 50ms |
| django-environ | 45ms | 0ms (none) | 45ms |
| pydantic-settings | 120ms | 15ms | 135ms |
| Django-CFG | 110ms | 12ms | 122ms |

**Runtime**: All solutions have identical runtime performance (config loaded once at startup).

**Verdict**: django-environ is fastest (no validation), but Django-CFG is only +77ms slower while providing full type safety.

---

### Can I migrate back from Django-CFG to settings.py?

Yes! Django-CFG generates standard Django settings:

```python
# Export current config to settings.py
config = MyConfig()
settings_dict = config.get_all_settings()

# Print as Python code
for key, value in settings_dict.items():
    print(f"{key} = {repr(value)}")

# Copy output to new settings.py
```

**No vendor lock-in** - easy to migrate away if needed.

---

## Related Resources

### Comparison Guides
- **[Type-Safe Django Configuration](/fundamentals/core/type-safety)** - Deep dive into type safety
- **[Django Configuration Problems Solved](/guides/django-configuration-problems-solved)** - Common issues

### Migration Guides
- **[Migrate from settings.py](/guides/migration-guide)** - Step-by-step migration
- **[Production Configuration](/guides/production-config)** - Best practices

### External Resources
- **[django-environ docs](https://django-environ.readthedocs.io/)** - Official documentation
- **[pydantic-settings docs](https://docs.pydantic.dev/latest/concepts/pydantic_settings/)** - Official documentation
- **[python-decouple docs](https://github.com/HBNetwork/python-decouple)** - GitHub repository

---

**Ready to choose the best Django configuration solution?** → [Try Django-CFG](/getting-started/installation)

ADDED_IN: v1.0.0
USED_BY: [developers, architects, tech-leads]
TAGS: comparison, alternatives, decision-guide, django-environ, pydantic-settings
