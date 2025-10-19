---
title: Integrations Overview
description: Django-CFG integrations overview. Production-ready third-party integrations with built-in validation, type safety, and seamless Django integration.
sidebar_label: Overview
sidebar_position: 0
keywords:
  - django-cfg integrations
  - django third-party integrations
  - dramatiq integration
  - ngrok integration
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# Integrations Overview

Django-CFG provides seamless integrations with essential third-party services and tools, making it easy to add powerful features to your Django application with minimal configuration.

## Available Integrations

<Tabs groupId="integration-categories">
  <TabItem value="tasks" label="🔄 Background Tasks" default>

### [Dramatiq Integration](./dramatiq/overview)

Production-ready background task processing with Redis:

**Core Features:**
- ✅ **Redis-backed** message broker with automatic configuration
- ✅ **Type-safe** task definitions with Pydantic validation
- ✅ **Worker management** via CLI commands
- ✅ **Monitoring** with built-in metrics and dashboards
- ✅ **Error handling** with automatic retries and dead letter queues

**Use Cases:**
- Async email sending ([Email Module](/features/modules/email/overview))
- Payment processing ([Payment System](/features/built-in-apps/payments/overview))
- Document processing ([AI Knowledge Base](/features/built-in-apps/ai-knowledge/overview))
- Bulk operations (Newsletter campaigns, data imports)

[**Full Dramatiq Guide →**](./dramatiq/overview)

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

### Enable Dramatiq for Background Tasks

```yaml
# config.dev.yaml
dramatiq:
  enabled: true
  broker: "redis://localhost:6379/0"
  result_backend: "redis://localhost:6379/1"
```

```python
# tasks.py
import dramatiq

@dramatiq.actor
def send_welcome_email(user_id: int):
    # Task runs in background
    pass
```

[**Full Dramatiq Guide →**](./dramatiq/overview)

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
from django_cfg.models import DramatiqConfig, NgrokConfig

class MyConfig(DjangoConfig):
    # Dramatiq configuration
    dramatiq: DramatiqConfig | None = DramatiqConfig(
        enabled=True,
        broker="redis://localhost:6379/0"
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

- **Dramatiq**: Adds middleware, configures broker, sets up workers
- **Ngrok**: Updates ALLOWED_HOSTS, CSRF_TRUSTED_ORIGINS, generates public URL
- **Auth**: Configures authentication backends, middleware, JWT settings

---

## Integration Comparison

| Integration | Type | Production Ready | Auto-Config | CLI Tools |
|-------------|------|------------------|-------------|-----------|
| **Dramatiq** | Background Tasks | ✅ Yes | ✅ Yes | ✅ `rundramatiq` |
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

    # Dramatiq for production background tasks
    dramatiq: DramatiqConfig = DramatiqConfig(
        enabled=True,
        broker="${REDIS_URL}"
    )
```

### 3. Test Integrations Before Production

```bash
# Test Dramatiq workers
python manage.py test_dramatiq

# Test Twilio SMS
python manage.py test_sms +1234567890

# Test ngrok tunnel (dev only)
python manage.py runserver_ngrok --test
```

---

## See Also

### Core Integrations

**Background Processing:**
- **[Dramatiq Overview](./dramatiq/overview)** - Complete background task guide
- **[Dramatiq Configuration](./dramatiq/configuration)** - Setup and configuration
- **[Dramatiq Examples](./dramatiq/examples)** - Real-world task patterns

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
- **[Redis Configuration](/fundamentals/configuration/cache)** - Redis setup for Dramatiq
- **[Security Settings](/fundamentals/configuration/security)** - Webhook signature verification
- **[Environment Variables](/fundamentals/configuration/environment)** - Manage API keys securely

### Related Features

**Apps Using Integrations:**
- **[Payment System](/features/built-in-apps/payments/overview)** - Uses Dramatiq for async processing
- **[AI Knowledge Base](/features/built-in-apps/ai-knowledge/overview)** - Uses Dramatiq for document processing
- **[Newsletter](/features/built-in-apps/user-management/newsletter)** - Uses Dramatiq for bulk emails

**Other Modules:**
- **[Modules Overview](/features/modules/overview)** - All available modules
- **[LLM Module](/features/modules/llm/overview)** - AI model integration

### Tools & Guides

**CLI Commands:**
- **[Background Task Commands](/cli/commands/background-tasks)** - Manage Dramatiq workers
- **[CLI Introduction](/cli/introduction)** - All CLI tools

**Guides:**
- **[Integration Patterns](./patterns)** - Best practices
- **[Production Config](/guides/production-config)** - Production integration setup
- **[Troubleshooting](/guides/troubleshooting)** - Common integration issues

---

## Next Steps

**New to Integrations?**
1. Start with [Dramatiq Overview](./dramatiq/overview) for background tasks
2. Try [Ngrok Overview](./ngrok/overview) for webhook testing
3. Review [Integration Patterns](./patterns) for best practices

**Ready for Production?**
1. Review [Production Config](/guides/production-config)
2. Set up [Redis](/fundamentals/configuration/cache) for Dramatiq
3. Configure [environment variables](/fundamentals/configuration/environment) for secrets

**Need Help?**
- [Troubleshooting Guide](/guides/troubleshooting)
- [FAQ](/guides/faq)
- [CLI Commands](/cli/introduction)

---

Django-CFG integrations: **Production-ready, type-safe, zero-config.** 🚀
