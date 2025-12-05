# Docker Deployment Guide

Deploy your Django-CFG project with Docker.

## Directory Structure

```
docker/
├── .env.local                    # Local environment
├── .env.production               # Production environment
├── docker-compose-local.yaml     # Local development
├── docker-compose-production.yaml # Production deployment
└── services/
    ├── django/
    │   └── Dockerfile
    ├── centrifugo/
    │   └── config.json
    └── nginx/
        └── nginx.conf
```

## Local Development

### 1. Configure Environment

```bash
cd docker
cp .env.local.example .env.local
nano .env.local
```

### 2. Start Services

```bash
docker-compose -f docker-compose-local.yaml up -d
```

### 3. Access Services

| Service | URL |
|---------|-----|
| Django API | http://localhost:7301 |
| Admin Panel | http://localhost:7301/admin/ |
| API Docs | http://localhost:7301/api/docs/ |
| Centrifugo | ws://localhost:8120 |
| Redis | localhost:6379 |
| PostgreSQL | localhost:5432 |

### 4. View Logs

```bash
docker-compose -f docker-compose-local.yaml logs -f django
```

### 5. Stop Services

```bash
docker-compose -f docker-compose-local.yaml down
```

## Production Deployment

### 1. Configure Environment

```bash
cp .env.production.example .env.production
nano .env.production
```

**Required settings:**

```env
# Security
SECRET_KEY=your-production-secret-key
DEBUG=false

# Database
DATABASE_URL=postgresql://user:password@db:5432/prod_db

# Domain
ALLOWED_HOSTS=yourdomain.com,api.yourdomain.com
CSRF_TRUSTED_ORIGINS=https://yourdomain.com
```

### 2. Build and Start

```bash
docker-compose -f docker-compose-production.yaml up -d --build
```

### 3. Run Migrations

```bash
docker-compose -f docker-compose-production.yaml exec django python manage.py migrate
```

### 4. Create Superuser

```bash
docker-compose -f docker-compose-production.yaml exec django python manage.py superuser
```

### 5. Collect Static Files

```bash
docker-compose -f docker-compose-production.yaml exec django python manage.py collectstatic --noinput
```

## Services

### Django

The main application container.

```yaml
django:
  build: ./services/django
  environment:
    - DATABASE_URL=${DATABASE_URL}
    - SECRET_KEY=${SECRET_KEY}
  ports:
    - "7301:8000"
```

### PostgreSQL

Database server.

```yaml
postgres:
  image: postgres:16-alpine
  environment:
    - POSTGRES_USER=${DB_USER}
    - POSTGRES_PASSWORD=${DB_PASSWORD}
    - POSTGRES_DB=${DB_NAME}
  volumes:
    - postgres_data:/var/lib/postgresql/data
```

### Redis

Cache and task queue.

```yaml
redis:
  image: redis:7-alpine
  ports:
    - "6379:6379"
```

### Centrifugo

Real-time WebSocket server.

```yaml
centrifugo:
  image: centrifugo/centrifugo:v5
  command: centrifugo -c config.json
  ports:
    - "8120:8000"
```

### Nginx

Reverse proxy (production).

```yaml
nginx:
  image: nginx:alpine
  ports:
    - "80:80"
    - "443:443"
  volumes:
    - ./services/nginx/nginx.conf:/etc/nginx/nginx.conf
```

## Common Commands

```bash
# View all containers
docker-compose -f docker-compose-local.yaml ps

# Restart specific service
docker-compose -f docker-compose-local.yaml restart django

# Shell into container
docker-compose -f docker-compose-local.yaml exec django bash

# Run management command
docker-compose -f docker-compose-local.yaml exec django python manage.py <command>

# View resource usage
docker stats

# Clean up unused images
docker system prune -a
```

## Backup Database

```bash
# Backup
docker-compose -f docker-compose-local.yaml exec postgres pg_dump -U user dbname > backup.sql

# Restore
docker-compose -f docker-compose-local.yaml exec -T postgres psql -U user dbname < backup.sql
```

## SSL/TLS (Production)

For production, use Let's Encrypt with certbot or a reverse proxy like Traefik.

Example with Nginx:

```nginx
server {
    listen 443 ssl;
    server_name yourdomain.com;

    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;

    location / {
        proxy_pass http://django:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## Troubleshooting

### Container Won't Start

```bash
# Check logs
docker-compose -f docker-compose-local.yaml logs django

# Check container status
docker-compose -f docker-compose-local.yaml ps
```

### Database Connection Error

Ensure PostgreSQL is running and healthy:

```bash
docker-compose -f docker-compose-local.yaml exec postgres pg_isready
```

### Permission Denied

```bash
# Fix volume permissions
sudo chown -R $USER:$USER ./volumes
```

## More Information

Full documentation: https://djangocfg.com/docs/deployment
