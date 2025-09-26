# Universal Payment System v2.0

🚀 **Complete payment system with webhook support, provider management, and modern dashboard.**

## 🏗️ Architecture Overview

Built using **Skyscraper Architecture** - 8 levels from foundation to integration:

```
Level 7: Integration Layer    │ ✅ Webhooks, Templates, URLs
Level 6: Interface Layer      │ ✅ Admin, Management, Dashboard  
Level 5: API Layer           │ ✅ REST API, ViewSets, Serializers
Level 4: Service Layer       │ ✅ PaymentService, ProviderRegistry
Level 3: Business Logic      │ ✅ Signals, Middleware, Managers
Level 2: Data Layer          │ ✅ Models, Migrations, Relationships
Level 1: Infrastructure      │ ✅ Cache, Config, Ready Modules
Level 0: Foundation          │ ✅ Django, PostgreSQL, Redis, Python
```

## 🚀 Quick Start

### 1. Installation

```bash
# Add to INSTALLED_APPS
INSTALLED_APPS = [
    # ...
    'django_cfg.apps.payments',
    # ...
]

# Include URLs
urlpatterns = [
    # External API (requires API keys)
    path('payments/api/', include('django_cfg.apps.payments.urls_api')),
    
    # Internal admin (requires staff access)
    path('payments/admin/', include('django_cfg.apps.payments.urls_admin')),
]
```

### 2. Development with Ngrok

```bash
# Start development server with ngrok tunnel
python manage.py runserver_ngrok

# Access webhook dashboard
http://localhost:8000/payments/admin/webhooks/
```

### 3. Provider Configuration

The system automatically detects providers from `ProviderRegistry`. No hardcoded providers!

```python
# Providers are loaded dynamically from registry
from django_cfg.apps.payments.services.providers.registry import get_provider_registry

registry = get_provider_registry()
providers = registry.list_available_providers()  # ['nowpayments', ...]
```

## 📡 Webhook System

### Universal Webhook Handler

```python
# Supports any provider dynamically
POST /payments/api/webhooks/{provider}/

# Examples:
POST /payments/api/webhooks/nowpayments/
POST /payments/api/webhooks/stripe/
POST /payments/api/webhooks/new_provider/  # Automatically supported!
```

### Provider Management

```python
# Get webhook URLs for all providers
GET /payments/api/webhooks/providers/

# Response:
{
    "success": true,
    "providers": [
        {
            "name": "nowpayments",
            "display_name": "NowPayments", 
            "webhook_url": "https://abc123.ngrok.io/payments/api/webhooks/nowpayments/",
            "signature_header": "x-nowpayments-sig",
            "signature_algorithm": "HMAC-SHA512",
            "icon": "💎"
        }
    ]
}
```

### Security Features

- ✅ **Signature Validation** - Provider-specific HMAC verification
- ✅ **Replay Protection** - Request ID tracking and deduplication  
- ✅ **Rate Limiting** - Configurable per-provider limits
- ✅ **IP Filtering** - Optional whitelist support
- ✅ **Audit Logging** - Complete request/response logging

## 🎨 Dashboard Features

### Modern UI Components

- 🌙 **Dark Mode Support** - Automatic theme switching
- 📱 **Responsive Design** - Works on all devices  
- ⚡ **Real-time Updates** - Auto-refresh every 30 seconds
- 🔄 **Interactive Elements** - Copy URLs, test webhooks
- 📊 **Live Statistics** - Provider health, success rates

### Template Components

Reusable, dynamic components:

```django
<!-- Status Card -->
{% include 'payments/components/status_card.html' with title="Ngrok Status" icon="🌐" %}

<!-- Provider Card (dynamic) -->
{% include 'payments/components/provider_card.html' with provider=provider_data %}

<!-- Loading Spinner -->
{% include 'payments/components/loading_spinner.html' with size="large" %}
```

## 🔧 Configuration

### Provider Registration

```python
# Add new provider (no code changes needed!)
from django_cfg.apps.payments.services.integrations.providers_config import WEBHOOK_METADATA

# Just add to WEBHOOK_METADATA
WEBHOOK_METADATA['new_provider'] = WebhookProviderInfo(
    name='new_provider',
    display_name='New Provider',
    signature_header='x-new-provider-sig',
    signature_algorithm='HMAC-SHA256',
    icon='🆕'
)
```

### Ngrok Integration

```python
# Automatic ngrok support via django-cfg
# No configuration needed - just run:
python manage.py runserver_ngrok
```

### Environment Variables

```bash
# Ngrok authentication
NGROK_AUTHTOKEN=your_token_here

# Provider secrets (via Constance)
NOWPAYMENTS_API_KEY=your_api_key
NOWPAYMENTS_IPN_SECRET=your_secret
```

## 📊 API Endpoints

### External API (requires API keys)

```
# Payment Management
GET    /payments/api/payments/
POST   /payments/api/payments/
GET    /payments/api/payments/{id}/

# Webhook Endpoints  
POST   /payments/api/webhooks/{provider}/
GET    /payments/api/webhooks/providers/
GET    /payments/api/webhooks/health/
GET    /payments/api/webhooks/stats/

# Currency & Rates
GET    /payments/api/currencies/
GET    /payments/api/currencies/rates/
POST   /payments/api/currencies/convert/
```

### Internal Admin (requires staff access)

```
# Dashboard
GET    /payments/admin/
GET    /payments/admin/webhooks/

# Management Tools
GET    /payments/admin/ajax/webhooks/status/
GET    /payments/admin/ajax/webhooks/stats/
```

## 🧪 Testing

### Webhook Testing

```bash
# Test webhook endpoint
curl -X POST https://abc123.ngrok.io/payments/api/webhooks/nowpayments/ \
  -H "Content-Type: application/json" \
  -H "x-nowpayments-sig: test_signature" \
  -d '{"payment_id": "test", "payment_status": "finished"}'
```

### Health Checks

```bash
# Check system health
curl /payments/api/webhooks/health/

# Get statistics  
curl /payments/api/webhooks/stats/?days=7
```

## 🔄 Adding New Providers

### 1. Register Provider Class

```python
# In your provider module
class NewProvider(BaseProvider):
    def validate_webhook(self, payload, signature):
        # Provider-specific validation
        pass

# Register with system
registry.register_provider_class('new_provider', NewProvider, NewProviderConfig)
```

### 2. Add Webhook Metadata

```python
# In providers_config.py
WEBHOOK_METADATA['new_provider'] = WebhookProviderInfo(
    name='new_provider',
    display_name='New Provider',
    signature_header='x-new-provider-sig', 
    signature_algorithm='HMAC-SHA256',
    icon='🆕'
)
```

### 3. That's it! 

The system automatically:
- ✅ Creates webhook endpoint: `/webhooks/new_provider/`
- ✅ Adds to dashboard UI with icon
- ✅ Includes in provider list API
- ✅ Handles signature validation
- ✅ Provides ngrok URLs

## 📈 Performance & Scalability

- **Lazy Loading** - Providers loaded on-demand
- **Caching** - Redis-backed provider and rate limit caching
- **Async Support** - Ready for async webhook processing
- **Health Monitoring** - Automatic provider health checks
- **Fallback Mechanisms** - Graceful degradation when providers fail

## 🛡️ Security Best Practices

1. **Always validate signatures** - Never trust unsigned webhooks
2. **Use HTTPS in production** - Ngrok is for development only
3. **Implement rate limiting** - Prevent abuse and DoS attacks
4. **Monitor webhook activity** - Set up alerts for failures
5. **Rotate secrets regularly** - Update provider secrets periodically

## 📚 Documentation

- [Webhook Integration Guide](/@docs_new/integration/webhooks-ngrok.md)
- [Provider Configuration](/@docs_new/models/config.md)
- [Service Layer Documentation](/@docs_new/services/index.md)
- [Architecture Overview](/@docs_new/architecture.md)

## 🎯 Production Deployment

### Requirements

- Python 3.11+
- Django 4.2+
- PostgreSQL 12+
- Redis 6+
- Nginx (for static files)

### Environment Setup

```bash
# Production settings
DEBUG=False
ALLOWED_HOSTS=your-domain.com
DATABASE_URL=postgresql://...
REDIS_URL=redis://...

# Provider configuration
NOWPAYMENTS_API_KEY=prod_key
NOWPAYMENTS_IPN_SECRET=prod_secret
```

### Nginx Configuration

```nginx
location /payments/api/webhooks/ {
    proxy_pass http://django;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
}
```

---

## 🎉 **Universal Payment System v2.0 - Ready for Production!**

**Built with ❤️ using Django-CFG framework**
