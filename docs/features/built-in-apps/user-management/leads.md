---
title: Leads Management System
description: Django-CFG leads feature guide. Production-ready leads management system with built-in validation, type safety, and seamless Django integration.
sidebar_label: Leads
sidebar_position: 2
keywords:
  - django-cfg leads
  - django leads
  - leads django-cfg
---

# Leads Management System

Django-CFG includes a **comprehensive lead management system** for tracking and managing potential customers across all your applications.

## Overview

The Leads app provides a **universal lead capture and management system** with:
- **Multi-channel lead capture** (Email, WhatsApp, Telegram, Phone)
- **Lead status tracking** (New → Contacted → Qualified → Converted)
- **User association** and lead attribution
- **Admin interface** with filtering and export capabilities
- **API endpoints** for lead management

## Quick Start

### Enable Leads in Configuration

```python
# config.py
from django_cfg import DjangoConfig

class MyConfig(DjangoConfig):
    enable_leads: bool = True  # Enable lead management
```

### Basic Lead Creation

```python
from django_cfg.apps.leads.models import Lead

# Create a new lead
lead = Lead.objects.create(
    name="John Doe",
    email="john@example.com",
    company="Tech Corp",
    contact_type=Lead.ContactTypeChoices.EMAIL,
    subject="Product Inquiry",
    message="Interested in your Django-CFG solution",
    source="website_form"
)
```

## Data Models

### Lead Model

```python
class Lead(models.Model):
    """Universal model for storing leads from all sites"""
    
    class StatusChoices(models.TextChoices):
        NEW = 'new', 'New'
        CONTACTED = 'contacted', 'Contacted'
        QUALIFIED = 'qualified', 'Qualified'
        CONVERTED = 'converted', 'Converted'
        REJECTED = 'rejected', 'Rejected'
    
    class ContactTypeChoices(models.TextChoices):
        EMAIL = 'email', 'Email'
        WHATSAPP = 'whatsapp', 'WhatsApp'
        TELEGRAM = 'telegram', 'Telegram'
        PHONE = 'phone', 'Phone'
        OTHER = 'other', 'Other'
    
    # User relation
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Basic information
    name = models.CharField(max_length=200)
    email = models.EmailField()
    company = models.CharField(max_length=200, blank=True, null=True)
    company_site = models.CharField(max_length=200, blank=True, null=True)
    
    # Contact information
    contact_type = models.CharField(max_length=20, choices=ContactTypeChoices.choices)
    contact_value = models.CharField(max_length=200, blank=True, null=True)
    
    # Message
    subject = models.CharField(max_length=200, blank=True, null=True)
    message = models.TextField(blank=True, null=True)
    
    # Lead tracking
    status = models.CharField(max_length=20, choices=StatusChoices.choices, default=StatusChoices.NEW)
    source = models.CharField(max_length=100, blank=True, null=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

## API Usage

### Lead Management API

```python
from django_cfg.apps.leads.serializers import LeadSerializer
from django_cfg.apps.leads.views import LeadViewSet

# Create lead via API
POST /api/leads/
{
    "name": "Jane Smith",
    "email": "jane@example.com",
    "company": "StartupCorp",
    "contact_type": "email",
    "subject": "Partnership Inquiry",
    "message": "Looking for integration opportunities",
    "source": "contact_form"
}

# Update lead status
PATCH /api/leads/{id}/
{
    "status": "contacted"
}

# List leads with filtering
GET /api/leads/?status=new&source=website_form
```

### Lead Status Workflow

```python
from django_cfg.apps.leads.models import Lead

# Lead progression workflow
lead = Lead.objects.get(id=1)

# Mark as contacted
lead.status = Lead.StatusChoices.CONTACTED
lead.save()

# Qualify lead
lead.status = Lead.StatusChoices.QUALIFIED
lead.save()

# Convert lead
lead.status = Lead.StatusChoices.CONVERTED
lead.save()
```

## Admin Interface

### Lead Management

The admin interface provides:
- **Lead listing** with status filters
- **Bulk actions** for status updates
- **Export functionality** for lead data
- **Search and filtering** by multiple fields
- **Lead details** with full message history

### Admin Configuration

```python
# admin.py (automatically configured)
from django_cfg.apps.leads.admin import LeadAdmin

# Features included:
# - Status-based filtering
# - Date range filtering
# - Source filtering
# - Bulk status updates
# - CSV export
# - Lead details view
```

## Lead Analytics

### Management Commands

```bash
# Get lead statistics
python manage.py leads_stats

# Export leads to CSV
python manage.py export_leads --status=new --format=csv

# Lead conversion report
python manage.py lead_conversion_report --days=30
```

### Lead Metrics

```python
from django_cfg.apps.leads.models import Lead
from django.db.models import Count

# Lead statistics
stats = {
    'total_leads': Lead.objects.count(),
    'new_leads': Lead.objects.filter(status='new').count(),
    'converted_leads': Lead.objects.filter(status='converted').count(),
    'conversion_rate': Lead.objects.filter(status='converted').count() / Lead.objects.count() * 100
}

# Leads by source
leads_by_source = Lead.objects.values('source').annotate(count=Count('id'))

# Monthly lead trends
from django.utils import timezone
from datetime import timedelta

last_30_days = timezone.now() - timedelta(days=30)
recent_leads = Lead.objects.filter(created_at__gte=last_30_days)
```

## Integration Examples

### Form Integration

```python
# forms.py
from django import forms
from django_cfg.apps.leads.models import Lead

class ContactForm(forms.ModelForm):
    class Meta:
        model = Lead
        fields = ['name', 'email', 'company', 'subject', 'message']
    
    def save(self, commit=True):
        lead = super().save(commit=False)
        lead.source = 'contact_form'
        lead.contact_type = Lead.ContactTypeChoices.EMAIL
        if commit:
            lead.save()
        return lead
```

### API Integration

```python
# views.py
from rest_framework import status
from rest_framework.response import Response
from django_cfg.apps.leads.models import Lead

def capture_lead(request):
    """Capture lead from external source"""
    lead_data = {
        'name': request.data.get('name'),
        'email': request.data.get('email'),
        'source': 'api_integration',
        'message': request.data.get('inquiry')
    }
    
    lead = Lead.objects.create(**lead_data)
    return Response({'lead_id': lead.id}, status=status.HTTP_201_CREATED)
```

## Configuration Options

### Lead Settings

```python
# config.py
class MyConfig(DjangoConfig):
    enable_leads: bool = True
    
    # Lead-specific settings
    lead_auto_assign: bool = True          # Auto-assign leads to users
    lead_notification_email: str = "leads@company.com"
    lead_retention_days: int = 365         # Keep leads for 1 year
    lead_duplicate_check: bool = True      # Check for duplicate emails
```

### Notifications

```python
# Automatic lead notifications
from django_cfg.apps.leads.signals import lead_created

@receiver(lead_created)
def notify_new_lead(sender, lead, **kwargs):
    """Send notification when new lead is created"""
    send_email_notification(
        to=settings.LEAD_NOTIFICATION_EMAIL,
        subject=f"New Lead: {lead.name}",
        template='leads/new_lead_notification.html',
        context={'lead': lead}
    )
```

## 🧪 Testing

### Lead Testing

```python
# tests/test_leads.py
from django.test import TestCase
from django_cfg.apps.leads.models import Lead

class LeadModelTest(TestCase):
    def test_lead_creation(self):
        lead = Lead.objects.create(
            name="Test User",
            email="test@example.com",
            source="test"
        )
        self.assertEqual(lead.status, Lead.StatusChoices.NEW)
        self.assertEqual(str(lead), "Test User - test@example.com")
    
    def test_lead_status_progression(self):
        lead = Lead.objects.create(
            name="Test User",
            email="test@example.com"
        )
        
        # Test status progression
        lead.status = Lead.StatusChoices.CONTACTED
        lead.save()
        self.assertEqual(lead.status, Lead.StatusChoices.CONTACTED)
```

## Related Documentation

- [**Newsletter System**](./newsletter) - Email marketing integration
- [**Support System**](./support) - Customer support tickets
- [**User Management**](./accounts) - User account system
- [**API Documentation**](/api/intro) - REST API endpoints

The Leads system provides comprehensive lead management for your Django applications! 📈

TAGS: leads, crm, lead-management, sales, conversion-tracking
DEPENDS_ON: [accounts, newsletter, api]
USED_BY: [support, analytics, reporting]
