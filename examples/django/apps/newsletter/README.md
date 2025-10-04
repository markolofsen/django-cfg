# 📧 Django CFG Newsletter App

Clean, optimized newsletter and email management system for Django CFG.

## 🎯 Features

- **Newsletter Management**: Create and manage newsletters with campaigns
- **Subscription System**: User subscriptions with email/unsubscribe functionality  
- **Bulk Email Sending**: Send emails to multiple recipients using base template
- **Campaign System**: Draft, send, and track newsletter campaigns
- **Email Logging**: Track all sent emails with status and error handling
- **Management Commands**: CLI tools for testing and management

## 🏗️ Architecture

### Models
- `Newsletter` - Newsletter definitions with auto-subscribe option
- `NewsletterSubscription` - User subscriptions to newsletters
- `NewsletterCampaign` - Email campaigns with content and status tracking
- `EmailLog` - Audit trail of all sent emails

### Custom Managers
- `NewsletterManager` - Active newsletters, auto-subscribe filtering
- `NewsletterSubscriptionManager` - Active subscriptions, newsletter filtering

### API Endpoints (DRF)
```
GET    /newsletters/           - List active newsletters
GET    /newsletters/{id}/      - Newsletter details
POST   /subscribe/             - Subscribe to newsletter
POST   /unsubscribe/           - Unsubscribe from newsletter
GET    /subscriptions/         - User's subscriptions (auth required)
GET    /campaigns/             - List campaigns (auth required)
POST   /campaigns/             - Create campaign (auth required)
GET    /campaigns/{id}/        - Campaign details (auth required)
PUT    /campaigns/{id}/        - Update campaign (auth required)
DELETE /campaigns/{id}/        - Delete campaign (auth required)
POST   /campaigns/send/        - Send campaign (auth required)
POST   /test/                  - Send test email
POST   /bulk/                  - Send bulk email (auth required)
GET    /logs/                  - Email logs (auth required)
```

## 🚀 Usage

### Management Command
```bash
# Test newsletter sending
python manage.py test_newsletter --email test@example.com --create-subscription

# Use existing newsletter
python manage.py test_newsletter --email test@example.com --newsletter-id 1

# Use existing campaign
python manage.py test_newsletter --email test@example.com --campaign-id 1
```

### API Examples
```python
# Subscribe to newsletter
POST /newsletter/subscribe/
{
    "newsletter_id": 1,
    "email": "user@example.com"
}

# Send bulk email
POST /newsletter/bulk/
{
    "recipients": ["user1@example.com", "user2@example.com"],
    "subject": "Test Email",
    "email_title": "Hello!",
    "main_text": "This is a test email.",
    "button_text": "Visit Site",
    "button_url": "https://example.com"
}
```

## 🔧 Integration

The app is automatically integrated into Django CFG:
- URLs: `/newsletter/` (included in main URL config)
- Admin: Available in Django admin with Unfold theme
- Signals: Auto-send welcome/unsubscribe emails
- Templates: Uses `emails/base_email.html` template

## 📝 Notes

- All emails use the centralized `DjangoEmailService`
- No legacy code - clean, modern DRF implementation
- KISS principle - simple, focused functionality
- Follows Django CFG patterns and conventions
