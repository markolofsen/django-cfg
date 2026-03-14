# django-cfg RQ Integration

REST API layer and management tooling for [django-rq](https://github.com/rq/django-rq) built on top of the django-cfg configuration framework.

**Requires:** `django-rq >= 4.0`, `rq >= 2.7`, `rq-scheduler >= 0.14` (optional, for scheduled jobs)

---

## Contents

- [Overview](#overview)
- [Installation](#installation)
- [Configuration](#configuration)
- [API Endpoints](#api-endpoints)
- [Scheduled Jobs](#scheduled-jobs)
- [Management Commands](#management-commands)
- [Maintenance Tasks](#maintenance-tasks)
- [Internal Models](#internal-models)
- [Module Layout](#module-layout)

---

## Overview

This app wraps django-rq with:

- **REST API** — monitor and manage queues, workers, jobs, and schedules via JSON endpoints
- **Pydantic-based config** — declare queues and scheduled tasks in `DjangoRQConfig` instead of raw `settings.py`
- **Deterministic schedule registration** — stable job IDs prevent duplicate scheduled jobs across restarts
- **Maintenance tasks** — cleanup of old finished/failed jobs and orphaned Redis keys
- **Prometheus metrics** — optional export of queue/worker metrics

---

## Installation

Add to your django-cfg config class:

```python
from django_cfg.models.django.django_rq import DjangoRQConfig

class MyConfig(BaseConfig):
    django_rq: DjangoRQConfig = DjangoRQConfig(
        enabled=True,
        queues={
            "default": {"HOST": "localhost", "PORT": 6379, "DB": 0},
            "high":    {"HOST": "localhost", "PORT": 6379, "DB": 0},
        },
    )
```

`DjangoRQConfig.to_django_settings()` automatically emits `RQ_QUEUES` and `RQ` dict into Django settings. The app is auto-registered via `apps_builder.py` when `enabled=True`.

---

## Configuration

All fields on `DjangoRQConfig` (defined in `django_cfg/models/django/django_rq.py`):

| Field | Default | Description |
|-------|---------|-------------|
| `enabled` | `False` | Enable the integration |
| `queues` | `{}` | Queue definitions forwarded to `RQ_QUEUES` |
| `redis_db` | `1` | Redis DB number for queue isolation |
| `result_ttl` | `500` | Default result TTL (seconds) |
| `scheduler_interval` | `60` | rq-scheduler polling interval (seconds) |
| `prometheus_enabled` | `True` | Expose Prometheus metrics |
| `commit_mode` | `"auto"` | Django-RQ commit mode (see below) |
| `schedules` | `[]` | List of `RQScheduleConfig` for periodic/scheduled jobs |

### Commit Mode

Controls when enqueued jobs are actually pushed to Redis (django-rq v4+):

| Value | Behaviour |
|-------|-----------|
| `"auto"` | Enqueue immediately (v3-compatible default) |
| `"on_db_commit"` | Enqueue after the current DB transaction commits |
| `"request_finished"` | Enqueue at the end of the HTTP request |

---

## API Endpoints

All endpoints are mounted at `/cfg/rq/` and require admin authentication.

| Prefix | ViewSet | Description |
|--------|---------|-------------|
| `monitor/` | `RQMonitorViewSet` | Health checks, config, Prometheus metrics |
| `queues/` | `QueueViewSet` | List queues, get details, empty a queue |
| `workers/` | `WorkerViewSet` | List workers and their statistics |
| `jobs/` | `JobViewSet` | List, cancel, requeue, delete jobs |
| `schedules/` | `ScheduleViewSet` | List, create, retrieve, cancel scheduled jobs |
| `testing/` | `TestingViewSet` | Enqueue demo tasks and stress-test payloads |

### Schedules API

`POST /cfg/rq/schedules/` — create a scheduled job:

```json
{
  "func": "myapp.tasks.send_report",
  "queue_name": "default",
  "args": [42],
  "kwargs": {"format": "pdf"},
  "cron": "0 9 * * 1-5"
}
```

The `func` string is imported and validated at request time — a bad import path returns HTTP 400 immediately rather than failing silently at execution time.

Three scheduling modes:

| Field | Type | Description |
|-------|------|-------------|
| `scheduled_time` | ISO datetime | One-time execution at a specific time |
| `interval` | int (seconds) | Recurring execution every N seconds |
| `cron` | cron string | Recurring execution on a cron schedule |

---

## Scheduled Jobs

Declare recurring jobs in config using `RQScheduleConfig`:

```python
from django_cfg.models.django.django_rq import DjangoRQConfig, RQScheduleConfig

class MyConfig(BaseConfig):
    django_rq: DjangoRQConfig = DjangoRQConfig(
        enabled=True,
        queues={"default": {...}},
        schedules=[
            RQScheduleConfig(
                func="myapp.tasks.daily_report",
                cron="0 8 * * *",
                description="Send daily report at 08:00",
                queue="default",
                timeout=300,
            ),
            RQScheduleConfig(
                func="myapp.tasks.sync_data",
                interval=300,           # every 5 minutes
                description="Sync external data",
            ),
        ],
    )
```

`RQScheduleConfig` fields:

| Field | Description |
|-------|-------------|
| `func` | Dotted import path to the task function |
| `cron` | Cron expression (mutually exclusive with `interval`/`scheduled_time`) |
| `interval` | Repeat interval in seconds |
| `scheduled_time` | ISO datetime for one-time execution |
| `args` | Positional arguments for the task |
| `kwargs` | Keyword arguments for the task |
| `queue` | Target queue (defaults to `"default"`) |
| `timeout` | Job execution timeout in seconds |
| `result_ttl` | How long to keep job result in Redis |
| `repeat` | Number of repetitions (`None` = infinite) |
| `description` | Human-readable description shown in the RQ dashboard |
| `job_id` | Override the auto-generated deterministic job ID |

### Schedule Registration

Schedules are registered **only by the `rqscheduler` management command**, not on `AppConfig.ready()`. This prevents race conditions in multi-container deployments.

Job IDs are deterministic (SHA-256 hash of func + queue + schedule params), so restarting the scheduler replaces existing jobs rather than creating duplicates.

---

## Management Commands

### `rqscheduler`

Wraps django-rq's `rqscheduler` command with two additions:

1. Cleans up stale `rq:scheduler_instance:*` Redis locks from crashed processes
2. Registers schedules from `DjangoRQConfig.schedules`

```bash
python manage.py rqscheduler
python manage.py rqscheduler --queue high   # must match the queue in RQScheduleConfig
python manage.py rqscheduler --interval 30  # polling interval in seconds
```

> **Important:** rq-scheduler processes jobs for exactly one queue per daemon instance. If your tasks target `queue="high"`, run `rqscheduler --queue high`.

### `rqworker`

Standard django-rq worker with django-cfg dependency validation:

```bash
python manage.py rqworker default high
```

### `rqworker_pool`

Worker pool (rq 2.x):

```bash
python manage.py rqworker_pool default --num-workers 4
```

### `rqstats`

Print queue/worker statistics:

```bash
python manage.py rqstats
python manage.py rqstats --interval 5   # refresh every 5 seconds
```

### `rq_cleanup_locks`

Remove stale Redis locks left by crashed workers or schedulers:

```bash
python manage.py rq_cleanup_locks
```

---

## Maintenance Tasks

Located in `tasks/maintenance.py`. Designed to be scheduled via `RQScheduleConfig`.

### `cleanup_old_jobs`

Delete finished and failed jobs older than N days:

```python
from django_cfg.apps.integrations.rq.tasks.maintenance import cleanup_old_jobs

# Dry run
stats = cleanup_old_jobs(max_age_days=7, dry_run=True)
print(f"Would delete {stats['total_deleted']} jobs")

# Actually delete
stats = cleanup_old_jobs(max_age_days=7, queue_name="default")
```

### `cleanup_orphaned_job_keys`

Remove `rq:job:*` Redis keys not referenced by any queue, registry, or the scheduler sorted set:

```python
from django_cfg.apps.integrations.rq.tasks.maintenance import cleanup_orphaned_job_keys

stats = cleanup_orphaned_job_keys(dry_run=True)
```

### `diagnose_scheduled_jobs`

Check that every job ID in `rq:scheduler:scheduled_jobs` has a corresponding `rq:job:*` key:

```python
from django_cfg.apps.integrations.rq.tasks.maintenance import diagnose_scheduled_jobs

result = diagnose_scheduled_jobs()
if result["missing_keys"] > 0:
    print(f"{result['missing_keys']} scheduled jobs have missing Redis keys")
```

### Auto-scheduling maintenance

Add maintenance tasks to your config to run them automatically:

```python
schedules=[
    RQScheduleConfig(
        func="django_cfg.apps.integrations.rq.tasks.maintenance.cleanup_old_jobs",
        cron="0 3 * * *",          # daily at 03:00
        kwargs={"max_age_days": 14},
        description="Clean up jobs older than 14 days",
    ),
]
```

---

## Internal Models

`services/models/` — Pydantic models for internal data transfer (not Django ORM models):

| Model | Description |
|-------|-------------|
| `RQJobModel` | Flat representation of an RQ job (all timestamps as ISO strings, args/kwargs as JSON strings) |
| `RQQueueModel` | Queue statistics |
| `RQWorkerModel` | Worker statistics |
| `RQEventModel` | Worker lifecycle events |

### `JobStatus` enum

Maps rq's `JobStatus` enum to django-cfg's internal representation:

```python
class JobStatus(str, Enum):
    QUEUED    = "queued"
    STARTED   = "started"
    FINISHED  = "finished"
    FAILED    = "failed"
    DEFERRED  = "deferred"
    SCHEDULED = "scheduled"
    CANCELED  = "canceled"
    CREATED   = "created"   # rq 2.x
    STOPPED   = "stopped"   # rq 2.x
```

---

## Module Layout

```
rq/
├── apps.py                        # AppConfig — dependency checks, admin registration
├── urls.py                        # Router — mounts all ViewSets at /cfg/rq/
├── _cfg/
│   └── dependencies.py            # Dependency validation helpers
├── management/commands/
│   ├── rqscheduler.py             # Wrapper: lock cleanup + schedule registration
│   ├── rqworker.py                # Wrapper: django-rq rqworker
│   ├── rqworker_pool.py           # Wrapper: rq 2.x worker pool
│   ├── rqstats.py                 # Queue/worker statistics
│   └── rq_cleanup_locks.py        # Remove stale Redis locks
├── services/
│   ├── config_helper.py           # register_schedules_from_config() + Redis helpers
│   ├── cancellation.py            # Job cancellation logic
│   ├── job_service.py             # Job fetching and registry access
│   ├── rq_converters.py           # rq Job → RQJobModel conversion
│   └── models/
│       ├── job.py                 # RQJobModel, JobStatus
│       ├── queue.py               # RQQueueModel
│       ├── worker.py              # RQWorkerModel
│       └── event.py               # RQEventModel
├── serializers/                   # DRF serializers for all ViewSets
├── tasks/
│   ├── maintenance.py             # cleanup_old_jobs, cleanup_orphaned_job_keys, etc.
│   └── demo_tasks.py              # Demo/test tasks for the testing endpoint
└── views/
    ├── monitoring.py              # RQMonitorViewSet
    ├── queues.py                  # QueueViewSet
    ├── workers.py                 # WorkerViewSet
    ├── jobs.py                    # JobViewSet
    ├── schedule.py                # ScheduleViewSet
    └── testing.py                 # TestingViewSet
```
