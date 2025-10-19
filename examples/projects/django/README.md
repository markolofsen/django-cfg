# Django CFG Demo Project

A demonstration project for **django-cfg** - showcasing modern type-safe Django configuration using Pydantic v2 and YAML.

## What is this?

This is a **fully-functional example** of a crypto trading Django application that demonstrates:

- Type-safe configuration via Pydantic v2
- YAML-based environment settings
- Unfold Admin with custom navigation
- OpenAPI/Swagger documentation
- JWT authentication
- RPC over WebSocket (django-ipc)
- Payment integration (NowPayments)
- Dynamic settings (Constance)

## Quick Start

### 1. Install Dependencies

```bash
# Standard installation
make install

# Or with local django-cfg and django-ipc
make install-local
```

### 2. Setup Database

```bash
# Apply migrations
make migrate

# Or populate with sample data
make populate  # Clears DB and creates examples
```

### 3. Run

```bash
# Development server (automatically kills processes on port 8000)
make dev

# With ngrok tunnel
make dev-ngrok
```

Server will start at http://127.0.0.1:8000

## Main Commands

### Development

```bash
make dev           # Run development server
make dev-ngrok     # Run with ngrok tunnel
make kill-ports    # Kill processes on port 8000
make shell         # Django shell
make claude        # Start Claude Code
```

### Database

```bash
make migrate       # Apply all migrations
make populate      # Clear DB and populate with examples
```

### Configuration

```bash
make config        # Show current configuration
make check         # Django system checks
make check-settings # Check django-cfg settings
```

### URLs & Structure

```bash
make show-urls     # Show all URL patterns
make list-urls     # List URLs (Rich format)
make check-endpoints # Check API endpoints status
make tree          # Show project structure
```

### API

```bash
make api           # Generate OpenAPI clients
```

### Users

```bash
make superuser     # Create superuser
```

### Tasks (Dramatiq)

```bash
make tasks-status  # Task queue status
make tasks-worker  # Run Dramatiq worker
make tasks-clear   # Clear pending tasks
```

### Testing

```bash
make test          # Run tests
```

### Other

```bash
make manage CMD="command" # Run manage.py command
make commit        # git add + commit + push
```

## Key Files

```
api/
├── config.py              # Main config (DjangoConfig)
├── settings.py            # Auto-generated Django settings
├── urls.py                # URL routes
└── environment/
    ├── config.dev.yaml    # Development settings
    └── loader.py          # YAML config loader

apps/
├── profiles/              # User profiles
├── trading/               # Trading (Portfolio, Orders)
└── crypto/                # Crypto (Coins, Exchanges, Wallets)
```

## How It Works

### 1. YAML Configuration

`api/environment/config.dev.yaml`:
```yaml
env:
  env_mode: development

app:
  name: "Django CFG Demo"
  site_url: "http://localhost:8000"

database:
  url: "postgresql://user:pass@localhost/db"

payments_api_keys:
  nowpayments_api_key: "your-key"
```

### 2. Type-safe Config Class

`api/config.py`:
```python
from django_cfg import DjangoConfig

class DjangoCfgConfig(DjangoConfig):
    project_name: str = env.app.name
    debug: bool = env.debug
    secret_key: str = env.secret_key

    # All other settings...
```

### 3. Django Settings

`api/settings.py`:
```python
from api.config import config
locals().update(config.get_all_settings())
```

One line replaces hundreds of configuration lines!

## Admin Panel

- **URL**: http://127.0.0.1:8000/admin/
- **Theme**: Unfold (dark mode)
- **Navigation**: Auto-generated from config
- **Dashboard**: Custom metrics (users, orders, wallets, etc.)

## API Documentation

- **Swagger UI**: http://127.0.0.1:8000/api/schema/swagger-ui/
- **ReDoc**: http://127.0.0.1:8000/api/schema/redoc/
- **Health Check**: http://127.0.0.1:8000/cfg/health/

## Useful Links

- 📚 Django CFG Docs: https://djangocfg.com
- 🎨 Unfold Admin: https://unfoldadmin.com
- 🔌 DRF: https://www.django-rest-framework.org

## License

MIT
