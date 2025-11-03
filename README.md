# Django-CFG: Type-Safe Django Configuration Framework

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

### 🚀 The Modern Django Framework for Enterprise Applications

**Type-safe configuration** • **Next.js Admin** • **AI Agents** • **Real-time WebSockets** • **8 Enterprise Apps**

**[🎯 Live Demo](http://demo.djangocfg.com)** • **[📚 Documentation](https://djangocfg.com/docs/getting-started/intro)** • **[🐙 GitHub](https://github.com/markolofsen/django-cfg)**

</div>

---

## 🎯 What is Django-CFG?

**Django-CFG** is a next-generation Django framework that replaces traditional `settings.py` with **type-safe Pydantic v2 models**. It eliminates runtime configuration errors, provides complete IDE autocomplete, and includes **production-ready enterprise features** out of the box.

### Why Django-CFG?

**Traditional Django problems:**
- ❌ **Runtime errors** - configuration bugs discovered in production
- ❌ **No IDE support** - zero autocomplete, manual documentation lookup
- ❌ **200+ lines** of unmaintainable settings.py
- ❌ **Weeks of setup** - for user auth, admin UI, payments, real-time features

**Django-CFG solution:**
- ✅ **Startup validation** - catch all config errors before deployment
- ✅ **Full IDE autocomplete** - IntelliSense for every setting
- ✅ **30 lines of code** - 90% boilerplate reduction
- ✅ **30 seconds to production** - everything included and ready

**[📚 Read the full comparison →](https://djangocfg.com/docs/getting-started/django-cfg-vs-alternatives)**

---

## 🚀 Quick Start

### Installation

```bash
pip install django-cfg
django-cfg create-project "My App"
cd my-app && python manage.py runserver
```

**What you get instantly:**
- 🎨 **Modern Admin UI** → `http://127.0.0.1:8000/admin/`
- ⚡ **Next.js Dashboard** (optional) → Modern React admin interface
- 📡 **Real-time WebSockets** → Live updates with Centrifugo
- 🚀 **Production-ready** → Type-safe config, security hardened

<div align="center">
<img src="https://raw.githubusercontent.com/markolofsen/django-cfg/refs/heads/main/static/startup.png" alt="Django-CFG Startup Screen" width="800">
<p><em>Django-CFG startup with type-safe configuration validation</em></p>
</div>

**[📚 Installation Guide →](https://djangocfg.com/docs/getting-started/installation)**

### Optional Features (Extras)

Install additional features based on your needs:

```bash
# Full installation (recommended for production)
pip install django-cfg[full]

# Individual extras
pip install django-cfg[grpc]        # gRPC microservices
pip install django-cfg[centrifugo]  # Real-time WebSockets
pip install django-cfg[rq]          # Background tasks with Redis Queue
pip install django-cfg[ai]          # AI agents with Pydantic AI

# Combine multiple extras
pip install django-cfg[grpc,centrifugo,rq]
```

**Available extras:**
- 🔄 **`[full]`** - All features (grpc + centrifugo + rq + ai)
- 🌐 **`[grpc]`** - gRPC server support (grpcio, grpcio-tools, protobuf)
- 📡 **`[centrifugo]`** - Real-time WebSocket integration (cent, websockets)
- 📋 **`[rq]`** - Redis Queue for background tasks (django-rq, rq-scheduler)
- 🤖 **`[ai]`** - AI agents framework (pydantic-ai)

---

### Try Live Demo

**See Django-CFG in action:**

**[→ http://demo.djangocfg.com](http://demo.djangocfg.com)**

**Demo credentials:**
- **Admin:** `admin@example.com` / `admin123`

**Explore:** Modern admin • Next.js dashboard • AI agents • Real-time updates • Support system

---

## 💡 Core Features

### 🔒 Type-Safe Configuration with Pydantic v2

**Replace error-prone settings.py with validated Pydantic models.**

#### Before: Django settings.py
```python
# settings.py - Runtime errors, no validation
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
# ... 200+ more lines
```

#### After: Django-CFG
```python
# config.py - Type-safe, validated at startup
from django_cfg import DjangoConfig, DatabaseConfig

class MyConfig(DjangoConfig):
    """Production-ready type-safe configuration"""

    project_name: str = "My App"
    debug: bool = False  # ✅ Pydantic validates boolean

    # Type-safe database with startup validation
    databases: dict[str, DatabaseConfig] = {
        "default": DatabaseConfig(
            name="${DB_NAME}",  # ✅ Validated at startup
            port=5432,          # ✅ Type-checked integer
        )
    }
```

**Benefits:**
- ✅ **Pydantic v2 validation** - catch errors before deployment
- ✅ **Full IDE autocomplete** - IntelliSense everywhere
- ✅ **90% less code** - 200+ lines → 30 lines
- ✅ **Type hints** - mypy and pyright compatible

**[📚 Type-safe configuration guide →](https://djangocfg.com/docs/fundamentals/core/type-safety)**

---

### ⚛️ Next.js Admin Integration

**Build modern admin interfaces with React** - the only Django framework with built-in Next.js integration.

```python
from django_cfg import DjangoConfig, NextJsAdminConfig

class MyConfig(DjangoConfig):
    # One line for complete Next.js admin!
    nextjs_admin: NextJsAdminConfig = NextJsAdminConfig(
        project_path="../admin",
    )
```

**What you get:**
- 🌐 **Three-in-One Architecture** - Public site + User dashboard + Admin panel in ONE Next.js project
- ⚙️ **Dual Admin Strategy** - Django Unfold (90% quick CRUD) + Next.js (10% complex features)
- ✨ **Zero Configuration** - Auto JWT auth, theme sync, TypeScript generation
- 📦 **60% Smaller** - ZIP deployment (~7MB vs ~20MB)
- ⚡ **Auto-Detection** - Dev mode automatically detected on ports 3000/3001

**No migration needed** - start with built-in admin, add Next.js when you need complex features!

**[📚 Next.js Admin Documentation →](https://djangocfg.com/docs/features/integrations/nextjs-admin)**

---

### 📡 Real-Time WebSockets with Centrifugo

**Production-ready WebSocket integration** - live updates, notifications, and real-time collaboration.

```python
from django_cfg import DjangoConfig, CentrifugoConfig

class MyConfig(DjangoConfig):
    # Enable real-time features
    centrifugo: CentrifugoConfig = CentrifugoConfig(
        enabled=True,
        api_url="http://localhost:8001/api",
    )
```

**Built-in features:**
- ⚡ **Live Updates** - Real-time data synchronization
- 🔔 **Notifications** - Push notifications to connected clients
- 👥 **Presence** - Track online users
- 💬 **Chat** - Real-time messaging out of the box
- 🔒 **JWT Auth** - Secure WebSocket connections

**[📚 Centrifugo Integration Guide →](https://djangocfg.com/docs/features/integrations/centrifugo)**

---

### 🤖 AI-Ready Infrastructure

**Built-in AI agent framework** - LLM workflow automation with Django ORM integration.

```python
from django_cfg import DjangoConfig

class MyConfig(DjangoConfig):
    # AI features (optional)
    openai_api_key: str = "${OPENAI_API_KEY}"
    anthropic_api_key: str = "${ANTHROPIC_API_KEY}"

    enable_agents: bool = True      # AI workflow automation
    enable_knowbase: bool = True    # Vector DB + RAG
```

**Features:**
- 🤖 **AI Agents Framework** - Type-safe LLM integration
- 📚 **Vector Database** - ChromaDB for semantic search
- 🔍 **RAG** - Retrieval-augmented generation
- 🎯 **Pydantic AI** - Validated AI input/output
- 🌐 **Multi-LLM** - OpenAI, Anthropic, Claude support

**[📚 AI Agents Guide →](https://djangocfg.com/docs/ai-agents/introduction)**

---

### 📦 8 Enterprise Apps Included

**Ship features in days, not months** - production-ready apps out of the box:

| App | Description | Time Saved |
|-----|-------------|------------|
| 👤 **Accounts** | User management + OTP + SMS auth | 3-4 weeks |
| 🎫 **Support** | Ticketing system + SLA tracking | 2-3 weeks |
| 📧 **Newsletter** | Email campaigns + analytics | 2-3 weeks |
| 📊 **Leads** | CRM + sales pipeline | 2-3 weeks |
| 🤖 **AI Agents** | Workflow automation | 3-4 weeks |
| 📚 **KnowBase** | AI knowledge base + RAG | 2-3 weeks |
| 💳 **Payments** | Multi-provider payments | 2-3 weeks |
| 🔧 **Maintenance** | Multi-site management | 1-2 weeks |

**Total time saved: 18+ months of development**

```python
class MyConfig(DjangoConfig):
    # Enable apps as needed (one line each!)
    enable_accounts: bool = True
    enable_support: bool = True
    enable_newsletter: bool = True
    enable_leads: bool = True
    enable_agents: bool = True
    enable_knowbase: bool = True
    enable_payments: bool = True
    enable_maintenance: bool = True
```

**[📚 Built-in Apps Overview →](https://djangocfg.com/docs/features/built-in-apps/overview)**

---

### 🎨 Modern API UI with Tailwind 4

**Beautiful browsable API** - 88% smaller bundle, modern design.

- ✅ Glass morphism design
- ✅ Light/Dark/Auto themes
- ✅ Command palette (⌘K)
- ✅ 88% smaller (278KB → 33KB)
- ✅ Auto-generated TypeScript clients

**[📚 API Generation Guide →](https://djangocfg.com/docs/features/api-generation/overview)**

---

### 🔄 Smart Multi-Database Routing

**Zero-config database routing** with automatic sharding:

```python
from django_cfg import DjangoConfig, DatabaseConfig

class MyConfig(DjangoConfig):
    databases: dict[str, DatabaseConfig] = {
        "default": DatabaseConfig(
            name="${DB_NAME}",
        ),
        "analytics": DatabaseConfig(
            name="${ANALYTICS_DB}",
            routing_apps=["analytics", "reports"],  # Auto-route!
        ),
    }
```

✅ Auto-routes read/write • ✅ Cross-DB transactions • ✅ Connection pooling

**[📚 Multi-Database Guide →](https://djangocfg.com/docs/fundamentals/database/multi-database)**

---

## ⚙️ Complete Configuration Example

**All features in one DjangoConfig:**

```python
from django_cfg import DjangoConfig, DatabaseConfig, CacheConfig, NextJsAdminConfig

class ProductionConfig(DjangoConfig):
    # Project
    project_name: str = "My Enterprise App"
    secret_key: str = "${SECRET_KEY}"
    debug: bool = False

    # Next.js Admin (optional)
    nextjs_admin: NextJsAdminConfig = NextJsAdminConfig(
        project_path="../admin",
    )

    # Real-time WebSockets (optional)
    centrifugo: CentrifugoConfig = CentrifugoConfig(
        enabled=True,
    )

    # 8 Enterprise Apps (enable as needed)
    enable_accounts: bool = True      # User management
    enable_support: bool = True       # Ticketing
    enable_newsletter: bool = True    # Email campaigns
    enable_leads: bool = True         # CRM
    enable_agents: bool = True        # AI automation
    enable_knowbase: bool = True      # Vector DB
    enable_payments: bool = True      # Payments
    enable_maintenance: bool = True   # Site management

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

    # Integrations
    twilio_account_sid: str = "${TWILIO_ACCOUNT_SID}"
    stripe_api_key: str = "${STRIPE_API_KEY}"
    cloudflare_api_token: str = "${CF_API_TOKEN}"
```

**[📚 Configuration Reference →](https://djangocfg.com/docs/getting-started/configuration)**

---

## 📊 Comparison with Alternatives

### Django-CFG vs Traditional Solutions

| Feature | settings.py | django-environ | pydantic-settings | **Django-CFG** |
|---------|-------------|----------------|-------------------|----------------|
| **Type Safety** | ❌ Runtime | ⚠️ Basic | ✅ Pydantic | ✅ **Full Pydantic v2** |
| **IDE Autocomplete** | ❌ None | ❌ None | ⚠️ Partial | ✅ **100%** |
| **Startup Validation** | ❌ No | ⚠️ Partial | ✅ Yes | ✅ **Yes + Custom** |
| **Next.js Admin** | ❌ Manual | ❌ None | ❌ None | ✅ **Built-in** |
| **WebSocket (Centrifugo)** | ❌ Manual | ❌ None | ❌ None | ✅ **Built-in** |
| **Enterprise Apps** | ❌ Build all | ❌ None | ❌ None | ✅ **8 included** |
| **AI Framework** | ❌ Manual | ❌ None | ❌ None | ✅ **Built-in** |
| **Setup Time** | 🟡 Weeks | 🟡 Hours | 🟡 Days | ✅ **30 seconds** |
| **Config Lines** | ⚠️ 200+ | ⚠️ 150+ | ⚠️ 100+ | ✅ **30 lines** |

**Legend:** ✅ Excellent | 🟡 Requires Work | ⚠️ Partial | ❌ Not Available

**[📚 Detailed Comparison Guide →](https://djangocfg.com/docs/getting-started/django-cfg-vs-alternatives)**

---

## 📚 Documentation

### 🚀 Getting Started
- **[Installation](https://djangocfg.com/docs/getting-started/installation)** - Quick setup
- **[First Project](https://djangocfg.com/docs/getting-started/first-project)** - Create your first app
- **[Configuration](https://djangocfg.com/docs/getting-started/configuration)** - Type-safe config
- **[Why Django-CFG?](https://djangocfg.com/docs/getting-started/why-django-cfg)** - Full comparison

### ⚛️ Next.js Integration
- **[Overview](https://djangocfg.com/docs/features/integrations/nextjs-admin)** - Three-in-One architecture
- **[Core Concepts](https://djangocfg.com/docs/features/integrations/nextjs-admin/concepts)** - Philosophy & design
- **[Quick Start](https://djangocfg.com/docs/features/integrations/nextjs-admin/quick-start)** - 5-minute setup
- **[Configuration](https://djangocfg.com/docs/features/integrations/nextjs-admin/configuration)** - All options

### 📡 Real-Time Features
- **[Centrifugo Integration](https://djangocfg.com/docs/features/integrations/centrifugo)** - WebSocket setup
- **[Live Updates](https://djangocfg.com/docs/features/integrations/centrifugo/live-updates)** - Real-time data

### 🏗️ Core Features
- **[Built-in Apps](https://djangocfg.com/docs/features/built-in-apps/overview)** - 8 enterprise apps
- **[API Generation](https://djangocfg.com/docs/features/api-generation/overview)** - Auto TypeScript clients
- **[Database](https://djangocfg.com/docs/fundamentals/database/multi-database)** - Multi-DB routing
- **[Type Safety](https://djangocfg.com/docs/fundamentals/core/type-safety)** - Pydantic validation

### 🤖 AI Features (Optional)
- **[AI Agents](https://djangocfg.com/docs/ai-agents/introduction)** - Workflow automation
- **[Creating Agents](https://djangocfg.com/docs/ai-agents/creating-agents)** - Build custom agents
- **[Django Integration](https://djangocfg.com/docs/ai-agents/django-integration)** - ORM integration

### 🚀 Deployment
- **[Production Config](https://djangocfg.com/docs/deployment)** - Best practices
- **[CLI Commands](https://djangocfg.com/docs/cli)** - 50+ commands

---

## 🤝 Community & Support

### Resources
- 🌐 **[djangocfg.com](https://djangocfg.com/)** - Official website & docs
- 🐙 **[GitHub](https://github.com/markolofsen/django-cfg)** - Source code & issues
- 💬 **[Discussions](https://github.com/markolofsen/django-cfg/discussions)** - Community support

### Links
- **[🎯 Live Demo](http://demo.djangocfg.com)** - See it in action
- **[📦 PyPI](https://pypi.org/project/django-cfg/)** - Package repository
- **[📚 Documentation](https://djangocfg.com/docs)** - Complete guides

---

## 📄 License

**MIT License** - Free for commercial use

---

**Made with ❤️ by the Django-CFG Team**

---

<div align="center">

**Modern Django Framework** • **Type-Safe Configuration** • **Next.js Admin** • **Real-Time WebSockets** • **AI-Ready**

Django-CFG is the modern Django framework for enterprise applications. Built with Pydantic v2 for type-safe configuration, includes Next.js admin integration, Centrifugo WebSocket support, AI agent framework, and 8 production-ready apps. Perfect for building scalable Django applications with reduced boilerplate and enterprise features out of the box.

---

**Get Started:** **[Documentation](https://djangocfg.com/docs/getting-started/intro)** • **[Live Demo](http://demo.djangocfg.com)** • **[GitHub](https://github.com/markolofsen/django-cfg)**

</div>
