---
title: Telegram Bot Overview
description: Django-CFG overview feature guide. Production-ready telegram bot overview with built-in validation, type safety, and seamless Django integration.
sidebar_label: Overview & Philosophy
sidebar_position: 1
keywords:
  - django-cfg overview
  - django overview
  - overview django-cfg
---

# Telegram Module

Django-CFG includes a **comprehensive Telegram integration** that provides bot functionality, notifications, webhooks, media handling, and advanced messaging capabilities for your Django applications.

## Overview

The Django Telegram module provides:
- **Bot Integration** - Complete Telegram bot functionality
- **Notification System** - Send alerts and notifications via Telegram
- **Webhook Support** - Handle incoming Telegram webhooks
- **Media Handling** - Send photos, documents, and other media
- **Message Templates** - Rich message formatting and templates
- **User Management** - Track and manage Telegram users

## Quick Start

### Configuration

```python
# config.py
from django_cfg import DjangoConfig

class MyConfig(DjangoConfig):
    # Telegram bot configuration
    telegram_bot_token: str = "YOUR_BOT_TOKEN"
    telegram_webhook_url: str = "https://yoursite.com/telegram/webhook/"
    telegram_webhook_secret: str = "your-webhook-secret"
    
    # Notification settings
    telegram_admin_chat_id: str = "123456789"
    telegram_error_notifications: bool = True
    telegram_debug_mode: bool = False
```

### Basic Usage

```python
from django_cfg.modules.django_telegram import DjangoTelegram, send_telegram_message

# Initialize Telegram service
telegram = DjangoTelegram()

# Send simple message
send_telegram_message(
    chat_id="123456789",
    text="Hello from Django-CFG!"
)

# Send formatted message
send_telegram_message(
    chat_id="123456789",
    text="*Bold text* and _italic text_",
    parse_mode="Markdown"
)

# Send message with keyboard
from django_cfg.modules.django_telegram import InlineKeyboard

keyboard = InlineKeyboard()
keyboard.add_button("Visit Website", url="https://yoursite.com")
keyboard.add_button("Contact Support", callback_data="support")

send_telegram_message(
    chat_id="123456789",
    text="Choose an option:",
    reply_markup=keyboard.get_markup()
)
```

## Bot Functionality

### Bot Commands

```python
from django_cfg.modules.django_telegram import TelegramBot, command_handler

class MyTelegramBot(TelegramBot):
    """Custom Telegram bot with commands"""
    
    @command_handler('start')
    def start_command(self, message):
        """Handle /start command"""
        user_id = message.from_user.id
        username = message.from_user.username or "User"
        
        welcome_text = f"""
🎉 Welcome to our bot, {username}!

Available commands:
/help - Show this help message
/status - Check system status
/subscribe - Subscribe to notifications
/unsubscribe - Unsubscribe from notifications
        """
        
        self.send_message(
            chat_id=user_id,
            text=welcome_text
        )
    
    @command_handler('help')
    def help_command(self, message):
        """Handle /help command"""
        help_text = """
🤖 *Bot Commands:*

/start - Start using the bot
/help - Show this help message
/status - Check system status
/subscribe - Get notifications
/unsubscribe - Stop notifications
/feedback <message> - Send feedback

*Need more help?* Contact @admin
        """
        
        self.send_message(
            chat_id=message.from_user.id,
            text=help_text,
            parse_mode="Markdown"
        )
    
    @command_handler('status')
    def status_command(self, message):
        """Handle /status command"""
        from django_cfg.modules.django_health import get_health_status
        
        health = get_health_status()
        status_emoji = "✅" if health['status'] == 'healthy' else "❌"
        
        status_text = f"""
{status_emoji} *System Status: {health['status'].upper()}*

🗄️ Database: {'✅' if health['checks']['database']['status'] == 'ok' else '❌'}
💾 Cache: {'✅' if health['checks']['cache']['status'] == 'ok' else '❌'}
🖥️ System: {'✅' if health['checks']['system']['status'] == 'ok' else '❌'}

_Last updated: {health['timestamp']}_
        """
        
        self.send_message(
            chat_id=message.from_user.id,
            text=status_text,
            parse_mode="Markdown"
        )

# Register bot
bot = MyTelegramBot()
bot.start_polling()
```

### Callback Handlers

```python
from django_cfg.modules.django_telegram import callback_handler

class MyTelegramBot(TelegramBot):
    
    @callback_handler('support')
    def handle_support_callback(self, callback_query):
        """Handle support button callback"""
        user_id = callback_query.from_user.id
        
        # Answer callback query
        self.answer_callback_query(
            callback_query.id,
            text="Opening support chat..."
        )
        
        # Send support message
        support_text = """
📞 *Support Options:*

• Email: support@yoursite.com
• Live Chat: Available 9 AM - 6 PM
• Phone: +1 (555) 123-4567

What can we help you with today?
        """
        
        keyboard = InlineKeyboard()
        keyboard.add_button("Technical Issue", callback_data="tech_support")
        keyboard.add_button("Billing Question", callback_data="billing_support")
        keyboard.add_button("General Inquiry", callback_data="general_support")
        
        self.send_message(
            chat_id=user_id,
            text=support_text,
            parse_mode="Markdown",
            reply_markup=keyboard.get_markup()
        )
    
    @callback_handler('tech_support')
    def handle_tech_support(self, callback_query):
        """Handle technical support callback"""
        user_id = callback_query.from_user.id
        
        # Create support ticket
        from myapp.models import SupportTicket
        ticket = SupportTicket.objects.create(
            user_telegram_id=user_id,
            category='technical',
            status='open'
        )
        
        self.send_message(
            chat_id=user_id,
            text=f"🎫 Support ticket #{ticket.id} created!\n\nPlease describe your technical issue and our team will respond shortly."
        )
```

## 🔔 Notification System

### Alert Notifications

```python
from django_cfg.modules.django_telegram import TelegramNotifier

class SystemNotifier:
    def __init__(self):
        self.notifier = TelegramNotifier()
    
    def send_error_alert(self, error_message, traceback=None):
        """Send error alert to admin"""
        alert_text = f"""
🚨 *System Error Alert*

*Error:* {error_message}
*Time:* {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
*Server:* {socket.gethostname()}

{f'*Traceback:*\n```\n{traceback}\n```' if traceback else ''}
        """
        
        self.notifier.send_to_admin(
            text=alert_text,
            parse_mode="Markdown"
        )
    
    def send_user_notification(self, user_id, notification_type, data):
        """Send notification to specific user"""
        templates = {
            'order_confirmed': """
✅ *Order Confirmed!*

Order #: {order_id}
Total: ${total}
Estimated delivery: {delivery_date}

Track your order: /track_{order_id}
            """,
            'payment_received': """
💰 *Payment Received*

Amount: ${amount}
Method: {payment_method}
Transaction ID: {transaction_id}

Thank you for your payment!
            """,
            'system_maintenance': """
🔧 *Scheduled Maintenance*

Our system will be under maintenance:
Start: {start_time}
Duration: {duration}

We apologize for any inconvenience.
            """
        }
        
        template = templates.get(notification_type)
        if template:
            message = template.format(**data)
            self.notifier.send_message(
                chat_id=user_id,
                text=message,
                parse_mode="Markdown"
            )

# Usage
notifier = SystemNotifier()

# Send error alert
try:
    # Some operation that might fail
    risky_operation()
except Exception as e:
    notifier.send_error_alert(str(e), traceback.format_exc())

# Send user notification
notifier.send_user_notification(
    user_id="123456789",
    notification_type="order_confirmed",
    data={
        'order_id': 'ORD-12345',
        'total': '99.99',
        'delivery_date': '2023-12-05'
    }
)
```

### Bulk Notifications

```python
from django_cfg.modules.django_telegram import BulkTelegramSender

class NewsletterSender:
    def __init__(self):
        self.sender = BulkTelegramSender(
            batch_size=30,  # Telegram rate limit: 30 messages/second
            delay_between_batches=1.0
        )
    
    def send_newsletter(self, subscribers, content):
        """Send newsletter to all subscribers"""
        messages = []
        
        for subscriber in subscribers:
            message = {
                'chat_id': subscriber.telegram_chat_id,
                'text': content.format(name=subscriber.name),
                'parse_mode': 'Markdown',
                'disable_web_page_preview': True
            }
            messages.append(message)
        
        # Send in batches
        result = self.sender.send_bulk(messages)
        
        return {
            'total_sent': result['successful'],
            'failed': result['failed'],
            'total_time': result['total_time']
        }
    
    def send_promotional_message(self, target_users, promo_data):
        """Send promotional message with media"""
        messages = []
        
        for user in target_users:
            # Create personalized message
            promo_text = f"""
🎉 *Special Offer for {user.name}!*

{promo_data['title']}

💰 Save {promo_data['discount']}% on your next purchase!
⏰ Valid until: {promo_data['expires']}

Use code: `{promo_data['code']}`
            """
            
            keyboard = InlineKeyboard()
            keyboard.add_button("Shop Now", url=promo_data['shop_url'])
            keyboard.add_button("View Details", callback_data=f"promo_{promo_data['id']}")
            
            message = {
                'chat_id': user.telegram_chat_id,
                'photo': promo_data['image_url'],
                'caption': promo_text,
                'parse_mode': 'Markdown',
                'reply_markup': keyboard.get_markup()
            }
            messages.append(message)
        
        return self.sender.send_bulk_media(messages)

# Usage
newsletter = NewsletterSender()

# Send newsletter
subscribers = TelegramSubscriber.objects.filter(active=True)
newsletter_content = """
📰 *Weekly Newsletter*

Hello {name}!

This week's highlights:
• New feature: Dark mode
• 50% off premium plans
• Upcoming webinar on Dec 15

Stay tuned for more updates!
"""

result = newsletter.send_newsletter(subscribers, newsletter_content)
print(f"Newsletter sent to {result['total_sent']} subscribers")
```

## 📸 Media Handling

### Photo and Document Sending

```python
from django_cfg.modules.django_telegram import TelegramMediaSender

class MediaSender:
    def __init__(self):
        self.sender = TelegramMediaSender()
    
    def send_report_with_chart(self, chat_id, report_data):
        """Send report with generated chart"""
        import matplotlib.pyplot as plt
        import io
        
        # Generate chart
        fig, ax = plt.subplots()
        ax.plot(report_data['dates'], report_data['values'])
        ax.set_title('Monthly Sales Report')
        
        # Save to bytes
        img_buffer = io.BytesIO()
        plt.savefig(img_buffer, format='png', dpi=300, bbox_inches='tight')
        img_buffer.seek(0)
        
        # Send photo with caption
        caption = f"""
📊 *Monthly Sales Report*

Total Sales: ${report_data['total']:,.2f}
Growth: {report_data['growth']:+.1f}%
Best Day: {report_data['best_day']}

Generated on {datetime.now().strftime('%Y-%m-%d')}
        """
        
        self.sender.send_photo(
            chat_id=chat_id,
            photo=img_buffer,
            caption=caption,
            parse_mode="Markdown"
        )
    
    def send_document_with_preview(self, chat_id, file_path, description):
        """Send document with preview"""
        with open(file_path, 'rb') as document:
            self.sender.send_document(
                chat_id=chat_id,
                document=document,
                caption=f"📄 {description}",
                filename=os.path.basename(file_path)
            )
    
    def send_media_group(self, chat_id, media_files, caption):
        """Send multiple media files as album"""
        media_group = []
        
        for i, file_path in enumerate(media_files):
            with open(file_path, 'rb') as media:
                media_type = 'photo' if file_path.lower().endswith(('.jpg', '.png', '.gif')) else 'document'
                
                media_item = {
                    'type': media_type,
                    'media': media,
                    'caption': caption if i == 0 else None  # Caption only on first item
                }
                media_group.append(media_item)
        
        self.sender.send_media_group(
            chat_id=chat_id,
            media=media_group
        )

# Usage
media_sender = MediaSender()

# Send chart
report_data = {
    'dates': ['2023-11-01', '2023-11-02', '2023-11-03'],
    'values': [1000, 1200, 1100],
    'total': 3300.00,
    'growth': 15.5,
    'best_day': '2023-11-02'
}

media_sender.send_report_with_chart("123456789", report_data)

# Send document
media_sender.send_document_with_preview(
    chat_id="123456789",
    file_path="/path/to/report.pdf",
    description="Monthly Financial Report - November 2023"
)
```

## Webhook Integration

### Webhook Handler

```python
from django_cfg.modules.django_telegram import TelegramWebhookView
from django.urls import path

class CustomTelegramWebhook(TelegramWebhookView):
    """Custom webhook handler"""
    
    def handle_message(self, update):
        """Handle incoming messages"""
        message = update.message
        user_id = message.from_user.id
        text = message.text
        
        # Log message
        self.log_message(user_id, text)
        
        # Process commands
        if text.startswith('/'):
            self.handle_command(message)
        else:
            self.handle_text_message(message)
    
    def handle_callback_query(self, update):
        """Handle button callbacks"""
        callback = update.callback_query
        data = callback.data
        user_id = callback.from_user.id
        
        # Process callback
        if data.startswith('support_'):
            self.handle_support_callback(callback)
        elif data.startswith('order_'):
            self.handle_order_callback(callback)
        else:
            self.handle_generic_callback(callback)
    
    def handle_inline_query(self, update):
        """Handle inline queries"""
        query = update.inline_query
        search_term = query.query
        
        # Search results
        results = self.search_content(search_term)
        
        # Send results
        self.answer_inline_query(
            inline_query_id=query.id,
            results=results,
            cache_time=300
        )
    
    def log_message(self, user_id, text):
        """Log incoming message"""
        from myapp.models import TelegramMessage
        
        TelegramMessage.objects.create(
            user_telegram_id=user_id,
            message_text=text,
            timestamp=timezone.now()
        )

# URL configuration
urlpatterns = [
    path('telegram/webhook/', CustomTelegramWebhook.as_view(), name='telegram_webhook'),
]
```

### Webhook Security

```python
from django_cfg.modules.django_telegram import verify_telegram_webhook

class SecureTelegramWebhook(TelegramWebhookView):
    """Secure webhook with signature verification"""
    
    def dispatch(self, request, *args, **kwargs):
        """Verify webhook signature"""
        if not verify_telegram_webhook(request, self.webhook_secret):
            return HttpResponseForbidden("Invalid signature")
        
        return super().dispatch(request, *args, **kwargs)
    
    def post(self, request, *args, **kwargs):
        """Handle webhook POST request"""
        try:
            # Rate limiting
            if not self.check_rate_limit(request):
                return HttpResponseTooManyRequests("Rate limit exceeded")
            
            # Process update
            return super().post(request, *args, **kwargs)
            
        except Exception as e:
            # Log error
            logger.error(f"Webhook error: {e}", exc_info=True)
            
            # Send error notification
            self.send_error_notification(str(e))
            
            return HttpResponseServerError("Internal error")
    
    def check_rate_limit(self, request):
        """Check rate limiting"""
        client_ip = self.get_client_ip(request)
        cache_key = f"telegram_webhook_rate_{client_ip}"
        
        current_requests = cache.get(cache_key, 0)
        if current_requests >= 100:  # 100 requests per minute
            return False
        
        cache.set(cache_key, current_requests + 1, 60)
        return True
```

## 🧪 Testing Telegram Integration

### Unit Tests

```python
from django.test import TestCase
from unittest.mock import patch, MagicMock
from django_cfg.modules.django_telegram import DjangoTelegram, send_telegram_message

class TelegramIntegrationTest(TestCase):
    def setUp(self):
        self.telegram = DjangoTelegram()
        self.test_chat_id = "123456789"
    
    @patch('django_cfg.modules.django_telegram.telebot.TeleBot')
    def test_send_message(self, mock_bot):
        """Test sending Telegram message"""
        mock_bot_instance = MagicMock()
        mock_bot.return_value = mock_bot_instance
        
        # Send message
        send_telegram_message(
            chat_id=self.test_chat_id,
            text="Test message"
        )
        
        # Verify bot was called
        mock_bot_instance.send_message.assert_called_once_with(
            chat_id=self.test_chat_id,
            text="Test message",
            parse_mode=None,
            reply_markup=None
        )
    
    @patch('django_cfg.modules.django_telegram.telebot.TeleBot')
    def test_send_photo(self, mock_bot):
        """Test sending photo"""
        mock_bot_instance = MagicMock()
        mock_bot.return_value = mock_bot_instance
        
        # Mock photo file
        photo_data = b"fake_photo_data"
        
        self.telegram.send_photo(
            chat_id=self.test_chat_id,
            photo=photo_data,
            caption="Test photo"
        )
        
        mock_bot_instance.send_photo.assert_called_once()
    
    def test_webhook_signature_verification(self):
        """Test webhook signature verification"""
        from django_cfg.modules.django_telegram import verify_telegram_webhook
        from django.test import RequestFactory
        
        factory = RequestFactory()
        
        # Valid signature
        request = factory.post('/webhook/', data='{"test": "data"}', content_type='application/json')
        request.META['HTTP_X_TELEGRAM_BOT_API_SECRET_TOKEN'] = 'valid_secret'
        
        # This would normally verify against actual secret
        # For testing, we mock the verification
        with patch('django_cfg.modules.django_telegram.verify_signature') as mock_verify:
            mock_verify.return_value = True
            self.assertTrue(verify_telegram_webhook(request, 'valid_secret'))
```

## Related Documentation

- [**Twilio Integration**](/features/integrations/twilio) - SMS and voice integration
- [**Email Module**](/features/modules/email/overview) - Email notifications
- [**Webhook Patterns**](/features/integrations/patterns) - Webhook best practices
- [**Configuration Guide**](/fundamentals/configuration) - Telegram configuration

The Telegram module provides comprehensive bot and messaging functionality for your Django applications! 🤖

TAGS: telegram, bot, notifications, webhooks, media, messaging
DEPENDS_ON: [configuration, webhooks, notifications]
USED_BY: [alerts, notifications, customer-support, automation]
