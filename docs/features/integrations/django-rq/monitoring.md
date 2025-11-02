---
title: Django-RQ Monitoring
description: Complete guide to monitoring Django-RQ jobs, queues, and workers in django-cfg
sidebar_position: 5
tags:
  - monitoring
  - django-rq
  - observability
  - prometheus
  - rest-api
---

# Django-RQ Monitoring

Comprehensive monitoring and management guide for Django-RQ in django-cfg, including Django Admin, REST API, Prometheus metrics, and CLI tools.

---

## Monitoring Overview

Django-cfg provides multiple ways to monitor Django-RQ:

| Method | Use Case | Real-time | Production |
|--------|----------|-----------|------------|
| **Django Admin** | Manual monitoring and management | ✅ Yes | ✅ Yes |
| **REST API** | Programmatic access, dashboards | ✅ Yes | ✅ Yes |
| **Prometheus** | Metrics and alerting | ✅ Yes | ✅ Yes |
| **CLI Commands** | Quick checks, debugging | ✅ Yes | ⚠️ Limited |
| **Web Dashboard** | Visual monitoring (django-rq) | ✅ Yes | ✅ Yes |

---

## Django Admin Interface

### Access

Navigate to `/admin/django_rq/` in your Django admin:

```
http://localhost:8000/admin/django_rq/
```

### Features

**Queue Management:**
- View all queues and their job counts
- See queue statistics (queued, started, finished, failed)
- Empty queues
- Clear finished/failed jobs

**Job Management:**
- Browse all jobs with filtering
- View job details (status, args, result, error)
- Cancel running jobs
- Requeue failed jobs
- Delete jobs

**Worker Monitoring:**
- See active workers
- Check worker status and health
- View worker statistics

### Configuration

Enable admin link in config:

```python
django_rq: DjangoRQConfig = DjangoRQConfig(
    enabled=True,
    show_admin_link=True,  # Show link in admin
)
```

---

## REST API

### Endpoints

Django-cfg provides comprehensive REST API for monitoring:

```
GET  /api/cfg/rq/monitor/          - Health check and system info
GET  /api/cfg/rq/monitor/health/   - System health status
GET  /api/cfg/rq/monitor/config/   - RQ configuration

GET  /api/cfg/rq/queues/            - List all queues
GET  /api/cfg/rq/queues/{name}/     - Queue details
POST /api/cfg/rq/queues/{name}/empty/ - Empty queue

GET  /api/cfg/rq/workers/           - List all workers
GET  /api/cfg/rq/workers/{name}/    - Worker details

GET  /api/cfg/rq/jobs/              - List all jobs
GET  /api/cfg/rq/jobs/{id}/         - Job details
POST /api/cfg/rq/jobs/{id}/cancel/  - Cancel job
POST /api/cfg/rq/jobs/{id}/requeue/ - Requeue job
DELETE /api/cfg/rq/jobs/{id}/       - Delete job

GET  /api/cfg/rq/schedules/         - List scheduled jobs
```

### Examples

**Get System Health:**

```bash
curl http://localhost:8000/api/cfg/rq/monitor/health/
```

Response:
```json
{
  "healthy": true,
  "queues": {
    "default": {"count": 5, "workers": 2},
    "high": {"count": 0, "workers": 1}
  },
  "total_jobs": 5,
  "total_workers": 3
}
```

**List Queues:**

```bash
curl http://localhost:8000/api/cfg/rq/queues/
```

Response:
```json
[
  {
    "name": "default",
    "count": 5,
    "queued_jobs": 5,
    "started_jobs": 0,
    "finished_jobs": 42,
    "failed_jobs": 3,
    "workers": 2
  }
]
```

**Get Job Details:**

```bash
curl http://localhost:8000/api/cfg/rq/jobs/{job-id}/
```

Response:
```json
{
  "id": "abc123",
  "func_name": "apps.crypto.tasks.update_coin_prices",
  "status": "finished",
  "queue": "default",
  "created_at": "2025-01-15T10:30:00Z",
  "started_at": "2025-01-15T10:30:05Z",
  "ended_at": "2025-01-15T10:30:15Z",
  "result": {"success": true, "updated": 50},
  "args": [],
  "kwargs": {"limit": 50, "verbosity": 1}
}
```

**Cancel Job:**

```bash
curl -X POST http://localhost:8000/api/cfg/rq/jobs/{job-id}/cancel/
```

---

## Prometheus Metrics

### Enable Metrics

```python
django_rq: DjangoRQConfig = DjangoRQConfig(
    enabled=True,
    prometheus_enabled=True,
)
```

### Access Metrics

```
http://localhost:8000/django-rq/metrics/
```

### Available Metrics

```prometheus
# Job counts by queue and status
rq_jobs_total{queue="default",status="finished"} 12450
rq_jobs_total{queue="default",status="failed"} 125

# Current queue length
rq_queue_length{queue="default"} 42

# Worker counts
rq_workers_total{queue="default"} 2

# Job duration
rq_job_duration_seconds{queue="default"} 1.5
```

### Prometheus Configuration

```yaml
# prometheus.yml
scrape_configs:
  - job_name: 'django-rq'
    static_configs:
      - targets: ['localhost:8000']
    metrics_path: '/django-rq/metrics/'
```

### Grafana Dashboard

Example queries for Grafana:

```promql
# Jobs per minute
rate(rq_jobs_total[1m])

# Failed jobs percentage
rate(rq_jobs_total{status="failed"}[5m]) / rate(rq_jobs_total[5m]) * 100

# Queue depth
rq_queue_length

# Average job duration
rate(rq_job_duration_seconds_sum[5m]) / rate(rq_job_duration_seconds_count[5m])
```

---

## CLI Commands

### rqstats

View queue statistics:

```bash
# Basic stats
python manage.py rqstats

# Real-time monitoring (refresh every 1 second)
python manage.py rqstats --interval 1

# Specific queue
python manage.py rqstats --queue default
```

Output:
```
default       |██████████████████              |  42  0  0
high          |█                                |   1  0  0
low           |                                 |   0  0  0

queued: 43 workers: 3
```

### Worker Management

```bash
# Start single worker
python manage.py rqworker default

# Start worker pool (4 workers)
python manage.py rqworker-pool default --num-workers 4

# Start worker for multiple queues (priority)
python manage.py rqworker high default low

# Start with verbose logging
python manage.py rqworker default --verbose
```

### Scheduler Management

```bash
# Start scheduler
python manage.py rqscheduler

# Scheduler with verbose logging
python manage.py rqscheduler --verbose
```

---

## Web Dashboard

Django-RQ includes built-in web dashboard:

```
http://localhost:8000/django-rq/
```

### Features

- **Queues Overview**: See all queues at a glance
- **Job Browser**: Browse and filter jobs
- **Worker Status**: Monitor active workers
- **Statistics**: Charts and graphs
- **Actions**: Cancel, requeue, delete jobs

---

## Monitoring Best Practices

### 1. Set Up Alerting

```python
# Monitor queue depth
if queue.count > 1000:
    send_alert("Queue depth too high")

# Monitor failed jobs
failed_rate = failed_jobs / total_jobs
if failed_rate > 0.1:  # 10%
    send_alert("High failure rate")

# Monitor worker health
if active_workers == 0:
    send_alert("No active workers")
```

### 2. Track Key Metrics

- **Queue depth**: Number of pending jobs
- **Processing rate**: Jobs per second
- **Failure rate**: Failed jobs percentage
- **Average duration**: Job execution time
- **Worker count**: Active workers

### 3. Monitor Redis Health

```bash
# Check Redis memory usage
redis-cli info memory

# Check Redis keyspace
redis-cli info keyspace

# Monitor Redis connections
redis-cli info clients
```

### 4. Use Logging

```python
import logging

logger = logging.getLogger('rq.jobs')

def my_task():
    logger.info("Task started")
    # ...
    logger.info("Task completed")
```

### 5. Implement Health Checks

```python
def health_check_task():
    """Periodic health check task."""
    import django_rq

    # Check queues
    for queue_name in ['default', 'high', 'low']:
        queue = django_rq.get_queue(queue_name)

        # Check queue depth
        if queue.count > 1000:
            logger.warning(f"Queue {queue_name} depth: {queue.count}")

        # Check failed jobs
        failed_count = len(queue.failed_job_registry)
        if failed_count > 100:
            logger.warning(f"Queue {queue_name} failed jobs: {failed_count}")

    # Check workers
    workers = django_rq.get_workers()
    if len(workers) == 0:
        logger.error("No active workers!")

    return {"healthy": True, "queues": len(queues), "workers": len(workers)}

# Schedule health check
RQScheduleConfig(
    func="apps.monitoring.tasks.health_check_task",
    interval=60,  # Every minute
    queue="high",
)
```

---

## Troubleshooting

### Issue: Jobs Not Processing

**Check:**
1. Are workers running? `ps aux | grep rqworker`
2. Is Redis running? `redis-cli ping`
3. Check worker logs
4. Check queue: `python manage.py rqstats`

**Solution:**
```bash
# Start workers
python manage.py rqworker default
```

### Issue: High Memory Usage

**Check:**
1. Redis memory: `redis-cli info memory`
2. Worker memory: `ps aux | grep rqworker`

**Solution:**
```python
# Set result TTL to expire old results
RQQueueConfig(
    queue="default",
    default_result_ttl=500,  # 8 minutes
)
```

### Issue: Failed Jobs Accumulating

**Check:**
```bash
# View failed jobs
curl http://localhost:8000/api/cfg/rq/jobs/?status=failed
```

**Solution:**
```bash
# Requeue all failed jobs
curl -X POST http://localhost:8000/api/cfg/rq/jobs/registries/failed/requeue-all/?queue=default

# Or clear failed jobs
curl -X POST http://localhost:8000/api/cfg/rq/jobs/registries/failed/clear/?queue=default
```

---

## See Also

### Documentation
- [Overview](./overview) - Introduction
- [Configuration](./configuration) - Setup
- [Examples](./examples) - Code examples
- [Architecture](./architecture) - Design

### Tools
- [Django-RQ Dashboard](https://github.com/rq/django-rq) - Built-in dashboard
- [RQ Dashboard](https://github.com/Parallels/rq-dashboard) - Standalone dashboard
- [Prometheus](https://prometheus.io/) - Metrics platform
- [Grafana](https://grafana.com/) - Visualization
