---
title: Background Tasks
description: Asynchronous task processing with Dramatiq in Django-CFG sample project
sidebar_label: Background Tasks
sidebar_position: 8
---

# Background Tasks

The Django-CFG sample project demonstrates background task processing with Dramatiq. This guide covers task creation, worker management, and common patterns for asynchronous operations.

## Background Tasks Overview

The sample project uses Dramatiq for:
- **Asynchronous email sending**
- **Order processing**
- **Data cleanup tasks**
- **Scheduled jobs**
- **Long-running operations**

## Dramatiq Integration

### Configuration

Dramatiq is configured automatically by Django-CFG:

```python
# api/config.py
from django_cfg import DjangoConfig

class SampleProjectConfig(DjangoConfig):
    # Dramatiq uses Redis as message broker
    dramatiq_broker_url: str = "redis://localhost:6379/0"
```

### Starting Workers

Run Dramatiq workers to process tasks:

```bash
# Start worker
python manage.py rundramatiq

# Start with specific queues
python manage.py rundramatiq --queues default,email,processing

# Start multiple workers
python manage.py rundramatiq --processes 4
```

## Task Definitions

### Basic Task

Create a simple background task:

```python
import dramatiq
from django_cfg import DjangoEmailService

@dramatiq.actor
def send_welcome_email(user_id):
    """Send welcome email to new user."""
    from django.contrib.auth import get_user_model

    User = get_user_model()
    user = User.objects.get(id=user_id)

    email = DjangoEmailService()
    email.send_template(
        template_name="emails/welcome.html",
        context={
            "user_name": user.get_full_name() or user.email,
            "login_url": "https://myapp.com/login"
        },
        recipient_list=[user.email],
        subject="Welcome to Django-CFG Sample!"
    )

    return f"Welcome email sent to {user.email}"
```

### Task with Options

Customize task behavior:

```python
@dramatiq.actor(
    max_retries=3,           # Retry up to 3 times
    min_backoff=15000,       # Wait 15s before first retry
    max_backoff=3600000,     # Max 1 hour between retries
    queue_name="email",      # Use specific queue
    time_limit=60000,        # 60 second timeout
)
def send_order_confirmation(order_id):
    """Send order confirmation email."""
    from apps.shop.models import Order

    order = Order.objects.get(id=order_id)

    email = DjangoEmailService()
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

    return f"Confirmation sent for order {order_id}"
```

## Common Task Patterns

### Email Tasks

Handle email sending asynchronously:

```python
@dramatiq.actor(queue_name="email")
def send_welcome_email(user_id):
    """Send welcome email to new user."""
    from django.contrib.auth import get_user_model

    User = get_user_model()
    user = User.objects.get(id=user_id)

    email = DjangoEmailService()
    email.send_template(
        template_name="emails/welcome.html",
        context={
            "user_name": user.get_full_name() or user.email,
            "login_url": "https://myapp.com/login"
        },
        recipient_list=[user.email],
        subject="Welcome to Django-CFG Sample!"
    )

    return f"Welcome email sent to {user.email}"

@dramatiq.actor(queue_name="email")
def send_password_reset_email(user_id, reset_token):
    """Send password reset email."""
    from django.contrib.auth import get_user_model

    User = get_user_model()
    user = User.objects.get(id=user_id)

    email = DjangoEmailService()
    email.send_template(
        template_name="emails/password_reset.html",
        context={
            "user_name": user.get_full_name() or user.email,
            "reset_url": f"https://myapp.com/reset/{reset_token}"
        },
        recipient_list=[user.email],
        subject="Password Reset Request"
    )

    return f"Reset email sent to {user.email}"
```

See [Service Integrations](./service-integrations) for email configuration.

### Order Processing Tasks

Process e-commerce orders asynchronously:

```python
@dramatiq.actor(queue_name="processing")
def process_order(order_id):
    """Process e-commerce order."""
    from apps.shop.models import Order

    order = Order.objects.get(id=order_id)

    # Process payment
    process_payment(order)

    # Update inventory
    update_inventory(order)

    # Send confirmation email
    send_order_confirmation.send(order_id)

    # Update order status
    order.status = 'processed'
    order.save()

    return f"Order {order_id} processed successfully"

def process_payment(order):
    """Process payment for order."""
    # Payment processing logic
    pass

def update_inventory(order):
    """Update product inventory."""
    for item in order.items.all():
        product = item.product
        product.stock -= item.quantity
        product.save()
```

### Cleanup Tasks

Perform periodic maintenance:

```python
@dramatiq.actor
def cleanup_old_data():
    """Periodic cleanup task."""
    from django.utils import timezone
    from datetime import timedelta

    # Clean up old OTP codes
    from django_cfg.apps.accounts.models import OTPSecret

    cutoff = timezone.now() - timedelta(hours=1)
    deleted_count = OTPSecret.objects.filter(
        created_at__lt=cutoff
    ).delete()[0]

    return f"Cleaned up {deleted_count} old OTP codes"

@dramatiq.actor
def cleanup_expired_sessions():
    """Remove expired sessions."""
    from django.contrib.sessions.models import Session
    from django.utils import timezone

    Session.objects.filter(expire_date__lt=timezone.now()).delete()

    return "Expired sessions cleaned up"
```

### Data Export Tasks

Handle long-running data exports:

```python
@dramatiq.actor(
    time_limit=3600000,  # 1 hour timeout
    queue_name="exports"
)
def export_user_data(user_id):
    """Export all user data to CSV."""
    from django.contrib.auth import get_user_model
    import csv
    from io import StringIO

    User = get_user_model()
    user = User.objects.get(id=user_id)

    # Collect user data
    data = collect_user_data(user)

    # Generate CSV
    output = StringIO()
    writer = csv.writer(output)
    writer.writerows(data)

    # Upload to storage
    file_url = upload_to_storage(output.getvalue(), f"export_{user_id}.csv")

    # Send download link via email
    send_export_ready_email.send(user_id, file_url)

    return f"Data exported for user {user_id}"
```

## Invoking Tasks

### Simple Invocation

Call tasks asynchronously:

```python
# Send task to queue
send_welcome_email.send(user.id)

# Task runs in background, execution continues immediately
```

### Delayed Execution

Schedule tasks for future execution:

```python
from datetime import timedelta

# Send reminder in 24 hours
send_reminder_email.send_with_options(
    args=(user.id,),
    delay=timedelta(hours=24).total_seconds() * 1000  # milliseconds
)
```

### Task Chaining

Execute tasks in sequence:

```python
# Create order -> Process payment -> Send confirmation
def handle_order_creation(order):
    """Handle new order creation."""
    # Process order
    process_order.send(order.id)

    # Send confirmation (after processing)
    send_order_confirmation.send_with_options(
        args=(order.id,),
        delay=5000  # Wait 5 seconds
    )
```

### Task Groups

Execute multiple tasks in parallel:

```python
from dramatiq import group

# Send notifications to multiple users
user_ids = [1, 2, 3, 4, 5]
tasks = group([
    send_notification.message(user_id)
    for user_id in user_ids
])
tasks.run()
```

## Scheduled Tasks

### Cron-style Scheduling

Configure periodic tasks:

```python
# settings.py (generated by Django-CFG)
DRAMATIQ_CRON_JOBS = [
    {
        'actor_name': 'cleanup_old_data',
        'cron': '0 2 * * *',  # Daily at 2 AM
    },
    {
        'actor_name': 'send_daily_report',
        'cron': '0 9 * * 1-5',  # Weekdays at 9 AM
    },
    {
        'actor_name': 'backup_database',
        'cron': '0 0 * * 0',  # Weekly on Sunday
    }
]
```

### Cron Expression Format

```
* * * * *
│ │ │ │ │
│ │ │ │ └── Day of week (0-6, Sunday=0)
│ │ │ └──── Month (1-12)
│ │ └────── Day of month (1-31)
│ └──────── Hour (0-23)
└────────── Minute (0-59)
```

Examples:
- `0 * * * *` - Every hour
- `*/15 * * * *` - Every 15 minutes
- `0 0 * * *` - Daily at midnight
- `0 9 * * 1` - Every Monday at 9 AM

### Scheduled Task Examples

```python
@dramatiq.actor
def send_daily_report():
    """Send daily analytics report."""
    from django.core.mail import send_mail
    from datetime import date

    report = generate_daily_report(date.today())

    send_mail(
        subject=f"Daily Report - {date.today()}",
        message=report,
        from_email="reports@myapp.com",
        recipient_list=["admin@myapp.com"]
    )

    return "Daily report sent"

@dramatiq.actor
def backup_database():
    """Backup database to cloud storage."""
    import subprocess

    # Create backup
    subprocess.run([
        'pg_dump',
        '-h', 'localhost',
        '-U', 'postgres',
        '-d', 'myapp',
        '-f', f'/backups/myapp_{date.today()}.sql'
    ])

    # Upload to S3
    upload_to_s3(f'/backups/myapp_{date.today()}.sql')

    return "Database backed up"
```

## Error Handling

### Retry Logic

Tasks automatically retry on failure:

```python
@dramatiq.actor(
    max_retries=3,
    min_backoff=1000,   # 1 second
    max_backoff=60000,  # 1 minute
)
def unreliable_task(data):
    """Task that may fail and needs retries."""
    try:
        result = process_data(data)
        return result
    except Exception as e:
        # Log error
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Task failed: {e}")
        raise  # Re-raise to trigger retry
```

### Dead Letter Queue

Handle tasks that fail permanently:

```python
@dramatiq.actor(
    max_retries=3,
    throws=(ValueError, TypeError),  # Don't retry these errors
)
def process_user_input(user_id, input_data):
    """Process user input with validation."""
    if not validate_input(input_data):
        raise ValueError("Invalid input")

    # Process valid input
    process_data(input_data)
```

### Error Notifications

Send notifications for task failures:

```python
@dramatiq.actor
def critical_task(data):
    """Critical task that notifies on failure."""
    try:
        result = perform_critical_operation(data)
        return result
    except Exception as e:
        # Send alert
        from django_cfg import DjangoTelegram
        telegram = DjangoTelegram()
        telegram.send_message(
            chat_id="@alerts",
            text=f"🚨 Critical task failed: {str(e)}"
        )
        raise
```

## Monitoring Tasks

### Task Status

Check task execution status:

```python
# Send task and get message
message = send_welcome_email.send(user.id)

# Check if task completed (requires result backend)
# message.get_result()
```

### Logging

Add logging to tasks:

```python
import logging
import dramatiq

logger = logging.getLogger(__name__)

@dramatiq.actor
def logged_task(data):
    """Task with logging."""
    logger.info(f"Task started with data: {data}")

    try:
        result = process_data(data)
        logger.info(f"Task completed: {result}")
        return result
    except Exception as e:
        logger.error(f"Task failed: {e}", exc_info=True)
        raise
```

### Task Metrics

Track task performance:

```python
from django.utils import timezone

@dramatiq.actor
def monitored_task(data):
    """Task with performance monitoring."""
    start_time = timezone.now()

    result = process_data(data)

    duration = (timezone.now() - start_time).total_seconds()

    # Log metrics
    log_task_metrics("monitored_task", duration, success=True)

    return result
```

## Best Practices

### 1. Keep Tasks Idempotent

Tasks should produce the same result when run multiple times:

```python
# ✅ Good: Idempotent task
@dramatiq.actor
def update_user_stats(user_id):
    user = User.objects.get(id=user_id)
    user.post_count = user.posts.count()  # Recalculate
    user.save()

# ❌ Bad: Non-idempotent task
@dramatiq.actor
def increment_user_count(user_id):
    user = User.objects.get(id=user_id)
    user.post_count += 1  # Increments on each run
    user.save()
```

### 2. Use Specific Queues

Organize tasks by priority and type:

```python
# ✅ Good: Separate queues
@dramatiq.actor(queue_name="email")
def send_email(user_id):
    pass

@dramatiq.actor(queue_name="processing")
def process_order(order_id):
    pass

# ❌ Bad: All in default queue
@dramatiq.actor
def all_tasks(*args):
    pass
```

### 3. Set Appropriate Timeouts

Prevent tasks from running indefinitely:

```python
# ✅ Good: Reasonable timeout
@dramatiq.actor(time_limit=60000)  # 1 minute
def quick_task(data):
    pass

@dramatiq.actor(time_limit=3600000)  # 1 hour
def long_task(data):
    pass

# ❌ Bad: No timeout
@dramatiq.actor
def risky_task(data):
    pass
```

### 4. Handle Errors Gracefully

Don't let tasks fail silently:

```python
# ✅ Good: Error handling
@dramatiq.actor
def robust_task(data):
    try:
        result = process_data(data)
        return result
    except Exception as e:
        logger.error(f"Task failed: {e}")
        notify_admin(e)
        raise

# ❌ Bad: Ignoring errors
@dramatiq.actor
def silent_task(data):
    try:
        process_data(data)
    except:
        pass  # Silent failure
```

## Docker Deployment

Run workers in Docker:

```yaml
# docker-compose.yml
services:
  web:
    build: .
    command: gunicorn api.wsgi:application

  dramatiq:
    build: .
    command: python manage.py rundramatiq
    environment:
      - DJANGO_SETTINGS_MODULE=api.settings
    depends_on:
      - redis

  redis:
    image: redis:7-alpine
```

See [Deployment Guide](./deployment) for complete Docker setup.

## Related Topics

- [Service Integrations](./service-integrations) - Email and notification services
- [Configuration](./configuration) - Dramatiq configuration
- [Deployment](./deployment) - Running workers in production

Background tasks enable scalable, responsive applications!
