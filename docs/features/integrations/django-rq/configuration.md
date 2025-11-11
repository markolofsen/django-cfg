---
title: Django-RQ Configuration
description: Complete configuration guide for Django-RQ in django-cfg with examples and best practices
sidebar_position: 3
tags:
  - configuration
  - django-rq
  - setup
  - queues
  - scheduler
---

# Django-RQ Configuration

Complete guide to configuring Django-RQ in django-cfg projects, including queue setup, scheduling, and advanced Redis configurations.

---

## Quick Start

### Minimal Configuration

The simplest Django-RQ configuration uses `redis_url` from parent `DjangoConfig`:

```python
# api/config.py
from django_cfg import DjangoConfig
from django_cfg.models import DjangoRQConfig, RQQueueConfig

class MyConfig(DjangoConfig):
    # Redis URL (used by Django-RQ automatically)
    redis_url: str = "redis://localhost:6379/0"

    # Django-RQ configuration
    django_rq: DjangoRQConfig = DjangoRQConfig(
        enabled=True,
        queues=[
            RQQueueConfig(queue="default"),
        ],
    )
```

That's it! Django-RQ will automatically:
- Use `redis_url` for all queues
- Configure default timeouts and TTL
- Register the `default` queue
- Enable admin interface
- **✨ NEW:** Add automatic cleanup tasks (daily + weekly)
- **✨ NEW:** Add demo heartbeat task (development only)

---

## Complete Configuration

### Full Example

Here's a production-ready configuration with multiple queues and scheduling:

```python
# api/config.py
from django_cfg import DjangoConfig
from django_cfg.models import DjangoRQConfig, RQQueueConfig, RQScheduleConfig

class MyConfig(DjangoConfig):
    # === Redis Configuration ===
    redis_url: str = "redis://localhost:6379/0"

    # === Django-RQ Configuration ===
    django_rq: DjangoRQConfig = DjangoRQConfig(
        enabled=True,

        # Queue configurations
        queues=[
            # High priority queue for urgent tasks
            RQQueueConfig(
                queue="high",
                default_timeout=180,      # 3 minutes
                default_result_ttl=300,   # 5 minutes
            ),

            # Default queue for normal tasks
            RQQueueConfig(
                queue="default",
                default_timeout=360,      # 6 minutes
                default_result_ttl=500,   # 8 minutes
            ),

            # Low priority queue for batch operations
            RQQueueConfig(
                queue="low",
                default_timeout=600,      # 10 minutes
                default_result_ttl=800,   # 13 minutes
            ),

            # Knowledge base queue (if enable_knowbase=True)
            RQQueueConfig(
                queue="knowledge",
                default_timeout=600,      # 10 minutes
                default_result_ttl=3600,  # 1 hour
            ),
        ],

        # Scheduled tasks
        schedules=[
            # Update prices every 5 minutes
            RQScheduleConfig(
                func="apps.crypto.tasks.update_coin_prices",
                interval=300,  # seconds
                queue="default",
                limit=50,
                verbosity=0,
                description="Update coin prices (frequent)",
            ),

            # Daily report at midnight
            RQScheduleConfig(
                func="apps.crypto.tasks.generate_report",
                cron="0 0 * * *",  # Cron expression
                queue="low",
                report_type="daily",
                description="Generate daily report",
            ),
        ],

        # Admin and monitoring
        show_admin_link=True,
        prometheus_enabled=True,
    )
```

---

## Configuration Models

### DjangoRQConfig

Main configuration model for Django-RQ:

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `enabled` | `bool` | `True` | Enable Django-RQ integration |
| `queues` | `List[RQQueueConfig]` | `[RQQueueConfig(queue="default")]` | Queue configurations |
| `schedules` | `List[RQScheduleConfig]` | `[]` | Scheduled job configurations |
| `show_admin_link` | `bool` | `True` | Show Django-RQ link in admin |
| `prometheus_enabled` | `bool` | `True` | Enable Prometheus metrics |
| `enable_auto_cleanup` | `bool` | `True` | Enable automatic cleanup of old jobs |
| `cleanup_max_age_days` | `int` | `7` | Maximum age in days before cleanup |
| `exception_handlers` | `List[str]` | `[]` | Exception handler function paths |
| `api_token` | `Optional[str]` | `None` | API token for authentication |

**Methods:**
```python
config.to_django_settings(parent_config)  # Generate Django settings
config.get_queue_names()                  # Get list of queue names
config.get_queue_config(name)             # Get specific queue config
config.add_queue(queue_config)            # Add queue programmatically
config.remove_queue(name)                 # Remove queue programmatically
config.get_all_schedules()                # Get all schedules (including auto-generated)
```

**Auto-Generated Schedules:**

When `enable_auto_cleanup=True` (default), Django-RQ automatically adds:

**Production & Development:**
- `cleanup_old_jobs` - Runs daily (86400s), removes jobs older than `cleanup_max_age_days`
- `cleanup_orphaned_job_keys` - Runs weekly (604800s), removes orphaned Redis keys

**Development Only:**
- `demo_scheduler_heartbeat` - Runs every minute (60s), verifies scheduler is working

### RQQueueConfig

Configuration for a single queue:

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `queue` | `str` | *required* | Queue name (alphanumeric, hyphens, underscores) |
| `url` | `Optional[str]` | `None` | Redis URL (overrides host/port/db) |
| `host` | `str` | `"localhost"` | Redis host |
| `port` | `int` | `6379` | Redis port |
| `db` | `int` | `0` | Redis database number (0-15) |
| `username` | `Optional[str]` | `None` | Redis username (Redis 6+) |
| `password` | `Optional[str]` | `None` | Redis password |
| `default_timeout` | `int` | `360` | Default job timeout in seconds |
| `default_result_ttl` | `int` | `800` | Default result TTL in seconds |
| `socket_timeout` | `Optional[float]` | `None` | Redis socket timeout |
| `connection_kwargs` | `Dict[str, Any]` | `{}` | Additional connection arguments |
| `redis_client_kwargs` | `Dict[str, Any]` | `{}` | Additional Redis client arguments |

**Advanced Options:**
```python
# Redis Sentinel support
RQQueueConfig(
    queue="default",
    sentinels=[("host1", 26379), ("host2", 26379)],
    master_name="mymaster",
    sentinel_kwargs={"password": "sentinel_pass"},
)

# SSL/TLS connection
RQQueueConfig(
    queue="default",
    url="rediss://localhost:6380/0",  # Note: rediss://
    connection_kwargs={
        "ssl_cert_reqs": "required",
        "ssl_ca_certs": "/path/to/ca.crt",
    },
)
```

### RQScheduleConfig

Configuration for scheduled jobs:

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `func` | `str` | *required* | Function path (e.g., `apps.myapp.tasks.my_task`) |
| `cron` | `Optional[str]` | `None` | Cron expression (e.g., `0 0 * * *`) |
| `interval` | `Optional[int]` | `None` | Interval in seconds |
| `scheduled_time` | `Optional[str]` | `None` | ISO datetime for one-time job |
| `queue` | `str` | `"default"` | Queue name |
| `timeout` | `Optional[int]` | `None` | Job timeout (overrides queue default) |
| `result_ttl` | `Optional[int]` | `None` | Result TTL (overrides queue default) |
| `args` | `List[Any]` | `[]` | Positional arguments |
| `kwargs` | `Dict[str, Any]` | `{}` | Keyword arguments |
| `job_id` | `Optional[str]` | `None` | Custom job ID |
| `description` | `Optional[str]` | `None` | Human-readable description |
| `repeat` | `Optional[int]` | `None` | Number of times to repeat |

**Declarative Task Parameters:**

RQScheduleConfig supports declarative parameters that are automatically added to `kwargs`:

| Parameter | Type | Description |
|-----------|------|-------------|
| `limit` | `Optional[int]` | Limit parameter for tasks |
| `verbosity` | `Optional[int]` | Verbosity level (0-3) |
| `report_type` | `Optional[str]` | Report type parameter |
| `days` | `Optional[int]` | Days parameter |
| `force` | `Optional[bool]` | Force parameter |

**Example:**
```python
# Declarative syntax (recommended)
RQScheduleConfig(
    func="apps.crypto.tasks.update_coin_prices",
    interval=300,
    limit=50,          # Automatically added to kwargs
    verbosity=1,       # Automatically added to kwargs
    force=True,        # Automatically added to kwargs
)

# Traditional syntax (still works)
RQScheduleConfig(
    func="apps.crypto.tasks.update_coin_prices",
    interval=300,
    kwargs={"limit": 50, "verbosity": 1, "force": True},
)
```

---

## Queue Configuration

### Basic Queue Setup

```python
django_rq: DjangoRQConfig = DjangoRQConfig(
    enabled=True,
    queues=[
        # Single queue with defaults
        RQQueueConfig(queue="default"),
    ],
)
```

### Multiple Queues

```python
django_rq: DjangoRQConfig = DjangoRQConfig(
    enabled=True,
    queues=[
        # High priority (short timeout, short TTL)
        RQQueueConfig(
            queue="high",
            default_timeout=180,
            default_result_ttl=300,
        ),

        # Normal priority
        RQQueueConfig(
            queue="default",
            default_timeout=360,
            default_result_ttl=500,
        ),

        # Low priority (long timeout, long TTL)
        RQQueueConfig(
            queue="low",
            default_timeout=600,
            default_result_ttl=800,
        ),
    ],
)
```

### Per-Queue Redis Configuration

```python
django_rq: DjangoRQConfig = DjangoRQConfig(
    enabled=True,
    queues=[
        # Queue 1: Use default redis_url
        RQQueueConfig(queue="default"),

        # Queue 2: Use specific Redis URL
        RQQueueConfig(
            queue="slow",
            url="redis://redis-slow:6379/0",
        ),

        # Queue 3: Use different Redis instance
        RQQueueConfig(
            queue="archive",
            host="redis-archive",
            port=6380,
            db=1,
        ),
    ],
)
```

### Queue Naming Best Practices

```python
# Good queue names
"default"        # ✅ Main queue
"high"           # ✅ High priority
"low"            # ✅ Low priority
"email"          # ✅ Specific purpose
"knowledge"      # ✅ AI/knowledge tasks
"reports"        # ✅ Report generation

# Bad queue names
"Queue-1"        # ❌ Non-descriptive
"myqueue"        # ❌ Too generic
"QUEUE"          # ❌ All caps
"queue with spaces"  # ❌ Contains spaces (invalid)
```

---

## Schedule Configuration

### Cron Schedules

Use cron expressions for time-based scheduling:

```python
schedules=[
    # Every 5 minutes
    RQScheduleConfig(
        func="apps.myapp.tasks.cleanup",
        cron="*/5 * * * *",
        queue="low",
    ),

    # Every day at midnight
    RQScheduleConfig(
        func="apps.myapp.tasks.daily_report",
        cron="0 0 * * *",
        queue="low",
        report_type="daily",
    ),

    # Every Monday at 9 AM
    RQScheduleConfig(
        func="apps.myapp.tasks.weekly_summary",
        cron="0 9 * * 1",
        queue="default",
    ),

    # First day of month at midnight
    RQScheduleConfig(
        func="apps.myapp.tasks.monthly_invoice",
        cron="0 0 1 * *",
        queue="default",
    ),
]
```

**Cron Expression Format:**
```
* * * * *
│ │ │ │ │
│ │ │ │ └─── Day of week (0-7, 0=Sunday)
│ │ │ └───── Month (1-12)
│ │ └─────── Day of month (1-31)
│ └───────── Hour (0-23)
└─────────── Minute (0-59)
```

### Interval Schedules

Use intervals for periodic tasks:

```python
schedules=[
    # Every 30 seconds
    RQScheduleConfig(
        func="apps.myapp.tasks.health_check",
        interval=30,
        queue="high",
    ),

    # Every 5 minutes (300 seconds)
    RQScheduleConfig(
        func="apps.crypto.tasks.update_prices",
        interval=300,
        queue="default",
        limit=100,
    ),

    # Every hour (3600 seconds)
    RQScheduleConfig(
        func="apps.crypto.tasks.sync_exchanges",
        interval=3600,
        queue="default",
    ),

    # Every 24 hours (86400 seconds)
    RQScheduleConfig(
        func="apps.myapp.tasks.backup",
        interval=86400,
        queue="low",
    ),
]
```

### One-Time Schedules

Schedule jobs for specific times:

```python
from datetime import datetime

schedules=[
    # New Year's Eve task
    RQScheduleConfig(
        func="apps.myapp.tasks.new_year_notification",
        scheduled_time="2025-12-31T23:59:00",
        queue="high",
    ),

    # Product launch notification
    RQScheduleConfig(
        func="apps.myapp.tasks.launch_notification",
        scheduled_time="2025-06-01T09:00:00",
        queue="high",
    ),
]
```

### Schedule with Task Parameters

```python
schedules=[
    # Update prices with parameters
    RQScheduleConfig(
        func="apps.crypto.tasks.update_coin_prices",
        interval=300,
        queue="default",
        # Declarative parameters (recommended)
        limit=50,
        verbosity=0,
        force=False,
        description="Update top 50 coins every 5 minutes",
    ),

    # Generate report with custom parameters
    RQScheduleConfig(
        func="apps.crypto.tasks.generate_report",
        cron="0 0 * * *",
        queue="low",
        # Declarative parameters
        report_type="daily",
        description="Daily market report at midnight",
    ),

    # Traditional syntax (still works)
    RQScheduleConfig(
        func="apps.myapp.tasks.custom_task",
        interval=3600,
        args=[],
        kwargs={
            "param1": "value1",
            "param2": 42,
        },
    ),
]
```

---

## Redis Configuration

### Standard Redis

```python
# Using redis_url from parent config (recommended)
class MyConfig(DjangoConfig):
    redis_url: str = "redis://localhost:6379/0"

    django_rq: DjangoRQConfig = DjangoRQConfig(
        enabled=True,
        queues=[RQQueueConfig(queue="default")],
    )

# Using explicit host/port/db
django_rq: DjangoRQConfig = DjangoRQConfig(
    enabled=True,
    queues=[
        RQQueueConfig(
            queue="default",
            host="localhost",
            port=6379,
            db=0,
        ),
    ],
)
```

### Redis with Authentication

```python
# Redis 6+ with username and password
django_rq: DjangoRQConfig = DjangoRQConfig(
    enabled=True,
    queues=[
        RQQueueConfig(
            queue="default",
            url="redis://username:password@localhost:6379/0",
        ),
    ],
)

# Redis < 6 with password only
django_rq: DjangoRQConfig = DjangoRQConfig(
    enabled=True,
    queues=[
        RQQueueConfig(
            queue="default",
            url="redis://:password@localhost:6379/0",
        ),
    ],
)
```

### Redis SSL/TLS

```python
django_rq: DjangoRQConfig = DjangoRQConfig(
    enabled=True,
    queues=[
        RQQueueConfig(
            queue="default",
            url="rediss://localhost:6380/0",  # Note: rediss://
            connection_kwargs={
                "ssl_cert_reqs": "required",
                "ssl_ca_certs": "/path/to/ca.crt",
                "ssl_certfile": "/path/to/client.crt",
                "ssl_keyfile": "/path/to/client.key",
            },
        ),
    ],
)
```

### Redis Sentinel

High availability with Redis Sentinel:

```python
django_rq: DjangoRQConfig = DjangoRQConfig(
    enabled=True,
    queues=[
        RQQueueConfig(
            queue="default",
            # Sentinel configuration
            sentinels=[
                ("sentinel1", 26379),
                ("sentinel2", 26379),
                ("sentinel3", 26379),
            ],
            master_name="mymaster",
            db=0,
            socket_timeout=0.5,
            # Sentinel authentication (if needed)
            sentinel_kwargs={
                "username": "sentinel_user",
                "password": "sentinel_pass",
            },
            # Redis authentication (if needed)
            username="redis_user",
            password="redis_pass",
        ),
    ],
)
```

### Redis Cluster

```python
# Redis Cluster is not directly supported by RQ
# Use a Redis Cluster proxy or stick to standard Redis
```

---

## Environment-Based Configuration

### Development vs Production

```python
from django_cfg import DjangoConfig
from django_cfg.models import DjangoRQConfig, RQQueueConfig

class MyConfig(DjangoConfig):
    @property
    def django_rq(self) -> DjangoRQConfig:
        """Environment-aware Django-RQ configuration."""
        if self.is_development:
            # Development: simple setup
            return DjangoRQConfig(
                enabled=True,
                queues=[
                    RQQueueConfig(queue="default"),
                ],
                prometheus_enabled=False,
            )
        else:
            # Production: full setup with multiple queues
            return DjangoRQConfig(
                enabled=True,
                queues=[
                    RQQueueConfig(queue="high", default_timeout=180),
                    RQQueueConfig(queue="default", default_timeout=360),
                    RQQueueConfig(queue="low", default_timeout=600),
                ],
                prometheus_enabled=True,
                schedules=[...],  # Add schedules
            )
```

### YAML-Based Configuration

```yaml
# config.dev.yaml
redis_url: "redis://localhost:6379/0"

django_rq:
  enabled: true
  queues:
    - queue: "default"
      default_timeout: 360
  prometheus_enabled: false

# config.prod.yaml
redis_url: "${REDIS_URL}"

django_rq:
  enabled: true
  queues:
    - queue: "high"
      default_timeout: 180
    - queue: "default"
      default_timeout: 360
    - queue: "low"
      default_timeout: 600
  prometheus_enabled: true
  schedules:
    - func: "apps.crypto.tasks.update_coin_prices"
      interval: 300
      queue: "default"
```

---

## Advanced Configuration

### Exception Handlers

Custom exception handlers for failed jobs:

```python
# myapp/handlers.py
def log_exception(job, exc_type, exc_value, traceback):
    """Log exception to custom logger."""
    import logging
    logger = logging.getLogger('rq.exceptions')
    logger.error(f"Job {job.id} failed: {exc_value}")

def send_exception_to_sentry(job, exc_type, exc_value, traceback):
    """Send exception to Sentry."""
    import sentry_sdk
    sentry_sdk.capture_exception(exc_value)

# config.py
django_rq: DjangoRQConfig = DjangoRQConfig(
    enabled=True,
    queues=[...],
    exception_handlers=[
        "myapp.handlers.log_exception",
        "myapp.handlers.send_exception_to_sentry",
    ],
)
```

### API Token Authentication

Secure API endpoints with token:

```python
django_rq: DjangoRQConfig = DjangoRQConfig(
    enabled=True,
    queues=[...],
    api_token="your-secret-token-here",
)

# Access API with token
# GET /api/cfg/rq/monitor/health/
# Header: Authorization: Token your-secret-token-here
```

### Custom Queue Defaults

```python
# Global timeout for all queues
DEFAULT_TIMEOUT = 360
DEFAULT_RESULT_TTL = 500

django_rq: DjangoRQConfig = DjangoRQConfig(
    enabled=True,
    queues=[
        RQQueueConfig(
            queue="default",
            default_timeout=DEFAULT_TIMEOUT,
            default_result_ttl=DEFAULT_RESULT_TTL,
        ),
        RQQueueConfig(
            queue="low",
            default_timeout=DEFAULT_TIMEOUT * 2,
            default_result_ttl=DEFAULT_RESULT_TTL * 2,
        ),
    ],
)
```

---

## Configuration Validation

Django-cfg automatically validates your configuration:

### Validation Rules

```python
# ✅ Valid configurations
RQQueueConfig(queue="default")  # OK
RQQueueConfig(queue="my-queue")  # OK
RQQueueConfig(queue="my_queue")  # OK

# ❌ Invalid configurations
RQQueueConfig(queue="")  # Error: queue name required
RQQueueConfig(queue="my queue")  # Error: contains spaces
RQQueueConfig(queue="My Queue!")  # Error: invalid characters

# ✅ Valid timeouts
RQQueueConfig(queue="default", default_timeout=360)  # OK
RQQueueConfig(queue="default", default_timeout=1)    # OK

# ❌ Invalid timeouts
RQQueueConfig(queue="default", default_timeout=0)    # Error: must be >= 1
RQQueueConfig(queue="default", default_timeout=-1)   # Error: must be >= 1

# ✅ Valid schedules
RQScheduleConfig(func="myapp.tasks.task1", interval=60)  # OK
RQScheduleConfig(func="myapp.tasks.task2", cron="0 * * * *")  # OK

# ❌ Invalid schedules
RQScheduleConfig(func="myapp.tasks.task3")  # Error: no schedule type
RQScheduleConfig(func="myapp.tasks.task4", interval=60, cron="0 * * * *")  # Error: multiple schedule types
```

### Validation Errors

```python
# Missing required queue
django_rq: DjangoRQConfig = DjangoRQConfig(
    enabled=True,
    queues=[
        RQQueueConfig(queue="high"),
        # Missing: RQQueueConfig(queue="default")
    ],
)
# Error: A queue named 'default' is required

# Duplicate queue names
django_rq: DjangoRQConfig = DjangoRQConfig(
    enabled=True,
    queues=[
        RQQueueConfig(queue="default"),
        RQQueueConfig(queue="default"),  # Duplicate
    ],
)
# Error: Duplicate queue names found: {'default'}
```

---

## Configuration Best Practices

### 1. Use Multiple Queues

```python
# Good: Separate queues by priority/purpose
queues=[
    RQQueueConfig(queue="high"),     # Critical tasks
    RQQueueConfig(queue="default"),  # Normal tasks
    RQQueueConfig(queue="low"),      # Batch operations
]

# Bad: Single queue for everything
queues=[
    RQQueueConfig(queue="default"),
]
```

### 2. Set Appropriate Timeouts

```python
# Good: Timeouts match task duration
queues=[
    RQQueueConfig(queue="api_calls", default_timeout=30),     # 30s for API calls
    RQQueueConfig(queue="default", default_timeout=360),      # 6m for normal tasks
    RQQueueConfig(queue="reports", default_timeout=1800),     # 30m for reports
]

# Bad: Same timeout for all tasks
queues=[
    RQQueueConfig(queue="default", default_timeout=360),
]
```

### 3. Use Declarative Schedule Parameters

```python
# Good: Declarative syntax
RQScheduleConfig(
    func="apps.crypto.tasks.update_prices",
    interval=300,
    limit=50,        # Automatically added to kwargs
    verbosity=1,     # Automatically added to kwargs
)

# Bad: Manual kwargs
RQScheduleConfig(
    func="apps.crypto.tasks.update_prices",
    interval=300,
    kwargs={"limit": 50, "verbosity": 1},
)
```

### 4. Use Environment Variables

```python
# Good: Environment variables for secrets
class MyConfig(DjangoConfig):
    redis_url: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")

# Bad: Hardcoded credentials
class MyConfig(DjangoConfig):
    redis_url: str = "redis://:password@production-redis:6379/0"
```

### 5. Enable Monitoring

```python
# Good: Enable monitoring in production
django_rq: DjangoRQConfig = DjangoRQConfig(
    enabled=True,
    show_admin_link=True,
    prometheus_enabled=True,
)

# Bad: Disable monitoring
django_rq: DjangoRQConfig = DjangoRQConfig(
    enabled=True,
    show_admin_link=False,
    prometheus_enabled=False,
)
```

---

## Automatic Cleanup ✨ NEW

### Overview

Django-RQ v1.5.35+ includes **automatic cleanup enabled by default** to prevent Redis bloat and ensure healthy job queue operation.

### What Gets Cleaned Up

**1. Old Finished Jobs** (Daily)
- Removes finished jobs older than `cleanup_max_age_days` (default: 7 days)
- Keeps recent job history for debugging
- Runs every 24 hours (86400s)

**2. Old Failed Jobs** (Daily)
- Removes failed jobs older than `cleanup_max_age_days`
- Preserves recent failures for investigation
- Runs every 24 hours (86400s)

**3. Orphaned Job Keys** (Weekly)
- Removes job keys that don't belong to any queue/registry
- Cleans up keys left after crashes or improper cancellations
- Runs every 7 days (604800s)

### Default Configuration

```python
# Zero configuration - cleanup enabled by default
django_rq: DjangoRQConfig = DjangoRQConfig(
    enabled=True,
    # enable_auto_cleanup=True,   # Default
    # cleanup_max_age_days=7,     # Default
)
```

### Customize Cleanup

```python
# Keep jobs for 14 days instead of 7
django_rq: DjangoRQConfig = DjangoRQConfig(
    enabled=True,
    cleanup_max_age_days=14,  # Jobs kept for 2 weeks
)

# Disable automatic cleanup
django_rq: DjangoRQConfig = DjangoRQConfig(
    enabled=True,
    enable_auto_cleanup=False,  # Manual cleanup only
)
```

### Manual Cleanup

You can still run cleanup manually:

```python
from django_cfg.apps.integrations.rq.tasks.maintenance import (
    cleanup_old_jobs,
    cleanup_orphaned_job_keys,
    get_rq_stats,
)

# Clean up jobs older than 7 days
stats = cleanup_old_jobs(max_age_days=7, dry_run=False)
print(f"Deleted {stats['total_deleted']} jobs")

# Clean up orphaned keys
stats = cleanup_orphaned_job_keys(dry_run=False)
print(f"Deleted {stats['orphaned_deleted']} keys")

# Get RQ statistics
stats = get_rq_stats()
print(f"Queued: {stats['queue']['queued']}")
print(f"Failed: {stats['queue']['failed']}")
```

### Safety Guarantees

- **No data loss**: Only removes old finished/failed jobs, never queued or running jobs
- **No interference**: Scheduled jobs live in separate storage, won't be cleaned up
- **Isolated scope**: Only touches RQ-specific keys (`rq:job:*`, `rq:finished:*`, `rq:failed:*`)
- **Application data safe**: Never touches custom keys (`stockapis:*`, `wallets:*`, etc.)

### Benefits

Before automatic cleanup:
- 4564+ scheduled job duplicates after multiple restarts
- 501 job keys with TTL=-1 (never expire)
- Redis memory growing indefinitely

After automatic cleanup:
- Stable 6-10 scheduled jobs (no duplicates)
- Jobs automatically expire (24h for finished, 7d for failed)
- Automatic cleanup prevents accumulation
- **Zero configuration required!**

---

## See Also

### Documentation
- [Overview](./overview) - Introduction and features
- [Architecture](./architecture) - System design
- [Examples](./examples) - Real-world examples
- [Monitoring](./monitoring) - Monitoring and management

### Reference
- [Django-RQ Docs](https://github.com/rq/django-rq) - Official documentation
- [RQ Docs](https://python-rq.org/) - Core RQ documentation
- [RQ Scheduler](https://github.com/rq/rq-scheduler) - Scheduler documentation
