---
title: ReArq Background Tasks
description: Async Redis-based task queue with built-in monitoring for django-cfg
sidebar_position: 1
tags:
  - tasks
  - rearq
  - redis
  - async
  - background-jobs
  - cron
---

# ReArq Background Tasks

> **📚 Part of**: [Integrations](/features/integrations/overview) - Explore all django-cfg integrations

Async Redis-based task queue with Tortoise ORM persistence, built-in monitoring, and distributed task execution for django-cfg projects.

---

## Quick Navigation

### For Developers
- [Quick Start](#quick-start) - Get started in 5 minutes
- [Task Decorators](#task-decorators) - Define tasks with `@task` and `@cron_task`
- [Usage Examples](./examples) - Practical code examples
- [Configuration Reference](./configuration) - Complete configuration guide

### For DevOps
- [Configuration](#configuration) - Settings and environment setup
- [Deployment Guide](./deployment) - Production deployment
- [Monitoring](#monitoring) - Job tracking and worker status

---

## Key Features

### Async-First Design
- **Native Async/Await**: All operations use modern async Python
- **High Performance**: Non-blocking I/O for maximum throughput
- **Django Integration**: Works seamlessly with Django ORM via `sync_to_async`

### Redis-Backed Queue
- **Reliable**: Redis persistence ensures no job loss
- **Fast**: In-memory operations with sub-millisecond latency
- **Scalable**: Horizontal scaling with multiple workers
- **Distributed Locks**: Prevent concurrent execution of critical tasks

### Built-in Monitoring
- **Job Tracking**: Complete history of all task executions
- **REST API**: Query jobs, workers, and statistics
- **Django Admin**: View and manage tasks via admin interface
- **TaskLog Model**: Persistent execution logs with analytics

### Scheduled Tasks
- **Cron Support**: Schedule tasks with cron expressions
- **Run at Start**: Execute tasks immediately on worker startup
- **Timezone Aware**: Respects Django timezone settings

### Automatic Retries
- **Configurable**: Set retry count and delay per task
- **Exponential Backoff**: Optional progressive retry delays
- **Error Tracking**: Capture and store error messages

### Tortoise ORM Persistence
- **Job History**: All jobs stored in database
- **Result Storage**: Task outputs persisted automatically
- **Query Interface**: Rich filtering and analytics
- **Multi-DB Support**: Separate database for task data

---

## Implementation Status

| Component | Status | Notes |
|-----------|--------|-------|
| ReArq Client Wrapper | ✅ Complete | Thread-safe singleton with lazy initialization |
| Task Decorators | ✅ Complete | `@task` and `@cron_task` decorators |
| Configuration Model | ✅ Complete | `TaskConfig` with ReArq settings |
| TaskLog Model | ✅ Complete | 20 fields, 6 indexes, full ReArq compatibility |
| REST API | ✅ Complete | 7 endpoints with filtering and pagination |
| Django Admin | ✅ Complete | Job management and monitoring |
| Sync Utilities | ✅ Complete | ReArq Job/JobResult synchronization |
| Worker CLI | ✅ Complete | Native ReArq CLI: `rearq main:rearq worker` |
| Migration System | ✅ Complete | Database schema applied |
| Documentation | ✅ Complete | Full docs with examples |

---

## Quick Start

### 1. Configuration

Add ReArq configuration to your django-cfg settings:

```python
# config.py
from django_cfg import DjangoConfig
from django_cfg.models.tasks import TaskConfig, RearqConfig

class Config(DjangoConfig):
    project_name = "My Project"

    # Enable ReArq tasks
    tasks = TaskConfig(
        enabled=True,
        backend="rearq",
        rearq=RearqConfig(
            redis_url="redis://localhost:6379/0",
            db_url="sqlite:///./rearq.db",  # Or PostgreSQL
            max_jobs=10,
            job_timeout=300,
        ),
    )

config = Config()
```

### 2. Define Tasks

Create tasks using decorators:

```python
# myapp/tasks.py
from django_cfg.apps.tasks import task, cron_task

@task(queue="default")
async def send_email(to: str, subject: str, body: str):
    """Send email asynchronously."""
    # Your implementation
    return {"sent": True, "to": to}

@cron_task(cron="0 * * * *")  # Every hour
async def cleanup_old_data():
    """Clean up old records every hour."""
    from datetime import datetime, timedelta
    from asgiref.sync import sync_to_async
    from myapp.models import TempFile

    cutoff = datetime.now() - timedelta(days=7)
    deleted = await sync_to_async(
        TempFile.objects.filter(created_at__lt=cutoff).delete
    )()

    return {"deleted": deleted[0]}
```

### 3. Execute Tasks

Call tasks from views or other code:

```python
# myapp/views.py
from myapp.tasks import send_email

async def register_user(request):
    # ... create user ...

    # Schedule email task
    job = await send_email.delay(
        to=user.email,
        subject="Welcome!",
        body="Thanks for registering"
    )

    # Optional: wait for result
    result = await job.result(timeout=5)

    return JsonResponse({
        "job_id": job.job_id,
        "status": "scheduled"
    })
```

### 4. Run Workers

ReArq uses native CLI commands (not Django management commands). You need to create a `main.py` file that imports your Django app and defines tasks:

```python
# main.py (in your project root)
import os
import django

# Initialize Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'your_project.settings')
django.setup()

# Import ReArq client and tasks
from django_cfg.apps.tasks import get_rearq_client

rearq = get_rearq_client().rearq

# Import your task modules to register them
from myapp.tasks import *  # noqa
```

Start worker processes:

```bash
# Terminal 1: Start worker for specific queues
rearq main:rearq worker --queue default --queue high_priority

# Terminal 2: Start worker with timer for cron tasks
rearq main:rearq worker --with-timer

# Terminal 3: Start Django
python manage.py runserver
```

For Docker deployment, see the [Deployment Guide](./deployment.md).

---

## Configuration

### Minimal Configuration

```python
from django_cfg.models.tasks import TaskConfig, RearqConfig

tasks = TaskConfig(
    enabled=True,
    rearq=RearqConfig(
        redis_url="redis://localhost:6379/0",
    ),
)
```

### Production Configuration

```python
tasks = TaskConfig(
    enabled=True,
    backend="rearq",
    rearq=RearqConfig(
        # Core settings
        redis_url="redis://localhost:6379/0",
        db_url="postgresql://user:pass@localhost/tasks",

        # Worker settings
        max_jobs=20,              # Max concurrent jobs per worker
        job_timeout=600,          # Default timeout (10 minutes)
        job_retry=5,              # Default retry count
        job_retry_after=120,      # Retry delay (2 minutes)

        # Monitoring
        server_enabled=True,      # Enable ReArq monitoring server
        server_port=8001,

        # Cleanup
        keep_job_days=14,         # Delete jobs after 14 days

        # Advanced
        delay_queue_num=4,        # Delay queue shards
        logs_dir="/var/log/rearq",
    ),
)
```

### Redis Sentinel

```python
rearq=RearqConfig(
    sentinels=[
        "sentinel1.example.com:26379",
        "sentinel2.example.com:26379",
        "sentinel3.example.com:26379",
    ],
    sentinel_master="mymaster",
    db_url="postgresql://user:pass@localhost/tasks",
)
```

---

## Task Decorators

### @task - Background Tasks

```python
from django_cfg.apps.tasks import task

@task(queue="default", job_retry=3, job_timeout=300)
async def process_data(data_id: str, options: dict = None):
    """Process data in background."""
    # Your implementation
    return {"processed": True}

# Execute task
job = await process_data.delay(data_id="123", options={"format": "json"})

# Wait for result (optional)
result = await job.result(timeout=60)
if result and result.success:
    print(result.result)
```

**Parameters**:
- `queue` - Queue name (default: "default")
- `job_retry` - Number of retries on failure
- `job_timeout` - Timeout in seconds
- `run_with_lock` - Use distributed lock (prevents concurrent execution)
- `lock_timeout` - Lock timeout in seconds

### @cron_task - Scheduled Tasks

```python
from django_cfg.apps.tasks import cron_task

@cron_task(cron="0 0 * * *")  # Daily at midnight
async def daily_report():
    """Generate daily report."""
    # Your implementation
    return {"report_generated": True}

@cron_task(cron="*/5 * * * *")  # Every 5 minutes
async def health_check():
    """Check system health."""
    return {"status": "ok"}
```

**Cron Format**:
```
┌───────────── minute (0-59)
│ ┌───────────── hour (0-23)
│ │ ┌───────────── day of month (1-31)
│ │ │ ┌───────────── month (1-12)
│ │ │ │ ┌───────────── day of week (0-6) (Sunday=0)
│ │ │ │ │
* * * * *
```

**Examples**:
- `"* * * * *"` - Every minute
- `"0 * * * *"` - Every hour
- `"0 0 * * *"` - Daily at midnight
- `"0 9 * * 1"` - Every Monday at 9 AM
- `"0 0 1 * *"` - First day of month at midnight

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                     Django Application                       │
│                                                               │
│  ┌────────────────────────────────────────────────────────┐ │
│  │          django_cfg.apps.tasks                         │ │
│  │                                                         │ │
│  │  ├─ ReArqClient (wrapper around rearq.ReArq)          │ │
│  │  ├─ Task decorators (@task, @cron_task)               │ │
│  │  ├─ TaskLog model (execution tracking)                │ │
│  │  ├─ REST API (job management)                         │ │
│  │  └─ Django Admin (monitoring)                         │ │
│  └────────────────────────────────────────────────────────┘ │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            ▼
         ┌──────────────────────────────────────┐
         │     Redis (Message Broker)           │
         │                                       │
         │  • Task queues (default, high, low)  │
         │  • Scheduled tasks (cron)            │
         │  • Job state & results               │
         │  • Worker heartbeats                 │
         │  • Distributed locks                 │
         └──────────────────────────────────────┘
                            ▲
         ┌──────────────────┼──────────────────┐
         │                  │                  │
         ▼                  ▼                  ▼
┌────────────────┐ ┌────────────────┐ ┌────────────────┐
│  ReArq Worker  │ │  ReArq Worker  │ │  ReArq Worker  │
│   (Process)    │ │   (Process)    │ │   (Process)    │
│                │ │                │ │                │
│  Queue: all    │ │  Queue: high   │ │  Queue: low    │
└────────────────┘ └────────────────┘ └────────────────┘
         │                  │                  │
         └──────────────────┼──────────────────┘
                            │
                            ▼
         ┌──────────────────────────────────────┐
         │   Database (Tortoise ORM)            │
         │                                       │
         │  • rearq_job (job metadata)          │
         │  • rearq_job_results (results)       │
         │  • django_cfg_task_log (analytics)   │
         └──────────────────────────────────────┘
```

**Key Components**:

1. **ReArqClient**: Django wrapper providing configuration and singleton access
2. **Task Decorators**: `@task` and `@cron_task` for easy task definition
3. **Redis**: Message broker for job queues and real-time coordination
4. **Workers**: Async processes that execute tasks from queues
5. **Tortoise ORM**: Separate database for job persistence
6. **TaskLog Model**: Django model for analytics and historical tracking

---

## Monitoring

### REST API Endpoints

Query task execution status via REST API:

```python
# List all jobs
GET /cfg/tasks/logs/
  ?task_name=send_email
  &status=success
  &start_time=2025-10-30T00:00:00Z

# Get job details
GET /cfg/tasks/logs/{id}/

# Get statistics
GET /cfg/tasks/logs/stats/
  ?period_hours=24
  ?task_name=send_email

# Get execution timeline
GET /cfg/tasks/logs/timeline/
  ?period_hours=24
  &interval=hourly

# System overview
GET /cfg/tasks/logs/overview/
```

### Django Admin

Access task monitoring via Django admin:

1. Navigate to `/admin/tasks/tasklog/`
2. Filter by task name, status, queue, date range
3. View execution details, arguments, results
4. Search by job ID or error message
5. Export data for analysis

### TaskLog Model

Track all task executions with rich metadata:

```python
from django_cfg.apps.tasks.models import TaskLog

# Query recent failures
failures = TaskLog.objects.filter(
    status='failed',
    enqueue_time__gte=datetime.now() - timedelta(hours=24)
)

# Get task statistics
from django.db.models import Count, Avg
stats = TaskLog.objects.aggregate(
    total=Count('id'),
    avg_duration=Avg('duration_ms'),
    success_rate=Count('id', filter=Q(success=True)) * 100.0 / Count('id')
)

# Find slow tasks
slow_tasks = TaskLog.objects.filter(
    duration_ms__gt=5000  # > 5 seconds
).order_by('-duration_ms')
```

---

## Migration from Dramatiq

ReArq replaces Dramatiq in django-cfg with these advantages:

| Feature | Dramatiq | ReArq |
|---------|----------|-------|
| **Async Support** | Sync with thread pool | Native async/await |
| **Database** | Django ORM only | Tortoise ORM + Django ORM |
| **Monitoring** | Basic | Built-in UI + REST API |
| **Cron Tasks** | Via APScheduler | Native support |
| **Job Results** | No persistence | Stored in database |
| **Distributed Locks** | Manual Redis locks | Built-in support |
| **Performance** | Good | Excellent (async) |

**Migration Path**:

1. Update configuration (replace `DramatiqConfig` with `RearqConfig`)
2. Convert task decorators (`@dramatiq.actor` → `@task`)
3. Update task calls (`.send()` → `await .delay()`)
4. Run migrations for TaskLog model
5. Create `main.py` entry point for ReArq workers
6. Start ReArq workers using native CLI: `rearq main:rearq worker`

See the [Configuration Guide](./configuration) and [Deployment Guide](./deployment) for detailed instructions.

---

## See Also

### Core Documentation
- **[Getting Started](/getting-started/intro)** - Set up django-cfg with ReArq
- **[Configuration Guide](/fundamentals/configuration)** - Configure your project
- **[Production Deployment](/guides/production-config)** - Deploy with ReArq workers

### Related Features
- **[AI Knowledge Base](/features/built-in-apps/ai-knowledge/overview)** - Uses ReArq for document processing
- **[Built-in Apps Overview](/features/built-in-apps/overview)** - Apps that integrate with tasks
- **[Docker Deployment](/guides/docker/production)** - Run ReArq workers in containers

### Integration Guides
- **[Centrifugo Integration](/features/integrations/centrifugo/)** - Real-time updates for tasks
- **[Integrations Overview](/features/integrations/overview)** - All available integrations

---

**Status**: Production Ready
**Version**: 1.0.0
**Last Updated**: 2025-10-30
