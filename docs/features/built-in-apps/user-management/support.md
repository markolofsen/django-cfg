---
title: Support Ticket System
description: Django-CFG support feature guide. Production-ready support ticket system with built-in validation, type safety, and seamless Django integration.
sidebar_label: Support
sidebar_position: 4
keywords:
  - django-cfg support
  - django support
  - support django-cfg
---

# Support Ticket System

Django-CFG includes a **comprehensive support ticket system** for managing customer support, help desk operations, and user communications.

## Overview

The Support app provides:
- **Ticket management** with status tracking
- **Real-time chat interface** for ticket conversations
- **User-friendly ticket creation** and management
- **Admin dashboard** for support team management
- **Email notifications** for ticket updates
- **Ticket analytics** and performance metrics
- **File attachments** and rich text support

## Quick Start

### Enable Support in Configuration

```python
# config.py
from django_cfg import DjangoConfig

from .environment import env

class MyConfig(DjangoConfig):
    enable_support: bool = True  # Enable support system

    # Email configuration for notifications
    email: EmailConfig = EmailConfig(
        backend="django.core.mail.backends.smtp.EmailBackend",
        host="smtp.gmail.com",
        port=587,
        use_tls=True,
        username=env.email.username,
        password=env.email.password,
        default_from_email="support@yoursite.com"
    )
```

### Create Support Ticket

```python
from django_cfg.apps.support.models import Ticket, Message

# Create ticket
ticket = Ticket.objects.create(
    user=user,
    subject="Login Issue",
    status=Ticket.TicketStatus.OPEN
)

# Add initial message
message = Message.objects.create(
    ticket=ticket,
    user=user,
    content="I'm having trouble logging into my account",
    is_from_user=True
)
```

## Data Models

### Ticket Model

```python
class Ticket(models.Model):
    """Support ticket model."""
    
    class TicketStatus(models.TextChoices):
        OPEN = 'open', 'Open'
        WAITING_FOR_USER = 'waiting_for_user', 'Waiting for User'
        WAITING_FOR_ADMIN = 'waiting_for_admin', 'Waiting for Admin'
        RESOLVED = 'resolved', 'Resolved'
        CLOSED = 'closed', 'Closed'
    
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='support_tickets')
    subject = models.CharField(max_length=255)
    status = models.CharField(max_length=32, choices=TicketStatus.choices, default=TicketStatus.OPEN)
    created_at = models.DateTimeField(auto_now_add=True)
    
    @property
    def last_message(self):
        return self.messages.order_by('-created_at').first()
    
    def is_author(self, user):
        """Check if the given user is the author of this ticket."""
        return self.user == user
    
    @property
    def unanswered_messages_count(self) -> int:
        """Get count of unanswered messages for this specific ticket."""
        return Ticket.objects.get_unanswered_messages_count_for_ticket(self)
```

### Message Model

```python
class Message(models.Model):
    """Support ticket message model."""
    
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name='messages')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.TextField()
    is_from_user = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['created_at']
```

## API Usage

### Ticket Management API

```python
# Create support ticket
POST /api/support/tickets/
{
    "subject": "Payment Issue",
    "initial_message": "I was charged twice for my subscription"
}

# Get user's tickets
GET /api/support/tickets/

# Get ticket details
GET /api/support/tickets/{uuid}/

# Add message to ticket
POST /api/support/tickets/{uuid}/messages/
{
    "content": "Thank you for contacting support. We'll investigate this issue."
}

# Update ticket status
PATCH /api/support/tickets/{uuid}/
{
    "status": "resolved"
}
```

### Ticket Management

```python
from django_cfg.apps.support.models import Ticket, Message

# Create ticket with initial message
def create_support_ticket(user, subject, initial_message):
    ticket = Ticket.objects.create(
        user=user,
        subject=subject,
        status=Ticket.TicketStatus.OPEN
    )
    
    Message.objects.create(
        ticket=ticket,
        user=user,
        content=initial_message,
        is_from_user=True
    )
    
    return ticket

# Add admin response
def add_admin_response(ticket, admin_user, content):
    message = Message.objects.create(
        ticket=ticket,
        user=admin_user,
        content=content,
        is_from_user=False
    )
    
    # Update ticket status
    ticket.status = Ticket.TicketStatus.WAITING_FOR_USER
    ticket.save()
    
    return message
```

## 💬 Chat Interface

### Real-time Chat

The support system includes a **real-time chat interface** for seamless communication:

```html
<!-- ticket_chat.html -->
<div class="chat-container">
    <div class="chat-messages" id="chat-messages">
        {% for message in ticket.messages.all %}
            <div class="message {% if message.is_from_user %}user-message{% else %}admin-message{% endif %}">
                <div class="message-content">{{ message.content }}</div>
                <div class="message-time">{{ message.created_at|date:"M d, H:i" }}</div>
            </div>
        {% endfor %}
    </div>
    
    <form class="chat-form" id="message-form">
        <textarea name="content" placeholder="Type your message..." required></textarea>
        <button type="submit">Send</button>
    </form>
</div>
```

### Chat JavaScript

```javascript
// Real-time message updates
class TicketChat {
    constructor(ticketUuid) {
        this.ticketUuid = ticketUuid;
        this.initializeChat();
    }
    
    initializeChat() {
        // Poll for new messages
        setInterval(() => {
            this.checkForNewMessages();
        }, 5000);
        
        // Handle form submission
        document.getElementById('message-form').addEventListener('submit', (e) => {
            e.preventDefault();
            this.sendMessage();
        });
    }
    
    async sendMessage() {
        const form = document.getElementById('message-form');
        const content = form.content.value;
        
        const response = await fetch(`/api/support/tickets/${this.ticketUuid}/messages/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({ content })
        });
        
        if (response.ok) {
            form.content.value = '';
            this.loadMessages();
        }
    }
    
    async checkForNewMessages() {
        const response = await fetch(`/api/support/tickets/${this.ticketUuid}/messages/`);
        const messages = await response.json();
        this.updateChatDisplay(messages);
    }
}
```

## Admin Interface

### Support Dashboard

The admin interface provides:
- **Ticket queue** with priority and status filtering
- **Real-time chat** for admin responses
- **Bulk actions** for ticket management
- **Analytics dashboard** with support metrics
- **User lookup** and ticket history
- **Canned responses** for common issues

### Ticket Management

```python
# admin.py (automatically configured)
from django_cfg.apps.support.admin import TicketAdmin, MessageAdmin

# Features included:
# - Status-based filtering
# - User filtering
# - Date range filtering
# - Bulk status updates
# - Message inline editing
# - Ticket analytics
```

### Management Commands

```bash
# Support system statistics
python manage.py support_stats

# Close old resolved tickets
python manage.py close_old_tickets --days=30

# Send ticket reminders
python manage.py send_ticket_reminders

# Export support data
python manage.py export_support_data --format=csv --days=90
```

## Analytics & Metrics

### Support Metrics

```python
from django_cfg.apps.support.models import Ticket, Message
from django.db.models import Count, Avg
from django.utils import timezone
from datetime import timedelta

# Support statistics
def get_support_stats(days=30):
    cutoff_date = timezone.now() - timedelta(days=days)
    
    stats = {
        # Ticket counts
        'total_tickets': Ticket.objects.filter(created_at__gte=cutoff_date).count(),
        'open_tickets': Ticket.objects.filter(status='open').count(),
        'resolved_tickets': Ticket.objects.filter(
            status='resolved',
            created_at__gte=cutoff_date
        ).count(),
        
        # Response metrics
        'avg_response_time': get_avg_response_time(),
        'avg_resolution_time': get_avg_resolution_time(),
        
        # User satisfaction
        'tickets_by_status': Ticket.objects.values('status').annotate(count=Count('uuid')),
    }
    
    return stats

def get_avg_response_time():
    """Calculate average time to first admin response"""
    # Implementation for calculating response time metrics
    pass

def get_avg_resolution_time():
    """Calculate average time to ticket resolution"""
    # Implementation for calculating resolution time metrics
    pass
```

### Performance Dashboard

```python
# Support team performance
def get_team_performance():
    return {
        'tickets_per_agent': get_tickets_per_agent(),
        'resolution_rates': get_resolution_rates(),
        'customer_satisfaction': get_satisfaction_scores(),
        'response_time_trends': get_response_time_trends()
    }
```

## Integration Examples

### Email Integration

```python
# Email notifications for ticket updates
from django_cfg.apps.support.utils.support_email_service import SupportEmailService

class TicketNotificationService:
    def __init__(self):
        self.email_service = SupportEmailService()
    
    def notify_ticket_created(self, ticket):
        """Notify admins of new ticket"""
        self.email_service.send_ticket_notification(
            ticket=ticket,
            template='support/ticket_created.html',
            recipients=settings.SUPPORT_TEAM_EMAILS
        )
    
    def notify_ticket_updated(self, ticket, message):
        """Notify user of ticket update"""
        self.email_service.send_ticket_update(
            ticket=ticket,
            message=message,
            recipient=ticket.user.email
        )
```

### Webhook Integration

```python
# Webhook for external integrations
from django_cfg.apps.support.views.webhook import SupportWebhookView

class SupportWebhookView(APIView):
    """Handle external support system webhooks"""
    
    def post(self, request):
        # Handle external ticket creation
        external_data = request.data
        
        ticket = Ticket.objects.create(
            user=self.get_or_create_user(external_data['email']),
            subject=external_data['subject'],
            status=Ticket.TicketStatus.OPEN
        )
        
        Message.objects.create(
            ticket=ticket,
            user=ticket.user,
            content=external_data['message'],
            is_from_user=True
        )
        
        return Response({'ticket_id': str(ticket.uuid)})
```

## Configuration Options

### Support Settings

```python
# config.py
class MyConfig(DjangoConfig):
    enable_support: bool = True
    
    # Support-specific settings
    support_email: str = "support@company.com"
    support_auto_assign: bool = True
    support_max_tickets_per_user: int = 10
    support_ticket_retention_days: int = 365
    support_enable_chat: bool = True
    support_enable_file_uploads: bool = True
```

### Notification Settings

```python
# Automatic notifications
SUPPORT_NOTIFICATIONS = {
    'ticket_created': True,
    'ticket_updated': True,
    'ticket_resolved': True,
    'admin_response': True,
    'escalation_alerts': True
}
```

## 🧪 Testing

### Support System Testing

```python
# tests/test_support.py
from django.test import TestCase
from django.contrib.auth import get_user_model
from django_cfg.apps.support.models import Ticket, Message

User = get_user_model()

class SupportSystemTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com'
        )
    
    def test_ticket_creation(self):
        ticket = Ticket.objects.create(
            user=self.user,
            subject="Test Issue",
            status=Ticket.TicketStatus.OPEN
        )
        self.assertEqual(str(ticket), f"Ticket #{ticket.pk} - testuser (Open)")
    
    def test_message_creation(self):
        ticket = Ticket.objects.create(
            user=self.user,
            subject="Test Issue"
        )
        
        message = Message.objects.create(
            ticket=ticket,
            user=self.user,
            content="Test message",
            is_from_user=True
        )
        
        self.assertEqual(ticket.last_message, message)
    
    def test_ticket_status_workflow(self):
        ticket = Ticket.objects.create(
            user=self.user,
            subject="Test Issue"
        )
        
        # Test status progression
        ticket.status = Ticket.TicketStatus.WAITING_FOR_ADMIN
        ticket.save()
        self.assertEqual(ticket.status, Ticket.TicketStatus.WAITING_FOR_ADMIN)
```

## Related Documentation

- [**User Management**](./accounts) - User account system
- [**Newsletter System**](./newsletter) - Email integration
- [**Leads System**](./leads) - Customer relationship management
- [**Email Configuration**](/fundamentals/configuration) - Email setup

The Support system provides comprehensive customer support for your Django applications! 🎫

TAGS: support, tickets, helpdesk, customer-service, chat
DEPENDS_ON: [accounts, email, tasks]
USED_BY: [leads, newsletter, admin]
