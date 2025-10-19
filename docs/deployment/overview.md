---
title: Deployment Overview
description: Deploy Django-CFG to production. Overview of deployment strategies including Docker, cloud platforms, and traditional VPS deployment.
sidebar_label: Overview
sidebar_position: 1
keywords:
  - django-cfg deployment
  - deploy django-cfg
  - django-cfg production
  - containerize django
---

# Deployment Overview

Django-CFG supports multiple deployment strategies to fit your infrastructure needs.

---

## 🐳 Docker (Recommended)

**Best for**: Modern cloud deployments, microservices, consistent environments

**Complete Docker deployment guide:**
**[Docker Setup Guide →](/guides/docker/overview)**

### What's Included
- ✅ Development and production Docker Compose configurations
- ✅ Multi-service architecture (Django, PostgreSQL, Redis, Workers)
- ✅ Automated health checks and service dependencies
- ✅ Configuration via YAML files and environment variables
- ✅ Build optimization for minimal image sizes
- ✅ Comprehensive troubleshooting guide

### Quick Links
- **[Development Setup](/guides/docker/development)** - Local Docker environment
- **[Production Setup](/guides/docker/production)** - Production-ready deployment
- **[Configuration Strategy](/guides/docker/configuration)** - YAML + env vars
- **[Build Optimization](/guides/docker/build-optimization)** - Performance tips
- **[Troubleshooting](/guides/docker/troubleshooting)** - Common issues

---

## ☁️ Cloud Platforms

### AWS
- **ECS/Fargate**: Container orchestration (use Docker setup)
- **Elastic Beanstalk**: Platform-as-a-Service
- **EC2**: Traditional virtual machines

**Guide**: Coming soon

### Google Cloud
- **Cloud Run**: Serverless containers (use Docker setup)
- **GKE**: Kubernetes cluster
- **Compute Engine**: Virtual machines

**Guide**: Coming soon

### Azure
- **Azure Container Instances**: Simple container deployment
- **AKS**: Azure Kubernetes Service
- **App Service**: Platform-as-a-Service

**Guide**: Coming soon

---

## 🚀 Traditional Deployment

### VPS/Dedicated Servers

**Requirements**:
- Python 3.12+
- PostgreSQL 15+
- Redis 7+
- Nginx/Apache (reverse proxy)

**Basic setup**:
```bash
# Install Django-CFG
pip install django-cfg

# Configure settings
# See Configuration Guide for details

# Run with gunicorn
gunicorn api.wsgi:application

# Start Dramatiq workers
python manage.py rundramatiq
```

**Recommended guides**:
- [Environment Setup](./environment-setup) - Environment variables
- [Security Settings](./security) - Production security
- [Logging Configuration](./logging) - Structured logs

---

## 🔧 Infrastructure Components

All deployment methods require:

### Database
- **PostgreSQL** - Primary database (recommended)
- **MySQL/MariaDB** - Alternative option
- **SQLite** - Development only

[Database Configuration Guide →](/fundamentals/configuration/database)

### Cache Layer
- **Redis** - Recommended for caching and task queues
- **Memcached** - Alternative caching backend

[Cache Configuration Guide →](/fundamentals/configuration/cache)

### Background Tasks
- **Dramatiq** - Built-in task processing
- **Celery** - Alternative (requires additional setup)

[Dramatiq Integration →](/features/integrations/dramatiq/overview)

### Reverse Proxy
- **Nginx** - Recommended
- **Apache** - Alternative
- **Traefik** - For Docker deployments (included)

---

## 📋 Deployment Checklist

Before deploying to production:

### Security
- [ ] `DEBUG = False` in production
- [ ] Strong `SECRET_KEY` (50+ characters)
- [ ] Configure `ALLOWED_HOSTS` with actual domains
- [ ] Enable HTTPS/SSL
- [ ] Set up CORS properly via `security_domains`
- [ ] Use environment variables for secrets

[Security Settings Guide →](./security)

### Configuration
- [ ] Database connection configured
- [ ] Redis/cache configured
- [ ] Email service configured
- [ ] Static files configured (Whitenoise or CDN)
- [ ] Media files storage configured
- [ ] Logging configured

[Environment Setup Guide →](./environment-setup)

### Monitoring
- [ ] Health check endpoints configured
- [ ] Logging to centralized service
- [ ] Error tracking (Sentry, etc.)
- [ ] Performance monitoring
- [ ] Uptime monitoring

[Monitoring Guide →](./monitoring)

### Backup & Recovery
- [ ] Database backups automated
- [ ] Media files backups
- [ ] Backup restore tested
- [ ] Disaster recovery plan

---

## See Also

### Docker Deployment
- **[Docker Overview](/guides/docker/overview)** - Complete Docker guide
- **[Development Setup](/guides/docker/development)** - Local environment
- **[Production Setup](/guides/docker/production)** - Production deployment
- **[Configuration](/guides/docker/configuration)** - Docker-specific config

### Configuration
- **[Environment Setup](./environment-setup)** - Environment variables
- **[Security Settings](./security)** - Production security
- **[Logging Configuration](./logging)** - Structured logging
- **[Monitoring Setup](./monitoring)** - Health checks and monitoring

### Guides
- **[Production Config](/guides/production-config)** - Production best practices
- **[Multi-Database Setup](/guides/multi-database)** - Database routing
- **[Troubleshooting](/guides/troubleshooting)** - Common issues

---

TAGS: deployment, production, docker, cloud, infrastructure
DEPENDS_ON: [django-cfg, docker, postgresql, redis]
USED_BY: [production, ci-cd, devops]
