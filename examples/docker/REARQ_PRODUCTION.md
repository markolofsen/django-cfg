# ReArq Production Deployment Guide

## Overview

ReArq is configured for production deployment with:
- **Worker**: Background task processor
- **Server**: Web UI + REST API for monitoring
- **Storage**: Shared Redis (Dokploy) for tasks, SQLite for Web UI metadata

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Traefik (Dokploy)                    │
│            https://tasks.djangocfg.com                  │
└────────────────────┬────────────────────────────────────┘
                     │
         ┌───────────┴───────────┐
         │                       │
    ┌────▼─────┐         ┌──────▼──────┐
    │  ReArq   │         │   ReArq     │
    │  Server  │◄────────┤   Worker    │
    │ (Web UI) │         │  (Tasks)    │
    └────┬─────┘         └──────┬──────┘
         │                      │
         │      ┌───────────────┘
         │      │
    ┌────▼──────▼───┐
    │  Shared Redis │
    │  (DB: 1)      │
    └───────────────┘
```

## Deployment

### 1. Build Images

```bash
cd /path/to/django-cfg/solution/docker

# Build ReArq images
docker compose -f docker-compose-production.yaml build rearq-worker rearq-server
```

### 2. Deploy Services

```bash
# Start ReArq services
docker compose -f docker-compose-production.yaml up -d rearq-worker rearq-server

# Check status
docker compose -f docker-compose-production.yaml ps
```

### 3. Access Web UI

**URL**: https://tasks.djangocfg.com

**Features**:
- Dashboard with task statistics
- Real-time task monitoring
- Job queue management
- Worker status
- REST API at `/docs`

## Configuration

### Environment Variables (.env.prod)

```bash
# Redis connection
REARQ_REDIS_HOST=shared-db-redis
REARQ_REDIS_PORT=6379
REARQ_REDIS_DB=1

# Web UI database (SQLite or PostgreSQL)
REARQ_DB_URL=sqlite:///app/rearq.db
```

### Resource Limits

**Worker**:
- CPU: 1.0 core
- Memory: 512MB (128MB reserved)

**Server**:
- CPU: 0.5 core
- Memory: 256MB (128MB reserved)

## Security

### Option 1: Basic Authentication (Recommended)

Add basic auth to Traefik labels in `docker-compose-production.yaml`:

```yaml
labels:
  - "traefik.http.routers.djangocfg-rearq.middlewares=rearq-auth"
  - "traefik.http.middlewares.rearq-auth.basicauth.users=admin:$$apr1$$hash$$here"
```

Generate password hash:
```bash
htpasswd -nb admin your-password
```

### Option 2: IP Whitelist

Restrict access to specific IPs:

```yaml
labels:
  - "traefik.http.routers.djangocfg-rearq.middlewares=rearq-ipwhitelist"
  - "traefik.http.middlewares.rearq-ipwhitelist.ipwhitelist.sourcerange=1.2.3.4/32,5.6.7.8/32"
```

## Monitoring

### Check Logs

```bash
# Worker logs
docker logs django-cfg-rearq-worker -f

# Server logs
docker logs django-cfg-rearq-server -f
```

### Health Checks

```bash
# Server health
curl https://tasks.djangocfg.com/

# API status
curl https://tasks.djangocfg.com/api/
```

## Task Queues

ReArq worker processes tasks from 3 queues (priority order):

1. **high_priority**: Critical tasks (e.g., payment processing)
2. **default**: Standard tasks (e.g., email sending)
3. **low_priority**: Background tasks (e.g., cleanup jobs)

## Scaling

### Scale Workers

```bash
# Scale to 3 workers
docker compose -f docker-compose-production.yaml up -d --scale rearq-worker=3
```

### PostgreSQL for Web UI (Optional)

For better performance with many jobs, switch to PostgreSQL:

```bash
# In .env.prod
REARQ_DB_URL=postgresql://postgres:postgres@shared-db-postgres:5432/rearq
```

Then recreate server:
```bash
docker compose -f docker-compose-production.yaml up -d --force-recreate rearq-server
```

## Backup & Maintenance

### SQLite Database Backup

```bash
# Backup Web UI metadata
docker exec django-cfg-rearq-server cp /app/rearq.db /app/rearq.db.backup

# Copy to host
docker cp django-cfg-rearq-server:/app/rearq.db.backup ./rearq-backup-$(date +%Y%m%d).db
```

### Clear Old Jobs

ReArq automatically keeps jobs for 7 days (configurable in `main.py`).

To manually clear old jobs, use Web UI or API.

## Troubleshooting

### Worker Not Processing Tasks

1. Check Redis connection:
   ```bash
   docker exec django-cfg-rearq-worker redis-cli -h shared-db-redis ping
   ```

2. Check worker logs:
   ```bash
   docker logs django-cfg-rearq-worker
   ```

3. Verify queues are registered:
   ```bash
   # Should see: "Registered tasks: example_task, send_email_task, process_file_task"
   docker logs django-cfg-rearq-worker | grep "Registered tasks"
   ```

### Web UI Not Accessible

1. Check server is running:
   ```bash
   docker ps | grep rearq-server
   ```

2. Check Traefik routing:
   ```bash
   docker logs traefik | grep djangocfg-rearq
   ```

3. Test internal access:
   ```bash
   docker exec django-cfg-rearq-server curl localhost:8080/
   ```

### Database Errors

If Tortoise ORM errors occur, recreate with fresh database:

```bash
docker compose -f docker-compose-production.yaml down rearq-server
docker volume rm django-cfg_rearq_data  # if using volume
docker compose -f docker-compose-production.yaml up -d rearq-server
```

## Upgrading

```bash
# Pull latest changes
git pull

# Rebuild images
docker compose -f docker-compose-production.yaml build rearq-worker rearq-server

# Restart services
docker compose -f docker-compose-production.yaml up -d rearq-worker rearq-server
```

## Support

- ReArq Documentation: https://github.com/long2ice/rearq
- Django-CFG ReArq Setup: `/solution/docker/services/rearq/README.md`
