# 📦 Configuration Toolkit - Isolated Settings Interface %%PRIORITY:HIGH%%

## 🎯 Quick Summary
Complete documentation for ConfigToolkit - the isolated, type-safe interface for accessing all Django configuration without touching business logic.

## 📋 Table of Contents
1. [Core Concepts](#core-concepts)
2. [Basic Usage](#basic-usage)
3. [Configuration Properties](#configuration-properties)
4. [Advanced Features](#advanced-features)
5. [Performance Patterns](#performance-patterns)
6. [Integration Examples](#integration-examples)

## 🔑 Core Concepts at a Glance
- **ConfigToolkit**: Singleton class providing all configuration access
- **Isolation**: Zero dependencies on business logic or application code
- **Type Safety**: 100% typed with Pydantic validation
- **Performance**: Cached properties, zero validation overhead at runtime
- **Simplicity**: Single import, single interface

## 🚀 Basic Usage

### Import and Initialize
```python
# Single import for all configuration needs
from api.config import ConfigToolkit

# Automatic initialization on first access
debug_mode = ConfigToolkit.debug  # Triggers initialization if needed
```

### Django Settings Integration
```python
# settings.py - Complete Django configuration
from api.config import ConfigToolkit

# One line replacement for entire Django settings
globals().update(ConfigToolkit.get_django_settings())

# Optional: Access specific settings if needed
DEBUG = ConfigToolkit.debug
SECRET_KEY = ConfigToolkit.secret_key
DATABASES = ConfigToolkit.get_databases()
```

### Configuration Access Patterns
```python
# Type-safe property access
def my_view(request):
    # Core Django settings
    if ConfigToolkit.debug:
        logger.debug("Debug mode active")
    
    # Database configuration
    db_url = ConfigToolkit.database_url
    max_connections = ConfigToolkit.database_max_connections
    
    # API configuration
    page_size = ConfigToolkit.api_page_size
    rate_limit = ConfigToolkit.api_rate_limit_enabled
    
    # Security settings
    cors_enabled = ConfigToolkit.cors_enabled
    csrf_protection = ConfigToolkit.csrf_enabled
```

## 📊 Configuration Properties

### Core Django Settings
```python
# Environment and core settings
ConfigToolkit.debug: bool                    # DEBUG setting
ConfigToolkit.secret_key: str               # SECRET_KEY (validated min 32 chars)
ConfigToolkit.allowed_hosts: List[str]      # ALLOWED_HOSTS
ConfigToolkit.is_production: bool           # Environment detection
ConfigToolkit.is_development: bool          # Development mode
ConfigToolkit.is_docker: bool               # Docker container detection

# Paths and directories
ConfigToolkit.base_dir: Path               # Application base directory
ConfigToolkit.media_dir: Path              # Media files directory
ConfigToolkit.static_dir: Path             # Static files directory
ConfigToolkit.logs_dir: Path               # Logs directory
```

### Database Configuration
```python
# Database connection settings
ConfigToolkit.database_url: str             # Primary database URL
ConfigToolkit.database_max_connections: int # Connection pool size (1-50)
ConfigToolkit.database_conn_max_age: int    # Connection lifetime seconds
ConfigToolkit.database_ssl_required: bool   # SSL connection requirement

# Multiple database support
ConfigToolkit.cars_database_url: str        # Cars database URL
ConfigToolkit.analytics_database_url: str   # Analytics database URL
```

### Security Configuration
```python
# CORS settings
ConfigToolkit.cors_enabled: bool            # Enable CORS
ConfigToolkit.cors_allowed_origins: List[str] # Allowed origins
ConfigToolkit.cors_allow_credentials: bool  # Allow credentials

# CSRF protection
ConfigToolkit.csrf_enabled: bool            # Enable CSRF protection
ConfigToolkit.csrf_trusted_origins: List[str] # Trusted origins
ConfigToolkit.csrf_cookie_secure: bool      # Secure CSRF cookies

# SSL/TLS settings
ConfigToolkit.ssl_enabled: bool             # Enable SSL redirect
ConfigToolkit.ssl_redirect: bool            # Force HTTPS redirect
ConfigToolkit.hsts_enabled: bool            # HTTP Strict Transport Security
```

### API Configuration
```python
# REST Framework settings
ConfigToolkit.api_page_size: int            # Default pagination size (1-100)
ConfigToolkit.api_max_page_size: int        # Maximum page size
ConfigToolkit.api_rate_limit_enabled: bool  # Enable rate limiting
ConfigToolkit.api_docs_enabled: bool        # Enable API documentation

# JWT settings
ConfigToolkit.jwt_access_token_lifetime: int # Access token lifetime (seconds)
ConfigToolkit.jwt_refresh_token_lifetime: int # Refresh token lifetime
ConfigToolkit.jwt_algorithm: str            # JWT signing algorithm
```

### Cache Configuration
```python
# Cache backend settings
ConfigToolkit.cache_backend: str            # 'redis' or 'memory'
ConfigToolkit.cache_redis_url: str          # Redis connection URL
ConfigToolkit.cache_default_timeout: int    # Default cache timeout (seconds)
ConfigToolkit.cache_key_prefix: str         # Cache key prefix
```

### Email Configuration
```python
# Email backend settings
ConfigToolkit.email_backend: str            # Email backend class
ConfigToolkit.email_host: str               # SMTP host
ConfigToolkit.email_port: int               # SMTP port (1-65535)
ConfigToolkit.email_use_tls: bool           # Enable TLS
ConfigToolkit.email_default_from: str       # Default sender email
```

## 🧩 Advanced Features

### Environment-Specific Configuration
```python
# Automatic environment detection and configuration
class ConfigToolkit:
    @classmethod
    def get_environment_info(cls) -> Dict[str, Any]:
        """Get detailed environment information."""
        return {
            'environment': cls.environment,
            'is_production': cls.is_production,
            'is_development': cls.is_development,
            'is_docker': cls.is_docker,
            'python_version': cls.python_version,
            'django_version': cls.django_version,
        }
    
    @classmethod  
    def get_performance_info(cls) -> Dict[str, Any]:
        """Get configuration performance metrics."""
        return {
            'initialization_time_ms': cls._initialization_time,
            'memory_usage_mb': cls._memory_usage,
            'cached_properties': len(cls._property_cache),
            'total_configurations': cls._config_count,
        }
```

### Custom Configuration Registration
```python
# Add application-specific configuration
from api.config import ConfigToolkit
from api.config.base import BaseConfig
from pydantic import Field

class PaymentConfig(BaseConfig):
    """Payment gateway configuration."""
    stripe_api_key: str = Field(description="Stripe API key")
    stripe_webhook_secret: str = Field(description="Webhook secret")
    timeout_seconds: int = Field(default=30, ge=5, le=120)

# Register custom configuration
ConfigToolkit.register_config('payment', PaymentConfig)

# Access custom configuration
stripe_key = ConfigToolkit.payment.stripe_api_key
webhook_secret = ConfigToolkit.payment.stripe_webhook_secret
```

### Configuration Validation
```python
# Manual validation and health checks
@classmethod
def validate_all_configurations(cls) -> bool:
    """Validate all configurations for current environment."""
    try:
        # Validate core configurations
        cls._validate_core_config()
        cls._validate_database_config()
        cls._validate_security_config()
        
        # Validate custom configurations
        for name, config in cls._custom_configs.items():
            config.validate_for_environment(cls.environment)
        
        return True
    except ValidationError as e:
        logger.error(f"Configuration validation failed: {e}")
        return False

# Health check endpoint
def config_health_check() -> Dict[str, Any]:
    """Get configuration health status."""
    return {
        'status': 'healthy' if ConfigToolkit.validate_all_configurations() else 'unhealthy',
        'environment': ConfigToolkit.environment,
        'debug': ConfigToolkit.debug,
        'database_connected': ConfigToolkit.test_database_connection(),
        'cache_available': ConfigToolkit.test_cache_connection(),
    }
```

## ⚡ Performance Patterns

### Initialization Performance
```python
import time
from api.config import ConfigToolkit

# Measure initialization performance
start_time = time.perf_counter()
debug_mode = ConfigToolkit.debug  # Triggers initialization
initialization_time = time.perf_counter() - start_time

print(f"ConfigToolkit initialization: {initialization_time*1000:.2f}ms")
# Target: <50ms

# Get performance metrics
perf_info = ConfigToolkit.get_performance_info()
print(f"Memory usage: {perf_info['memory_usage_mb']:.2f}MB")
print(f"Cached properties: {perf_info['cached_properties']}")
```

### Runtime Access Optimization
```python
# Optimized configuration access patterns
class UserService:
    def __init__(self):
        # Cache frequently accessed configuration at initialization
        self.debug_mode = ConfigToolkit.debug
        self.page_size = ConfigToolkit.api_page_size
        self.rate_limit_enabled = ConfigToolkit.api_rate_limit_enabled
    
    def get_users(self, page: int = 1) -> List[User]:
        """Get users with cached configuration."""
        # Use cached values instead of property access in loops
        if self.debug_mode:
            logger.debug(f"Fetching users page {page}")
        
        return User.objects.all()[
            (page-1) * self.page_size : page * self.page_size
        ]
```

### Memory Usage Optimization
```python
# Memory-efficient configuration access
import weakref

class ConfigurationCache:
    """Memory-efficient configuration caching."""
    
    def __init__(self):
        self._cache = weakref.WeakValueDictionary()
        self._access_count = {}
    
    def get_config_value(self, key: str) -> Any:
        """Get configuration value with memory-efficient caching."""
        if key in self._cache:
            self._access_count[key] = self._access_count.get(key, 0) + 1
            return self._cache[key]
        
        # Get value from ConfigToolkit
        value = getattr(ConfigToolkit, key)
        
        # Cache only frequently accessed values
        if self._access_count.get(key, 0) > 10:
            self._cache[key] = value
        
        return value
```

## 🔗 Integration Examples

### Django Views Integration
```python
from django.http import JsonResponse
from django.views import View
from api.config import ConfigToolkit

class CarListView(View):
    """Car listing view with configuration integration."""
    
    def get(self, request):
        # Type-safe configuration access
        page_size = ConfigToolkit.api_page_size
        debug_mode = ConfigToolkit.debug
        
        # Apply configuration to business logic
        cars = Car.objects.all()[:page_size]
        
        # Debug information if enabled
        response_data = {
            'cars': [car.to_dict() for car in cars],
            'page_size': page_size,
        }
        
        if debug_mode:
            response_data['debug'] = {
                'query_count': len(connection.queries),
                'environment': ConfigToolkit.environment,
            }
        
        return JsonResponse(response_data)
```

### Database Integration
```python
from django.db import connections
from api.config import ConfigToolkit

class DatabaseService:
    """Database service with configuration integration."""
    
    def __init__(self):
        self.default_db = connections['default']
        self.cars_db = connections.get('cars_db') if ConfigToolkit.cars_database_url else None
    
    def get_connection_info(self) -> Dict[str, Any]:
        """Get database connection information."""
        return {
            'default_db': {
                'url': ConfigToolkit.database_url,
                'max_connections': ConfigToolkit.database_max_connections,
                'ssl_required': ConfigToolkit.database_ssl_required,
            },
            'cars_db': {
                'url': ConfigToolkit.cars_database_url,
                'enabled': self.cars_db is not None,
            } if ConfigToolkit.cars_database_url else None,
        }
```

### API Middleware Integration
```python
from django.http import HttpResponse
from api.config import ConfigToolkit

class APIConfigurationMiddleware:
    """Middleware that applies configuration to API requests."""
    
    def __init__(self, get_response):
        self.get_response = get_response
        # Cache configuration at middleware initialization
        self.cors_enabled = ConfigToolkit.cors_enabled
        self.rate_limit_enabled = ConfigToolkit.api_rate_limit_enabled
        self.debug_mode = ConfigToolkit.debug
    
    def __call__(self, request):
        # Apply CORS headers if enabled
        if self.cors_enabled and request.path.startswith('/api/'):
            response = self.get_response(request)
            response['Access-Control-Allow-Origin'] = '*'
            return response
        
        response = self.get_response(request)
        
        # Add debug headers if enabled
        if self.debug_mode:
            response['X-Debug-Environment'] = ConfigToolkit.environment
            response['X-Debug-Version'] = ConfigToolkit.version
        
        return response
```

### Testing Integration
```python
import pytest
from api.config import ConfigToolkit

@pytest.fixture
def test_configuration():
    """Test configuration fixture."""
    # Override configuration for testing
    original_values = {}
    test_overrides = {
        'debug': True,
        'database_url': 'sqlite:///:memory:',
        'api_rate_limit_enabled': False,
        'email_backend': 'django.core.mail.backends.locmem.EmailBackend',
    }
    
    # Store original values
    for key in test_overrides:
        original_values[key] = getattr(ConfigToolkit, key)
    
    # Apply test overrides
    ConfigToolkit.override(test_overrides)
    
    yield ConfigToolkit
    
    # Restore original values
    ConfigToolkit.reset_overrides()

def test_car_listing_with_config(test_configuration):
    """Test car listing with test configuration."""
    assert test_configuration.debug is True
    assert 'memory' in test_configuration.database_url
    
    # Test business logic with test configuration
    response = client.get('/api/cars/')
    assert response.status_code == 200
```

## ❌ Common Mistakes & Solutions

### Mistake: Direct Configuration Access in Loops
```python
# ❌ WRONG - Configuration access in loop
def process_cars(cars):
    for car in cars:
        if ConfigToolkit.debug:  # Property access in loop!
            logger.debug(f"Processing car {car.id}")

# ✅ CORRECT - Cache configuration outside loop  
def process_cars(cars):
    debug_mode = ConfigToolkit.debug  # Cache once
    for car in cars:
        if debug_mode:
            logger.debug(f"Processing car {car.id}")
```

### Mistake: Configuration Logic in Business Code
```python
# ❌ WRONG - Configuration logic mixed with business logic
def send_email(user, message):
    if ConfigToolkit.environment == 'production':
        if ConfigToolkit.email_backend == 'smtp':
            # Complex configuration logic in business method
            smtp_client = SMTPClient(
                host=ConfigToolkit.email_host,
                port=ConfigToolkit.email_port,
                use_tls=ConfigToolkit.email_use_tls
            )
            smtp_client.send(user.email, message)

# ✅ CORRECT - Configuration handled in service layer
class EmailService:
    def __init__(self):
        # Configuration handled once in service initialization
        self.backend = self._create_email_backend()
    
    def _create_email_backend(self):
        if ConfigToolkit.email_backend == 'smtp':
            return SMTPBackend(
                host=ConfigToolkit.email_host,
                port=ConfigToolkit.email_port,
                use_tls=ConfigToolkit.email_use_tls
            )
        else:
            return ConsoleBackend()
    
    def send_email(self, user, message):
        # Simple business logic, configuration abstracted away
        self.backend.send(user.email, message)
```

## 🧪 Testing Patterns

### Configuration Override Testing
```python
def test_with_custom_config():
    """Test with custom configuration values."""
    # Override specific configuration for test
    ConfigToolkit.override({
        'api_page_size': 10,
        'debug': True,
        'cors_enabled': False,
    })
    
    # Test behavior with overridden configuration
    response = client.get('/api/cars/')
    data = response.json()
    
    # Verify configuration was applied
    assert len(data['cars']) <= 10  # Page size respected
    assert 'debug' in data  # Debug info included
    
    # Reset configuration
    ConfigToolkit.reset_overrides()
```

### Performance Testing
```python
def test_configuration_performance():
    """Test configuration access performance."""
    import time
    
    # Test initialization performance
    start_time = time.perf_counter()
    _ = ConfigToolkit.debug  # Trigger initialization
    init_time = time.perf_counter() - start_time
    assert init_time < 0.05, f"Initialization too slow: {init_time*1000:.2f}ms"
    
    # Test runtime access performance
    start_time = time.perf_counter()
    for _ in range(1000):
        _ = ConfigToolkit.debug
        _ = ConfigToolkit.database_url
        _ = ConfigToolkit.api_page_size
    access_time = time.perf_counter() - start_time
    assert access_time < 0.001, f"Access too slow: {access_time*1000:.2f}ms"
```

## 🏷️ Metadata
**Tags**: `config-toolkit, interface, isolation, type-safety, performance`  
**Added in**: `v4.0`  
**Dependencies**: `pydantic>=2.0`, `pydantic-settings>=2.0`  
**Performance**: `%%PERFORMANCE:HIGH%%` - <50ms init, instant access  
**Security**: `%%SECURITY:HIGH%%` - Input validation, no secrets exposure  
**Complexity**: `%%COMPLEXITY:SIMPLE%%` - Single interface, clear API  
%%AI_HINT: This is the main isolated interface for all configuration access%%

## ✅ Quality Gates
- [ ] All configuration access goes through ConfigToolkit
- [ ] No business logic in configuration classes
- [ ] Configuration properties are cached for performance
- [ ] Type annotations are 100% complete
- [ ] Integration examples work out of the box

**Next**: See [Environment Setup](./environment-setup.md) for environment configuration!
