---
title: Django-CFG Examples
description: Django-CFG examples guide. Practical tutorial for django-cfg examples with real-world examples, troubleshooting tips, and production patterns.
sidebar_label: Examples
sidebar_position: 10
keywords:
  - django-cfg examples
  - django-cfg guide examples
  - how to examples django
---

# Django-CFG Examples

Comprehensive real-world examples demonstrating Django-CFG capabilities across different features and industries.

## 🚀 Quick Start Examples

Start here if you're new to Django-CFG:

### **[Sample Project Guide](./sample-project/overview)**
Complete walkthrough of a production-ready Django-CFG project with all features:
- Multi-database setup
- Modern admin interface
- API documentation
- Background tasks
- Service integrations

**Perfect for**: Beginners wanting to see everything in action

---

## 🤖 AI Agents Examples

Real-world examples of building intelligent workflows with Django-CFG AI agents.

### **[AI Agents Examples](/ai-agents/examples)**
- Document processing agents
- Customer support automation
- Data analysis workflows
- Business process automation

**Use cases**: Content generation, automated support, data processing

---

## 💱 Currency Conversion Examples

Examples showing multi-currency support across different industries.

### **[E-commerce Applications](../features/modules/currency/examples/ecommerce)**
- Multi-currency product catalogs
- Shopping cart with currency conversion
- Dynamic pricing

### **[Financial Applications](../features/modules/currency/examples/financial)**
- Crypto portfolio tracking
- Investment returns calculator
- Multi-asset tracking

### **[Import/Export Business](../features/modules/currency/examples/import-export)**
- Vehicle import cost calculator
- Global pricing strategies
- International shipping costs

### **[Gaming & Entertainment](../features/modules/currency/examples/gaming)**
- In-game currency exchange
- Regional pricing for game items
- Optimal purchase calculator

### **[Business Intelligence](../features/modules/currency/examples/business-intelligence)**
- Multi-currency revenue analytics
- Cross-border sales analysis
- Currency exposure reporting

**Supports**: 14K+ currencies including fiat, crypto, stocks, commodities

---

## 🔄 Background Tasks Examples

Production-ready background task processing with ReArq.

### **[ReArq Examples](../features/integrations/rearq/overview)**
- Email campaign processing
- Document processing pipelines
- Data synchronization
- Report generation
- Scheduled cleanup tasks

**Perfect for**: Asynchronous workflows, heavy computations, scheduled jobs

---

## 💳 Payments Integration Examples

Real-world payment integration examples with webhook handling.

### **[Payments Examples](../features/built-in-apps/payments/examples)**
- Stripe integration
- NowPayments crypto payments
- Webhook handling
- Payment status tracking

**Includes**: Webhook dashboard, ngrok integration for local testing

---

## 📧 Communication Examples

Multi-channel communication examples (Email, SMS, Telegram).

### Email Examples
```python
from django_cfg.modules.django_email import DjangoEmailService

email = DjangoEmailService()
email.send_simple(
    subject="Welcome to Django-CFG",
    body="Thank you for signing up!",
    recipients=["user@example.com"]
)
```

### SMS Examples (Twilio)
```python
from django_cfg.modules.django_twilio import DjangoTwilioService

twilio = DjangoTwilioService()
twilio.send_sms(
    to="+1234567890",
    message="Your verification code: 123456"
)
```

### Telegram Examples
```python
from django_cfg.modules.django_telegram import DjangoTelegramService

telegram = DjangoTelegramService()
telegram.send_message(
    chat_id="123456",
    text="🚀 Your order has been shipped!"
)
```

**Use cases**: Notifications, OTP authentication, customer support

---

## 🗄️ Multi-Database Examples

Examples showing smart database routing and multi-database architecture.

### Basic Multi-Database Setup
```python
from django_cfg import DjangoConfig, DatabaseConfig

class MyConfig(DjangoConfig):
    databases: dict[str, DatabaseConfig] = {
        "default": DatabaseConfig(
            engine="postgresql",
            name="main_db",
        ),
        "analytics": DatabaseConfig(
            name="analytics_db",
            routing_apps=["analytics", "reports"],  # Auto-routes!
        ),
    }
```

### Usage in Code
```python
# No manual .using() calls needed!
report = Report.objects.create(...)  # Automatically goes to analytics_db
user = User.objects.create(...)      # Goes to default database
```

**See**: [Sample Project Multi-Database Guide](./sample-project/multi-database)

---

## 🎨 Admin Interface Examples

Examples of customizing the modern Unfold admin interface.

### Dashboard Integration

Dashboard is automatically available at `/admin/` with Next.js frontend and REST API backend:

```python
# Built-in endpoints automatically available:
# - /cfg/dashboard/api/statistics/ - Real-time statistics
# - /cfg/dashboard/api/health/ - System health monitoring
# - /cfg/dashboard/api/charts/ - Chart data
# - /cfg/dashboard/api/commands/ - Command execution

# To customize, extend the service classes:
from django_cfg.apps.dashboard.services import StatisticsService

class CustomStatisticsService(StatisticsService):
    def get_custom_metrics(self):
        # Add your custom metrics
        return {"custom_metric": 42}
```

**See**: [Sample Project Admin Interface](./sample-project/admin-interface)

---

## 📚 API Documentation Examples

Auto-generated OpenAPI documentation with TypeScript and Python clients.

### Multi-Group API Setup
```python
from django_cfg import OpenAPIClientConfig, OpenAPIGroupConfig

class MyConfig(DjangoConfig):
    openapi_client: OpenAPIClientConfig = OpenAPIClientConfig(
        enabled=True,
        generate_package_files=True,
        generate_zod_schemas=True,
        generate_fetchers=True,
        generate_swr_hooks=True,
        api_prefix="api",
        output_dir="openapi",
        drf_title="My App API",
        drf_description="Complete API documentation",
        drf_version="1.0.0",
        groups=[
            OpenAPIGroupConfig(
                name="public",
                apps=["blog", "products"],
                title="Public API",
                description="Public-facing API endpoints",
                version="1.0.0",
            ),
            OpenAPIGroupConfig(
                name="partner",
                apps=["integrations"],
                title="Partner API",
                description="Partner integration endpoints",
                version="1.0.0",
            ),
        ],
    )
```

**Automatically provides**:
- **TypeScript clients** with Zod validation schemas
- **Python clients** with type hints
- **SWR hooks** for React/Next.js integration
- **Type-safe fetchers** with error handling

**See**: [Sample Project API Documentation](./sample-project/api-documentation)

---

## 🎫 Built-in Apps Examples

Production-ready built-in applications.

### Support Ticket System
```python
# config.py
enable_support: bool = True  # Complete ticketing system!

# Automatically provides:
# - Ticket management
# - Modern chat interface
# - Email notifications
# - Admin dashboard
# - REST API endpoints
```

### User Management with OTP
```python
enable_accounts: bool = True  # Advanced user management!

# Automatically provides:
# - Email OTP authentication
# - SMS OTP authentication (Twilio)
# - User profiles
# - Activity tracking
# - Security audit logs
```

### Newsletter System
```python
enable_newsletter: bool = True  # Email marketing!

# Automatically provides:
# - Newsletter campaigns
# - Subscriber management
# - Email tracking (opens, clicks)
# - Analytics dashboard
```

**See**: [Built-in Apps Documentation](../features/built-in-apps/overview)

---

## 🌐 Webhook Testing Examples

Local webhook testing with automatic ngrok integration.

### Setup
```python
# config.py
ngrok: NgrokConfig = NgrokConfig(enabled=True)
```

### Usage
```bash
# Start with ngrok tunnel
python manage.py runserver_ngrok

# Output:
# ✅ Ngrok tunnel ready: https://abc123.ngrok.io
```

```python
from django_cfg.modules.django_ngrok import get_webhook_url

# Get webhook URL automatically
stripe_webhook = get_webhook_url("/api/webhooks/stripe/")
# "https://abc123.ngrok.io/api/webhooks/stripe/"
```

**See**:
- [Ngrok Integration Overview](../features/integrations/ngrok/overview)
- [Webhook Examples](../features/integrations/ngrok/webhook-examples)
- [Webhook Admin Panel](../features/integrations/ngrok/payments-panel)

---

## 🔐 Authentication Examples

Multi-channel OTP authentication examples.

### Email OTP
```python
from django_cfg.apps.accounts.services.otp_service import OTPService

# Request OTP
success, error = OTPService.request_email_otp("user@example.com")

# Verify OTP
user = OTPService.verify_email_otp("user@example.com", "123456")
```

### SMS OTP (Twilio)
```python
# Request SMS OTP
success, error = OTPService.request_phone_otp("+1234567890")

# Verify SMS OTP
user = OTPService.verify_phone_otp("+1234567890", "123456")
```

**See**: [Sample Project Authentication](./sample-project/authentication)

---

## 📖 More Examples

### By Feature
- **[First Project Guide](/getting-started/first-project)** - Step-by-step project setup
- **[Production Examples](./production-config)** - Production-ready configurations
- **[Migration Examples](./migration-guide)** - Migrating existing Django projects

### By Industry
- **E-commerce** - Product catalogs, shopping carts, payments
- **Finance** - Portfolio tracking, investment calculators
- **SaaS** - Multi-tenant, subscriptions, billing
- **Enterprise** - Support tickets, user management, analytics

---

## 🎯 Choose Your Path

**New to Django-CFG?**
→ Start with [Sample Project Guide](./sample-project/overview)

**Building E-commerce?**
→ See [Currency Examples](../features/modules/currency/examples/ecommerce) and [Payments Examples](../features/built-in-apps/payments/examples)

**Need AI Automation?**
→ Check [AI Agents Examples](/ai-agents/examples)

**Setting up Background Tasks?**
→ Explore [ReArq Examples](../features/integrations/rearq/overview)

**Testing Webhooks?**
→ Learn [Ngrok Integration](../features/integrations/ngrok/overview)

---

## 💡 Contributing Examples

Have a great Django-CFG example? We'd love to include it!

1. Fork the [documentation repository](https://github.com/markolofsen/django-cfg)
2. Add your example with clear code comments
3. Submit a pull request

---

**All examples are production-tested and ready to use!** 🚀
