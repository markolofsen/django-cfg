---
title: Webhook Integration Examples
description: Django-CFG webhook examples feature guide. Production-ready webhook integration examples with built-in validation, type safety, and seamless Django integration.
sidebar_label: Webhook Examples
sidebar_position: 4
keywords:
  - django-cfg webhook examples
  - django webhook examples
  - webhook examples django-cfg
---

# Webhook Integration Examples

Complete examples of webhook integration with external services using Django-CFG ngrok integration.

## Stripe Webhooks

### Basic Setup

```python
# services/stripe_service.py
from django_cfg.modules.django_ngrok import get_webhook_url
import stripe
from django.conf import settings

stripe.api_key = settings.STRIPE_SECRET_KEY

class StripeService:
    def create_payment_intent(self, amount: int, currency: str = "usd") -> dict:
        """Create Stripe payment with ngrok webhook."""

        # Automatically get webhook URL
        webhook_url = get_webhook_url("/api/webhooks/stripe/")

        # Create payment intent
        intent = stripe.PaymentIntent.create(
            amount=amount,
            currency=currency,
            metadata={
                "webhook_url": webhook_url  # Ngrok URL!
            }
        )

        return intent


# views.py
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import stripe

@csrf_exempt
def stripe_webhook(request):
    """Handle Stripe webhook - accessible via ngrok!"""
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')

    try:
        # Verify webhook signature
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError:
        return JsonResponse({"error": "Invalid payload"}, status=400)
    except stripe.error.SignatureVerificationError:
        return JsonResponse({"error": "Invalid signature"}, status=400)

    # Handle event
    if event['type'] == 'payment_intent.succeeded':
        payment_intent = event['data']['object']
        print(f"✅ Payment succeeded: {payment_intent['id']}")
        # Process successful payment
        process_successful_payment(payment_intent)

    elif event['type'] == 'payment_intent.payment_failed':
        payment_intent = event['data']['object']
        print(f"❌ Payment failed: {payment_intent['id']}")
        # Handle failed payment
        handle_failed_payment(payment_intent)

    return JsonResponse({"status": "success"})
```

### Complete Workflow

```python
# 1. Start Django with ngrok
# $ python manage.py runserver_ngrok
# ✅ Ngrok tunnel ready: https://abc123.ngrok.io

# 2. Create Stripe payment
from services.stripe_service import StripeService

service = StripeService()
intent = service.create_payment_intent(amount=1000)  # $10.00

print(f"Payment Intent ID: {intent.id}")
print(f"Webhook URL: {intent.metadata['webhook_url']}")
# Webhook URL: https://abc123.ngrok.io/api/webhooks/stripe/

# 3. Stripe sends webhook to your local server via ngrok!
# Your stripe_webhook view receives and processes the event
```

---

## NowPayments Crypto Webhooks

### Basic Setup

```python
# services/nowpayments_service.py
from django_cfg.modules.django_ngrok import get_webhook_url
import requests
from django.conf import settings
import uuid

class NowPaymentsService:
    API_URL = "https://api.nowpayments.io/v1"

    def __init__(self):
        self.api_key = settings.NOWPAYMENTS_API_KEY

    def create_payment(
        self,
        amount: float,
        currency: str = "BTC",
        order_id: str = None
    ) -> dict:
        """Create crypto payment with webhook."""

        # Get webhook URL automatically
        ipn_url = get_webhook_url("/api/webhooks/nowpayments/")

        # Create payment
        response = requests.post(
            f"{self.API_URL}/payment",
            headers={"x-api-key": self.api_key},
            json={
                "price_amount": amount,
                "price_currency": "USD",
                "pay_currency": currency,
                "ipn_callback_url": ipn_url,  # Ngrok tunnel!
                "order_id": order_id or f"order-{uuid.uuid4()}",
                "order_description": "Test payment"
            }
        )

        return response.json()

    def create_invoice(self, amount_usd: float) -> dict:
        """Create crypto invoice with webhook."""

        ipn_url = get_webhook_url("/api/webhooks/nowpayments/")

        response = requests.post(
            f"{self.API_URL}/invoice",
            headers={"x-api-key": self.api_key},
            json={
                "price_amount": amount_usd,
                "price_currency": "usd",
                "ipn_callback_url": ipn_url,  # Ngrok URL!
                "success_url": f"{ipn_url}success/",
                "cancel_url": f"{ipn_url}cancel/",
            }
        )

        return response.json()


# views.py
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import hmac
import hashlib

@csrf_exempt
def nowpayments_webhook(request):
    """Handle NowPayments IPN webhook."""

    # Verify signature
    signature = request.META.get('HTTP_X_NOWPAYMENTS_SIG')
    payload = request.body

    # Verify HMAC signature
    expected_signature = hmac.new(
        settings.NOWPAYMENTS_IPN_SECRET.encode(),
        payload,
        hashlib.sha512
    ).hexdigest()

    if signature != expected_signature:
        return JsonResponse({"error": "Invalid signature"}, status=400)

    # Parse webhook data
    data = json.loads(payload)

    payment_status = data.get('payment_status')
    order_id = data.get('order_id')

    if payment_status == 'finished':
        print(f"✅ Payment finished: {order_id}")
        # Process successful payment
        process_crypto_payment(data)

    elif payment_status == 'failed':
        print(f"❌ Payment failed: {order_id}")
        # Handle failed payment
        handle_failed_crypto_payment(data)

    return JsonResponse({"status": "ok"})
```

### Complete Workflow

```python
# 1. Start Django with ngrok
# $ python manage.py runserver_ngrok

# 2. Create crypto payment
from services.nowpayments_service import NowPaymentsService

service = NowPaymentsService()
payment = service.create_payment(amount=100.0, currency="BTC")

print(f"Payment ID: {payment['payment_id']}")
print(f"Payment URL: {payment['pay_address']}")
print(f"Webhook URL: {payment['ipn_callback_url']}")
# Webhook URL: https://abc123.ngrok.io/api/webhooks/nowpayments/

# 3. Customer pays with crypto
# 4. NowPayments sends IPN to your local server via ngrok!
```

---

## Telegram Bot Webhooks

### Basic Setup

```python
# bots/telegram_bot.py
from django_cfg.modules.django_ngrok import get_webhook_url, is_tunnel_active
from telegram import Bot, Update
from telegram.ext import Dispatcher
from django.conf import settings

class TelegramBotService:
    def __init__(self, token: str = None):
        self.token = token or settings.TELEGRAM_BOT_TOKEN
        self.bot = Bot(token=self.token)
        self.webhook_url = get_webhook_url("/api/webhooks/telegram/")

    def setup_webhook(self):
        """Setup webhook for Telegram bot."""
        if not is_tunnel_active():
            print("⚠️ Ngrok tunnel is not active!")
            return False

        # Set webhook to ngrok URL
        success = self.bot.set_webhook(url=self.webhook_url)

        if success:
            print(f"✅ Telegram webhook set to: {self.webhook_url}")
        else:
            print("❌ Failed to set webhook")

        return success

    def remove_webhook(self):
        """Remove webhook."""
        self.bot.delete_webhook()
        print("✅ Webhook removed")

    def get_webhook_info(self):
        """Get current webhook info."""
        info = self.bot.get_webhook_info()
        return {
            "url": info.url,
            "has_custom_certificate": info.has_custom_certificate,
            "pending_update_count": info.pending_update_count,
        }


# views.py
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from telegram import Update, Bot
import json

@csrf_exempt
def telegram_webhook(request):
    """Handle Telegram updates through ngrok."""
    bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)

    # Parse update
    update = Update.de_json(json.loads(request.body), bot)

    # Process message
    if update.message:
        chat_id = update.message.chat_id
        text = update.message.text

        # Echo message back
        bot.send_message(
            chat_id=chat_id,
            text=f"You said: {text}"
        )

    # Process callback query
    elif update.callback_query:
        callback_query = update.callback_query
        callback_query.answer()

        bot.send_message(
            chat_id=callback_query.message.chat_id,
            text=f"Button clicked: {callback_query.data}"
        )

    return JsonResponse({"ok": True})
```

### Complete Workflow

```python
# 1. Start Django with ngrok
# $ python manage.py runserver_ngrok
# ✅ Ngrok tunnel ready: https://abc123.ngrok.io

# 2. Setup Telegram webhook
from bots.telegram_bot import TelegramBotService

bot_service = TelegramBotService()
bot_service.setup_webhook()
# ✅ Telegram webhook set to: https://abc123.ngrok.io/api/webhooks/telegram/

# 3. Check webhook status
info = bot_service.get_webhook_info()
print(info)
# {'url': 'https://abc123.ngrok.io/api/webhooks/telegram/', ...}

# 4. Send message to bot
# Bot receives update via ngrok and responds!
```

---

## Practical Example 1: Development Workflow with Stripe

Complete development workflow for Stripe integration:

```python
# 1. Configure ngrok in config.py
from django_cfg import DjangoConfig, NgrokConfig

class MyConfig(DjangoConfig):
    ngrok: NgrokConfig = NgrokConfig(enabled=True)

config = MyConfig()

# 2. Start server with ngrok
# $ python manage.py runserver_ngrok
# ✅ Ngrok tunnel ready: https://abc123.ngrok.io

# 3. Create payment in Django view
from django.http import JsonResponse
from django_cfg.modules.django_ngrok import get_webhook_url
import stripe

def create_payment_view(request):
    # Get webhook URL automatically
    webhook_url = get_webhook_url("/api/webhooks/stripe/")

    # Create Stripe payment intent
    intent = stripe.PaymentIntent.create(
        amount=1000,
        currency="usd",
        metadata={"webhook_url": webhook_url}
    )

    return JsonResponse({
        "client_secret": intent.client_secret,
        "webhook_url": webhook_url
    })

# 4. Configure webhook in Stripe Dashboard
# URL: https://abc123.ngrok.io/api/webhooks/stripe/
# Events: payment_intent.succeeded, payment_intent.payment_failed

# 5. Test payment locally
# Stripe will send webhook to your local server via ngrok!

# 6. Handle webhook
@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']

    event = stripe.Webhook.construct_event(
        payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
    )

    if event['type'] == 'payment_intent.succeeded':
        print("✅ Payment successful!")
        # Your business logic here

    return JsonResponse({"status": "success"})
```

---

## Practical Example 2: Testing Crypto Payments Locally

Complete workflow for testing crypto payments:

```python
# services/payment_service.py
from django_cfg.modules.django_ngrok import get_webhook_url, is_tunnel_active
import requests
from django.conf import settings

class CryptoPaymentService:
    def create_crypto_invoice(self, amount_usd: float):
        """Create crypto payment invoice with local webhook testing."""

        # Ensure ngrok is active
        if not is_tunnel_active():
            raise RuntimeError("Ngrok tunnel is not active! Run: python manage.py runserver_ngrok")

        # Get ngrok URL for webhook
        ipn_url = get_webhook_url("/api/payments/crypto-webhook/")

        # Create invoice in NowPayments
        response = requests.post(
            "https://api.nowpayments.io/v1/invoice",
            headers={"x-api-key": settings.NOWPAYMENTS_API_KEY},
            json={
                "price_amount": amount_usd,
                "price_currency": "usd",
                "ipn_callback_url": ipn_url,  # Ngrok URL!
                "success_url": f"{ipn_url}success/",
                "cancel_url": f"{ipn_url}cancel/",
            }
        )

        invoice = response.json()

        # Log for testing
        print(f"Invoice created: {invoice['id']}")
        print(f"Payment URL: {invoice['invoice_url']}")
        print(f"Webhook URL: {ipn_url}")

        return invoice

# Usage:
# $ python manage.py runserver_ngrok
# ✅ Ngrok tunnel ready: https://abc123.ngrok.io
#
# >>> service = CryptoPaymentService()
# >>> invoice = service.create_crypto_invoice(100.0)
# Invoice created: INV123
# Payment URL: https://nowpayments.io/payment/?iid=INV123
# Webhook URL: https://abc123.ngrok.io/api/payments/crypto-webhook/
#
# Customer pays → NowPayments sends webhook → Your local server receives it!
```

---

## Practical Example 3: Telegram Bot Development

Complete Telegram bot development workflow:

```python
# management/commands/setup_telegram_bot.py
from django.core.management.base import BaseCommand
from django_cfg.modules.django_ngrok import get_webhook_url, is_tunnel_active
from telegram import Bot
from django.conf import settings

class Command(BaseCommand):
    help = "Setup Telegram bot webhook"

    def handle(self, *args, **options):
        # Check ngrok status
        if not is_tunnel_active():
            self.stdout.write(
                self.style.ERROR("❌ Ngrok tunnel is not active!")
            )
            self.stdout.write("Run: python manage.py runserver_ngrok")
            return

        # Get webhook URL
        webhook_url = get_webhook_url("/api/webhooks/telegram/")

        # Setup Telegram webhook
        bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)
        success = bot.set_webhook(url=webhook_url)

        if success:
            self.stdout.write(
                self.style.SUCCESS(f"✅ Webhook set to: {webhook_url}")
            )

            # Get webhook info
            info = bot.get_webhook_info()
            self.stdout.write(f"Pending updates: {info.pending_update_count}")
        else:
            self.stdout.write(
                self.style.ERROR("❌ Failed to set webhook")
            )

# Usage:
# $ python manage.py runserver_ngrok
# ✅ Ngrok tunnel ready: https://abc123.ngrok.io
#
# $ python manage.py setup_telegram_bot
# ✅ Webhook set to: https://abc123.ngrok.io/api/webhooks/telegram/
# Pending updates: 0
#
# Now Telegram bot works locally via ngrok!
```

---

## Testing Webhooks

### Using Stripe CLI (Alternative)

```bash
# Terminal 1: Start Django with ngrok
python manage.py runserver_ngrok

# Terminal 2: Test webhook manually with Stripe CLI
stripe trigger payment_intent.succeeded --webhook-endpoint https://abc123.ngrok.io/api/webhooks/stripe/
```

### Using curl

```bash
# Test webhook manually
curl -X POST https://abc123.ngrok.io/api/webhooks/test/ \
  -H "Content-Type: application/json" \
  -d '{"event": "test", "data": {"amount": 1000}}'
```

### Monitoring Webhooks

```python
# Add logging to webhook handlers
import logging

logger = logging.getLogger(__name__)

@csrf_exempt
def webhook_handler(request):
    # Log incoming webhook
    logger.info(f"Webhook received from {request.META.get('REMOTE_ADDR')}")
    logger.debug(f"Headers: {request.META}")
    logger.debug(f"Payload: {request.body.decode()}")

    # Process webhook
    # ...

    return JsonResponse({"status": "ok"})
```

---

## Next Steps

- **[Payments Panel](./payments-panel)** - View webhook URLs in admin panel
- **[Troubleshooting](./troubleshooting)** - Debug webhook issues
- **[Configuration](./configuration)** - Advanced ngrok configuration

## See Also

### Ngrok Integration

**Core Documentation:**
- [**Ngrok Overview**](./overview) - Ngrok integration introduction
- [**Configuration Guide**](./configuration) - Complete ngrok configuration
- [**Implementation Guide**](./implementation) - Getting tunnel URLs and helpers
- [**Payments Panel**](./payments-panel) - View webhook URLs in admin
- [**Troubleshooting**](./troubleshooting) - Debug webhook issues

### Payment & Webhook Integration

**Payment Systems:**
- [**Payments App**](/features/built-in-apps/payments/overview) - Built-in payment features
- [**Payments Configuration**](/features/built-in-apps/payments/configuration) - Payment provider setup
- [**Payment Examples**](/features/built-in-apps/payments/examples) - Real payment flows

**Related Integrations:**
- [**Dramatiq Integration**](/features/integrations/dramatiq/overview) - Process webhooks async
- [**Background Tasks**](/features/built-in-apps/operations/tasks) - Async webhook processing
- [**Integrations Overview**](/features/integrations/overview) - All integrations

### Configuration & Setup

**Getting Started:**
- [**Installation**](/getting-started/installation) - Install Django-CFG with ngrok
- [**Configuration Guide**](/getting-started/configuration) - Configure ngrok integration
- [**First Project**](/getting-started/first-project) - Quick start tutorial

**Advanced:**
- [**Environment Variables**](/fundamentals/configuration/environment) - Ngrok auth token setup
- [**Environment Detection**](/fundamentals/configuration/environment) - Dev-only ngrok
- [**Type-Safe Configuration**](/fundamentals/core/type-safety) - Ngrok config validation

### Development & Tools

**CLI & Management:**
- [**CLI Tools**](/cli/introduction) - Ngrok management commands
- [**Development Commands**](/cli/commands/development) - runserver_ngrok command
- [**Troubleshooting**](/guides/troubleshooting) - Common webhook issues

**Examples:**
- [**Sample Project**](/guides/sample-project/overview) - Production webhook example
- [**Examples Guide**](/guides/examples) - More webhook patterns
