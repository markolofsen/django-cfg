---
title: Ngrok Implementation Guide
description: Django-CFG implementation feature guide. Production-ready ngrok implementation guide with built-in validation, type safety, and seamless Django integration.
sidebar_label: Implementation
sidebar_position: 3
keywords:
  - django-cfg implementation
  - django implementation
  - implementation django-cfg
---

# Ngrok Implementation Guide

Learn how to get tunnel URLs in your code and use management commands effectively.

## Getting Tunnel URL

Django-CFG provides multiple ways to get the current tunnel URL in your code.

### Method 1: Via DjangoNgrok Service (Recommended)

The recommended way to get tunnel URLs is through the `DjangoNgrok` service helper functions:

```python
from django_cfg.modules.django_ngrok import (
    get_tunnel_url,
    get_webhook_url,
    get_api_url,
    is_tunnel_active
)

# Check if tunnel is active
if is_tunnel_active():
    print("✅ Ngrok tunnel is running!")

# Get base URL
tunnel_url = get_tunnel_url()
# Returns: "https://abc123.ngrok.io" or None if not active

# Get webhook URL with automatic fallback
webhook_url = get_webhook_url("/payments/callback/")
# If ngrok active: "https://abc123.ngrok.io/payments/callback/"
# If not: "http://localhost:8000/payments/callback/" (fallback)

# Get API URL
api_url = get_api_url()
# If ngrok active: "https://abc123.ngrok.io"
# If not: api_url from DjangoConfig
```

#### Function Reference

**`get_tunnel_url() -> Optional[str]`**
- Returns current ngrok tunnel URL
- Returns `None` if tunnel is not active
- Example: `"https://abc123.ngrok.io"`

**`get_webhook_url(path: str = "/webhooks/") -> str`**
- Returns webhook URL with automatic fallback
- Always returns a valid URL (tunnel or fallback)
- Automatically adds path to tunnel URL
- Example: `"https://abc123.ngrok.io/api/webhooks/stripe/"`

**`get_api_url() -> str`**
- Returns API URL (tunnel if active, otherwise from config)
- Always returns a valid URL
- Example: `"https://abc123.ngrok.io"` or `"http://localhost:8000"`

**`is_tunnel_active() -> bool`**
- Check if ngrok tunnel is currently active
- Returns `True` if tunnel is running
- Use before tunnel-dependent operations

---

### Method 2: Via Environment Variables

After starting `runserver_ngrok`, tunnel info is available via environment variables:

```python
import os

# Tunnel URL
ngrok_url = os.environ.get('NGROK_URL')
# "https://abc123.ngrok.io" or None

# Tunnel host
ngrok_host = os.environ.get('NGROK_HOST')
# "abc123.ngrok.io" or None

# Scheme (http/https)
ngrok_scheme = os.environ.get('NGROK_SCHEME')
# "https" or None

# Build webhook URL manually
if ngrok_url:
    webhook_url = f"{ngrok_url}/api/webhooks/stripe/"
else:
    webhook_url = "http://localhost:8000/api/webhooks/stripe/"
```

---

### Method 3: Via Django Settings

Django-CFG automatically updates `ALLOWED_HOSTS` when tunnel starts:

```python
from django.conf import settings

# After runserver_ngrok starts:
print(settings.ALLOWED_HOSTS)
# ['localhost', '127.0.0.1', 'abc123.ngrok.io']

# Check if ngrok host is in allowed hosts
ngrok_host = os.environ.get('NGROK_HOST')
if ngrok_host and ngrok_host in settings.ALLOWED_HOSTS:
    print("✅ Ngrok tunnel is configured")
```

---

## Usage Patterns

### Pattern 1: Simple Webhook URL

```python
from django_cfg.modules.django_ngrok import get_webhook_url

def create_payment(request):
    # Get webhook URL (with automatic fallback)
    webhook_url = get_webhook_url("/api/payments/webhook/")

    # Use in payment provider
    payment = create_stripe_payment(
        amount=1000,
        webhook_url=webhook_url
    )

    return JsonResponse({"payment_id": payment.id})
```

### Pattern 2: Conditional Tunnel Usage

```python
from django_cfg.modules.django_ngrok import is_tunnel_active, get_webhook_url

def setup_external_service(request):
    if is_tunnel_active():
        # Use ngrok URL for webhook
        webhook_url = get_webhook_url("/webhooks/service/")
        print("✅ Using ngrok tunnel for webhooks")
    else:
        # Use production URL
        webhook_url = "https://api.myapp.com/webhooks/service/"
        print("⚠️ Using production URL")

    # Configure external service
    external_service.set_webhook(webhook_url)
```

### Pattern 3: Multiple Webhook Paths

```python
from django_cfg.modules.django_ngrok import get_webhook_url

# Different webhooks for different providers
stripe_webhook = get_webhook_url("/webhooks/stripe/")
nowpayments_webhook = get_webhook_url("/webhooks/nowpayments/")
telegram_webhook = get_webhook_url("/webhooks/telegram/")

print(f"Stripe: {stripe_webhook}")
print(f"NowPayments: {nowpayments_webhook}")
print(f"Telegram: {telegram_webhook}")

# Output (if ngrok active):
# Stripe: https://abc123.ngrok.io/webhooks/stripe/
# NowPayments: https://abc123.ngrok.io/webhooks/nowpayments/
# Telegram: https://abc123.ngrok.io/webhooks/telegram/
```

### Pattern 4: Dynamic Configuration

```python
from django_cfg.modules.django_ngrok import get_api_url, is_tunnel_active

class PaymentService:
    def __init__(self):
        # Automatically use correct base URL
        self.base_url = get_api_url()
        self.is_local = is_tunnel_active()

    def get_callback_url(self, endpoint: str) -> str:
        """Build callback URL with correct base."""
        return f"{self.base_url}{endpoint}"

    def create_payment(self, amount: int):
        callback_url = self.get_callback_url("/api/payments/callback/")

        if self.is_local:
            print(f"💡 Testing locally via ngrok: {callback_url}")

        # Create payment with callback URL
        # ...
```

---

## Management Commands

### runserver_ngrok

Runs Django development server with automatic ngrok tunnel creation.

#### Basic Usage

```bash
# Start server with ngrok tunnel
python manage.py runserver_ngrok

# Start on specific port
python manage.py runserver_ngrok 8080

# Start on specific host:port
python manage.py runserver_ngrok 0.0.0.0:8000
```

#### Advanced Options

```bash
# Use custom ngrok domain (paid plan)
python manage.py runserver_ngrok --domain myapp.ngrok.io

# Disable ngrok (run as regular runserver)
python manage.py runserver_ngrok --no-ngrok

# Force HTTPS
python manage.py runserver_ngrok --bind-tls

# Enable debug output
python manage.py runserver_ngrok --verbosity 2
```

#### Command Output

```bash
$ python manage.py runserver_ngrok

🚇 Starting ngrok tunnel...
⏳ Waiting for tunnel to be established...
⏳ Tunnel check 1/10...
⏳ Tunnel check 2/10...
✅ Ngrok tunnel ready: https://abc123.ngrok.io

Django version 5.0, using settings 'myproject.settings'
Starting development server at http://127.0.0.1:8000/
Public URL: https://abc123.ngrok.io
Quit the server with CONTROL-C.

Environment variables set:
  NGROK_URL=https://abc123.ngrok.io
  NGROK_HOST=abc123.ngrok.io
  NGROK_SCHEME=https

ALLOWED_HOSTS updated: ['localhost', '127.0.0.1', 'abc123.ngrok.io']
```

---

## Integration Patterns

### Django Views

```python
from django.http import JsonResponse
from django_cfg.modules.django_ngrok import get_webhook_url

def create_stripe_payment(request):
    """Create Stripe payment with ngrok webhook."""
    import stripe

    # Get webhook URL automatically
    webhook_url = get_webhook_url("/api/webhooks/stripe/")

    # Create payment intent
    intent = stripe.PaymentIntent.create(
        amount=1000,
        currency="usd",
        metadata={"webhook_url": webhook_url}
    )

    return JsonResponse({
        "client_secret": intent.client_secret,
        "webhook_url": webhook_url
    })
```

### Django REST Framework

```python
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django_cfg.modules.django_ngrok import get_webhook_url

@api_view(['POST'])
def create_payment_api(request):
    """API endpoint for payment creation."""
    amount = request.data.get('amount')

    # Get webhook URL
    webhook_url = get_webhook_url("/api/webhooks/payment/")

    # Create payment
    payment = PaymentService().create(
        amount=amount,
        webhook_url=webhook_url
    )

    return Response({
        "payment_id": payment.id,
        "webhook_url": webhook_url
    })
```

### Management Commands

```python
from django.core.management.base import BaseCommand
from django_cfg.modules.django_ngrok import get_webhook_url, is_tunnel_active

class Command(BaseCommand):
    help = "Setup Telegram bot webhook"

    def handle(self, *args, **options):
        if not is_tunnel_active():
            self.stdout.write(
                self.style.WARNING("⚠️ Ngrok tunnel is not active!")
            )
            return

        # Get webhook URL
        webhook_url = get_webhook_url("/api/webhooks/telegram/")

        # Setup Telegram webhook
        from telegram import Bot
        bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)
        bot.set_webhook(url=webhook_url)

        self.stdout.write(
            self.style.SUCCESS(f"✅ Webhook set to: {webhook_url}")
        )
```

### Background Tasks (ReArq)

```python
from rearq.decorators import task
from django_cfg.modules.django_ngrok import get_webhook_url

@task
async def send_webhook_notification(user_id: int):
    """Send webhook URL to user via email."""
    from django.core.mail import send_mail

    # Get current webhook URL
    webhook_url = get_webhook_url("/api/webhooks/user/")

    send_mail(
        subject="Your Webhook URL",
        message=f"Use this URL for testing: {webhook_url}",
        from_email="noreply@myapp.com",
        recipient_list=["user@example.com"],
    )
```

---

## Best Practices

### 1. Always Use Helper Functions

```python
# ✅ CORRECT - automatic fallback
from django_cfg.modules.django_ngrok import get_webhook_url

webhook_url = get_webhook_url("/webhooks/")
# Always returns valid URL (tunnel or fallback)

# ❌ WRONG - manual check
import os
ngrok_url = os.environ.get('NGROK_URL')
webhook_url = f"{ngrok_url}/webhooks/" if ngrok_url else "http://localhost:8000/webhooks/"
```

### 2. Check Tunnel Status Before Critical Operations

```python
# ✅ CORRECT - check before using
from django_cfg.modules.django_ngrok import is_tunnel_active, get_webhook_url

if is_tunnel_active():
    webhook_url = get_webhook_url("/webhooks/")
    setup_external_service(webhook_url)
else:
    print("⚠️ Tunnel not active, using fallback")
```

### 3. Use Type Hints

```python
# ✅ CORRECT - type hints
from typing import Optional
from django_cfg.modules.django_ngrok import get_tunnel_url

def get_public_url() -> Optional[str]:
    """Get public URL for webhooks."""
    return get_tunnel_url()
```

### 4. Log Tunnel Info

```python
# ✅ CORRECT - log for debugging
import logging
from django_cfg.modules.django_ngrok import is_tunnel_active, get_tunnel_url

logger = logging.getLogger(__name__)

if is_tunnel_active():
    logger.info(f"✅ Ngrok tunnel active: {get_tunnel_url()}")
else:
    logger.warning("⚠️ Ngrok tunnel not active")
```

---

## Next Steps

- **[Webhook Examples](./webhook-examples)** - See real-world webhook integrations
- **[Payments Panel](./payments-panel)** - Use built-in webhook admin panel
- **[Troubleshooting](./troubleshooting)** - Common issues and solutions

## See Also

### Ngrok Integration

**Core Documentation:**
- [**Ngrok Overview**](./overview) - Ngrok integration introduction
- [**Configuration Guide**](./configuration) - Complete ngrok configuration reference
- [**Webhook Examples**](./webhook-examples) - Real-world webhook integrations
- [**Payments Panel**](./payments-panel) - Built-in webhook admin panel
- [**Troubleshooting**](./troubleshooting) - Common implementation issues

### Implementation Guides

**Practical Examples:**
- [**Sample Project**](/guides/sample-project/overview) - Production ngrok example
- [**Examples Guide**](/guides/examples) - More webhook patterns
- [**Production Config**](/guides/production-config) - Production webhook setup

**Related Features:**
- [**Payments App**](/features/built-in-apps/payments/overview) - Payment webhooks
- [**Background Tasks**](/features/integrations/rearq/overview) - Async webhook processing
- [**Integrations Overview**](/features/integrations/overview) - All integrations

### Configuration & Setup

**Getting Started:**
- [**Installation**](/getting-started/installation) - Install Django-CFG with ngrok
- [**Configuration Guide**](/getting-started/configuration) - Configure ngrok
- [**First Project**](/getting-started/first-project) - Quick start tutorial

**Advanced:**
- [**Configuration Models**](/fundamentals/configuration) - NgrokConfig API reference
- [**Environment Variables**](/fundamentals/configuration/environment) - Ngrok auth token
- [**Environment Detection**](/fundamentals/configuration/environment) - Dev-only setup

### Tools & Development

**CLI & Management:**
- [**CLI Tools**](/cli/introduction) - Ngrok management commands
- [**Development Commands**](/cli/commands/development) - runserver_ngrok command
- [**Core Commands**](/cli/commands/core-commands) - Management utilities
- [**Troubleshooting**](/guides/troubleshooting) - Debug webhook issues
