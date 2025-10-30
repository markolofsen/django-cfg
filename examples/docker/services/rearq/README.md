# ReArq - Async Task Queue for Django-CFG

ReArq is a production-ready async task queue with full-featured Web UI, REST API, and monitoring. Based on ARQ with extended functionality.

## 📋 Features

- **Web UI & REST API** — complete monitoring and task management through browser
- **Task History** — result storage in Redis
- **Cron Tasks** — built-in scheduler for periodic tasks
- **Multiple Queues** — task prioritization (high/default/low priority)
- **OpenAPI Documentation** — automatic API documentation
- **Distributed Locks** — coordination between workers
- **Async/await** — native asyncio support
- **Lightweight** — no separate database required, only Redis

## 🚀 Quick Start

### Local Development

```bash
cd solution/docker

# Quick start with Makefile
make services

# Access Web UI
open http://localhost:7380/

# Stop services
make services-down
```

### Production Deployment

```bash
cd solution/docker

# Build and start ReArq
make prod-rearq

# Access Web UI (with SSL)
open https://tasks.djangocfg.com

# View logs
make prod-rearq-logs

# Restart services
make prod-rearq-restart
```

**📖 Full production guide**: See `/solution/docker/REARQ_PRODUCTION.md`

### Manual Docker Compose

**Local:**
```bash
# Start services
docker compose -f docker-compose-local-services.yml up -d

# View logs
docker compose -f docker-compose-local-services.yml logs -f

# Stop services
docker compose -f docker-compose-local-services.yml down
```

**Production:**
```bash
# Start services
docker compose -f docker-compose-production.yaml up -d rearq-worker rearq-server

# View logs
docker compose -f docker-compose-production.yaml logs -f rearq-worker rearq-server

# Stop services
docker compose -f docker-compose-production.yaml down
```

### Verify Setup

**Local Web UI:**
```
http://localhost:7380
```

**Production Web UI:**
```
https://tasks.djangocfg.com
```

**API Documentation (Swagger):**
```
http://localhost:7380/docs
https://tasks.djangocfg.com/docs
```

**Health Check:**
```bash
curl http://localhost:7380/
curl https://tasks.djangocfg.com/
```

## 📝 Usage in Code

### Create Task

Add your task in `services/rearq/main.py`:

```python
@rearq.task(queue="default")
async def my_custom_task(user_id: int, action: str) -> dict:
    """
    Your custom task.
    """
    # Your logic here
    return {"status": "success", "user_id": user_id}
```

### Queue Task

```python
# From Django view or other code
await my_custom_task.delay(user_id=123, action="process")
```

### Priority Tasks

```python
# High priority
@rearq.task(queue="high_priority")
async def urgent_task():
    pass

# Normal priority
@rearq.task(queue="default")
async def normal_task():
    pass

# Low priority
@rearq.task(queue="low_priority", timeout=300)
async def slow_task():
    pass
```

### Cron Tasks (Scheduler)

```python
# Run daily at midnight
@rearq.cron(cron="0 0 * * *")
async def daily_report():
    pass

# Run every 5 minutes
@rearq.cron(cron="*/5 * * * *")
async def health_check():
    pass
```

## 🔧 Configuration

### Environment Variables

Main settings in `docker-compose-local-services.yml`:

```yaml
environment:
  REARQ_REDIS_HOST: redis
  REARQ_REDIS_PORT: 6379
  REARQ_REDIS_DB: 1
```

### Using Separate Redis for ReArq

If you want to isolate ReArq from main Redis:

```yaml
rearq_redis:
  image: redis:7-alpine
  container_name: djangocfg_rearq_redis
  restart: unless-stopped
  ports:
    - "7378:6379"
  volumes:
    - rearq_redis_data:/data

# Then update in worker:
environment:
  REARQ_REDIS_HOST: rearq_redis
  REARQ_REDIS_PORT: 6379
  REARQ_REDIS_DB: 0
```

## 📊 Architecture

```
┌─────────────────┐
│   Django App    │
│                 │
│  await task()   │
└────────┬────────┘
         │
         v
┌─────────────────┐      ┌──────────────┐
│  Redis (7379)   │◄────►│ ReArq Worker │
│  Task Broker +  │      │  (Processor) │
│  Job Storage    │      └──────────────┘
└─────────────────┘
         ▲
         │
         │
  ┌──────┴───────┐
  │ ReArq Server │
  │  Web UI:7380 │
  └──────────────┘
```

**Simplified Architecture**: ReArq stores everything in Redis, no separate database required.

## 🎯 Queues and Workers

### Current Queues

1. **high_priority** — critical tasks (emails, notifications)
2. **default** — normal tasks
3. **low_priority** — background tasks (reports, cleanup)

### Scaling Workers

To increase performance, run more workers:

```bash
docker compose -f docker-compose-local-services.yml up -d --scale rearq_worker=3
```

Or add more workers in docker-compose:

```yaml
rearq_worker_2:
  build:
    context: .
    dockerfile: services/rearq/Dockerfile
  container_name: djangocfg_rearq_worker_2
  # ... same configuration as rearq_worker
```

## 🌐 Web UI Features

### Available Sections

- **Dashboard** — overall statistics
- **Queues** — view queues and tasks
- **Jobs** — history of executed tasks
- **Workers** — worker status
- **Cron** — scheduled tasks
- **API Docs** — Swagger UI

### Example Operations via UI

1. **View Tasks** — list all tasks with filters
2. **Retry Task** — restart failed tasks
3. **Cancel Task** — stop execution
4. **View Results** — execution details
5. **Statistics** — charts and metrics

## 🔌 REST API

### Main Endpoints

```bash
# List jobs
curl http://localhost:7380/api/jobs

# Job details
curl http://localhost:7380/api/jobs/{job_id}

# Queue statistics
curl http://localhost:7380/api/queues

# Worker list
curl http://localhost:7380/api/workers

# Cron tasks
curl http://localhost:7380/api/cron
```

Full documentation: http://localhost:7380/docs

## 🐛 Debugging

### Check Redis Connection

```bash
docker compose -f docker-compose-local-services.yml exec redis redis-cli ping
# Should return: PONG
```

### Check Task Data in Redis

```bash
docker compose -f docker-compose-local-services.yml exec redis redis-cli -n 1
> KEYS arq:*
> HGETALL arq:job:<job_id>
```

### View Tasks in Redis

```bash
docker compose -f docker-compose-local-services.yml exec redis redis-cli
> SELECT 1
> KEYS *
> HGETALL arq:queue:default
```

### View All Queues

```bash
docker compose -f docker-compose-local-services.yml exec redis redis-cli -n 1
> KEYS arq:queue:*
> LLEN arq:queue:default
> LRANGE arq:queue:default 0 -1
```

## 🔄 Django Integration

### Example Django View

```python
# views.py
from django.http import JsonResponse
from services.rearq.main import send_email_task

async def send_notification(request):
    user_id = request.GET.get('user_id')

    # Queue task
    job = await send_email_task.delay(
        email="user@example.com",
        subject="Hello",
        body="Welcome!"
    )

    return JsonResponse({
        "status": "queued",
        "job_id": job.job_id
    })
```

### Example Django Management Command

```python
# management/commands/process_users.py
from django.core.management.base import BaseCommand
from services.rearq.main import process_file_task

class Command(BaseCommand):
    async def handle(self, *args, **options):
        await process_file_task.delay(file_path="/path/to/file.txt")
        self.stdout.write("Task queued!")
```

## 📦 Production Deployment

### Production Recommendations

1. **Use separate Redis** for ReArq (isolation from main Redis)
2. **Set up monitoring** — integrate with Prometheus/Grafana
3. **Enable authentication** for Web UI (via reverse proxy)
4. **Configure Redis persistence** (AOF or RDB) to preserve tasks on restart
5. **Scale workers** based on load (use replicas in docker-compose)
6. **Set up logging** in ELK/Loki
7. **Use Redis Sentinel** for high availability

### Example Production Configuration

```yaml
rearq_worker:
  deploy:
    replicas: 5
    resources:
      limits:
        cpus: '2.0'
        memory: 2G
      reservations:
        cpus: '0.5'
        memory: 512M
```

## 🔐 Security

### Basic Authentication for UI

For production environment, add reverse proxy (nginx) with authentication:

```nginx
location /rearq {
    auth_basic "ReArq Admin";
    auth_basic_user_file /etc/nginx/.htpasswd;
    proxy_pass http://localhost:7380;
}
```

### Access Restriction

In `docker-compose-production.yaml`, don't publish ReArq ports externally:

```yaml
rearq_server:
  # Remove ports for internal use only
  # ports:
  #   - "7380:8080"
  networks:
    - internal
```

## 📚 Links

- **ReArq GitHub**: https://github.com/long2ice/rearq
- **ARQ (base project)**: https://github.com/samuelcolvin/arq
- **Documentation**: https://rearq.readthedocs.io/
- **OpenAPI Spec**: http://localhost:7380/openapi.json

## 🆘 Support

If you encounter issues:

1. Check logs: `docker compose logs rearq_worker rearq_server`
2. Check service status: `docker compose ps`
3. Check Redis connection
4. Open issue in Django-CFG project

---

**Django-CFG Team** | Production-Ready Django Template
