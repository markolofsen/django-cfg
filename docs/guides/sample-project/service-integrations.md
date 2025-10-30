---
title: Service Integrations
description: Integration with external services - Twilio, SendGrid, and Telegram in Django-CFG
sidebar_label: Service Integrations
sidebar_position: 9
---

# Service Integrations

The Django-CFG sample project demonstrates integration with popular external services. This guide covers setup and usage of Twilio (SMS), SendGrid (email), and Telegram (notifications).

## Service Overview

The sample project integrates:
- **Twilio** - SMS, WhatsApp, and voice calls
- **SendGrid** - Professional email delivery
- **Telegram** - Real-time notifications and bot commands

## Twilio Integration

### Configuration

Configure Twilio in `api/config.py`:

```python
from django_cfg import TwilioConfig

twilio: TwilioConfig = TwilioConfig(
    account_sid=env.twilio.account_sid,
    auth_token=env.twilio.auth_token,
    verify_service_sid=env.twilio.verify_service_sid,
    phone_number=env.twilio.phone_number
)
```

Environment configuration:

```yaml
# api/environment/config.prod.yaml
twilio:
  account_sid: "<from-yaml-config>"
  auth_token: "<from-yaml-config>"
  verify_service_sid: "<from-yaml-config>"
  phone_number: "+1234567890"
```

See [Configuration](./configuration) for environment setup details.

### SMS Messages

Send SMS messages:

```python
from django_cfg.modules.django_twilio.service import UnifiedOTPService

twilio = UnifiedOTPService()

# Send SMS OTP
def send_sms_otp(phone_number, otp_code):
    """Send OTP code via SMS."""
    message = twilio.send_sms(
        to=phone_number,
        body=f"Your verification code is: {otp_code}"
    )
    return message.sid

# Send custom SMS
def send_order_notification(phone_number, order_id):
    """Send order notification via SMS."""
    message = twilio.send_sms(
        to=phone_number,
        body=f"Your order #{order_id} has been confirmed!"
    )
    return message.sid
```

### WhatsApp Messages

Send WhatsApp messages:

```python
from django_cfg.modules.django_twilio.service import UnifiedOTPService

twilio = UnifiedOTPService()

# Send WhatsApp message
def send_whatsapp_notification(phone_number, message):
    """Send notification via WhatsApp."""
    response = twilio.send_whatsapp(
        to=f"whatsapp:{phone_number}",
        body=message
    )
    return response.sid

# Send order confirmation
def send_whatsapp_order_confirmation(phone_number, order):
    """Send order confirmation via WhatsApp."""
    message = f"""
Hello {order.user.get_full_name()},

Your order #{order.id} has been confirmed!

Total: ${order.total}
Items: {order.items.count()}

Track your order: https://myapp.com/orders/{order.id}

Thank you for shopping with us!
    """

    return send_whatsapp_notification(phone_number, message.strip())
```

### Voice Calls

Make automated voice calls:

```python
from django_cfg.modules.django_twilio.service import UnifiedOTPService

twilio = UnifiedOTPService()

# Make alert call
def make_alert_call(phone_number, alert_message):
    """Make voice call for critical alerts."""
    call = twilio.make_call(
        to=phone_number,
        twiml_url=f"https://myapp.com/voice/alert?message={alert_message}"
    )
    return call.sid

# TwiML endpoint for voice call
from django.http import HttpResponse
from twilio.twiml.voice_response import VoiceResponse

def voice_alert_view(request):
    """Generate TwiML for voice alert."""
    message = request.GET.get('message', 'Alert')

    response = VoiceResponse()
    response.say(
        f"This is an important alert: {message}",
        voice='alice',
        language='en-US'
    )

    return HttpResponse(str(response), content_type='text/xml')
```

### Twilio Verify Service

Use Twilio Verify for OTP management:

```python
from django_cfg.modules.django_twilio.service import UnifiedOTPService

twilio = UnifiedOTPService()

# Send verification code
def send_verify_code(phone_number):
    """Send verification code via Twilio Verify."""
    verification = twilio.send_verify_code(
        to=phone_number,
        channel='sms'  # or 'call'
    )
    return verification.sid

# Check verification code
def check_verify_code(phone_number, code):
    """Verify code entered by user."""
    verification_check = twilio.check_verify_code(
        to=phone_number,
        code=code
    )
    return verification_check.status == 'approved'
```

## SendGrid Integration

### Configuration

Configure SendGrid in `api/config.py`:

```python
from django_cfg import EmailConfig

email: EmailConfig = EmailConfig(
    backend="sendgrid" if env.is_prod else "console",
    sendgrid_api_key=env.email.sendgrid_api_key,
    from_email="noreply@djangocfg.com",
    from_name="Django-CFG Sample"
)
```

Environment configuration:

```yaml
# api/environment/config.prod.yaml
email:
  sendgrid_api_key: "<from-yaml-config>"
  from_email: "noreply@myapp.com"
  from_name: "My App"
```

### Simple Email

Send basic emails:

```python
from django_cfg import DjangoEmailService

email = DjangoEmailService()

# Send simple email
def send_simple_email(to_email, subject, message):
    """Send simple text email."""
    email.send_simple(
        subject=subject,
        message=message,
        recipient_list=[to_email]
    )
```

### Template-Based Emails

Send emails using HTML templates:

```python
from django_cfg import DjangoEmailService

email = DjangoEmailService()

# Send welcome email
def send_welcome_email(user):
    """Send welcome email to new user."""
    email.send_template(
        template_name="emails/welcome.html",
        context={
            "user_name": user.get_full_name() or user.email,
            "login_url": "https://myapp.com/login"
        },
        recipient_list=[user.email],
        subject="Welcome to Django-CFG Sample!"
    )

# Send order confirmation
def send_order_confirmation(order):
    """Send order confirmation email."""
    email.send_template(
        template_name="emails/order_confirmation.html",
        context={
            "order": order,
            "customer_name": order.user.get_full_name(),
            "order_items": order.items.all(),
            "total_amount": order.total
        },
        recipient_list=[order.user.email],
        subject=f"Order Confirmation #{order.id}"
    )
```

### Email Templates

Create HTML email templates:

```html
<!-- templates/emails/welcome.html -->
<!DOCTYPE html>
<html>
<head>
    <style>
        body {
            font-family: Arial, sans-serif;
            line-height: 1.6;
            color: #333;
        }
        .container {
            max-width: 600px;
            margin: 0 auto;
            padding: 20px;
        }
        .button {
            display: inline-block;
            padding: 12px 24px;
            background-color: #4F46E5;
            color: white;
            text-decoration: none;
            border-radius: 5px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Welcome to Django-CFG Sample!</h1>
        <p>Hi {{ user_name }},</p>
        <p>Thank you for joining Django-CFG Sample. We're excited to have you on board!</p>
        <p>
            <a href="{{ login_url }}" class="button">Get Started</a>
        </p>
        <p>If you have any questions, feel free to reply to this email.</p>
        <p>Best regards,<br>The Django-CFG Team</p>
    </div>
</body>
</html>
```

```html
<!-- templates/emails/order_confirmation.html -->
<!DOCTYPE html>
<html>
<head>
    <style>
        body {
            font-family: Arial, sans-serif;
            color: #333;
        }
        .container {
            max-width: 600px;
            margin: 0 auto;
            padding: 20px;
        }
        .order-details {
            background-color: #f5f5f5;
            padding: 15px;
            border-radius: 5px;
        }
        .item {
            padding: 10px 0;
            border-bottom: 1px solid #ddd;
        }
        .total {
            font-size: 18px;
            font-weight: bold;
            margin-top: 15px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Order Confirmation</h1>
        <p>Hi {{ customer_name }},</p>
        <p>Thank you for your order! Here are the details:</p>

        <div class="order-details">
            <h2>Order #{{ order.id }}</h2>
            {% for item in order_items %}
            <div class="item">
                <strong>{{ item.product.name }}</strong><br>
                Quantity: {{ item.quantity }} × ${{ item.price }}
            </div>
            {% endfor %}
            <div class="total">
                Total: ${{ total_amount }}
            </div>
        </div>

        <p>We'll send you another email when your order ships.</p>
        <p>Best regards,<br>The Django-CFG Team</p>
    </div>
</body>
</html>
```

### Bulk Emails

Send bulk emails with SendGrid:

```python
from django_cfg import DjangoEmailService

email = DjangoEmailService()

# Send newsletter
def send_newsletter(subscribers, newsletter_data):
    """Send newsletter to all subscribers."""
    email.send_bulk_sendgrid(
        template_id="d-newsletter-template-id",
        recipients=[
            {"email": sub.email, "name": sub.name}
            for sub in subscribers
        ],
        template_data=newsletter_data
    )

# Send marketing campaign
def send_campaign(users, campaign_data):
    """Send marketing campaign."""
    email.send_bulk_sendgrid(
        template_id="d-campaign-template-id",
        recipients=[
            {
                "email": user.email,
                "name": user.get_full_name(),
                "custom_data": {
                    "user_id": user.id,
                    "discount_code": generate_discount_code(user)
                }
            }
            for user in users
        ],
        template_data=campaign_data
    )
```

## Telegram Integration

### Configuration

Configure Telegram in `api/config.py`:

```python
from django_cfg import TelegramConfig

telegram: TelegramConfig = TelegramConfig(
    bot_token=env.telegram.bot_token,
    chat_id=env.telegram.chat_id,
    enabled=env.is_prod
)
```

Environment configuration:

```yaml
# api/environment/config.prod.yaml
telegram:
  bot_token: "<from-yaml-config>"
  chat_id: "@your_channel"  # or numeric chat ID
```

### Sending Messages

Send messages to Telegram:

```python
from django_cfg import DjangoTelegram

telegram = DjangoTelegram()

# Send simple message
def send_alert(message):
    """Send alert to Telegram channel."""
    telegram.send_message(
        chat_id="@system_alerts",
        text=message
    )

# Send formatted message
def send_system_alert(message, level="info"):
    """Send formatted system alert."""
    emoji = {"info": "ℹ️", "warning": "⚠️", "error": "🚨"}

    telegram.send_message(
        chat_id="@system_alerts",
        text=f"{emoji[level]} *System Alert*\n\n{message}",
        parse_mode="Markdown"
    )
```

### Order Notifications

Send order notifications via Telegram:

```python
from django_cfg import DjangoTelegram

telegram = DjangoTelegram()

# Notify new order
def notify_new_order(order):
    """Send new order notification."""
    message = f"""
🛒 *New Order Received*

Order ID: `{order.id}`
Customer: {order.user.get_full_name()}
Total: ${order.total}
Items: {order.items.count()}

[View Order](https://admin.myapp.com/admin/shop/order/{order.id}/)
    """

    telegram.send_message(
        chat_id="@order_notifications",
        text=message,
        parse_mode="Markdown"
    )

# Notify order status change
def notify_order_status(order, old_status, new_status):
    """Notify when order status changes."""
    message = f"""
📦 *Order Status Updated*

Order ID: `{order.id}`
Status: {old_status} → *{new_status}*
Customer: {order.user.email}

[View Order](https://admin.myapp.com/admin/shop/order/{order.id}/)
    """

    telegram.send_message(
        chat_id="@order_notifications",
        text=message,
        parse_mode="Markdown"
    )
```

### Bot Commands

Create interactive bot commands:

```python
from django_cfg import DjangoTelegram

telegram = DjangoTelegram()

# Status command
@telegram.command("status")
def handle_status_command(update, context):
    """Handle /status command."""
    from django.contrib.auth import get_user_model

    User = get_user_model()

    status = f"""
🏥 *System Status*

Database: ✅ Connected
Cache: ✅ Active
Workers: ✅ Running

👥 Users: {User.objects.count()}
📊 Load: Low
    """

    return status

# Stats command
@telegram.command("stats")
def handle_stats_command(update, context):
    """Handle /stats command."""
    from django.contrib.auth import get_user_model
    from apps.shop.models import Order
    from django.db.models import Sum

    User = get_user_model()

    stats = f"""
📊 *Quick Stats*

👥 Users: {User.objects.count()}
🛒 Orders: {Order.objects.count()}
💰 Revenue: ${Order.objects.aggregate(Sum('total'))['total__sum'] or 0}
    """

    return stats

# Orders command
@telegram.command("orders")
def handle_orders_command(update, context):
    """Handle /orders command - show recent orders."""
    from apps.shop.models import Order

    recent_orders = Order.objects.order_by('-created_at')[:5]

    message = "📦 *Recent Orders*\n\n"
    for order in recent_orders:
        message += f"#{order.id} - ${order.total} - {order.status}\n"

    return message
```

## Async Service Usage

### Background Email Sending

Send emails asynchronously:

```python
from arq import ArqRedis
from django_cfg import DjangoEmailService

async def send_welcome_email_async(ctx, user_id):
    """Send welcome email in background."""
    from django.contrib.auth import get_user_model

    User = get_user_model()
    user = User.objects.get(id=user_id)

    email = DjangoEmailService()
    email.send_template(
        template_name="emails/welcome.html",
        context={"user_name": user.get_full_name()},
        recipient_list=[user.email],
        subject="Welcome!"
    )

# Usage
async def handle_user_registration(user):
    """Handle new user registration."""
    redis = await ArqRedis.create()
    await redis.enqueue_job('send_welcome_email_async', user.id)
```

See [Background Tasks](/features/integrations/rearq/overview) for async processing details.

### Background SMS Sending

Send SMS asynchronously:

```python
from arq import ArqRedis
from django_cfg.modules.django_twilio.service import UnifiedOTPService

async def send_sms_async(ctx, phone_number, message):
    """Send SMS in background."""
    twilio = UnifiedOTPService()
    twilio.send_sms(to=phone_number, body=message)

# Usage
async def handle_order_creation(order):
    """Handle new order creation."""
    if order.user.phone:
        redis = await ArqRedis.create()
        await redis.enqueue_job(
            'send_sms_async',
            order.user.phone,
            f"Order #{order.id} confirmed! Total: ${order.total}"
        )
```

## Error Handling

### Graceful Degradation

Handle service failures gracefully:

```python
from django_cfg import DjangoTelegram
import logging

logger = logging.getLogger(__name__)

def notify_error(error_message):
    """Send error notification with fallback."""
    try:
        # Try Telegram first
        telegram = DjangoTelegram()
        telegram.send_message(
            chat_id="@system_alerts",
            text=f"🚨 Error: {error_message}"
        )
    except Exception as e:
        # Fallback to email
        logger.warning(f"Telegram notification failed: {e}")
        try:
            email = DjangoEmailService()
            email.send_simple(
                subject="System Error",
                message=error_message,
                recipient_list=["admin@myapp.com"]
            )
        except Exception as e:
            # Log as last resort
            logger.error(f"All notifications failed: {e}")
```

### Retry Logic

Implement retry logic for transient failures:

```python
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=10)
)
def send_critical_sms(phone_number, message):
    """Send SMS with automatic retries."""
    twilio = UnifiedOTPService()
    return twilio.send_sms(to=phone_number, body=message)
```

## Best Practices

### 1. Use Environment-Specific Configuration

```python
# ✅ Good: Environment-aware
email: EmailConfig = EmailConfig(
    backend="sendgrid" if env.is_prod else "console",
    sendgrid_api_key=env.email.sendgrid_api_key
)

# ❌ Bad: Hard-coded production settings
email: EmailConfig = EmailConfig(
    backend="sendgrid",
    sendgrid_api_key="SG.xxxxx"
)
```

### 2. Template-Based Messages

```python
# ✅ Good: Template-based
email.send_template(
    template_name="emails/welcome.html",
    context={"user": user}
)

# ❌ Bad: Hard-coded messages
email.send_simple(
    message="Welcome! Click here: https://..."
)
```

### 3. Async for Non-Critical Operations

```python
# ✅ Good: Async notification
notify_user.send(user.id)  # Non-blocking

# ❌ Bad: Synchronous notification
send_notification(user.id)  # Blocks request
```

### 4. Handle Service Failures

```python
# ✅ Good: Graceful error handling
try:
    telegram.send_message(chat_id, message)
except Exception as e:
    logger.warning(f"Telegram failed: {e}")
    # Continue without failing

# ❌ Bad: Unhandled failures
telegram.send_message(chat_id, message)  # Crashes on error
```

## Testing Service Integrations

### Mock External Services

Test without calling real services:

```python
from unittest.mock import patch
from django.test import TestCase

class ServiceIntegrationTest(TestCase):
    @patch('django_cfg.DjangoEmailService.send_template')
    def test_send_welcome_email(self, mock_send):
        """Test welcome email sending."""
        send_welcome_email(self.user)

        mock_send.assert_called_once()
        self.assertEqual(
            mock_send.call_args[1]['recipient_list'],
            [self.user.email]
        )
```

## Related Topics

- [Configuration](./configuration) - Service configuration setup
- [Background Tasks](/features/integrations/rearq/overview) - Async service usage
- [Authentication](./authentication) - OTP via SMS/email

External service integrations enhance application capabilities!
