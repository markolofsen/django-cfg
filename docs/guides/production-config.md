---
title: Production Configuration
description: Django-CFG production config guide. Practical tutorial for production configuration with real-world examples, troubleshooting tips, and production patterns.
sidebar_label: Production Config
sidebar_position: 4
keywords:
  - django-cfg production config
  - django-cfg guide production config
  - how to production config django
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# Production Configuration

Production-ready Django-CFG configuration demonstrating all features, security best practices, and real-world patterns.

:::danger[Security First]
Production configuration requires careful attention to **secrets management**, **SSL/TLS**, and **security headers**. Never commit secrets to version control.
:::

## Minimal Production Setup

:::danger[Production Deployment Checklist]
**CRITICAL: Before deploying to production, verify ALL of these:**
- 🔒 **DEBUG = False** - Never run with DEBUG=True in production
- 🔒 **Strong SECRET_KEY** - At least 50 random characters
- 🔒 **Reverse proxy SSL** - nginx/Cloudflare handles HTTPS
- 🔒 **Secrets from environment** - No hardcoded credentials
- 🔒 **Database SSL** - Encrypted database connections
- 🔒 **security_domains set** - Production domains configured
- 🔒 **Static files collected** - Run collectstatic before deploy
:::

:::tip[Start Simple]
Start with minimal configuration and add features as needed. This prevents configuration bloat and reduces attack surface.
:::

<Tabs>
  <TabItem value="minimal" label="Minimal Config" default>

```python title="config.py"
from django_cfg import DjangoConfig, DatabaseConfig
from .environment import env

class ProductionConfig(DjangoConfig):
    # Project basics
    project_name: str = env.app.name
    project_version: str = env.app.version

    # Security
    secret_key: str = env.secret_key
    debug: bool = False
    # ssl_redirect: Optional - not specified (defaults to None)
    # Assumes reverse proxy (nginx/Cloudflare) handles SSL
    security_domains: list[str] = env.security.domains

    # Database from environment
    databases: dict[str, DatabaseConfig] = {
        "default": DatabaseConfig.from_url(url=env.database.url)
    }

config = ProductionConfig()
```

  </TabItem>
  <TabItem value="yaml" label="Environment YAML">

```yaml title="config.prod.yaml"
secret_key: "${SECRET_KEY}"  # From environment variable
debug: false

app:
  name: "My Production App"
  version: "1.0.0"

# Security domains - flexible format (Django-CFG auto-normalizes)
security:
  domains:
    - "myapp.com"              # ✅ No protocol
    - "https://api.myapp.com"  # ✅ With protocol
    - "admin.myapp.com:8443"   # ✅ With port

database:
  url: "${DATABASE_URL}"  # From environment variable
```

:::warning[Environment Variables]
Always use environment variables for secrets in production. Never hardcode sensitive values in YAML files.
:::

  </TabItem>
</Tabs>

## Complete Production Configuration

:::warning[Configuration Complexity]
This complete example shows **all available features**. For most production deployments, start with the minimal setup above and add features incrementally as needed. Unnecessary features increase attack surface and maintenance burden.
:::

```python
# config.py
from typing import Optional
from django_cfg import (
    DjangoConfig,
    DatabaseConfig,
    CacheConfig,
    EmailConfig,
    TwilioConfig,
    TaskConfig,
    UnfoldConfig,
    SpectacularConfig,
)
from .environment import env


class MyProductionConfig(DjangoConfig):
    """
    Production configuration with all Django-CFG features.

    Environment-aware, type-safe, and production-ready.
    """

    # === Project Metadata ===
    project_name: str = env.app.name
    project_version: str = env.app.version or "1.0.0"
    project_description: str = env.app.description or ""

    # === Security Settings ===
    secret_key: str = env.secret_key
    debug: bool = env.debug
    # ssl_redirect: Optional - not specified (reverse proxy handles SSL)
    security_domains: list[str] = env.security.domains

    # === Built-in Applications ===
    # User management
    enable_accounts: bool = True
    enable_support: bool = True
    enable_newsletter: bool = env.features.marketing
    enable_leads: bool = env.features.marketing

    # AI features (optional)
    enable_knowbase: bool = env.features.ai
    enable_agents: bool = env.features.ai

    # Maintenance
    enable_maintenance: bool = True

    # === Custom Applications ===
    project_apps: list[str] = [
        "core",
        "apps.users",
        "apps.api",
        # Add your apps here
    ]

    # === Database Configuration ===
    databases: dict[str, DatabaseConfig] = {
        # Primary database
        "default": DatabaseConfig.from_url(
            url=env.database.url,
            sslmode="require" if env.is_production else "prefer",
            connect_timeout=10,
        ),
    }

    # === Cache Configuration ===
    # ✨ AUTO-MAGIC: Just set redis_url - cache auto-created!
    redis_url: Optional[str] = env.redis.url
    # Django-CFG automatically creates CacheConfig with:
    # - timeout=300 (5 minutes)
    # - key_prefix=project_name.lower()
    # - max_connections=50
    # Override with explicit cache_default if needed

    # === Email Configuration ===
    email: Optional[EmailConfig] = (
        EmailConfig(
            backend="django.core.mail.backends.smtp.EmailBackend",
            host=env.email.host,
            port=env.email.port,
            user=env.email.user,
            password=env.email.password,
            use_tls=True,
            from_email=env.email.from_email,
        )
        if env.email.enabled
        else None
    )

    # === SMS/OTP Configuration ===
    telegram: Optional[TelegramConfig] = (
        TelegramConfig(
            bot_token=env.telegram.bot_token,
            chat_id=env.telegram.chat_id,
        )
        if env.telegram.enabled
        else None
    )

    # === Background Tasks ===
    tasks: Optional[TaskConfig] = (
        TaskConfig(
            redis_url=env.redis.url,
            processes=env.tasks.processes or 4,
            threads=env.tasks.threads or 8,
            queues=env.tasks.queues or ["default", "high", "low"],
            max_retries=3,
        )
        if env.redis.url
        else None
    )

    # === Admin Interface ===
    unfold: Optional[UnfoldConfig] = UnfoldConfig(
        site_title=f"{env.app.name} Admin",
        site_header=f"{env.app.name} Administration",
        dashboard_enabled=True,
        show_search=True,
    )

    # === API Documentation ===
    spectacular: Optional[SpectacularConfig] = SpectacularConfig(
        title=f"{env.app.name} API",
        description=env.app.description or "API Documentation",
        version=env.app.version or "1.0.0",
    )

    # === API Keys (from environment) ===
    api_keys: dict[str, str] = {
        "service_a": env.api_keys.service_a or "",
        "service_b": env.api_keys.service_b or "",
        # Add your API keys here
    }


# Create and set configuration
config = MyProductionConfig()
```

## Environment Configuration

:::danger[NEVER Commit .env Files]
**Critical security rule:** Environment files contain production secrets and MUST NEVER be committed to version control.

**Add to .gitignore:**
```gitignore
# Environment files
.env
.env.*
env.production
config.prod.yaml
*.secret.yaml

# But keep examples
!.env.example
!config.example.yaml
```

**Instead:**
- ✅ Use `.env.example` with placeholder values
- ✅ Document required variables in README
- ✅ Use secret management systems (AWS Secrets Manager, HashiCorp Vault)
- ✅ Set environment variables in deployment platform
:::

```yaml
# environment/config.yaml
app:
  name: "My Application"
  slug: "myapp"
  version: "1.0.0"
  description: "Production application"

secret_key: "${SECRET_KEY}"
debug: false

# ssl_redirect: Optional - not needed (reverse proxy handles SSL)

security:
  domains:
    - "example.com"
    - "www.example.com"

database:
  url: "${DATABASE_URL}"

redis:
  url: "${REDIS_URL}"

email:
  enabled: true
  host: "smtp.example.com"
  port: 587
  user: "${EMAIL_USER}"
  password: "${EMAIL_PASSWORD}"
  from_email: "noreply@example.com"

telegram:
  enabled: false
  bot_token: "${TELEGRAM_BOT_TOKEN}"
  chat_id: "${TELEGRAM_CHAT_ID}"

features:
  marketing: true  # Enable leads & newsletter
  ai: false        # Disable AI features in production

tasks:
  processes: 4
  threads: 8
  queues:
    - default
    - high
    - low
    - emails
    - reports

api_keys:
  service_a: "${SERVICE_A_API_KEY}"
  service_b: "${SERVICE_B_API_KEY}"
```

## Multi-Environment Setup

:::info[Environment Strategy]
Use separate configuration classes for each environment to ensure proper isolation and prevent production mistakes.
:::

<Tabs>
  <TabItem value="development" label="Development" default>

```python title="config.py"
class DevelopmentConfig(DjangoConfig):
    debug: bool = True
    # security_domains: Optional - not needed in development
    # Django-CFG auto-configures CORS fully open

    # All features enabled for development
    enable_accounts: bool = True
    enable_support: bool = True
    enable_newsletter: bool = True
    enable_leads: bool = True
    enable_knowbase: bool = True
    enable_agents: bool = True

    # SQLite for development
    databases: dict[str, DatabaseConfig] = {
        "default": DatabaseConfig.from_url("sqlite:///dev.db")
    }
```

:::danger[DEBUG=True is DANGEROUS in Production]
**Never run with DEBUG=True in production. It exposes:**
- 🔓 **Full stack traces** - Reveals source code paths and logic
- 🔓 **Environment variables** - Shows SECRET_KEY and credentials
- 🔓 **SQL queries** - Exposes database structure and data
- 🔓 **Internal paths** - File system layout and dependencies
- 🔓 **Library versions** - Makes exploit targeting easier

**Performance impact:**
- Templates not cached - Every request recompiles
- Static files served by Django - Slow, not production-ready
- Query logging enabled - Memory leaks over time
:::

:::tip[Development Benefits]
Development environment enables all features for testing, uses SQLite for simplicity, and disables SSL redirect for local testing.
:::

  </TabItem>
  <TabItem value="staging" label="Staging">

```python title="config.py"
class StagingConfig(DjangoConfig):
    debug: bool = False
    security_domains: list[str] = ["staging.myapp.com"]

    # Essential apps only
    enable_accounts: bool = True
    enable_support: bool = True

    # PostgreSQL from environment
    databases: dict[str, DatabaseConfig] = {
        "default": DatabaseConfig.from_url(env.database.url)
    }
```

:::note[Staging Purpose]
Staging mirrors production settings but with reduced feature set for focused testing before production deployment.
:::

  </TabItem>
  <TabItem value="production" label="Production">

```python title="config.py"
class ProductionConfig(DjangoConfig):
    debug: bool = False
    security_domains: list[str] = env.security.domains

    # Production apps
    enable_accounts: bool = True
    enable_support: bool = True
    enable_maintenance: bool = True

    # Conditional features
    enable_newsletter: bool = env.features.marketing
    enable_leads: bool = env.features.marketing
    enable_knowbase: bool = env.features.ai

    # Production database with replicas
    databases: dict[str, DatabaseConfig] = {
        "default": DatabaseConfig.from_url(
            env.database.url,
            sslmode="require",
            operations=["write", "migrate"],
        ),
        "read_replica": DatabaseConfig.from_url(
            env.database.replica_url,
            operations=["read"],
            migrate_to="default",
        ),
    }
```

:::danger[Production Deployment Checklist]
**Before deploying ProductionConfig, verify:**
- ✅ `debug = False` always
- ✅ `security_domains` configured with production domains
- ✅ Reverse proxy (nginx/Cloudflare) handles SSL/TLS
- ✅ SSL required for databases (`sslmode=require`)
- ✅ Read replicas configured for scalability
- ✅ Feature flags from environment (not hardcoded)
- ✅ **Static files collected**: `python manage.py collectstatic --noinput`
- ✅ **Migrations applied**: `python manage.py migrate --noinput`
- ✅ **Health check working**: `/health/` returns 200 OK
- ✅ **Logs configured**: Check application writes to production logs
- ✅ **Secrets validated**: All required environment variables set
:::

  </TabItem>
</Tabs>

## Configuration Selection

:::danger[Wrong Environment = Production Disaster]
**Loading the wrong configuration can cause catastrophic failures:**
- ❌ Development config in production → Exposed debug info, disabled security
- ❌ Production config in development → Data corruption in wrong database
- ❌ Missing environment variable → Application crash on startup

**Always validate environment selection:**
```python
# Fail fast if environment is wrong
if env.environment not in CONFIG_MAP:
    raise ValueError(f"Invalid environment: {env.environment}")

# Validate production safeguards
if env.environment == "production" and config.debug:
    raise ValueError("DEBUG cannot be True in production!")
```
:::

```python
# config.py
from django_cfg import DjangoConfig
from .environment import env

# Define all configurations
class DevelopmentConfig(DjangoConfig):
    ...

class StagingConfig(DjangoConfig):
    ...

class ProductionConfig(DjangoConfig):
    ...

# Select configuration based on environment
CONFIG_MAP = {
    "development": DevelopmentConfig,
    "staging": StagingConfig,
    "production": ProductionConfig,
}

# Validate environment
if env.environment not in CONFIG_MAP:
    raise ValueError(
        f"Invalid environment '{env.environment}'. "
        f"Must be one of: {list(CONFIG_MAP.keys())}"
    )

config = CONFIG_MAP[env.environment]()

# Final production validation
if env.environment == "production":
    if config.debug:
        raise ValueError("CRITICAL: DEBUG=True in production!")
    if len(config.secret_key) < 50:
        raise ValueError("CRITICAL: SECRET_KEY too short for production!")
    if not config.security_domains:
        raise ValueError("CRITICAL: security_domains not configured!")
```

## Security Best Practices

:::danger[Critical Security Requirements]
Production applications **must** implement all security best practices below. Skipping any of these increases vulnerability to attacks.
:::

### 1. Secret Management

<Tabs>
  <TabItem value="validation" label="Validate Secrets" default>

```python
import os
from django_cfg import DjangoConfig

class SecureConfig(DjangoConfig):
    # Fail fast if missing
    secret_key: str = os.environ["SECRET_KEY"]

    # Validate at startup
    def __post_init__(self):
        if len(self.secret_key) < 50:
            raise ValueError("SECRET_KEY too short")
        if self.debug and "production" in self.environment:
            raise ValueError("DEBUG cannot be True in production")
```

:::warning[Secret Key Length]
Django's `SECRET_KEY` must be at least **50 characters** long and cryptographically random. Use `django.core.management.utils.get_random_secret_key()` to generate.
:::

  </TabItem>
  <TabItem value="storage" label="Secret Storage">

**✅ Recommended:**
```bash
# Environment variables
export SECRET_KEY="your-secret-key-here"
export DATABASE_URL="postgresql://..."
```

**❌ Never do this:**
```yaml
# DON'T hardcode secrets in YAML
secret_key: "my-secret-key-123"  # ❌ WRONG
database_password: "admin123"     # ❌ WRONG
```

:::danger[Secret Leaks]
Hardcoded secrets in files can be leaked through:
- Git history (even after deletion)
- Log files
- Error messages
- Backup systems
:::

  </TabItem>
  <TabItem value="rotation" label="Secret Rotation">

```python
# Implement secret rotation
class SecureConfig(DjangoConfig):
    secret_key: str = os.environ["SECRET_KEY"]

    # Optional: Support multiple keys for rotation
    old_secret_keys: list[str] = [
        os.environ.get("OLD_SECRET_KEY_1", ""),
        os.environ.get("OLD_SECRET_KEY_2", ""),
    ]
```

:::tip[Rotation Strategy]
Rotate secrets regularly (every 90 days) and keep old keys temporarily to avoid session invalidation.
:::

  </TabItem>
</Tabs>

### 2. Database Security

:::warning[SSL Required]
**Always** use SSL/TLS for database connections in production. Unencrypted connections expose credentials and data.
:::

<Tabs>
  <TabItem value="ssl" label="SSL Configuration" default>

```python
databases: dict[str, DatabaseConfig] = {
    "default": DatabaseConfig(
        sslmode="require",  # Force SSL
        connect_timeout=10,  # Timeout protection
        options={
            "options": "-c statement_timeout=30000",  # 30s query timeout
        },
    )
}
```

  </TabItem>
  <TabItem value="credentials" label="Credential Management">

```python
# Use DATABASE_URL from environment
databases: dict[str, DatabaseConfig] = {
    "default": DatabaseConfig.from_url(
        url=os.environ["DATABASE_URL"],
        sslmode="require",
    )
}
```

:::danger[Connection Strings]
Never log database URLs - they contain credentials. Ensure logging filters strip passwords.
:::

  </TabItem>
</Tabs>

### 3. CORS & Security Headers

:::info[Security Headers]
Django-CFG automatically configures security headers when `security_domains` is set. Manual configuration rarely needed.
:::

```python
class SecureConfig(DjangoConfig):
    security_domains: list[str] = [
        "myapp.com",              # ✅ Flexible format
        "https://api.myapp.com",  # ✅ With protocol
        "www.myapp.com:8443",     # ✅ With port
    ]
    # ssl_redirect: Optional - not needed (reverse proxy handles SSL)
    cors_allow_headers: list[str] = [
        "accept",
        "content-type",
        "authorization",
    ]
```

<details>
  <summary>Auto-configured Security Headers</summary>

When `security_domains` is set, Django-CFG automatically enables:

- `SECURE_SSL_REDIRECT = False` - Reverse proxy handles redirects
- `SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')` - Trust proxy
- `SECURE_HSTS_SECONDS = 31536000` - Force HTTPS for 1 year
- `SECURE_HSTS_INCLUDE_SUBDOMAINS = True` - Apply to subdomains
- `SECURE_CONTENT_TYPE_NOSNIFF = True` - Prevent MIME sniffing
- `X_FRAME_OPTIONS = "DENY"` - Prevent clickjacking
- `SECURE_BROWSER_XSS_FILTER = True` - Enable XSS protection

</details>

## Performance Optimization

:::tip[Performance Best Practices]
Proper configuration of database pooling, caching, and task queues is critical for production performance at scale.
:::

<Tabs>
  <TabItem value="database" label="Database Pooling" default>

```python title="config.py"
databases: dict[str, DatabaseConfig] = {
    "default": DatabaseConfig(
        options={
            "MAX_CONNS": 20,  # Maximum connections
            "MIN_CONNS": 5,   # Minimum idle connections
        },
        connect_timeout=10,  # Connection timeout
    )
}
```

:::info[Connection Pool Sizing]
**Rule of thumb:** `MAX_CONNS = (CPU cores × 2) + effective spindle count`

For cloud databases, limit connections to avoid quota exhaustion.
:::

  </TabItem>
  <TabItem value="cache" label="Cache Configuration">

```python title="config.py"
cache_default: CacheConfig = CacheConfig(
    redis_url=env.redis.url,
    timeout=300,  # 5 minutes default
    key_prefix="myapp",
    options={
        "CONNECTION_POOL_KWARGS": {
            "max_connections": 50,
        },
    },
)
```

:::note[Cache Strategy]
- **Short TTL (1-5 min):** Dynamic content, user sessions
- **Medium TTL (5-60 min):** API responses, computed data
- **Long TTL (1+ hours):** Static content, reference data
:::

  </TabItem>
  <TabItem value="tasks" label="Task Queues">

```python title="config.py"
tasks: TaskConfig = TaskConfig(
    redis_url=env.redis.url,
    processes=6,  # CPU cores
    threads=8,    # I/O-bound tasks
    queues=["default", "high", "low", "emails", "reports"],
    max_retries=3,
)
```

:::tip[Queue Design]
Separate queues by priority and characteristics:
- **high:** Critical tasks (payments, notifications)
- **default:** Regular background tasks
- **low:** Bulk operations, cleanup
- **emails:** Email sending (dedicated workers)
:::

  </TabItem>
</Tabs>

<details>
  <summary>Advanced Performance Tuning</summary>

### Read Replicas
```python
databases: dict[str, DatabaseConfig] = {
    "default": DatabaseConfig.from_url(
        env.database.url,
        operations=["write", "migrate"],
    ),
    "read_replica_1": DatabaseConfig.from_url(
        env.database.replica_1_url,
        operations=["read"],
    ),
    "read_replica_2": DatabaseConfig.from_url(
        env.database.replica_2_url,
        operations=["read"],
    ),
}
```

### Cache Layering
```python
# Multiple cache backends
CACHES = {
    "default": {  # Redis for session/general
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": env.redis.url,
    },
    "local": {  # Local memory for hot data
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "unique-snowflake",
    },
}
```

</details>

## Monitoring & Logging

:::info[Production Observability]
Production systems require comprehensive logging, monitoring, and alerting to ensure reliability and quick incident response.
:::

<Tabs>
  <TabItem value="logging" label="Logging Configuration" default>

```python title="config.py"
class MonitoredConfig(DjangoConfig):
    # Startup information
    startup_info_mode: str = "SHORT"  # Minimal logs in production

    # Telegram notifications
    telegram: TelegramConfig = TelegramConfig(
        bot_token=env.telegram.bot_token,
        chat_id=env.telegram.admin_chat,
    )

    # Custom logging
    @property
    def logging(self) -> dict:
        return {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "verbose": {
                    "format": "{levelname} {asctime} {module} {message}",
                    "style": "{",
                },
            },
            "handlers": {
                "file": {
                    "class": "logging.handlers.RotatingFileHandler",
                    "filename": "/var/log/myapp/django.log",
                    "maxBytes": 10485760,  # 10MB
                    "backupCount": 5,
                    "formatter": "verbose",
                },
                "telegram": {
                    "class": "myapp.logging.TelegramHandler",
                    "bot_token": self.telegram.bot_token,
                    "chat_id": self.telegram.chat_id,
                    "level": "ERROR",  # Only errors to Telegram
                },
            },
            "loggers": {
                "django": {
                    "handlers": ["file", "telegram"],
                    "level": "INFO",
                },
                "django.request": {
                    "handlers": ["file", "telegram"],
                    "level": "ERROR",
                    "propagate": False,
                },
            },
        }
```

:::warning[Log Rotation]
Always use **RotatingFileHandler** or **TimedRotatingFileHandler** in production to prevent disk space exhaustion.
:::

  </TabItem>
  <TabItem value="monitoring" label="Health Monitoring">

```python title="views.py"
from django.http import JsonResponse
from django.db import connection
from django.core.cache import cache

def health_check(request):
    """Production health check endpoint."""
    health = {
        "status": "healthy",
        "database": False,
        "cache": False,
        "version": settings.PROJECT_VERSION,
    }

    # Check database
    try:
        connection.ensure_connection()
        health["database"] = True
    except Exception as e:
        health["status"] = "unhealthy"
        health["database_error"] = str(e)

    # Check cache
    try:
        cache.set("health_check", "ok", 1)
        health["cache"] = cache.get("health_check") == "ok"
    except Exception as e:
        health["status"] = "unhealthy"
        health["cache_error"] = str(e)

    status = 200 if health["status"] == "healthy" else 503
    return JsonResponse(health, status=status)
```

:::tip[Health Check Endpoint]
Expose `/health/` endpoint for monitoring systems (Kubernetes, AWS ELB, etc.). Return HTTP 503 for unhealthy state.
:::

  </TabItem>
  <TabItem value="alerts" label="Alert Configuration">

```python title="config.py"
# Configure Telegram alerts for critical errors
telegram: TelegramConfig = TelegramConfig(
    bot_token=env.telegram.bot_token,
    chat_id=env.telegram.admin_chat,
)

# Custom logging handler for Telegram alerts
class TelegramHandler(logging.Handler):
    """Send critical errors to Telegram."""

    def __init__(self, bot_token: str, chat_id: str):
        super().__init__()
        self.bot_token = bot_token
        self.chat_id = chat_id

    def emit(self, record):
        """Send log record to Telegram."""
        message = self.format(record)
        # Send via Telegram API
        send_telegram_message(
            bot_token=self.bot_token,
            chat_id=self.chat_id,
            message=f"🚨 Production Error:\n{message}",
        )
```

:::note[Alert Channels]
Common alert channels for production:
- **Telegram:** Real-time notifications
- **Email:** Detailed error reports
- **Slack:** Team collaboration
- **PagerDuty:** On-call rotation
:::

  </TabItem>
</Tabs>

## See Also

### Deployment & Production

**Production Setup:**
- **[Docker Deployment](/guides/docker/production)** - Containerized production deployment
- **[Multi-Database Setup](./multi-database)** - Advanced database configuration
- **[Logging Configuration](/deployment/logging)** - Structured logging setup
- **[Health Monitoring](/features/modules/health/overview)** - System health checks

**Configuration:**
- **[Configuration Guide](/getting-started/configuration)** - YAML configuration setup
- **[Configuration Models](/fundamentals/configuration)** - Complete config API
- **[Environment Detection](/fundamentals/configuration/environment)** - Auto-detect environments
- **[Environment Variables](/fundamentals/configuration/environment)** - Secure credential management

### Security & Performance

**Security:**
- **[Security Settings](/fundamentals/configuration/security)** - CORS, CSRF, SSL/TLS hardening
- **[Type-Safe Configuration](/fundamentals/core/type-safety)** - Pydantic validation

**Performance:**
- **[Cache Configuration](/fundamentals/configuration/cache)** - Redis, Memcached setup
- **[Background Tasks](/features/integrations/django-rq/overview)** - Async processing
- **[Database Optimization](/fundamentals/database)** - Connection pooling, read replicas

### Features & Integration

**Built-in Features:**
- **[Built-in Apps Overview](/features/built-in-apps/overview)** - Production-ready apps
- **[Payment System](/features/built-in-apps/payments/overview)** - Payment processing
- **[AI Agents](/ai-agents/ai-django-development-framework)** - AI workflow automation

**Integration:**
- **[API Generation](/features/api-generation/overview)** - Auto-generate API clients
- **[Webhook Testing](/features/integrations/ngrok/overview)** - Test webhooks with ngrok

### Tools & Support

**CLI Tools:**
- **[CLI Introduction](/cli/introduction)** - Command-line tools
- **[Core Commands](/cli/commands/core-commands)** - Validation and deployment commands

**Support:**
- **[Troubleshooting](/guides/troubleshooting)** - Common production issues
- **[Migration Guide](/guides/migration-guide)** - Migrate to production
- **[FAQ](/guides/faq)** - Frequently asked questions

**Note:** All examples use YAML-based configuration. See [Configuration Guide](/getting-started/configuration) for complete setup.
