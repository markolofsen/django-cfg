# Django-RQ Production Deployment Guide

## Overview

Django-RQ is configured for production deployment with:
- **Worker**: Background task processor
- **Scheduler**: Cron-like scheduled tasks
- **Dashboard**: Integrated web UI in Django Admin (Next.js)
- **Storage**: Shared Redis for task queue

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Traefik (Dokploy)                    │
│            https://api.djangocfg.com                    │
└────────────────────┬────────────────────────────────────┘
                     │
         ┌───────────┴───────────┐
         │                       │
    ┌────▼─────┐         ┌──────▼──────┐
    │  Django  │         │   Django    │
    │   API    │         │   Admin     │
    │          │         │  (Next.js)  │
    └────┬─────┘         └──────┬──────┘
         │                      │
         │      RQ Dashboard ───┘
         │      /cfg/admin/ → RQ tab
         │
    ┌────┴──────────────────────┴───┐
    │                                │
┌───▼────────┐              ┌───────▼──────┐
│ RQ Worker  │              │ RQ Scheduler │
│  (Tasks)   │              │   (Cron)     │
└────┬───────┘              └───────┬──────┘
     │                              │
     │      ┌───────────────────────┘
     │      │
┌────▼──────▼───┐
│  Shared Redis │
│  (DB: 0)      │
└───────────────┘
```

## Services

### 1. RQ Worker
Processes background tasks from queues: `default`, `high`, `low`, `knowledge`

### 2. RQ Scheduler
Runs scheduled tasks (configured in `config.py` via `RQScheduleConfig`)

### 3. RQ Dashboard
Integrated into Django Admin Next.js UI at `/cfg/admin/` → RQ tab
- Real-time monitoring
- Queue statistics
- Worker status
- Job management
- Testing interface

## Deployment

### Production Deployment

```bash
cd /path/to/django-cfg/solution/docker

# Build Django image (used for worker and scheduler)
docker compose -f docker-compose-production.yaml build django

# Start all services including RQ
docker compose -f docker-compose-production.yaml up -d

# Check status
docker compose -f docker-compose-production.yaml ps
```

### Local Development

**Option 1: Run RQ workers in Docker**

```bash
# Start separate services (Redis + RQ + Centrifugo)
docker compose -f docker-compose-local-services.yml up -d

# Check logs
docker logs djangocfg_rq_worker -f
docker logs djangocfg_rq_scheduler -f
```

**Option 2: Run RQ workers from Django project**

```bash
# Terminal 1: Start Django server
cd projects/django
poetry run python manage.py runserver

# Terminal 2: Start RQ worker
poetry run python manage.py rqworker default high low knowledge

# Terminal 3: Start RQ scheduler (optional, if you have scheduled tasks)
poetry run python manage.py rqscheduler
```

## Configuration

### Environment Variables

RQ uses `REDIS_URL` from Django settings (auto-configured by django-cfg):

```bash
# In .env.prod or .env.local
REDIS_URL=redis://shared-db-redis:6379/0
```

### Queue Configuration

Queues are configured in `api/config.py`:

```python
from django_cfg import DjangoRQConfig, RQQueueConfig

django_rq: Optional[DjangoRQConfig] = DjangoRQConfig(
    enabled=True,
    queues=[
        RQQueueConfig(
            queue="default",
            default_timeout=360,
            default_result_ttl=500,
        ),
        RQQueueConfig(
            queue="high",
            default_timeout=180,
            default_result_ttl=300,
        ),
        RQQueueConfig(
            queue="low",
            default_timeout=600,
            default_result_ttl=800,
        ),
        RQQueueConfig(
            queue="knowledge",
            default_timeout=600,
            default_result_ttl=3600,
        ),
    ],
    show_admin_link=True,
    prometheus_enabled=True,
)
```

### Scheduled Tasks

Configure scheduled tasks in `api/config.py`:

```python
from django_cfg import RQScheduleConfig

django_rq: Optional[DjangoRQConfig] = DjangoRQConfig(
    enabled=True,
    queues=[...],
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
        # Generate daily report
        RQScheduleConfig(
            func="apps.crypto.tasks.generate_report",
            interval=86400,  # 24 hours
            queue="low",
            report_type="daily",
            description="Generate daily crypto market report",
        ),
    ],
)
```

### Resource Limits

**Worker**:
- CPU: 1.0 core
- Memory: 1GB (256MB reserved)

**Scheduler**:
- CPU: 0.5 core
- Memory: 512MB (128MB reserved)

## Monitoring

### Access RQ Dashboard

**URL**: https://api.djangocfg.com/cfg/admin/ → RQ tab

**Features**:
- System health status
- Queue statistics (jobs count, failed, finished)
- Worker monitoring
- Real-time job tracking
- Job registries (queued, started, finished, failed, deferred, scheduled)
- Testing interface (run demo tasks, stress tests, cleanup)

### Check Logs

```bash
# Worker logs
docker logs django-cfg-rq-worker -f

# Scheduler logs
docker logs django-cfg-rq-scheduler -f

# Django API logs
docker logs django-cfg-django -f
```

### Health Checks

```bash
# Check worker is running
docker exec django-cfg-rq-worker pgrep -f rqworker

# Check scheduler is running
docker exec django-cfg-rq-scheduler pgrep -f rqscheduler

# Check Redis connection
docker exec django-cfg-rq-worker redis-cli -h shared-db-redis ping
```

### Queue Inspection (CLI)

```bash
# Enter Django container
docker exec -it django-cfg-django bash

# List all queues
python manage.py rqstats

# Show queue details
python manage.py rqstats --interval 5

# Empty a queue
python manage.py rqempty default

# Flush failed jobs
python manage.py rqenqueue --queue failed --empty
```

## Task Queues

RQ processes tasks from 4 queues:

1. **high**: High-priority tasks (e.g., payment processing)
2. **default**: Standard tasks (e.g., email sending, price updates)
3. **low**: Background tasks (e.g., cleanup, daily reports)
4. **knowledge**: Knowledge base processing tasks

**Priority**: Workers process `high` → `default` → `low` → `knowledge` in order.

## Scaling

### Scale Workers Horizontally

```bash
# Scale to 3 workers
docker compose -f docker-compose-production.yaml up -d --scale rq-worker=3

# Check worker status
docker compose -f docker-compose-production.yaml ps rq-worker
```

### Scale Workers Vertically

Edit resource limits in `docker-compose-production.yaml`:

```yaml
rq-worker:
  deploy:
    resources:
      limits:
        cpus: '2.0'      # Increase CPU
        memory: 2G       # Increase memory
      reservations:
        memory: 512M
```

Then restart:

```bash
docker compose -f docker-compose-production.yaml up -d rq-worker
```

### Queue-Specific Workers

Run separate workers for specific queues:

```bash
# High-priority only worker
docker run -d \
  --name rq-worker-high \
  --env-file .env.prod \
  django-cfg-django:latest \
  poetry run python manage.py rqworker high

# Low-priority only worker
docker run -d \
  --name rq-worker-low \
  --env-file .env.prod \
  django-cfg-django:latest \
  poetry run python manage.py rqworker low
```

## Troubleshooting

### Worker Not Processing Tasks

1. **Check Redis connection**:
   ```bash
   docker exec django-cfg-rq-worker redis-cli -h shared-db-redis ping
   # Expected: PONG
   ```

2. **Check worker is running**:
   ```bash
   docker exec django-cfg-rq-worker pgrep -f rqworker
   # Should return a process ID
   ```

3. **Check worker logs**:
   ```bash
   docker logs django-cfg-rq-worker --tail 100
   ```

4. **Verify queues are registered**:
   ```bash
   docker exec django-cfg-django python manage.py rqstats
   ```

### Scheduler Not Running Scheduled Tasks

1. **Check scheduler is running**:
   ```bash
   docker exec django-cfg-rq-scheduler pgrep -f rqscheduler
   ```

2. **Check scheduler logs**:
   ```bash
   docker logs django-cfg-rq-scheduler --tail 100
   ```

3. **Verify scheduled jobs are registered**:
   ```bash
   docker exec django-cfg-django python manage.py shell
   >>> from django_rq import get_scheduler
   >>> scheduler = get_scheduler('default')
   >>> scheduler.get_jobs()
   ```

### Tasks Failing Silently

1. **Check failed job registry**:
   - Go to RQ Dashboard → Registries tab → Failed
   - Click on failed jobs to see error details

2. **Re-enqueue failed jobs**:
   ```bash
   docker exec django-cfg-django python manage.py rqenqueue --queue failed
   ```

3. **Clear failed jobs**:
   ```bash
   docker exec django-cfg-django python manage.py rqempty failed
   ```

### Redis Out of Memory

1. **Check Redis memory usage**:
   ```bash
   docker exec shared-db-redis redis-cli info memory
   ```

2. **Clear old results** (via RQ Dashboard):
   - Go to Testing tab → Cleanup section
   - Click "Cleanup Test Jobs"

3. **Adjust Redis max memory** in docker-compose:
   ```yaml
   redis:
     command: >
       redis-server
       --maxmemory 1gb  # Increase from 512mb
       --maxmemory-policy allkeys-lru
   ```

### Dashboard Not Accessible

1. **Check Django is running**:
   ```bash
   docker ps | grep django-cfg-django
   ```

2. **Check admin URL**:
   ```bash
   curl https://api.djangocfg.com/cfg/admin/
   ```

3. **Verify user has admin permissions**:
   - Login to Django admin
   - Check user has staff/superuser status

## Security

### Production Checklist

- ✅ Redis protected (internal network only)
- ✅ RQ Dashboard requires Django admin authentication
- ✅ Worker/Scheduler in private network
- ✅ HTTPS enabled (Traefik + Let's Encrypt)
- ✅ Health checks enabled

### Additional Security (Optional)

**IP Whitelist for Admin**:

```yaml
# In docker-compose-production.yaml
django:
  labels:
    - "traefik.http.routers.djangocfg-api.middlewares=admin-ipwhitelist"
    - "traefik.http.middlewares.admin-ipwhitelist.ipwhitelist.sourcerange=1.2.3.4/32"
```

**Rate Limiting**:

```yaml
django:
  labels:
    - "traefik.http.middlewares.ratelimit.ratelimit.average=100"
    - "traefik.http.middlewares.ratelimit.ratelimit.burst=50"
```

## Backup & Maintenance

### Clear Old Jobs

RQ automatically expires finished jobs based on `result_ttl` setting.

To manually clear old jobs:

```bash
# Via RQ Dashboard: Testing tab → Cleanup
# Or CLI:
docker exec django-cfg-django python manage.py shell
>>> from django_rq import get_connection
>>> conn = get_connection()
>>> conn.flushdb()  # WARNING: Clears all Redis data!
```

### Restart Workers

```bash
# Graceful restart (finishes current jobs)
docker compose -f docker-compose-production.yaml restart rq-worker rq-scheduler

# Force restart (stops immediately)
docker compose -f docker-compose-production.yaml stop rq-worker rq-scheduler
docker compose -f docker-compose-production.yaml up -d rq-worker rq-scheduler
```

### Update Django-RQ

```bash
# Update django-rq package
cd projects/django
poetry update django-rq

# Rebuild Docker image
cd ../../docker
docker compose -f docker-compose-production.yaml build django

# Restart services
docker compose -f docker-compose-production.yaml up -d
```

## Migration from ReArq

If migrating from ReArq:

1. ✅ **Docker services updated** (rearq-worker → rq-worker, rearq-server removed)
2. ✅ **Tasks migrated** to django-rq format
3. ✅ **Schedules configured** in `config.py`
4. ✅ **Dashboard integrated** into Django Admin
5. ⚠️ **Manual cleanup required**: Remove ReArq Dockerfile and configs

```bash
# Remove old ReArq service directory
rm -rf solution/docker/services/rearq

# Remove old documentation
rm -f solution/docker/REARQ_PRODUCTION.md

# Clean up Docker images
docker rmi django-cfg-rearq-worker:latest
docker rmi django-cfg-rearq-server:latest
```

## Performance Tips

1. **Use correct queue**: High-priority tasks → `high`, long-running → `low`
2. **Set appropriate timeouts**: Fast tasks (60s), slow tasks (600s+)
3. **Monitor worker count**: 1 worker per CPU core recommended
4. **Use result_ttl wisely**: Short TTL (300s) for frequent tasks, longer (3600s+) for reports
5. **Enable Prometheus**: `prometheus_enabled=True` for metrics collection

## Support

- **Django-RQ Documentation**: https://github.com/rq/django-rq
- **RQ Documentation**: https://python-rq.org/
- **Django-CFG RQ Integration**: `/projects/django-cfg-dev/src/django_cfg/apps/rq/`
- **Testing Interface**: https://api.djangocfg.com/cfg/admin/ → RQ tab → Testing

## Quick Reference

```bash
# Production
docker compose -f docker-compose-production.yaml up -d
docker logs django-cfg-rq-worker -f

# Local (Docker)
docker compose -f docker-compose-local-services.yml up -d
docker logs djangocfg_rq_worker -f

# Local (Python)
poetry run python manage.py rqworker default high low knowledge
poetry run python manage.py rqscheduler

# Management
python manage.py rqstats           # Show queue statistics
python manage.py rqempty default   # Empty a queue
python manage.py rqenqueue         # Re-enqueue failed jobs
```
