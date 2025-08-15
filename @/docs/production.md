# 🚀 Production Deployment - Secure & Scalable %%PRIORITY:HIGH%%

## 🎯 Quick Summary
Complete production deployment guide for the isolated Django configuration system with security hardening, performance optimization, and operational best practices.

## 📋 Table of Contents
1. [Production Checklist](#production-checklist)
2. [Security Configuration](#security-configuration)
3. [Performance Optimization](#performance-optimization)
4. [Deployment Strategies](#deployment-strategies)
5. [Monitoring & Health Checks](#monitoring--health-checks)
6. [Troubleshooting](#troubleshooting)

## 🔑 Key Concepts at a Glance
- **Security first**: All production settings secure by default
- **Performance optimized**: <50ms startup, minimal resource usage
- **Zero-downtime deployment**: Rolling updates and health checks
- **Observability**: Comprehensive monitoring and alerting
- **Disaster recovery**: Backup and rollback procedures

## ✅ Production Checklist

### Pre-Deployment Security Checklist
```python
# Run production security validation
from api.config import ConfigToolkit

def production_security_checklist():
    """Comprehensive production security checklist."""
    
    checks = []
    
    # 1. Core Django Security
    checks.append(("DEBUG disabled", not ConfigToolkit.debug))
    checks.append(("SECRET_KEY secure", len(ConfigToolkit.secret_key) >= 32 and not ConfigToolkit.secret_key.startswith('django-insecure')))
    checks.append(("ALLOWED_HOSTS configured", ConfigToolkit.allowed_hosts and '*' not in ConfigToolkit.allowed_hosts))
    
    # 2. Database Security
    checks.append(("Database SSL required", ConfigToolkit.database_ssl_required))
    checks.append(("Database URL secure", ConfigToolkit.database_url.startswith(('postgresql://', 'mysql://'))))
    
    # 3. HTTPS/SSL Security
    checks.append(("SSL enabled", ConfigToolkit.ssl_enabled))
    checks.append(("HSTS enabled", ConfigToolkit.hsts_enabled))
    checks.append(("Secure cookies", ConfigToolkit.session_cookie_secure))
    
    # 4. CORS Security
    checks.append(("CORS properly configured", not (ConfigToolkit.cors_enabled and ConfigToolkit.cors_allow_all_origins)))
    
    # 5. API Security
    checks.append(("Rate limiting enabled", ConfigToolkit.api_rate_limit_enabled))
    checks.append(("API docs disabled", not ConfigToolkit.api_docs_enabled))
    
    # Print checklist results
    print("🔒 Production Security Checklist")
    print("=" * 40)
    
    all_passed = True
    for check_name, passed in checks:
        status = "✅" if passed else "❌"
        print(f"{status} {check_name}")
        if not passed:
            all_passed = False
    
    print("=" * 40)
    if all_passed:
        print("✅ All security checks PASSED - ready for production")
    else:
        print("❌ Security checks FAILED - DO NOT deploy to production")
    
    return all_passed

# Run checklist before deployment
if __name__ == "__main__":
    production_security_checklist()
```

### Environment Setup Checklist
```bash
# Production environment setup checklist

# 1. Environment Variables
echo "🔍 Checking environment variables..."
[ -n "$SECRET_KEY" ] && echo "✅ SECRET_KEY set" || echo "❌ SECRET_KEY missing"
[ -n "$DATABASE_URL" ] && echo "✅ DATABASE_URL set" || echo "❌ DATABASE_URL missing"
[ -n "$ALLOWED_HOSTS" ] && echo "✅ ALLOWED_HOSTS set" || echo "❌ ALLOWED_HOSTS missing"

# 2. SSL Certificates
echo "🔍 Checking SSL certificates..."
[ -f "/etc/ssl/certs/server.crt" ] && echo "✅ SSL certificate found" || echo "❌ SSL certificate missing"
[ -f "/etc/ssl/private/server.key" ] && echo "✅ SSL private key found" || echo "❌ SSL private key missing"

# 3. Database Connectivity
echo "🔍 Testing database connectivity..."
python -c "
from api.config import ConfigToolkit
from django.db import connection
try:
    connection.ensure_connection()
    print('✅ Database connection successful')
except Exception as e:
    print(f'❌ Database connection failed: {e}')
"

# 4. Cache Connectivity (if Redis)
echo "🔍 Testing cache connectivity..."
python -c "
from api.config import ConfigToolkit
if ConfigToolkit.cache_backend == 'redis':
    import redis
    try:
        r = redis.from_url(ConfigToolkit.cache_redis_url)
        r.ping()
        print('✅ Redis connection successful')
    except Exception as e:
        print(f'❌ Redis connection failed: {e}')
else:
    print('✅ Memory cache configured')
"

# 5. Configuration Validation
echo "🔍 Validating configuration..."
python -c "
from api.config import ConfigToolkit
try:
    ConfigToolkit.validate_all_configurations()
    print('✅ Configuration validation passed')
except Exception as e:
    print(f'❌ Configuration validation failed: {e}')
"
```

## 🔐 Security Configuration

### Production Environment Variables
```bash
# .env.prod - Production configuration template
# Set these environment variables in your deployment platform

# Core Django Security
SECRET_KEY=${SECRET_KEY}  # 50+ character random string
DEBUG=false
DJANGO_ENV=production
ALLOWED_HOSTS=${DOMAIN_NAME},${SUBDOMAIN_NAME}

# Database Security
DATABASE_URL=${DATABASE_URL}  # postgresql://user:pass@host:5432/db
DATABASE_SSL_REQUIRED=true
DATABASE_MAX_CONNECTIONS=20
DATABASE_CONN_MAX_AGE=300

# HTTPS/SSL Security
SSL_ENABLED=true
SECURE_SSL_REDIRECT=true
HSTS_ENABLED=true
HSTS_MAX_AGE=31536000
SECURE_PROXY_SSL_HEADER_NAME=HTTP_X_FORWARDED_PROTO
SECURE_PROXY_SSL_HEADER_VALUE=https

# Session Security
SESSION_COOKIE_SECURE=true
SESSION_COOKIE_HTTPONLY=true
SESSION_COOKIE_SAMESITE=Lax
SESSION_COOKIE_AGE=86400

# CSRF Security
CSRF_ENABLED=true
CSRF_COOKIE_SECURE=true
CSRF_COOKIE_HTTPONLY=true
CSRF_TRUSTED_ORIGINS=${TRUSTED_ORIGINS}

# CORS Security (restrictive)
CORS_ENABLED=false
CORS_ALLOWED_ORIGINS=${FRONTEND_URLS}
CORS_ALLOW_CREDENTIALS=false

# API Security
API_RATE_LIMIT_ENABLED=true
API_DOCS_ENABLED=false
API_PAGE_SIZE=50
API_MAX_PAGE_SIZE=100

# Cache Security
CACHE_BACKEND=redis
CACHE_REDIS_URL=${REDIS_URL}
CACHE_DEFAULT_TIMEOUT=3600
CACHE_KEY_PREFIX=prod

# Email Security
EMAIL_BACKEND=smtp
EMAIL_HOST=${EMAIL_HOST}
EMAIL_PORT=${EMAIL_PORT}
EMAIL_HOST_USER=${EMAIL_HOST_USER}
EMAIL_HOST_PASSWORD=${EMAIL_HOST_PASSWORD}
EMAIL_USE_TLS=true

# Logging & Monitoring
LOG_LEVEL=INFO
LOG_TO_FILE=true
SENTRY_DSN=${SENTRY_DSN}
MONITORING_ENABLED=true
```

### Security Headers Configuration
```python
# ConfigToolkit automatically applies security headers in production
class ProductionSecurityHeaders:
    """Security headers applied in production."""
    
    @classmethod
    def get_security_headers(cls):
        """Get production security headers."""
        
        if not ConfigToolkit.is_production:
            return {}
        
        return {
            # HTTPS enforcement
            'SECURE_SSL_REDIRECT': ConfigToolkit.ssl_enabled,
            'SECURE_PROXY_SSL_HEADER': ('HTTP_X_FORWARDED_PROTO', 'https'),
            
            # HSTS (HTTP Strict Transport Security)
            'SECURE_HSTS_SECONDS': 31536000 if ConfigToolkit.hsts_enabled else 0,
            'SECURE_HSTS_INCLUDE_SUBDOMAINS': True,
            'SECURE_HSTS_PRELOAD': True,
            
            # Content Security Policy
            'CSP_DEFAULT_SRC': ["'self'"],
            'CSP_SCRIPT_SRC': ["'self'", "'unsafe-inline'"],
            'CSP_STYLE_SRC': ["'self'", "'unsafe-inline'"],
            'CSP_IMG_SRC': ["'self'", "data:", "https:"],
            
            # Additional security headers
            'SECURE_CONTENT_TYPE_NOSNIFF': True,
            'SECURE_BROWSER_XSS_FILTER': True,
            'SECURE_REFERRER_POLICY': 'strict-origin-when-cross-origin',
            'X_FRAME_OPTIONS': 'DENY',
        }
```

### Secrets Management
```python
# Production secrets management
class ProductionSecretsManager:
    """Manage secrets in production environment."""
    
    @classmethod
    def load_from_aws_ssm(cls, parameter_prefix: str):
        """Load secrets from AWS Systems Manager Parameter Store."""
        import boto3
        
        ssm = boto3.client('ssm')
        
        parameters = ssm.get_parameters_by_path(
            Path=parameter_prefix,
            Recursive=True,
            WithDecryption=True
        )
        
        secrets = {}
        for param in parameters['Parameters']:
            key = param['Name'].replace(parameter_prefix, '').lstrip('/')
            secrets[key.upper()] = param['Value']
        
        return secrets
    
    @classmethod
    def load_from_vault(cls, vault_path: str):
        """Load secrets from HashiCorp Vault."""
        import hvac
        
        client = hvac.Client(url=os.getenv('VAULT_URL'))
        client.token = os.getenv('VAULT_TOKEN')
        
        response = client.secrets.kv.v2.read_secret_version(path=vault_path)
        return response['data']['data']
    
    @classmethod
    def load_from_kubernetes_secrets(cls):
        """Load secrets from Kubernetes secret mounts."""
        secrets = {}
        secrets_dir = Path('/var/secrets')
        
        if secrets_dir.exists():
            for secret_file in secrets_dir.iterdir():
                if secret_file.is_file():
                    key = secret_file.name.upper()
                    secrets[key] = secret_file.read_text().strip()
        
        return secrets
```

## ⚡ Performance Optimization

### Production Performance Configuration
```python
# Production performance settings
class ProductionPerformanceConfig:
    """Production performance optimization settings."""
    
    @classmethod
    def get_performance_settings(cls):
        """Get production performance settings."""
        
        return {
            # Database optimization
            'DATABASES': {
                'default': {
                    'ENGINE': 'django.db.backends.postgresql',
                    'NAME': ConfigToolkit.database_name,
                    'USER': ConfigToolkit.database_user,
                    'PASSWORD': ConfigToolkit.database_password,
                    'HOST': ConfigToolkit.database_host,
                    'PORT': ConfigToolkit.database_port,
                    'OPTIONS': {
                        'sslmode': 'require' if ConfigToolkit.database_ssl_required else 'prefer',
                        'connect_timeout': 10,
                        'options': '-c default_transaction_isolation=read_committed'
                    },
                    'CONN_MAX_AGE': ConfigToolkit.database_conn_max_age,
                    'CONN_HEALTH_CHECKS': True,
                }
            },
            
            # Cache optimization
            'CACHES': {
                'default': {
                    'BACKEND': 'django.core.cache.backends.redis.RedisCache',
                    'LOCATION': ConfigToolkit.cache_redis_url,
                    'OPTIONS': {
                        'CONNECTION_POOL_KWARGS': {
                            'max_connections': 50,
                            'retry_on_timeout': True,
                        },
                        'COMPRESSOR': 'django.core.cache.backends.redis.GzipCompressor',
                    },
                    'KEY_PREFIX': ConfigToolkit.cache_key_prefix,
                    'TIMEOUT': ConfigToolkit.cache_default_timeout,
                }
            },
            
            # Static files optimization
            'STATICFILES_STORAGE': 'whitenoise.storage.CompressedManifestStaticFilesStorage',
            'WHITENOISE_USE_FINDERS': False,
            'WHITENOISE_AUTOREFRESH': False,
            'WHITENOISE_MAX_AGE': 31536000,  # 1 year
            
            # Session optimization
            'SESSION_ENGINE': 'django.contrib.sessions.backends.cache',
            'SESSION_CACHE_ALIAS': 'default',
            'SESSION_COOKIE_AGE': 86400,  # 24 hours
            
            # Email optimization
            'EMAIL_TIMEOUT': 30,
            'EMAIL_USE_LOCALTIME': True,
        }

# Apply production performance settings
if ConfigToolkit.is_production:
    performance_settings = ProductionPerformanceConfig.get_performance_settings()
    # Settings are automatically applied by ConfigToolkit
```

### Gunicorn Configuration
```python
# gunicorn.conf.py - Production WSGI server configuration
import multiprocessing
from api.config import ConfigToolkit

# Server socket
bind = "0.0.0.0:8000"
backlog = 2048

# Worker processes
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "sync"
worker_connections = 1000
timeout = 30
keepalive = 2

# Restart workers after this many requests, with up to 50% jitter
max_requests = 1000
max_requests_jitter = 500

# Logging
loglevel = ConfigToolkit.log_level.lower()
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'
accesslog = "/var/log/gunicorn/access.log" if ConfigToolkit.log_to_file else "-"
errorlog = "/var/log/gunicorn/error.log" if ConfigToolkit.log_to_file else "-"

# Security
limit_request_line = 4094
limit_request_fields = 100
limit_request_field_size = 8190

# Performance
preload_app = True
enable_stdio_inheritance = True

# Process naming
proc_name = 'django-app'

# Worker lifecycle hooks
def on_starting(server):
    """Called just before the master process is initialized."""
    server.log.info("Gunicorn master starting")

def on_reload(server):
    """Called to recycle workers during a reload via SIGHUP."""
    server.log.info("Gunicorn master reloading")

def when_ready(server):
    """Called just after the server is started."""
    server.log.info("Gunicorn master ready")

def worker_int(worker):
    """Called just after a worker exited on SIGINT or SIGQUIT."""
    worker.log.info("Worker received INT or QUIT signal")

def on_exit(server):
    """Called just before exiting."""
    server.log.info("Gunicorn master exiting")
```

## 🚀 Deployment Strategies

### Docker Production Deployment
```dockerfile
# Dockerfile.prod - Multi-stage production build
FROM python:3.11-slim as builder

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Production stage
FROM python:3.11-slim

# Create application user
RUN groupadd -r django && useradd -r -g django django

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

# Copy Python dependencies from builder stage
COPY --from=builder /root/.local /home/django/.local

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PATH=/home/django/.local/bin:$PATH
ENV DJANGO_ENV=production

# Create application directory
WORKDIR /app

# Copy application code
COPY --chown=django:django . .

# Create necessary directories
RUN mkdir -p /app/logs /app/staticfiles /app/media && \
    chown -R django:django /app

# Switch to application user
USER django

# Collect static files
RUN python manage.py collectstatic --noinput

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "from api.config import ConfigToolkit; ConfigToolkit.validate_all_configurations()" || exit 1

# Start application
CMD ["gunicorn", "--config", "gunicorn.conf.py", "api.wsgi:application"]
```

### Kubernetes Deployment
```yaml
# k8s-deployment.yaml - Kubernetes production deployment
apiVersion: apps/v1
kind: Deployment
metadata:
  name: django-app
  labels:
    app: django-app
spec:
  replicas: 3
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 0
  selector:
    matchLabels:
      app: django-app
  template:
    metadata:
      labels:
        app: django-app
    spec:
      containers:
      - name: django-app
        image: myregistry/django-app:latest
        ports:
        - containerPort: 8000
        env:
        - name: DJANGO_ENV
          value: "production"
        - name: SECRET_KEY
          valueFrom:
            secretKeyRef:
              name: django-secrets
              key: secret-key
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: django-secrets
              key: database-url
        - name: REDIS_URL
          valueFrom:
            secretKeyRef:
              name: django-secrets
              key: redis-url
        
        # Resource limits
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        
        # Health checks
        livenessProbe:
          httpGet:
            path: /health/
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
          timeoutSeconds: 5
          failureThreshold: 3
        
        readinessProbe:
          httpGet:
            path: /ready/
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
          timeoutSeconds: 3
          failureThreshold: 3
        
        # Security context
        securityContext:
          runAsNonRoot: true
          runAsUser: 1000
          allowPrivilegeEscalation: false
          readOnlyRootFilesystem: false
        
        # Volume mounts
        volumeMounts:
        - name: static-files
          mountPath: /app/staticfiles
        - name: media-files
          mountPath: /app/media
        - name: logs
          mountPath: /app/logs
      
      volumes:
      - name: static-files
        emptyDir: {}
      - name: media-files
        persistentVolumeClaim:
          claimName: media-pvc
      - name: logs
        emptyDir: {}

---
apiVersion: v1
kind: Service
metadata:
  name: django-app-service
spec:
  selector:
    app: django-app
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8000
  type: ClusterIP
```

### CI/CD Pipeline
```yaml
# .github/workflows/deploy.yml - GitHub Actions deployment
name: Deploy to Production

on:
  push:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install -r requirements-test.txt
    
    - name: Run tests
      run: |
        python -m pytest
        
    - name: Security check
      run: |
        python -c "
        from api.config import ConfigToolkit
        ConfigToolkit.override({'django_env': 'production'})
        assert ConfigToolkit.validate_production_security()
        "

  deploy:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Build Docker image
      run: |
        docker build -f Dockerfile.prod -t myregistry/django-app:${{ github.sha }} .
        docker tag myregistry/django-app:${{ github.sha }} myregistry/django-app:latest
    
    - name: Push to registry
      run: |
        echo ${{ secrets.DOCKER_PASSWORD }} | docker login -u ${{ secrets.DOCKER_USERNAME }} --password-stdin
        docker push myregistry/django-app:${{ github.sha }}
        docker push myregistry/django-app:latest
    
    - name: Deploy to Kubernetes
      run: |
        echo "${{ secrets.KUBECONFIG }}" | base64 -d > kubeconfig
        export KUBECONFIG=kubeconfig
        kubectl set image deployment/django-app django-app=myregistry/django-app:${{ github.sha }}
        kubectl rollout status deployment/django-app
```

## 📊 Monitoring & Health Checks

### Health Check Endpoints
```python
# api/health/views.py - Health check endpoints
from django.http import JsonResponse
from django.views import View
from api.config import ConfigToolkit
import time

class HealthCheckView(View):
    """Basic health check endpoint."""
    
    def get(self, request):
        """Basic health check - application is running."""
        return JsonResponse({
            'status': 'healthy',
            'timestamp': time.time(),
            'environment': ConfigToolkit.environment,
        })

class ReadinessCheckView(View):
    """Readiness check - application is ready to serve traffic."""
    
    def get(self, request):
        """Check if application is ready to serve requests."""
        
        checks = {}
        overall_status = 'ready'
        
        # Database check
        try:
            from django.db import connection
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
            checks['database'] = 'healthy'
        except Exception as e:
            checks['database'] = f'unhealthy: {e}'
            overall_status = 'not_ready'
        
        # Cache check (if Redis)
        if ConfigToolkit.cache_backend == 'redis':
            try:
                from django.core.cache import cache
                cache.set('health_check', 'ok', 10)
                cache.get('health_check')
                checks['cache'] = 'healthy'
            except Exception as e:
                checks['cache'] = f'unhealthy: {e}'
                overall_status = 'not_ready'
        else:
            checks['cache'] = 'memory_cache_ok'
        
        # Configuration check
        try:
            ConfigToolkit.validate_all_configurations()
            checks['configuration'] = 'valid'
        except Exception as e:
            checks['configuration'] = f'invalid: {e}'
            overall_status = 'not_ready'
        
        status_code = 200 if overall_status == 'ready' else 503
        
        return JsonResponse({
            'status': overall_status,
            'checks': checks,
            'timestamp': time.time(),
        }, status=status_code)

class LivenessCheckView(View):
    """Liveness check - application should be restarted if this fails."""
    
    def get(self, request):
        """Check if application is alive and functioning."""
        
        # Basic application health
        try:
            # Test configuration access
            _ = ConfigToolkit.debug
            _ = ConfigToolkit.database_url
            
            return JsonResponse({
                'status': 'alive',
                'timestamp': time.time(),
            })
        except Exception as e:
            return JsonResponse({
                'status': 'dead',
                'error': str(e),
                'timestamp': time.time(),
            }, status=500)
```

### Metrics Collection
```python
# api/monitoring/metrics.py - Production metrics
import time
import psutil
from django.http import JsonResponse
from django.views import View
from api.config import ConfigToolkit

class MetricsView(View):
    """Application metrics for monitoring."""
    
    def get(self, request):
        """Get application metrics."""
        
        process = psutil.Process()
        
        # Performance metrics
        performance_info = ConfigToolkit.get_performance_info()
        
        # System metrics
        system_metrics = {
            'memory_usage_mb': process.memory_info().rss / 1024 / 1024,
            'cpu_percent': process.cpu_percent(),
            'open_files': len(process.open_files()),
            'threads': process.num_threads(),
        }
        
        # Database metrics
        database_metrics = {}
        try:
            from django.db import connection
            database_metrics = {
                'queries_count': len(connection.queries),
                'connection_status': 'connected' if connection.connection else 'disconnected',
            }
        except Exception as e:
            database_metrics = {'error': str(e)}
        
        # Cache metrics
        cache_metrics = {}
        if ConfigToolkit.cache_backend == 'redis':
            try:
                from django.core.cache import cache
                import redis
                r = redis.from_url(ConfigToolkit.cache_redis_url)
                info = r.info()
                cache_metrics = {
                    'connected_clients': info['connected_clients'],
                    'used_memory_mb': info['used_memory'] / 1024 / 1024,
                    'keyspace_hits': info['keyspace_hits'],
                    'keyspace_misses': info['keyspace_misses'],
                }
            except Exception as e:
                cache_metrics = {'error': str(e)}
        
        return JsonResponse({
            'timestamp': time.time(),
            'environment': ConfigToolkit.environment,
            'performance': performance_info,
            'system': system_metrics,
            'database': database_metrics,
            'cache': cache_metrics,
        })
```

### Logging Configuration
```python
# Production logging configuration
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'json': {
            'format': '{"level": "%(levelname)s", "time": "%(asctime)s", "module": "%(module)s", "message": "%(message)s"}',
        },
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'json' if ConfigToolkit.is_production else 'verbose',
        },
        'file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': '/app/logs/django.log',
            'maxBytes': 1024*1024*10,  # 10MB
            'backupCount': 5,
            'formatter': 'json',
        },
        'error_file': {
            'level': 'ERROR',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': '/app/logs/django-error.log',
            'maxBytes': 1024*1024*10,  # 10MB
            'backupCount': 5,
            'formatter': 'json',
        },
    },
    'root': {
        'handlers': ['console'] + (['file', 'error_file'] if ConfigToolkit.log_to_file else []),
        'level': ConfigToolkit.log_level,
    },
    'loggers': {
        'django': {
            'handlers': ['console'] + (['file'] if ConfigToolkit.log_to_file else []),
            'level': 'INFO',
            'propagate': False,
        },
        'api': {
            'handlers': ['console'] + (['file'] if ConfigToolkit.log_to_file else []),
            'level': 'INFO',
            'propagate': False,
        },
    },
}
```

## 🐛 Troubleshooting

### Production Issue Diagnostics
```python
# Production diagnostic script
def diagnose_production_issues():
    """Comprehensive production issue diagnosis."""
    
    print("🔍 Production Issue Diagnosis")
    print("=" * 50)
    
    # 1. Configuration validation
    print("\n1. Configuration Validation:")
    try:
        ConfigToolkit.validate_all_configurations()
        print("✅ Configuration is valid")
    except Exception as e:
        print(f"❌ Configuration error: {e}")
    
    # 2. Database connectivity
    print("\n2. Database Connectivity:")
    try:
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT version()")
            version = cursor.fetchone()[0]
        print(f"✅ Database connected: {version}")
    except Exception as e:
        print(f"❌ Database error: {e}")
    
    # 3. Cache connectivity
    print("\n3. Cache Connectivity:")
    try:
        from django.core.cache import cache
        cache.set('diagnostic_test', 'ok', 10)
        result = cache.get('diagnostic_test')
        print(f"✅ Cache working: {result}")
    except Exception as e:
        print(f"❌ Cache error: {e}")
    
    # 4. Security validation
    print("\n4. Security Validation:")
    try:
        security_issues = validate_production_security()
        if security_issues:
            for issue in security_issues:
                print(f"⚠️ Security issue: {issue}")
        else:
            print("✅ All security checks passed")
    except Exception as e:
        print(f"❌ Security validation error: {e}")
    
    # 5. Performance metrics
    print("\n5. Performance Metrics:")
    try:
        perf_info = ConfigToolkit.get_performance_info()
        print(f"✅ Initialization time: {perf_info['initialization_time_ms']:.2f}ms")
        print(f"✅ Memory usage: {perf_info['memory_usage_mb']:.2f}MB")
    except Exception as e:
        print(f"❌ Performance metrics error: {e}")
    
    # 6. Environment information
    print("\n6. Environment Information:")
    env_info = ConfigToolkit.get_environment_info()
    for key, value in env_info.items():
        print(f"📊 {key}: {value}")

if __name__ == "__main__":
    diagnose_production_issues()
```

### Common Production Issues

#### Issue 1: High Memory Usage
```python
# Diagnose memory issues
def diagnose_memory_issues():
    """Diagnose high memory usage in production."""
    
    import gc
    import tracemalloc
    
    # Start memory tracing
    tracemalloc.start()
    
    # Force garbage collection
    gc.collect()
    
    # Get memory snapshot
    snapshot = tracemalloc.take_snapshot()
    top_stats = snapshot.statistics('lineno')
    
    print("🔍 Memory Usage Analysis")
    print("Top 10 memory allocations:")
    for stat in top_stats[:10]:
        print(f"{stat.size / 1024 / 1024:.2f}MB: {stat}")
    
    # Check for configuration memory leaks
    config_memory = sum(
        stat.size for stat in top_stats 
        if 'config' in str(stat.traceback).lower()
    )
    print(f"Configuration memory usage: {config_memory / 1024 / 1024:.2f}MB")
```

#### Issue 2: Slow Response Times
```python
# Diagnose performance issues
def diagnose_performance_issues():
    """Diagnose slow response times in production."""
    
    import time
    
    print("🔍 Performance Diagnosis")
    
    # Test configuration access speed
    start_time = time.perf_counter()
    for _ in range(1000):
        _ = ConfigToolkit.debug
        _ = ConfigToolkit.database_url
    config_time = time.perf_counter() - start_time
    print(f"1000 config accesses: {config_time*1000:.2f}ms")
    
    # Test database query speed
    start_time = time.perf_counter()
    from django.db import connection
    with connection.cursor() as cursor:
        cursor.execute("SELECT 1")
        cursor.fetchone()
    db_time = time.perf_counter() - start_time
    print(f"Simple DB query: {db_time*1000:.2f}ms")
    
    # Test cache access speed
    if ConfigToolkit.cache_backend == 'redis':
        start_time = time.perf_counter()
        from django.core.cache import cache
        cache.set('perf_test', 'value', 10)
        cache.get('perf_test')
        cache_time = time.perf_counter() - start_time
        print(f"Cache roundtrip: {cache_time*1000:.2f}ms")
```

## 🏷️ Metadata
**Tags**: `production, deployment, security, performance, monitoring, troubleshooting`  
**Added in**: `v4.0`  
**Performance**: `%%PERFORMANCE:CRITICAL%%` - Production optimization guide  
**Security**: `%%SECURITY:CRITICAL%%` - Production security hardening  
**Complexity**: `%%COMPLEXITY:MODERATE%%` - Production deployment complexity  
%%AI_HINT: This is the complete production deployment guide with security and performance optimization%%

## ✅ Quality Gates
- [ ] All security checks pass before deployment
- [ ] Performance benchmarks met in production
- [ ] Health checks and monitoring configured
- [ ] Rollback procedures tested and documented
- [ ] Production troubleshooting tools available

**Next**: See [Troubleshooting](./troubleshooting.md) for detailed issue resolution!
