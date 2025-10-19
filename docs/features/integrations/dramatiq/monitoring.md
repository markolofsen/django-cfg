---
title: Dramatiq Monitoring
description: Django-CFG monitoring feature guide. Production-ready dramatiq monitoring with built-in validation, type safety, and seamless Django integration.
sidebar_label: Monitoring
sidebar_position: 5
keywords:
  - django-cfg monitoring
  - django monitoring
  - monitoring django-cfg
---

# Dramatiq Monitoring

## Error Handling Examples

### Graceful Error Handling

```python
# tasks.py
import dramatiq
from dramatiq.middleware import CurrentMessage
import logging

logger = logging.getLogger(__name__)

@dramatiq.actor(max_retries=3)
def robust_task(data_id: int):
    """Task with comprehensive error handling"""
    message = CurrentMessage.get_current_message()

    try:
        # Main task logic
        data = process_data(data_id)

        # Success logging
        logger.info(f"Successfully processed data {data_id}")

    except RecoverableError as e:
        # Recoverable error - will retry
        logger.warning(f"Recoverable error for data {data_id}: {e}")
        raise  # Re-raise for retry

    except NonRecoverableError as e:
        # Non-recoverable error - don't retry
        logger.error(f"Non-recoverable error for data {data_id}: {e}")
        handle_permanent_failure(data_id, str(e))
        return  # Don't re-raise

    except Exception as e:
        # Unknown error - retry with exponential backoff
        retry_count = message.retries
        if retry_count >= 2:  # Last retry
            logger.error(f"Final retry failed for data {data_id}: {e}")
            handle_permanent_failure(data_id, str(e))
            return

        logger.warning(f"Retry {retry_count + 1} for data {data_id}: {e}")
        raise

def handle_permanent_failure(data_id: int, error_message: str):
    """Handle permanently failed tasks"""
    from myapp.models import DataRecord

    DataRecord.objects.filter(id=data_id).update(
        status="failed",
        error_message=error_message,
        failed_at=timezone.now()
    )

    # Notify administrators
    notify_admin_of_failure.send(data_id, error_message)
```

## Custom Middleware Example

```python
# middleware.py
import dramatiq
from dramatiq.middleware import Middleware
import logging
import time

logger = logging.getLogger(__name__)

class TaskTimingMiddleware(Middleware):
    """Middleware to log task execution times"""

    def before_process_message(self, broker, message):
        message.options["start_time"] = time.time()
        logger.info(f"Starting task {message.actor_name} with args {message.args}")

    def after_process_message(self, broker, message, *, result=None, exception=None):
        duration = time.time() - message.options.get("start_time", 0)

        if exception:
            logger.error(f"Task {message.actor_name} failed after {duration:.2f}s: {exception}")
        else:
            logger.info(f"Task {message.actor_name} completed in {duration:.2f}s")

# Add to configuration
class MyConfig(DjangoConfig):
    tasks: TaskConfig = TaskConfig(
        dramatiq=DramatiqConfig(
            middleware=[
                "dramatiq.middleware.AgeLimit",
                "dramatiq.middleware.TimeLimit",
                "dramatiq.middleware.Callbacks",
                "dramatiq.middleware.Retries",
                "myapp.middleware.TaskTimingMiddleware",  # Custom middleware
                "django_dramatiq.middleware.AdminMiddleware",
                "django_dramatiq.middleware.DbConnectionsMiddleware",
            ]
        )
    )
```

## Monitoring and Observability

### Prometheus Metrics

```python
# monitoring.py
from prometheus_client import Counter, Histogram, Gauge
import dramatiq

# Custom metrics
task_counter = Counter('dramatiq_tasks_total', 'Total tasks processed', ['task_name', 'status'])
task_duration = Histogram('dramatiq_task_duration_seconds', 'Task duration', ['task_name'])
queue_depth = Gauge('dramatiq_queue_depth', 'Queue depth', ['queue_name'])

@dramatiq.actor
def monitored_task(data_id: int):
    """Task with custom monitoring"""
    start_time = time.time()

    try:
        # Task logic here
        result = process_data(data_id)

        # Record success metrics
        task_counter.labels(task_name='monitored_task', status='success').inc()

        return result

    except Exception as e:
        # Record failure metrics
        task_counter.labels(task_name='monitored_task', status='failure').inc()
        raise

    finally:
        # Record duration
        duration = time.time() - start_time
        task_duration.labels(task_name='monitored_task').observe(duration)
```

### Health Check Endpoint

```python
# health.py
from django.http import JsonResponse
from django_cfg.modules.django_tasks import get_task_service

def task_health_check(request):
    """Health check endpoint for task system"""
    task_service = get_task_service()

    if not task_service.is_enabled():
        return JsonResponse({
            "status": "disabled",
            "message": "Task system is disabled"
        })

    try:
        # Check Redis connection
        redis_ok = task_service.check_redis_connection()

        # Check worker status
        workers = task_service.get_worker_stats()
        active_workers = len([w for w in workers if w['status'] == 'active'])

        # Check queue depths
        queues = task_service.get_queue_stats()
        total_pending = sum(q['pending'] for q in queues)

        return JsonResponse({
            "status": "healthy" if redis_ok and active_workers > 0 else "degraded",
            "redis_connection": redis_ok,
            "active_workers": active_workers,
            "total_workers": len(workers),
            "total_pending_tasks": total_pending,
            "queues": queues
        })

    except Exception as e:
        return JsonResponse({
            "status": "unhealthy",
            "error": str(e)
        }, status=500)
```

## Monitoring Best Practices

### Log Aggregation

When running multiple workers, consider implementing centralized logging:

```python
# logging_config.py
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'dramatiq': {
            'format': '[{asctime}] [{levelname}] [{name}] {message}',
            'style': '{',
        },
    },
    'handlers': {
        'dramatiq_file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': '/var/log/dramatiq/tasks.log',
            'maxBytes': 1024 * 1024 * 100,  # 100 MB
            'backupCount': 10,
            'formatter': 'dramatiq',
        },
    },
    'loggers': {
        'dramatiq': {
            'handlers': ['dramatiq_file'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}
```

### Alert Configuration

Set up alerts for critical task failures:

```python
# alerts.py
import dramatiq
from django.core.mail import mail_admins

@dramatiq.actor
def alert_on_critical_failure(task_name: str, error_message: str):
    """Send alert email on critical task failure"""
    subject = f"Critical Task Failure: {task_name}"
    message = f"""
    A critical task has failed:

    Task: {task_name}
    Error: {error_message}

    Please investigate immediately.
    """

    mail_admins(subject, message, fail_silently=False)
```

### Performance Monitoring

Track task performance metrics over time:

```python
# performance.py
from django.utils import timezone
from myapp.models import TaskMetric

def record_task_metrics(task_name: str, duration: float, success: bool):
    """Record task execution metrics"""
    TaskMetric.objects.create(
        task_name=task_name,
        duration=duration,
        success=success,
        timestamp=timezone.now()
    )
```

This comprehensive monitoring documentation provides patterns for error handling, custom middleware, metrics collection, and health checks to ensure your Dramatiq tasks run reliably in production.

## See Also

### Dramatiq Integration

**Core Documentation:**
- [**Dramatiq Overview**](./overview) - Background task processing introduction
- [**Configuration Guide**](./configuration) - Configure monitoring and middleware
- [**Task Examples**](./examples) - Real-world task patterns with monitoring
- [**Implementation Guide**](./implementation) - Implementation roadmap
- [**Testing Tasks**](./testing) - Test monitoring in background tasks

### Monitoring & Operations

**Infrastructure:**
- [**Logging Configuration**](/deployment/logging) - Structured task logging
- [**Docker Deployment**](/guides/docker/production) - Monitor containerized workers
- [**Production Config**](/guides/production-config) - Production monitoring setup

**Operations:**
- [**Operations Apps**](/features/built-in-apps/operations/overview) - Built-in monitoring
- [**Maintenance App**](/features/built-in-apps/operations/maintenance) - System health checks
- [**Tasks App**](/features/built-in-apps/operations/tasks) - Task management UI

### Configuration & Setup

**Getting Started:**
- [**Installation**](/getting-started/installation) - Install Django-CFG with monitoring
- [**Configuration Guide**](/getting-started/configuration) - Enable task monitoring
- [**Redis Configuration**](/fundamentals/configuration/cache) - Redis as message broker

**Advanced:**
- [**Configuration Models**](/fundamentals/configuration) - Monitoring config API
- [**Environment Detection**](/fundamentals/configuration/environment) - Environment-specific monitoring

### Tools & Troubleshooting

**CLI & Management:**
- [**Background Task Commands**](/cli/commands/background-tasks) - Monitor workers via CLI
- [**CLI Tools**](/cli/introduction) - Command-line monitoring tools
- [**Troubleshooting**](/guides/troubleshooting) - Debug task issues
