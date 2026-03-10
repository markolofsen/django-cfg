# Django-CFG

**Modern Django framework with type-safe Pydantic v2 configuration**

![Django-CFG](https://raw.githubusercontent.com/markolofsen/django-cfg/refs/heads/main/static/catroon.webp)

[![PyPI](https://img.shields.io/pypi/v/django-cfg.svg)](https://pypi.org/project/django-cfg/)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## What is this?

Django-CFG is a Django framework that replaces `settings.py` with type-safe Pydantic v2 models. It includes production-ready enterprise features like Next.js admin, WebSockets, AI agents, and background task processing.

**Key features:**
- Type-safe configuration with Pydantic v2
- Startup validation (catch config errors before deployment)
- Next.js admin integration
- Real-time WebSockets (Centrifugo)
- gRPC server support
- Background tasks (Redis Queue)
- AI agents framework
- 8 built-in enterprise apps

---

## Quick Start

```bash
# Install
pip install django-cfg[full]

# Create project
django-cfg create-project "My App"
cd my-app

# Run
python manage.py runserver
```

**Access:**
- Admin: http://127.0.0.1:8000/admin/
- API: http://127.0.0.1:8000/api/docs/

---

## Project Structure

This repository contains:

```
django-cfg/
├── projects/
│   ├── django-cfg-dev/          # PyPI package source
│   │   ├── src/django_cfg/      # Framework core
│   │   └── pyproject.toml       # Package config
│   │
│   ├── django/                  # Sample Django project
│   │   ├── apps/                # Built-in apps
│   │   └── api/                 # Configuration
│   │
│   └── web/                     # Documentation site
│       └── docs/                # Markdown docs
│
└── README.md                    # This file
```

---

## Installation Options

**Full install (recommended):**
```bash
pip install django-cfg[full]
```

**Individual extras:**
```bash
pip install django-cfg[grpc]        # gRPC microservices
pip install django-cfg[centrifugo]  # WebSockets
pip install django-cfg[rq]          # Background tasks
pip install django-cfg[ai]          # AI agents
```

**Available extras:**
- `[full]` - All features (grpc + centrifugo + rq + ai)
- `[grpc]` - gRPC server (grpcio, grpcio-tools, protobuf)
- `[centrifugo]` - Real-time WebSockets (cent, websockets)
- `[rq]` - Redis Queue (django-rq, rq-scheduler, hiredis)
- `[ai]` - AI framework (pydantic-ai)

---

## Development

### Local Development with Package

**Option 1: Use published package**
```bash
cd projects/django
poetry install
poetry run python manage.py runserver
```

**Option 2: Use local django-cfg**
```bash
cd projects/django
make install-local  # Uses local django-cfg with [full]
poetry run python manage.py runserver
```

### Work on Package

```bash
cd projects/django-cfg-dev
poetry install
poetry run pytest
```

### Documentation

```bash
cd projects/web
npm install
npm run dev  # http://localhost:3000
```

---

## Configuration Example

**Replace settings.py with type-safe config:**

```python
# config.py
from django_cfg import DjangoConfig, DatabaseConfig

class MyConfig(DjangoConfig):
    project_name: str = "My App"
    debug: bool = False
    secret_key: str = "${SECRET_KEY}"

    # Type-safe database
    databases: dict[str, DatabaseConfig] = {
        "default": DatabaseConfig(name="${DB_NAME}")
    }

    # Optional features
    enable_accounts: bool = True
    enable_support: bool = True
    enable_ai: bool = True

# settings.py (just 3 lines)
from .config import MyConfig
config = MyConfig()
globals().update(config.get_all_settings())
```

**Benefits:**
- IDE autocomplete for all settings
- Pydantic validation at startup
- 90% less boilerplate code
- Environment variable support

---

## Built-in Apps

Enable production-ready apps with one line:

| App | Description |
|-----|-------------|
| `accounts` | User management + OTP + SMS auth |
| `support` | Ticketing system + SLA tracking |
| `newsletter` | Email campaigns + analytics |
| `leads` | CRM + sales pipeline |
| `agents` | AI workflow automation |
| `knowbase` | Vector DB + RAG |
| `payments` | Multi-provider payments |
| `maintenance` | Multi-site management |

```python
class MyConfig(DjangoConfig):
    enable_accounts: bool = True
    enable_support: bool = True
    # ... more as needed
```

---

## Publishing

**Publish to PyPI:**

```bash
cd projects/django-cfg-dev

# Update version in pyproject.toml
# Update CHANGELOG.md

# Build and publish
poetry build
poetry publish
```

**Test locally before publish:**
```bash
pip install -e projects/django-cfg-dev[full]
```

---

## Documentation

- **Package docs:** `projects/django-cfg-dev/README.md` (published to PyPI)
- **Full docs:** `projects/web/docs/` (deployed to djangocfg.com)
- **Sample project:** `projects/django/` (demo all features)

---

## Architecture

**django-cfg-dev** (PyPI package):
- Framework core with Pydantic models
- Type-safe configuration classes
- Built-in enterprise apps
- Integration modules (gRPC, Centrifugo, Next.js)

**django** (Sample project):
- Shows all django-cfg features
- Production-ready configuration
- 8 enterprise apps enabled
- Used as reference implementation

**web** (Documentation):
- Docusaurus site with full guides
- API reference and examples
- Deployment guides

---

## Requirements

- Python 3.12+
- Django 5.2+ (peer dependency, install separately)
- PostgreSQL (recommended)
- Redis (for WebSockets/tasks)

---

## License

MIT License - Free for commercial use

---

## Links

- PyPI: https://pypi.org/project/django-cfg/
- Documentation: https://djangocfg.com
- Demo: http://demo.djangocfg.com

---

**For contributors:** See `CONTRIBUTING.md` in django-cfg-dev/

**For users:** Full documentation at https://djangocfg.com/docs/
