# ReArq Setup Guide

## Quick Start

### 1. Start ReArq Services

```bash
cd solution/docker
docker compose -f docker-compose-local-services.yml up -d
```

### 2. Verify Setup

```bash
# Check logs
docker compose -f docker-compose-local-services.yml logs -f rearq_worker rearq_server

# Open Web UI
open http://localhost:7380
```

## Configuration Verified

✅ ReArq is properly configured with:
- **Redis as the only backend** (no MySQL/PostgreSQL required)
- **redis_url parameter** for ReArq initialization
- **Correct commands** for starting worker and server

## Main ReArq Parameters

```python
rearq = ReArq(
    redis_url="redis://redis:6379/1",  # ✅ Correct parameter
    job_retry=3,
    job_retry_after=60,
    max_jobs=10,
    job_timeout=300,
    keep_job_days=7,
)
```

## Management Commands

### Worker
```bash
rearq main:rearq worker --queue default --queue high_priority
```

### Server (Web UI)
```bash
rearq main:rearq server --host 0.0.0.0 --port 8080
```

### Timer (Cron tasks)
```bash
rearq main:rearq timer
```

## Endpoints

- **Web UI**: http://localhost:7380
- **API Docs**: http://localhost:7380/docs
- **OpenAPI JSON**: http://localhost:7380/openapi.json

## Environment Variables

```bash
REARQ_REDIS_HOST=redis
REARQ_REDIS_PORT=6379
REARQ_REDIS_DB=1
```

## Differences from Previous Dramatiq Version

| Aspect | Dramatiq | ReArq |
|--------|----------|-------|
| Backend | Redis + RabbitMQ | Redis only |
| Web UI | None (requires arq-ui) | Built-in |
| Database | Not required | Not required |
| Async support | Limited | Full asyncio |
| Cron tasks | Via APScheduler | Built-in |
| API | None | REST API + OpenAPI |

## Verification

```bash
# 1. Check Redis
docker compose -f docker-compose-local-services.yml exec redis redis-cli -n 1 PING

# 2. Check worker
docker compose -f docker-compose-local-services.yml logs rearq_worker | grep "Worker started"

# 3. Check Web UI
curl http://localhost:7380/ | grep "rearq"
```

## Troubleshooting

### Issue: Worker doesn't start

**Solution**: Check that Redis is accessible
```bash
docker compose -f docker-compose-local-services.yml exec rearq_worker nc -zv redis 6379
```

### Issue: Web UI doesn't open

**Solution**: Check server logs
```bash
docker compose -f docker-compose-local-services.yml logs rearq_server
```

### Issue: Tasks not processing

**Solution**: Check queues in Redis
```bash
docker compose -f docker-compose-local-services.yml exec redis redis-cli -n 1
> KEYS arq:queue:*
> LLEN arq:queue:default
```

## Full Documentation

See [README.md](./README.md) for detailed documentation.
