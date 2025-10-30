---
title: Email Quick Start
description: Django-CFG quick start feature guide. Production-ready email quick start with built-in validation, type safety, and seamless Django integration.
sidebar_label: Quick Start
sidebar_position: 2
keywords:
  - django-cfg quick start
  - django quick start
  - quick start django-cfg
---

# Email Module

Django-CFG includes a **comprehensive email system** that provides advanced email functionality with template support, delivery tracking, multi-provider integration, and production-ready features.

## Overview

The Django Email module provides:
- **Template Engine** - Rich HTML/text email templates with context
- **Multi-Provider Support** - SMTP, SendGrid, Mailgun, Amazon SES integration
- **Delivery Tracking** - Email status tracking and analytics
- **Bulk Operations** - Efficient bulk email sending with queuing
- **Error Handling** - Robust error handling and retry mechanisms
- **Testing Tools** - Email testing and debugging utilities

## Quick Start

### Basic Configuration

```python
# config.py
from django_cfg import DjangoConfig

class MyConfig(DjangoConfig):
    # Email backend configuration
    email_backend: str = "django.core.mail.backends.smtp.EmailBackend"
    email_host: str = "smtp.gmail.com"
    email_port: int = 587
    email_use_tls: bool = True
    email_host_user: str = "your-email@gmail.com"
    email_host_password: str = "your-app-password"
    
    # Django-CFG email settings
    default_from_email: str = "noreply@yoursite.com"
    email_template_dir: str = "emails"
    email_tracking_enabled: bool = True
```

### Simple Email Sending

```python
from django_cfg.modules.django_email import send_email, send_template_email

# Send simple email
send_email(
    subject="Welcome to our platform!",
    message="Thank you for joining us.",
    recipient_list=["user@example.com"],
    from_email="noreply@yoursite.com"
)

# Send template-based email
send_template_email(
    template="welcome",
    context={"user_name": "John Doe", "activation_link": "https://..."},
    recipient_list=["user@example.com"],
    subject="Welcome to our platform!"
)
```

## Template System

### Email Templates

Create email templates in your `templates/emails/` directory:

```html
<!-- templates/emails/welcome.html -->
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Welcome to {{ site_name }}</title>
    <style>
        .email-container {
            max-width: 600px;
            margin: 0 auto;
            font-family: Arial, sans-serif;
        }
        .header {
            background-color: #3b82f6;
            color: white;
            padding: 20px;
            text-align: center;
        }
        .content {
            padding: 30px;
            background-color: #f9fafb;
        }
        .button {
            display: inline-block;
            background-color: #3b82f6;
            color: white;
            padding: 12px 24px;
            text-decoration: none;
            border-radius: 6px;
            margin: 20px 0;
        }
    </style>
</head>
<body>
    <div class="email-container">
        <div class="header">
            <h1>Welcome to {{ site_name }}!</h1>
        </div>
        <div class="content">
            <h2>Hello {{ user_name }}!</h2>
            <p>Thank you for joining our platform. We're excited to have you on board!</p>
            
            <p>To get started, please activate your account by clicking the button below:</p>
            
            <a href="{{ activation_link }}" class="button">Activate Account</a>
            
            <p>If you have any questions, feel free to contact our support team.</p>
            
            <p>Best regards,<br>The {{ site_name }} Team</p>
        </div>
    </div>
</body>
</html>
```

```text
<!-- templates/emails/welcome.txt -->
Welcome to {{ site_name }}!

Hello {{ user_name }}!

Thank you for joining our platform. We're excited to have you on board!

To get started, please activate your account by visiting:
{{ activation_link }}

If you have any questions, feel free to contact our support team.

Best regards,
The {{ site_name }} Team
```

### Advanced Template Usage

```python
from django_cfg.modules.django_email import EmailTemplate, send_template_email

# Create reusable email template
class WelcomeEmailTemplate(EmailTemplate):
    template_name = "welcome"
    subject_template = "Welcome to {{ site_name }}, {{ user_name }}!"
    
    def get_context_data(self, user, **kwargs):
        """Generate context for template"""
        context = super().get_context_data(**kwargs)
        context.update({
            'user_name': user.get_full_name() or user.username,
            'site_name': 'My Platform',
            'activation_link': self.generate_activation_link(user),
            'support_email': 'support@myplatform.com'
        })
        return context
    
    def generate_activation_link(self, user):
        """Generate secure activation link"""
        from django.contrib.auth.tokens import default_token_generator
        from django.utils.http import urlsafe_base64_encode
        from django.utils.encoding import force_bytes
        
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        
        return f"https://myplatform.com/activate/{uid}/{token}/"

# Use template
template = WelcomeEmailTemplate()
template.send(
    user=user_instance,
    recipient_list=[user_instance.email]
)
```

## Email Tracking

### Delivery Tracking

```python
from django_cfg.modules.django_email import EmailTracker, get_email_stats

# Track email delivery
tracker = EmailTracker()

# Send tracked email
email_id = send_template_email(
    template="newsletter",
    context={"content": "Monthly update..."},
    recipient_list=["subscriber@example.com"],
    track=True  # Enable tracking
)

# Check delivery status
status = tracker.get_delivery_status(email_id)
print(status)
# {
#     'status': 'delivered',
#     'sent_at': '2023-12-01T10:30:00Z',
#     'delivered_at': '2023-12-01T10:30:15Z',
#     'opened_at': '2023-12-01T11:45:22Z',
#     'clicked_at': None,
#     'bounced': False,
#     'complaint': False
# }

# Get email statistics
stats = get_email_stats(days=30)
print(stats)
# {
#     'total_sent': 1247,
#     'delivered': 1198,
#     'opened': 856,
#     'clicked': 234,
#     'bounced': 23,
#     'complaints': 2,
#     'delivery_rate': 96.1,
#     'open_rate': 71.5,
#     'click_rate': 19.5
# }
```

### Open and Click Tracking

```python
# Enable tracking in templates
<!-- In your email template -->
<img src="{{ tracking_pixel_url }}" width="1" height="1" style="display:none;">

<!-- Track clicks -->
<a href="{{ track_click_url }}?url={{ original_url|urlencode }}">
    Click here
</a>

# Generate tracking URLs
from django_cfg.modules.django_email import generate_tracking_urls

tracking_data = generate_tracking_urls(email_id, recipient_email)
context.update({
    'tracking_pixel_url': tracking_data['pixel_url'],
    'track_click_url': tracking_data['click_url']
})
```

## Bulk Email Operations

### Bulk Email Sending

```python
from django_cfg.modules.django_email import BulkEmailSender
from django.contrib.auth import get_user_model

User = get_user_model()

# Create bulk email sender
bulk_sender = BulkEmailSender(
    template="newsletter",
    subject="Monthly Newsletter - {{ month }} {{ year }}",
    batch_size=100,  # Send in batches of 100
    delay_between_batches=5  # 5 seconds between batches
)

# Prepare recipients
recipients = []
for user in User.objects.filter(newsletter_subscription=True):
    recipients.append({
        'email': user.email,
        'context': {
            'user_name': user.get_full_name(),
            'month': 'December',
            'year': '2023',
            'unsubscribe_url': f'/unsubscribe/{user.id}/'
        }
    })

# Send bulk emails
result = bulk_sender.send_bulk(recipients)
print(result)
# {
#     'total_recipients': 5000,
#     'successful_sends': 4987,
#     'failed_sends': 13,
#     'batches_processed': 50,
#     'total_time': '00:08:32',
#     'average_batch_time': '00:00:10'
# }
```

### Queue Integration

```python
# Use with ReArq for background processing
from django_cfg.modules.django_email import send_bulk_email_task

# Queue bulk email task
task_id = await send_bulk_email_task.enqueue(
    template="newsletter",
    recipients=recipients,
    context={'month': 'December', 'year': '2023'}
)

# Check task status
from rearq import ReArq
arq = ReArq()
result = await arq.get_job_result(task_id)
print(f"Status: {result.status}")
print(f"Result: {result.result}")
```

## Multi-Provider Support

### Provider Configuration

```python
# config.py
class MyConfig(DjangoConfig):
    # Primary email provider
    email_provider: str = "smtp"  # smtp, sendgrid, mailgun, ses
    
    # SMTP configuration
    email_host: str = "smtp.gmail.com"
    email_port: int = 587
    email_use_tls: bool = True
    email_host_user: str = "user@gmail.com"
    email_host_password: str = "password"
    
    # SendGrid configuration
    sendgrid_api_key: str = "SG.xxx"
    sendgrid_from_email: str = "noreply@yoursite.com"
    
    # Mailgun configuration  
    mailgun_api_key: str = "key-xxx"
    mailgun_domain: str = "mg.yoursite.com"
    
    # Amazon SES configuration
    aws_access_key_id: str = "AKIA..."
    aws_secret_access_key: str = "xxx"
    aws_ses_region: str = "us-east-1"
```

### Provider Switching

```python
from django_cfg.modules.django_email import EmailProvider, switch_provider

# Switch providers dynamically
switch_provider('sendgrid')

# Send with specific provider
send_email(
    subject="Test Email",
    message="Testing SendGrid integration",
    recipient_list=["test@example.com"],
    provider='sendgrid'
)

# Provider failover
providers = ['sendgrid', 'mailgun', 'smtp']
for provider in providers:
    try:
        send_email(
            subject="Important Email",
            message="This email must be delivered",
            recipient_list=["user@example.com"],
            provider=provider
        )
        break
    except Exception as e:
        print(f"Provider {provider} failed: {e}")
        continue
```

## 🧪 Testing and Debugging

### Email Testing

```python
from django_cfg.modules.django_email import EmailTester

# Test email configuration
tester = EmailTester()

# Test SMTP connection
smtp_result = tester.test_smtp_connection()
print(smtp_result)
# {
#     'success': True,
#     'host': 'smtp.gmail.com',
#     'port': 587,
#     'tls': True,
#     'response_time': 0.234
# }

# Test email sending
send_result = tester.test_email_send(
    recipient="test@example.com",
    template="test"
)
print(send_result)
# {
#     'success': True,
#     'message_id': '<abc123@gmail.com>',
#     'delivery_time': 1.456,
#     'provider': 'smtp'
# }

# Test template rendering
template_result = tester.test_template_rendering(
    template="welcome",
    context={'user_name': 'Test User'}
)
print(template_result)
# {
#     'success': True,
#     'html_rendered': True,
#     'text_rendered': True,
#     'subject_rendered': True,
#     'context_variables_used': ['user_name', 'site_name']
# }
```

### Debug Mode

```python
# Enable email debugging
class MyConfig(DjangoConfig):
    email_debug: bool = True
    email_debug_level: str = "INFO"  # DEBUG, INFO, WARNING, ERROR
    
    # Save emails to file in debug mode
    email_debug_save_to_file: bool = True
    email_debug_file_path: str = "/tmp/debug_emails/"

# Debug email sending
from django_cfg.modules.django_email import debug_email

with debug_email():
    send_template_email(
        template="welcome",
        context={'user_name': 'Debug User'},
        recipient_list=["debug@example.com"]
    )
    # Email will be saved to debug file instead of sent
```

## Analytics and Reporting

### Email Analytics

```python
from django_cfg.modules.django_email import EmailAnalytics

analytics = EmailAnalytics()

# Campaign performance
campaign_stats = analytics.get_campaign_stats('newsletter_2023_12')
print(campaign_stats)
# {
#     'sent': 5000,
#     'delivered': 4987,
#     'opened': 3567,
#     'clicked': 892,
#     'unsubscribed': 23,
#     'bounced': 13,
#     'delivery_rate': 99.7,
#     'open_rate': 71.5,
#     'click_rate': 17.9,
#     'unsubscribe_rate': 0.5
# }

# Top performing emails
top_emails = analytics.get_top_performing_emails(days=30)
for email in top_emails:
    print(f"{email['subject']}: {email['open_rate']}% open rate")

# Engagement trends
trends = analytics.get_engagement_trends(days=90)
print(trends)
# {
#     'daily_opens': [...],
#     'daily_clicks': [...],
#     'weekly_summary': {...},
#     'best_send_times': ['10:00', '14:00', '19:00']
# }
```

### Reporting Dashboard

```python
# Generate email report
from django_cfg.modules.django_email import generate_email_report

report = generate_email_report(
    start_date='2023-11-01',
    end_date='2023-11-30',
    format='html'  # html, pdf, csv
)

# Save report
with open('email_report_november.html', 'w') as f:
    f.write(report)

# Email report to stakeholders
send_template_email(
    template="monthly_report",
    context={
        'report_month': 'November 2023',
        'report_attachment': report
    },
    recipient_list=["manager@company.com"],
    attachments=[('email_report.html', report, 'text/html')]
)
```

## Related Documentation

- [**Configuration Guide**](/fundamentals/configuration) - Email configuration
- [**Newsletter System**](/features/built-in-apps/user-management/newsletter) - Newsletter integration
- [**Task System**](/features/built-in-apps/operations/tasks) - Background email processing
- [**Template System**](/fundamentals/system/utilities) - Template management

The Email module provides comprehensive email functionality for your Django applications! 📧

TAGS: email, templates, tracking, bulk-operations, multi-provider, analytics
DEPENDS_ON: [configuration, templates, tasks]
USED_BY: [newsletter, accounts, support, notifications]
