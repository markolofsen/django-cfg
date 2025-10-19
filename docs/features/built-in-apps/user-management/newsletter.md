---
title: Newsletter System
description: Django-CFG newsletter feature guide. Production-ready newsletter system with built-in validation, type safety, and seamless Django integration.
sidebar_label: Newsletter
sidebar_position: 3
keywords:
  - django-cfg newsletter
  - django newsletter
  - newsletter django-cfg
---

# Newsletter System

Django-CFG includes a **comprehensive email newsletter system** for managing email campaigns, subscriptions, and automated marketing workflows.

## Overview

The Newsletter app provides:
- **Newsletter management** with multiple campaigns
- **Subscription management** with opt-in/opt-out
- **Email tracking** (opens, clicks, bounces, unsubscribes)
- **Campaign analytics** and performance metrics
- **Auto-subscribe** new users to newsletters
- **Email templates** and customization
- **Admin interface** for campaign management

## Quick Start

### Enable Newsletter in Configuration

```python
# config.py
from django_cfg import DjangoConfig

from .environment import env

class MyConfig(DjangoConfig):
    enable_newsletter: bool = True  # Enable newsletter system

    # Email configuration required
    email: EmailConfig = EmailConfig(
        backend="django.core.mail.backends.smtp.EmailBackend",
        host="smtp.gmail.com",
        port=587,
        use_tls=True,
        username=env.email.username,
        password=env.email.password,
        default_from_email="noreply@yoursite.com"
    )
```

### Create Newsletter Campaign

```python
from django_cfg.apps.newsletter.models import Newsletter, NewsletterSubscription

# Create newsletter
newsletter = Newsletter.objects.create(
    title="Weekly Tech Updates",
    description="Latest technology news and updates",
    is_active=True,
    auto_subscribe=True  # Auto-subscribe new users
)

# Subscribe user
subscription = NewsletterSubscription.objects.create(
    newsletter=newsletter,
    email="user@example.com",
    is_active=True
)
```

## Data Models

### Newsletter Model

```python
class Newsletter(models.Model):
    """Newsletter model for managing email campaigns."""
    
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    auto_subscribe = models.BooleanField(
        default=False,
        help_text="Automatically subscribe new users to this newsletter"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    @property
    def subscribers_count(self):
        """Get count of active subscribers."""
        return self.subscriptions.filter(is_active=True).count()
```

### Subscription Model

```python
class NewsletterSubscription(models.Model):
    """Newsletter subscription model."""
    
    class SubscriptionStatus(models.TextChoices):
        PENDING = 'pending', 'Pending Confirmation'
        ACTIVE = 'active', 'Active'
        UNSUBSCRIBED = 'unsubscribed', 'Unsubscribed'
        BOUNCED = 'bounced', 'Bounced'
    
    newsletter = models.ForeignKey(Newsletter, on_delete=models.CASCADE, related_name='subscriptions')
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    email = models.EmailField()
    status = models.CharField(max_length=20, choices=SubscriptionStatus.choices, default=SubscriptionStatus.PENDING)
    is_active = models.BooleanField(default=True)
    
    # Tracking
    subscribed_at = models.DateTimeField(auto_now_add=True)
    unsubscribed_at = models.DateTimeField(null=True, blank=True)
    confirmation_token = models.CharField(max_length=64, unique=True)
```

### Email Campaign Model

```python
class NewsletterEmail(models.Model):
    """Individual newsletter email campaigns."""
    
    class EmailStatus(models.TextChoices):
        DRAFT = 'draft', 'Draft'
        SCHEDULED = 'scheduled', 'Scheduled'
        SENDING = 'sending', 'Sending'
        SENT = 'sent', 'Sent'
        FAILED = 'failed', 'Failed'
    
    newsletter = models.ForeignKey(Newsletter, on_delete=models.CASCADE, related_name='emails')
    subject = models.CharField(max_length=255)
    content_html = models.TextField()
    content_text = models.TextField(blank=True)
    
    status = models.CharField(max_length=20, choices=EmailStatus.choices, default=EmailStatus.DRAFT)
    scheduled_at = models.DateTimeField(null=True, blank=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    
    # Analytics
    total_sent = models.PositiveIntegerField(default=0)
    total_opened = models.PositiveIntegerField(default=0)
    total_clicked = models.PositiveIntegerField(default=0)
    total_bounced = models.PositiveIntegerField(default=0)
    total_unsubscribed = models.PositiveIntegerField(default=0)
```

## API Usage

### Newsletter Management API

```python
# Create newsletter subscription
POST /api/newsletter/subscribe/
{
    "newsletter_id": 1,
    "email": "user@example.com"
}

# Unsubscribe
POST /api/newsletter/unsubscribe/
{
    "token": "unsubscribe_token_here"
}

# Get newsletter campaigns
GET /api/newsletter/campaigns/

# Send newsletter email
POST /api/newsletter/campaigns/{id}/send/
{
    "subject": "Weekly Update #42",
    "content_html": "<h1>Newsletter Content</h1>",
    "scheduled_at": "2024-01-15T10:00:00Z"
}
```

### Subscription Management

```python
from django_cfg.apps.newsletter.models import Newsletter, NewsletterSubscription

# Subscribe user to newsletter
def subscribe_user(email, newsletter_id):
    newsletter = Newsletter.objects.get(id=newsletter_id)
    subscription, created = NewsletterSubscription.objects.get_or_create(
        newsletter=newsletter,
        email=email,
        defaults={'is_active': True}
    )
    return subscription

# Bulk subscribe users
def bulk_subscribe(emails, newsletter_id):
    newsletter = Newsletter.objects.get(id=newsletter_id)
    subscriptions = []
    
    for email in emails:
        subscription = NewsletterSubscription(
            newsletter=newsletter,
            email=email,
            is_active=True
        )
        subscriptions.append(subscription)
    
    NewsletterSubscription.objects.bulk_create(subscriptions, ignore_conflicts=True)
```

## Email Campaigns

### Campaign Creation

```python
from django_cfg.apps.newsletter.models import NewsletterEmail

# Create email campaign
campaign = NewsletterEmail.objects.create(
    newsletter=newsletter,
    subject="Weekly Tech Updates - Issue #42",
    content_html="""
    <html>
        <body>
            <h1>This Week in Tech</h1>
            <p>Latest updates from the tech world...</p>
            <a href="{{unsubscribe_url}}">Unsubscribe</a>
        </body>
    </html>
    """,
    content_text="This Week in Tech\n\nLatest updates..."
)

# Schedule campaign
from django.utils import timezone
from datetime import timedelta

campaign.scheduled_at = timezone.now() + timedelta(hours=1)
campaign.status = NewsletterEmail.EmailStatus.SCHEDULED
campaign.save()
```

### Email Templates

```python
# Email template with variables
template_html = """
<!DOCTYPE html>
<html>
<head>
    <title>{{newsletter.title}}</title>
</head>
<body>
    <h1>{{subject}}</h1>
    <div>{{content}}</div>
    
    <footer>
        <p>You're receiving this because you subscribed to {{newsletter.title}}</p>
        <a href="{{unsubscribe_url}}">Unsubscribe</a>
    </footer>
</body>
</html>
"""

# Template context
context = {
    'newsletter': newsletter,
    'subject': campaign.subject,
    'content': campaign.content_html,
    'unsubscribe_url': f"/newsletter/unsubscribe/{subscription.confirmation_token}/"
}
```

## Analytics & Tracking

### Email Tracking

```python
from django_cfg.apps.newsletter.models import EmailTracking

class EmailTracking(models.Model):
    """Track email interactions."""
    
    class ActionType(models.TextChoices):
        SENT = 'sent', 'Sent'
        OPENED = 'opened', 'Opened'
        CLICKED = 'clicked', 'Clicked'
        BOUNCED = 'bounced', 'Bounced'
        UNSUBSCRIBED = 'unsubscribed', 'Unsubscribed'
    
    email = models.ForeignKey(NewsletterEmail, on_delete=models.CASCADE)
    subscription = models.ForeignKey(NewsletterSubscription, on_delete=models.CASCADE)
    action_type = models.CharField(max_length=20, choices=ActionType.choices)
    timestamp = models.DateTimeField(auto_now_add=True)
    user_agent = models.TextField(blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
```

### Campaign Analytics

```python
# Campaign performance metrics
def get_campaign_stats(campaign_id):
    campaign = NewsletterEmail.objects.get(id=campaign_id)
    
    stats = {
        'total_sent': campaign.total_sent,
        'total_opened': campaign.total_opened,
        'total_clicked': campaign.total_clicked,
        'total_bounced': campaign.total_bounced,
        'total_unsubscribed': campaign.total_unsubscribed,
        
        # Calculated metrics
        'open_rate': (campaign.total_opened / campaign.total_sent * 100) if campaign.total_sent > 0 else 0,
        'click_rate': (campaign.total_clicked / campaign.total_sent * 100) if campaign.total_sent > 0 else 0,
        'bounce_rate': (campaign.total_bounced / campaign.total_sent * 100) if campaign.total_sent > 0 else 0,
        'unsubscribe_rate': (campaign.total_unsubscribed / campaign.total_sent * 100) if campaign.total_sent > 0 else 0,
    }
    
    return stats
```

## Admin Interface

### Newsletter Management

The admin interface provides:
- **Newsletter creation** and management
- **Subscriber management** with bulk actions
- **Campaign creation** and scheduling
- **Analytics dashboard** with performance metrics
- **Email preview** and testing
- **Export functionality** for subscriber lists

### Management Commands

```bash
# Send scheduled newsletters
python manage.py send_newsletters

# Newsletter statistics
python manage.py newsletter_stats

# Clean up old tracking data
python manage.py cleanup_newsletter_tracking --days=90

# Test newsletter sending
python manage.py test_newsletter --email=test@example.com

# Export subscribers
python manage.py export_subscribers --newsletter=1 --format=csv
```

## Integration Examples

### Auto-Subscribe New Users

```python
# signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from django_cfg.apps.newsletter.models import Newsletter, NewsletterSubscription

User = get_user_model()

@receiver(post_save, sender=User)
def auto_subscribe_user(sender, instance, created, **kwargs):
    """Auto-subscribe new users to newsletters with auto_subscribe=True"""
    if created:
        auto_newsletters = Newsletter.objects.filter(auto_subscribe=True, is_active=True)
        
        for newsletter in auto_newsletters:
            NewsletterSubscription.objects.get_or_create(
                newsletter=newsletter,
                user=instance,
                email=instance.email,
                defaults={'is_active': True}
            )
```

### Newsletter Widget

```python
# forms.py
from django import forms
from django_cfg.apps.newsletter.models import Newsletter

class NewsletterSubscriptionForm(forms.Form):
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'placeholder': 'Enter your email',
            'class': 'form-control'
        })
    )
    newsletter = forms.ModelChoiceField(
        queryset=Newsletter.objects.filter(is_active=True),
        widget=forms.HiddenInput()
    )
    
    def save(self):
        email = self.cleaned_data['email']
        newsletter = self.cleaned_data['newsletter']
        
        subscription, created = NewsletterSubscription.objects.get_or_create(
            newsletter=newsletter,
            email=email,
            defaults={'is_active': True}
        )
        
        return subscription
```

## Configuration Options

### Newsletter Settings

```python
# config.py
class MyConfig(DjangoConfig):
    enable_newsletter: bool = True
    
    # Newsletter-specific settings
    newsletter_from_email: str = "newsletter@company.com"
    newsletter_reply_to: str = "support@company.com"
    newsletter_unsubscribe_url: str = "https://yoursite.com/newsletter/unsubscribe/"
    newsletter_tracking_enabled: bool = True
    newsletter_double_opt_in: bool = True  # Require email confirmation
```

## 🧪 Testing

### Newsletter Testing

```python
# tests/test_newsletter.py
from django.test import TestCase
from django_cfg.apps.newsletter.models import Newsletter, NewsletterSubscription

class NewsletterTest(TestCase):
    def test_newsletter_creation(self):
        newsletter = Newsletter.objects.create(
            title="Test Newsletter",
            description="Test description"
        )
        self.assertEqual(str(newsletter), "Test Newsletter")
    
    def test_subscription_creation(self):
        newsletter = Newsletter.objects.create(title="Test Newsletter")
        subscription = NewsletterSubscription.objects.create(
            newsletter=newsletter,
            email="test@example.com"
        )
        self.assertEqual(subscription.status, NewsletterSubscription.SubscriptionStatus.PENDING)
    
    def test_auto_subscribe(self):
        newsletter = Newsletter.objects.create(
            title="Auto Newsletter",
            auto_subscribe=True
        )
        # Test that new users are auto-subscribed
        # (implementation depends on your user creation flow)
```

## Related Documentation

- [**Email Configuration**](/fundamentals/configuration) - Email setup
- [**Leads System**](./leads) - Lead management integration
- [**User Management**](./accounts) - User account system
- [**Task System**](../operations/tasks) - Background email processing

The Newsletter system provides comprehensive email marketing for your Django applications! 📧

TAGS: newsletter, email-marketing, campaigns, subscriptions, analytics
DEPENDS_ON: [accounts, email, tasks]
USED_BY: [leads, support, marketing]
