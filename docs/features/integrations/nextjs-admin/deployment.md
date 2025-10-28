---
id: deployment
title: Production Deployment
description: Deploy Next.js admin to production with Docker and best practices
sidebar_label: Deployment
tags:
  - nextjs
  - admin
  - deployment
  - docker
---

# Production Deployment

Complete guide to deploying your Next.js admin to production.

## Overview

The Next.js admin integration is designed for zero-hassle production deployment:

- ✅ **ZIP-based** - Single file instead of thousands
- ✅ **Auto-extraction** - Extracts on first request
- ✅ **Docker-optimized** - Minimal image size
- ✅ **No collectstatic** - WhiteNoise serves directly
- ✅ **CDN-ready** - Optional CDN integration

## Production Checklist

Before deploying, ensure:

- [ ] `auto_build=True` in `NextJsAdminConfig` (or manually build)
- [ ] ZIP archive exists: `static/nextjs_admin.zip`
- [ ] Environment variables configured
- [ ] CORS settings for production domain
- [ ] SECRET_KEY set from environment
- [ ] DEBUG=False in production

## Deployment Methods

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

<Tabs groupId="deployment-method">
  <TabItem value="docker" label="Docker (Recommended)" default>

## Docker Deployment

### 1. Build Next.js Admin

First, generate API clients and build Next.js:

```bash
# Generate TypeScript clients and build
python manage.py generate_clients --typescript

# Verify ZIP was created
ls -lh static/nextjs_admin.zip
# Should show ~5-10MB file
```

### 2. Create Dockerfile

```dockerfile title="Dockerfile"
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy Django application
COPY . .

# Copy ZIP archives (NOT extracted directories!)
COPY static/frontend/admin.zip /app/static/frontend/
COPY static/nextjs_admin.zip /app/static/

# Collect static files (optional, WhiteNoise serves from STATICFILES_DIRS)
# RUN python manage.py collectstatic --noinput

# Expose port
EXPOSE 8000

# Run application
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "4", "core.wsgi:application"]
```

:::tip Image Size Optimization
Copying ZIP files instead of extracted directories reduces image size by ~60%.

**Before** (extracted):
```dockerfile
COPY static/frontend/admin/ /app/static/frontend/admin/  # ~20MB, 5000+ files
```

**After** (ZIP):
```dockerfile
COPY static/frontend/admin.zip /app/static/frontend/  # ~7MB, 1 file
```
:::

### 3. Build Docker Image

```bash
# Build image
docker build -t myapp:latest .

# Check image size
docker images myapp:latest
# REPOSITORY   TAG       SIZE
# myapp        latest    450MB  (with ZIP files)
```

### 4. Run Container

```bash
docker run -d \
  --name myapp \
  -p 8000:8000 \
  -e DEBUG=False \
  -e SECRET_KEY="your-secret-key" \
  -e DATABASE_URL="postgresql://..." \
  myapp:latest
```

### 5. Verify Deployment

```bash
# Check logs for ZIP extraction
docker logs myapp

# Should see:
# INFO: Extracting admin.zip to static/frontend/admin/...
# INFO: Successfully extracted admin.zip
# INFO: Extracting nextjs_admin.zip to static/nextjs_admin/...
# INFO: Successfully extracted nextjs_admin.zip

# Test endpoint
curl http://localhost:8000/admin/
```

### Docker Compose Example

```yaml title="docker-compose.yml"
version: '3.8'

services:
  web:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DEBUG=False
      - SECRET_KEY=${SECRET_KEY}
      - DATABASE_URL=${DATABASE_URL}
      - ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
      - CORS_ALLOWED_ORIGINS=https://yourdomain.com
    volumes:
      - static_data:/app/static_extracted
    depends_on:
      - db

  db:
    image: postgres:15
    environment:
      - POSTGRES_DB=myapp
      - POSTGRES_USER=myapp
      - POSTGRES_PASSWORD=${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
  static_data:  # Persists extracted files across restarts
```

```bash
# Run with docker-compose
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f web
```

  </TabItem>
  <TabItem value="kubernetes" label="Kubernetes">

## Kubernetes Deployment

### 1. Create Deployment

```yaml title="k8s/deployment.yaml"
apiVersion: apps/v1
kind: Deployment
metadata:
  name: myapp
  labels:
    app: myapp
spec:
  replicas: 3
  selector:
    matchLabels:
      app: myapp
  template:
    metadata:
      labels:
        app: myapp
    spec:
      containers:
      - name: web
        image: myregistry/myapp:latest
        ports:
        - containerPort: 8000
        env:
        - name: DEBUG
          value: "False"
        - name: SECRET_KEY
          valueFrom:
            secretKeyRef:
              name: myapp-secrets
              key: secret-key
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: myapp-secrets
              key: database-url
        volumeMounts:
        - name: static-cache
          mountPath: /app/static_extracted
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        readinessProbe:
          httpGet:
            path: /health/
            port: 8000
          initialDelaySeconds: 10
          periodSeconds: 5
        livenessProbe:
          httpGet:
            path: /health/
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
      volumes:
      - name: static-cache
        emptyDir: {}
```

### 2. Create Service

```yaml title="k8s/service.yaml"
apiVersion: v1
kind: Service
metadata:
  name: myapp
spec:
  selector:
    app: myapp
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8000
  type: LoadBalancer
```

### 3. Create Secrets

```yaml title="k8s/secrets.yaml"
apiVersion: v1
kind: Secret
metadata:
  name: myapp-secrets
type: Opaque
stringData:
  secret-key: "your-secret-key-here"
  database-url: "postgresql://user:pass@host/db"
```

### 4. Deploy

```bash
# Apply secrets
kubectl apply -f k8s/secrets.yaml

# Deploy application
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml

# Check status
kubectl get pods
kubectl get svc

# View logs
kubectl logs -f deployment/myapp

# Should see ZIP extraction logs
```

### 5. Ingress Configuration

```yaml title="k8s/ingress.yaml"
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: myapp-ingress
  annotations:
    cert-manager.io/cluster-issuer: letsencrypt-prod
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
spec:
  tls:
  - hosts:
    - yourdomain.com
    secretName: myapp-tls
  rules:
  - host: yourdomain.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: myapp
            port:
              number: 80
```

```bash
kubectl apply -f k8s/ingress.yaml
```

  </TabItem>
  <TabItem value="cloud" label="Cloud Platforms">

## Cloud Platform Deployment

### AWS ECS

```bash
# 1. Build and push to ECR
aws ecr get-login-password --region us-east-1 | \
  docker login --username AWS --password-stdin \
  123456789.dkr.ecr.us-east-1.amazonaws.com

docker build -t myapp .
docker tag myapp:latest 123456789.dkr.ecr.us-east-1.amazonaws.com/myapp:latest
docker push 123456789.dkr.ecr.us-east-1.amazonaws.com/myapp:latest

# 2. Create task definition
# (Use AWS Console or CLI)

# 3. Create service
aws ecs create-service \
  --cluster myapp-cluster \
  --service-name myapp-service \
  --task-definition myapp:1 \
  --desired-count 3 \
  --launch-type FARGATE \
  --network-configuration "awsvpcConfiguration={subnets=[subnet-xxx],securityGroups=[sg-xxx]}"
```

### Google Cloud Run

```bash
# 1. Build and push to GCR
gcloud builds submit --tag gcr.io/PROJECT_ID/myapp

# 2. Deploy to Cloud Run
gcloud run deploy myapp \
  --image gcr.io/PROJECT_ID/myapp \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars "DEBUG=False,SECRET_KEY=xxx"
```

### Azure Container Instances

```bash
# 1. Build and push to ACR
az acr build --registry myregistry --image myapp:latest .

# 2. Deploy to ACI
az container create \
  --resource-group myapp-rg \
  --name myapp \
  --image myregistry.azurecr.io/myapp:latest \
  --dns-name-label myapp \
  --ports 8000 \
  --environment-variables DEBUG=False SECRET_KEY=xxx
```

  </TabItem>
  <TabItem value="traditional" label="Traditional Server">

## Traditional Server Deployment

### Using systemd + Nginx

#### 1. Install Dependencies

```bash
# On Ubuntu/Debian
sudo apt-get update
sudo apt-get install -y python3-pip nginx

# Install Python packages
pip3 install -r requirements.txt
```

#### 2. Generate and Build

```bash
# Generate API clients and build Next.js
python3 manage.py generate_clients --typescript

# Verify ZIP files
ls -lh static/*.zip static/frontend/*.zip
```

#### 3. Create systemd Service

```ini title="/etc/systemd/system/myapp.service"
[Unit]
Description=My Django App
After=network.target

[Service]
Type=notify
User=www-data
Group=www-data
WorkingDirectory=/var/www/myapp
Environment="DEBUG=False"
Environment="SECRET_KEY=your-secret-key"
Environment="DATABASE_URL=postgresql://..."
ExecStart=/usr/bin/gunicorn \
    --bind unix:/run/myapp.sock \
    --workers 4 \
    --access-logfile /var/log/myapp/access.log \
    --error-logfile /var/log/myapp/error.log \
    core.wsgi:application

[Install]
WantedBy=multi-user.target
```

```bash
# Enable and start service
sudo systemctl enable myapp
sudo systemctl start myapp

# Check status
sudo systemctl status myapp

# View logs
sudo journalctl -u myapp -f
```

#### 4. Configure Nginx

```nginx title="/etc/nginx/sites-available/myapp"
upstream myapp {
    server unix:/run/myapp.sock fail_timeout=0;
}

server {
    listen 80;
    server_name yourdomain.com;

    client_max_body_size 10M;

    location / {
        proxy_pass http://myapp;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Optional: Serve static files directly with Nginx
    # (WhiteNoise can handle this too)
    location /static/ {
        alias /var/www/myapp/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
```

```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/myapp /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

#### 5. SSL with Let's Encrypt

```bash
# Install certbot
sudo apt-get install -y certbot python3-certbot-nginx

# Get certificate
sudo certbot --nginx -d yourdomain.com

# Auto-renewal is set up automatically
```

  </TabItem>
</Tabs>

## Environment Configuration

### Production Settings

```python title="api/config.py"
import os

config = DjangoConfig(
    # Environment mode
    env_mode=os.getenv("ENV_MODE", "production"),

    # Security
    secret_key=os.getenv("SECRET_KEY"),
    debug=os.getenv("DEBUG", "False") == "True",
    allowed_hosts=os.getenv("ALLOWED_HOSTS", "").split(","),

    # Next.js Admin
    nextjs_admin=NextJsAdminConfig(
        project_path=os.getenv("NEXTJS_ADMIN_PATH", "../django_admin"),
        static_url="/admin-ui/",
    ),

    # CORS
    cors_allowed_origins=os.getenv("CORS_ALLOWED_ORIGINS", "").split(","),

    # Database
    databases={
        "default": DatabaseConfig(
            url=os.getenv("DATABASE_URL"),
        )
    },
)
```

### Environment Variables

```bash title=".env.production"
# Django
ENV_MODE=production
DEBUG=False
SECRET_KEY=your-long-random-secret-key
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

# Next.js Admin
NEXTJS_ADMIN_PATH=/app/django_admin

# CORS
CORS_ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com

# Database
DATABASE_URL=postgresql://user:password@host:5432/dbname
```

## Performance Optimization

### 1. WhiteNoise Configuration

WhiteNoise is auto-configured by django-cfg, but you can optimize:

```python title="api/config.py"
config = DjangoConfig(
    # WhiteNoise is enabled by default
    # Serves static files with compression and caching
)
```

WhiteNoise automatically:
- ✅ Compresses static files (gzip, brotli)
- ✅ Sets cache headers (`Cache-Control: max-age=31536000`)
- ✅ Serves with optimal performance

### 2. Gunicorn Workers

```bash
# Calculate optimal workers: (2 * CPU cores) + 1
gunicorn --workers 9 --bind 0.0.0.0:8000 core.wsgi:application

# With threading
gunicorn --workers 4 --threads 2 --bind 0.0.0.0:8000 core.wsgi:application
```

### 3. CDN Integration (Optional)

For global deployments, use a CDN:

```python
# Configure CDN URL
STATIC_URL = "https://cdn.yourdomain.com/static/"
```

Upload ZIP contents to CDN:

```bash
# Extract ZIP
unzip static/nextjs_admin.zip -d /tmp/nextjs_admin

# Upload to S3 + CloudFront
aws s3 sync /tmp/nextjs_admin s3://yourbucket/static/nextjs_admin/ \
  --cache-control "max-age=31536000"

# Invalidate CloudFront cache
aws cloudfront create-invalidation \
  --distribution-id XXXXX \
  --paths "/static/nextjs_admin/*"
```

## Monitoring and Logging

### Health Check Endpoint

```python title="api/urls.py"
from django.http import JsonResponse

def health_check(request):
    return JsonResponse({
        "status": "healthy",
        "nextjs_admin": has_nextjs_admin(),
    })

urlpatterns = [
    path("health/", health_check),
    # ...
]
```

### Logging Configuration

```python title="api/config.py"
config = DjangoConfig(
    # ...

    logging={
        "version": 1,
        "disable_existing_loggers": False,
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
            },
            "file": {
                "class": "logging.FileHandler",
                "filename": "/var/log/myapp/django.log",
            },
        },
        "loggers": {
            "django_cfg.apps.frontend": {
                "handlers": ["console", "file"],
                "level": "INFO",
            },
        },
    },
)
```

### Monitor ZIP Extraction

```bash
# Docker logs
docker logs -f myapp | grep "Extracting"

# Output:
# INFO: Extracting nextjs_admin.zip to /app/static/nextjs_admin/...
# INFO: Successfully extracted nextjs_admin.zip (7.2MB in 95ms)
```

## Troubleshooting Production

### ZIP Not Extracting

**Check 1**: Does ZIP file exist?

```bash
docker exec myapp ls -lh /app/static/nextjs_admin.zip
```

**Check 2**: Permissions

```bash
docker exec myapp ls -ld /app/static/
# Should be writable by app user
```

**Check 3**: Disk space

```bash
docker exec myapp df -h
```

### 404 on Admin Page

**Check 1**: URL configuration

```python
# Verify static_url in config
nextjs_admin=NextJsAdminConfig(
    static_url="/cfg/admin/",  # Check this matches your URLs
)
```

**Check 2**: URL patterns

```bash
# List URLs
docker exec myapp python manage.py show_urls | grep admin
```

### Slow First Request

This is expected (ZIP extraction). Optimize with:

1. **Pre-extract in Docker build** (not recommended, increases image size)
2. **Use persistent volumes** (extraction persists across restarts)
3. **Accept one-time cost** (~100ms, only first request)

## CI/CD Integration

### GitHub Actions Example

```yaml title=".github/workflows/deploy.yml"
name: Deploy

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v2

      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: pip install -r requirements.txt

      - name: Generate API and build Next.js
        run: |
          python manage.py generate_clients --typescript
          ls -lh static/nextjs_admin.zip

      - name: Build Docker image
        run: docker build -t myapp:${{ github.sha }} .

      - name: Push to registry
        run: |
          echo ${{ secrets.DOCKER_PASSWORD }} | docker login -u ${{ secrets.DOCKER_USERNAME }} --password-stdin
          docker push myapp:${{ github.sha }}

      - name: Deploy to production
        run: |
          # Deploy command (depends on your infrastructure)
          kubectl set image deployment/myapp web=myapp:${{ github.sha }}
```

## Next Steps

- [Troubleshooting Guide](./troubleshooting) - Common issues
- [Examples](./examples) - Real-world examples
- [How It Works](./how-it-works) - Architecture deep dive

:::tip Production Checklist
Use our [production checklist](https://github.com/django-cfg/production-checklist) to ensure nothing is missed.
:::
