> **📚 Part of**: [ReArq Integration](/features/integrations/rearq/overview) - Return to ReArq overview

# ReArq Tasks Deployment Guide

**Status**: Draft
**Author**: Django-CFG Team
**Date**: 2025-10-30
**Version**: 1.0

## Overview

Complete production deployment guide for ReArq tasks in django-cfg projects.

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Infrastructure Setup](#infrastructure-setup)
3. [Worker Configuration](#worker-configuration)
4. [Monitoring Setup](#monitoring-setup)
5. [Scaling Strategy](#scaling-strategy)
6. [Security Hardening](#security-hardening)
7. [Performance Tuning](#performance-tuning)
8. [Backup & Recovery](#backup--recovery)
9. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Required Services

| Service | Version | Purpose |
|---------|---------|---------|
| Redis | 6.0+ | Task queue & state |
| PostgreSQL | 13+ | Task persistence |
| Python | 3.11+ | Runtime |
| Django | 5.0+ | Web framework |

### System Requirements

**Minimum** (Development):
- 2 CPU cores
- 2GB RAM
- 10GB disk space

**Recommended** (Production):
- 4+ CPU cores
- 8GB+ RAM
- 50GB+ SSD
- Separate Redis instance
- Database with replication

---

## Infrastructure Setup

### 1. Redis Configuration

#### Basic redis.conf

```conf
# /etc/redis/redis.conf

# Network
bind 127.0.0.1
port 6379
protected-mode yes
requirepass your-strong-password-here

# Persistence
save 900 1
save 300 10
save 60 10000
stop-writes-on-bgsave-error yes
rdbcompression yes
rdbchecksum yes
dbfilename dump.rdb
dir /var/lib/redis

# Memory
maxmemory 2gb
maxmemory-policy allkeys-lru

# Logging
loglevel notice
logfile /var/log/redis/redis-server.log

# Performance
tcp-backlog 511
timeout 0
tcp-keepalive 300
```

#### Redis Sentinel (High Availability)

```conf
# /etc/redis/sentinel.conf

port 26379
sentinel monitor mymaster 127.0.0.1 6379 2
sentinel auth-pass mymaster your-strong-password-here
sentinel down-after-milliseconds mymaster 5000
sentinel parallel-syncs mymaster 1
sentinel failover-timeout mymaster 10000
```

**Start Sentinel**:
```bash
redis-sentinel /etc/redis/sentinel.conf
```

### 2. PostgreSQL Setup

#### Create Database

```sql
-- Create user
CREATE USER rearq_user WITH PASSWORD 'strong-password';

-- Create database
CREATE DATABASE rearq_db
    OWNER rearq_user
    ENCODING 'UTF8'
    LC_COLLATE 'en_US.UTF-8'
    LC_CTYPE 'en_US.UTF-8';

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE rearq_db TO rearq_user;
```

#### Connection Pooling (pgbouncer)

```ini
; /etc/pgbouncer/pgbouncer.ini

[databases]
rearq_db = host=localhost port=5432 dbname=rearq_db

[pgbouncer]
listen_addr = 127.0.0.1
listen_port = 6432
auth_type = md5
auth_file = /etc/pgbouncer/userlist.txt
pool_mode = transaction
max_client_conn = 100
default_pool_size = 20
```

### 3. System Limits

```bash
# /etc/security/limits.conf

# Redis
redis soft nofile 65535
redis hard nofile 65535

# Worker processes
www-data soft nofile 65535
www-data hard nofile 65535
```

### 4. Firewall Rules

```bash
# Allow Redis (internal only)
sudo ufw allow from 10.0.0.0/8 to any port 6379

# Allow PostgreSQL (internal only)
sudo ufw allow from 10.0.0.0/8 to any port 5432

# Allow ReArq monitoring server (internal only)
sudo ufw allow from 10.0.0.0/8 to any port 8001
```

---

## Worker Configuration

### 1. Systemd Services

#### Worker Service

```ini
# /etc/systemd/system/rearq-worker@.service

[Unit]
Description=ReArq Worker (%i)
After=network.target redis.service postgresql.service
Requires=redis.service postgresql.service

[Service]
Type=simple
User=www-data
Group=www-data
WorkingDirectory=/opt/myproject
Environment="DJANGO_SETTINGS_MODULE=myproject.settings.production"
Environment="PYTHONPATH=/opt/myproject"

# Worker command
ExecStart=/opt/myproject/venv/bin/rearq main:rearq worker --queue %i

# Restart policy
Restart=always
RestartSec=10
StartLimitInterval=0

# Resource limits
LimitNOFILE=65535
MemoryMax=1G
CPUQuota=50%

# Logging
StandardOutput=journal
StandardError=journal
SyslogIdentifier=rearq-worker-%i

[Install]
WantedBy=multi-user.target
```

**Enable multiple workers**:
```bash
# Enable workers for different queues
sudo systemctl enable rearq-worker@default
sudo systemctl enable rearq-worker@high
sudo systemctl enable rearq-worker@low
sudo systemctl enable rearq-worker@emails

# Start services
sudo systemctl start rearq-worker@default
sudo systemctl start rearq-worker@high
sudo systemctl start rearq-worker@low
sudo systemctl start rearq-worker@emails

# Check status
sudo systemctl status rearq-worker@*
```

#### Timer Service

```ini
# /etc/systemd/system/rearq-timer.service

[Unit]
Description=ReArq Timer (Cron Tasks)
After=network.target redis.service postgresql.service
Requires=redis.service postgresql.service

[Service]
Type=simple
User=www-data
Group=www-data
WorkingDirectory=/opt/myproject
Environment="DJANGO_SETTINGS_MODULE=myproject.settings.production"

ExecStart=/opt/myproject/venv/bin/rearq main:rearq worker --with-timer

Restart=always
RestartSec=10

StandardOutput=journal
StandardError=journal
SyslogIdentifier=rearq-timer

[Install]
WantedBy=multi-user.target
```

**Enable timer**:
```bash
sudo systemctl enable rearq-timer
sudo systemctl start rearq-timer
```

#### Monitoring Server Service

```ini
# /etc/systemd/system/rearq-server.service

[Unit]
Description=ReArq Monitoring Server
After=network.target redis.service postgresql.service

[Service]
Type=simple
User=www-data
Group=www-data
WorkingDirectory=/opt/myproject
Environment="DJANGO_SETTINGS_MODULE=myproject.settings.production"

ExecStart=/opt/myproject/venv/bin/rearq main:rearq server

Restart=always
RestartSec=5

StandardOutput=journal
StandardError=journal
SyslogIdentifier=rearq-server

[Install]
WantedBy=multi-user.target
```

### 2. Supervisor Configuration

Alternative to systemd:

```ini
; /etc/supervisor/conf.d/rearq.conf

[group:rearq]
programs=worker-default,worker-high,worker-low,timer,server

[program:worker-default]
command=/opt/myproject/venv/bin/rearq main:rearq worker --queue default
directory=/opt/myproject
user=www-data
autostart=true
autorestart=true
stopasgroup=true
killasgroup=true
redirect_stderr=true
stdout_logfile=/var/log/rearq/worker-default.log
stdout_logfile_maxbytes=50MB
stdout_logfile_backups=10
environment=DJANGO_SETTINGS_MODULE="myproject.settings.production"

[program:worker-high]
command=/opt/myproject/venv/bin/rearq main:rearq worker --queue high
directory=/opt/myproject
user=www-data
autostart=true
autorestart=true
stopasgroup=true
killasgroup=true
redirect_stderr=true
stdout_logfile=/var/log/rearq/worker-high.log
environment=DJANGO_SETTINGS_MODULE="myproject.settings.production"

[program:worker-low]
command=/opt/myproject/venv/bin/rearq main:rearq worker --queue low
directory=/opt/myproject
user=www-data
autostart=true
autorestart=true
stopasgroup=true
killasgroup=true
redirect_stderr=true
stdout_logfile=/var/log/rearq/worker-low.log
environment=DJANGO_SETTINGS_MODULE="myproject.settings.production"

[program:timer]
command=/opt/myproject/venv/bin/rearq main:rearq worker --with-timer
directory=/opt/myproject
user=www-data
autostart=true
autorestart=true
stopasgroup=true
killasgroup=true
redirect_stderr=true
stdout_logfile=/var/log/rearq/timer.log
environment=DJANGO_SETTINGS_MODULE="myproject.settings.production"

[program:server]
command=/opt/myproject/venv/bin/rearq main:rearq server
directory=/opt/myproject
user=www-data
autostart=true
autorestart=true
stopasgroup=true
killasgroup=true
redirect_stderr=true
stdout_logfile=/var/log/rearq/server.log
environment=DJANGO_SETTINGS_MODULE="myproject.settings.production"
```

**Manage services**:
```bash
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start rearq:*
sudo supervisorctl status rearq:*
```

### 3. Docker Setup

#### Dockerfile

```dockerfile
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Create logs directory
RUN mkdir -p /var/log/rearq

# Run as non-root
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app /var/log/rearq
USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD rearq main:rearq health || exit 1

# Default command
CMD ["rearq", "main:rearq", "worker", "--queue", "default"]
```

#### docker-compose.yml

```yaml
version: '3.8'

services:
  redis:
    image: redis:7-alpine
    command: redis-server --requirepass ${REDIS_PASSWORD}
    volumes:
      - redis-data:/data
    networks:
      - backend
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 5s
      timeout: 3s
      retries: 5

  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: ${DB_NAME}
      POSTGRES_USER: ${DB_USER}
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres-data:/var/lib/postgresql/data
    networks:
      - backend
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${DB_USER}"]
      interval: 5s
      timeout: 5s
      retries: 5

  worker-default:
    build: .
    command: rearq main:rearq worker --queue default
    environment:
      - DJANGO_SETTINGS_MODULE=myproject.settings.production
      - REDIS_URL=redis://:${REDIS_PASSWORD}@redis:6379/0
      - DATABASE_URL=postgresql://${DB_USER}:${DB_PASSWORD}@postgres:5432/${DB_NAME}
    depends_on:
      redis:
        condition: service_healthy
      postgres:
        condition: service_healthy
    networks:
      - backend
    restart: unless-stopped
    deploy:
      replicas: 2
      resources:
        limits:
          cpus: '0.5'
          memory: 512M

  worker-high:
    build: .
    command: rearq main:rearq worker --queue high
    environment:
      - DJANGO_SETTINGS_MODULE=myproject.settings.production
      - REDIS_URL=redis://:${REDIS_PASSWORD}@redis:6379/0
      - DATABASE_URL=postgresql://${DB_USER}:${DB_PASSWORD}@postgres:5432/${DB_NAME}
    depends_on:
      redis:
        condition: service_healthy
      postgres:
        condition: service_healthy
    networks:
      - backend
    restart: unless-stopped
    deploy:
      replicas: 1

  timer:
    build: .
    command: rearq main:rearq worker --with-timer
    environment:
      - DJANGO_SETTINGS_MODULE=myproject.settings.production
      - REDIS_URL=redis://:${REDIS_PASSWORD}@redis:6379/0
      - DATABASE_URL=postgresql://${DB_USER}:${DB_PASSWORD}@postgres:5432/${DB_NAME}
    depends_on:
      redis:
        condition: service_healthy
      postgres:
        condition: service_healthy
    networks:
      - backend
    restart: unless-stopped
    deploy:
      replicas: 1

  rearq-server:
    build: .
    command: rearq main:rearq server
    ports:
      - "8001:8001"
    environment:
      - DJANGO_SETTINGS_MODULE=myproject.settings.production
      - REDIS_URL=redis://:${REDIS_PASSWORD}@redis:6379/0
      - DATABASE_URL=postgresql://${DB_USER}:${DB_PASSWORD}@postgres:5432/${DB_NAME}
    depends_on:
      redis:
        condition: service_healthy
      postgres:
        condition: service_healthy
    networks:
      - backend
    restart: unless-stopped

networks:
  backend:
    driver: bridge

volumes:
  redis-data:
  postgres-data:
```

---

## Monitoring Setup

### 1. Prometheus Metrics

```python
# myproject/monitoring.py

from prometheus_client import Counter, Histogram, Gauge

# Metrics
task_counter = Counter(
    'rearq_tasks_total',
    'Total tasks executed',
    ['task_name', 'status']
)

task_duration = Histogram(
    'rearq_task_duration_seconds',
    'Task execution duration',
    ['task_name']
)

queue_size = Gauge(
    'rearq_queue_size',
    'Current queue size',
    ['queue_name']
)

worker_count = Gauge(
    'rearq_workers_active',
    'Number of active workers'
)
```

### 2. Health Check Endpoint

```python
# myproject/health.py

from django.http import JsonResponse
from django_cfg.apps.tasks import get_rearq_client

async def rearq_health_check(request):
    """Health check endpoint for load balancers."""
    try:
        client = get_rearq_client()

        # Check Redis connection
        await client.redis.ping()

        # Check worker count
        workers_info = await client.redis.hgetall("rearq:workers")
        worker_count = len(workers_info)

        return JsonResponse({
            "status": "healthy",
            "redis": "ok",
            "workers": worker_count,
        })
    except Exception as e:
        return JsonResponse({
            "status": "unhealthy",
            "error": str(e)
        }, status=503)
```

### 3. Grafana Dashboard

```json
{
  "dashboard": {
    "title": "ReArq Tasks Monitoring",
    "panels": [
      {
        "title": "Task Execution Rate",
        "targets": [
          {
            "expr": "rate(rearq_tasks_total[5m])"
          }
        ]
      },
      {
        "title": "Queue Sizes",
        "targets": [
          {
            "expr": "rearq_queue_size"
          }
        ]
      },
      {
        "title": "Task Duration (p95)",
        "targets": [
          {
            "expr": "histogram_quantile(0.95, rearq_task_duration_seconds_bucket)"
          }
        ]
      },
      {
        "title": "Active Workers",
        "targets": [
          {
            "expr": "rearq_workers_active"
          }
        ]
      }
    ]
  }
}
```

### 4. Alerting Rules

```yaml
# prometheus-alerts.yml

groups:
  - name: rearq
    interval: 30s
    rules:
      - alert: ReArqNoWorkers
        expr: rearq_workers_active == 0
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "No ReArq workers running"
          description: "All ReArq workers are down"

      - alert: ReArqQueueBacklog
        expr: rearq_queue_size > 1000
        for: 10m
        labels:
          severity: warning
        annotations:
          summary: "ReArq queue backlog detected"
          description: "Queue {{ $labels.queue_name }} has {{ $value }} jobs"

      - alert: ReArqHighFailureRate
        expr: rate(rearq_tasks_total{status="failed"}[5m]) > 0.1
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High task failure rate"
          description: "Failure rate is {{ $value }} per second"
```

---

## Scaling Strategy

### Horizontal Scaling

#### Add More Workers

```bash
# Start additional workers for specific queue
sudo systemctl start rearq-worker@default-2
sudo systemctl start rearq-worker@default-3

# Or with Docker Compose
docker-compose up -d --scale worker-default=5
```

#### Queue-Based Scaling

```python
# config.py - Production settings
from django_cfg.models.tasks import TaskConfig, RearqConfig

tasks = TaskConfig(
    enabled=True,
    rearq=RearqConfig(
        redis_url=env("REDIS_URL"),
        db_url=env("DATABASE_URL"),

        # Increase max jobs per worker
        max_jobs=20,

        # Increase timeout for long tasks
        job_timeout=600,
    )
)
```

**Worker allocation strategy**:

| Queue | Workers | Purpose |
|-------|---------|---------|
| `high` | 2-4 | Critical tasks (payments, notifications) |
| `default` | 4-8 | General tasks |
| `low` | 1-2 | Background jobs |
| `emails` | 2-4 | Email sending |
| `processing` | 2-4 | Data processing |

### Vertical Scaling

#### Optimize Worker Resources

```ini
# systemd service
[Service]
MemoryMax=2G
CPUQuota=100%
```

#### Connection Pool Tuning

```python
# Increase Redis connection pool
from django_cfg.models.tasks import TaskConfig, RearqConfig

tasks = TaskConfig(
    enabled=True,
    rearq=RearqConfig(
        redis_url="redis://localhost:6379/0?max_connections=50",
    )
)
```

### Auto-Scaling (Kubernetes)

```yaml
# hpa.yaml - Horizontal Pod Autoscaler

apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: rearq-worker-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: rearq-worker
  minReplicas: 2
  maxReplicas: 20
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: External
    external:
      metric:
        name: rearq_queue_size
      target:
        type: AverageValue
        averageValue: "100"
  behavior:
    scaleUp:
      stabilizationWindowSeconds: 60
      policies:
      - type: Percent
        value: 50
        periodSeconds: 60
    scaleDown:
      stabilizationWindowSeconds: 300
      policies:
      - type: Pods
        value: 1
        periodSeconds: 60
```

---

## Security Hardening

### 1. Redis Security

```conf
# redis.conf

# Strong password
requirepass $(openssl rand -base64 32)

# Disable dangerous commands
rename-command FLUSHDB ""
rename-command FLUSHALL ""
rename-command CONFIG ""

# Network security
bind 127.0.0.1
protected-mode yes

# TLS/SSL
tls-port 6380
tls-cert-file /path/to/redis.crt
tls-key-file /path/to/redis.key
tls-ca-cert-file /path/to/ca.crt
```

### 2. Database Security

```python
# settings/production.py

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'OPTIONS': {
            'sslmode': 'require',
            'sslrootcert': '/path/to/ca.crt',
        },
    }
}
```

### 3. Monitoring Server Protection

```nginx
# /etc/nginx/sites-available/rearq-server

server {
    listen 443 ssl http2;
    server_name rearq.internal.example.com;

    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;

    # Basic auth
    auth_basic "ReArq Monitoring";
    auth_basic_user_file /etc/nginx/.htpasswd;

    # IP whitelist
    allow 10.0.0.0/8;
    deny all;

    location / {
        proxy_pass http://localhost:8001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### 4. Task Argument Validation

```python
from pydantic import BaseModel, validator

class TaskInput(BaseModel):
    """Validated task input."""
    user_id: int
    email: str

    @validator('email')
    def validate_email(cls, v):
        # Validate email format
        if '@' not in v:
            raise ValueError('Invalid email')
        return v

@task()
async def send_email_validated(input_data: dict):
    """Task with validated input."""
    # Parse and validate
    data = TaskInput(**input_data)

    # Use validated data
    await send_email(data.email, "Subject", "Body")
```

---

## Performance Tuning

### 1. Redis Performance

```conf
# redis.conf

# Use faster allocator
# Install jemalloc: apt-get install libjemalloc-dev

# Increase client output buffer
client-output-buffer-limit normal 0 0 0
client-output-buffer-limit replica 256mb 64mb 60
client-output-buffer-limit pubsub 32mb 8mb 60

# Disable RDB in production (use AOF)
save ""
appendonly yes
appendfsync everysec

# Lazy freeing
lazyfree-lazy-eviction yes
lazyfree-lazy-expire yes
lazyfree-lazy-server-del yes
replica-lazy-flush yes
```

### 2. Database Optimization

```sql
-- Create indexes
CREATE INDEX idx_job_status ON rearq_job(status);
CREATE INDEX idx_job_task ON rearq_job(task);
CREATE INDEX idx_job_enqueue_time ON rearq_job(enqueue_time);
CREATE INDEX idx_result_job_id ON rearq_job_results(job_id);

-- Partitioning (for large tables)
CREATE TABLE rearq_job (
    id BIGSERIAL,
    enqueue_time TIMESTAMP NOT NULL,
    -- other fields
) PARTITION BY RANGE (enqueue_time);

CREATE TABLE rearq_job_2025_01 PARTITION OF rearq_job
    FOR VALUES FROM ('2025-01-01') TO ('2025-02-01');
```

### 3. Worker Optimization

```python
# config.py
from django_cfg.models.tasks import TaskConfig, RearqConfig

tasks = TaskConfig(
    enabled=True,
    rearq=RearqConfig(
        # Increase concurrent jobs
        max_jobs=25,

        # Reduce timeout for fast tasks
        job_timeout=60,

        # Faster retry
        job_retry_after=10,

        # More delay queues (better distribution)
        delay_queue_num=8,
    )
)
```

---

## Backup & Recovery

### 1. Redis Backup

```bash
#!/bin/bash
# backup-redis.sh

BACKUP_DIR="/backups/redis"
DATE=$(date +%Y%m%d_%H%M%S)

# Trigger BGSAVE
redis-cli BGSAVE

# Wait for save to complete
while [ $(redis-cli LASTSAVE) -eq $LAST_SAVE ]; do
    sleep 1
done

# Copy dump
cp /var/lib/redis/dump.rdb "$BACKUP_DIR/dump_$DATE.rdb"

# Keep last 7 days
find "$BACKUP_DIR" -name "dump_*.rdb" -mtime +7 -delete
```

### 2. Database Backup

```bash
#!/bin/bash
# backup-postgres.sh

BACKUP_DIR="/backups/postgres"
DATE=$(date +%Y%m%d_%H%M%S)

pg_dump -h localhost -U rearq_user rearq_db | gzip > "$BACKUP_DIR/rearq_db_$DATE.sql.gz"

# Keep last 30 days
find "$BACKUP_DIR" -name "rearq_db_*.sql.gz" -mtime +30 -delete
```

### 3. Disaster Recovery

```bash
# Restore Redis
sudo systemctl stop redis
cp /backups/redis/dump_20250130_120000.rdb /var/lib/redis/dump.rdb
sudo chown redis:redis /var/lib/redis/dump.rdb
sudo systemctl start redis

# Restore PostgreSQL
gunzip < /backups/postgres/rearq_db_20250130_120000.sql.gz | psql -h localhost -U rearq_user rearq_db
```

---

## Troubleshooting

### Common Issues

#### 1. Workers Not Processing Jobs

**Symptoms**: Jobs stuck in "queued" status

**Diagnosis**:
```bash
# Check worker status
sudo systemctl status rearq-worker@*

# Check logs
sudo journalctl -u rearq-worker@default -f

# Check Redis connection
redis-cli -h localhost -p 6379 -a password PING
```

**Solution**:
```bash
# Restart workers
sudo systemctl restart rearq-worker@*

# Check firewall
sudo ufw status

# Verify Redis
redis-cli -a password LLEN rearq:queue:default
```

#### 2. Memory Leaks

**Symptoms**: Worker memory usage growing over time

**Diagnosis**:
```bash
# Monitor memory
ps aux | grep "rearq main:rearq worker"

# Check for memory leaks in ReArq
ps aux | grep "rearq main:rearq"
```

**Solution**:
```bash
# Restart workers periodically
# Add to crontab
0 */6 * * * systemctl restart rearq-worker@*

# Or limit memory in systemd
MemoryMax=1G
```

#### 3. Task Deadlocks

**Symptoms**: Tasks stuck in "in_progress"

**Diagnosis**:
```bash
# Check long-running jobs
redis-cli -a password HGETALL rearq:workers
```

**Solution**:
```python
# Add timeout to all tasks
@task(job_timeout=300)  # 5 minutes max
async def my_task():
    pass
```

#### 4. Redis Connection Errors

**Symptoms**: `ConnectionError: Error connecting to Redis`

**Solution**:
```bash
# Check Redis status
sudo systemctl status redis

# Check network
telnet localhost 6379

# Check password
redis-cli -a password PING
```

### Debug Mode

```python
# settings/development.py
from django_cfg.models.tasks import TaskConfig, RearqConfig

tasks = TaskConfig(
    enabled=True,
    rearq=RearqConfig(
        raise_job_error=True,  # Propagate errors
        logs_dir="/tmp/rearq-logs",
    )
)
```

### Logging Configuration

```python
# settings.py

LOGGING = {
    'version': 1,
    'handlers': {
        'rearq': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': '/var/log/rearq/rearq.log',
            'maxBytes': 10485760,  # 10MB
            'backupCount': 5,
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'rearq': {
            'handlers': ['rearq'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
}
```

---

## Checklist

### Pre-Deployment

- [ ] Redis configured with password
- [ ] Database created and migrated
- [ ] Environment variables set
- [ ] Firewall rules configured
- [ ] SSL certificates installed
- [ ] Backup scripts created
- [ ] Monitoring configured
- [ ] Health checks implemented

### Post-Deployment

- [ ] Workers running
- [ ] Timer service running
- [ ] Test task execution
- [ ] Verify monitoring
- [ ] Check logs
- [ ] Test failover
- [ ] Document runbook

---

## See Also

### Deployment Guides
- **[Deployment Overview](/deployment/overview)** - All deployment options
- **[Production Configuration](/guides/production-config)** - Production settings
- **[Docker Production](/guides/docker/production)** - Docker deployment guide
- **[Docker Development](/guides/docker/development)** - Local development with Docker

### Infrastructure
- **[Database Setup](/fundamentals/configuration/database)** - PostgreSQL configuration
- **[Multi-Database](/guides/multi-database)** - Separate task database

### Monitoring
- **[Monitoring Guide](/features/integrations/rearq/monitoring)** - Monitor your workers
- **[Operations App](/features/built-in-apps/operations/overview)** - System operations

---

**End of Deployment Guide**
