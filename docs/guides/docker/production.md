---
title: Production Docker Setup
description: Deploy Django-CFG with docker production. Complete deployment guide for production docker setup with Docker, environment configuration, and production best practices.
sidebar_label: Production
sidebar_position: 6
keywords:
  - django-cfg docker production
  - deploy django-cfg
  - django docker production deployment
  - production docker compose
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# Production Docker Setup

> **📚 Part of**: [Docker Guide](./overview) - Return to Docker overview

:::tip[Production-Ready Infrastructure]
Django-CFG provides **production-ready Docker infrastructure** with modular compose files, automated health checks, and integrated task processing for scalable Django applications.
:::

## Overview

The Docker setup includes:
- **Modular Architecture** - Separate compose files for services and nginx
- **PostgreSQL + pgvector** - Database with vector extension for embeddings
- **Redis** - Caching and task queue management
- **Django Application** - Web server with health checks
- **ReArq Workers** - Background task processing
- **Nginx Proxy** - Production reverse proxy

## Quick Start

### Project Structure

```
docker/
├── docker-compose.yml              # Main compose file with includes
├── docker-compose.services.yml     # Core services (DB, Redis, Django)
├── docker-compose.nginx.yml        # Nginx reverse proxy
├── Dockerfile.django               # Django application image
├── env.production                  # Environment variables
├── postgres/
│   ├── Dockerfile                  # PostgreSQL + pgvector
│   └── init-db.sh                 # Database initialization
├── redis/
│   ├── Dockerfile                  # Redis configuration
│   └── redis.conf                 # Custom Redis settings
└── scripts/
    ├── entrypoint.sh              # Universal container entrypoint
    ├── build-and-run.sh           # Management script
    └── debug-django-rq.sh          # Django-RQ debugging
```

### Basic Commands

```bash
# Build all images
./scripts/build-and-run.sh build

# Start all services
./scripts/build-and-run.sh up

# Stop all services
./scripts/build-and-run.sh down

# View logs
docker compose logs -f [service_name]

# Check service health
docker compose ps
```

## Service Configuration

### PostgreSQL Database

**Configuration:**
- **Port:** 5433 (external) → 5432 (internal)
- **Databases:** `carapis_db` (main), `vehicles` (catalog)
- **Extensions:** `uuid-ossp`, `pg_trgm`, `vector` (pgvector)

```yaml
# docker-compose.services.yml
carapis_postgres:
  build:
    context: postgres
    dockerfile: Dockerfile
  container_name: carapis_postgres
  restart: unless-stopped
  environment:
    POSTGRES_DB: carapis_db
    POSTGRES_USER: carapis
    POSTGRES_PASSWORD: carapis_password
  ports:
    - "5433:5432"
  volumes:
    - ./volumes/postgres:/var/lib/postgresql/data
    - ./postgres/init-db.sh:/docker-entrypoint-initdb.d/init-db.sh
  healthcheck:
    test: ["CMD-SHELL", "pg_isready -U carapis -d carapis_db"]
    interval: 30s
    timeout: 10s
    retries: 5
    start_period: 60s
```

**Environment Variables:**
```bash
DATABASE_URL=postgresql://carapis:carapis_password@carapis_postgres:5432/carapis_db
DATABASE_VEHICLES_URL=postgresql://carapis:carapis_password@carapis_postgres:5432/vehicles
```

:::warning[Database Security]
**Production database security checklist:**
- ⚠️ **Change default passwords** - Never use example passwords in production
- ⚠️ **Restrict network access** - Bind to internal network only, not `0.0.0.0`
- ⚠️ **Use secrets management** - Store credentials in Docker secrets or vault
- ⚠️ **Enable SSL/TLS** - Encrypt database connections in production
- ⚠️ **Regular backups** - Automate backups to separate storage

**Example secure configuration:**
```yaml
environment:
  POSTGRES_PASSWORD_FILE: /run/secrets/db_password  # Use Docker secrets
```
:::

### Redis Cache & Task Queue

**Configuration:**
- **Port:** 6380 (external) → 6379 (internal)
- **Databases:** DB 0 (cache), DB 2 (Django-RQ tasks)
- **Custom config:** Optimized `redis.conf`

```yaml
carapis_redis:
  build:
    context: redis
    dockerfile: Dockerfile
  container_name: carapis_redis
  restart: unless-stopped
  ports:
    - "6380:6379"
  volumes:
    - ./volumes/redis:/data
    - ./redis/redis.conf:/usr/local/etc/redis/redis.conf
  command: redis-server /usr/local/etc/redis/redis.conf
  healthcheck:
    test: ["CMD", "redis-cli", "ping"]
    interval: 30s
    timeout: 10s
    retries: 3
    start_period: 30s
```

**Environment Variables:**
```bash
REDIS_URL=redis://carapis_redis:6379/0
DRAMATIQ_REDIS_DB=2
```

### Django Application

**Configuration:**
- **Port:** 8001 (external) → 8000 (internal)
- **Health Check:** `GET /cfg/health/`
- **Features:** Auto migrations, static files, Django-CFG integration

```yaml
carapis-django:
  build:
    context: ..
    dockerfile: docker/Dockerfile.django
  container_name: carapis_django
  restart: unless-stopped
  env_file:
    - env.production
  ports:
    - "8001:8000"
  volumes:
    - ./volumes/django/logs:/app/logs
    - ./volumes/django/static:/app/static
    - ./volumes/django/media:/app/media
  depends_on:
    carapis_postgres:
      condition: service_healthy
    carapis_redis:
      condition: service_healthy
  command: ["runserver"]
  healthcheck:
    test: ["CMD", "curl", "-f", "http://localhost:8000/cfg/health/"]
    interval: 30s
    timeout: 10s
    retries: 3
    start_period: 60s
```

### Django-RQ Workers

**Configuration:**
- **Processes:** 2 (configurable via `DRAMATIQ_PROCESSES`)
- **Threads:** 4 per process (configurable via `DRAMATIQ_THREADS`)
- **Command:** `rundjango-rq` (Django-CFG 1.1.67+)

```yaml
carapis-django-rq:
  build:
    context: ..
    dockerfile: docker/Dockerfile.django
  container_name: carapis_django-rq
  restart: unless-stopped
  env_file:
    - env.production
  environment:
    DRAMATIQ_PROCESSES: 2
    DRAMATIQ_THREADS: 4
  volumes:
    - ./volumes/django/logs:/app/logs
  depends_on:
    carapis_postgres:
      condition: service_healthy
    carapis_redis:
      condition: service_healthy
  command: ["rundjango-rq"]
  healthcheck:
    test: ["CMD", "ps", "aux"]
    interval: 30s
    timeout: 10s
    retries: 3
    start_period: 60s
```

## Dockerfile Configuration

### Django Application Image

```dockerfile
# Dockerfile.django
FROM python:3.12-slim

# Environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    DJANGO_SETTINGS_MODULE=api.settings \
    ENVIRONMENT=production \
    DEBUG=false \
    IS_PROD=true \
    IS_DOCKER=true

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    netcat-openbsd \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN pip install poetry==1.8.4

# Configure Poetry for Docker
ENV POETRY_NO_INTERACTION=1 \
    POETRY_VENV_IN_PROJECT=1 \
    POETRY_CACHE_DIR=/tmp/poetry_cache

WORKDIR /app

# Copy and install dependencies
COPY django/pyproject.toml ./
RUN poetry config virtualenvs.create false && \
    sed -i '/^\[tool\.poetry\.group\.local\]/,/^\[tool\.poetry\.scripts\]/{ /^\[tool\.poetry\.scripts\]/!d; }' pyproject.toml && \
    poetry lock && \
    poetry install --only main --no-root && \
    rm -rf $POETRY_CACHE_DIR

# Copy application code
COPY django/ .
COPY docker/scripts/ ./docker/scripts/

# Set permissions and create directories
RUN chmod +x /app/docker/scripts/entrypoint.sh && \
    mkdir -p /app/logs /app/static /app/media

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8000/cfg/health/ || exit 1

# Entrypoint and default command
ENTRYPOINT ["/app/docker/scripts/entrypoint.sh"]
CMD ["runserver"]
```

### PostgreSQL with pgvector

```dockerfile
# postgres/Dockerfile
FROM postgres:16

# Install build dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    git \
    postgresql-server-dev-16 \
    && rm -rf /var/lib/apt/lists/*

# Install pgvector extension
RUN git clone --branch v0.5.1 https://github.com/pgvector/pgvector.git /tmp/pgvector && \
    cd /tmp/pgvector && \
    make && \
    make install && \
    rm -rf /tmp/pgvector

# Copy initialization script
COPY init-db.sh /docker-entrypoint-initdb.d/
RUN chmod +x /docker-entrypoint-initdb.d/init-db.sh
```

## Application Startup Flow

### Service Dependencies

```mermaid
graph TD
    A[PostgreSQL] --> B[Database Ready]
    C[Redis] --> D[Cache Ready]
    B --> E[Django Application]
    D --> E
    E --> F[Web Server Running]
    B --> G[Django-RQ Workers]
    D --> G
    G --> H[Task Processing Active]
```

### Entrypoint Script

```bash
#!/bin/bash
# scripts/entrypoint.sh

set -e

# Wait for database
echo "Waiting for database..."
while ! nc -z carapis_postgres 5432; do
  sleep 1
done
echo "Database is ready!"

# Wait for Redis
echo "Waiting for Redis..."
while ! nc -z carapis_redis 6379; do
  sleep 1
done
echo "Redis is ready!"

# Run migrations
echo "Running migrations..."
python manage.py migrate --noinput

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Execute command based on argument
case "$1" in
    runserver)
        echo "Starting Django server..."
        exec python manage.py runserver 0.0.0.0:8000
        ;;
    rearq_worker)
        echo "Starting ReArq workers..."
        exec rearq main:rearq worker
        ;;
    migrate)
        echo "Running migrations only..."
        exec python manage.py migrate
        ;;
    shell)
        echo "Starting Django shell..."
        exec python manage.py shell
        ;;
    bash)
        echo "Starting bash shell..."
        exec /bin/bash
        ;;
    help)
        echo "Available commands:"
        echo "  runserver    - Start Django development server (default)"
        echo "  rearq_worker - Start ReArq workers"
        echo "  migrate      - Run database migrations"
        echo "  shell        - Django interactive shell"
        echo "  bash         - Debug shell"
        echo "  help         - Show this help"
        ;;
    *)
        echo "Unknown command: $1"
        echo "Use 'help' to see available commands"
        exit 1
        ;;
esac
```

## Environment Configuration

:::danger[Environment Security Critical]
**Environment files contain sensitive credentials:**
- 🔒 **Never commit** `.env` files to version control
- 🔒 **Use `.env.example`** with placeholder values for documentation
- 🔒 **Restrict file permissions** - `chmod 600 env.production`
- 🔒 **Use secrets management** - Docker secrets, AWS Secrets Manager, or HashiCorp Vault
- 🔒 **Rotate credentials** regularly (every 90 days minimum)

Add to `.gitignore`:
```
env.production
env.*.local
.env
*.env
```
:::

### Production Environment File

```bash
# env.production

# Django Configuration
DJANGO_SECRET_KEY=your-secret-key-here  # ⚠️ CHANGE THIS - Generate with: python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
DEBUG=false  # ⚠️ MUST be false in production
ALLOWED_HOSTS=localhost,127.0.0.1,your-domain.com  # ⚠️ Set to your actual domains
ENVIRONMENT=production

# Database Configuration
DATABASE_URL=postgresql://carapis:carapis_password@carapis_postgres:5432/carapis_db  # ⚠️ CHANGE PASSWORD
DATABASE_VEHICLES_URL=postgresql://carapis:carapis_password@carapis_postgres:5432/vehicles

# Redis Configuration
REDIS_URL=redis://carapis_redis:6379/0
REARQ_REDIS_DB=2

# ReArq Configuration
REARQ_WORKERS=2

# Logging Configuration
LOG_LEVEL=INFO
DJANGO_LOG_LEVEL=INFO

# Security Configuration
SECURE_SSL_REDIRECT=true  # ⚠️ Enable only if SSL/TLS is configured
SECURE_HSTS_SECONDS=31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS=true
SECURE_HSTS_PRELOAD=true

# Email Configuration (if using email features)
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=true
EMAIL_HOST_USER=your-email@gmail.com  # ⚠️ CHANGE THIS
EMAIL_HOST_PASSWORD=your-app-password  # ⚠️ Use app-specific password, not account password
```

:::warning[Configuration Best Practices]
**Required changes for production:**
1. ✅ Generate new `DJANGO_SECRET_KEY` (50+ characters)
2. ✅ Change all default passwords
3. ✅ Set `DEBUG=false`
4. ✅ Configure `ALLOWED_HOSTS` with actual domains
5. ✅ Enable SSL/TLS and set `SECURE_SSL_REDIRECT=true`
6. ✅ Use strong database passwords (16+ characters, mixed case, numbers, symbols)
7. ✅ Use app-specific passwords for email (not account passwords)

**Never use example values:**
- ❌ `carapis_password` - Example password
- ❌ `your-secret-key-here` - Placeholder
- ❌ `localhost` only in `ALLOWED_HOSTS` - Too permissive
:::

## Monitoring & Health Checks

### Health Check Endpoints

```bash
# Application health
curl http://localhost:8001/cfg/health/

# Database health
docker compose exec carapis_postgres pg_isready -U carapis

# Redis health
docker compose exec carapis_redis redis-cli ping

# Check all services
docker compose ps
```

### Log Monitoring

```bash
# View all logs
docker compose logs -f

# Specific service logs
docker compose logs -f carapis-django
docker compose logs -f carapis-rearq
docker compose logs -f carapis_postgres
docker compose logs -f carapis_redis

# Follow logs with timestamps
docker compose logs -f --timestamps
```

### Performance Monitoring

```bash
# Container resource usage
docker stats

# Redis memory usage
docker compose exec carapis_redis redis-cli info memory

# PostgreSQL connections
docker compose exec carapis_postgres psql -U carapis -d carapis_db -c "SELECT count(*) FROM pg_stat_activity;"

# ReArq queue status
docker compose exec carapis_redis redis-cli -n 2 LLEN rearq:queue:default
```

## Management Scripts

### Build and Run Script

```bash
#!/bin/bash
# scripts/build-and-run.sh

set -e

case "$1" in
    build)
        echo "🔨 Building Docker images..."
        docker compose build --no-cache
        echo "✅ Build completed!"
        ;;
    up)
        echo "🚀 Starting services..."
        docker compose up -d
        echo "⏳ Waiting for services to be healthy..."
        sleep 30
        docker compose ps
        echo "✅ Services started!"
        ;;
    down)
        echo "🛑 Stopping services..."
        docker compose down
        echo "✅ Services stopped!"
        ;;
    restart)
        echo "🔄 Restarting services..."
        docker compose down
        docker compose up -d
        echo "✅ Services restarted!"
        ;;
    logs)
        echo "📋 Showing logs..."
        docker compose logs -f
        ;;
    *)
        echo "Usage: $0 {build|up|down|restart|logs}"
        echo ""
        echo "Commands:"
        echo "  build    - Build all Docker images"
        echo "  up       - Start all services"
        echo "  down     - Stop all services"
        echo "  restart  - Restart all services"
        echo "  logs     - Show service logs"
        exit 1
        ;;
esac
```

### ReArq Debug Script

```bash
#!/bin/bash
# scripts/debug-rearq.sh

set -e

echo "🔍 Debugging ReArq integration..."

# Check if services are running
echo "📊 Service status:"
docker compose ps

# Check Redis connection
echo "🔗 Testing Redis connection..."
docker compose exec carapis_redis redis-cli ping

# Check task queue
echo "📋 Task queue status:"
docker compose exec carapis_redis redis-cli -n 2 LLEN rearq:queue:default

# Check worker logs
echo "📝 Recent worker logs:"
docker compose logs --tail=20 carapis-rearq

# Test document processing (if available)
if [ "$1" = "test_document" ]; then
    echo "🧪 Testing document processing..."
    docker compose exec carapis-django python manage.py shell -c "
from apps.knowbase.tasks.document_processing import process_document_async
print('Testing document processing task...')
# Add your test logic here
"
fi

echo "✅ Debug completed!"
```

## 🚨 Troubleshooting

### Common Issues

**Database Connection Issues:**
```bash
# Check PostgreSQL health
docker compose exec carapis_postgres pg_isready -U carapis

# View database logs
docker compose logs carapis_postgres

# Connect to database manually
docker compose exec carapis_postgres psql -U carapis -d carapis_db
```

**ReArq Worker Issues:**
```bash
# Check worker logs
docker compose logs -f carapis-rearq

# Restart workers
docker compose restart carapis-rearq

# Test task processing
./scripts/debug-rearq.sh test_document
```

**Performance Issues:**
```bash
# Check container resources
docker stats

# Monitor Redis memory
docker compose exec carapis_redis redis-cli info memory

# Check database connections
docker compose exec carapis_postgres psql -U carapis -d carapis_db -c "SELECT count(*) FROM pg_stat_activity;"
```

### Recovery Procedures

```bash
# Full system restart
docker compose down
docker compose build --no-cache
docker compose up -d

# Database reset (⚠️ DESTRUCTIVE)
docker compose down -v
docker compose up -d

# Clean Docker system
docker system prune -f
docker volume prune -f
```

:::danger[Destructive Operations Warning]
**The following commands permanently delete data:**

⚠️ **`docker compose down -v`**
- **Effect**: Deletes ALL Docker volumes
- **Loss**: Database data, uploaded files, logs
- **Recovery**: Only from backups
- **Use case**: Complete reset in development only

⚠️ **`docker volume prune -f`**
- **Effect**: Deletes all unused volumes
- **Loss**: Any data in unused volumes
- **Recovery**: Irreversible
- **Use case**: Cleanup after testing

⚠️ **`docker system prune -af`**
- **Effect**: Deletes containers, images, networks, volumes
- **Loss**: Everything not currently running
- **Recovery**: Must rebuild from scratch
- **Use case**: Complete cleanup (development only)

**Safe production procedure:**
1. ✅ Backup database first: `pg_dump`
2. ✅ Stop services: `docker compose stop`
3. ✅ Verify backups
4. ✅ Then perform restart
5. ✅ Test after restart

**Never run in production without backups!**
:::

## See Also

### Deployment & Infrastructure

**Docker Guides:**
- [**Docker Overview**](./overview) - Complete Docker guide
- [**Development Setup**](./development) - Local environment
- [**Configuration**](./configuration) - YAML + env vars strategy
- [**Build Optimization**](./build-optimization) - Performance tips
- [**Troubleshooting**](./troubleshooting) - Quick fixes

**Deployment:**
- [**Deployment Overview**](/deployment/overview) - All deployment options
- [**Logging Configuration**](/deployment/logging) - Production logging
- [**Production Config**](/guides/production-config) - Best practices
- [**Environment Detection**](/fundamentals/configuration/environment) - Multi-environment setup

**Infrastructure:**
- [**Database Configuration**](/fundamentals/database) - PostgreSQL and multi-database setup
- [**Cache Configuration**](/fundamentals/configuration/cache) - Redis configuration and caching
- [**Security Settings**](/fundamentals/configuration/security) - CORS, CSRF, SSL configuration

### Background Processing

**Task Processing:**
- [**ReArq Integration**](/features/integrations/django-rq/overview) - Background task processing
- [**Background Task Commands**](/features/integrations/django-rq/overview) - Manage workers via CLI
- [**Tasks App**](/features/built-in-apps/operations/tasks) - Built-in task management

### Configuration & Setup

**Getting Started:**
- [**Installation**](/getting-started/installation) - Install Django-CFG
- [**Configuration Guide**](/getting-started/configuration) - YAML configuration setup
- [**First Project**](/getting-started/first-project) - Quick start tutorial

**Production Configuration:**
- [**Configuration Models**](/fundamentals/configuration) - Complete config API
- [**Environment Variables**](/fundamentals/configuration/environment) - Secure secrets management
- [**Type-Safe Configuration**](/fundamentals/core/type-safety) - Pydantic patterns

### Tools & Guides

**CLI & Monitoring:**
- [**CLI Tools**](/cli/introduction) - Command-line interface
- [**Core Commands**](/cli/commands/core-commands) - Essential management commands
- [**Troubleshooting**](/guides/troubleshooting) - Common deployment issues

This Docker setup provides a robust, scalable foundation for Django-CFG applications! 🐳

TAGS: docker, production, postgresql, redis, rearq, nginx, deployment
DEPENDS_ON: [django-cfg, postgresql, redis, docker-compose]
USED_BY: [production-deployment, development, ci-cd]
