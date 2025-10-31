---
title: Django-Q2 Task Scheduling
description: Type-safe task scheduling with Django-Q2 integration for distributed async tasks and scheduled job execution
sidebar_label: Overview & Philosophy
sidebar_position: 1
tags:
  - scheduling
  - django-q2
  - async-tasks
  - automation
  - background-jobs
keywords:
  - django-cfg scheduling
  - django-q2
  - scheduled tasks
  - async tasks
  - distributed tasks
---

# Django-Q2 Task Scheduling

> **📚 Part of**: [Modules](/features/modules/overview) - Explore all django-cfg modules

Type-safe task scheduling with Django-Q2 integration for async task execution, scheduled jobs, and distributed task processing in django-cfg projects.

---

## Quick Navigation

### For Developers
- [Quick Start](#quick-start) - Get started in 5 minutes
- [Configuration](#configuration) - Declarative task setup
- [Schedule Types](#schedule-types) - Cron, intervals, and one-time tasks
- [Examples](#examples) - Practical code examples

### For DevOps
- [Installation](#installation) - Django-Q2 setup
- [Management](#management) - Cluster and task management
- [Production](#production-best-practices) - Production deployment
- [Monitoring](#monitoring) - Task monitoring and debugging
- [Troubleshooting](#troubleshooting) - Common issues

---

## Philosophy

### "Type-Safe Configuration"
Define scheduled tasks with Pydantic models, not dictionaries:

```python
from django_cfg import DjangoQ2Config, DjangoQ2ScheduleConfig

django_q2 = DjangoQ2Config(
    enabled=True,
    workers=4,
    schedules=[
        DjangoQ2ScheduleConfig(
            name="Sync balances",
            schedule_type="minutes",
            minutes=5,
            command="sync_account_balances",
        ),
    ],
)
```

### "Declarative Over Imperative"
Tasks defined in `config.py` automatically sync to database:

- ✅ **No Manual Setup** - Schedules created from configuration
- ✅ **Version Controlled** - Tasks tracked in source control
- ✅ **Environment Aware** - Different schedules per environment
- ✅ **Type Validated** - Catch errors before deployment

### "Production-Ready Features"
Built for enterprise applications:

- ✅ **Distributed** - Multi-worker task processing
- ✅ **Async** - Both scheduled and ad-hoc async tasks
- ✅ **Reliable** - Redis/database backed with retries
- ✅ **Monitored** - Built-in admin interface and dashboard
- ✅ **Scalable** - Horizontal scaling with multiple clusters

### "Auto-Magic Configuration" 🎉
Zero-boilerplate Redis setup:

```python
class MyConfig(DjangoConfig):
    # Step 1: Set redis_url once
    redis_url: Optional[str] = env.redis_url  # e.g., "redis://redis:6379/0"

    # Step 2: Django-Q2 automatically uses it!
    django_q2 = DjangoQ2Config(
        enabled=True,
        # broker_url is auto-detected from config.redis_url! ✨
        workers=4,
        schedules=[...],
    )
```

**Benefits:**
- ✅ **DRY Principle** - Set `redis_url` once, use everywhere
- ✅ **Auto-Cache** - Redis cache automatically created too
- ✅ **No Duplication** - Broker URL automatically configured
- ✅ **Type-Safe** - Pydantic validation for all settings

---

## Key Features

### Django Integration
- **Management Commands** - Schedule any Django command
- **Python Callables** - Schedule any Python function
- **ORM Access** - Full Django ORM available in tasks
- **Admin Interface** - Built-in Django admin for monitoring

### Schedule Types
- **Cron Expressions** - Traditional cron syntax
- **Intervals** - Minutes, hourly, daily, weekly, monthly, yearly
- **One-Time** - Run once at scheduled time
- **Flexible** - Mix and match schedule types

### Reliability
- **Retries** - Automatic task retry on failure
- **Result Storage** - Task results saved to database
- **Hooks** - Post-execution callbacks
- **Timeouts** - Configurable task timeouts

### Async Tasks
- **On-Demand** - Queue tasks from anywhere in your code
- **Task Groups** - Group related tasks
- **Task Chains** - Execute tasks sequentially
- **Scheduled** - Run tasks at specific times

### Monitoring
- **Django Admin** - View tasks, schedules, and results
- **Dashboard API** - REST API for monitoring
- **Logging** - Comprehensive execution logging
- **Metrics** - Track success/failure rates

---

## Migration from django-crontab

Django-Q2 is the modern replacement for django-crontab with significant improvements:

### Why Migrate?

| Feature | django-crontab | Django-Q2 |
|---------|---------------|-----------|
| **Maintenance** | ❌ Unmaintained | ✅ Active (Django 5.x support) |
| **Async Tasks** | ❌ No | ✅ Yes |
| **Admin Interface** | ❌ No | ✅ Built-in |
| **Distributed** | ❌ No | ✅ Yes |
| **Result Storage** | ❌ No | ✅ Yes |
| **Retries** | ❌ Manual | ✅ Automatic |
| **Monitoring** | ❌ Logs only | ✅ Admin + Dashboard API |

### Migration Guide

**Before (django-crontab):**
```python
from django_cfg import CrontabConfig, CrontabJobConfig

crontab = CrontabConfig(
    jobs=[
        CrontabJobConfig(
            name="sync_data",
            command="sync_data",
            minute="*/5",
            hour="*",
        ),
    ],
)
```

**After (Django-Q2):**
```python
from django_cfg import DjangoQ2Config, DjangoQ2ScheduleConfig

django_q2 = DjangoQ2Config(
    enabled=True,
    schedules=[
        DjangoQ2ScheduleConfig(
            name="Sync data",
            schedule_type="minutes",
            minutes=5,
            command="sync_data",
        ),
    ],
)
```

**Schedule Mapping:**
- `*/5 * * * *` → `schedule_type="minutes", minutes=5`
- `0 * * * *` → `schedule_type="hourly"`
- `0 2 * * *` → `schedule_type="cron", cron="0 2 * * *"`
- `0 9 * * 1-5` → `schedule_type="cron", cron="0 9 * * 1-5"`

---

## Implementation Status

| Component | Status | Notes |
|-----------|--------|-------|
| DjangoQ2Config Model | ✅ Complete | Type-safe Pydantic configuration |
| DjangoQ2ScheduleConfig Model | ✅ Complete | Individual schedule configuration |
| Settings Generator | ✅ Complete | Auto-generate Q_CLUSTER settings |
| Apps Integration | ✅ Complete | Auto-add django_q to INSTALLED_APPS |
| Schedule Validation | ✅ Complete | Type validation and schedule syntax |
| Dashboard API | ✅ Complete | REST API for monitoring |
| Management Commands | ✅ Complete | Via django-q2 CLI |
| Documentation | ✅ Complete | Full docs with examples |

---

## Quick Start

### 1. Configuration

Add Django-Q2 configuration to your django-cfg settings:

```python title="config.py"
from django_cfg import DjangoConfig, DjangoQ2Config, DjangoQ2ScheduleConfig

class Config(DjangoConfig):
    project_name = "My Project"

    # Enable Django-Q2 scheduling
    django_q2 = DjangoQ2Config(
        enabled=True,
        workers=4,  # Number of worker processes
        schedules=[
            # Sync data every 5 minutes
            DjangoQ2ScheduleConfig(
                name="Sync data (frequent)",
                schedule_type="minutes",
                minutes=5,
                command="sync_data",
                command_args=["--ignore-errors"],
                command_kwargs={"verbosity": 0},
            ),
            # Daily cleanup at 2 AM
            DjangoQ2ScheduleConfig(
                name="Daily cleanup",
                schedule_type="cron",
                cron="0 2 * * *",
                command="cleanup_old_data",
            ),
        ],
    )

config = Config()
```

### 2. Run Migrations

Django-Q2 requires database tables:

```bash
# Apply migrations
python manage.py migrate

# You should see:
# Running migrations:
#   Applying django_q.0001_initial... OK
```

### 3. Start Cluster

Start the Django-Q2 worker cluster:

```bash
# Start cluster (development)
python manage.py qcluster

# Expected output:
# INFO: Q Cluster django_cfg_cluster starting.
# INFO: Process-1 ready for work at 12345
# INFO: Process-2 ready for work at 12346
# ...
```

### 4. Verify

Check schedules in Django admin:

```
http://localhost:8000/admin/django_q/schedule/
```

Or via shell:

```python
python manage.py shell
>>> from django_q.models import Schedule
>>> Schedule.objects.all()
<QuerySet [<Schedule: Sync data (frequent)>, <Schedule: Daily cleanup>]>
```

---

## Configuration

### Minimal Configuration

```python
from django_cfg import DjangoQ2Config, DjangoQ2ScheduleConfig

django_q2 = DjangoQ2Config(
    enabled=True,
    schedules=[
        DjangoQ2ScheduleConfig(
            name="My task",
            schedule_type="hourly",
            command="my_command",
        ),
    ],
)
```

### Complete Configuration

```python
django_q2 = DjangoQ2Config(
    # Enable/disable Django-Q2
    enabled=True,

    # Worker configuration
    workers=4,                    # Number of worker processes
    timeout=300,                  # Task timeout in seconds
    retry=3600,                   # Retry failed tasks after N seconds

    # Broker configuration - AUTO-MAGIC! 🎉
    # broker_url automatically uses config.redis_url (no need to specify!)
    # Just set: redis_url: Optional[str] = env.redis_url in your DjangoConfig
    broker_class="redis",         # redis or orm

    # Queue configuration
    queue_limit=50,               # Max tasks in queue

    # Result storage
    save_limit=250,               # Max successful tasks to save
    cached=500,                   # Max tasks to cache

    # Monitoring
    monitor_interval=30,          # Seconds between monitor checks
    log_level="INFO",             # DEBUG, INFO, WARNING, ERROR

    # Advanced
    compress=False,               # Compress task data
    catch_up=True,                # Run missed scheduled tasks
    sync=False,                   # Sync mode (for testing)

    # Schedules
    schedules=[
        DjangoQ2ScheduleConfig(
            # Task identification
            name="Unique task name",
            enabled=True,

            # Schedule type
            schedule_type="minutes",  # cron, minutes, hourly, daily, weekly, monthly, yearly, once

            # For schedule_type="minutes"
            minutes=5,

            # For schedule_type="cron"
            cron="0 2 * * *",

            # Task configuration
            command="my_command",                # Django management command
            command_args=["--flag", "value"],    # Command arguments
            command_kwargs={"verbosity": 1},     # Command kwargs

            # Or use function directly
            func="myapp.tasks.my_function",      # Python callable
            args=[1, 2, 3],                       # Function args
            kwargs={"key": "value"},              # Function kwargs

            # Task options
            timeout=60,                           # Override default timeout
            repeats=-1,                           # -1 = infinite, N = repeat N times
            hook="myapp.tasks.on_complete",       # Post-execution hook
            cluster="my_cluster",                 # Specific cluster name
        ),
    ],
)
```

---

## Schedule Types

### Minutes Interval

Run every N minutes:

```python
DjangoQ2ScheduleConfig(
    name="Every 5 minutes",
    schedule_type="minutes",
    minutes=5,
    command="my_task",
)
```

### Hourly

Run every hour (at minute 0):

```python
DjangoQ2ScheduleConfig(
    name="Every hour",
    schedule_type="hourly",
    command="my_task",
)
```

### Daily

Run every day at midnight:

```python
DjangoQ2ScheduleConfig(
    name="Daily",
    schedule_type="daily",
    command="my_task",
)
```

### Weekly

Run every week (Sunday at midnight):

```python
DjangoQ2ScheduleConfig(
    name="Weekly",
    schedule_type="weekly",
    command="my_task",
)
```

### Monthly

Run first day of every month:

```python
DjangoQ2ScheduleConfig(
    name="Monthly",
    schedule_type="monthly",
    command="my_task",
)
```

### Yearly

Run January 1st every year:

```python
DjangoQ2ScheduleConfig(
    name="Yearly",
    schedule_type="yearly",
    command="my_task",
)
```

### Cron Expression

Full cron syntax support:

```python
DjangoQ2ScheduleConfig(
    name="Complex schedule",
    schedule_type="cron",
    cron="0 9 * * 1-5",  # 9 AM on weekdays
    command="my_task",
)
```

### Once

Run once at scheduled time:

```python
DjangoQ2ScheduleConfig(
    name="One-time task",
    schedule_type="once",
    func="myapp.tasks.setup",
)
```

---

## Examples

### Real-World Use Cases

#### Data Synchronization

```python
schedules=[
    # Frequent quiet sync every 5 minutes
    DjangoQ2ScheduleConfig(
        name="Sync balances (frequent)",
        schedule_type="minutes",
        minutes=5,
        command="sync_account_balances",
        command_args=["--ignore-errors"],
        command_kwargs={"verbosity": 0},
    ),

    # Verbose hourly sync for monitoring
    DjangoQ2ScheduleConfig(
        name="Sync balances (verbose)",
        schedule_type="hourly",
        command="sync_account_balances",
        command_args=["--verbose"],
        command_kwargs={"verbosity": 1},
    ),
]
```

#### Daily Reports

```python
DjangoQ2ScheduleConfig(
    name="Daily report",
    schedule_type="cron",
    cron="0 9 * * 1-5",  # 9 AM on weekdays
    command="generate_report",
    command_args=["--type=daily", "--email-admins"],
)
```

#### Database Maintenance

```python
schedules=[
    # Clean old sessions daily at 2 AM
    DjangoQ2ScheduleConfig(
        name="Cleanup sessions",
        schedule_type="cron",
        cron="0 2 * * *",
        command="clearsessions",
    ),

    # Database vacuum weekly (Sunday 3 AM)
    DjangoQ2ScheduleConfig(
        name="Vacuum database",
        schedule_type="cron",
        cron="0 3 * * 0",
        func="myapp.maintenance.vacuum_database",
    ),
]
```

#### Cache Warming

```python
DjangoQ2ScheduleConfig(
    name="Warm cache",
    schedule_type="minutes",
    minutes=15,
    command="warm_cache",
    command_args=["--endpoints=/api/popular/,/api/trending/"],
)
```

#### Function-Based Tasks

```python
DjangoQ2ScheduleConfig(
    name="Cleanup old files",
    schedule_type="daily",
    func="myapp.tasks.cleanup_old_files",
    kwargs={"days": 7},
    hook="myapp.tasks.notify_admin",  # Called after completion
)
```

---

## Installation

### Prerequisites

```bash
# Install Redis (recommended broker)
# Ubuntu/Debian
sudo apt-get install redis-server
sudo systemctl start redis

# macOS
brew install redis
brew services start redis

# Verify Redis
redis-cli ping  # Should return "PONG"
```

### Setup

Django-Q2 is automatically configured when you enable it in django-cfg:

```python
django_q2 = DjangoQ2Config(enabled=True)
```

This automatically:
1. Adds `django_q` to INSTALLED_APPS
2. Generates Q_CLUSTER settings
3. Configures broker and workers

### Database Migration

```bash
python manage.py migrate
```

---

## Management

### Start Cluster

```bash
# Development (foreground)
python manage.py qcluster

# Production (with supervisor/systemd)
# See Production Best Practices below
```

### Monitor Cluster

```bash
# Monitor in separate terminal
python manage.py qmonitor

# Expected output:
# ┌─────────────────────────────────────┐
# │   CLUSTER MONITOR                   │
# ├─────────────────────────────────────┤
# │ Workers: 4                          │
# │ Status: Running                     │
# │ Queued: 0                           │
# │ Success: 142                        │
# │ Failures: 3                         │
# └─────────────────────────────────────┘
```

### Check Statistics

```bash
# View cluster statistics
python manage.py qinfo

# Output:
# Cluster: django_cfg_cluster
# Workers: 4
# ...
```

### Django Admin

View tasks and schedules in Django admin:

```
http://localhost:8000/admin/django_q/
```

Available views:
- `/admin/django_q/schedule/` - Scheduled tasks
- `/admin/django_q/success/` - Successful tasks
- `/admin/django_q/failure/` - Failed tasks
- `/admin/django_q/ormq/` - Queued tasks (ORM broker)

### Dashboard API

Query tasks via REST API:

```python
# GET /cfg/dashboard/api/django_q2/
{
  "status": {
    "cluster_running": true,
    "total_schedules": 3,
    "recent_tasks": 10,
    "successful_tasks": 142,
    "failed_tasks": 3
  },
  "schedules": [...],
  "recent_tasks": [...]
}
```

---

## Production Best Practices

### 1. Use Redis Broker (Auto-Configured!)

```python
# Step 1: Set redis_url once in your DjangoConfig
class MyConfig(DjangoConfig):
    redis_url: Optional[str] = env.redis_url  # e.g., "redis://redis:6379/0"

    # Step 2: Django-Q2 automatically uses it! 🎉
    django_q2 = DjangoQ2Config(
        enabled=True,
        broker_class="redis",  # Recommended for production
        # broker_url is auto-detected from config.redis_url!
    )
```

### 2. Configure Workers

```python
django_q2 = DjangoQ2Config(
    workers=4,      # Start with CPU count
    timeout=300,    # 5 minutes default
    retry=3600,     # Retry after 1 hour
)
```

### 3. Supervisor Configuration

```ini title="/etc/supervisor/conf.d/django-q2.conf"
[program:django-q2]
command=/path/to/venv/bin/python /path/to/manage.py qcluster
directory=/path/to/project
user=www-data
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/django-q2.log
```

```bash
# Start with supervisor
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start django-q2
```

### 4. Systemd Service

```ini title="/etc/systemd/system/django-q2.service"
[Unit]
Description=Django-Q2 Cluster
After=network.target redis.service postgresql.service

[Service]
Type=simple
User=www-data
WorkingDirectory=/path/to/project
Environment="DJANGO_SETTINGS_MODULE=myproject.settings"
ExecStart=/path/to/venv/bin/python /path/to/manage.py qcluster
Restart=on-failure
RestartSec=5s

[Install]
WantedBy=multi-user.target
```

```bash
# Enable and start
sudo systemctl enable django-q2
sudo systemctl start django-q2
sudo systemctl status django-q2
```

### 5. Multiple Clusters

```python
# Separate clusters for different task types
DjangoQ2Config(
    workers=2,
    schedules=[
        DjangoQ2ScheduleConfig(
            name="Heavy task",
            cluster="heavy",
            command="heavy_computation",
        ),
        DjangoQ2ScheduleConfig(
            name="Light task",
            cluster="light",
            command="quick_update",
        ),
    ],
)
```

### 6. Error Handling

```python
# Task with retry and hooks
DjangoQ2ScheduleConfig(
    name="Important task",
    command="critical_sync",
    timeout=60,
    repeats=-1,  # Infinite retries
    hook="myapp.tasks.on_complete",
)
```

```python
# myapp/tasks.py
def on_complete(task):
    """Hook called after task completion."""
    if task.success:
        print(f"Task {task.name} succeeded")
    else:
        # Send alert
        send_alert(f"Task {task.name} failed: {task.result}")
```

### 7. Monitoring

```python
# Enable comprehensive logging
django_q2 = DjangoQ2Config(
    log_level="INFO",
    save_limit=1000,  # Keep more history
)
```

### 8. Result Storage

```python
django_q2 = DjangoQ2Config(
    save_limit=250,   # Successful tasks
    cached=500,       # Cached results
)
```

---

## Monitoring

### Django Admin

Monitor tasks in real-time:

1. Navigate to `/admin/django_q/`
2. View scheduled tasks: `/admin/django_q/schedule/`
3. Check successful tasks: `/admin/django_q/success/`
4. Review failures: `/admin/django_q/failure/`

### Dashboard API Endpoints

```bash
# Get cluster status and schedules
curl http://localhost:8000/cfg/dashboard/api/django_q2/

# Get all schedules
curl http://localhost:8000/cfg/dashboard/api/django_q2/schedules/

# Get recent tasks
curl http://localhost:8000/cfg/dashboard/api/django_q2/tasks/?limit=50

# Get cluster status only
curl http://localhost:8000/cfg/dashboard/api/django_q2/status/
```

### Command Line

```bash
# Check cluster info
python manage.py qinfo

# Monitor cluster
python manage.py qmonitor

# Memory usage
python manage.py qmemory
```

### Logging

```python
# Configure Django logging for django-q
LOGGING = {
    'handlers': {
        'django_q': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': 'logs/django-q.log',
            'maxBytes': 10485760,  # 10MB
            'backupCount': 5,
        },
    },
    'loggers': {
        'django_q': {
            'handlers': ['django_q'],
            'level': 'INFO',
        },
    },
}
```

---

## Troubleshooting

### Cluster Not Starting

**Check dependencies:**

```bash
# Verify Redis is running
redis-cli ping

# Check database connection
python manage.py dbshell
```

**Check configuration:**

```python
python manage.py shell
>>> from django.conf import settings
>>> settings.Q_CLUSTER
>>> 'django_q' in settings.INSTALLED_APPS
True
```

### Tasks Not Running

**Verify schedules in database:**

```python
python manage.py shell
>>> from django_q.models import Schedule
>>> Schedule.objects.filter(repeats__gt=0)
```

**Check cluster is running:**

```bash
# Should see workers running
python manage.py qmonitor

# Check logs
tail -f logs/django-q.log
```

### High Memory Usage

```bash
# Monitor memory
python manage.py qmemory

# Reduce workers or cached results
```

```python
django_q2 = DjangoQ2Config(
    workers=2,      # Reduce workers
    cached=100,     # Reduce cache
)
```

### Failed Tasks

```bash
# View failures in admin
/admin/django_q/failure/

# Or via shell
python manage.py shell
>>> from django_q.models import Failure
>>> for f in Failure.objects.all()[:10]:
...     print(f.name, f.result)
```

### Redis Connection Errors

```python
# Test Redis connection
import redis
r = redis.Redis(host='localhost', port=6379, db=0)
r.ping()  # Should return True
```

---

## Architecture

### Components

```
┌─────────────────────────────────────────────────────────────┐
│                     Django Application                       │
│                                                               │
│  ┌────────────────────────────────────────────────────────┐ │
│  │          django_cfg.models.django_q2                   │ │
│  │                                                         │ │
│  │  ├─ DjangoQ2Config (cluster configuration)            │ │
│  │  ├─ DjangoQ2ScheduleConfig (scheduled tasks)          │ │
│  │  ├─ Schedule validation                               │ │
│  │  └─ Django settings generation                        │ │
│  └────────────────────────────────────────────────────────┘ │
│                            │                                 │
│  ┌────────────────────────────────────────────────────────┐ │
│  │     django_cfg.core.generation.django_q2               │ │
│  │                                                         │ │
│  │  ├─ DjangoQ2SettingsGenerator                         │ │
│  │  └─ Q_CLUSTER settings generation                     │ │
│  └────────────────────────────────────────────────────────┘ │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            ▼
         ┌──────────────────────────────────────┐
         │     Django Settings (settings.py)    │
         │                                       │
         │  • Q_CLUSTER = {...}                 │
         │  • INSTALLED_APPS += ['django_q']    │
         └──────────────────────────────────────┘
                            │
                            ▼
         ┌──────────────────────────────────────┐
         │         django-q2 package             │
         │                                       │
         │  • Worker cluster                    │
         │  • Task scheduler                    │
         │  • Result storage                    │
         │  manage.py qcluster/qmonitor/qinfo   │
         └──────────────────────────────────────┘
                            │
                     ┌──────┴──────┐
                     │             │
                     ▼             ▼
         ┌──────────────┐  ┌──────────────┐
         │    Redis      │  │  PostgreSQL  │
         │   (Broker)    │  │  (Storage)   │
         │               │  │              │
         │  Task Queue   │  │  Schedules   │
         │               │  │  Results     │
         └──────────────┘  └──────────────┘
```

### Execution Flow

1. **Configuration**: Define schedules in `config.py` using `DjangoQ2Config`
2. **Generation**: django-cfg generates `Q_CLUSTER` in Django settings
3. **Registration**: django_q added to `INSTALLED_APPS` automatically
4. **Migration**: Run migrations to create database tables
5. **Cluster**: Start worker cluster with `manage.py qcluster`
6. **Scheduling**: Scheduler creates tasks based on schedules
7. **Execution**: Workers process tasks from broker
8. **Storage**: Results saved to database
9. **Monitoring**: View in admin or via Dashboard API

---

## See Also

### Core Documentation
- **[Getting Started](/getting-started/intro)** - Set up django-cfg with Django-Q2
- **[Configuration Guide](/fundamentals/configuration)** - Configure your project
- **[Type Safety](/fundamentals/core/type-safety)** - Pydantic configuration

### Related Features
- **[Modules Overview](/features/modules/overview)** - All available modules
- **[Email Module](/features/modules/email/overview)** - Send emails from tasks
- **[Telegram Module](/features/modules/telegram/overview)** - Telegram notifications
- **[Dashboard](/features/modules/django-admin/overview)** - Monitor tasks in admin

### External Documentation
- **[Django-Q2](https://github.com/GDay/django-q2)** - Official Django-Q2 documentation
- **[Django-Q Docs](https://django-q2.readthedocs.io/)** - Complete user guide
- **[Crontab Guru](https://crontab.guru/)** - Interactive cron schedule editor

---

**Status**: Production Ready
**Version**: 1.0.0
**Last Updated**: 2025-10-31
