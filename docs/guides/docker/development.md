---
title: Docker Development Setup
description: Set up Django-CFG development environment with Docker Compose. Complete guide with service configuration, common tasks, and troubleshooting.
sidebar_label: Development
sidebar_position: 2
keywords:
  - django-cfg docker development
  - docker compose django development
  - local docker setup django
  - django docker dev environment
---

# Docker Development Setup

> **📚 Part of**: [Docker Guide](./overview) - Return to Docker overview

Complete guide for running Django-CFG in local development with Docker Compose.

---

## Quick Start

```bash
# Navigate to docker directory
cd docker

# Start all services
docker compose up -d

# Check status
docker compose ps

# View logs
docker compose logs -f
```

All services should be healthy in ~60 seconds.

---

## Project Structure

```
docker/
├── docker-compose.yaml              # Main compose file
├── .env                            # Environment variables
├── .dockerignore                   # Build context exclusions
│
├── services/                        # Service-specific configs
│   ├── django/
│   │   ├── Dockerfile              # Django application
│   │   ├── entrypoint.sh          # Container startup
│   │   ├── config.dev.ignore.yaml # Dev API keys (in git!)
│   │   └── config.prod.ignore.yaml# Prod API keys (in git!)
│   ├── demo/Dockerfile            # Next.js demo app
│   ├── websocket/Dockerfile       # WebSocket RPC server
│   ├── web/Dockerfile             # Nuxt.js docs site
│   └── postgres/init.sql          # DB initialization
│
├── volumes/                         # Persistent data (git-ignored)
│   ├── postgres/                  # Database files
│   ├── django/media/              # User uploads
│   └── django/logs/               # Application logs
│
└── @docs/                           # Documentation
    ├── README.md                   # Complete reference
    ├── CONFIG_STRATEGY.md         # Configuration guide
    ├── DOCKER_BUILD_LESSONS.md    # Build optimization
    └── QUICK_REFERENCE.md         # Command reference
```

---

## Service Configuration

### Infrastructure Services

#### PostgreSQL Database

**Port**: `5432` (internal)
**Databases**: `djangocfg` (main)
**Extensions**: `uuid-ossp`, `pg_trgm`, `vector` (pgvector)

```yaml
postgres:
  image: pgvector/pgvector:pg15
  environment:
    POSTGRES_DB: djangocfg
    POSTGRES_USER: postgres
    POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
  healthcheck:
    test: ["CMD-SHELL", "pg_isready -U postgres -d djangocfg"]
    interval: 10s
```

**Environment variable**:
```bash
DATABASE_URL=postgresql://postgres:password@postgres:5432/djangocfg
```

#### Redis Cache & Queue

**Port**: `6379` (internal)
**Databases**:
- DB 0: Django cache
- DB 1: Dramatiq task queue
- DB 2: Centrifugo broker

```yaml
redis:
  image: redis:7-alpine
  command: >
    redis-server
    --maxmemory 512mb
    --maxmemory-policy allkeys-lru
    --databases 3
```

**Environment variables**:
```bash
REDIS_URL=redis://redis:6379/0
REDIS_DRAMATIQ_URL=redis://redis:6379/1
```

---

### Backend Services

#### Django API

**Port**: `8300:8000`
**Access**: http://localhost:8300

```yaml
django:
  build:
    context: ..
    dockerfile: docker/services/django/Dockerfile
  environment:
    DJANGO_SETTINGS_MODULE: api.settings
    DATABASE_URL: postgresql://postgres:${POSTGRES_PASSWORD}@postgres:5432/djangocfg
    REDIS_URL: redis://redis:6379/0
  healthcheck:
    test: ["CMD", "curl", "-f", "http://localhost:8000/cfg/health/"]
    interval: 30s
```

**Key features**:
- Auto-runs migrations on startup
- Health check endpoint at `/cfg/health/`
- Volume-mounted media files
- Hot-reload enabled

#### Django Dramatiq Workers

**Container**: `django-dramatiq`
**Purpose**: Background task processing

```yaml
django-dramatiq:
  image: djangocfg-django:latest
  environment:
    SKIP_MIGRATIONS: "true"
    DRAMATIQ_PROCESSES: 2
    DRAMATIQ_THREADS: 4
  command: ["/entrypoint.sh", "python", "manage.py", "rundramatiq"]
  depends_on:
    django:
      condition: service_healthy
```

**Configuration**:
- `DRAMATIQ_PROCESSES`: Number of worker processes (default: 2)
- `DRAMATIQ_THREADS`: Threads per process (default: 4)
- Skips migrations (handled by main Django service)

#### WebSocket RPC Server

**Ports**:
- `9065`: WebSocket connections
- `9066`: Health check

**Access**: ws://localhost:9065

```yaml
websocket:
  environment:
    WS_HOST: 0.0.0.0
    WS_PORT: 9065
    HEALTH_PORT: 9066
    REDIS_URL: redis://redis:6379/2
    JWT_SECRET: ${JWT_SECRET}
```

---

### Frontend Services

#### Demo Application (Next.js)

**Port**: `3300`
**Access**: http://localhost:3300

Built with Next.js standalone output for minimal image size.

#### Documentation Site (Nuxt.js)

**Port**: `3301`
**Access**: http://localhost:3301

This documentation site you're reading now!

---

### Traefik Reverse Proxy

**Dashboard**: http://localhost:8390
**HTTP**: Port `380`
**HTTPS**: Port `743`

**Routes**:
- `api.localhost:380` → Django API
- `demo.localhost:380` → Demo app
- `ws.localhost:380` → WebSocket

:::tip[Access via Traefik]
For a production-like experience, access services through Traefik:
```
http://api.localhost:380/admin/
http://demo.localhost:380
```
:::

---

## Common Development Tasks

### Django Management

```bash
# Run migrations
docker exec django python manage.py migrate

# Create superuser
docker exec -it django python manage.py createsuperuser

# Django shell
docker exec -it django python manage.py shell

# Collect static files (if needed)
docker exec django python manage.py collectstatic --noinput

# Custom management command
docker exec django python manage.py your_command
```

### Database Operations

```bash
# Access PostgreSQL shell
docker exec -it djangocfg_postgres psql -U postgres -d djangocfg

# Run SQL query
docker exec djangocfg_postgres psql -U postgres -d djangocfg -c "SELECT * FROM django_migrations LIMIT 5;"

# Backup database
docker exec djangocfg_postgres pg_dump -U postgres djangocfg > backup.sql

# Restore database
docker exec -i djangocfg_postgres psql -U postgres djangocfg < backup.sql

# Reset database (⚠️ DESTRUCTIVE)
docker exec djangocfg_postgres psql -U postgres -c "DROP DATABASE djangocfg;"
docker exec djangocfg_postgres psql -U postgres -c "CREATE DATABASE djangocfg;"
docker exec django python manage.py migrate
```

### View Logs

```bash
# All services
docker compose logs -f

# Specific service
docker compose logs -f django

# Last 50 lines
docker compose logs --tail=50 django

# With timestamps
docker compose logs -f --timestamps django
```

### Service Management

```bash
# Restart single service
docker compose restart django

# Stop all services
docker compose stop

# Start all services
docker compose start

# Remove all services (keeps volumes)
docker compose down

# Remove all including volumes (⚠️ DELETES DATA)
docker compose down -v
```

### Rebuild After Changes

```bash
# Rebuild single service
docker compose build django --no-cache
docker compose up -d django

# Rebuild all services
docker compose build --no-cache
docker compose up -d

# Force recreate containers
docker compose up -d --force-recreate
```

---

## Configuration

### Environment Variables

Edit `docker/.env`:

```bash
# Database
POSTGRES_DB=djangocfg
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_password_here

# Django
DJANGO_SECRET_KEY=your-secret-key-here
DJANGO_DEBUG=true

# Dramatiq
DRAMATIQ_PROCESSES=2
DRAMATIQ_THREADS=4

# API Keys (optional)
ANTHROPIC_API_KEY=sk-ant-your-key
OPENAI_API_KEY=sk-proj-your-key

# JWT
JWT_SECRET_KEY=your-jwt-secret-here
```

### YAML Configuration Files

Django-CFG uses YAML files for detailed configuration:

**For Docker development** (team-shared API keys):
```yaml
# docker/services/django/config.dev.ignore.yaml
api_keys:
  openai: "sk-proj-your-team-key"
  anthropic: "sk-ant-your-team-key"

email:
  backend: "smtp"
  host: "mail.example.com"
  username: "dev@example.com"
  password: "smtp-password"
```

:::info[Why .ignore.yaml in Git?]
Docker configs with team-shared API keys are intentionally committed:
- `docker/services/django/*.ignore.yaml` - Team configs (in git)
- `projects/django/api/environment/*.ignore.yaml` - Personal (git-ignored)

See [Configuration Strategy](./configuration) for details.
:::

---

## Service Access

| Service | URL | Credentials |
|---------|-----|-------------|
| Django Admin | http://localhost:8300/admin/ | Create with `createsuperuser` |
| Django API | http://localhost:8300 | - |
| API via Traefik | http://api.localhost:380 | - |
| Demo App | http://localhost:3300 | - |
| Demo via Traefik | http://demo.localhost:380 | - |
| Documentation | http://localhost:3301 | - |
| Traefik Dashboard | http://localhost:8390 | - |
| PostgreSQL | localhost:5432 | postgres / (from .env) |
| Redis | localhost:6379 | No password |

---

## Troubleshooting

### Services Won't Start

**Check logs**:
```bash
docker compose logs django
docker compose ps
```

**Common issues**:
- Ports already in use → Change ports in docker-compose.yaml
- Previous containers running → `docker compose down`
- Build cache issues → `docker compose build --no-cache`

### Configuration Not Loading

**Check which config is loaded**:
```bash
docker exec django python -c "from api.environment.loader import env; print(env.env.env_mode)"
# Should output: development
```

**Verify config file exists**:
```bash
docker exec django ls -la /app/api/environment/
```

### Database Connection Failed

**Check database is healthy**:
```bash
docker compose ps djangocfg_postgres
docker exec djangocfg_postgres pg_isready -U postgres
```

**Test connection**:
```bash
docker exec django python manage.py check --database default
```

### Port Already in Use

**Find process using port**:
```bash
lsof -i :8300
```

**Kill process**:
```bash
kill -9 <PID>
```

**Or change port** in `docker-compose.yaml`:
```yaml
ports:
  - "8301:8000"  # Changed from 8300
```

### Volume Permission Errors

**Fix permissions**:
```bash
sudo chown -R $USER:$USER docker/volumes/
```

---

## Performance Tips

### Optimize Build Speed

1. **Use .dockerignore** - Already configured
2. **Layer caching** - Don't change Dockerfile often
3. **BuildKit** - Enable with `DOCKER_BUILDKIT=1`

### Reduce Container Size

Images are optimized with multi-stage builds:
- Django: ~300MB
- Next.js demo: ~300MB (with standalone output)
- Nuxt.js docs: ~200MB

See [Build Optimization](./build-optimization) for details.

### Improve Runtime Performance

```yaml
# Increase worker threads
DRAMATIQ_PROCESSES=4
DRAMATIQ_THREADS=8

# Increase Redis memory
redis:
  command: redis-server --maxmemory 1gb
```

---

## Next Steps

**Production Deployment**:
[Production Docker Setup →](./production)

**Configuration Deep Dive**:
[Configuration Strategy →](./configuration)

**Build Optimization**:
[Build Optimization Guide →](./build-optimization)

**Common Issues**:
[Troubleshooting Guide →](./troubleshooting)

---

## See Also

### Docker Guides
- **[Docker Overview](./overview)** - Complete Docker guide
- **[Production Setup](./production)** - Deploy to production
- **[Configuration](./configuration)** - YAML + env vars strategy
- **[Build Optimization](./build-optimization)** - Performance tips
- **[Troubleshooting](./troubleshooting)** - Quick fixes

### Configuration
- **[Database Configuration](/fundamentals/configuration/database)** - PostgreSQL setup
- **[Cache Configuration](/fundamentals/configuration/cache)** - Redis setup
- **[Environment Variables](/fundamentals/configuration/environment)** - Env vars

### Getting Started
- **[First Project](/getting-started/first-project)** - Create your first app
- **[Installation](/getting-started/installation)** - Install Django-CFG
- **[Configuration Guide](/getting-started/configuration)** - Basic setup

---

TAGS: docker, development, docker-compose, local-setup
DEPENDS_ON: [docker, docker-compose, postgresql, redis]
USED_BY: [development, testing, local-environment]
