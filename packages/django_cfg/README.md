# Django-CFG: Type-Safe Django Configuration Framework with AI-Ready Infrastructure

[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg?style=flat-square&logo=python)](https://www.python.org/downloads/)
[![Django 5.2+](https://img.shields.io/badge/django-5.2+-green.svg?style=flat-square&logo=django)](https://www.djangoproject.com/)
[![PyPI](https://img.shields.io/pypi/v/django-cfg.svg?style=flat-square&logo=pypi)](https://pypi.org/project/django-cfg/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=flat-square)](https://opensource.org/licenses/MIT)
[![Downloads](https://img.shields.io/pypi/dm/django-cfg.svg?style=flat-square)](https://pypi.org/project/django-cfg/)
[![GitHub Stars](https://img.shields.io/github/stars/markolofsen/django-cfg?style=flat-square&logo=github)](https://github.com/markolofsen/django-cfg)

<div align="center">
<img src="https://raw.githubusercontent.com/markolofsen/django-cfg/refs/heads/main/static/django-cfg.png" alt="Django-CFG Framework" width="100%">
</div>

---

<div align="center">

### 🚀 Pydantic Django Settings: Reduce Django Configuration Code by 90%

**Type-safe Django configuration with Pydantic v2 models** • **Full IDE autocomplete** • **Startup validation** • **8 enterprise apps**

**[🤖 AI Project Generator](https://editor.djangocfg.com)** • **[🎯 Live Demo](http://demo.djangocfg.com)** • **[📚 Documentation](https://djangocfg.com/docs/getting-started/intro)**

</div>

## 🤖 AI Project Generator - Zero Setup Required

**Describe your app in plain English, get production-ready Django project in 30 seconds:**

> *"I need a SaaS app with user authentication, Stripe payments, and admin dashboard"*

**AI generates:** ✅ Type-safe config • ✅ Database models • ✅ REST API + docs • ✅ Modern UI • ✅ Deployment ready

### **[→ Try AI Editor Now](https://editor.djangocfg.com)**

---

## 🎯 Type-Safe Django Configuration with Pydantic v2

**Django-CFG replaces error-prone `settings.py` with type-safe Pydantic models** - eliminate runtime configuration errors, get full IDE autocomplete, and validate settings at startup. The only Django configuration framework with built-in AI agents and enterprise apps.

### Why Type-Safe Configuration Matters

**Traditional Django settings.py problems:**
- ❌ **Runtime errors** - typos caught in production, not at startup
- ❌ **No IDE support** - zero autocomplete, manual docs lookup
- ❌ **200+ lines** - unmaintainable configuration sprawl
- ❌ **Manual validation** - environment variables unchecked until used

**Django-CFG Pydantic solution:**
- ✅ **Compile-time validation** - catch errors before deployment
- ✅ **Full IDE autocomplete** - IntelliSense for all settings
- ✅ **30 lines of code** - 90% boilerplate reduction
- ✅ **Startup validation** - fail fast with clear error messages

### Django Configuration Comparison

| Feature | settings.py | django-environ | pydantic-settings | **Django-CFG** |
|---------|-------------|----------------|-------------------|----------------|
| **Type Safety** | ❌ Runtime only | ⚠️ Basic casting | ✅ Pydantic | ✅ **Full Pydantic v2** |
| **IDE Autocomplete** | ❌ None | ❌ None | ⚠️ Partial | ✅ **100%** |
| **Startup Validation** | ❌ No | ⚠️ Partial | ✅ Yes | ✅ **Yes + Custom validators** |
| **Django Integration** | ✅ Native | ⚠️ Partial | ❌ Manual | ✅ **Seamless** |
| **Built-in Apps** | ❌ Build yourself | ❌ None | ❌ None | ✅ **8 enterprise apps** |
| **AI-Ready** | ❌ Manual setup | ❌ None | ❌ None | ✅ **LLM + Vector DB** |

**[📚 Full comparison guide →](https://djangocfg.com/docs/getting-started/django-cfg-vs-alternatives)**

---

## 🚀 Three Ways to Start

### Option 1: AI Editor (Fastest - 30 seconds) ⚡

**Generate project with AI - no installation needed:**

1. Go to **[editor.djangocfg.com](https://editor.djangocfg.com)**
2. Describe your app in plain English
3. Download ready-to-deploy project

**[→ Generate with AI](https://editor.djangocfg.com)**

---

### Option 2: Traditional CLI

```bash
pip install django-cfg
django-cfg create-project "My SaaS App"
cd my-saas-app && python manage.py runserver
```

**What you get instantly:**
- 🎨 Modern Admin UI → `http://127.0.0.1:8000/admin/`
- 📚 API Docs → `http://127.0.0.1:8000/api/docs/`
- 🚀 Production-ready app

<div align="center">
<img src="https://raw.githubusercontent.com/markolofsen/django-cfg/refs/heads/main/static/startup.png" alt="Django-CFG Startup Screen" width="800">
<p><em>Django-CFG startup screen showing type-safe configuration validation</em></p>
</div>

**[📚 Installation Guide →](https://djangocfg.com/docs/getting-started/installation)**

---

### Option 3: Explore Live Demo First 🎯

**See a real production Django-CFG app in action:**

### **[→ http://demo.djangocfg.com](http://demo.djangocfg.com)**

**Demo credentials:**
- **Admin:** `demo@djangocfg.com` / `demo2024`
- **User:** `user@djangocfg.com` / `user2024`

**What you'll see:** Modern admin • Auto-generated API docs • AI agents • Support system • Payments

---

## 💡 Core Features

### 🔒 Type-Safe Django Settings with Pydantic v2 Models

**Replace Django's settings.py with Pydantic v2 for complete type safety, IDE autocomplete, and startup validation.**

#### Before: Django settings.py (Runtime Errors)

```python
# settings.py - No type checking, runtime errors
import os

DEBUG = os.getenv('DEBUG', 'False') == 'True'  # ❌ String comparison bug
DATABASE_PORT = os.getenv('DB_PORT', '5432')   # ❌ Still a string!

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DB_NAME'),  # ❌ No validation until connection
        'PORT': DATABASE_PORT,          # ❌ Type mismatch in production
    }
}
# ... 200+ more lines of unvalidated configuration
```

#### After: Django-CFG (Type-Safe Pydantic Configuration)

```python
# config.py - Type-safe Pydantic Django settings
from django_cfg import DjangoConfig
from django_cfg.models import DatabaseConfig

class MyConfig(DjangoConfig):
    """Production-grade type-safe Django configuration"""

    project_name: str = "My SaaS App"
    debug: bool = False  # ✅ Pydantic validates boolean conversion

    # Type-safe database configuration with startup validation
    databases: dict[str, DatabaseConfig] = {
        "default": DatabaseConfig(
            name="${DB_NAME}",     # ✅ Validated at startup
            port=5432,             # ✅ Type-checked integer
        )
    }
```

**Django Configuration Benefits:**
- ✅ **Pydantic v2 validation** - catch config errors before deployment
- ✅ **Full IDE autocomplete** - IntelliSense for all Django settings
- ✅ **90% less code** - reduce 200+ lines to 30 lines
- ✅ **Type hints everywhere** - mypy and pyright compatible

**[📚 Type-safe configuration guide →](https://djangocfg.com/docs/getting-started/configuration)**

---

### 🤖 AI Django Framework - Production-Ready AI Agents

**Django AI integration made simple** - type-safe AI agents, LLM workflow automation, and vector database built into Django.

```python
from django_cfg import DjangoConfig

class MyConfig(DjangoConfig):
    # AI-powered Django development - zero setup
    openai_api_key: str = "${OPENAI_API_KEY}"
    anthropic_api_key: str = "${ANTHROPIC_API_KEY}"

    # Enable AI Django agents (optional)
    enable_agents: bool = True        # AI workflow automation
    enable_knowbase: bool = True      # Vector database + RAG
```

**Django AI Features:**
- 🤖 **AI Agents Framework** - Type-safe Django LLM integration
- 📚 **Vector Database** - ChromaDB semantic search for Django
- 🔍 **RAG Integration** - Retrieval-augmented generation built-in
- 🎯 **Pydantic AI** - Type-safe AI input/output validation
- 🌐 **Multi-LLM** - OpenAI, Anthropic, Claude API support

**[📚 Django AI agents guide →](https://djangocfg.com/docs/ai-agents/introduction)**

---

### 📦 8 Production-Ready Enterprise Apps

**Ship features in days, not months** - everything you need is included:

- **👤 Accounts** - User management + OTP + SMS auth
- **🎫 Support** - Ticketing system + SLA tracking
- **📧 Newsletter** - Email campaigns + analytics
- **📊 Leads** - CRM + sales pipeline
- **🤖 AI Agents** - Optional workflow automation
- **📚 KnowBase** - Optional AI knowledge base + RAG
- **💳 Payments** - Multi-provider crypto/fiat payments
- **🔧 Maintenance** - Multi-site Cloudflare management

**Total time saved: 18 months of development**

**[📚 Explore all apps →](https://djangocfg.com/docs/features/built-in-apps)**

---

### 🎨 Modern API UI with Tailwind 4

**Beautiful browsable API** - 88% smaller bundle, 66% faster than old DRF UI.

- ✅ Glass morphism design
- ✅ Light/Dark/Auto themes
- ✅ Command palette (⌘K)
- ✅ 88% smaller bundle (278KB → 33KB)

**[📚 See API Theme →](https://djangocfg.com/docs/features/api-generation)**

---

### 🔄 Smart Multi-Database Routing

**Zero-config database routing** with automatic sharding:

```python
databases: dict[str, DatabaseConfig] = {
    "analytics": DatabaseConfig(
        name="${ANALYTICS_DB}",
        routing_apps=["analytics", "reports"],  # Auto-route!
    ),
}
```

✅ Auto-routes read/write • ✅ Cross-DB transactions • ✅ Connection pooling

**[📚 Multi-DB Guide →](https://djangocfg.com/docs/fundamentals/database)**

---

## ⚙️ Complete Configuration Example

**All available apps and integrations in one DjangoConfig:**

```python
from django_cfg import DjangoConfig
from django_cfg.models import DatabaseConfig, CacheConfig

class ProductionConfig(DjangoConfig):
    # Project settings
    project_name: str = "My Enterprise App"
    secret_key: str = "${SECRET_KEY}"
    debug: bool = False

    # 8 Built-in Enterprise Apps (enable as needed)
    enable_accounts: bool = True      # 👤 User management + OTP + SMS
    enable_support: bool = True       # 🎫 Ticketing + SLA tracking
    enable_newsletter: bool = True    # 📧 Email campaigns
    enable_leads: bool = True         # 📊 CRM + sales pipeline
    enable_agents: bool = True        # 🤖 AI workflow automation
    enable_knowbase: bool = True      # 📚 AI knowledge base + RAG
    enable_payments: bool = True      # 💳 Crypto/fiat payments
    enable_maintenance: bool = True   # 🔧 Cloudflare management

    # Infrastructure
    databases: dict[str, DatabaseConfig] = {
        "default": DatabaseConfig(name="${DB_NAME}"),
    }
    caches: dict[str, CacheConfig] = {
        "default": CacheConfig(backend="redis"),
    }

    # AI Providers (optional)
    openai_api_key: str = "${OPENAI_API_KEY}"
    anthropic_api_key: str = "${ANTHROPIC_API_KEY}"

    # Third-party Integrations
    twilio_account_sid: str = "${TWILIO_ACCOUNT_SID}"  # SMS
    stripe_api_key: str = "${STRIPE_API_KEY}"          # Payments
    cloudflare_api_token: str = "${CF_API_TOKEN}"      # CDN/DNS
```

**[📚 Full configuration reference →](https://djangocfg.com/docs/getting-started/configuration)**

---

## 📊 Django Configuration Framework Comparison

**Django-CFG vs Traditional Django, DRF, FastAPI, and django-environ:**

| Feature | Django settings.py | django-environ | DRF | FastAPI | **Django-CFG** |
|---------|-------------------|----------------|-----|---------|----------------|
| **Type-Safe Config** | ❌ Runtime | ⚠️ Basic | ❌ Manual | ✅ Pydantic | ✅ **Full Pydantic v2** |
| **IDE Autocomplete** | ❌ None | ❌ None | ❌ Manual | ⚠️ Partial | ✅ **100% IntelliSense** |
| **Startup Validation** | ❌ No | ⚠️ Partial | ❌ No | ✅ Yes | ✅ **Pydantic + Custom** |
| **Django Integration** | ✅ Native | ✅ Native | ✅ Native | ❌ Manual | ✅ **Seamless** |
| **Admin UI** | 🟡 Basic | 🟡 Basic | 🟡 Basic | ❌ None | ✅ **Modern Unfold** |
| **API Docs** | ❌ Manual | ❌ Manual | 🟡 Basic | ✅ Auto | ✅ **OpenAPI + Swagger** |
| **AI Agents Built-in** | ❌ Manual | ❌ None | ❌ Manual | ❌ Manual | ✅ **LLM Framework** |
| **Setup Time** | 🟡 Weeks | 🟡 Hours | 🟡 Weeks | 🟡 Days | ✅ **30 seconds** |
| **Enterprise Apps** | ❌ Build all | ❌ None | ❌ Build all | ❌ Build all | ✅ **8 included** |
| **Configuration Lines** | ⚠️ 200+ | ⚠️ 150+ | ⚠️ 200+ | ⚠️ 100+ | ✅ **30 lines** |

**Legend:** ✅ Excellent | 🟡 Requires Work | ⚠️ Partial | ❌ Not Available

**[📚 Django-CFG vs django-environ detailed comparison →](https://djangocfg.com/docs/getting-started/django-cfg-vs-alternatives)**

---

## 📚 Documentation

### 🚀 Getting Started
- **[Installation](https://djangocfg.com/docs/getting-started/installation)** - Quick setup guide
- **[First Project](https://djangocfg.com/docs/getting-started/first-project)** - Create your first app
- **[Configuration](https://djangocfg.com/docs/getting-started/configuration)** - Type-safe config guide
- **[Why Django-CFG?](https://djangocfg.com/docs/getting-started/why-django-cfg)** - Full comparison

### 🏗️ Core Features
- **[Built-in Apps](https://djangocfg.com/docs/features/built-in-apps)** - 8 enterprise apps
- **[API Generation](https://djangocfg.com/docs/features/api-generation)** - Auto OpenAPI docs
- **[Database](https://djangocfg.com/docs/fundamentals/database)** - Multi-DB routing
- **[Integrations](https://djangocfg.com/docs/features/integrations)** - Third-party services

### 🤖 AI Integration (Optional)
- **[AI Agents](https://djangocfg.com/docs/ai-agents/introduction)** - Workflow automation
- **[Creating Agents](https://djangocfg.com/docs/ai-agents/creating-agents)** - Build custom agents
- **[Django Integration](https://djangocfg.com/docs/ai-agents/django-integration)** - Connect to your app

### 🚀 Deployment
- **[Production Config](https://djangocfg.com/docs/deployment)** - Production best practices
- **[CLI Commands](https://djangocfg.com/docs/cli)** - 50+ management commands

---

## 🤝 Community & Support

### Resources
- 🌐 **[djangocfg.com](https://djangocfg.com/)** - Official website & documentation
- 🐙 **[GitHub](https://github.com/markolofsen/django-cfg)** - Source code & issues
- 💬 **[Discussions](https://github.com/markolofsen/django-cfg/discussions)** - Community support

### Links
- **[🚀 AI Project Generator](https://editor.djangocfg.com)** - Generate projects with AI
- **[🎯 Live Demo](http://demo.djangocfg.com)** - See it in action
- **[📦 PyPI](https://pypi.org/project/django-cfg/)** - Package repository

---

## 📄 License

**MIT License** - Free for commercial use

---

**Made with ❤️ by the Django-CFG Team**

---

<div align="center">

**Django AI Framework** • **Type-Safe Configuration** • **Pydantic Settings** • **Enterprise Apps**

Django-CFG is the AI-first Django framework for production-ready AI agents, type-safe Pydantic v2 configuration, and enterprise development. Replace settings.py with validated models, build AI workflows with Django ORM integration, and ship faster with 8 built-in apps. Perfect for Django LLM integration, AI-powered Django development, scalable Django architecture, and reducing Django boilerplate.

---

**Get Started:** **[Documentation](https://djangocfg.com/docs/getting-started/intro)** • **[AI Project Generator](https://editor.djangocfg.com)** • **[Live Demo](http://demo.djangocfg.com)**

</div>
