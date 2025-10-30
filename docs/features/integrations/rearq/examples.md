> **📚 Part of**: [ReArq Integration](/features/integrations/rearq/overview) - Return to ReArq overview

# ReArq Integration - Production-Ready Examples

**Status**: Production Ready
**Author**: Django-CFG Team
**Date**: 2025-10-30
**Version**: 1.0

## Table of Contents

1. [Quick Start](#1-quick-start)
2. [Task Definition Examples](#2-task-definition-examples)
3. [Cron Task Examples](#3-cron-task-examples)
4. [Django ORM Integration](#4-django-orm-integration)
5. [Advanced Patterns](#5-advanced-patterns)
6. [Batch Processing](#6-batch-processing)
7. [View Integration](#7-view-integration)
8. [API Integration](#8-api-integration)
9. [Signal Integration](#9-signal-integration)
10. [Testing Tasks](#10-testing-tasks)

---

## 1. Quick Start

### Minimal Configuration

```python
# config.py
from django_cfg import DjangoConfig
from django_cfg.models.tasks import TaskConfig, RearqConfig

class Config(DjangoConfig):
    project_name = "My Project"

    # Enable ReArq tasks
    tasks = TaskConfig(
        enabled=True,
        rearq=RearqConfig(
            redis_url="redis://localhost:6379/0",
        )
    )

config = Config()
```

### Define Your First Task

```python
# myapp/tasks.py
from django_cfg.apps.tasks import task

@task(queue="default")
async def hello_world(name: str):
    """Simple hello world task."""
    print(f"Hello, {name}!")
    return f"Greeted {name}"
```

### Call the Task from View

```python
# myapp/views.py
from django.http import JsonResponse
from myapp.tasks import hello_world

async def my_view(request):
    # Schedule task
    job = await hello_world.delay(name="World")

    # Wait for result (optional)
    result = await job.result(timeout=5)

    return JsonResponse({
        "job_id": job.job_id,
        "status": job.status,
        "result": result.result if result else None
    })
```

### Run Worker

```bash
# Terminal 1: Start worker
rearq main:rearq worker --queue default

# Terminal 2: Start timer (for cron tasks)
rearq main:rearq worker --with-timer

# Terminal 3: Start Django
python manage.py runserver
```

---

## 2. Task Definition Examples

### Basic Task with Type Hints

```python
from django_cfg.apps.tasks import task

@task()
async def add_numbers(a: int, b: int) -> int:
    """Add two numbers."""
    return a + b

# Usage
job = await add_numbers.delay(a=5, b=3)
result = await job.result(timeout=10)
print(result.result)  # 8
```

### Task with Custom Queue

```python
@task(queue="emails")
async def send_email(to: str, subject: str, body: str):
    """Send email via SMTP."""
    import smtplib
    from email.mime.text import MIMEText

    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['To'] = to
    msg['From'] = 'noreply@example.com'

    # Send email logic
    return {"sent": True, "to": to}

# Usage
job = await send_email.delay(
    to="user@example.com",
    subject="Welcome!",
    body="Thank you for signing up."
)
```

### Task with Timeout

```python
@task(queue="processing", job_timeout=300)  # 5 minutes
async def long_running_process(data_id: int):
    """Process large dataset with timeout."""
    # If this takes longer than 5 minutes, it will be terminated
    result = await process_data(data_id)
    return result
```

### Task with Complex Return Type

```python
from pydantic import BaseModel
from typing import List

class ProcessResult(BaseModel):
    success: bool
    items_processed: int
    errors: List[str]
    total_cost: float

@task()
async def process_batch(item_ids: List[int]) -> ProcessResult:
    """Process batch of items."""
    errors = []
    processed = 0
    cost = 0.0

    for item_id in item_ids:
        try:
            # Process item
            item_cost = await process_single_item(item_id)
            processed += 1
            cost += item_cost
        except Exception as e:
            errors.append(f"Item {item_id}: {str(e)}")

    return ProcessResult(
        success=len(errors) == 0,
        items_processed=processed,
        errors=errors,
        total_cost=cost
    )

# Usage
job = await process_batch.delay(item_ids=[1, 2, 3, 4, 5])
result = await job.result(timeout=60)

if result and result.success:
    data = result.get_result_data()
    print(f"Processed {data['items_processed']} items")
    print(f"Total cost: ${data['total_cost']}")
```

### Fire and Forget Task

```python
@task(queue="logs")
async def log_event(event_type: str, data: dict):
    """Log event without waiting for result."""
    from datetime import datetime

    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "event_type": event_type,
        "data": data
    }

    # Store in database or send to logging service
    await store_log(log_entry)

# Call without waiting
await log_event.delay(
    event_type="user_login",
    data={"user_id": 123, "ip": "192.168.1.1"}
)
# Don't wait for result - continue immediately
```

### Task with Multiple Queues

```python
# High priority queue
@task(queue="high", job_timeout=60)
async def process_payment(payment_id: int):
    """Process payment with high priority."""
    return await charge_payment(payment_id)

# Low priority queue
@task(queue="low", job_timeout=3600)
async def generate_report(report_id: int):
    """Generate report with low priority."""
    return await create_report(report_id)

# Critical queue
@task(queue="critical", job_timeout=30)
async def send_verification_code(user_id: int):
    """Send verification code immediately."""
    return await send_sms_code(user_id)
```

---

## 3. Cron Task Examples

### Every Minute

```python
from django_cfg.apps.tasks import cron_task

@cron_task(cron="* * * * *")
async def check_system_health():
    """Check system health every minute."""
    health_status = await check_health()
    if not health_status.is_healthy:
        await send_alert("System health check failed")
    return {"healthy": health_status.is_healthy}
```

### Every 5 Minutes

```python
@cron_task(cron="*/5 * * * *")
async def sync_external_data():
    """Sync data from external API every 5 minutes."""
    data = await fetch_external_data()
    await update_local_cache(data)
    return {"synced_records": len(data)}
```

### Hourly Tasks

```python
@cron_task(cron="0 * * * *")  # At minute 0 of every hour
async def hourly_cleanup():
    """Run cleanup every hour."""
    from datetime import datetime, timedelta
    from asgiref.sync import sync_to_async
    from myapp.models import TempFile

    cutoff = datetime.now() - timedelta(hours=24)
    deleted_count = await sync_to_async(
        TempFile.objects.filter(created_at__lt=cutoff).delete
    )()

    return {"deleted": deleted_count[0]}

@cron_task(cron="30 * * * *")  # At minute 30 of every hour
async def send_summary_notifications():
    """Send hourly summary notifications."""
    users = await get_active_users()
    sent = 0

    for user in users:
        await send_notification(user, "hourly_summary")
        sent += 1

    return {"notifications_sent": sent}
```

### Daily Tasks

```python
@cron_task(cron="0 0 * * *")  # Every day at midnight
async def daily_backup():
    """Run daily backup at midnight."""
    backup_file = await create_database_backup()
    await upload_to_s3(backup_file)
    return {"backup_file": backup_file}

@cron_task(cron="0 2 * * *")  # Every day at 2 AM
async def cleanup_temp_files():
    """Delete temporary files older than 7 days."""
    from datetime import datetime, timedelta
    from asgiref.sync import sync_to_async
    from myapp.models import TempFile

    cutoff = datetime.now() - timedelta(days=7)
    deleted_count = await sync_to_async(
        TempFile.objects.filter(created_at__lt=cutoff).delete
    )()

    return {"deleted": deleted_count[0]}

@cron_task(cron="0 6 * * *")  # Every day at 6 AM
async def morning_analytics_report():
    """Generate and send morning analytics report."""
    report = await generate_daily_analytics()
    await email_report_to_admins(report)
    return {"report_generated": True}
```

### Weekly Tasks

```python
@cron_task(cron="0 9 * * 1")  # Every Monday at 9 AM
async def weekly_summary():
    """Generate and send weekly summary every Monday."""
    from datetime import datetime, timedelta

    end_date = datetime.now()
    start_date = end_date - timedelta(days=7)

    summary = await generate_weekly_summary(start_date, end_date)
    await send_weekly_email(summary)

    return {"summary_sent": True, "week": start_date.strftime("%Y-W%W")}

@cron_task(cron="0 18 * * 5")  # Every Friday at 6 PM
async def friday_cleanup():
    """Clean up before weekend."""
    await close_pending_tickets()
    await archive_completed_tasks()
    return {"cleanup_completed": True}
```

### Monthly Tasks

```python
@cron_task(cron="0 0 1 * *")  # First day of month at midnight
async def monthly_billing():
    """Process monthly billing on the first day of each month."""
    from datetime import datetime

    current_month = datetime.now().strftime("%Y-%m")
    invoices = await generate_monthly_invoices()

    for invoice in invoices:
        await send_invoice_email(invoice)

    return {
        "month": current_month,
        "invoices_generated": len(invoices)
    }

@cron_task(cron="0 3 1 * *")  # First day of month at 3 AM
async def monthly_archive():
    """Archive last month's data."""
    from datetime import datetime, timedelta

    last_month_start = (datetime.now().replace(day=1) - timedelta(days=1)).replace(day=1)
    last_month_end = datetime.now().replace(day=1) - timedelta(days=1)

    archived_count = await archive_records(last_month_start, last_month_end)

    return {
        "archived_records": archived_count,
        "period": f"{last_month_start.strftime('%Y-%m')}"
    }
```

### Custom Schedule with Seconds

```python
@cron_task(cron="*/5 * * * * *")  # Every 5 seconds (6-field format)
async def frequent_health_check():
    """Check critical systems every 5 seconds."""
    status = await check_critical_systems()
    if not status.all_ok:
        await trigger_emergency_alert()
    return {"status": "checked"}

@cron_task(cron="0/30 * * * * *")  # Every 30 seconds
async def process_high_priority_queue():
    """Process high priority items every 30 seconds."""
    processed = await process_queue("high_priority", limit=10)
    return {"processed_items": processed}
```

### Run at Start

```python
@cron_task(cron="0 * * * *", run_at_start=True)
async def initialize_and_hourly():
    """Run immediately on startup, then every hour."""
    await initialize_system()
    await run_hourly_tasks()
    return {"initialized": True}

# With arguments on startup
@cron_task(cron="0 * * * *", run_at_start={"mode": "startup"})
async def hourly_with_startup_mode(mode: str = "normal"):
    """Run with special mode on startup."""
    if mode == "startup":
        print("Running startup initialization")
        await warm_up_caches()
    else:
        print("Running scheduled task")
        await regular_maintenance()
    return {"mode": mode}
```

### Weekday Tasks

```python
@cron_task(cron="0 18 * * 1-5")  # Weekdays at 6 PM
async def weekday_evening_report():
    """Send report every weekday evening."""
    report = await generate_daily_report()
    await send_to_team(report)
    return {"report_sent": True}

@cron_task(cron="0 8 * * 1-5")  # Weekdays at 8 AM
async def weekday_morning_briefing():
    """Send morning briefing on weekdays."""
    briefing = await create_morning_briefing()
    await send_to_stakeholders(briefing)
    return {"briefing_sent": True}
```

---

## 4. Django ORM Integration

### Basic ORM Query

```python
from asgiref.sync import sync_to_async
from django_cfg.apps.tasks import task
from myapp.models import User

@task()
async def update_user_profile(user_id: int, data: dict):
    """Update user profile asynchronously."""

    # Get user (wrap sync call)
    user = await sync_to_async(User.objects.get)(id=user_id)

    # Update fields
    user.first_name = data.get("first_name", user.first_name)
    user.last_name = data.get("last_name", user.last_name)
    user.email = data.get("email", user.email)

    # Save (wrap sync call)
    await sync_to_async(user.save)()

    return {"updated": True, "user_id": user_id}
```

### QuerySet Operations

```python
from asgiref.sync import sync_to_async
from myapp.models import Order

@task(queue="processing")
async def process_pending_orders():
    """Process all pending orders."""

    @sync_to_async
    def get_pending_orders():
        return list(Order.objects.filter(status="pending"))

    @sync_to_async
    def update_order_status(order_id, status):
        Order.objects.filter(id=order_id).update(status=status)

    # Get orders
    orders = await get_pending_orders()

    if not orders:
        return {"processed": 0}

    # Process each order
    results = []
    for order in orders:
        try:
            await update_order_status(order.id, "processing")
            result = await process_single_order(order)
            await update_order_status(order.id, "completed")
            results.append({"order_id": order.id, "success": True})
        except Exception as e:
            await update_order_status(order.id, "failed")
            results.append({"order_id": order.id, "success": False, "error": str(e)})

    return {"processed": len(results), "results": results}
```

### Bulk Operations with Transactions

```python
from asgiref.sync import sync_to_async
from django.db import transaction
from myapp.models import Product, Inventory

@task(queue="inventory")
async def bulk_update_inventory(updates: list):
    """Bulk update inventory with transaction."""

    @sync_to_async
    @transaction.atomic
    def perform_bulk_update(update_list):
        updated_count = 0
        for update in update_list:
            product_id = update["product_id"]
            quantity = update["quantity"]

            product = Product.objects.get(id=product_id)
            inventory, created = Inventory.objects.get_or_create(
                product=product,
                defaults={"quantity": quantity}
            )

            if not created:
                inventory.quantity = quantity
                inventory.save()

            updated_count += 1

        return updated_count

    # Execute bulk update in transaction
    count = await perform_bulk_update(updates)

    return {
        "success": True,
        "updated_count": count
    }
```

### Complex Queries with Aggregation

```python
from asgiref.sync import sync_to_async
from django.db.models import Count, Sum, Avg, F
from myapp.models import Order, OrderItem

@task()
async def generate_sales_analytics(start_date, end_date):
    """Generate sales analytics for date range."""

    @sync_to_async
    def get_order_statistics():
        return Order.objects.filter(
            created_at__gte=start_date,
            created_at__lte=end_date,
            status="completed"
        ).aggregate(
            total_orders=Count("id"),
            total_revenue=Sum("total_amount"),
            avg_order_value=Avg("total_amount")
        )

    @sync_to_async
    def get_top_products():
        return list(
            OrderItem.objects.filter(
                order__created_at__gte=start_date,
                order__created_at__lte=end_date,
                order__status="completed"
            ).values("product__name")
            .annotate(
                total_sold=Sum("quantity"),
                revenue=Sum(F("quantity") * F("price"))
            )
            .order_by("-total_sold")[:10]
        )

    # Get statistics
    stats = await get_order_statistics()
    top_products = await get_top_products()

    return {
        "period": f"{start_date} to {end_date}",
        "statistics": stats,
        "top_products": top_products
    }
```

### Related Objects

```python
from asgiref.sync import sync_to_async
from myapp.models import User, Profile, Subscription

@task()
async def update_user_subscription(user_id: int, plan: str):
    """Update user subscription with related objects."""

    @sync_to_async
    def get_user_with_related():
        return User.objects.select_related(
            'profile',
            'subscription'
        ).get(id=user_id)

    @sync_to_async
    def update_subscription(user, new_plan):
        subscription = user.subscription
        old_plan = subscription.plan
        subscription.plan = new_plan
        subscription.save()

        # Update profile
        user.profile.subscription_updated_at = timezone.now()
        user.profile.save()

        return old_plan

    # Get user with related objects
    user = await get_user_with_related()

    # Update subscription
    old_plan = await update_subscription(user, plan)

    # Send notification
    await send_subscription_change_email(user, old_plan, plan)

    return {
        "user_id": user_id,
        "old_plan": old_plan,
        "new_plan": plan,
        "success": True
    }
```

### Prefetch Related

```python
from asgiref.sync import sync_to_async
from myapp.models import Course, Enrollment, Lesson

@task()
async def generate_course_progress_report(course_id: int):
    """Generate progress report with prefetch_related."""

    @sync_to_async
    def get_course_with_enrollments():
        return Course.objects.prefetch_related(
            'enrollments__user',
            'lessons'
        ).get(id=course_id)

    @sync_to_async
    def calculate_completion(enrollment, total_lessons):
        completed = enrollment.completed_lessons.count()
        return (completed / total_lessons * 100) if total_lessons > 0 else 0

    # Get course with all related data
    course = await get_course_with_enrollments()
    total_lessons = course.lessons.count()

    # Calculate progress for each enrollment
    progress_data = []
    for enrollment in course.enrollments.all():
        completion = await calculate_completion(enrollment, total_lessons)
        progress_data.append({
            "user": enrollment.user.email,
            "completion_percentage": round(completion, 2),
            "enrolled_date": enrollment.created_at.isoformat()
        })

    return {
        "course_id": course_id,
        "course_name": course.name,
        "total_students": len(progress_data),
        "total_lessons": total_lessons,
        "student_progress": progress_data
    }
```

### Real-World Example: Archive Processing

```python
from asgiref.sync import sync_to_async
from django.contrib.auth import get_user_model
from django_cfg.apps.tasks import task
from knowbase.models import DocumentArchive, ArchiveItem
from knowbase.services.archive import DocumentArchiveService

User = get_user_model()

@task(queue="knowbase", job_retry=3, job_retry_after=60)
async def process_archive_task(archive_id: str, user_id: str):
    """
    Process a document archive asynchronously.

    This is a production example from the knowbase app that shows:
    - Error handling with retries
    - Complex service integration
    - Transaction management
    - Status updates
    """
    from knowbase.services.archive import ArchiveProcessingError

    @sync_to_async
    def get_archive_and_user():
        archive = DocumentArchive.objects.all_users().get(pk=archive_id)
        user = User.objects.get(pk=user_id)
        return archive, user

    @sync_to_async
    def verify_ownership(archive, user):
        return archive.user_id == user.id

    @sync_to_async
    def process_with_service(archive, user):
        service = DocumentArchiveService(user=user)
        return service.process_archive(archive)

    try:
        # Get archive and user
        archive, user = await get_archive_and_user()

        # Verify user owns the archive
        if not await verify_ownership(archive, user):
            raise ArchiveProcessingError(
                message=f"User {user_id} does not own archive {archive_id}",
                code="UNAUTHORIZED_ACCESS"
            )

        # Process the archive
        success = await process_with_service(archive, user)

        return {"success": success, "archive_id": archive_id}

    except DocumentArchive.DoesNotExist:
        raise ArchiveProcessingError(
            message=f"Archive {archive_id} not found",
            code="ARCHIVE_NOT_FOUND"
        )
    except User.DoesNotExist:
        raise ArchiveProcessingError(
            message=f"User {user_id} not found",
            code="USER_NOT_FOUND"
        )
```

---

## 5. Advanced Patterns

### Retry Logic with Custom Delays

```python
from django_cfg.apps.tasks import task
from rearq.exceptions import Retry

@task(queue="external", job_retry=5, job_retry_after=60)
async def call_external_api(url: str):
    """Call external API with automatic retry."""
    import httpx

    async with httpx.AsyncClient() as client:
        response = await client.get(url, timeout=10)
        response.raise_for_status()
        return response.json()

    # If it fails, it will retry 5 times with 60 seconds between retries
```

### Smart Retry with Conditional Logic

```python
@task(bind=True, queue="payments", job_retry=5)
async def process_payment_with_retry(self, payment_id: int):
    """Process payment with smart retry logic."""
    from asgiref.sync import sync_to_async
    from myapp.models import Payment
    import httpx

    @sync_to_async
    def get_payment():
        return Payment.objects.get(id=payment_id)

    @sync_to_async
    def update_payment_status(payment, status, error=None):
        payment.status = status
        if error:
            payment.error_message = error
        payment.save()

    payment = await get_payment()

    try:
        # Call payment gateway
        result = await charge_credit_card(
            amount=payment.amount,
            card_token=payment.card_token
        )

        # Mark as completed
        await update_payment_status(payment, "completed")

        return {
            "success": True,
            "transaction_id": result["transaction_id"]
        }

    except httpx.TimeoutError:
        # Timeout - retry after 30 seconds
        raise Retry(countdown=30)

    except httpx.HTTPStatusError as e:
        if e.response.status_code >= 500:
            # Server error - retry after 60 seconds
            raise Retry(countdown=60)
        else:
            # Client error - don't retry
            await update_payment_status(
                payment,
                "failed",
                f"Payment failed: {e.response.status_code}"
            )
            return {"success": False, "error": str(e)}

    except Exception as e:
        # Unexpected error - retry with exponential backoff
        retry_count = self.job_retry
        countdown = min(300, 30 * (2 ** retry_count))  # Max 5 minutes
        raise Retry(countdown=countdown)
```

### Distributed Locks

```python
@task(queue="sync", run_with_lock=True, lock_timeout=300)
async def sync_external_data():
    """
    Sync data from external API.

    Only one instance runs at a time across all workers.
    Lock is automatically released when task completes.
    """
    data = await fetch_external_data()
    await update_database(data)
    return {"synced_records": len(data)}
```

### Manual Lock Management

```python
@task()
async def manual_lock_example():
    """Manual lock management for complex scenarios."""
    from django_cfg.apps.tasks import get_rearq_client

    client = get_rearq_client()
    redis = client.redis

    lock_key = "my_custom_lock:process_data"
    lock_value = "worker_1"
    lock_timeout = 300  # 5 minutes

    # Try to acquire lock
    lock_acquired = await redis.set(
        lock_key,
        lock_value,
        nx=True,  # Only set if not exists
        ex=lock_timeout
    )

    if not lock_acquired:
        return {
            "skipped": True,
            "reason": "Another instance is running"
        }

    try:
        # Do work
        result = await do_important_work()
        return {"success": True, "result": result}
    finally:
        # Release lock
        await redis.delete(lock_key)
```

### Error Handling and Logging

```python
from django_cfg.modules.django_logging import get_logger

logger = get_logger("tasks")

@task(queue="default", job_retry=3)
async def task_with_comprehensive_logging():
    """Task with comprehensive error handling and logging."""
    logger.info("Task started", extra={
        "task_name": "task_with_comprehensive_logging",
        "timestamp": timezone.now().isoformat()
    })

    try:
        # Risky operation
        result = await perform_operation()

        logger.info("Task completed successfully", extra={
            "result": result,
            "execution_time": "2.5s"
        })

        return {"success": True, "result": result}

    except ValueError as e:
        # Recoverable error - log and return gracefully
        logger.warning(f"Validation error: {e}", extra={
            "error_type": "ValueError",
            "recoverable": True
        })
        return {"success": False, "error": str(e)}

    except ConnectionError as e:
        # Temporary error - log and retry
        logger.error(f"Connection error: {e}", extra={
            "error_type": "ConnectionError",
            "will_retry": True
        })
        raise  # Re-raise to trigger retry

    except Exception as e:
        # Unexpected error - log with full traceback
        logger.error(
            f"Unexpected error in task: {e}",
            exc_info=True,
            extra={
                "error_type": type(e).__name__,
                "unexpected": True
            }
        )
        raise
```

### Task Chaining

```python
@task()
async def step1_fetch_data():
    """Step 1: Fetch data."""
    data = await fetch_from_api()
    return {"data": data, "step": 1}

@task()
async def step2_transform_data(input_data: dict):
    """Step 2: Transform data."""
    transformed = await transform(input_data["data"])
    return {"data": transformed, "step": 2}

@task()
async def step3_save_data(input_data: dict):
    """Step 3: Save data."""
    saved_count = await save_to_database(input_data["data"])
    return {"saved_count": saved_count, "step": 3}

# Chain tasks together
async def run_data_pipeline():
    """Run multi-step data pipeline."""
    # Step 1
    job1 = await step1_fetch_data.delay()
    result1 = await job1.result(timeout=30)

    # Step 2
    job2 = await step2_transform_data.delay(input_data=result1.result)
    result2 = await job2.result(timeout=30)

    # Step 3
    job3 = await step3_save_data.delay(input_data=result2.result)
    result3 = await job3.result(timeout=30)

    return {
        "pipeline_completed": True,
        "final_result": result3.result
    }
```

### Rate Limiting

```python
import asyncio
from datetime import datetime, timedelta

@task()
async def rate_limited_api_calls(items: list):
    """Make API calls with rate limiting."""
    results = []
    max_calls_per_minute = 60
    delay_between_calls = 60 / max_calls_per_minute

    for item in items:
        try:
            result = await call_api(item)
            results.append({"item": item, "success": True, "result": result})
        except Exception as e:
            results.append({"item": item, "success": False, "error": str(e)})

        # Rate limit: wait before next call
        await asyncio.sleep(delay_between_calls)

    return {
        "total_items": len(items),
        "successful": sum(1 for r in results if r["success"]),
        "failed": sum(1 for r in results if not r["success"]),
        "results": results
    }
```

---

## 6. Batch Processing

### Simple Batch Processing

```python
@task(queue="processing")
async def process_items_in_batches(item_ids: list, batch_size: int = 100):
    """Process items in batches."""
    from asgiref.sync import sync_to_async
    from myapp.models import Item

    @sync_to_async
    def get_batch(ids):
        return list(Item.objects.filter(id__in=ids))

    results = []
    total = len(item_ids)

    # Process in batches
    for i in range(0, total, batch_size):
        batch_ids = item_ids[i:i + batch_size]
        items = await get_batch(batch_ids)

        for item in items:
            try:
                result = await process_single_item(item)
                results.append({"item_id": item.id, "success": True})
            except Exception as e:
                results.append({
                    "item_id": item.id,
                    "success": False,
                    "error": str(e)
                })

    successful = sum(1 for r in results if r["success"])
    failed = sum(1 for r in results if not r["success"])

    return {
        "total": total,
        "successful": successful,
        "failed": failed,
        "success_rate": round(successful / total * 100, 2) if total > 0 else 0
    }
```

### Parallel Batch Processing

```python
import asyncio

@task(queue="processing")
async def parallel_batch_processing(item_ids: list, batch_size: int = 50):
    """Process batches in parallel with concurrency control."""
    from asgiref.sync import sync_to_async
    from myapp.models import Item

    @sync_to_async
    def get_batch(ids):
        return list(Item.objects.filter(id__in=ids))

    async def process_batch(batch_ids):
        """Process a single batch."""
        items = await get_batch(batch_ids)
        batch_results = []

        for item in items:
            try:
                result = await process_single_item(item)
                batch_results.append({"item_id": item.id, "success": True})
            except Exception as e:
                batch_results.append({
                    "item_id": item.id,
                    "success": False,
                    "error": str(e)
                })

        return batch_results

    # Split into batches
    batches = [
        item_ids[i:i + batch_size]
        for i in range(0, len(item_ids), batch_size)
    ]

    # Process batches in parallel (max 5 concurrent batches)
    semaphore = asyncio.Semaphore(5)

    async def process_with_semaphore(batch):
        async with semaphore:
            return await process_batch(batch)

    # Execute all batches
    batch_results = await asyncio.gather(*[
        process_with_semaphore(batch)
        for batch in batches
    ])

    # Flatten results
    all_results = [item for batch in batch_results for item in batch]

    successful = sum(1 for r in all_results if r["success"])
    failed = sum(1 for r in all_results if not r["success"])

    return {
        "total": len(item_ids),
        "batches_processed": len(batches),
        "successful": successful,
        "failed": failed,
        "success_rate": round(successful / len(item_ids) * 100, 2)
    }
```

### Batch with Progress Tracking

```python
@task(queue="processing")
async def batch_with_progress(item_ids: list, batch_size: int = 100):
    """Process items in batches with progress tracking."""
    from asgiref.sync import sync_to_async
    from myapp.models import Item, ProcessingProgress

    @sync_to_async
    def update_progress(total, processed, successful, failed):
        progress, _ = ProcessingProgress.objects.update_or_create(
            task_id=self.job_id,
            defaults={
                "total": total,
                "processed": processed,
                "successful": successful,
                "failed": failed,
                "percentage": round(processed / total * 100, 2)
            }
        )
        return progress

    total = len(item_ids)
    processed = 0
    successful = 0
    failed = 0

    # Process in batches
    for i in range(0, total, batch_size):
        batch_ids = item_ids[i:i + batch_size]

        # Process batch
        for item_id in batch_ids:
            try:
                await process_single_item_by_id(item_id)
                successful += 1
            except Exception as e:
                failed += 1

            processed += 1

        # Update progress after each batch
        await update_progress(total, processed, successful, failed)

    return {
        "total": total,
        "successful": successful,
        "failed": failed,
        "success_rate": round(successful / total * 100, 2)
    }
```

### Real-World Example: Archive Vectorization

```python
@task(queue="knowbase", job_retry=2, job_retry_after=120)
async def vectorize_archive_items_task(archive_id: str, user_id: str):
    """
    Vectorize all items in a document archive.

    Production example showing:
    - Batch processing with embeddings
    - Cost tracking
    - Progress monitoring
    - Error recovery
    """
    from asgiref.sync import sync_to_async
    from knowbase.models import DocumentArchive
    from knowbase.services.archive import ArchiveVectorizationService

    @sync_to_async
    def get_archive_and_user():
        archive = DocumentArchive.objects.all_users().get(pk=archive_id)
        user = User.objects.get(pk=user_id)
        return archive, user

    @sync_to_async
    def verify_ownership(archive, user):
        return archive.user_id == user.id

    @sync_to_async
    def vectorize_items(service, archive):
        return service.vectorize_archive_items(archive)

    try:
        # Get archive and user
        archive, user = await get_archive_and_user()

        # Verify ownership
        if not await verify_ownership(archive, user):
            raise ArchiveProcessingError(
                message=f"User {user_id} does not own archive {archive_id}",
                code="UNAUTHORIZED_ACCESS"
            )

        # Initialize vectorization service
        service = ArchiveVectorizationService(user=user)

        # Vectorize archive items (batched internally)
        vectorized_count = await vectorize_items(service, archive)

        return {
            "success": True,
            "archive_id": archive_id,
            "vectorized_count": vectorized_count
        }

    except DocumentArchive.DoesNotExist:
        raise ArchiveProcessingError(
            message=f"Archive {archive_id} not found",
            code="ARCHIVE_NOT_FOUND"
        )
    except Exception as e:
        raise ArchiveProcessingError(
            message=f"Archive vectorization failed: {str(e)}",
            code="VECTORIZATION_FAILED"
        )
```

---

## 7. View Integration

### Basic Async View with Task

```python
from django.http import JsonResponse
from myapp.tasks import process_data

async def process_view(request):
    """Async view that schedules task."""
    import json

    data = json.loads(request.body)

    # Schedule task
    job = await process_data.delay(data=data)

    return JsonResponse({
        "job_id": job.job_id,
        "status": "processing",
        "message": "Task scheduled successfully",
        "poll_url": f"/api/tasks/{job.job_id}/status/"
    })
```

### View with Result Polling

```python
from django.http import JsonResponse
from django_cfg.apps.tasks.models import Job, JobResult

async def start_task_view(request):
    """Start long-running task."""
    from myapp.tasks import long_running_task

    job = await long_running_task.delay(arg1="value")

    return JsonResponse({
        "job_id": job.job_id,
        "poll_url": f"/api/tasks/{job.job_id}/status/",
        "message": "Task started"
    })

async def check_task_status_view(request, job_id):
    """Check task status."""
    try:
        job = await Job.objects.aget(job_id=job_id)

        response = {
            "job_id": job.job_id,
            "status": job.status,
            "enqueued_at": job.enqueue_time.isoformat() if job.enqueue_time else None,
        }

        if job.status == "complete":
            result = await JobResult.objects.filter(job=job).afirst()
            if result:
                response["result"] = result.result
                response["success"] = result.success

        return JsonResponse(response)

    except Job.DoesNotExist:
        return JsonResponse(
            {"error": "Job not found"},
            status=404
        )
```

### View with Timeout

```python
async def process_with_timeout_view(request):
    """Process with timeout."""
    from myapp.tasks import quick_task
    import json

    data = json.loads(request.body)

    # Schedule task
    job = await quick_task.delay(data=data)

    # Wait for result (5 seconds max)
    result = await job.result(timeout=5)

    if result:
        return JsonResponse({
            "success": result.success,
            "result": result.result,
            "completed_at": result.finish_time.isoformat() if result.finish_time else None
        })
    else:
        return JsonResponse({
            "status": "timeout",
            "job_id": job.job_id,
            "message": "Task still processing",
            "poll_url": f"/api/tasks/{job.job_id}/status/"
        }, status=202)
```

### File Upload with Background Processing

```python
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from myapp.tasks import process_uploaded_file

@require_http_methods(["POST"])
async def upload_and_process_view(request):
    """Upload file and process in background."""
    uploaded_file = request.FILES.get("file")

    if not uploaded_file:
        return JsonResponse(
            {"error": "No file uploaded"},
            status=400
        )

    # Save file temporarily
    import os
    from django.conf import settings

    upload_dir = os.path.join(settings.MEDIA_ROOT, "uploads")
    os.makedirs(upload_dir, exist_ok=True)

    file_path = os.path.join(upload_dir, uploaded_file.name)

    with open(file_path, "wb+") as destination:
        for chunk in uploaded_file.chunks():
            destination.write(chunk)

    # Schedule processing task
    job = await process_uploaded_file.delay(
        file_path=file_path,
        user_id=request.user.id
    )

    return JsonResponse({
        "job_id": job.job_id,
        "filename": uploaded_file.name,
        "status": "processing",
        "poll_url": f"/api/tasks/{job.job_id}/status/"
    })
```

### Bulk Action View

```python
async def bulk_delete_view(request):
    """Bulk delete items in background."""
    import json
    from myapp.tasks import bulk_delete_items

    data = json.loads(request.body)
    item_ids = data.get("item_ids", [])

    if not item_ids:
        return JsonResponse(
            {"error": "No items specified"},
            status=400
        )

    # Schedule bulk delete task
    job = await bulk_delete_items.delay(
        item_ids=item_ids,
        user_id=request.user.id
    )

    return JsonResponse({
        "job_id": job.job_id,
        "items_count": len(item_ids),
        "status": "processing",
        "message": f"Deleting {len(item_ids)} items in background"
    })
```

---

## 8. API Integration

### DRF ViewSet with Tasks

```python
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from myapp.serializers import DataSerializer
from myapp.tasks import process_data

class DataViewSet(viewsets.ModelViewSet):
    """ViewSet with background task processing."""

    serializer_class = DataSerializer

    @action(detail=True, methods=["post"])
    async def process(self, request, pk=None):
        """Process data in background."""
        obj = await self.aget_object()

        # Schedule processing task
        job = await process_data.delay(data_id=obj.id)

        return Response({
            "job_id": job.job_id,
            "status": "processing",
            "poll_url": f"/api/tasks/{job.job_id}/status/"
        }, status=status.HTTP_202_ACCEPTED)

    @action(detail=False, methods=["post"])
    async def bulk_process(self, request):
        """Bulk process multiple items."""
        from myapp.tasks import bulk_process_items

        item_ids = request.data.get("item_ids", [])

        if not item_ids:
            return Response(
                {"error": "No items specified"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Schedule bulk processing
        job = await bulk_process_items.delay(item_ids=item_ids)

        return Response({
            "job_id": job.job_id,
            "items_count": len(item_ids),
            "status": "processing"
        }, status=status.HTTP_202_ACCEPTED)
```

### Task Status Endpoint

```python
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django_cfg.apps.tasks.models import Job, JobResult

class TaskStatusView(APIView):
    """API endpoint for checking task status."""

    async def get(self, request, job_id):
        """Get task status."""
        try:
            job = await Job.objects.aget(job_id=job_id)

            response_data = {
                "job_id": job.job_id,
                "status": job.status,
                "task_name": job.task,
                "enqueued_at": job.enqueue_time.isoformat() if job.enqueue_time else None,
                "started_at": job.start_time.isoformat() if job.start_time else None,
            }

            if job.status == "complete":
                result = await JobResult.objects.filter(job=job).afirst()
                if result:
                    response_data.update({
                        "completed_at": result.finish_time.isoformat() if result.finish_time else None,
                        "success": result.success,
                        "result": result.result
                    })
            elif job.status == "failed":
                response_data["error"] = "Task failed"

            return Response(response_data)

        except Job.DoesNotExist:
            return Response(
                {"error": "Job not found"},
                status=status.HTTP_404_NOT_FOUND
            )
```

### Webhook Integration

```python
from rest_framework.views import APIView
from rest_framework.response import Response
from myapp.tasks import process_webhook

class WebhookView(APIView):
    """Handle webhook and process in background."""

    authentication_classes = []  # Webhook-specific auth

    async def post(self, request):
        """Receive webhook and schedule processing."""
        webhook_data = request.data

        # Validate webhook signature (if applicable)
        if not await self.validate_webhook(request):
            return Response(
                {"error": "Invalid signature"},
                status=status.HTTP_401_UNAUTHORIZED
            )

        # Schedule webhook processing
        job = await process_webhook.delay(data=webhook_data)

        return Response({
            "received": True,
            "job_id": job.job_id
        }, status=status.HTTP_202_ACCEPTED)

    async def validate_webhook(self, request):
        """Validate webhook signature."""
        # Implement your webhook validation logic
        return True
```

### Export API with Progress

```python
from rest_framework.views import APIView
from rest_framework.response import Response
from myapp.tasks import export_data

class ExportView(APIView):
    """Export data with progress tracking."""

    async def post(self, request):
        """Start export."""
        export_format = request.data.get("format", "csv")
        filters = request.data.get("filters", {})

        # Schedule export task
        job = await export_data.delay(
            user_id=request.user.id,
            format=export_format,
            filters=filters
        )

        return Response({
            "job_id": job.job_id,
            "status": "processing",
            "progress_url": f"/api/export/{job.job_id}/progress/",
            "download_url": f"/api/export/{job.job_id}/download/"
        }, status=status.HTTP_202_ACCEPTED)

    async def get(self, request, job_id):
        """Get export status and download link."""
        from django_cfg.apps.tasks.models import Job, JobResult

        try:
            job = await Job.objects.aget(job_id=job_id)

            if job.status == "complete":
                result = await JobResult.objects.filter(job=job).afirst()
                if result and result.success:
                    file_url = result.result.get("file_url")
                    return Response({
                        "status": "complete",
                        "download_url": file_url
                    })

            return Response({
                "status": job.status,
                "message": "Export in progress"
            })

        except Job.DoesNotExist:
            return Response(
                {"error": "Export job not found"},
                status=status.HTTP_404_NOT_FOUND
            )
```

---

## 9. Signal Integration

### Post-Save Signal

```python
# models.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from asgiref.sync import async_to_sync
from myapp.models import User
from myapp.tasks import send_welcome_email, create_user_profile

@receiver(post_save, sender=User)
def user_created(sender, instance, created, **kwargs):
    """Send welcome email and create profile when user is created."""
    if created:
        # Schedule welcome email
        async_to_sync(send_welcome_email.delay)(
            user_id=instance.id,
            email=instance.email
        )

        # Schedule profile creation
        async_to_sync(create_user_profile.delay)(
            user_id=instance.id
        )

# tasks.py
@task(queue="emails")
async def send_welcome_email(user_id: int, email: str):
    """Send welcome email to new user."""
    from asgiref.sync import sync_to_async
    from myapp.models import User

    user = await sync_to_async(User.objects.get)(id=user_id)

    # Send email
    await send_email(
        to=email,
        subject="Welcome to Our Platform!",
        template="welcome_email.html",
        context={"user": user}
    )

    return {"email_sent": True, "user_id": user_id}

@task(queue="default")
async def create_user_profile(user_id: int):
    """Create user profile asynchronously."""
    from asgiref.sync import sync_to_async
    from myapp.models import User, Profile

    user = await sync_to_async(User.objects.get)(id=user_id)

    profile = await sync_to_async(Profile.objects.create)(
        user=user,
        bio="",
        avatar=""
    )

    return {"profile_created": True, "profile_id": profile.id}
```

### Pre-Delete Signal

```python
# models.py
from django.db.models.signals import pre_delete
from django.dispatch import receiver
from asgiref.sync import async_to_sync
from myapp.models import Document
from myapp.tasks import cleanup_document_files, archive_document

@receiver(pre_delete, sender=Document)
def document_pre_delete(sender, instance, **kwargs):
    """Clean up files and archive document before deletion."""
    # Archive document data
    async_to_sync(archive_document.delay)(
        document_id=instance.id,
        document_data={
            "title": instance.title,
            "content": instance.content,
            "metadata": instance.metadata
        }
    )

    # Schedule file cleanup
    if instance.file_path:
        async_to_sync(cleanup_document_files.delay)(
            file_path=instance.file_path
        )

# tasks.py
@task(queue="cleanup")
async def cleanup_document_files(file_path: str):
    """Delete document files from storage."""
    import os
    import aiofiles.os

    if os.path.exists(file_path):
        await aiofiles.os.remove(file_path)

    return {"file_deleted": True, "file_path": file_path}

@task(queue="archival")
async def archive_document(document_id: int, document_data: dict):
    """Archive document to long-term storage."""
    from asgiref.sync import sync_to_async
    from myapp.models import ArchivedDocument

    archive = await sync_to_async(ArchivedDocument.objects.create)(
        original_id=document_id,
        data=document_data,
        archived_at=timezone.now()
    )

    return {"archived": True, "archive_id": archive.id}
```

### M2M Changed Signal

```python
# models.py
from django.db.models.signals import m2m_changed
from django.dispatch import receiver
from asgiref.sync import async_to_sync
from myapp.models import Project
from myapp.tasks import notify_team_members, update_project_permissions

@receiver(m2m_changed, sender=Project.members.through)
def project_members_changed(sender, instance, action, pk_set, **kwargs):
    """Handle project member changes."""
    if action == "post_add":
        # New members added
        async_to_sync(notify_team_members.delay)(
            project_id=instance.id,
            member_ids=list(pk_set),
            action="added"
        )

        # Update permissions
        async_to_sync(update_project_permissions.delay)(
            project_id=instance.id,
            member_ids=list(pk_set)
        )

    elif action == "post_remove":
        # Members removed
        async_to_sync(notify_team_members.delay)(
            project_id=instance.id,
            member_ids=list(pk_set),
            action="removed"
        )

# tasks.py
@task(queue="notifications")
async def notify_team_members(project_id: int, member_ids: list, action: str):
    """Notify team members about project changes."""
    from asgiref.sync import sync_to_async
    from myapp.models import Project, User

    project = await sync_to_async(Project.objects.get)(id=project_id)

    @sync_to_async
    def get_users():
        return list(User.objects.filter(id__in=member_ids))

    users = await get_users()

    for user in users:
        if action == "added":
            await send_notification(
                user=user,
                message=f"You have been added to project: {project.name}"
            )
        elif action == "removed":
            await send_notification(
                user=user,
                message=f"You have been removed from project: {project.name}"
            )

    return {"notified_users": len(users)}
```

### Custom Signal

```python
# signals.py
from django.dispatch import Signal

payment_completed = Signal()
order_status_changed = Signal()

# models.py
from asgiref.sync import async_to_sync
from .signals import payment_completed
from myapp.tasks import process_payment_completion

class Payment(models.Model):
    # ... fields ...

    def mark_as_completed(self):
        """Mark payment as completed and send signal."""
        self.status = "completed"
        self.completed_at = timezone.now()
        self.save()

        # Send signal
        payment_completed.send(
            sender=self.__class__,
            payment=self,
            amount=self.amount
        )

# receivers.py
from django.dispatch import receiver
from asgiref.sync import async_to_sync
from .signals import payment_completed
from myapp.tasks import process_payment_completion, send_payment_receipt

@receiver(payment_completed)
def handle_payment_completion(sender, payment, amount, **kwargs):
    """Handle payment completion."""
    # Process payment completion
    async_to_sync(process_payment_completion.delay)(
        payment_id=payment.id
    )

    # Send receipt
    async_to_sync(send_payment_receipt.delay)(
        payment_id=payment.id,
        user_email=payment.user.email
    )

# tasks.py
@task(queue="payments")
async def process_payment_completion(payment_id: int):
    """Process completed payment."""
    from asgiref.sync import sync_to_async
    from myapp.models import Payment, Order

    payment = await sync_to_async(Payment.objects.get)(id=payment_id)

    # Update order status
    if payment.order:
        order = payment.order
        order.status = "paid"
        await sync_to_async(order.save)()

    # Record in accounting system
    await record_payment_in_accounting(payment)

    return {"processed": True, "payment_id": payment_id}
```

---

## 10. Testing Tasks

### Basic Task Test

```python
import pytest
from myapp.tasks import add_numbers

@pytest.mark.asyncio
async def test_add_numbers():
    """Test add_numbers task."""
    job = await add_numbers.delay(a=5, b=3)

    # Wait for result
    result = await job.result(timeout=5)

    assert result is not None
    assert result.success is True
    assert result.result == 8
```

### Test with Mock

```python
import pytest
from unittest.mock import patch, AsyncMock

@pytest.mark.asyncio
@patch("myapp.tasks.external_api_call", new_callable=AsyncMock)
async def test_task_with_mock(mock_api_call):
    """Test task with mocked dependency."""
    mock_api_call.return_value = {"data": "mocked"}

    from myapp.tasks import process_api_data

    job = await process_api_data.delay(url="https://api.example.com")
    result = await job.result(timeout=5)

    assert result.success is True
    assert result.result["data"] == "mocked"
    mock_api_call.assert_called_once()
```

### Test Task Function Directly

```python
@pytest.mark.asyncio
async def test_task_function_directly():
    """Test task function directly without worker."""
    from myapp.tasks import process_data

    # Call task function directly (bypass queue)
    result = await process_data._function(
        data={"key": "value"}
    )

    assert result["processed"] is True
    assert result["items"] == 1
```

### Test with Django ORM

```python
import pytest
from django.contrib.auth import get_user_model
from myapp.tasks import update_user_profile

User = get_user_model()

@pytest.mark.asyncio
@pytest.mark.django_db
async def test_update_user_profile():
    """Test user profile update task."""
    # Create test user
    from asgiref.sync import sync_to_async

    user = await sync_to_async(User.objects.create_user)(
        username="testuser",
        email="test@example.com"
    )

    # Schedule task
    job = await update_user_profile.delay(
        user_id=user.id,
        data={
            "first_name": "John",
            "last_name": "Doe"
        }
    )

    # Wait for result
    result = await job.result(timeout=5)

    assert result.success is True

    # Verify database was updated
    user = await sync_to_async(User.objects.get)(id=user.id)
    assert user.first_name == "John"
    assert user.last_name == "Doe"
```

### Test Retry Logic

```python
import pytest
from unittest.mock import patch, AsyncMock
from myapp.tasks import task_with_retry

@pytest.mark.asyncio
@patch("myapp.tasks.external_service")
async def test_task_retry(mock_service):
    """Test task retry behavior."""
    # First two calls fail, third succeeds
    mock_service.call = AsyncMock(
        side_effect=[
            Exception("Network error"),
            Exception("Timeout"),
            {"success": True}
        ]
    )

    # This should eventually succeed after retries
    job = await task_with_retry.delay()
    result = await job.result(timeout=30)

    assert result.success is True
    assert mock_service.call.call_count == 3
```

### Test Error Handling

```python
import pytest
from myapp.tasks import task_with_error_handling

@pytest.mark.asyncio
async def test_task_error_handling():
    """Test task error handling."""
    # Pass invalid data to trigger error
    job = await task_with_error_handling.delay(
        invalid_param="bad_value"
    )

    result = await job.result(timeout=5)

    # Task should handle error gracefully
    assert result is not None
    assert result.success is False
    assert "error" in result.result
```

### Integration Test with Worker

```python
import pytest

@pytest.mark.asyncio
@pytest.mark.integration
async def test_with_worker():
    """Integration test with actual worker.

    Note: Requires worker to be running during test.
    """
    from myapp.tasks import send_email

    job = await send_email.delay(
        to="test@example.com",
        subject="Test",
        body="Test email"
    )

    # Wait for worker to process
    result = await job.result(timeout=10)

    assert result is not None
    assert result.success is True
    assert result.result["sent"] is True
```

### Test Cron Task

```python
import pytest
from myapp.tasks import daily_cleanup

@pytest.mark.asyncio
@pytest.mark.django_db
async def test_daily_cleanup():
    """Test cron task for daily cleanup."""
    from datetime import datetime, timedelta
    from asgiref.sync import sync_to_async
    from myapp.models import TempFile

    # Create old files
    old_date = datetime.now() - timedelta(days=8)

    old_file = await sync_to_async(TempFile.objects.create)(
        filename="old.txt",
        created_at=old_date
    )

    recent_file = await sync_to_async(TempFile.objects.create)(
        filename="recent.txt"
    )

    # Run cleanup task
    result = await daily_cleanup._function()

    # Verify old file was deleted
    old_exists = await sync_to_async(
        TempFile.objects.filter(id=old_file.id).exists
    )()

    recent_exists = await sync_to_async(
        TempFile.objects.filter(id=recent_file.id).exists
    )()

    assert old_exists is False
    assert recent_exists is True
    assert result["deleted"] == 1
```

### Pytest Fixtures for Tasks

```python
# conftest.py
import pytest
from django_cfg.apps.tasks import get_rearq_client

@pytest.fixture
async def rearq_client():
    """Get ReArq client for testing."""
    client = get_rearq_client()
    yield client
    # Cleanup if needed

@pytest.fixture
async def clear_queue(rearq_client):
    """Clear task queue before test."""
    redis = rearq_client.redis
    await redis.flushdb()
    yield
    await redis.flushdb()

# Use in tests
@pytest.mark.asyncio
async def test_with_clear_queue(clear_queue):
    """Test with clean queue."""
    from myapp.tasks import my_task

    job = await my_task.delay(arg="value")
    result = await job.result(timeout=5)

    assert result.success is True
```

### Test Task Performance

```python
import pytest
import time
from myapp.tasks import performance_critical_task

@pytest.mark.asyncio
async def test_task_performance():
    """Test task completes within time limit."""
    start_time = time.time()

    job = await performance_critical_task.delay(items=100)
    result = await job.result(timeout=10)

    duration = time.time() - start_time

    assert result.success is True
    assert duration < 5.0, f"Task took {duration}s, expected < 5s"
```

---

## Production Tips

### 1. Configuration Best Practices

```python
# Production configuration
from django_cfg import DjangoConfig
from django_cfg.models.tasks import TaskConfig, RearqConfig

class ProductionConfig(DjangoConfig):
    tasks = TaskConfig(
        enabled=True,
        rearq=RearqConfig(
            # Core settings
            redis_url=env("REDIS_URL"),
            db_url=env("DATABASE_URL"),

            # Performance
            max_jobs=20,              # Tune based on server capacity
            job_timeout=600,          # 10 minutes default

            # Reliability
            job_retry=3,              # Retry failed jobs
            job_retry_after=120,      # 2 minutes between retries

            # Monitoring
            server_enabled=True,
            server_host="0.0.0.0",
            server_port=8001,

            # Maintenance
            keep_job_days=30,         # Keep job history for 30 days

            # Advanced
            logs_dir="/var/log/rearq",
            raise_job_error=False,    # Don't crash on task errors
        )
    )
```

### 2. Queue Strategy

```python
# Use different queues for different priorities
QUEUE_STRATEGY = {
    "critical": {  # User-facing, must be fast
        "tasks": ["send_verification_code", "process_payment"],
        "workers": 5,
        "max_jobs": 10
    },
    "high": {  # Important but not critical
        "tasks": ["send_email", "update_cache"],
        "workers": 3,
        "max_jobs": 20
    },
    "default": {  # Normal priority
        "tasks": ["process_order", "generate_report"],
        "workers": 2,
        "max_jobs": 30
    },
    "low": {  # Can wait
        "tasks": ["cleanup_old_files", "archive_data"],
        "workers": 1,
        "max_jobs": 50
    }
}
```

### 3. Error Handling Strategy

```python
@task(queue="default", job_retry=3)
async def production_task_with_errors():
    """Production task with comprehensive error handling."""
    try:
        result = await perform_operation()
        return {"success": True, "result": result}

    except TemporaryError as e:
        # Retryable error - re-raise to trigger retry
        logger.warning(f"Temporary error, will retry: {e}")
        raise

    except PermanentError as e:
        # Permanent error - log and return failure
        logger.error(f"Permanent error: {e}")
        return {"success": False, "error": str(e)}

    except Exception as e:
        # Unexpected error - log with full context
        logger.error(f"Unexpected error: {e}", exc_info=True, extra={
            "task_name": "production_task_with_errors",
            "context": {"some": "context"}
        })
        raise
```

### 4. Monitoring and Alerting

```python
@cron_task(cron="*/5 * * * *")  # Every 5 minutes
async def monitor_task_health():
    """Monitor task system health."""
    from django_cfg.apps.tasks.models import Job
    from datetime import datetime, timedelta

    # Check for stuck jobs
    stuck_threshold = datetime.now() - timedelta(hours=1)
    stuck_jobs = await Job.objects.filter(
        status="in_progress",
        start_time__lt=stuck_threshold
    ).acount()

    if stuck_jobs > 0:
        await send_alert(f"Found {stuck_jobs} stuck jobs")

    # Check failure rate
    recent = datetime.now() - timedelta(minutes=5)
    total_jobs = await Job.objects.filter(
        enqueue_time__gte=recent
    ).acount()

    failed_jobs = await Job.objects.filter(
        status="failed",
        enqueue_time__gte=recent
    ).acount()

    failure_rate = (failed_jobs / total_jobs * 100) if total_jobs > 0 else 0

    if failure_rate > 10:  # More than 10% failure
        await send_alert(f"High failure rate: {failure_rate:.1f}%")

    return {
        "stuck_jobs": stuck_jobs,
        "failure_rate": failure_rate,
        "total_jobs": total_jobs
    }
```

---

**End of Examples**

This comprehensive guide covers all major use cases for ReArq task integration in django-cfg projects. For additional information, see:

- [Configuration Guide](./configuration)
- [Deployment Guide](./deployment)
- [Monitoring Guide](./monitoring)

---

## See Also

### Getting Started
- **[First Project](/getting-started/first-project)** - Your first django-cfg project

### Built-in Apps with Task Examples
- **[AI Knowledge Base](/features/built-in-apps/ai-knowledge/overview)** - Real-world task usage for document processing
- **[Operations App](/features/built-in-apps/operations/tasks)** - Background task examples

### Testing
- **[Troubleshooting](/guides/troubleshooting)** - Debug task issues

### Advanced Topics
- **[Multi-Database](/guides/multi-database)** - Task data in separate database
