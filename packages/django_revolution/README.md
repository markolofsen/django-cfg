# Django Revolution

> **Zero-config TypeScript & Python client generator for Django REST Framework** 🚀

[![PyPI version](https://badge.fury.io/py/django-revolution.svg)](https://badge.fury.io/py/django-revolution)
[![Python Support](https://img.shields.io/pypi/pyversions/django-revolution.svg)](https://pypi.org/project/django-revolution/)
[![Django Support](https://img.shields.io/pypi/djversions/django-revolution.svg)](https://pypi.org/project/django-revolution/)
[![License](https://img.shields.io/badge/license-Non--Commercial-red.svg)](LICENSE)

---

## 🏢 **Developed by Django-CFGAI - Epic Games Partner**

**AI-Powered Solutions for the Future** 🚀

We specialize in cutting-edge AI solutions, SaaS/PaaS development, and custom software that transforms businesses and drives innovation.

🌐 **Learn more:** [https://djangocfg.com/](https://djangocfg.com/)

### 📦 **Ready-to-Use Integration**

Django Revolution is **built-in** to [**django-cfg**](https://djangocfg.com/) - the ultimate Django configuration framework. Get both powerful configuration management AND automatic API client generation out of the box!

🔗 **Get started with django-cfg:** [https://djangocfg.com/](https://djangocfg.com/)

---

## ✨ What is Django Revolution?

**The fastest way to generate fully-authenticated TypeScript + Python clients from Django REST Framework.**

- 🧩 Organize your API into **zones** (`public`, `admin`, `mobile`, etc.)
- ⚙️ Generate strongly typed clients with **one command**
- 🔐 Built-in support for **Bearer tokens**, refresh logic, and API keys
- 🔄 Zero config for **Swagger/OpenAPI URLs** and **frontend integration**
- 🚀 **Dynamic zone management** - no static files, everything generated in-memory
- 🎨 **Rich CLI interface** - interactive commands with beautiful output
- ⚡ **Multithreaded generation** - parallel processing for faster client generation
- 🧪 **Comprehensive testing** - full test suite with pytest
- 🔧 **Ready-to-use Pydantic configs** - type-safe configuration with IDE support

> No boilerplate. No manual sync. Just clean clients in seconds.

## 🧪 Example: Instantly Get a Typed API Client

### TypeScript Client

```typescript
import API from '@myorg/api-client';

const api = new API('https://api.example.com');
api.setToken('your-access-token');

const profile = await api.public.getProfile();
const items = await api.public.listItems();
```

### Python Client

```python
from django_revolution_public import Client
from django_revolution_public.api.default import get_posts_list

# Configure API client
client = Client(base_url="https://api.example.com")
client = client.with_headers({"Authorization": "Bearer your-access-token"})

# Use generated functions with proper types
posts = get_posts_list.sync(client=client)
print(f"Found {len(posts.results)} posts")

# Async support
posts = await get_posts_list.asyncio(client=client)
```

> 🔐 Auth, ⚙️ Headers, 🔄 Refresh – handled automatically.

## ⛔ Without Django Revolution

Manually update OpenAPI spec → Run generator → Fix broken types → Sync clients → Write token logic → Repeat on every change.

## ✅ With Django Revolution

One command. Done.

### 🐍 Modern Python Generation

Django Revolution now uses `openapi-python-client` for:

- ✅ **Proper Enum generation** - Real `Enum` classes instead of `Optional[str]`
- ✅ **Pydantic v2 compatibility** - No more validation errors
- ✅ **Modern HTTP clients** - Using `httpx` for better performance  
- ✅ **attrs-based models** - Clean, efficient data classes
- ✅ **Type-safe configuration** - Full IDE autocomplete and validation
- ✅ **Automatic code formatting** - Built-in `ruff` formatting

## 🚀 5-Minute Setup

### 1. Install

```bash
pip install django-revolution
```

> **Note:** Django Revolution now uses `openapi-python-client` for modern Python client generation with proper enum support and attrs-based models. The system automatically detects the environment and works with Poetry, pip, or direct installation.

### 2. Add to Django Settings

```python
# settings.py
INSTALLED_APPS = [
    'drf_spectacular',
    'django_revolution',  # Add this line
]
```

### 3. **Easy Configuration with Ready-to-Use Configs** 🎯

Django Revolution provides **pre-built Pydantic configurations** that you can import and use directly:

#### **DRF + Spectacular Configuration** (services.py)

```python
# api/settings/config/services.py
from django_revolution import create_drf_spectacular_config

class SpectacularConfig(BaseModel):
    """API documentation configuration using django_revolution DRF config."""

    title: str = Field(default='API')
    description: str = Field(default='RESTful API')
    version: str = Field(default='1.0.0')
    schema_path_prefix: str = Field(default='/apix/')
    enable_browsable_api: bool = Field(default=False)
    enable_throttling: bool = Field(default=False)

    def get_django_settings(self) -> Dict[str, Any]:
        """Get drf-spectacular settings using django_revolution config."""
        # Use django_revolution DRF config - zero boilerplate!
        return create_drf_spectacular_config(
            title=self.title,
            description=self.description,
            version=self.version,
            schema_path_prefix=self.schema_path_prefix,
            enable_browsable_api=self.enable_browsable_api,
            enable_throttling=self.enable_throttling,
        )
```

#### **Zone Configuration** (revolution.py)

```python
# api/settings/config/revolution.py
from django_revolution.app_config import (
    DjangoRevolutionConfig,
    ZoneConfig,
    get_revolution_config
)

def create_revolution_config(env) -> Dict[str, Any]:
    """Get Django Revolution configuration as dictionary."""

    # Define zones with typed Pydantic models
    zones = {
        'public': ZoneConfig(
            apps=['accounts', 'billing', 'payments', 'support', 'public'],
            title='Public API',
            description='API for public client applications',
            public=True,
            auth_required=False,
            version='v1'
        ),
        'internal': ZoneConfig(
            apps=['system', 'mailer'],
            title='Internal API',
            description='Internal API for backend services',
            public=False,
            auth_required=True,
            version='v1'
        ),
        'admin': ZoneConfig(
            apps=['admin_panel', 'services'],
            title='Admin API',
            description='Administrative API endpoints',
            public=False,
            auth_required=True,
            version='v1'
        )
    }

    # Simple setup
    project_root = env.root_dir
    return get_revolution_config(project_root=project_root, zones=zones, debug=env.debug)
```

### 4. **Multithreaded Generation** ⚡

Django Revolution supports **multithreaded generation** for faster processing:

```python
# settings.py
DJANGO_REVOLUTION = {
    'enable_multithreading': True,  # Enable parallel processing
    'max_workers': 20,              # Maximum worker threads (default: 20)
    # ... other settings
}
```

**CLI Options:**
```bash
# Use 10 worker threads
python manage.py revolution --generate --max-workers 10

# Disable multithreading
python manage.py revolution --generate --no-multithreading
```

### 5. Generate Clients

```bash
# Generate everything (interactive mode)
python manage.py revolution

# Generate specific zones
python manage.py revolution --zones client admin

# TypeScript only
python manage.py revolution --typescript


```

## 🧬 What Does It Generate?

| Language       | Location                      | Structure                                                 |
| -------------- | ----------------------------- | --------------------------------------------------------- |
| **TypeScript** | `openapi/clients/typescript/` | `public/`, `admin/` → `index.ts`, `types.ts`, `services/` |
| **Python**     | `openapi/clients/python/`     | `public/`, `admin/` → `models/`, `services/`, `api_config.py` |

💡 Each zone gets its own NPM/PyPI-style package. Ready to publish or import.

### 🐍 Modern Python Client Structure

The new Python client generation using `openapi-python-client` creates:

```
python/
├── models/
│   ├── __init__.py
│   ├── user.py          # attrs-based models
│   ├── post.py
│   ├── status_enum.py   # Real Enum classes!
│   └── ...
├── api/
│   ├── __init__.py
│   └── default/         # API endpoints
├── client.py            # Main HTTP client
├── types.py             # Type definitions
└── __init__.py
```

**Features:**
- ✅ **Real Enum classes** - Proper `Enum` types instead of `Optional[str]`
- ✅ **attrs-based models** - Clean, efficient data classes
- ✅ **Modern HTTP client** - Using `httpx` for better performance
- ✅ **Type-safe configuration** - Full IDE autocomplete
- ✅ **Automatic formatting** - Built-in `ruff` code formatting
- ✅ **Clean structure** - No duplicate files, only essential components

## ⚡️ TypeScript Client Auth & Usage

Django Revolution automatically generates a smart TypeScript API client with built-in authentication:

```typescript
import API from '@myorg/api-client';

const api = new API('https://api.example.com');

// Authentication
api.setToken('your-access-token', 'your-refresh-token');

// Call any endpoint
const user = await api.public.getCurrentUser();
const products = await api.public.listProducts();

// Check authentication status
if (api.isAuthenticated()) {
  // User is logged in
}
```

**Features included:**

- ✅ Automatic token management (localStorage)
- ✅ Custom headers support
- ✅ API key authentication
- ✅ Zone-based endpoint organization
- ✅ TypeScript types for all endpoints
- ✅ Error handling and validation

## 🌐 Auto-Generated URLs

Django Revolution **automatically generates** all necessary URLs for your API zones:

```python
# urls.py
from django_revolution import add_revolution_urls

urlpatterns = [
    # Your existing URLs
    path('admin/', admin.site.urls),
]

# Django Revolution automatically adds:
# - /schema/public/schema/ (OpenAPI spec)
# - /schema/public/schema/swagger/ (Swagger UI)
# - /schema/public/redoc/ (Redoc UI)
# - /schema/admin/schema/ (OpenAPI spec)
# - /schema/admin/schema/swagger/ (Swagger UI)
# - /schema/admin/redoc/ (Redoc UI)
# - /api/public/ (Public API endpoints)
# - /api/admin/ (Admin API endpoints)
# - /openapi/archive/ (Generated clients)
urlpatterns = add_revolution_urls(urlpatterns)
```

## 🧪 CLI Toolbox

### Django Management Commands

```bash
# Generate all clients (interactive mode)
python manage.py revolution

# Specific zones
python manage.py revolution --zones public admin

# Generator options
python manage.py revolution --typescript
python manage.py revolution --python
python manage.py revolution --no-archive



# Utility commands
python manage.py revolution --status
python manage.py revolution --list-zones
python manage.py revolution --validate
python manage.py revolution --clean

# New validation commands
python manage.py revolution --validate-zones
python manage.py revolution --show-urls
python manage.py revolution --test-schemas
```

### Standalone CLI (Interactive)

```bash
# Interactive CLI with rich interface
django-revolution

# Or run directly
python -m django_revolution.cli
```

## 📁 Generated Output

**Generated locally:**

- `openapi/clients/typescript/` - TypeScript clients
- `openapi/clients/python/` - Python clients
- `openapi/archive/` - Versioned archives

## 🔧 Configuration

### **Easy Configuration with Ready-to-Use Configs** 🎯

Django Revolution provides **pre-built Pydantic configurations** that eliminate manual setup:

#### **1. DRF + Spectacular Configuration**

```python
# api/settings/config/services.py
from django_revolution import create_drf_spectacular_config

# One function call - everything configured with proper enum support!
settings_dict = create_drf_spectacular_config(
    title="My API",
    description="My awesome API",
    version="1.0.0",
    schema_path_prefix="/apix/",
    enable_browsable_api=False,
    enable_throttling=True,
)

# Get Django settings with comprehensive enum generation
REST_FRAMEWORK = settings_dict['REST_FRAMEWORK']
SPECTACULAR_SETTINGS = settings_dict['SPECTACULAR_SETTINGS']
```

#### **2. Zone Configuration**

```python
# api/settings/config/revolution.py
from django_revolution.app_config import ZoneConfig, get_revolution_config

# Typed zone definitions with Pydantic models
zones = {
    'public': ZoneConfig(
        apps=['accounts', 'billing', 'payments'],
        title='Public API',
        description='API for public client applications',
        public=True,
        auth_required=False,
        version='v1'
    ),
    'admin': ZoneConfig(
        apps=['admin_panel', 'analytics'],
        title='Admin API',
        description='Administrative API endpoints',
        public=False,
        auth_required=True,
        version='v1'
    )
}

# Simple configuration
config = get_revolution_config(project_root=Path.cwd(), zones=zones)
```

## ✅ When to Use

### ✅ Perfect For

- **Large Django projects** with multiple API audiences
- **Teams** needing consistent API client generation
- **Projects** requiring zone-based API organization
- **Automated CI/CD** pipelines
- **Frontend/backend separation** projects

### ❌ Not For

- **Simple single-zone APIs** (overkill)
- **Non-Django projects** (use Fern.dev instead)
- **Manual control freaks** (use drf-spectacular + generators)

## 🧠 Power Features

### Dynamic Zone Management

**No more static files!** Django Revolution uses **in-memory dynamic module generation**:

- ✅ **Zero static files** - Everything generated dynamically
- ✅ **Zone caching** - Fast repeated generation
- ✅ **Module registry** - Automatic cleanup and management
- ✅ **URL pattern validation** - Real-time validation
- ✅ **Schema testing** - Test generation before production

### Archive Management

```bash
# Automatic versioning with timestamped archives
openapi/archive/
├── files/
│   ├── 2024-01-15_14-30-00/
│   │   ├── public.zip
│   │   └── admin.zip
│   └── 2024-01-15_15-45-00/
│       ├── public.zip
│       └── admin.zip
└── latest/
    ├── public.zip
    └── admin.zip
```

Each archive contains both TypeScript and Python clients:

- `typescript/` - Generated TypeScript client
- `python/` - Generated Python client

### Custom Templates

```python
'generators': {
    'typescript': {
        'custom_templates': './templates/typescript'
    },
    'python': {
        'custom_templates': './templates/python'
    }
}
```

### Programmatic Usage

```python
from django_revolution import OpenAPIGenerator, get_settings

config = get_settings()
generator = OpenAPIGenerator(config)
summary = generator.generate_all(zones=['public', 'admin'])
```

## 📊 Comparison Table

| Feature                           | Django Revolution  | drf-spectacular + generators | openapi-generator-cli | Fern.dev | Manual Setup |
| --------------------------------- | ------------------ | ---------------------------- | --------------------- | -------- | ------------ |
| **Zone-based architecture**       | ✅ **UNIQUE**      | ❌                           | ❌                    | ✅       | ❌           |
| **Dynamic zone management**       | ✅ **UNIQUE**      | ❌                           | ❌                    | ❌       | ❌           |
| **Automatic URL generation**      | ✅ **UNIQUE**      | ❌                           | ❌                    | ❌       | ❌           |

| **Django management commands**    | ✅ **UNIQUE**      | ❌                           | ❌                    | ❌       | ❌           |
| **Rich CLI interface**            | ✅ **UNIQUE**      | ❌                           | ❌                    | ✅       | ❌           |
| **Zone validation & testing**     | ✅ **UNIQUE**      | ❌                           | ❌                    | ❌       | ❌           |
| **Archive management**            | ✅ **UNIQUE**      | ❌                           | ❌                    | ❌       | ❌           |
| **TypeScript + Python clients**   | ✅                 | ✅                           | ✅                    | ✅       | ✅           |
| **DRF native integration**        | ✅ **SEAMLESS**    | ✅                           | ⚠️ (via schema)       | ❌       | ✅           |
| **Ready-to-use Pydantic configs** | ✅ **UNIQUE**      | ❌                           | ❌                    | ❌       | ❌           |
| **Zero configuration**            | ✅ **UNIQUE**      | ❌                           | ❌                    | ❌       | ❌           |
| **Environment variables**         | ✅ **Pydantic**    | ❌                           | ❌                    | ❌       | ❌           |
| **CLI interface**                 | ✅ **Rich output** | ❌                           | ✅                    | ✅       | ❌           |
| **Multithreaded generation**      | ✅ **UNIQUE**      | ❌                           | ❌                    | ❌       | ❌           |
| **Comprehensive testing**         | ✅ **UNIQUE**      | ❌                           | ❌                    | ❌       | ❌           |
| **Modern Python client generation** | ✅ **openapi-python-client** | ❌ | ✅ | ❌ | ❌ |
| **Proper Enum generation** | ✅ **UNIQUE** | ❌ | ⚠️ | ✅ | ❌ |

## 🙋 FAQ

**Q: Is this production-ready?**  
✅ Yes. Used in multi-tenant production apps and large-scale Django projects.

**Q: What if I use DRF with custom auth?**  
Use `setHeaders()` or `setApiKey()` to inject custom logic.

**Q: Can I use this for simple projects?**  
Absolutely! Django Revolution works great for any Django project, from simple APIs to complex multi-zone applications.

**Q: What if I need only TypeScript clients?**  
Use `--typescript` flag to generate only TS clients.

**Q: Does it support custom OpenAPI decorators?**  
Yes, built on `drf-spectacular` so all extensions apply.

**Q: How do I use the ready-to-use Pydantic configs?**  
Simply import and use: `from django_revolution.drf_config import create_drf_config` and `from django_revolution.app_config import ZoneConfig, get_revolution_config`.

**Q: Are the Pydantic configs type-safe?**  
Yes! Full Pydantic v2 validation with IDE autocomplete and error checking.

**Q: What's new in the latest version?**  
- 🚀 **Dynamic zone management** - No more static files, everything generated in-memory
- 🎨 **Rich CLI interface** - Beautiful interactive commands with progress tracking
- ✅ **Zone validation & testing** - Validate zones and test schema generation
- 🔧 **Unified CLI architecture** - Single codebase for Django commands and standalone CLI
- 📊 **Enhanced output** - Rich tables and progress indicators
- ⚡ **Multithreaded generation** - Parallel processing for faster client generation
- 🧪 **Comprehensive testing** - Full test suite with pytest and proper mocking

- 🐍 **Modern Python client generation** - Switched to `openapi-python-client` for proper enum generation and attrs-based models
- 🎯 **Fixed enum generation** - Real `Enum` classes instead of `Optional[str]`

**Q: How does the dynamic zone system work?**  
Django Revolution creates URL configuration modules in-memory using Python's `importlib` and `exec`. This eliminates the need for static `.py` files and provides better performance and flexibility.

**Q: How does multithreading improve performance?**  
Multithreading allows parallel processing of multiple zones, schema generation, and client generation. For 3 zones, you can see 2-3x speedup compared to sequential processing.

**Q: What's the difference between the old and new Python client generation?**  
We switched from multiple generators to `openapi-python-client` for proper enum generation (real `Enum` classes instead of `Optional[str]`), attrs-based models, better type safety, and automatic code formatting with `ruff`.

**Q: Does it work without Poetry?**  
Yes! Django Revolution automatically detects your environment and tries multiple ways to run `openapi-python-client`:
1. Direct command: `openapi-python-client`
2. Poetry: `poetry run openapi-python-client`  
3. Python module: `python -m openapi_python_client`
4. Fallback to Poetry (most common)

This ensures it works in any environment - development, production, CI/CD, or Docker containers.



## 🤝 Contributing

```bash
# Development setup
git clone https://github.com/markolofsen/django-revolution.git
cd django-revolution
pip install -e ".[dev]"

# Run tests
pytest
black django_revolution/
isort django_revolution/
```

## 📞 Support

- **Documentation**: [https://revolution.djangocfg.com/](https://revolution.djangocfg.com/)
- **Issues**: [https://github.com/markolofsen/django-revolution/issues](https://github.com/markolofsen/django-revolution/issues)
- **Discussions**: [https://github.com/markolofsen/django-revolution/discussions](https://github.com/markolofsen/django-revolution/discussions)

## 📝 License

Non-Commercial License - see [LICENSE](LICENSE) file for details.

For commercial use, please contact Django-CFGAI Inc. at licensing@djangocfg.com

---

**Made with ❤️ by the [Django-CFGAI Team](https://djangocfg.com)**

**Django Revolution** - The **ONLY** tool that makes Django API client generation **truly automated** and **zone-aware**.
