# 🐳 Django-CFG Example - Docker Setup

Complete Docker infrastructure for Django-CFG Example application with PostgreSQL, Redis, Django, and Dramatiq workers.

## 📦 Services

- **django_cfg_example_postgres** - PostgreSQL 16 database
- **django_cfg_example_redis** - Redis 7 cache & message broker
- **django_cfg_example_django** - Django application server
- **django_cfg_example_dramatiq** - Background task workers

## 🚀 Quick Start

### 1. Setup Environment

```bash
cd docker/
cp .env.example .env
# Edit .env if needed
```

### 2. Start All Services

```bash
# Build and start all services
docker compose up -d --build

# Or start without building
docker compose up -d
```

### 3. Check Status

```bash
# View all services
docker compose ps

# View logs
docker compose logs -f

# View specific service logs
docker compose logs -f django_cfg_example_django
```

### 4. Access Application

- **Django App**: http://localhost:8000
- **Admin Panel**: http://localhost:8000/admin/
- **API Docs**: http://localhost:8000/api/schema/swagger-ui/
- **Health Check**: http://localhost:8000/cfg/status/

## 🛠️ Common Commands

### Service Management

```bash
# Start all services
docker compose up -d

# Stop all services
docker compose down

# Restart all services
docker compose restart

# Restart specific service
docker compose restart django_cfg_example_django

# Rebuild and restart
docker compose up -d --build

# View logs (all services)
docker compose logs -f

# View logs (specific service)
docker compose logs -f django_cfg_example_django
docker compose logs -f django_cfg_example_dramatiq
```

### Django Operations

```bash
# Run migrations
docker compose exec django_cfg_example_django python manage.py migrate

# Create superuser
docker compose exec django_cfg_example_django python manage.py superuser

# Access Django shell
docker compose exec django_cfg_example_django python manage.py shell

# Show URLs
docker compose exec django_cfg_example_django python manage.py show_urls

# Collect static files
docker compose exec django_cfg_example_django python manage.py collectstatic

# Run custom command
docker compose exec django_cfg_example_django python manage.py <command>
```

### Database Operations

```bash
# Connect to PostgreSQL
docker compose exec django_cfg_example_postgres psql -U django_cfg_example -d django_cfg_example

# Backup database
docker compose exec django_cfg_example_postgres pg_dump -U django_cfg_example django_cfg_example > backup.sql

# Restore database
cat backup.sql | docker compose exec -T django_cfg_example_postgres psql -U django_cfg_example django_cfg_example

# Check database health
docker compose exec django_cfg_example_postgres pg_isready -U django_cfg_example
```

### Redis Operations

```bash
# Connect to Redis CLI
docker compose exec django_cfg_example_redis redis-cli

# Check Redis info
docker compose exec django_cfg_example_redis redis-cli INFO

# Flush all cache
docker compose exec django_cfg_example_redis redis-cli FLUSHALL

# Monitor Redis
docker compose exec django_cfg_example_redis redis-cli MONITOR
```

### Dramatiq Workers

```bash
# View worker logs
docker compose logs -f django_cfg_example_dramatiq

# Check task status
docker compose exec django_cfg_example_django python manage.py task_status

# Clear task queue
docker compose exec django_cfg_example_django python manage.py task_clear

# Restart workers
docker compose restart django_cfg_example_dramatiq
```

### Debugging

```bash
# Access container shell
docker compose exec django_cfg_example_django bash

# View container logs
docker compose logs -f django_cfg_example_django

# Check container health
docker compose ps

# Inspect container
docker inspect django_cfg_example_django

# View resource usage
docker compose stats
```

## 📁 Project Structure

```
docker/
├── docker-compose.yml                # Main compose file (includes)
├── docker-compose.services.yml       # All services definition
├── Dockerfile.django                 # Django app Dockerfile
├── .env.example                      # Environment template
├── README.md                         # This file
│
├── postgres/
│   ├── Dockerfile                    # PostgreSQL Dockerfile
│   └── init-db.sh                    # Database initialization
│
├── redis/
│   ├── Dockerfile                    # Redis Dockerfile
│   └── redis.conf                    # Redis configuration
│
├── scripts/
│   └── entrypoint.sh                 # Django entrypoint script
│
└── volumes/                          # Persistent data (gitignored)
    ├── postgres/data/                # PostgreSQL data
    ├── redis/data/                   # Redis data
    └── django/
        ├── logs/                     # Application logs
        ├── static/                   # Static files
        └── media/                    # Media files
```

## 🔧 Configuration

### Environment Variables

See `.env.example` for all available options.

Key variables:
- `DEBUG` - Enable/disable debug mode
- `SECRET_KEY` - Django secret key (change in production!)
- `DATABASE_URL` - Database connection (auto-configured)
- `REDIS_URL` - Redis connection (auto-configured)
- `PORT` - Application port (default: 8000)

### Volumes

Persistent data stored in `./volumes/`:
- `volumes/postgres/data/` - PostgreSQL database
- `volumes/redis/data/` - Redis persistence
- `volumes/django/logs/` - Application logs
- `volumes/django/static/` - Static files
- `volumes/django/media/` - User uploads

## 🏗️ Architecture

```
┌─────────────────────────────────────┐
│    django_cfg_example_django        │
│    Django Application (Port 8000)   │
│  - REST API                         │
│  - Admin Panel                      │
│  - Background Task Submission       │
└────────┬────────────────────────────┘
         │
         ├──────────┐
         │          │
┌────────▼─────┐ ┌──▼──────────────────┐
│  PostgreSQL  │ │      Redis          │
│  (Port 5432) │ │   (Port 6379)       │
│   Database   │ │  Cache + Broker     │
└──────────────┘ └──────┬──────────────┘
                        │
               ┌────────▼────────────────┐
               │  django_cfg_example_    │
               │      dramatiq           │
               │  Background Workers     │
               └─────────────────────────┘
```

## 🧪 Testing

```bash
# Run tests inside container
docker compose exec django_cfg_example_django python manage.py test

# Run specific test
docker compose exec django_cfg_example_django python manage.py test apps.blog

# Run with coverage
docker compose exec django_cfg_example_django pytest --cov
```

## 🔍 Troubleshooting

### Container Won't Start

```bash
# Check logs
docker compose logs django_cfg_example_django

# Check health status
docker compose ps

# Rebuild from scratch
docker compose down -v
docker compose up -d --build
```

### Database Connection Issues

```bash
# Check PostgreSQL health
docker compose exec django_cfg_example_postgres pg_isready -U django_cfg_example

# View database logs
docker compose logs django_cfg_example_postgres

# Restart database
docker compose restart django_cfg_example_postgres
```

### Port Conflicts

If ports are already in use, edit `.env`:

```env
# Change to available port
PORT=8001
```

Or edit `docker-compose.services.yml` to change port mappings.

### Clear Everything and Start Fresh

```bash
# Stop and remove all containers, volumes, networks
docker compose down -v

# Remove images (optional)
docker compose down -v --rmi all

# Start fresh
docker compose up -d --build
```

## 🚀 Production Deployment

### Security Checklist

1. ✅ Change `SECRET_KEY` to random value
2. ✅ Set `DEBUG=False`
3. ✅ Configure proper `ALLOWED_HOSTS`
4. ✅ Use strong database password
5. ✅ Remove exposed ports in production
6. ✅ Use HTTPS (via reverse proxy)
7. ✅ Set up backups for volumes
8. ✅ Configure proper logging

### Using with Traefik

This setup can be integrated with Traefik reverse proxy. See root `docker/` directory for Traefik configuration.

## 📚 See Also

- [Django-CFG Documentation](/)
- [Docker Documentation](https://docs.docker.com)
- [PostgreSQL Docker Hub](https://hub.docker.com/_/postgres)
- [Redis Docker Hub](https://hub.docker.com/_/redis)

---

**Ready to start!** Run:
```bash
cd docker && docker compose up -d --build
```
