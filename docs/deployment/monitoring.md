---
title: Monitoring & Logging
description: Deploy Django-CFG with monitoring. Complete deployment guide for monitoring & logging with Docker, environment configuration, and production best practices.
sidebar_label: Monitoring
sidebar_position: 4
keywords:
  - django-cfg monitoring
  - deploy django-cfg
  - django monitoring deployment
---

# 📊 Monitoring Guide

Django-CFG provides built-in monitoring and logging capabilities that work seamlessly in both development and production environments.

---

## Core Principles

### Zero-Configuration Monitoring
- **Health checks** work out of the box
- **System metrics** automatically collected
- **Database monitoring** for all configured databases
- **Smart logging** with automatic level adjustment

### Environment-Aware
- Development: Verbose logging, detailed errors
- Production: Structured logs, error tracking
- Docker: Container-aware resource monitoring

---

## Health Check Endpoints

Django-CFG includes built-in health check endpoints for monitoring service status.

### Simple Health Check

Basic liveness probe for container orchestration:

```bash
GET /health/simple/
```

**Response:**
```json
{
  "status": "ok",
  "timestamp": "2025-10-14T12:34:56.789Z"
}
```

**Use cases:**
- Docker health checks
- Kubernetes liveness probes
- Load balancer health monitoring

### Comprehensive Health Check

Detailed system status with metrics:

```bash
GET /health/
```

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-10-14T12:34:56.789Z",
  "checks": {
    "database": {
      "status": "healthy",
      "databases": {
        "default": {
          "status": "healthy",
          "response_time_ms": 2.45,
          "engine": "django.db.backends.postgresql"
        }
      }
    },
    "cache": {
      "status": "healthy",
      "response_time_ms": 0.89,
      "backend": "django_redis.cache.RedisCache"
    },
    "system": {
      "status": "healthy",
      "cpu": {
        "usage_percent": 15.2,
        "status": "healthy"
      },
      "memory": {
        "usage_percent": 45.6,
        "total_gb": 16.0,
        "available_gb": 8.7,
        "status": "healthy"
      },
      "disk": {
        "usage_percent": 62.3,
        "total_gb": 500.0,
        "free_gb": 188.5,
        "status": "healthy"
      }
    },
    "configuration": {
      "status": "healthy",
      "django_cfg": {
        "version": "1.3.13",
        "debug": false,
        "environment": "production"
      }
    }
  }
}
```

**Monitored components:**
- ✅ Database connectivity and response times
- ✅ Cache availability and performance
- ✅ CPU, memory, disk usage
- ✅ System uptime and load average
- ✅ Configuration validation

---

## System Monitoring

Django-CFG includes a system monitor that tracks real-time metrics.

### Available Metrics

**CPU Metrics:**
- Usage percentage
- Core count (physical and logical)
- Load average (1min, 5min, 15min)

**Memory Metrics:**
- Usage percentage
- Total, used, available memory
- Memory breakdown by category

**Disk Metrics:**
- Disk usage percentage
- Total, used, free space
- I/O statistics

**Database Status:**
- Connection health per database
- Response time tracking
- Error detection

**User Statistics:**
- Total users
- Active users (30-day window)
- Staff and superuser counts

### Admin Dashboard Integration

The system monitor integrates with Django Admin (Unfold):

```python
# Automatic integration - no configuration needed
# Access via Django Admin dashboard

# Real-time metrics displayed:
# - CPU usage graphs
# - Memory consumption
# - Database connection status
# - Active user statistics
```

---

## Logging System

Django-CFG includes a built-in logging module that works out of the box.

### Zero-Configuration Logging

Logging is automatically configured based on environment:

**Development:**
- Console output with colors
- DEBUG level messages
- Rich tracebacks for errors

**Production:**
- File logging with rotation
- WARNING level and above
- Structured log format

### Basic Usage

```python
from django_cfg.modules.django_logging import logger

# Standard logging methods
logger.info("User logged in")
logger.warning("Cache miss")
logger.error("Connection failed")
logger.success("Deployment complete")
```

**That's it!** No configuration needed—the module handles everything automatically.

For detailed logging configuration, see **[Logging Configuration →](/deployment/logging)**

---

## Docker Health Checks

Django-CFG health checks work seamlessly with Docker.

### Docker Compose Configuration

```yaml
services:
  django:
    image: your-django-app
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health/simple/"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
```

### Kubernetes Probes

```yaml
apiVersion: v1
kind: Pod
spec:
  containers:
  - name: django
    image: your-django-app
    livenessProbe:
      httpGet:
        path: /health/simple/
        port: 8000
      initialDelaySeconds: 30
      periodSeconds: 10
    readinessProbe:
      httpGet:
        path: /health/
        port: 8000
      initialDelaySeconds: 10
      periodSeconds: 5
```

---

## Production Monitoring Best Practices

### 1. External Monitoring

Integrate with external monitoring services:

**Uptime Monitoring:**
- UptimeRobot
- Pingdom
- StatusCake

Configure to check `/health/simple/` endpoint every 1-5 minutes.

**Error Tracking:**
```python
# Add Sentry integration (optional)
# Django-CFG logging integrates with Sentry handlers

INSTALLED_APPS += ['sentry_sdk']

import sentry_sdk
sentry_sdk.init(
    dsn="your-sentry-dsn",
    environment="production",
)
```

### 2. Log Aggregation

Send logs to centralized service:

- **ELK Stack** (Elasticsearch, Logstash, Kibana)
- **Datadog** - Application monitoring
- **CloudWatch** - AWS logging
- **Grafana Loki** - Log aggregation

### 3. Alerting Rules

Set up alerts for:

```yaml
# Example alerting thresholds
cpu_usage: > 80%
memory_usage: > 85%
disk_usage: > 90%
database_response_time: > 1000ms
error_rate: > 10 errors/minute
```

### 4. Metrics Export

Export metrics to monitoring systems:

```python
# Prometheus metrics endpoint (optional)
# Django-CFG metrics can be exported via django-prometheus

INSTALLED_APPS += ['django_prometheus']

# Metrics available at /metrics/
```

---

## Monitoring Checklist

Before deploying to production:

### Health Checks
- [ ] `/health/simple/` endpoint returns 200 OK
- [ ] `/health/` shows all systems healthy
- [ ] Database connectivity verified
- [ ] Cache availability verified

### Logging
- [ ] Log directory exists and is writable
- [ ] Log rotation configured (10MB files)
- [ ] Error logs separated from info logs
- [ ] Log level set to WARNING or higher

### External Monitoring
- [ ] Uptime monitoring configured
- [ ] Error tracking service integrated
- [ ] Log aggregation set up
- [ ] Alert rules configured

### Resource Monitoring
- [ ] CPU usage tracking enabled
- [ ] Memory monitoring active
- [ ] Disk space alerts configured
- [ ] Database performance tracked

---

## Troubleshooting

### Health Check Returns "unhealthy"

**Check database connectivity:**
```bash
# Test database connection
python manage.py dbshell

# Check database logs
docker logs postgres_container
```

**Check cache connectivity:**
```bash
# Test Redis connection
redis-cli ping

# Check cache configuration
python manage.py shell -c "from django.core.cache import cache; print(cache.get('test'))"
```

### High Resource Usage Warnings

**CPU usage > 90%:**
- Check for infinite loops
- Review Dramatiq worker count
- Optimize database queries
- Enable query caching

**Memory usage > 85%:**
- Check for memory leaks
- Review queryset evaluation
- Optimize image processing
- Reduce worker memory limit

**Disk usage > 90%:**
- Clean up old log files
- Remove unused media files
- Set up log rotation
- Archive old backups

### Logs Not Writing

**Check permissions:**
```bash
# Ensure log directory is writable
chmod 755 logs/
chown -R django-user:django-user logs/
```

**Check disk space:**
```bash
# Verify available disk space
df -h /path/to/logs
```

**Check configuration:**
```python
# Verify logging config in settings
print(settings.LOGGING)
```

---

## See Also

- **[Logging Configuration](/deployment/logging)** - Detailed logging setup
- **[Docker Guide](/guides/docker/overview)** - Docker health checks
- **[Security Guide](/deployment/security)** - Security monitoring
- **[Production Config](/guides/production-config)** - Production best practices

---

TAGS: monitoring, logging, health-checks, metrics, docker, kubernetes, production
DEPENDS_ON: [django-cfg, docker, postgresql, redis]
USED_BY: [production, devops, sre, monitoring-tools]
