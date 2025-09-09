# 🐳 UnrealOS Django - Docker Infrastructure

This directory contains modular Docker configuration for the UnrealOS Django CFG Sample Project.

## 📁 Modular Structure

Проект использует модульную архитектуру Docker Compose с разделением на отдельные файлы:

```
docker/
├── config/                        # Configuration files
│   └── nginx.conf                # Nginx configuration
├── postgres/                      # PostgreSQL database
│   └── default/
│       ├── Dockerfile            # PostgreSQL custom image
│       └── init-db.sh            # Database initialization script
├── redis/                         # Redis cache
│   └── default/
│       ├── Dockerfile            # Redis custom image
│       └── redis.conf            # Redis configuration
├── scripts/                       # Startup scripts
│   └── entrypoint.sh             # Application entrypoint
├── volumes/                       # Shared volumes
│   ├── postgres/                 # PostgreSQL data
│   ├── redis/                    # Redis data
│   └── django/                   # Django data
├── docker-compose.yml            # Центральный файл с includes
├── docker-compose.services.yml   # Основные сервисы (PostgreSQL + Django)
├── docker-compose.nginx.yml      # Nginx reverse proxy
├── env.production                # Production environment variables
└── README.md                     # This file
```

## 🚀 Quick Start

### Модульный запуск

```bash
# Запуск всех сервисов (через центральный файл)
docker compose up -d

# Запуск только основных сервисов (PostgreSQL + Django)
docker compose -f docker-compose.services.yml up -d

# Запуск только Nginx
docker compose -f docker-compose.nginx.yml up -d

# Просмотр логов
docker compose logs -f django

# Остановка всех сервисов
docker compose down
```

### Production Environment

```bash
# Запуск production окружения
docker compose up -d --build

# Или поэтапно:
# 1. Сначала основные сервисы
docker compose -f docker-compose.services.yml up -d
# 2. Затем Nginx
docker compose -f docker-compose.nginx.yml up -d
```

## 🔧 Available Commands

The entrypoint script supports the following commands:

- `runserver` - Django development server (default)
- `gunicorn` - Production server with Gunicorn
- `uvicorn` - ASGI server with Uvicorn
- `migrate` - Run migrations only
- `shell` - Django shell
- `help` - Show help message

## 🌐 Services

### Django Application
- **Port**: 8000
- **Health Check**: `http://localhost:8000/cfg/health/`
- **Admin**: `http://localhost:8000/admin/`

### PostgreSQL Database
- **Port**: 5432
- **Database**: `unrealos_db`
- **User**: `unrealos`
- **Password**: `unrealos_password`

### Redis Cache
- **Port**: 6379
- **Memory Limit**: 256MB

### Nginx Proxy (Optional)
- **Port**: 80 (HTTP)
- **Port**: 443 (HTTPS)

## 🔐 Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | - | PostgreSQL connection URL |
| `REDIS_URL` | - | Redis connection URL |
| `ENVIRONMENT` | `development` | Application environment |
| `DEBUG` | `true` | Django debug mode |
| `DJANGO_SECRET_KEY` | - | Django secret key |
| `DJANGO_SUPERUSER_USERNAME` | `admin` | Admin username |
| `DJANGO_SUPERUSER_EMAIL` | `admin@unrealos.com` | Admin email |
| `DJANGO_SUPERUSER_PASSWORD` | `admin` | Admin password |
| `PORT` | `8000` | Application port |
| `GUNICORN_WORKERS` | `2` | Number of Gunicorn workers |
| `LOG_LEVEL` | `DEBUG` | Logging level |

## 📊 Volumes

- `postgres_data` - PostgreSQL data persistence
- `redis_data` - Redis data persistence
- `django_logs` - Application logs
- `django_static` - Static files
- `django_media` - Media files

## 🔍 Troubleshooting

### Database Connection Issues
```bash
# Check PostgreSQL status
docker-compose exec postgres pg_isready -U unrealos

# View PostgreSQL logs
docker-compose logs postgres
```

### Application Issues
```bash
# Check Django logs
docker-compose logs django

# Access Django shell
docker-compose exec django ./scripts/entrypoint.sh shell

# Run migrations manually
docker-compose exec django ./scripts/entrypoint.sh migrate
```

### Redis Issues
```bash
# Check Redis status
docker-compose exec redis redis-cli ping

# View Redis logs
docker-compose logs redis
```

## 🛠 Development

### Rebuilding Images
```bash
# Rebuild Django image
docker-compose build django

# Rebuild all images
docker-compose build
```

### Database Reset
```bash
# Stop services
docker-compose down

# Remove volumes
docker-compose down -v

# Start fresh
docker-compose up -d
```

### Adding Dependencies
1. Update `pyproject.toml` or `requirements.txt`
2. Rebuild the image: `docker-compose build django`
3. Restart services: `docker-compose up -d`

## 📝 Notes

- The application uses Poetry for dependency management
- Static files are collected automatically on startup
- Database migrations run automatically in production mode
- Health checks are configured for all services
- The container runs as a non-root user for security
