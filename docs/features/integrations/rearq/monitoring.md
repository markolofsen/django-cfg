> **📚 Part of**: [ReArq Integration](/features/integrations/rearq/overview) - Return to ReArq overview

# ReArq Monitoring and Observability

**Version**: 1.0
**Last Updated**: 2025-10-30
**Status**: Production Ready

## Table of Contents

1. [Overview](#overview)
2. [TaskLog Model](#tasklog-model)
3. [TaskLog REST API](#tasklog-rest-api)
4. [Django Admin Interface](#django-admin-interface)
5. [ReArq Built-in Server](#rearq-built-in-server)
6. [Error Tracking](#error-tracking)
7. [Performance Metrics](#performance-metrics)
8. [Statistics and Analytics](#statistics-and-analytics)
9. [Health Checks](#health-checks)
10. [Alerting](#alerting)
11. [Best Practices](#best-practices)

---

## Overview

Django-CFG provides comprehensive monitoring and observability for ReArq task execution through multiple interfaces:

- **TaskLog Model**: Django ORM model for historical task execution tracking
- **REST API**: DRF-based API for programmatic access to task logs
- **Django Admin**: Rich web interface for browsing and analyzing task execution
- **ReArq Server**: Built-in FastAPI monitoring UI (port 7380)

### Architecture

```
┌─────────────────────────────────────────────────────┐
│                Django Application                    │
├─────────────────────────────────────────────────────┤
│                                                       │
│  ┌────────────────────────────────────────────┐    │
│  │         ReArq Database (Tortoise)          │    │
│  │  ┌──────────────┐  ┌──────────────────┐   │    │
│  │  │  rearq_job   │  │ rearq_job_result │   │    │
│  │  │  (operational)│  │   (operational)  │   │    │
│  │  └──────────────┘  └──────────────────┘   │    │
│  │          ▲                  ▲               │    │
│  │          │                  │               │    │
│  │     ReArq Workers      ReArq API           │    │
│  │   (read/write)        (port 7380)          │    │
│  └────────────────────────────────────────────┘    │
│                                                       │
│  ┌────────────────────────────────────────────┐    │
│  │       Django Database (Django ORM)          │    │
│  │  ┌──────────────────────────────────┐      │    │
│  │  │    django_cfg_task_log           │      │    │
│  │  │    (historical/analytics)        │      │    │
│  │  └──────────────────────────────────┘      │    │
│  │                 ▲                            │    │
│  │                 │                            │    │
│  │          TaskLog API                        │    │
│  │      /cfg/tasks/logs/                       │    │
│  └────────────────────────────────────────────┘    │
│                                                       │
└─────────────────────────────────────────────────────┘
```

### Key Features

- **Dual Database Architecture**: Operational data in ReArq DB, historical data in Django DB
- **Real-time Monitoring**: ReArq FastAPI server for active jobs
- **Historical Analysis**: TaskLog for completed task analysis
- **Advanced Filtering**: 30+ filter options for precise queries
- **Performance Tracking**: Duration metrics, retry counts, success rates
- **User Attribution**: Link tasks to Django users
- **Admin Integration**: Rich Django admin interface with badges and charts

---

## TaskLog Model

The `TaskLog` model stores historical execution data for all ReArq tasks.

### Model Definition

**Location**: `/apps/tasks/models/task_log.py`

```python
from django.db import models
from django.conf import settings

class TaskLog(models.Model):
    """
    Log of task executions.

    Stores execution history from ReArq task queue.
    Status values match ReArq's JobStatus enum.
    """

    class StatusChoices(models.TextChoices):
        DEFERRED = "deferred", "Deferred"
        QUEUED = "queued", "Queued"
        IN_PROGRESS = "in_progress", "In Progress"
        SUCCESS = "success", "Success"
        FAILED = "failed", "Failed"
        EXPIRED = "expired", "Expired"
        CANCELED = "canceled", "Canceled"

    # Task identification
    job_id = models.CharField(max_length=100, unique=True, db_index=True)
    task_name = models.CharField(max_length=200, db_index=True)
    queue_name = models.CharField(max_length=100, db_index=True)

    # Arguments
    args = models.JSONField(default=list)
    kwargs = models.JSONField(default=dict)

    # Status tracking
    status = models.CharField(
        max_length=20,
        choices=StatusChoices.choices,
        default=StatusChoices.QUEUED,
        db_index=True
    )

    # Performance metrics
    duration_ms = models.IntegerField(null=True, blank=True)

    # Retry configuration (from ReArq Job)
    job_retry = models.IntegerField(default=0)
    job_retries = models.IntegerField(default=0)
    job_retry_after = models.IntegerField(default=60)

    # Result tracking
    success = models.BooleanField(null=True, blank=True)
    result = models.TextField(null=True, blank=True)
    error_message = models.TextField(null=True, blank=True)

    # Worker information
    worker_id = models.CharField(max_length=100, null=True, blank=True)

    # Timestamps (matching ReArq Job fields)
    enqueue_time = models.DateTimeField(db_index=True)
    expire_time = models.DateTimeField(null=True, blank=True)
    start_time = models.DateTimeField(null=True, blank=True)
    finish_time = models.DateTimeField(null=True, blank=True)

    # Django-specific timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # User tracking
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    class Meta:
        db_table = "django_cfg_task_log"
        ordering = ["-enqueue_time"]
        indexes = [
            models.Index(fields=["task_name", "-enqueue_time"]),
            models.Index(fields=["status", "-enqueue_time"]),
            models.Index(fields=["queue_name", "status"]),
            models.Index(fields=["success", "-enqueue_time"]),
            models.Index(fields=["-created_at"]),
        ]
```

### Field Descriptions

| Field | Type | Description |
|-------|------|-------------|
| `job_id` | CharField | Unique job identifier from ReArq (UUID) |
| `task_name` | CharField | Name of the task function |
| `queue_name` | CharField | Queue where task was executed |
| `args` | JSONField | Positional arguments passed to task |
| `kwargs` | JSONField | Keyword arguments passed to task |
| `status` | CharField | Current task status (7 choices) |
| `duration_ms` | IntegerField | Task execution duration in milliseconds |
| `job_retry` | IntegerField | Maximum number of retries allowed |
| `job_retries` | IntegerField | Number of retries performed so far |
| `job_retry_after` | IntegerField | Seconds to wait before retry |
| `success` | BooleanField | Whether task completed successfully |
| `result` | TextField | Task result (JSON string) |
| `error_message` | TextField | Error message if task failed |
| `worker_id` | CharField | ID of worker that processed the task |
| `enqueue_time` | DateTimeField | When job was enqueued to ReArq |
| `expire_time` | DateTimeField | When job will expire |
| `start_time` | DateTimeField | When task execution started |
| `finish_time` | DateTimeField | When task execution finished |
| `created_at` | DateTimeField | When TaskLog record was created |
| `updated_at` | DateTimeField | When TaskLog record was last updated |
| `user` | ForeignKey | User who triggered the task |

### Status Mapping

TaskLog status values match ReArq's JobStatus enum:

| Status | Description | Terminal |
|--------|-------------|----------|
| `deferred` | Scheduled for later execution | No |
| `queued` | In queue, waiting for worker | No |
| `in_progress` | Currently executing | No |
| `success` | Completed successfully | Yes |
| `failed` | Failed with error | Yes |
| `expired` | Expired before execution | Yes |
| `canceled` | Manually canceled | Yes |

### Computed Properties

```python
@property
def is_completed(self) -> bool:
    """Check if task is in a terminal state."""
    return self.status in [
        self.StatusChoices.SUCCESS,
        self.StatusChoices.FAILED,
        self.StatusChoices.EXPIRED,
        self.StatusChoices.CANCELED,
    ]

@property
def is_successful(self) -> bool:
    """Check if task completed successfully."""
    return self.status == self.StatusChoices.SUCCESS and self.success is True

@property
def is_failed(self) -> bool:
    """Check if task failed."""
    return self.status in [
        self.StatusChoices.FAILED,
        self.StatusChoices.EXPIRED,
    ] or self.success is False
```

### Helper Methods

```python
def mark_started(self, worker_id: str = None, start_time=None):
    """Mark task as started."""
    self.status = self.StatusChoices.IN_PROGRESS
    self.start_time = start_time or timezone.now()
    if worker_id:
        self.worker_id = worker_id
    self.save(update_fields=["status", "start_time", "worker_id", "updated_at"])

def mark_completed(self, result: str = None, finish_time=None):
    """Mark task as completed successfully."""
    self.status = self.StatusChoices.SUCCESS
    self.success = True
    self.finish_time = finish_time or timezone.now()
    if result is not None:
        self.result = result

    # Calculate duration
    if self.start_time and self.finish_time:
        delta = self.finish_time - self.start_time
        self.duration_ms = int(delta.total_seconds() * 1000)

    self.save(update_fields=["status", "success", "finish_time", "result", "duration_ms", "updated_at"])

def mark_failed(self, error_message: str, finish_time=None):
    """Mark task as failed with error message."""
    self.status = self.StatusChoices.FAILED
    self.success = False
    self.error_message = error_message
    self.finish_time = finish_time or timezone.now()

    # Calculate duration
    if self.start_time and self.finish_time:
        delta = self.finish_time - self.start_time
        self.duration_ms = int(delta.total_seconds() * 1000)

    self.save(update_fields=["status", "success", "error_message", "finish_time", "duration_ms", "updated_at"])
```

---

## TaskLog REST API

The TaskLog API provides programmatic access to task execution history.

**Base URL**: `/cfg/tasks/logs/`
**Authentication**: Django session or token-based
**Format**: JSON (DRF standard pagination)

### Endpoints

#### 1. List Task Logs

**Endpoint**: `GET /cfg/tasks/logs/`

**Description**: List all task logs with filtering, searching, and pagination.

**Query Parameters**:

| Parameter | Type | Description |
|-----------|------|-------------|
| `task_name` | string | Filter by task name (contains) |
| `task_name_exact` | string | Filter by exact task name |
| `queue_name` | string | Filter by queue name |
| `queue_name_in` | string | Filter by multiple queues (comma-separated) |
| `status` | string | Filter by status |
| `status_in` | string | Filter by multiple statuses |
| `job_id` | string | Filter by job ID |
| `is_completed` | boolean | Filter completed tasks |
| `is_successful` | boolean | Filter successful tasks |
| `is_failed` | boolean | Filter failed tasks |
| `created_after` | datetime | Filter by creation date (gte) |
| `created_before` | datetime | Filter by creation date (lte) |
| `duration_min` | integer | Minimum duration in milliseconds |
| `duration_max` | integer | Maximum duration in milliseconds |
| `job_retries_min` | integer | Minimum retry count |
| `job_retries_max` | integer | Maximum retry count |
| `has_error` | boolean | Has error message |
| `search` | string | Search across task_name, job_id, queue_name, error_message, worker_id |
| `ordering` | string | Order by field (prefix with `-` for descending) |
| `page` | integer | Page number |
| `page_size` | integer | Items per page |

**Example Request**:

```bash
# Get failed tasks from the last 24 hours
curl -X GET "/cfg/tasks/logs/?is_failed=true&created_after=2025-10-29T00:00:00Z"

# Get tasks by name with pagination
curl -X GET "/cfg/tasks/logs/?task_name=process_data&page=1&page_size=20"

# Get slow tasks (> 30 seconds)
curl -X GET "/cfg/tasks/logs/?duration_min=30000&ordering=-duration_ms"

# Search across multiple fields
curl -X GET "/cfg/tasks/logs/?search=error&ordering=-created_at"
```

**Response Format**:

```json
{
  "count": 150,
  "next": "http://example.com/cfg/tasks/logs/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "job_id": "efdfd9dc3a2e4c68a92a6362d83cd9c7",
      "task_name": "process_data",
      "queue_name": "default",
      "status": "success",
      "status_display": "Success",
      "success": true,
      "job_retries": 0,
      "duration_ms": 1250,
      "enqueue_time": "2025-10-30T10:00:00Z",
      "start_time": "2025-10-30T10:00:01Z",
      "finish_time": "2025-10-30T10:00:02Z"
    }
  ]
}
```

#### 2. Get Task Log Details

**Endpoint**: `GET /cfg/tasks/logs/{id}/`

**Description**: Get detailed information for a specific task log.

**Example Request**:

```bash
curl -X GET "/cfg/tasks/logs/123/"
```

**Response Format**:

```json
{
  "id": 123,
  "job_id": "efdfd9dc3a2e4c68a92a6362d83cd9c7",
  "task_name": "process_data",
  "queue_name": "default",
  "status": "success",
  "status_display": "Success",
  "success": true,
  "args": [1, 2, 3],
  "kwargs": {
    "message": "test",
    "priority": "high"
  },
  "result": "{\"status\": \"completed\", \"records_processed\": 150}",
  "error_message": null,
  "duration_ms": 1250,
  "duration_seconds": 1.25,
  "job_retry": 3,
  "job_retries": 0,
  "job_retry_after": 60,
  "worker_id": "worker-1-12345",
  "enqueue_time": "2025-10-30T10:00:00Z",
  "expire_time": null,
  "start_time": "2025-10-30T10:00:01Z",
  "finish_time": "2025-10-30T10:00:02Z",
  "created_at": "2025-10-30T10:00:00Z",
  "updated_at": "2025-10-30T10:00:02Z",
  "user": 1,
  "user_display": "admin (admin@example.com)"
}
```

#### 3. Get Task Statistics

**Endpoint**: `GET /cfg/tasks/logs/stats/`

**Description**: Get aggregated statistics for task execution.

**Query Parameters**:

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| `period_hours` | integer | Statistics period in hours | 24 |
| `task_name` | string | Filter by specific task name | - |

**Example Request**:

```bash
# Get stats for last 24 hours
curl -X GET "/cfg/tasks/logs/stats/"

# Get stats for specific task in last 7 days
curl -X GET "/cfg/tasks/logs/stats/?period_hours=168&task_name=process_data"
```

**Response Format**:

```json
{
  "total": 150,
  "successful": 145,
  "failed": 5,
  "in_progress": 2,
  "success_rate": 96.67,
  "avg_duration_ms": 1250,
  "avg_duration_seconds": 1.25,
  "period_hours": 24
}
```

#### 4. Get Task Timeline

**Endpoint**: `GET /cfg/tasks/logs/timeline/`

**Description**: Get task execution timeline grouped by time intervals.

**Query Parameters**:

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| `period_hours` | integer | Timeline period in hours | 24 |
| `interval` | string | Grouping interval ('hour', 'day') | hour |
| `task_name` | string | Filter by specific task name | - |

**Example Request**:

```bash
# Get hourly timeline for last 24 hours
curl -X GET "/cfg/tasks/logs/timeline/"

# Get daily timeline for last week
curl -X GET "/cfg/tasks/logs/timeline/?period_hours=168&interval=day"
```

**Response Format**:

```json
[
  {
    "timestamp": "2025-10-30T10:00:00Z",
    "total": 15,
    "successful": 14,
    "failed": 1,
    "avg_duration_ms": 1200
  },
  {
    "timestamp": "2025-10-30T11:00:00Z",
    "total": 18,
    "successful": 18,
    "failed": 0,
    "avg_duration_ms": 950
  }
]
```

#### 5. Get System Overview

**Endpoint**: `GET /cfg/tasks/logs/overview/`

**Description**: Get summary overview of the task system.

**Example Request**:

```bash
curl -X GET "/cfg/tasks/logs/overview/"
```

**Response Format**:

```json
{
  "total_tasks": 1500,
  "active_queues": ["default", "high", "knowledge"],
  "recent_failures": 5,
  "tasks_by_queue": {
    "default": 800,
    "high": 500,
    "knowledge": 200
  },
  "tasks_by_status": {
    "success": 1450,
    "failed": 45,
    "in_progress": 5
  }
}
```

#### 6. Get Related Tasks

**Endpoint**: `GET /cfg/tasks/logs/{id}/related/`

**Description**: Get related task logs (same job_id or task_name).

**Example Request**:

```bash
curl -X GET "/cfg/tasks/logs/123/related/"
```

**Response Format**:

```json
[
  {
    "id": 124,
    "job_id": "efdfd9dc3a2e4c68a92a6362d83cd9c7",
    "task_name": "process_data",
    "queue_name": "default",
    "status": "failed",
    "status_display": "Failed",
    "success": false,
    "job_retries": 1,
    "duration_ms": 2300,
    "enqueue_time": "2025-10-30T10:05:00Z",
    "start_time": "2025-10-30T10:05:01Z",
    "finish_time": "2025-10-30T10:05:03Z"
  }
]
```

### API Usage Examples

#### Python (requests)

```python
import requests

# Get failed tasks
response = requests.get(
    "http://localhost:8000/cfg/tasks/logs/",
    params={
        "is_failed": True,
        "created_after": "2025-10-29T00:00:00Z"
    },
    headers={"Authorization": "Token YOUR_TOKEN"}
)
tasks = response.json()["results"]

# Get statistics
response = requests.get(
    "http://localhost:8000/cfg/tasks/logs/stats/",
    params={"period_hours": 168}
)
stats = response.json()
print(f"Success rate: {stats['success_rate']}%")

# Get task details
response = requests.get(
    "http://localhost:8000/cfg/tasks/logs/123/"
)
task = response.json()
print(f"Duration: {task['duration_seconds']}s")
```

#### JavaScript (fetch)

```javascript
// Get failed tasks
const response = await fetch('/cfg/tasks/logs/?is_failed=true');
const data = await response.json();
console.log(`Failed tasks: ${data.count}`);

// Get statistics
const statsResponse = await fetch('/cfg/tasks/logs/stats/?period_hours=24');
const stats = await statsResponse.json();
console.log(`Success rate: ${stats.success_rate}%`);

// Get task details
const taskResponse = await fetch('/cfg/tasks/logs/123/');
const task = await taskResponse.json();
console.log(`Task: ${task.task_name}, Status: ${task.status}`);
```

#### cURL

```bash
# Get all tasks
curl -X GET "http://localhost:8000/cfg/tasks/logs/"

# Get failed tasks with authentication
curl -X GET "http://localhost:8000/cfg/tasks/logs/?is_failed=true" \
  -H "Authorization: Token YOUR_TOKEN"

# Get statistics for specific task
curl -X GET "http://localhost:8000/cfg/tasks/logs/stats/?task_name=process_data&period_hours=168"

# Search tasks
curl -X GET "http://localhost:8000/cfg/tasks/logs/?search=error&ordering=-created_at"
```

---

## Django Admin Interface

The Django Admin provides a rich web interface for browsing and analyzing task execution.

**URL**: `/admin/tasks/tasklog/`

### Features

- **Color-coded Status Badges**: Visual status indicators
- **Duration Display**: Performance indicators with color coding
- **Retry Count Tracking**: Badge display with warning levels
- **Formatted JSON**: Pretty-printed arguments and results
- **Error Highlighting**: Red-highlighted error messages
- **Queue Badges**: Color-coded queue indicators
- **Advanced Filtering**: Filter by status, task name, queue, dates
- **Search**: Full-text search across multiple fields
- **Date Hierarchy**: Browse by creation date
- **Performance Summary**: Duration, retries, worker info

### List View

The list view shows key information at a glance:

| Column | Description | Features |
|--------|-------------|----------|
| Task Name | Name of the task | Sortable, searchable |
| Queue | Queue badge | Color-coded by priority |
| Status | Status badge | Icon + color by status |
| User | User who triggered | Link to user |
| Duration | Execution time | Color-coded by speed |
| Retry Count | Number of retries | Badge with warning colors |
| Created At | When task was created | Date hierarchy |
| Completed At | When task finished | Sortable |

### Status Badge Colors

| Status | Color | Icon |
|--------|-------|------|
| Queued | Secondary (gray) | Timer |
| In Progress | Info (blue) | Speed |
| Success | Success (green) | Check Circle |
| Failed | Danger (red) | Error |
| Canceled | Warning (yellow) | Warning |

### Duration Color Coding

| Duration | Color | Icon | Description |
|----------|-------|------|-------------|
| < 1s | Success (green) | Speed | Fast |
| 1s - 5s | Info (blue) | Timer | Normal |
| 5s - 30s | Warning (yellow) | Timer | Slow |
| > 30s | Danger (red) | Error | Very slow |

### Queue Badge Colors

| Queue | Color |
|-------|-------|
| critical | Danger (red) |
| high | Warning (yellow) |
| default | Primary (blue) |
| low | Secondary (gray) |
| background | Secondary (gray) |

### Detail View

The detail view is organized into fieldsets:

**Task Information**:
- ID
- Job ID
- Task Name
- Queue Name
- Status
- User

**Arguments** (collapsible):
- Pretty-printed JSON of args and kwargs

**Performance**:
- Performance summary (duration, retries, worker)
- Created At
- Started At
- Completed At

**Error Details** (only if failed):
- Error details display with icon
- Full error message
- Retry information

### Filters

Available filters in the admin sidebar:

- **Status**: All status choices
- **Task Name**: All unique task names
- **Queue Name**: All unique queues
- **Created At**: Date hierarchy (year, month, day)

### Search

Search across these fields:
- Job ID
- Task Name
- Worker ID
- Error Message
- User Username
- User Email

### Configuration

**Location**: `/apps/tasks/admin/config.py`

```python
from django_cfg.modules.django_admin import (
    AdminConfig,
    BadgeField,
    DateTimeField,
    Icons,
    UserField,
)

tasklog_config = AdminConfig(
    model=TaskLog,

    # Performance optimization
    select_related=["user"],

    # List display
    list_display=[
        "task_name",
        "queue_badge",
        "status_badge",
        "user",
        "duration_display",
        "retry_count",
        "created_at",
        "completed_at",
    ],

    # Filters
    list_filter=["status", "task_name", "queue_name", "created_at"],
    search_fields=[
        "job_id",
        "task_name",
        "worker_id",
        "error_message",
        "user__username",
        "user__email",
    ],

    # Autocomplete for user field
    autocomplete_fields=["user"],

    # Date hierarchy
    date_hierarchy="created_at",

    # Per page
    list_per_page=50,

    # Ordering
    ordering=["-created_at"],
)
```

---

## ReArq Built-in Server

ReArq includes a built-in FastAPI monitoring server for real-time job monitoring.

**URL**: `http://localhost:7380/`
**Technology**: FastAPI + Tortoise ORM
**Database**: Separate from Django (SQLite/MySQL/PostgreSQL)

### Features

- **Web UI**: HTML interface for browsing jobs
- **REST API**: JSON API for programmatic access
- **Real-time Data**: Direct access to operational queue data
- **Job Management**: Create, update, cancel jobs
- **Worker Monitoring**: View active workers and their status

### ReArq API Endpoints

#### Job Endpoints

```
GET  /job                 - HTML page (web UI)
GET  /job/data            - List jobs (JSON API)
GET  /job/result?job_id=  - Get job result
POST /job                 - Create/enqueue job
PUT  /job                 - Update job (only queued/deferred)
PUT  /job/cancel          - Cancel job
DELETE /job?ids=1,2,3     - Delete jobs by IDs
```

#### Job List API

**Endpoint**: `GET /job/data`

**Query Parameters**:
- `task`: Filter by task name
- `job_id`: Filter by job ID
- `start_time`: Filter by enqueue time (gte)
- `end_time`: Filter by enqueue time (lte)
- `status`: Filter by status
- `limit`: Page size (default: 10)
- `offset`: Page offset (default: 0)

**Example**:

```bash
# Get all jobs
curl "http://localhost:7380/job/data"

# Get jobs by status
curl "http://localhost:7380/job/data?status=in_progress"

# Get jobs with pagination
curl "http://localhost:7380/job/data?limit=50&offset=0"
```

**Response Format**:

```json
{
  "rows": [
    {
      "id": 1,
      "task": "example_task",
      "args": [],
      "kwargs": {"message": "test"},
      "job_retry": 3,
      "job_retries": 0,
      "job_retry_after": 60,
      "job_id": "efdfd9dc3a2e4c68a92a6362d83cd9c7",
      "enqueue_time": "2025-10-30T11:09:10.042374Z",
      "expire_time": null,
      "status": "queued"
    }
  ],
  "total": 1
}
```

#### Job Result API

**Endpoint**: `GET /job/result?job_id={job_id}`

**Example**:

```bash
curl "http://localhost:7380/job/result?job_id=efdfd9dc3a2e4c68a92a6362d83cd9c7"
```

**Response Format**:

```json
{
  "id": 1,
  "worker": "9b79ed0c91ac-1",
  "success": true,
  "msg_id": "...",
  "result": "{\"data\": \"result\"}",
  "start_time": "2025-10-30T11:09:11Z",
  "finish_time": "2025-10-30T11:09:12Z",
  "job": {
    "id": 1,
    "task": "example_task",
    "job_id": "efdfd9dc3a2e4c68a92a6362d83cd9c7",
    "status": "success"
  }
}
```

### Starting the ReArq Server

The ReArq server is typically started as a separate process:

```bash
# Start ReArq server on default port 7380
rearq server

# Start with custom port
rearq server --port 8380

# Start with specific database
rearq server --db-url postgresql://user:pass@localhost/rearq
```

In production, use a process manager like systemd or supervisord:

```ini
# /etc/supervisor/conf.d/rearq-server.conf
[program:rearq-server]
command=/usr/local/bin/rearq server
directory=/app
user=www-data
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/rearq/server.log
```

### Accessing the Web UI

1. Open browser to `http://localhost:7380/`
2. View list of all jobs with status
3. Click job to see details
4. Use filters to find specific jobs

---

## Error Tracking

### Error Information in TaskLog

TaskLog captures comprehensive error information:

```python
class TaskLog(models.Model):
    # Error tracking fields
    error_message = models.TextField(null=True, blank=True)
    success = models.BooleanField(null=True, blank=True)
    status = models.CharField(...)  # 'failed', 'expired', 'canceled'
```

### Querying Failed Tasks

**API**:

```bash
# Get all failed tasks
curl "/cfg/tasks/logs/?is_failed=true"

# Get tasks with errors
curl "/cfg/tasks/logs/?has_error=true"

# Get failed tasks by task name
curl "/cfg/tasks/logs/?task_name=process_data&is_failed=true"

# Search error messages
curl "/cfg/tasks/logs/?search=timeout&is_failed=true"
```

**Django ORM**:

```python
from django_cfg.apps.tasks.models import TaskLog

# Get all failed tasks
failed_tasks = TaskLog.objects.filter(is_failed=True)

# Get tasks with specific error
timeout_tasks = TaskLog.objects.filter(
    error_message__icontains='timeout'
)

# Get recent failures (last 24 hours)
from django.utils import timezone
from datetime import timedelta

recent_failures = TaskLog.objects.filter(
    is_failed=True,
    created_at__gte=timezone.now() - timedelta(hours=24)
)

# Group errors by type
from django.db.models import Count

error_stats = TaskLog.objects.filter(
    is_failed=True
).values('task_name').annotate(
    count=Count('id')
).order_by('-count')
```

### Error Reporting Example

```python
def get_error_report(hours=24):
    """Generate error report for last N hours."""
    from django.utils import timezone
    from datetime import timedelta
    from django.db.models import Count

    time_threshold = timezone.now() - timedelta(hours=hours)

    # Get failed tasks
    failed_tasks = TaskLog.objects.filter(
        is_failed=True,
        created_at__gte=time_threshold
    )

    # Group by task name
    by_task = failed_tasks.values('task_name').annotate(
        count=Count('id')
    ).order_by('-count')

    # Group by error message
    by_error = failed_tasks.values('error_message').annotate(
        count=Count('id')
    ).order_by('-count')[:10]

    return {
        'total_failures': failed_tasks.count(),
        'by_task': list(by_task),
        'top_errors': list(by_error),
        'period_hours': hours
    }
```

---

## Performance Metrics

### Available Metrics

TaskLog tracks several performance-related metrics:

| Metric | Field | Description |
|--------|-------|-------------|
| Duration | `duration_ms` | Execution time in milliseconds |
| Retry Count | `job_retries` | Number of times task was retried |
| Queue Time | `start_time - enqueue_time` | Time waiting in queue |
| Success Rate | Computed | Percentage of successful executions |

### Duration Analysis

**API**:

```bash
# Get slow tasks (> 30 seconds)
curl "/cfg/tasks/logs/?duration_min=30000&ordering=-duration_ms"

# Get fast tasks (< 1 second)
curl "/cfg/tasks/logs/?duration_max=1000&ordering=duration_ms"

# Get average duration
curl "/cfg/tasks/logs/stats/?task_name=process_data"
```

**Django ORM**:

```python
from django.db.models import Avg, Max, Min, Count

# Get duration statistics
stats = TaskLog.objects.filter(
    task_name='process_data',
    duration_ms__isnull=False
).aggregate(
    avg_duration=Avg('duration_ms'),
    max_duration=Max('duration_ms'),
    min_duration=Min('duration_ms'),
    count=Count('id')
)

# Get slow tasks
slow_tasks = TaskLog.objects.filter(
    duration_ms__gt=30000
).order_by('-duration_ms')

# Get duration percentiles
from django.db.models import F, FloatField
from django.db.models.functions import Cast

tasks = TaskLog.objects.filter(
    task_name='process_data',
    duration_ms__isnull=False
).annotate(
    duration_seconds=Cast('duration_ms', FloatField()) / 1000
).order_by('duration_ms')

count = tasks.count()
p50 = tasks[int(count * 0.5)].duration_ms if count > 0 else 0
p95 = tasks[int(count * 0.95)].duration_ms if count > 0 else 0
p99 = tasks[int(count * 0.99)].duration_ms if count > 0 else 0
```

### Performance Dashboard Example

```python
def get_performance_dashboard(task_name: str, hours: int = 24):
    """Generate performance dashboard for a task."""
    from django.utils import timezone
    from datetime import timedelta
    from django.db.models import Avg, Max, Min, Count

    time_threshold = timezone.now() - timedelta(hours=hours)

    # Base queryset
    tasks = TaskLog.objects.filter(
        task_name=task_name,
        created_at__gte=time_threshold
    )

    # Overall stats
    total = tasks.count()
    successful = tasks.filter(is_successful=True).count()
    failed = tasks.filter(is_failed=True).count()

    # Duration stats (only completed tasks)
    duration_stats = tasks.filter(
        duration_ms__isnull=False
    ).aggregate(
        avg=Avg('duration_ms'),
        max=Max('duration_ms'),
        min=Min('duration_ms')
    )

    # Retry stats
    retry_stats = tasks.aggregate(
        avg_retries=Avg('job_retries'),
        max_retries=Max('job_retries')
    )

    # Queue distribution
    by_queue = tasks.values('queue_name').annotate(
        count=Count('id')
    ).order_by('-count')

    return {
        'task_name': task_name,
        'period_hours': hours,
        'total_executions': total,
        'successful': successful,
        'failed': failed,
        'success_rate': (successful / total * 100) if total > 0 else 0,
        'duration': {
            'avg_ms': int(duration_stats['avg'] or 0),
            'max_ms': duration_stats['max'] or 0,
            'min_ms': duration_stats['min'] or 0,
        },
        'retries': {
            'avg': round(retry_stats['avg_retries'] or 0, 2),
            'max': retry_stats['max_retries'] or 0
        },
        'by_queue': list(by_queue)
    }
```

---

## Statistics and Analytics

### Built-in Statistics API

The `/stats/` endpoint provides aggregated metrics:

```python
# apps/tasks/views/task_log.py
@action(detail=False, methods=['get'])
def stats(self, request):
    """Get aggregated task statistics."""
    period_hours = int(request.query_params.get('period_hours', 24))
    task_name = request.query_params.get('task_name')

    time_threshold = timezone.now() - timedelta(hours=period_hours)

    queryset = TaskLog.objects.filter(created_at__gte=time_threshold)
    if task_name:
        queryset = queryset.filter(task_name=task_name)

    total = queryset.count()
    successful = queryset.filter(is_successful=True).count()
    failed = queryset.filter(is_failed=True).count()
    in_progress = queryset.filter(
        Q(status='in_progress') | Q(status='queued')
    ).count()

    completed = successful + failed
    success_rate = (successful / completed * 100) if completed > 0 else 0.0

    avg_duration = queryset.filter(
        duration_ms__isnull=False
    ).aggregate(avg=Avg('duration_ms'))['avg'] or 0

    return Response({
        'total': total,
        'successful': successful,
        'failed': failed,
        'in_progress': in_progress,
        'success_rate': round(success_rate, 2),
        'avg_duration_ms': int(avg_duration),
        'avg_duration_seconds': round(avg_duration / 1000, 2),
        'period_hours': period_hours,
    })
```

### Custom Analytics Queries

**Success Rate by Task**:

```python
from django.db.models import Count, Q, F, FloatField
from django.db.models.functions import Cast

success_rates = TaskLog.objects.values('task_name').annotate(
    total=Count('id'),
    successful=Count('id', filter=Q(is_successful=True)),
    failed=Count('id', filter=Q(is_failed=True))
).annotate(
    success_rate=Cast('successful', FloatField()) / Cast('total', FloatField()) * 100
).order_by('-total')
```

**Tasks by Queue**:

```python
queue_stats = TaskLog.objects.values('queue_name').annotate(
    total=Count('id'),
    successful=Count('id', filter=Q(is_successful=True)),
    failed=Count('id', filter=Q(is_failed=True)),
    avg_duration=Avg('duration_ms')
).order_by('-total')
```

**Hourly Execution Counts**:

```python
from django.db.models.functions import TruncHour

hourly_stats = TaskLog.objects.filter(
    created_at__gte=timezone.now() - timedelta(hours=24)
).annotate(
    hour=TruncHour('created_at')
).values('hour').annotate(
    total=Count('id'),
    successful=Count('id', filter=Q(is_successful=True)),
    failed=Count('id', filter=Q(is_failed=True))
).order_by('hour')
```

**Retry Analysis**:

```python
retry_stats = TaskLog.objects.filter(
    job_retries__gt=0
).values('task_name').annotate(
    total_retried=Count('id'),
    avg_retries=Avg('job_retries'),
    max_retries=Max('job_retries')
).order_by('-total_retried')
```

---

## Health Checks

### Task Queue Health Check

Monitor the health of your task queue:

```python
from django.utils import timezone
from datetime import timedelta
from django_cfg.apps.tasks.models import TaskLog

def check_task_queue_health():
    """
    Check task queue health.

    Returns:
        dict: Health check results
    """
    now = timezone.now()
    last_hour = now - timedelta(hours=1)

    # Check for tasks stuck in progress
    stuck_tasks = TaskLog.objects.filter(
        status='in_progress',
        start_time__lt=now - timedelta(hours=1)
    ).count()

    # Check failure rate
    recent_tasks = TaskLog.objects.filter(created_at__gte=last_hour)
    total = recent_tasks.count()
    failed = recent_tasks.filter(is_failed=True).count()
    failure_rate = (failed / total * 100) if total > 0 else 0

    # Check queue backlog
    queued = TaskLog.objects.filter(status='queued').count()

    # Determine health status
    is_healthy = (
        stuck_tasks < 5 and
        failure_rate < 10 and
        queued < 100
    )

    return {
        'healthy': is_healthy,
        'stuck_tasks': stuck_tasks,
        'failure_rate': round(failure_rate, 2),
        'queued_tasks': queued,
        'total_last_hour': total,
        'failed_last_hour': failed,
        'timestamp': now.isoformat()
    }
```

### Django Health Check Integration

If using `django-health-check`:

```python
# apps/tasks/health.py
from health_check.backends import BaseHealthCheckBackend
from health_check.exceptions import ServiceUnavailable
from django.utils import timezone
from datetime import timedelta
from .models import TaskLog

class TaskQueueHealthCheck(BaseHealthCheckBackend):
    """Health check for ReArq task queue."""

    critical_service = True

    def check_status(self):
        """Check task queue status."""
        now = timezone.now()

        # Check for stuck tasks
        stuck_count = TaskLog.objects.filter(
            status='in_progress',
            start_time__lt=now - timedelta(hours=2)
        ).count()

        if stuck_count > 10:
            self.add_error(
                ServiceUnavailable(
                    f"Too many stuck tasks: {stuck_count}"
                )
            )

        # Check failure rate
        recent = TaskLog.objects.filter(
            created_at__gte=now - timedelta(hours=1)
        )
        total = recent.count()

        if total > 0:
            failed = recent.filter(is_failed=True).count()
            failure_rate = (failed / total * 100)

            if failure_rate > 20:
                self.add_error(
                    ServiceUnavailable(
                        f"High failure rate: {failure_rate:.1f}%"
                    )
                )

    def identifier(self):
        return "ReArq Task Queue"
```

Register in settings:

```python
# settings.py
HEALTH_CHECKS = {
    'BACKENDS': [
        'django_cfg.apps.tasks.health.TaskQueueHealthCheck',
    ]
}
```

---

## Alerting

### Alerting Strategy

Set up alerts for critical conditions:

1. **High Failure Rate**: > 10% in last hour
2. **Stuck Tasks**: Tasks in progress > 1 hour
3. **Queue Backlog**: > 100 queued tasks
4. **Slow Tasks**: Average duration > 30 seconds
5. **Retry Storms**: > 5 retries on average

### Example Alert Functions

```python
from django.core.mail import send_mail
from django.conf import settings

def check_and_alert_high_failure_rate(threshold=10):
    """Alert if failure rate exceeds threshold."""
    from django.utils import timezone
    from datetime import timedelta

    now = timezone.now()
    last_hour = now - timedelta(hours=1)

    recent = TaskLog.objects.filter(created_at__gte=last_hour)
    total = recent.count()

    if total < 10:  # Not enough data
        return

    failed = recent.filter(is_failed=True).count()
    failure_rate = (failed / total * 100)

    if failure_rate > threshold:
        send_mail(
            subject=f'[ALERT] High Task Failure Rate: {failure_rate:.1f}%',
            message=f'''
Task queue has high failure rate:
- Failure Rate: {failure_rate:.1f}%
- Failed Tasks: {failed}
- Total Tasks: {total}
- Time Period: Last hour
            ''',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=settings.ADMINS_EMAILS,
        )

def check_and_alert_stuck_tasks(max_hours=2):
    """Alert if tasks are stuck in progress."""
    from django.utils import timezone
    from datetime import timedelta

    threshold = timezone.now() - timedelta(hours=max_hours)

    stuck = TaskLog.objects.filter(
        status='in_progress',
        start_time__lt=threshold
    )

    count = stuck.count()

    if count > 5:
        task_list = '\n'.join([
            f"- {t.task_name} (job_id={t.job_id}, started={t.start_time})"
            for t in stuck[:10]
        ])

        send_mail(
            subject=f'[ALERT] {count} Stuck Tasks Detected',
            message=f'''
Tasks have been in progress for > {max_hours} hours:
- Count: {count}
- Top Tasks:
{task_list}
            ''',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=settings.ADMINS_EMAILS,
        )
```

### Scheduled Alert Check

Use Django management command or cron task:

```python
# management/commands/check_task_alerts.py
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = 'Check task queue health and send alerts'

    def handle(self, *args, **options):
        from django_cfg.apps.tasks.alerts import (
            check_and_alert_high_failure_rate,
            check_and_alert_stuck_tasks
        )

        self.stdout.write('Checking task queue health...')

        check_and_alert_high_failure_rate(threshold=10)
        check_and_alert_stuck_tasks(max_hours=2)

        self.stdout.write(self.style.SUCCESS('Health checks complete'))
```

Schedule with cron:

```bash
# Run every 15 minutes
*/15 * * * * cd /app && python manage.py check_task_alerts
```

Or use ReArq cron task:

```python
from django_cfg.apps.tasks import get_rearq_client

client = get_rearq_client()

@client.cron_task(cron="*/15 * * * *")  # Every 15 minutes
async def check_alerts():
    """Check task queue health and send alerts."""
    from django.core.management import call_command
    from asgiref.sync import sync_to_async

    await sync_to_async(call_command)('check_task_alerts')
```

---

## Best Practices

### 1. TaskLog Creation

**Create TaskLog entries for all tasks**:

```python
from django_cfg.apps.tasks import get_rearq_client
from django_cfg.apps.tasks.models import TaskLog

client = get_rearq_client()

@client.task(queue="default")
async def my_task(data_id: str):
    """Example task with logging."""
    # Task logic here
    return {"status": "success"}

# When enqueuing
async def enqueue_task_with_log(data_id: str, user=None):
    """Enqueue task and create log entry."""
    job = await my_task.delay(data_id)

    # Create TaskLog entry
    from asgiref.sync import sync_to_async
    await sync_to_async(TaskLog.objects.create)(
        job_id=job.job_id,
        task_name='my_task',
        queue_name='default',
        status='queued',
        args=[data_id],
        kwargs={},
        enqueue_time=timezone.now(),
        user=user
    )

    return job
```

### 2. Monitoring Critical Tasks

**Set up alerts for critical tasks**:

```python
def monitor_critical_task(task_name: str):
    """Monitor critical task execution."""
    recent = TaskLog.objects.filter(
        task_name=task_name,
        created_at__gte=timezone.now() - timedelta(hours=1)
    )

    total = recent.count()
    failed = recent.filter(is_failed=True).count()

    if total > 0:
        failure_rate = (failed / total * 100)
        if failure_rate > 5:  # Alert at 5% for critical tasks
            send_alert(
                f"Critical task {task_name} has {failure_rate:.1f}% failure rate"
            )
```

### 3. Performance Optimization

**Add indexes for common queries**:

```python
class TaskLog(models.Model):
    class Meta:
        indexes = [
            models.Index(fields=["task_name", "-enqueue_time"]),
            models.Index(fields=["status", "-enqueue_time"]),
            models.Index(fields=["queue_name", "status"]),
            models.Index(fields=["success", "-enqueue_time"]),
            models.Index(fields=["-created_at"]),
        ]
```

**Use select_related for user queries**:

```python
# Optimize user queries
tasks = TaskLog.objects.select_related('user').filter(
    task_name='my_task'
)
```

### 4. Data Retention

**Implement cleanup for old logs**:

```python
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta

class Command(BaseCommand):
    help = 'Clean up old task logs'

    def add_arguments(self, parser):
        parser.add_argument(
            '--days',
            type=int,
            default=90,
            help='Keep logs newer than N days'
        )

    def handle(self, *args, **options):
        days = options['days']
        threshold = timezone.now() - timedelta(days=days)

        deleted = TaskLog.objects.filter(
            created_at__lt=threshold
        ).delete()

        self.stdout.write(
            self.style.SUCCESS(
                f'Deleted {deleted[0]} logs older than {days} days'
            )
        )
```

Schedule cleanup:

```bash
# Daily at 2 AM
0 2 * * * cd /app && python manage.py cleanup_task_logs --days=90
```

### 5. Logging Standards

**Use consistent task naming**:

```python
# Good: Clear, hierarchical names
@client.task(queue="default")
async def users_process_signup():
    pass

@client.task(queue="default")
async def users_send_welcome_email():
    pass

# Bad: Unclear names
@client.task(queue="default")
async def task1():
    pass
```

**Log meaningful errors**:

```python
@client.task(queue="default")
async def process_data(data_id: str):
    try:
        # Process data
        result = await do_processing(data_id)
        return result
    except ValueError as e:
        # Log specific error
        raise ValueError(f"Invalid data format for {data_id}: {str(e)}")
    except Exception as e:
        # Log with context
        raise Exception(f"Failed to process {data_id}: {str(e)}")
```

### 6. Dashboard Integration

**Create custom monitoring dashboard**:

```python
# views.py
from rest_framework.views import APIView
from rest_framework.response import Response

class TaskMonitoringDashboard(APIView):
    """Custom monitoring dashboard."""

    def get(self, request):
        """Get dashboard data."""
        from django_cfg.apps.tasks.models import TaskLog
        from django.db.models import Count, Avg, Q

        # Last 24 hours
        time_threshold = timezone.now() - timedelta(hours=24)
        recent = TaskLog.objects.filter(created_at__gte=time_threshold)

        # Overall stats
        total = recent.count()
        successful = recent.filter(is_successful=True).count()
        failed = recent.filter(is_failed=True).count()
        in_progress = recent.filter(status='in_progress').count()

        # By task
        by_task = recent.values('task_name').annotate(
            total=Count('id'),
            successful=Count('id', filter=Q(is_successful=True)),
            failed=Count('id', filter=Q(is_failed=True)),
            avg_duration=Avg('duration_ms')
        ).order_by('-total')[:10]

        # By queue
        by_queue = recent.values('queue_name').annotate(
            total=Count('id'),
            successful=Count('id', filter=Q(is_successful=True)),
            failed=Count('id', filter=Q(is_failed=True))
        ).order_by('-total')

        return Response({
            'overview': {
                'total': total,
                'successful': successful,
                'failed': failed,
                'in_progress': in_progress,
                'success_rate': (successful / total * 100) if total > 0 else 0
            },
            'by_task': list(by_task),
            'by_queue': list(by_queue)
        })
```

### 7. Testing Monitoring

**Test monitoring functionality**:

```python
# tests/test_monitoring.py
from django.test import TestCase
from django.utils import timezone
from django_cfg.apps.tasks.models import TaskLog

class MonitoringTestCase(TestCase):
    def test_task_log_creation(self):
        """Test TaskLog creation."""
        log = TaskLog.objects.create(
            job_id='test-job-id',
            task_name='test_task',
            queue_name='default',
            status='queued',
            enqueue_time=timezone.now()
        )
        self.assertEqual(log.status, 'queued')

    def test_task_completion(self):
        """Test task completion tracking."""
        log = TaskLog.objects.create(
            job_id='test-job-id',
            task_name='test_task',
            queue_name='default',
            status='queued',
            enqueue_time=timezone.now()
        )

        # Mark as started
        log.mark_started(worker_id='worker-1')
        self.assertEqual(log.status, 'in_progress')

        # Mark as completed
        log.mark_completed(result='{"status": "ok"}')
        self.assertEqual(log.status, 'success')
        self.assertTrue(log.is_successful)
        self.assertIsNotNone(log.duration_ms)

    def test_failure_tracking(self):
        """Test failure tracking."""
        log = TaskLog.objects.create(
            job_id='test-job-id',
            task_name='test_task',
            queue_name='default',
            status='queued',
            enqueue_time=timezone.now()
        )

        log.mark_started(worker_id='worker-1')
        log.mark_failed(error_message='Test error')

        self.assertEqual(log.status, 'failed')
        self.assertTrue(log.is_failed)
        self.assertEqual(log.error_message, 'Test error')
```

### 8. Documentation

**Document your tasks**:

```python
@client.task(queue="default", job_retry=3)
async def process_user_data(user_id: int, options: dict = None):
    """
    Process user data asynchronously.

    Args:
        user_id: ID of the user to process
        options: Optional processing options
            - full_refresh (bool): Force full data refresh
            - notify (bool): Send notification on completion

    Returns:
        dict: Processing result with status and summary

    Raises:
        ValueError: If user_id is invalid
        ProcessingError: If data processing fails

    Retry Policy:
        - Max retries: 3
        - Retry after: 60 seconds
        - Queue: default

    Monitoring:
        - Check TaskLog for execution history
        - Alert if failure rate > 5%
        - Typical duration: 2-5 seconds
    """
    # Implementation
    pass
```

---

## Summary

Django-CFG provides comprehensive monitoring for ReArq tasks through:

1. **TaskLog Model**: Persistent storage of task execution history
2. **REST API**: Programmatic access with 30+ filter options
3. **Django Admin**: Rich web interface with badges and analytics
4. **ReArq Server**: Real-time operational monitoring
5. **Statistics**: Built-in analytics and reporting
6. **Health Checks**: Queue health monitoring
7. **Alerting**: Proactive error detection
8. **Best Practices**: Guidelines for effective monitoring

### Quick Reference

| Need | Solution |
|------|----------|
| View task history | Django Admin: `/admin/tasks/tasklog/` |
| Query tasks programmatically | REST API: `/cfg/tasks/logs/` |
| Real-time job status | ReArq Server: `http://localhost:7380/` |
| Get statistics | API: `/cfg/tasks/logs/stats/` |
| Monitor failures | API: `/cfg/tasks/logs/?is_failed=true` |
| Check performance | API: `/cfg/tasks/logs/?ordering=-duration_ms` |
| Set up alerts | Implement custom alert functions |
| View errors | Admin: Filter by "Failed" status |

### Next Steps

1. Set up TaskLog creation for your tasks
2. Configure Django Admin filters for your use case
3. Implement health checks and alerts
4. Create custom dashboards as needed
5. Document your monitoring strategy

For more information, see:
- [Configuration Guide](./configuration)
- [Deployment Guide](./deployment)
- [Usage Examples](./examples)

---

## See Also

### Monitoring & Observability
- **[Admin Customization](/features/modules/unfold/overview)** - Customize monitoring interface
- **[Production Deployment](/guides/production-config)** - Production monitoring setup

### Operations
- **[Operations App](/features/built-in-apps/operations/overview)** - System monitoring and management

### Integration
- **[Centrifugo](/features/integrations/centrifugo/)** - Real-time task updates
- **[Docker Monitoring](/guides/docker/production)** - Container monitoring
