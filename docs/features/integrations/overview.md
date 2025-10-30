---
title: Integrations Overview
description: Django-CFG integrations overview. Production-ready third-party integrations with built-in validation, type safety, and seamless Django integration.
sidebar_label: Overview
sidebar_position: 0
keywords:
  - django-cfg integrations
  - django third-party integrations
  - rearq integration
  - async task queue
  - ngrok integration
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# Integrations Overview

Django-CFG provides seamless integrations with essential third-party services and tools, making it easy to add powerful features to your Django application with minimal configuration.

## Available Integrations

<Tabs groupId="integration-categories">
  <TabItem value="tasks" label="🔄 Background Tasks" default>

### [ReArq Integration](./rearq/overview)

Production-ready async task queue with Redis and Tortoise ORM:

**Core Features:**
- ✅ **Async-first** architecture with native Python async/await
- ✅ **Redis-backed** queue with job persistence (PostgreSQL/MySQL/SQLite)
- ✅ **Type-safe** task definitions with Pydantic validation
- ✅ **Worker management** via CLI commands
- ✅ **Cron scheduling** with decorator-based configuration
- ✅ **Monitoring** with FastAPI server, Django REST API, and Admin interface
- ✅ **Retry logic** with exponential backoff and max attempts

**Use Cases:**
- Async email sending ([Email Module](/features/modules/email/overview))
- Payment processing ([Payment System](/features/built-in-apps/payments/overview))
- Document processing ([AI Knowledge Base](/features/built-in-apps/ai-knowledge/overview))
- Bulk operations (Newsletter campaigns, data imports)
- Scheduled tasks (cleanup jobs, report generation)

[**Full ReArq Guide →**](./rearq/overview)

  </TabItem>
  <TabItem value="development" label="🔧 Development Tools">

### [Ngrok Integration](./ngrok/overview)

Secure tunnels for webhook testing in development:

**Core Features:**
- ✅ **Automatic tunnel** creation with custom subdomains
- ✅ **HTTPS support** for secure webhook delivery
- ✅ **Custom domains** with ngrok auth token
- ✅ **Auto-configuration** of ALLOWED_HOSTS and CSRF settings
- ✅ **CLI integration** with `runserver_ngrok` command

**Use Cases:**
- Testing payment webhooks locally ([Payment System](/features/built-in-apps/payments/overview))
- OAuth callback testing ([Authentication](./auth))
- Third-party API webhooks
- Mobile app development

[**Full Ngrok Guide →**](./ngrok/overview)

  </TabItem>
  <TabItem value="auth" label="🔐 Authentication">

### [Authentication Patterns](./auth)

Enterprise authentication integration:

**Core Features:**
- ✅ **JWT authentication** with djangorestframework-simplejwt
- ✅ **OAuth2/OIDC** integration patterns
- ✅ **Multi-factor authentication** with OTP ([User Management](/features/built-in-apps/user-management/accounts))
- ✅ **Social auth** with django-allauth patterns
- ✅ **API key** authentication for machine-to-machine

**Use Cases:**
- REST API authentication
- SSO with OAuth2/OIDC providers
- Multi-factor authentication
- API key management

[**Full Auth Guide →**](./auth)

  </TabItem>
  <TabItem value="communication" label="📱 Communication">

### [Twilio Integration](./twilio)

SMS and voice communication integration:

**Core Features:**
- ✅ **SMS messaging** with Twilio API
- ✅ **Voice calls** and IVR integration
- ✅ **Number verification** via SMS
- ✅ **Webhook handling** for delivery status
- ✅ **Type-safe** configuration with Pydantic

**Alternatives:**
- **[Telegram Integration](/features/modules/telegram/overview)** - Bot-based notifications

**Use Cases:**
- SMS notifications and alerts
- Two-factor authentication
- Voice calls and IVR systems
- Phone number verification

[**Full Twilio Guide →**](./twilio)

  </TabItem>
  <TabItem value="patterns" label="📐 Best Practices">

### [Integration Patterns](./patterns)

Common patterns and best practices:

**Core Patterns:**
- ✅ **Webhook handling** patterns and security
- ✅ **API client** configuration and error handling
- ✅ **Rate limiting** and retry strategies
- ✅ **Secret management** with environment variables
- ✅ **Testing strategies** for third-party integrations

**Use Cases:**
- Building robust webhook handlers
- Implementing API rate limiting
- Managing third-party secrets
- Testing external integrations

[**Full Patterns Guide →**](./patterns)

  </TabItem>
</Tabs>

---

## Quick Start

### Enable ReArq for Background Tasks

```yaml
# config.dev.yaml
tasks:
  enabled: true
  redis_url: "redis://localhost:6379/0"
  db_url: "sqlite:///rearq.db"
```

```python
# tasks.py
from django_cfg.apps.tasks import task

@task()
async def send_welcome_email(user_id: int):
    """Task runs asynchronously in background."""
    # Async task code here
    pass
```

[**Full ReArq Guide →**](./rearq/overview)

### Enable Ngrok for Webhook Testing

```yaml
# config.dev.yaml
ngrok:
  enabled: true
  subdomain: "myapp"  # myapp.ngrok.io
  auth_token: "${NGROK_AUTH_TOKEN}"
```

```bash
# Start server with ngrok tunnel
python manage.py runserver_ngrok
```

[**Full Ngrok Guide →**](./ngrok/overview)

---

## Integration Architecture

### Type-Safe Configuration

All integrations use [Pydantic v2](/fundamentals/core/type-safety) for validation:

```python
from django_cfg import DjangoConfig
from django_cfg.models import RearqConfig, NgrokConfig

class MyConfig(DjangoConfig):
    # ReArq configuration
    tasks: RearqConfig | None = RearqConfig(
        enabled=True,
        redis_url="redis://localhost:6379/0",
        db_url="sqlite:///rearq.db"
    )

    # Ngrok configuration
    ngrok: NgrokConfig | None = NgrokConfig(
        enabled=True,
        subdomain="myapp"
    )
```

### Environment-Based Enablement

Enable integrations per environment using [environment detection](/fundamentals/configuration/environment):

```python
class MyConfig(DjangoConfig):
    @property
    def ngrok(self) -> NgrokConfig | None:
        # Only enable ngrok in development
        if self.is_development:
            return NgrokConfig(enabled=True)
        return None
```

### Automatic Django Integration

Integrations automatically configure Django settings:

- **ReArq**: Registers tasks app, configures Redis/DB connections, initializes workers
- **Ngrok**: Updates ALLOWED_HOSTS, CSRF_TRUSTED_ORIGINS, generates public URL
- **Auth**: Configures authentication backends, middleware, JWT settings

---

## Integration Comparison

| Integration | Type | Production Ready | Auto-Config | CLI Tools |
|-------------|------|------------------|-------------|-----------|
| **ReArq** | Async Task Queue | ✅ Yes | ✅ Yes | ✅ `rearq_worker`, `rearq_timer`, `rearq_server` |
| **Ngrok** | Development Tool | ⚠️ Dev Only | ✅ Yes | ✅ `runserver_ngrok` |
| **Auth** | Security | ✅ Yes | ✅ Yes | ✅ `test_auth` |
| **Twilio** | Communication | ✅ Yes | ✅ Yes | ✅ `test_sms` |

---

## Configuration Best Practices

### 1. Use Environment Variables for Secrets

```yaml
# config.prod.yaml
ngrok:
  auth_token: "${NGROK_AUTH_TOKEN}"  # From environment

twilio:
  account_sid: "${TWILIO_ACCOUNT_SID}"
  auth_token: "${TWILIO_AUTH_TOKEN}"
```

### 2. Disable in Production When Not Needed

```python
class ProductionConfig(DjangoConfig):
    # Ngrok only for development
    ngrok: None = None

    # ReArq for production background tasks
    tasks: RearqConfig = RearqConfig(
        enabled=True,
        redis_url="${REDIS_URL}",
        db_url="${DATABASE_URL}"
    )
```

### 3. Test Integrations Before Production

```bash
# Test ReArq workers
rearq main:rearq worker --test

# Test Twilio SMS
python manage.py test_sms +1234567890

# Test ngrok tunnel (dev only)
python manage.py runserver_ngrok --test
```

---

## See Also

### Core Integrations

**Background Processing:**
- **[ReArq Overview](./rearq/overview)** - Complete async task queue guide
- **[ReArq Configuration](./rearq/configuration)** - Setup and configuration
- **[ReArq Examples](./rearq/examples)** - Real-world task patterns
- **[ReArq Monitoring](./rearq/monitoring)** - Task monitoring and analytics
- **[ReArq Deployment](./rearq/deployment)** - Production deployment guide

**Development Tools:**
- **[Ngrok Overview](./ngrok/overview)** - Webhook testing guide
- **[Ngrok Configuration](./ngrok/configuration)** - Tunnel configuration

**Authentication:**
- **[Auth Patterns](./auth)** - Enterprise authentication
- **[User Management](/features/built-in-apps/user-management/accounts)** - Built-in user system

**Communication:**
- **[Twilio Integration](./twilio)** - SMS and voice
- **[Telegram Module](/features/modules/telegram/overview)** - Bot notifications
- **[Email Module](/features/modules/email/overview)** - Email sending

### Configuration & Setup

**Getting Started:**
- **[Configuration Guide](/getting-started/configuration)** - Enable integrations
- **[Configuration Models](/fundamentals/configuration)** - Integration config API
- **[Environment Detection](/fundamentals/configuration/environment)** - Environment-specific integrations

**Infrastructure:**
- **[Redis Configuration](/fundamentals/configuration/cache)** - Redis setup for ReArq
- **[Security Settings](/fundamentals/configuration/security)** - Webhook signature verification
- **[Environment Variables](/fundamentals/configuration/environment)** - Manage API keys securely

### Related Features

**Apps Using Integrations:**
- **[Payment System](/features/built-in-apps/payments/overview)** - Uses ReArq for async processing
- **[AI Knowledge Base](/features/built-in-apps/ai-knowledge/overview)** - Uses ReArq for document processing
- **[Newsletter](/features/built-in-apps/user-management/newsletter)** - Uses ReArq for bulk emails

**Other Modules:**
- **[Modules Overview](/features/modules/overview)** - All available modules
- **[LLM Module](/features/modules/llm/overview)** - AI model integration

### Tools & Guides

**CLI Commands:**
- **[CLI Introduction](/cli/introduction)** - All CLI tools

**Guides:**
- **[Integration Patterns](./patterns)** - Best practices
- **[Production Config](/guides/production-config)** - Production integration setup
- **[Troubleshooting](/guides/troubleshooting)** - Common integration issues

---

## Next Steps

**New to Integrations?**
1. Start with [ReArq Overview](./rearq/overview) for async background tasks
2. Try [Ngrok Overview](./ngrok/overview) for webhook testing
3. Review [Integration Patterns](./patterns) for best practices

**Ready for Production?**
1. Review [Production Config](/guides/production-config)
2. Set up [Redis](/fundamentals/configuration/cache) for ReArq
3. Configure [environment variables](/fundamentals/configuration/environment) for secrets
4. Deploy ReArq workers using [ReArq Deployment](./rearq/deployment) guide

**Need Help?**
- [Troubleshooting Guide](/guides/troubleshooting)
- [FAQ](/guides/faq)
- [CLI Commands](/cli/introduction)

---

Django-CFG integrations: **Production-ready, type-safe, zero-config.** 🚀
