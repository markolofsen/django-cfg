# 🌍 Environment Setup - Auto-Detection & Configuration %%PRIORITY:HIGH%%

## 🎯 Quick Summary
Complete guide for environment setup, detection, and configuration management across development, production, and Docker environments with zero manual intervention.

## 📋 Table of Contents
1. [Environment Detection](#environment-detection)
2. [Environment Files](#environment-files)
3. [Variable Naming Convention](#variable-naming-convention)
4. [Docker Integration](#docker-integration)
5. [Production Security](#production-security)
6. [Troubleshooting](#troubleshooting)

## 🔑 Key Concepts at a Glance
- **Auto-detection**: Environment automatically detected based on context
- **Zero configuration**: Works out of the box with sensible defaults
- **Security by default**: Production settings are secure by default
- **Docker awareness**: Automatic container detection and path resolution
- **Type safety**: All environment variables validated with Pydantic

## 🚀 Environment Detection

### Automatic Detection Logic
```python
# ConfigToolkit automatically detects environment
from api.config import ConfigToolkit

# Environment detection happens transparently
print(f"Environment: {ConfigToolkit.environment}")
print(f"Is Production: {ConfigToolkit.is_production}")
print(f"Is Development: {ConfigToolkit.is_development}")
print(f"Is Docker: {ConfigToolkit.is_docker}")
```

### Detection Rules
```python
def detect_environment():
    """Automatic environment detection rules."""
    
    # 1. Check explicit environment variable
    django_env = os.getenv('DJANGO_ENV', '').lower()
    if django_env in ['production', 'prod']:
        return 'production'
    elif django_env in ['development', 'dev']:
        return 'development'
    elif django_env in ['testing', 'test']:
        return 'testing'
    
    # 2. Check DEBUG setting
    debug = os.getenv('DEBUG', 'true').lower()
    if debug in ['false', '0', 'no']:
        return 'production'
    
    # 3. Check for production indicators
    if any([
        os.getenv('HEROKU_APP_NAME'),          # Heroku
        os.getenv('AWS_LAMBDA_FUNCTION_NAME'), # AWS Lambda
        os.getenv('GOOGLE_CLOUD_PROJECT'),     # Google Cloud
        os.getenv('RAILWAY_ENVIRONMENT'),      # Railway
    ]):
        return 'production'
    
    # 4. Check Docker environment
    if Path('/.dockerenv').exists() or os.getenv('DOCKER'):
        return 'docker'
    
    # 5. Default to development
    return 'development'
```

### Environment Properties
```python
# All environment information available through ConfigToolkit
class EnvironmentInfo:
    """Complete environment information."""
    
    environment: str              # 'development', 'production', 'testing', 'docker'
    is_production: bool          # True if production environment
    is_development: bool         # True if development environment
    is_testing: bool             # True if testing environment
    is_docker: bool              # True if running in Docker container
    
    # Path information
    base_dir: Path               # Application base directory
    project_root: Path           # Project root directory
    data_dir: Path               # Data storage directory
    logs_dir: Path               # Logs directory
    media_dir: Path              # Media files directory
    static_dir: Path             # Static files directory
    
    # Runtime information
    python_version: str          # Python version string
    django_version: str          # Django version string
    platform: str                # Operating system platform
```

## 📁 Environment Files

### File Priority Order
```python
# Environment files loaded in priority order:
env_file_priority = [
    '.env.local',          # Highest priority (local overrides)
    '.env.{environment}',  # Environment-specific (.env.prod, .env.dev)
    '.env',                # General environment file
    'defaults'             # Lowest priority (code defaults)
]
```

### Development Environment (.env.dev)
```bash
# .env.dev - Development configuration
# Auto-loaded when DJANGO_ENV=development or DEBUG=true

# Core Django settings
DEBUG=true
SECRET_KEY=django-insecure-dev-key-change-me-in-production

# Database (SQLite for easy development)
DATABASE_URL=sqlite:///./dev.db

# Security (permissive for development)
CORS_ENABLED=true
CORS_ALLOW_ALL_ORIGINS=true
CSRF_ENABLED=true
SSL_ENABLED=false

# API settings (no rate limiting in dev)
API_PAGE_SIZE=25
API_RATE_LIMIT_ENABLED=false
API_DOCS_ENABLED=true

# Cache (memory cache for development)
CACHE_BACKEND=memory
CACHE_DEFAULT_TIMEOUT=300

# Email (console backend for development)
EMAIL_BACKEND=console
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=true

# Logging (console output)
LOG_LEVEL=DEBUG
LOG_TO_FILE=false

# Feature flags (enable all features in dev)
FEATURE_NEW_UI=true
FEATURE_ANALYTICS=true
```

### Production Environment (.env.prod)
```bash
# .env.prod - Production configuration template
# Copy to .env.prod and set real values

# Core Django settings
DEBUG=false
SECRET_KEY=${SECRET_KEY}  # Set from secure environment variable
DJANGO_ENV=production

# Database (PostgreSQL with SSL)
DATABASE_URL=${DATABASE_URL}
DATABASE_SSL_REQUIRED=true
DATABASE_MAX_CONNECTIONS=20

# Security (strict for production)
ALLOWED_HOSTS=${ALLOWED_HOSTS}
CORS_ENABLED=false
CSRF_ENABLED=true
SSL_ENABLED=true
SECURE_SSL_REDIRECT=true
HSTS_ENABLED=true

# API settings (rate limiting enabled)
API_PAGE_SIZE=50
API_RATE_LIMIT_ENABLED=true
API_DOCS_ENABLED=false

# Cache (Redis for production)
CACHE_BACKEND=redis
CACHE_REDIS_URL=${REDIS_URL}
CACHE_DEFAULT_TIMEOUT=3600

# Email (SMTP for production)
EMAIL_BACKEND=smtp
EMAIL_HOST=${EMAIL_HOST}
EMAIL_PORT=${EMAIL_PORT}
EMAIL_HOST_USER=${EMAIL_HOST_USER}
EMAIL_HOST_PASSWORD=${EMAIL_HOST_PASSWORD}
EMAIL_USE_TLS=true

# Logging (file and external service)
LOG_LEVEL=INFO
LOG_TO_FILE=true
LOG_EXTERNAL_URL=${LOG_EXTERNAL_URL}

# Feature flags (controlled rollout)
FEATURE_NEW_UI=${FEATURE_NEW_UI:-false}
FEATURE_ANALYTICS=true

# Monitoring
SENTRY_DSN=${SENTRY_DSN}
MONITORING_ENABLED=true
```

### Testing Environment (.env.test)
```bash
# .env.test - Testing configuration
# Auto-loaded during test runs

# Core Django settings
DEBUG=true
SECRET_KEY=test-secret-key-not-for-production
DJANGO_ENV=testing

# Database (in-memory SQLite)
DATABASE_URL=sqlite:///:memory:

# Security (minimal for testing)
CORS_ENABLED=true
CSRF_ENABLED=false
SSL_ENABLED=false

# API settings (no limits for testing)
API_PAGE_SIZE=10
API_RATE_LIMIT_ENABLED=false
API_DOCS_ENABLED=false

# Cache (memory for testing)
CACHE_BACKEND=memory
CACHE_DEFAULT_TIMEOUT=1

# Email (memory backend for testing)
EMAIL_BACKEND=locmem

# Disable external services
MONITORING_ENABLED=false
FEATURE_NEW_UI=true
FEATURE_ANALYTICS=false
```

## 🏷️ Variable Naming Convention

### Standard Naming Pattern
```bash
# Use uppercase with underscores
# Group related settings with prefixes

# Core Django settings
DEBUG=true
SECRET_KEY=your-secret-key
DJANGO_ENV=development

# Database settings (DATABASE_ prefix)
DATABASE_URL=postgresql://user:pass@localhost:5432/myapp
DATABASE_MAX_CONNECTIONS=10
DATABASE_SSL_REQUIRED=false

# Security settings (SECURITY_ prefix when needed)
CORS_ENABLED=true
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8080
CSRF_ENABLED=true
SSL_ENABLED=false

# API settings (API_ prefix)
API_PAGE_SIZE=25
API_RATE_LIMIT_ENABLED=false
API_DOCS_ENABLED=true

# Cache settings (CACHE_ prefix)
CACHE_BACKEND=redis
CACHE_REDIS_URL=redis://localhost:6379/0
CACHE_DEFAULT_TIMEOUT=300

# Email settings (EMAIL_ prefix)
EMAIL_BACKEND=smtp
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=true
```

### Type Conversion Rules
```python
# ConfigToolkit automatically converts environment variable types
conversion_rules = {
    # Boolean conversion
    'true': True, 'false': False,
    '1': True, '0': False,
    'yes': True, 'no': False,
    'on': True, 'off': False,
    
    # Integer conversion
    '123': 123,
    '0': 0,
    
    # Float conversion  
    '123.45': 123.45,
    
    # List conversion (comma-separated)
    'item1,item2,item3': ['item1', 'item2', 'item3'],
    
    # Path conversion
    '/path/to/file': Path('/path/to/file'),
    
    # URL conversion (validated format)
    'postgresql://user:pass@host:5432/db': 'postgresql://user:pass@host:5432/db',
}
```

### Environment Variable Examples
```python
# Example of all supported environment variable types
class EnvironmentExamples:
    """Examples of environment variable usage."""
    
    # String values
    SECRET_KEY: str = "django-secret-key"
    DATABASE_URL: str = "postgresql://user:pass@localhost:5432/myapp"
    
    # Boolean values (multiple formats supported)
    DEBUG: bool = True          # DEBUG=true
    CORS_ENABLED: bool = False  # CORS_ENABLED=false
    SSL_ENABLED: bool = True    # SSL_ENABLED=1
    
    # Integer values
    API_PAGE_SIZE: int = 25           # API_PAGE_SIZE=25
    DATABASE_MAX_CONNECTIONS: int = 10 # DATABASE_MAX_CONNECTIONS=10
    
    # Float values
    CACHE_DEFAULT_TIMEOUT: float = 300.5  # CACHE_DEFAULT_TIMEOUT=300.5
    
    # List values (comma-separated)
    ALLOWED_HOSTS: List[str] = ["localhost", "127.0.0.1"]
    # ALLOWED_HOSTS=localhost,127.0.0.1
    
    # Path values
    MEDIA_DIR: Path = Path("/app/media")  # MEDIA_DIR=/app/media
    
    # Optional values
    REDIS_URL: Optional[str] = None  # REDIS_URL not set
```

## 🐳 Docker Integration

### Dockerfile Environment Setup
```dockerfile
# Dockerfile with environment configuration
FROM python:3.11-slim

# Set environment variables for Docker detection
ENV DOCKER=true
ENV PYTHONUNBUFFERED=1

# Create application user and directories
RUN useradd --create-home --shell /bin/bash app
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .
RUN chown -R app:app /app

# Switch to application user
USER app

# Environment-specific configuration will be loaded automatically
# No need to set DJANGO_ENV - ConfigToolkit detects Docker automatically

# Health check using configuration validation
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "from api.config import ConfigToolkit; ConfigToolkit.validate_all_configurations()"

# Start application
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "api.wsgi:application"]
```

### Docker Compose Configuration
```yaml
# docker-compose.yml with environment configuration
version: '3.8'

services:
  web:
    build: .
    ports:
      - "8000:8000"
    environment:
      # Django configuration
      - DJANGO_ENV=production
      - DEBUG=false
      - SECRET_KEY=${SECRET_KEY}
      
      # Database configuration
      - DATABASE_URL=postgresql://postgres:password@db:5432/myapp
      - DATABASE_MAX_CONNECTIONS=20
      
      # Cache configuration
      - CACHE_BACKEND=redis
      - CACHE_REDIS_URL=redis://redis:6379/0
      
      # Security configuration
      - CORS_ENABLED=false
      - SSL_ENABLED=true
      
      # API configuration
      - API_RATE_LIMIT_ENABLED=true
      - API_DOCS_ENABLED=false
    
    depends_on:
      - db
      - redis
    
    # Health check
    healthcheck:
      test: ["CMD", "python", "-c", "from api.config import ConfigToolkit; ConfigToolkit.validate_all_configurations()"]
      interval: 30s
      timeout: 10s
      retries: 3

  db:
    image: postgres:15
    environment:
      - POSTGRES_DB=myapp
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=password
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data

volumes:
  postgres_data:
  redis_data:
```

### Docker Environment Detection
```python
# ConfigToolkit automatically detects Docker environment
def detect_docker_environment():
    """Docker environment detection logic."""
    
    docker_indicators = [
        # Standard Docker indicators
        Path('/.dockerenv').exists(),
        os.getenv('DOCKER', '').lower() == 'true',
        
        # Container runtime indicators
        Path('/proc/1/cgroup').exists() and 'docker' in Path('/proc/1/cgroup').read_text(),
        
        # Kubernetes indicators
        os.getenv('KUBERNETES_SERVICE_HOST') is not None,
        
        # Common container platforms
        os.getenv('RAILWAY_ENVIRONMENT') is not None,
        os.getenv('HEROKU_DYNO_ID') is not None,
    ]
    
    return any(docker_indicators)

# Docker-specific path resolution
def resolve_docker_paths():
    """Resolve paths for Docker environment."""
    
    if ConfigToolkit.is_docker:
        return {
            'base_dir': Path('/app'),
            'data_dir': Path('/app/data'),
            'logs_dir': Path('/app/logs'),
            'media_dir': Path('/app/media'),
            'static_dir': Path('/app/staticfiles'),
        }
    else:
        # Local development paths
        base_dir = Path(__file__).parent.parent
        return {
            'base_dir': base_dir,
            'data_dir': base_dir / 'data',
            'logs_dir': base_dir / 'logs',
            'media_dir': base_dir / 'media',
            'static_dir': base_dir / 'staticfiles',
        }
```

## 🔐 Production Security

### Secure Environment Variable Management
```python
# Production security validation
class ProductionSecurityValidator:
    """Validate production environment security."""
    
    @classmethod
    def validate_production_config(cls):
        """Validate that production configuration is secure."""
        
        security_checks = []
        
        # Check 1: DEBUG must be False
        if ConfigToolkit.debug:
            security_checks.append("DEBUG=True in production - SECURITY RISK!")
        
        # Check 2: SECRET_KEY must be strong
        secret_key = ConfigToolkit.secret_key
        if len(secret_key) < 32:
            security_checks.append("SECRET_KEY too short - minimum 32 characters")
        if secret_key.startswith('django-insecure'):
            security_checks.append("SECRET_KEY is default insecure key")
        
        # Check 3: Database SSL in production
        if ConfigToolkit.is_production and not ConfigToolkit.database_ssl_required:
            security_checks.append("Database SSL not required in production")
        
        # Check 4: HTTPS enforcement
        if ConfigToolkit.is_production and not ConfigToolkit.ssl_enabled:
            security_checks.append("SSL not enabled in production")
        
        # Check 5: CORS configuration
        if ConfigToolkit.cors_enabled and ConfigToolkit.cors_allow_all_origins:
            security_checks.append("CORS allows all origins - potential security risk")
        
        # Check 6: Allowed hosts configured
        if not ConfigToolkit.allowed_hosts or ConfigToolkit.allowed_hosts == ['*']:
            security_checks.append("ALLOWED_HOSTS not properly configured")
        
        return security_checks
    
    @classmethod
    def enforce_production_security(cls):
        """Enforce production security requirements."""
        
        if not ConfigToolkit.is_production:
            return True
        
        security_violations = cls.validate_production_config()
        
        if security_violations:
            error_message = "Production security violations detected:\n"
            error_message += "\n".join(f"- {violation}" for violation in security_violations)
            raise SecurityError(error_message)
        
        return True
```

### Environment Secrets Management
```bash
# Production environment variables should be set via secure methods

# AWS Systems Manager Parameter Store
export SECRET_KEY=$(aws ssm get-parameter --name "/myapp/prod/secret-key" --with-decryption --query "Parameter.Value" --output text)
export DATABASE_URL=$(aws ssm get-parameter --name "/myapp/prod/database-url" --with-decryption --query "Parameter.Value" --output text)

# HashiCorp Vault
export SECRET_KEY=$(vault kv get -field=secret-key secret/myapp/prod)
export DATABASE_URL=$(vault kv get -field=database-url secret/myapp/prod)

# Kubernetes Secrets
# Values injected automatically via pod environment

# Docker Secrets
export SECRET_KEY=$(cat /run/secrets/secret_key)
export DATABASE_URL=$(cat /run/secrets/database_url)
```

## 🐛 Troubleshooting

### Environment Detection Issues
```python
# Debug environment detection
def debug_environment_detection():
    """Debug environment detection logic."""
    
    print("🔍 Environment Detection Debug")
    print("=" * 40)
    
    # Check environment variables
    env_vars = [
        'DJANGO_ENV', 'DEBUG', 'DOCKER',
        'HEROKU_APP_NAME', 'AWS_LAMBDA_FUNCTION_NAME',
        'GOOGLE_CLOUD_PROJECT', 'RAILWAY_ENVIRONMENT'
    ]
    
    print("Environment Variables:")
    for var in env_vars:
        value = os.getenv(var)
        print(f"  {var}: {value}")
    
    # Check file indicators
    print("\nFile Indicators:")
    docker_file = Path('/.dockerenv')
    print(f"  /.dockerenv exists: {docker_file.exists()}")
    
    # Check final detection
    print("\nDetection Results:")
    print(f"  Environment: {ConfigToolkit.environment}")
    print(f"  Is Production: {ConfigToolkit.is_production}")
    print(f"  Is Development: {ConfigToolkit.is_development}")
    print(f"  Is Docker: {ConfigToolkit.is_docker}")

# Run debug
debug_environment_detection()
```

### Environment File Loading Issues
```python
# Debug environment file loading
def debug_env_file_loading():
    """Debug environment file loading process."""
    
    print("🔍 Environment File Loading Debug")
    print("=" * 40)
    
    # Check which files exist
    env_files = ['.env.local', '.env.dev', '.env.prod', '.env.test', '.env']
    
    print("Environment Files:")
    for env_file in env_files:
        file_path = Path(env_file)
        if file_path.exists():
            print(f"  ✅ {env_file}: exists ({file_path.stat().st_size} bytes)")
            # Show first few lines
            with open(file_path) as f:
                lines = f.readlines()[:5]
                for line in lines:
                    if line.strip() and not line.startswith('#'):
                        print(f"     {line.strip()}")
        else:
            print(f"  ❌ {env_file}: not found")
    
    # Check which file was loaded
    print(f"\nLoaded Environment: {ConfigToolkit.environment}")
    print(f"Expected File: .env.{ConfigToolkit.environment}")
```

### Configuration Validation Issues
```python
# Debug configuration validation
def debug_configuration_validation():
    """Debug configuration validation issues."""
    
    print("🔍 Configuration Validation Debug")
    print("=" * 40)
    
    try:
        # Test each configuration component
        components = [
            ('environment', lambda: ConfigToolkit.environment),
            ('debug', lambda: ConfigToolkit.debug),
            ('secret_key', lambda: ConfigToolkit.secret_key),
            ('database_url', lambda: ConfigToolkit.database_url),
            ('allowed_hosts', lambda: ConfigToolkit.allowed_hosts),
        ]
        
        for name, getter in components:
            try:
                value = getter()
                print(f"  ✅ {name}: {type(value).__name__} = {str(value)[:50]}...")
            except Exception as e:
                print(f"  ❌ {name}: {e}")
        
        # Test Django settings generation
        try:
            django_settings = ConfigToolkit.get_django_settings()
            print(f"  ✅ Django settings: {len(django_settings)} keys generated")
        except Exception as e:
            print(f"  ❌ Django settings: {e}")
    
    except Exception as e:
        print(f"❌ Configuration validation failed: {e}")
```

### Performance Issues
```python
# Debug performance issues
def debug_performance_issues():
    """Debug configuration performance issues."""
    
    import time
    import psutil
    
    print("🔍 Configuration Performance Debug")
    print("=" * 40)
    
    # Memory usage before
    process = psutil.Process()
    memory_before = process.memory_info().rss / 1024 / 1024
    
    # Initialization time
    start_time = time.perf_counter()
    from api.config import ConfigToolkit
    _ = ConfigToolkit.debug  # Trigger initialization
    init_time = time.perf_counter() - start_time
    
    # Memory usage after
    memory_after = process.memory_info().rss / 1024 / 1024
    
    # Access time
    start_time = time.perf_counter()
    for _ in range(1000):
        _ = ConfigToolkit.debug
        _ = ConfigToolkit.database_url
    access_time = time.perf_counter() - start_time
    
    print("Performance Metrics:")
    print(f"  Initialization: {init_time*1000:.2f}ms")
    print(f"  Memory increase: {memory_after - memory_before:.2f}MB")
    print(f"  1000 accesses: {access_time*1000:.2f}ms")
    
    # Performance targets
    print("\nPerformance Targets:")
    print(f"  Init time: {'✅' if init_time < 0.05 else '❌'} <50ms")
    print(f"  Memory: {'✅' if memory_after - memory_before < 10 else '❌'} <10MB")
    print(f"  Access: {'✅' if access_time < 0.001 else '❌'} <1ms")
```

## 🏷️ Metadata
**Tags**: `environment, setup, detection, docker, security, configuration`  
**Added in**: `v4.0`  
**Performance**: `%%PERFORMANCE:HIGH%%` - Auto-detection with caching  
**Security**: `%%SECURITY:CRITICAL%%` - Production security validation  
**Complexity**: `%%COMPLEXITY:SIMPLE%%` - Zero-configuration setup  
%%AI_HINT: This guide covers complete environment setup with automatic detection%%

## ✅ Quality Gates
- [ ] Environment detection works in all deployment scenarios
- [ ] Environment files follow standard naming conventions
- [ ] Production security validation prevents insecure configurations
- [ ] Docker integration works automatically
- [ ] Troubleshooting tools help diagnose issues quickly

**Next**: See [Custom Configuration](./custom-config.md) for adding application-specific settings!
