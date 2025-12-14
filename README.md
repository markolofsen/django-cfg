<div align="center">

<img src="https://raw.githubusercontent.com/markolofsen/django-cfg/refs/heads/main/static/logo.png" alt="Django-CFG Logo" width="200" />

# Django-CFG

[![PyPI](https://img.shields.io/pypi/v/django-cfg.svg?style=flat-square&logo=pypi)](https://pypi.org/project/django-cfg/)
[![Python](https://img.shields.io/badge/python-3.12+-blue.svg?style=flat-square&logo=python)](https://www.python.org/)
[![Django](https://img.shields.io/badge/django-5.2+-green.svg?style=flat-square&logo=django)](https://www.djangoproject.com/)
[![License](https://img.shields.io/badge/license-MIT-yellow.svg?style=flat-square)](LICENSE)
[![Downloads](https://img.shields.io/pypi/dm/django-cfg.svg?style=flat-square)](https://pypi.org/project/django-cfg/)

**The Modern Django Framework for Enterprise Applications**

Type-safe configuration • Next.js Admin • Real-time WebSockets • gRPC Streaming • AI-Native Docs • 8 Production Apps

[Get Started](https://djangocfg.com/docs/getting-started/intro) • [Live Demo](https://djangocfg.com/demo) • [Documentation](https://djangocfg.com/docs) • [MCP Server](https://djangocfg.com/mcp)

</div>

---

## What is Django-CFG?

**Django-CFG** is a next-generation Django framework that replaces `settings.py` with **type-safe Pydantic v2 models**. Catch configuration errors at startup, get full IDE autocomplete, and ship production-ready features in **30 seconds** instead of weeks.

### Why Django-CFG?

- ✅ **Type-safe config** - Pydantic v2 validation catches errors before deployment
- ✅ **90% less code** - Replace 200+ line settings.py with 30 lines
- ✅ **Built-in Next.js admin** - Modern React admin interface out of the box
- ✅ **Real-time WebSockets** - Centrifugo integration included
- ✅ **gRPC streaming** - Bidirectional streaming with WebSocket bridge
- ✅ **AI-native docs** - First Django framework with MCP server for AI assistants
- ✅ **8 enterprise apps** - Save 18+ months of development

---

## Quick Start

### One-Line Install

```bash
# macOS / Linux
curl -L https://djangocfg.com/install.sh | sh

# Windows (PowerShell)
powershell -c "iwr https://djangocfg.com/install.ps1 | iex"
```

### Manual Install

```bash
pip install 'django-cfg[full]'
django-cfg create-project my_app
cd my_app/projects/django
poetry run python manage.py runserver
```

**What you get instantly:**
- 🎨 Django Admin → `http://127.0.0.1:8000/admin/`
- ⚛️ Next.js Dashboard → Modern React interface
- 📡 Real-time WebSockets → Live updates
- 🐳 Docker Ready → Production configs
- 🖥️ Electron App → Desktop template

[→ Full Installation Guide](https://djangocfg.com/docs/getting-started/installation)

---

## Configuration Example

**Before: settings.py**
```python
# 200+ lines of untyped configuration
DEBUG = os.getenv('DEBUG', 'False') == 'True'  # ❌ Bug waiting to happen
DATABASE_PORT = os.getenv('DB_PORT', '5432')   # ❌ Still a string!
```

**After: Django-CFG**
```python
from django_cfg import DjangoConfig, DatabaseConfig

class MyConfig(DjangoConfig):
    project_name: str = "My App"
    debug: bool = False  # ✅ Type-safe

    databases: dict[str, DatabaseConfig] = {
        "default": DatabaseConfig(
            name="${DB_NAME}",  # ✅ Validated at startup
            port=5432,          # ✅ Correct type
        )
    }
```

**Full IDE autocomplete** • **Startup validation** • **Zero runtime errors**

---

## Features

### 🔒 Type-Safe Configuration
Pydantic v2 models replace error-prone `settings.py` - catch bugs before deployment.

### ⚛️ Next.js Admin
Only Django framework with built-in Next.js integration - modern admin UI out of the box.

### 📡 Real-Time WebSockets
Production-ready Centrifugo integration - live updates, notifications, presence tracking.

### 🌐 gRPC Microservices
Bidirectional streaming with automatic WebSocket bridge - perfect for real-time architectures.

### 🤖 AI-Native Documentation
First Django framework with MCP server - AI assistants can access docs instantly.

### 📦 8 Enterprise Apps
User auth • Support tickets • Newsletter • CRM • AI agents • Knowledge base • Payments • Multi-site

**Time saved: 18+ months of development**

[→ See All Features](https://djangocfg.com/docs)

---

## What's Included

**Backend:**
- Django 5.2+ with type-safe config
- PostgreSQL, Redis, Centrifugo
- gRPC server with streaming
- 8 production-ready apps
- AI agent framework
- REST API with auto TypeScript generation

**Frontend:**
- Next.js 16 admin interface
- React 19 + TypeScript
- Tailwind CSS 4
- Real-time WebSocket client
- PWA support

**DevOps:**
- Docker Compose setup
- Traefik reverse proxy
- Production-ready configs
- Cloudflare integration

**AI Features:**
- MCP server for AI assistants
- Pydantic AI integration
- Vector DB (ChromaDB)
- RAG support

---

## Documentation

- **[Getting Started](https://djangocfg.com/docs/getting-started/intro)** - Quick setup guide
- **[Configuration](https://djangocfg.com/docs/getting-started/configuration)** - Type-safe config
- **[Next.js Admin](https://djangocfg.com/docs/features/integrations/nextjs-admin)** - Modern admin UI
- **[Real-Time](https://djangocfg.com/docs/features/integrations/centrifugo)** - WebSockets setup
- **[gRPC](https://djangocfg.com/docs/features/integrations/grpc)** - Microservices
- **[AI Agents](https://djangocfg.com/docs/ai-agents/introduction)** - Automation
- **[Built-in Apps](https://djangocfg.com/docs/features/built-in-apps/overview)** - 8 enterprise apps

---

## Community

- 🌐 **[djangocfg.com](https://djangocfg.com/)** - Official website
- 🎯 **[Live Demo](https://djangocfg.com/demo)** - See it in action
- 🐙 **[GitHub](https://github.com/markolofsen/django-cfg)** - Source code
- 💬 **[Discussions](https://github.com/markolofsen/django-cfg/discussions)** - Get help
- 📦 **[PyPI](https://pypi.org/project/django-cfg/)** - Package repository

---

## License

MIT License - Free for commercial use

---

<div align="center">

**Django-CFG** - Modern Django framework with type-safe configuration, AI-native docs, Next.js admin, gRPC streaming, real-time WebSockets, and 8 production-ready apps.

Made with ❤️ for the Django community

[Get Started](https://djangocfg.com/docs) • [Live Demo](https://djangocfg.com/demo) • [GitHub](https://github.com/markolofsen/django-cfg)

</div>
