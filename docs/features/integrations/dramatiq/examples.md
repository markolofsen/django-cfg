---
title: Dramatiq Examples
description: Django-CFG examples feature guide. Production-ready dramatiq examples with built-in validation, type safety, and seamless Django integration.
sidebar_label: Examples
sidebar_position: 4
keywords:
  - django-cfg examples
  - django examples
  - examples django-cfg
---

# Dramatiq Examples

## Quick Start Examples

### Basic Configuration

```python
# config.py
from django_cfg import DjangoConfig
from django_cfg.models.tasks import TaskConfig

class MyConfig(DjangoConfig):
    project_name: str = "MyApp"
    secret_key: str = "<from-yaml-config>"  # Set via environment/config.yaml
    debug: bool = True

    # Redis configuration (required for tasks)
    cache_default: CacheConfig = CacheConfig(
        redis_url="<from-yaml-config>"  # Set via environment/config.yaml  # e.g., "redis://localhost:6379/0"
    )

    # Enable tasks with zero configuration
    tasks: TaskConfig = TaskConfig()  # Uses intelligent defaults!

config = MyConfig()
```

### Environment-Specific Configuration

```python
# config.py
from django_cfg.models.tasks import TaskConfig, DramatiqConfig

class DevConfig(DjangoConfig):
    debug: bool = True

    tasks: TaskConfig = TaskConfig(
        dramatiq=DramatiqConfig(
            processes=2,  # Fewer processes for development
            threads=4,    # Fewer threads for development
            prometheus_enabled=False,  # Disable monitoring in dev
        )
    )

class ProdConfig(DjangoConfig):
    debug: bool = False

    tasks: TaskConfig = TaskConfig(
        dramatiq=DramatiqConfig(
            processes=8,   # More processes for production
            threads=16,    # More threads for production
            max_retries=5, # More retries in production
            queues=["critical", "default", "background"],
            prometheus_enabled=True,   # Enable monitoring
            admin_enabled=True,        # Enable admin interface
        )
    )

# Environment detection
config = ProdConfig() if os.getenv("PRODUCTION") else DevConfig()
```

## Task Definition Examples

### Simple Tasks

```python
# tasks.py
import dramatiq
from django.core.mail import send_mail
from django.contrib.auth import get_user_model
from myapp.models import Report

User = get_user_model()

@dramatiq.actor
def send_welcome_email(user_id: int):
    """Send welcome email to new user"""
    user = User.objects.get(id=user_id)
    send_mail(
        subject="Welcome to MyApp!",
        message=f"Hello {user.first_name}, welcome!",
        from_email="noreply@myapp.com",
        recipient_list=[user.email],
    )

@dramatiq.actor(queue_name="background")
def generate_monthly_report(month: int, year: int):
    """Generate monthly report in background"""
    report = Report.objects.create(
        month=month,
        year=year,
        status="generating"
    )

    # Heavy computation here...
    data = calculate_monthly_stats(month, year)

    report.data = data
    report.status = "completed"
    report.save()
```

### Advanced Task Patterns

```python
# tasks.py
import dramatiq
from dramatiq.middleware import CurrentMessage
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)

@dramatiq.actor(
    queue_name="high",
    max_retries=5,
    min_backoff=1000,  # 1 second
    max_backoff=30000, # 30 seconds
)
def process_payment(payment_id: int, idempotency_key: str):
    """Process payment with high reliability and idempotency"""
    from myapp.models import Payment

    # Get current message for metadata
    message = CurrentMessage.get_current_message()
    logger.info(f"Processing payment {payment_id}, attempt {message.retries + 1}")

    try:
        payment = Payment.objects.select_for_update().get(
            id=payment_id,
            idempotency_key=idempotency_key
        )

        if payment.status == "completed":
            logger.info(f"Payment {payment_id} already processed")
            return

        # Process payment with external API
        result = external_payment_api.charge(
            amount=payment.amount,
            card_token=payment.card_token,
            idempotency_key=idempotency_key
        )

        payment.external_id = result.transaction_id
        payment.status = "completed"
        payment.save()

        # Chain follow-up tasks
        send_payment_confirmation.send(payment_id)
        update_user_balance.send(payment.user_id, payment.amount)

    except Exception as e:
        logger.error(f"Payment processing failed: {e}")
        payment.status = "failed"
        payment.error_message = str(e)
        payment.save()
        raise  # Re-raise for retry mechanism

@dramatiq.actor(queue_name="default")
def send_payment_confirmation(payment_id: int):
    """Send payment confirmation email"""
    # Implementation here...
    pass

@dramatiq.actor(queue_name="default")
def update_user_balance(user_id: int, amount: int):
    """Update user balance after successful payment"""
    # Implementation here...
    pass
```

### Batch Processing

```python
# tasks.py
import dramatiq
from typing import List
from django.db import transaction

@dramatiq.actor(queue_name="background")
def process_csv_upload(file_path: str, user_id: int):
    """Process large CSV file upload"""
    import csv
    from myapp.models import DataRecord

    batch_size = 1000
    batch = []

    with open(file_path, 'r') as csvfile:
        reader = csv.DictReader(csvfile)

        for row in reader:
            batch.append(DataRecord(
                user_id=user_id,
                data=row,
                status="pending"
            ))

            if len(batch) >= batch_size:
                # Process batch
                process_data_batch.send([record.id for record in batch])

                # Save batch to database
                with transaction.atomic():
                    DataRecord.objects.bulk_create(batch)

                batch = []

        # Process remaining records
        if batch:
            with transaction.atomic():
                DataRecord.objects.bulk_create(batch)
            process_data_batch.send([record.id for record in batch])

@dramatiq.actor(queue_name="background")
def process_data_batch(record_ids: List[int]):
    """Process a batch of data records"""
    from myapp.models import DataRecord

    records = DataRecord.objects.filter(id__in=record_ids)

    for record in records:
        # Process individual record
        processed_data = transform_data(record.data)

        record.processed_data = processed_data
        record.status = "completed"
        record.save()
```

## Usage Patterns

### View Integration

```python
# views.py
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from .tasks import send_welcome_email, generate_monthly_report, process_csv_upload

@login_required
def complete_registration(request):
    """Complete user registration and send welcome email"""
    user = request.user

    # Send welcome email asynchronously
    send_welcome_email.send(user.id)

    messages.success(request, "Registration completed! Check your email.")
    return redirect('dashboard')

def generate_report_view(request):
    """Generate monthly report asynchronously"""
    if request.method == 'POST':
        month = int(request.POST['month'])
        year = int(request.POST['year'])

        # Queue report generation
        generate_monthly_report.send(month, year)

        return JsonResponse({
            "status": "queued",
            "message": "Report generation started. You'll be notified when complete."
        })

    return render(request, 'reports/generate.html')

def upload_csv_view(request):
    """Handle CSV file upload"""
    if request.method == 'POST' and request.FILES.get('csv_file'):
        csv_file = request.FILES['csv_file']

        # Save file temporarily
        file_path = f"/tmp/uploads/{csv_file.name}"
        with open(file_path, 'wb') as f:
            for chunk in csv_file.chunks():
                f.write(chunk)

        # Process asynchronously
        process_csv_upload.send(file_path, request.user.id)

        return JsonResponse({
            "status": "uploaded",
            "message": "File uploaded successfully. Processing started."
        })

    return render(request, 'upload.html')
```

### API Integration

```python
# api/views.py
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .tasks import process_payment

@api_view(['POST'])
def process_payment_api(request):
    """API endpoint for payment processing"""
    payment_data = request.data

    # Validate payment data
    if not all(k in payment_data for k in ['amount', 'card_token']):
        return Response(
            {"error": "Missing required fields"},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Create payment record
    payment = Payment.objects.create(
        user=request.user,
        amount=payment_data['amount'],
        card_token=payment_data['card_token'],
        status="pending"
    )

    # Process payment asynchronously
    process_payment.send_with_options(
        args=[payment.id, payment.idempotency_key],
        queue_name="high",  # High priority queue
        delay=1000,  # Delay 1 second
    )

    return Response({
        "payment_id": payment.id,
        "status": "processing",
        "message": "Payment is being processed"
    }, status=status.HTTP_202_ACCEPTED)
```

### Periodic Tasks with Cron

```python
# tasks.py
import dramatiq
from dramatiq_crontab import cron
from django.utils import timezone
from datetime import timedelta

@dramatiq.actor
@cron("0 2 * * *")  # Run daily at 2 AM
def cleanup_old_files():
    """Clean up old temporary files daily"""
    import os
    from django.conf import settings

    temp_dir = os.path.join(settings.MEDIA_ROOT, 'temp')
    cutoff_date = timezone.now() - timedelta(days=7)

    for filename in os.listdir(temp_dir):
        filepath = os.path.join(temp_dir, filename)
        if os.path.getctime(filepath) < cutoff_date.timestamp():
            os.remove(filepath)

@dramatiq.actor
@cron("0 0 1 * *")  # Run monthly on 1st day at midnight
def generate_monthly_reports():
    """Generate monthly reports for all users"""
    from django.contrib.auth import get_user_model

    User = get_user_model()
    current_date = timezone.now()

    for user in User.objects.filter(is_active=True):
        generate_user_monthly_report.send(
            user.id,
            current_date.month,
            current_date.year
        )

@dramatiq.actor(queue_name="background")
def generate_user_monthly_report(user_id: int, month: int, year: int):
    """Generate monthly report for specific user"""
    # Implementation here...
    pass
```

## Management Commands Usage

### Starting Workers

```bash
# Start workers with default configuration
python manage.py rundramatiq

# Start workers for specific queues
python manage.py rundramatiq --queues high,default

# Start with custom process/thread count
python manage.py rundramatiq --processes 4 --threads 8

# Start with verbose logging
python manage.py rundramatiq --log-level debug

# Start workers in background (production)
nohup python manage.py rundramatiq > /var/log/dramatiq.log 2>&1 &
```

### Monitoring and Management

```bash
# Check task status and queue statistics
python manage.py dramatiq_status

# Clear all failed tasks
python manage.py dramatiq_clear_failed

# Retry specific failed tasks
python manage.py dramatiq_retry_failed --task-name send_welcome_email

# Monitor queue depth
python manage.py dramatiq_status --format json | jq '.queues[].pending'

# Get worker statistics
python manage.py dramatiq_workers
```

## See Also

### Dramatiq Integration

**Core Documentation:**
- [**Dramatiq Overview**](./overview) - Background task processing introduction
- [**Configuration Guide**](./configuration) - Complete configuration reference
- [**Implementation Guide**](./implementation) - Implementation patterns and roadmap
- [**Monitoring Guide**](./monitoring) - Performance tracking and observability
- [**Testing Tasks**](./testing) - Test background tasks

### Practical Guides

**Use Case Examples:**
- [**Sample Project Guide**](/guides/sample-project/overview) - Production example with tasks
- [**Examples Overview**](/guides/examples) - More real-world patterns
- [**Production Config**](/guides/production-config) - Production task setup

**Related Features:**
- [**Operations Apps**](/features/built-in-apps/operations/overview) - Built-in operational features
- [**Tasks App**](/features/built-in-apps/operations/tasks) - Task management interface
- [**Email Module**](/features/modules/email/overview) - Email service for notifications

### Configuration & Infrastructure

**Setup:**
- [**Installation**](/getting-started/installation) - Install Django-CFG with Dramatiq
- [**Configuration Guide**](/getting-started/configuration) - Enable background tasks
- [**Redis Configuration**](/fundamentals/configuration/cache) - Redis as message broker
- [**Environment Variables**](/fundamentals/configuration/environment) - Broker credentials

**Apps Using Tasks:**
- [**AI Knowledge Base**](/features/built-in-apps/ai-knowledge/overview) - Document processing
- [**Payments System**](/features/built-in-apps/payments/overview) - Async payment processing
- [**Newsletter App**](/features/built-in-apps/user-management/newsletter) - Bulk emails

### Tools & Deployment

**CLI & Management:**
- [**Background Task Commands**](/cli/commands/background-tasks) - Manage workers
- [**CLI Tools**](/cli/introduction) - Command-line interface
- [**Troubleshooting**](/guides/troubleshooting) - Common task issues

**Production:**
- [**Docker Deployment**](/guides/docker/production) - Containerized workers
- [**Logging**](/deployment/logging) - Task execution logging
