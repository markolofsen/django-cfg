---
title: Modules System Overview
description: Django-CFG overview feature guide. Production-ready modules system overview with built-in validation, type safety, and seamless Django integration.
sidebar_label: Overview
sidebar_position: 1
keywords:
  - django-cfg overview
  - django overview
  - overview django-cfg
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# Modules System Overview

Django-CFG provides a powerful **modular system** that automatically configures Django services based on your configuration. Modules eliminate boilerplate code and provide production-ready functionality out of the box.

## What are Modules?

Modules are **auto-configuring services** that:

- **🔧 Auto-discover configuration** from your Django-CFG settings
- **⚡ Zero-setup integration** - just import and use
- **🛡️ Production-ready** with error handling and logging
- **🔌 Extensible** - create your own modules easily
- **📊 Observable** - built-in monitoring and health checks

## Architecture

### Base Module System

All modules inherit from `BaseCfgModule`:

```python
from django_cfg.modules.base import BaseCfgModule

class MyCustomModule(BaseCfgModule):
    def __init__(self):
        super().__init__()
        self.config = self.get_config()  # Auto-discovers Django-CFG config
        
    def my_method(self):
        # Access configuration automatically
        if hasattr(self.config, 'my_service'):
            return self.config.my_service.api_key
```

### Configuration Discovery

Modules automatically find your configuration:

```python
# api/config.py
class MyProjectConfig(DjangoConfig):
    email: EmailConfig = EmailConfig(
        backend="sendgrid",
        sendgrid_api_key=env.email.sendgrid_api_key
    )

# Anywhere in your code
from django_cfg import DjangoEmailService

email = DjangoEmailService()  # Automatically uses your EmailConfig
email.send_simple("Test", "Hello!", ["user@example.com"])
```

## Built-in Modules

<Tabs groupId="module-categories">
  <TabItem value="communication" label="📧 Communication" default>

### Email Module (`DjangoEmailService`)

Auto-configuring email service with multiple backends:

```python
from django_cfg import DjangoEmailService

email = DjangoEmailService()

# Simple email
email.send_simple(
    subject="Welcome!",
    message="Hello World!",
    recipient_list=["user@example.com"]
)

# Template-based email
email.send_template(
    template_name="welcome_email.html",
    context={"user_name": "John"},
    recipient_list=["user@example.com"],
    subject="Welcome to our platform!"
)

# Bulk email with SendGrid
email.send_bulk_sendgrid(
    template_id="d-123456789",
    recipients=[
        {"email": "user1@example.com", "name": "User 1"},
        {"email": "user2@example.com", "name": "User 2"}
    ],
    template_data={"company": "My Company"}
)
```

**Features:**
- ✅ Multiple backends (SMTP, SendGrid, etc.)
- ✅ Template rendering with Django templates
- ✅ Bulk email support
- ✅ Attachment handling
- ✅ HTML/text alternatives
- ✅ Error handling and retries

---

### Telegram Module (`DjangoTelegram`)

Bot integration and notifications:

```python
from django_cfg import DjangoTelegram, send_telegram_message

telegram = DjangoTelegram()

# Send notifications
telegram.send_message(
    chat_id="-1001234567890",
    text="🚀 Deployment completed successfully!"
)

# Send with formatting
telegram.send_message(
    chat_id="@my_channel",
    text="*Error Alert*\n`Database connection failed`",
    parse_mode="Markdown"
)

# Send files
telegram.send_document(
    chat_id="123456789",
    document=open("report.pdf", "rb"),
    caption="Monthly report"
)
```

**Features:** Message sending and formatting, file and media uploads, bot command handling, webhook integration, channel/group management, and error notifications.

  </TabItem>
  <TabItem value="operations" label="⚙️ Operations">

### Health Check Module

Django-CFG provides health check views:

```python
# In your urls.py
from django_cfg.modules.django_health import HealthCheckView, SimpleHealthView

urlpatterns = [
    path('health/', HealthCheckView.as_view(), name='health-check'),
    path('health/simple/', SimpleHealthView.as_view(), name='health-simple'),
]
```

**Built-in Checks:**
- ✅ Database connectivity
- ✅ Cache availability (Redis/Memcached)
- ✅ Disk space and memory
- ✅ Returns JSON health status

---

### Logger Module (`DjangoLogger`)

Enhanced logging with structured output:

```python
from django_cfg import DjangoLogger, get_logger

logger = get_logger("my_app")

# Structured logging
logger.info("User login", extra={
    "user_id": 123,
    "ip_address": "192.168.1.1",
    "user_agent": "Chrome/91.0"
})

# Performance monitoring
with logger.timer("database_query"):
    results = MyModel.objects.filter(active=True)
```

**Features:**
- ✅ Structured JSON logging
- ✅ Automatic request correlation
- ✅ Performance timing
- ✅ Error aggregation
- ✅ Multiple output formats
- ✅ Log rotation and archival

---

### Tasks Module (`DjangoTasks`)

Background task processing with ReArq:

```python
from django_cfg.modules.django_tasks import DjangoTasks

tasks = DjangoTasks()

# Simple task
@tasks.task
def send_welcome_email(user_id):
    user = User.objects.get(id=user_id)
    return f"Email sent to {user.email}"

# Schedule task
task_id = tasks.enqueue(send_welcome_email, user_id=123)

# Periodic task
tasks.schedule_periodic(
    "cleanup_old_files",
    cron="0 2 * * *",  # Daily at 2 AM
    func=cleanup_old_files
)
```

**Features:** Async task execution, scheduled/delayed tasks, periodic/cron tasks, task monitoring and retries, priority queues, and dead letter queues.

---

### Django-Q2 Task Scheduling Module

Type-safe task scheduling with Django-Q2 for distributed async tasks:

```python
from django_cfg import DjangoQ2Config, DjangoQ2ScheduleConfig

# In config.py
django_q2 = DjangoQ2Config(
    enabled=True,
    workers=4,
    schedules=[
        # Sync data every 5 minutes
        DjangoQ2ScheduleConfig(
            name="Sync data",
            schedule_type="minutes",
            minutes=5,
            command="sync_data",
        ),
        # Daily cleanup at 2 AM
        DjangoQ2ScheduleConfig(
            name="Cleanup",
            schedule_type="cron",
            cron="0 2 * * *",
            command="cleanup_old_data",
        ),
    ],
)
```

**Features:** Type-safe configuration, distributed task processing, async task execution, scheduled/cron/interval tasks, built-in admin interface, automatic retries, result storage, task monitoring via Dashboard API, and production-ready error handling.

**Learn more:** [Django-Q2 Scheduling Module Documentation](./scheduling/overview)

  </TabItem>
  <TabItem value="development" label="🔧 Development Tools">

### Ngrok Module (`DjangoNgrok`)

Development tunneling for webhooks:

```python
from django_cfg.modules.django_ngrok import DjangoNgrok

ngrok = DjangoNgrok()

# Start tunnel for development
tunnel_url = ngrok.start_tunnel(port=8000)
print(f"Public URL: {tunnel_url}")

# Configure webhooks automatically
ngrok.setup_webhook_urls({
    "stripe": "/webhooks/stripe/",
    "twilio": "/webhooks/twilio/",
    "github": "/webhooks/github/"
})
```

**Features:** Automatic tunnel creation, webhook URL management, SSL certificate handling, custom domain support, tunnel monitoring, and development/production switching.

  </TabItem>
  <TabItem value="advanced" label="🚀 Advanced Modules">

### Currency Module (`CurrencyConverter`)

Multi-currency support with real-time rates and crypto:

```python
from django_cfg.modules.django_currency import convert_currency, CurrencyConverter

# Quick conversions
usd_amount = convert_currency(100, "EUR", "USD")
btc_amount = convert_currency(50000, "USD", "BTC")

# Detailed conversion
converter = CurrencyConverter()
result = converter.convert(100, "USD", "EUR")
print(f"Rate: {result.rate.rate}, Source: {result.rate.source}")
```

---

### LLM Module (`LLMClient`)

AI/LLM integration with multiple providers:

```python
from django_cfg.modules.django_llm.llm.client import LLMClient

client = LLMClient()

# Chat completion
response = client.chat_completion(
    messages=[
        {"role": "system", "content": "You are a helpful Django expert"},
        {"role": "user", "content": "How do I optimize Django queries?"}
    ],
    model="gpt-4"
)
```

**Note:** See [LLM Module Documentation](/features/modules/llm/overview) for complete API reference.

---

### Twilio Module (OTP Services)

Complete Twilio Verify OTP integration:

```python
from django_cfg.modules.django_twilio.service import UnifiedOTPService

# Unified OTP service (SMS, WhatsApp, Email)
otp = UnifiedOTPService()

# Send OTP via SMS
verification = otp.send_otp(
    phone="+1234567890",
    channel="sms"
)

# Verify OTP code
is_valid = otp.verify_otp(
    phone="+1234567890",
    code="123456"
)
```

**Available Services:** `UnifiedOTPService` (multi-channel: SMS, WhatsApp, Email), `SMSOTPService` (SMS-only), `WhatsAppOTPService` (WhatsApp-only), and `EmailOTPService` (Email-only).

  </TabItem>
</Tabs>

## 🔌 Creating Custom Modules

### Basic Custom Module

```python
from django_cfg.modules.base import BaseCfgModule
from typing import Optional

class MyCustomService(BaseCfgModule):
    """Custom service module."""
    
    def __init__(self):
        super().__init__()
        self.config = self.get_config()
        self.my_config = getattr(self.config, 'my_service', None)
    
    def do_something(self) -> str:
        """Perform custom operation."""
        if not self.my_config:
            raise ValueError("MyService not configured")
        
        # Use configuration
        api_key = self.my_config.api_key
        base_url = self.my_config.base_url
        
        # Your service logic here
        return "Operation completed"
    
    def health_check(self) -> dict:
        """Health check for monitoring."""
        try:
            # Test your service
            result = self.do_something()
            return {
                "status": "healthy",
                "details": "Service is operational"
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "details": str(e)
            }
```

### Configuration Integration

```python
# api/config.py
from pydantic import BaseModel

class MyServiceConfig(BaseModel):
    api_key: str
    base_url: str = "https://api.myservice.com"
    timeout: int = 30
    retries: int = 3

class MyProjectConfig(DjangoConfig):
    my_service: MyServiceConfig = MyServiceConfig(
        api_key=env.my_service.api_key
    )
```

## Best Practices

### 1. Use Type Hints

```python
from typing import List, Dict, Optional

class MyService(BaseCfgModule):
    def process_items(self, items: List[Dict[str, str]]) -> Optional[str]:
        pass
```

### 2. Handle Configuration Gracefully

```python
def __init__(self):
    super().__init__()
    self.config = self.get_config()
    
    # Graceful degradation
    if not self.config or not hasattr(self.config, 'my_service'):
        self.enabled = False
        return
    
    self.enabled = True
    self.service_config = self.config.my_service
```

### 3. Implement Health Checks

```python
def health_check(self) -> dict:
    if not self.enabled:
        return {"status": "disabled", "details": "Service not configured"}
    
    try:
        # Test service connectivity
        self._test_connection()
        return {"status": "healthy"}
    except Exception as e:
        return {"status": "unhealthy", "details": str(e)}
```

### 4. Add Monitoring and Metrics

```python
import time
from collections import defaultdict

class MonitoredService(BaseCfgModule):
    def __init__(self):
        super().__init__()
        self.metrics = defaultdict(int)
        self.response_times = []
    
    def tracked_operation(self, data):
        start_time = time.time()
        
        try:
            result = self._process(data)
            self.metrics["success"] += 1
            return result
        except Exception as e:
            self.metrics["error"] += 1
            raise
        finally:
            duration = time.time() - start_time
            self.response_times.append(duration)
            self.metrics["total_requests"] += 1
```

## Integration with Django-CFG

### Automatic Discovery

Modules automatically discover your Django-CFG configuration:

```python
# No manual configuration needed!
email = DjangoEmailService()  # Finds EmailConfig automatically
health = DjangoHealthService()  # Finds all health-related configs
telegram = DjangoTelegramService()  # Finds TelegramConfig automatically
```

### Configuration Validation

```python
# api/config.py
class MyProjectConfig(DjangoConfig):
    email: EmailConfig = EmailConfig(...)
    
    def validate_modules(self):
        """Custom validation for modules."""
        # Ensure email is configured for production
        if self.is_prod and not self.email.sendgrid_api_key:
            raise ValueError("SendGrid API key required for production")
        
        # Validate Telegram config
        if hasattr(self, 'telegram') and self.telegram:
            if not self.telegram.bot_token:
                raise ValueError("Telegram bot token is required")
```

## Explore Modules

### Currency & Finance
- **[Currency Overview](./currency/overview)** - Multi-currency conversion with crypto support
- **[Currency Quick Start](./currency/quick-start)** - Get started in 5 minutes
- **[Database Integration](./currency/database-integration)** - ORM integration guide

### Communication
- **[Email Overview](./email/overview)** - Advanced email system
- **[Telegram Overview](./telegram/overview)** - Bot integration and notifications

### AI & Intelligence  
- **[LLM Overview](./llm/overview)** - Multi-provider AI integration

### Operations
- **[Health Overview](./health/overview)** - System monitoring
- **[Import/Export Overview](./import-export/overview)** - Data management
- **[Unfold Overview](./unfold/overview)** - Modern admin interface
- **[Scheduling Overview](./scheduling/overview)** - Django-Q2 task scheduling

### Related Documentation

**Available Modules:**
- **[Currency Module](./currency/overview)** - Multi-currency conversion with 14K+ currencies
- **[Email Module](./email/overview)** - Production email service integration
- **[Telegram Module](./telegram/overview)** - Telegram bot and notifications
- **[LLM Module](./llm/overview)** - Multi-provider LLM integration
- **[Tasks Module](/features/built-in-apps/operations/tasks)** - Background task management
- **[Health Module](./health/overview)** - System health checks
- **[Import/Export Module](./import-export/overview)** - Data import/export utilities
- **[Unfold Module](./unfold/overview)** - Modern admin interface
- **[Scheduling Module](./scheduling/overview)** - Django-Q2 distributed task scheduling

**Configuration & Setup:**
- **[Configuration Guide](/fundamentals/configuration)** - Configure modules
- **[Configuration Models](/fundamentals/configuration)** - Complete module config API
- **[Environment Detection](/fundamentals/configuration/environment)** - Environment-specific modules
- **[Installation](/getting-started/installation)** - Install Django-CFG with modules

**Apps Using Modules:**
- **[Built-in Apps Overview](/features/built-in-apps/overview)** - Production-ready apps
- **[User Management](/features/built-in-apps/user-management/overview)** - Uses Email, Tasks modules
- **[Payment System](/features/built-in-apps/payments/overview)** - Uses Currency, Tasks modules
- **[AI Knowledge Base](/features/built-in-apps/ai-knowledge/overview)** - Uses LLM, Tasks modules

**Integrations:**
- **[ReArq Integration](/features/built-in-apps/operations/tasks)** - Background task processing
- **[Ngrok Integration](/features/integrations/ngrok/overview)** - Webhook testing
- **[API Generation](/features/api-generation/overview)** - Auto-generate API clients
- **[Integrations Overview](/features/integrations/overview)** - All integrations

**Guides & Tools:**
- **[CLI Tools](/cli/introduction)** - Manage modules via CLI
- **[Production Config](/guides/production-config)** - Production module setup
- **[Troubleshooting](/guides/troubleshooting)** - Common module issues
- **[Examples](/guides/examples)** - Real-world module usage

The modular system makes Django-CFG incredibly powerful and flexible while maintaining simplicity! 🚀
