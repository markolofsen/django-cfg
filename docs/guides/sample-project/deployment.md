---
title: Deployment Guide
description: Production deployment with Docker and best practices for Django-CFG sample project
sidebar_label: Deployment
sidebar_position: 10
---

# Deployment Guide

The Django-CFG sample project includes production-ready Docker configuration and deployment best practices. This guide covers Docker setup, environment configuration, and deployment procedures.

## Docker Setup

### Dockerfile

Production-ready Dockerfile:

```dockerfile
# Dockerfile
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DJANGO_SETTINGS_MODULE=api.settings

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Create app directory
WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . .

# Collect static files
RUN python manage.py collectstatic --noinput

# Create non-root user
RUN adduser --disabled-password --gecos '' appuser
RUN chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/cfg/status/ || exit 1

# Start application
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "api.wsgi:application"]
```

### Docker Compose

Multi-container setup with Docker Compose:

```yaml
# docker-compose.yml
version: '3.8'

services:
  web:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DJANGO_SETTINGS_MODULE=api.settings
      - IS_PROD=true
    volumes:
      - ./media:/app/media
      - ./static:/app/static
    depends_on:
      - db
      - redis
    command: gunicorn --bind 0.0.0.0:8000 --workers 4 api.wsgi:application

  db:
    image: postgres:15
    environment:
      POSTGRES_DB: djangocfg_sample
      POSTGRES_USER: djangocfg
      POSTGRES_PASSWORD: secure_password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data
    ports:
      - "6379:6379"

  rearq:
    build: .
    command: rearq main:rearq worker
    environment:
      - DJANGO_SETTINGS_MODULE=api.settings
      - IS_PROD=true
    depends_on:
      - db
      - redis
    volumes:
      - ./media:/app/media

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./docker/nginx/nginx.conf:/etc/nginx/nginx.conf
      - ./static:/app/static
      - ./media:/app/media
      - ./docker/nginx/ssl:/etc/nginx/ssl
    depends_on:
      - web

volumes:
  postgres_data:
  redis_data:
```

### Nginx Configuration

Nginx as reverse proxy:

```nginx
# docker/nginx/nginx.conf
upstream django {
    server web:8000;
}

server {
    listen 80;
    server_name myapp.com www.myapp.com;

    # Redirect HTTP to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name myapp.com www.myapp.com;

    # SSL configuration
    ssl_certificate /etc/nginx/ssl/cert.pem;
    ssl_certificate_key /etc/nginx/ssl/key.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;

    # Security headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-Frame-Options "DENY" always;
    add_header X-XSS-Protection "1; mode=block" always;

    # Max upload size
    client_max_body_size 50M;

    # Static files
    location /static/ {
        alias /app/static/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    # Media files
    location /media/ {
        alias /app/media/;
        expires 7d;
        add_header Cache-Control "public";
    }

    # Django application
    location / {
        proxy_pass http://django;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_redirect off;
    }
}
```

## Production Configuration

### Environment Variables

Set production environment variables:

```bash
# .env.production
SECRET_KEY=your-super-secret-key-change-in-production
DEBUG=false
DJANGO_ENV=prod
IS_PROD=true

# Database
DATABASE_URL=postgresql://user:password@db:5432/djangocfg_sample
DB_HOST=db
DB_PORT=5432
DB_NAME=djangocfg_sample
DB_USER=djangocfg
DB_PASSWORD=secure_password

# Redis
REDIS_URL=redis://redis:6379/0

# Email (SendGrid)
SENDGRID_API_KEY=SG.xxxxxxxxxxxxx
EMAIL_FROM=noreply@myapp.com

# Twilio
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=your-auth-token
TWILIO_VERIFY_SERVICE_SID=VAxxxxxxxxxxxxx
TWILIO_PHONE_NUMBER=+1234567890

# Telegram
TELEGRAM_BOT_TOKEN=123456:ABC-DEF
TELEGRAM_CHAT_ID=@your_channel

# Domain
DOMAIN=myapp.com
ALLOWED_HOSTS=myapp.com,www.myapp.com

# Security (SSL handled by nginx reverse proxy)
# SECURE_SSL_REDIRECT not needed - Django-CFG defaults to reverse proxy mode
SESSION_COOKIE_SECURE=true
CSRF_COOKIE_SECURE=true
```

### Production YAML Configuration

```yaml
# api/environment/config.prod.yaml
secret_key: "<from-yaml-config>"  # Loaded from environment
debug: false
is_prod: true

# Database configuration
database:
  url: "postgresql://${DB_USER}:${DB_PASSWORD}@${DB_HOST}:${DB_PORT}/${DB_NAME}"

# Application settings
app:
  name: "Django CFG Sample"
  domain: "${DOMAIN}"

security_domains: ["${DOMAIN}", "www.${DOMAIN}"]

# Email configuration
email:
  sendgrid_api_key: "${SENDGRID_API_KEY}"
  from_email: "${EMAIL_FROM}"

# Twilio configuration
twilio:
  account_sid: "${TWILIO_ACCOUNT_SID}"
  auth_token: "${TWILIO_AUTH_TOKEN}"
  verify_service_sid: "${TWILIO_VERIFY_SERVICE_SID}"
  phone_number: "${TWILIO_PHONE_NUMBER}"

# Telegram configuration
telegram:
  bot_token: "${TELEGRAM_BOT_TOKEN}"
  chat_id: "${TELEGRAM_CHAT_ID}"

# Cache configuration (Redis)
cache:
  backend: "django_redis.cache.RedisCache"
  location: "${REDIS_URL}"

# Static files (served by nginx)
static:
  url: "/static/"
  root: "/app/static/"

# Media files (served by nginx)
media:
  url: "/media/"
  root: "/app/media/"

# Security settings
# Note: SSL/TLS handled by nginx reverse proxy
# secure_ssl_redirect not needed - Django-CFG defaults to reverse proxy mode
security:
  session_cookie_secure: true
  csrf_cookie_secure: true
  secure_browser_xss_filter: true
  secure_content_type_nosniff: true
  secure_hsts_seconds: 31536000

# Logging
logging:
  level: "INFO"
  format: "json"
```

See [Configuration](./configuration) for complete configuration details.

## Deployment Procedures

### Initial Deployment

Deploy for the first time:

```bash
# 1. Clone repository
git clone https://github.com/yourusername/myapp.git
cd myapp

# 2. Set environment variables
cp .env.production .env
# Edit .env with your production values

# 3. Build and start containers
docker-compose up -d --build

# 4. Run migrations
docker-compose exec web python manage.py migrate

# 5. Create superuser
docker-compose exec web python manage.py createsuperuser

# 6. Collect static files
docker-compose exec web python manage.py collectstatic --noinput

# 7. Check status
docker-compose ps
curl http://localhost/cfg/status/
```

### Updating Deployment

Deploy updates:

```bash
# 1. Pull latest code
git pull origin main

# 2. Rebuild containers
docker-compose up -d --build

# 3. Run new migrations
docker-compose exec web python manage.py migrate

# 4. Collect static files
docker-compose exec web python manage.py collectstatic --noinput

# 5. Restart services
docker-compose restart web rearq

# 6. Verify deployment
curl http://localhost/cfg/status/
```

### Zero-Downtime Deployment

Deploy without downtime:

```bash
# 1. Build new image
docker-compose build web

# 2. Start new containers
docker-compose up -d --scale web=2 --no-recreate

# 3. Run migrations
docker-compose exec web python manage.py migrate

# 4. Stop old containers
docker-compose stop old_web

# 5. Remove old containers
docker-compose rm -f old_web

# 6. Scale back to 1
docker-compose up -d --scale web=1
```

## Database Management

### Database Backup

Backup PostgreSQL database:

```bash
# Manual backup
docker-compose exec db pg_dump -U djangocfg djangocfg_sample > backup.sql

# Automated backup script
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="backup_${DATE}.sql"

docker-compose exec -T db pg_dump -U djangocfg djangocfg_sample > $BACKUP_FILE

# Upload to S3
aws s3 cp $BACKUP_FILE s3://myapp-backups/

# Keep only last 30 days
find . -name "backup_*.sql" -mtime +30 -delete
```

### Database Restore

Restore from backup:

```bash
# Restore from backup file
docker-compose exec -T db psql -U djangocfg djangocfg_sample < backup.sql

# Restore from S3
aws s3 cp s3://myapp-backups/backup_20231201_120000.sql - | \
  docker-compose exec -T db psql -U djangocfg djangocfg_sample
```

### Running Migrations

```bash
# Run all migrations
docker-compose exec web python manage.py migrate

# Run specific app migrations
docker-compose exec web python manage.py migrate blog

# Show migration status
docker-compose exec web python manage.py showmigrations

# Create new migrations
docker-compose exec web python manage.py makemigrations
```

## Monitoring

### Health Checks

Monitor application health:

```bash
# Check health endpoint
curl http://localhost/cfg/status/

# Response
{
  "status": "healthy",
  "checks": {
    "database": {"status": "healthy"},
    "cache": {"status": "healthy"},
    "email": {"status": "healthy"}
  }
}
```

### Log Monitoring

View application logs:

```bash
# View all logs
docker-compose logs -f

# View specific service
docker-compose logs -f web
docker-compose logs -f rearq

# View last 100 lines
docker-compose logs --tail=100 web
```

### Container Monitoring

Monitor container resources:

```bash
# View container stats
docker stats

# View specific service
docker stats djangocfg_web_1

# View disk usage
docker system df
```

## Security Best Practices

### 1. Secure Secret Keys

```bash
# ✅ Good: Environment variable
SECRET_KEY=$(openssl rand -hex 50)

# ❌ Bad: Hard-coded in code
SECRET_KEY = "insecure-key"
```

### 2. Use HTTPS

```nginx
# ✅ Good: Redirect HTTP to HTTPS
return 301 https://$server_name$request_uri;

# ❌ Bad: Allow HTTP
listen 80;
```

### 3. Set Security Headers

```nginx
# ✅ Good: Security headers
add_header Strict-Transport-Security "max-age=31536000";
add_header X-Content-Type-Options "nosniff";
add_header X-Frame-Options "DENY";
```

### 4. Limit File Upload Size

```nginx
# ✅ Good: Limit upload size
client_max_body_size 50M;

# ❌ Bad: Unlimited uploads
```

### 5. Run as Non-Root User

```dockerfile
# ✅ Good: Non-root user
USER appuser

# ❌ Bad: Run as root
USER root
```

## Performance Optimization

### Gunicorn Workers

Optimize worker count:

```bash
# Formula: (2 * CPU_CORES) + 1
# For 2 CPU cores: 5 workers
gunicorn --workers 5 --bind 0.0.0.0:8000 api.wsgi:application
```

### Database Connection Pooling

Configure connection pooling:

```python
# api/config.py
databases: Dict[str, DatabaseConfig] = {
    "default": DatabaseConfig(
        engine="django.db.backends.postgresql",
        name=env.database.name,
        user=env.database.user,
        password=env.database.password,
        host=env.database.host,
        port=env.database.port,
        options={
            "connect_timeout": 10,
            "options": "-c statement_timeout=30000",
            "pool_size": 20,
            "max_overflow": 0,
        }
    ),
}
```

### Redis Caching

Enable Redis caching:

```python
# api/config.py
cache: CacheConfig = CacheConfig(
    backend="django_redis.cache.RedisCache",
    location=env.redis.url,
    options={
        "CLIENT_CLASS": "django_redis.client.DefaultClient",
        "CONNECTION_POOL_KWARGS": {
            "max_connections": 50,
            "retry_on_timeout": True,
        },
    }
)
```

## Deployment Checklist

Before deploying to production:

- [ ] Set `DEBUG=false`
- [ ] Generate secure `SECRET_KEY`
- [ ] Configure allowed hosts
- [ ] Set up SSL/HTTPS
- [ ] Configure production database
- [ ] Set up Redis for caching
- [ ] Configure email service (SendGrid)
- [ ] Set up Twilio for SMS
- [ ] Configure Telegram notifications
- [ ] Enable security headers
- [ ] Set up automated backups
- [ ] Configure log aggregation
- [ ] Set up monitoring/alerts
- [ ] Test health checks
- [ ] Run security audit
- [ ] Document deployment process

## Troubleshooting

### Container Won't Start

```bash
# Check logs
docker-compose logs web

# Check container status
docker-compose ps

# Rebuild container
docker-compose up -d --build --force-recreate web
```

### Database Connection Issues

```bash
# Check database is running
docker-compose ps db

# Test database connection
docker-compose exec db psql -U djangocfg djangocfg_sample

# Check environment variables
docker-compose exec web env | grep DB_
```

### Static Files Not Loading

```bash
# Collect static files
docker-compose exec web python manage.py collectstatic --noinput

# Check nginx logs
docker-compose logs nginx

# Verify static file path
docker-compose exec web ls -la /app/static/
```

## Related Topics

- [Configuration](./configuration) - Production configuration setup
- [Multi-Database Setup](./multi-database) - Database deployment
- [Service Integrations](./service-integrations) - External service configuration
- [Background Tasks](/features/integrations/rearq/overview) - Worker deployment

Proper deployment ensures your Django-CFG application runs reliably in production!
