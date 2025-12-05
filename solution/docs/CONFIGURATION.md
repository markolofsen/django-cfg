# Configuration Guide

Django-CFG uses Pydantic v2 for type-safe configuration.

## Configuration Files

| File | Description |
|------|-------------|
| `api/environment/.env` | Environment variables (development) |
| `api/environment/.env.prod` | Production overrides |
| `api/environment/.env.secrets` | Secrets (never commit!) |
| `api/environment/loader.py` | Pydantic settings definitions |
| `api/config.py` | Django-CFG configuration class |

## Environment Loading Priority

1. **Environment variables** (highest priority)
2. `.env.secrets` (if exists)
3. `.env.prod` (if `IS_PROD=true`)
4. `.env` (base configuration)
5. **Default values** (lowest priority)

## Environment Variables

### Database

```env
# PostgreSQL (recommended)
DATABASE__URL=postgresql://user:password@localhost:5432/dbname

# SQLite (development only)
DATABASE__URL=sqlite:///db/default.sqlite3

# MySQL
DATABASE__URL=mysql://user:password@localhost:3306/dbname
```

### Security

```env
SECRET_KEY=your-secret-key-at-least-32-characters-long
DEBUG=true
IS_DEV=true
```

### Email

```env
EMAIL__BACKEND=console    # console (dev) or smtp (prod)
EMAIL__HOST=smtp.example.com
EMAIL__PORT=587
EMAIL__USERNAME=user@example.com
EMAIL__PASSWORD=password
EMAIL__USE_TLS=true
EMAIL__DEFAULT_FROM=noreply@example.com
```

### Redis (Cache & Tasks)

```env
REDIS_URL=redis://localhost:6379/0
```

### AI API Keys

```env
API_KEYS__OPENAI=sk-xxx
API_KEYS__OPENROUTER=sk-or-xxx
```

### Payments

```env
PAYMENTS_API_KEYS__NOWPAYMENTS_API_KEY=xxx
PAYMENTS_API_KEYS__NOWPAYMENTS_IPN_SECRET=xxx
PAYMENTS_API_KEYS__NOWPAYMENTS_SANDBOX_MODE=true
```

### Telegram Notifications

```env
TELEGRAM__BOT_TOKEN=123456:ABC-xxx
TELEGRAM__CHAT_ID=123456789
```

### GitHub OAuth

```env
GITHUB_OAUTH__CLIENT_ID=xxx
GITHUB_OAUTH__CLIENT_SECRET=xxx
```

### Centrifugo (WebSocket)

```env
CENTRIFUGO__ENABLED=true
CENTRIFUGO__CENTRIFUGO_URL=ws://localhost:8120/connection/websocket
CENTRIFUGO__CENTRIFUGO_API_URL=http://localhost:8120/api
CENTRIFUGO__CENTRIFUGO_API_KEY=your-api-key
CENTRIFUGO__CENTRIFUGO_TOKEN_HMAC_SECRET=your-hmac-secret
```

## Configuration Class (api/config.py)

The main configuration class extends `DjangoConfig`:

```python
from django_cfg import DjangoConfig, DatabaseConfig
from .environment import env

class DjangoCfgConfig(DjangoConfig):
    # Project info
    project_name: str = env.app.name
    secret_key: str = env.secret_key
    debug: bool = env.debug

    # URLs
    site_url: str = env.app.site_url
    api_url: str = env.app.api_url

    # Database
    databases: Dict[str, DatabaseConfig] = {
        "default": DatabaseConfig.from_url(url=env.database.url)
    }

    # Features (enable/disable)
    enable_support: bool = True
    enable_accounts: bool = True
    enable_newsletter: bool = True
    enable_payments: bool = True
    # ... more features
```

## Production Configuration

Create `.env.prod` for production overrides:

```env
DEBUG=false
IS_PROD=true

# Use stronger security
SECRET_KEY=production-secret-key-very-long-and-random

# Real email
EMAIL__BACKEND=smtp
EMAIL__HOST=smtp.sendgrid.net
```

## Secrets Management

Create `.env.secrets` for sensitive data (add to `.gitignore`!):

```env
# API keys
API_KEYS__OPENAI=sk-real-key
PAYMENTS_API_KEYS__NOWPAYMENTS_API_KEY=real-key

# Database credentials
DATABASE__URL=postgresql://prod_user:real_password@db.example.com:5432/prod_db
```

## Validation

Check your configuration:

```bash
poetry run python manage.py check
poetry run python manage.py validate_config
```

## More Information

Full documentation: https://djangocfg.com/docs/getting-started/configuration
