---
title: Tasks Module Overview
description: Django-CFG overview feature guide. Production-ready tasks module overview with built-in validation, type safety, and seamless Django integration.
sidebar_label: Overview
sidebar_position: 1
keywords:
  - django-cfg overview
  - django overview
  - overview django-cfg
---

# Django Tasks Module

The **django_tasks module** (`django_cfg.modules.django_tasks`) provides a service layer for background task processing using ReArq.

## ⚠️ Module vs App Clarification

Django-CFG has TWO separate "tasks" components:

| Component | Type | Purpose | Import Path |
|-----------|------|---------|-------------|
| **Tasks Module** | Service Layer | Execute background tasks | `django_cfg.modules.django_tasks` |
| **Tasks App** | Django App | Track & monitor tasks (UI/DB) | `django_cfg.apps.tasks` |

**This document covers the MODULE** (service layer). For the Django app with models and admin UI, see [Built-in Apps - Tasks](/features/built-in-apps/operations/tasks).

---

## Quick Start

### Basic Task Definition

```python
from django_cfg.modules.django_tasks import task

@task
def send_email_notification(user_id: int, message: str):
    """Background task for sending email notifications"""
    from django.contrib.auth import get_user_model

    User = get_user_model()
    user = User.objects.get(id=user_id)

    # Send email
    send_mail(
        subject="Notification",
        message=message,
        from_email="noreply@example.com",
        recipient_list=[user.email]
    )

    return f"Email sent to {user.email}"

# Call task asynchronously
send_email_notification.send(user_id=123, message="Hello!")
```

### Task Manager

```python
from django_cfg.modules.django_tasks import DjangoTasks

# Create task manager instance
tasks = DjangoTasks()

# Get queue statistics
stats = tasks.get_queue_stats()
print(f"Pending tasks: {stats['pending']}")
print(f"Active workers: {stats['workers']}")

# Clear failed tasks
tasks.clear_failed_tasks()

# Schedule periodic task
tasks.schedule_periodic_task(
    task_name="cleanup_old_sessions",
    task_function=cleanup_sessions,
    interval_seconds=3600  # Every hour
)
```

---

## Module Components

### 1. `@task` Decorator

Converts a function into a background task:

```python
from django_cfg.modules.django_tasks import task

@task(
    queue_name="emails",  # Custom queue
    max_retries=3,        # Retry failed tasks
    priority=10,          # Task priority (higher = more important)
    time_limit=60000      # Timeout in milliseconds
)
def process_large_dataset(dataset_id: int):
    """Process dataset in background"""
    dataset = Dataset.objects.get(id=dataset_id)

    # Heavy processing
    for record in dataset.records.all():
        process_record(record)

    return f"Processed {dataset.records.count()} records"

# Synchronous execution (for testing)
result = process_large_dataset(dataset_id=456)

# Asynchronous execution (production)
process_large_dataset.send(dataset_id=456)

# Delayed execution (schedule for later)
process_large_dataset.send_with_options(
    args=(456,),
    delay=3600000  # 1 hour delay in milliseconds
)
```

### 2. `DjangoTasks` Class

Task management and monitoring:

```python
from django_cfg.modules.django_tasks import DjangoTasks

class TaskManager:
    def __init__(self):
        self.tasks = DjangoTasks()

    def get_system_health(self):
        """Get task system health status"""
        stats = self.tasks.get_queue_stats()

        return {
            'status': 'healthy' if stats['workers'] > 0 else 'unhealthy',
            'pending_tasks': stats['pending'],
            'active_workers': stats['workers'],
            'failed_tasks': stats.get('failed', 0)
        }

    def retry_failed_tasks(self, queue_name: str = "default"):
        """Retry all failed tasks in a queue"""
        failed = self.tasks.get_failed_tasks(queue=queue_name)

        for task_data in failed:
            task_id = task_data['message_id']
            self.tasks.retry_task(task_id)

        return f"Retried {len(failed)} failed tasks"

    def pause_queue(self, queue_name: str):
        """Pause task processing for a queue"""
        self.tasks.pause_queue(queue_name)

    def resume_queue(self, queue_name: str):
        """Resume task processing for a queue"""
        self.tasks.resume_queue(queue_name)
```

### 3. `get_task_service()` Function

Access the global task service:

```python
from django_cfg.modules.django_tasks import get_task_service

def admin_dashboard_view(request):
    """Admin dashboard showing task statistics"""
    task_service = get_task_service()

    # Get real-time statistics
    stats = {
        'total_queues': len(task_service.get_all_queues()),
        'pending_tasks': task_service.count_pending_tasks(),
        'completed_today': task_service.count_completed_tasks(hours=24),
        'failed_tasks': task_service.count_failed_tasks(),
    }

    return render(request, 'admin/tasks_dashboard.html', stats)
```

---

## Configuration

### Via TaskConfig

Use `TaskConfig` for type-safe configuration:

```python
from django_cfg import DjangoConfig, TaskConfig

class MyConfig(DjangoConfig):
    tasks: TaskConfig = TaskConfig(
        broker_url="redis://localhost:6379/0",
        worker_concurrency=8,
        task_timeout=300,
        max_retries=3,
        retry_delay=60,
        queues=["default", "emails", "processing"]
    )
```

See [TaskConfig documentation](/fundamentals/configuration) for all options.

### Direct ReArq Configuration

For advanced ReArq configuration:

```python
# config.py
from django_cfg import DjangoConfig

class MyConfig(DjangoConfig):
    @property
    def rearq_settings(self) -> dict:
        return {
            'REDIS_URL': 'redis://localhost:6379/0',
            'REDIS_POOL_SETTINGS': {
                'max_connections': 20
            },
            'TASK_TIMEOUT': 300,
            'MAX_RETRIES': 3,
            'RETRY_DELAY': 60,
            'KEEP_RESULTS': 3600
        }
```

---

## Common Patterns

### Pattern 1: Email Queue

```python
from django_cfg.modules.django_tasks import task

@task(queue_name="emails", priority=10)
def send_welcome_email(user_id: int):
    """Send welcome email to new user"""
    user = User.objects.get(id=user_id)

    send_mail(
        subject=f"Welcome {user.username}!",
        message="Thank you for joining...",
        from_email="welcome@myapp.com",
        recipient_list=[user.email]
    )

@task(queue_name="emails", priority=5)
def send_bulk_newsletter(newsletter_id: int):
    """Send newsletter to all subscribers"""
    newsletter = Newsletter.objects.get(id=newsletter_id)

    for subscriber in newsletter.subscribers.all():
        send_mail(
            subject=newsletter.subject,
            message=newsletter.content,
            from_email="newsletter@myapp.com",
            recipient_list=[subscriber.email]
        )
```

### Pattern 2: Data Processing Pipeline

```python
from django_cfg.modules.django_tasks import task

@task(queue_name="processing")
def extract_data(source_id: int):
    """Step 1: Extract data from source"""
    data = extract_from_source(source_id)

    # Chain to next step
    transform_data.send(data=data)

    return f"Extracted {len(data)} records"

@task(queue_name="processing")
def transform_data(data: dict):
    """Step 2: Transform extracted data"""
    transformed = apply_transformations(data)

    # Chain to next step
    load_data.send(data=transformed)

    return f"Transformed {len(transformed)} records"

@task(queue_name="processing")
def load_data(data: dict):
    """Step 3: Load data into database"""
    bulk_create_records(data)

    return f"Loaded {len(data)} records"
```

### Pattern 3: Scheduled Maintenance

```python
from django_cfg.modules.django_tasks import DjangoTasks, task

tasks = DjangoTasks()

@task
def cleanup_old_sessions():
    """Remove expired sessions"""
    from django.contrib.sessions.models import Session
    Session.objects.filter(expire_date__lt=now()).delete()

@task
def backup_database():
    """Create daily database backup"""
    subprocess.run(["pg_dump", "mydb", "-f", f"backup-{now().date()}.sql"])

# Schedule periodic tasks
tasks.schedule_periodic_task("cleanup", cleanup_old_sessions, interval_seconds=3600)
tasks.schedule_periodic_task("backup", backup_database, interval_seconds=86400)
```

---

## Integration with Tasks App

The **Tasks Module** (this) can work with the **Tasks App** for persistence:

```python
from django_cfg.modules.django_tasks import task
from django_cfg.apps.tasks.models import TaskResult  # From the app

@task
def tracked_task(data: dict):
    """Task that stores results in database"""

    # Execute task
    result = process_data(data)

    # Store result in database (using Tasks App)
    TaskResult.objects.create(
        task_name="tracked_task",
        status="completed",
        result=result,
        executed_at=now()
    )

    return result
```

---

## Comparison: Module vs App

### Use the MODULE (`django_cfg.modules.django_tasks`) when:
- ✅ Defining background tasks with `@task` decorator
- ✅ Managing task queues programmatically
- ✅ Accessing task service for monitoring
- ✅ Configuring ReArq workers

### Use the APP (`django_cfg.apps.tasks`) when:
- ✅ Storing task execution history in database
- ✅ Building admin UI for task monitoring
- ✅ Creating REST API endpoints for tasks
- ✅ Displaying task dashboards

### Both together:
Most projects use **both**:
- **Module** provides the execution engine
- **App** provides the tracking and UI layer

---

## Related Documentation

- [**TaskConfig**](/fundamentals/configuration) - Configuration options
- [**Tasks App**](/features/built-in-apps/operations/tasks) - Django app with models and UI
- [**ReArq Integration**](/features/integrations/rearq/overview) - Full ReArq documentation
- [**CLI Commands**](/cli/commands/overview) - `manage.py rearq` and task commands

---

TAGS: tasks, background-jobs, rearq, async, queue, workers, module
DEPENDS_ON: [rearq, configuration, redis]
USED_BY: [tasks-app, ai-agents, email, processing]
