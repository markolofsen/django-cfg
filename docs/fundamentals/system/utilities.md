---
title: Utilities - Smart Defaults & Version Management
description: Django-CFG utilities fundamentals. Comprehensive guide to utilities - smart defaults & version management with Pydantic validation, type safety, and enterprise 
sidebar_label: Utilities
sidebar_position: 7
keywords:
  - django-cfg utilities
  - django utilities
---

# Utilities - Smart Defaults & Version Management

Django-CFG provides a comprehensive **utility system** with smart defaults and version management to enhance developer experience and ensure compatibility.

## Overview

The Utilities system includes:

- **Smart Defaults** - Environment-aware automatic configuration
- **Version Management** - Python version checking and compatibility
- **Performance Optimization** - Efficient configuration access
- **Type Safety** - Full type hints and validation
- **Developer Experience** - Beautiful error messages and helpful tools

## Smart Defaults System

### Environment-Aware Configuration

Smart Defaults automatically configure services based on your environment:

```python
from django_cfg.utils.smart_defaults import SmartDefaults
from django_cfg import CacheConfig, EmailConfig, DatabaseConfig

# Cache configuration with smart defaults
cache_config = CacheConfig(backend="auto")  # Will be determined automatically

# Smart defaults configure based on environment
optimized_cache = SmartDefaults.configure_cache_backend(
    cache_config=cache_config,
    environment="production",  # or "development", "testing"
    debug=False
)

# Result: Redis in production, LocMem in development
print(optimized_cache.backend)  # "django_redis.cache.RedisCache" in prod
```

### Automatic Service Detection

Smart defaults detect available services and configure accordingly:

```python
# Email configuration with smart defaults
email_config = EmailConfig(backend="auto")

# Automatically detects and configures best available backend
optimized_email = SmartDefaults.configure_email_backend(
    email_config=email_config,
    environment="production",
    debug=False
)

# Detection logic:
# 1. SendGrid API key available? → Use SendGrid
# 2. SMTP settings configured? → Use SMTP
# 3. Development mode? → Use console backend
# 4. Testing mode? → Use locmem backend
```

### Database Optimization

Smart defaults optimize database configuration:

```python
# Database configuration with smart defaults
db_config = DatabaseConfig(
    engine="django.db.backends.postgresql",
    name="myapp",
    host="localhost"
)

# Optimize for environment
optimized_db = SmartDefaults.configure_database(
    db_config=db_config,
    environment="production",
    debug=False
)

# Automatic optimizations:
# - Connection pooling in production
# - Query logging in development
# - Test database isolation in testing
# - Performance tuning based on environment
```

### Security Defaults

Automatically configure security settings:

```python
# Security configuration with smart defaults
security_config = SmartDefaults.configure_security(
    environment="production",
    debug=False,
    domain="myapp.com"
)

# Automatic security settings:
# - HTTPS enforcement in production
# - Secure cookies in production
# - CSRF protection
# - XSS protection
# - Content type sniffing protection
```

### Smart Defaults API

Complete Smart Defaults API:

```python
class SmartDefaults:
    """Environment-aware smart defaults for Django configuration."""
    
    @classmethod
    def configure_cache_backend(
        cls,
        cache_config: CacheConfig,
        environment: Optional[str] = None,
        debug: bool = False
    ) -> CacheConfig:
        """Configure cache backend with environment-aware defaults."""
        
        if environment == "production":
            # Production: Use Redis with connection pooling
            if cls._is_redis_available():
                cache_config.backend = "django_redis.cache.RedisCache"
                cache_config.location = "redis://localhost:6379/1"
                cache_config.options = {
                    "CONNECTION_POOL_KWARGS": {"max_connections": 50},
                    "COMPRESSOR": "django_redis.compressors.zlib.ZlibCompressor",
                }
            else:
                # Fallback to database cache
                cache_config.backend = "django.core.cache.backends.db.DatabaseCache"
                cache_config.location = "cache_table"
        
        elif environment == "development" or debug:
            # Development: Use local memory cache
            cache_config.backend = "django.core.cache.backends.locmem.LocMemCache"
            cache_config.location = "dev-cache"
        
        elif environment == "testing":
            # Testing: Use dummy cache (no caching)
            cache_config.backend = "django.core.cache.backends.dummy.DummyCache"
        
        return cache_config
    
    @classmethod
    def configure_email_backend(
        cls,
        email_config: EmailConfig,
        environment: Optional[str] = None,
        debug: bool = False
    ) -> EmailConfig:
        """Configure email backend with environment-aware defaults."""
        
        if environment == "production":
            # Production: Use SendGrid or SMTP
            if email_config.sendgrid_api_key:
                email_config.backend = "sendgrid"
            elif cls._is_smtp_configured(email_config):
                email_config.backend = "django.core.mail.backends.smtp.EmailBackend"
            else:
                raise ConfigurationError("No email backend configured for production")
        
        elif environment == "development" or debug:
            # Development: Use console backend
            email_config.backend = "django.core.mail.backends.console.EmailBackend"
        
        elif environment == "testing":
            # Testing: Use locmem backend
            email_config.backend = "django.core.mail.backends.locmem.EmailBackend"
        
        return email_config
    
    @classmethod
    def configure_logging(
        cls,
        environment: Optional[str] = None,
        debug: bool = False
    ) -> Dict[str, Any]:
        """Configure logging with environment-aware defaults."""
        
        if environment == "production":
            return {
                'version': 1,
                'disable_existing_loggers': False,
                'formatters': {
                    'json': {
                        'format': '{"time": "%(asctime)s", "level": "%(levelname)s", "message": "%(message)s"}',
                    },
                },
                'handlers': {
                    'file': {
                        'level': 'INFO',
                        'class': 'logging.handlers.RotatingFileHandler',
                        'filename': 'logs/django.log',
                        'maxBytes': 1024*1024*10,  # 10MB
                        'backupCount': 5,
                        'formatter': 'json',
                    },
                },
                'root': {
                    'handlers': ['file'],
                    'level': 'INFO',
                },
            }
        
        elif environment == "development" or debug:
            return {
                'version': 1,
                'disable_existing_loggers': False,
                'formatters': {
                    'verbose': {
                        'format': '{levelname} {asctime} {module} {message}',
                        'style': '{',
                    },
                },
                'handlers': {
                    'console': {
                        'level': 'DEBUG',
                        'class': 'logging.StreamHandler',
                        'formatter': 'verbose',
                    },
                },
                'root': {
                    'handlers': ['console'],
                    'level': 'DEBUG',
                },
            }
        
        return {}
    
    @classmethod
    def _is_redis_available(cls) -> bool:
        """Check if Redis is available."""
        try:
            import redis
            r = redis.Redis(host='localhost', port=6379, db=0)
            r.ping()
            return True
        except:
            return False
    
    @classmethod
    def _is_smtp_configured(cls, email_config: EmailConfig) -> bool:
        """Check if SMTP is properly configured."""
        return bool(
            email_config.host and 
            email_config.port and 
            email_config.username
        )
```

## Version Management

### Python Version Checking

Beautiful Python version checking with helpful upgrade instructions:

```python
from django_cfg.utils.version_check import check_python_version

# Check Python version (raises SystemExit if incompatible)
check_python_version("django-cfg")

# Check compatibility without exiting
from django_cfg.utils.version_check import is_python_compatible

if not is_python_compatible():
    print("Python 3.12+ required")
```

### Version Check Implementation

```python
def check_python_version(context: str = "django-cfg") -> None:
    """
    Check if Python version meets requirements with beautiful output.
    
    Args:
        context: Context string for error messages
    
    Raises:
        SystemExit: If Python version is < 3.12
    """
    if sys.version_info >= (3, 12):
        return  # Version is OK
    
    # Show beautiful error message with Rich formatting
    _show_version_error(context)

def _show_version_error(context: str) -> NoReturn:
    """Show beautiful version error message and exit."""
    try:
        from rich.console import Console
        from rich.panel import Panel
        from rich.text import Text
        from rich.table import Table
        
        console = Console()
        
        # Create error message
        error_text = Text()
        error_text.append("🐍 Python Version Incompatible\n\n", style="bold red")
        error_text.append(f"{context} requires ", style="white")
        error_text.append("Python 3.12+", style="bold green")
        error_text.append(" but you're using ", style="white")
        error_text.append(f"Python {sys.version_info.major}.{sys.version_info.minor}", style="bold red")
        
        # Create upgrade instructions
        upgrade_table = Table(show_header=True, header_style="bold cyan")
        upgrade_table.add_column("Platform", style="bold blue")
        upgrade_table.add_column("Command", style="green")
        upgrade_table.add_column("Notes", style="dim")
        
        upgrade_table.add_row("macOS", "brew install python@3.12", "Homebrew")
        upgrade_table.add_row("Ubuntu", "sudo apt install python3.12", "22.04+")
        upgrade_table.add_row("Windows", "Download from python.org", "Official")
        upgrade_table.add_row("pyenv", "pyenv install 3.12.0", "Recommended")
        
        # Show benefits
        benefits_text = Text()
        benefits_text.append("✨ Python 3.12 Benefits:\n", style="bold yellow")
        benefits_text.append("• 40% faster performance\n", style="green")
        benefits_text.append("• Better error messages\n", style="green")
        benefits_text.append("• Modern syntax features\n", style="green")
        
        # Display panels
        console.print(Panel(error_text, title="🚫 Version Error", border_style="red"))
        console.print(Panel(upgrade_table, title="🔧 Upgrade Instructions", border_style="blue"))
        console.print(Panel(benefits_text, title="💡 Why Upgrade?", border_style="yellow"))
        
    except ImportError:
        # Fallback without Rich
        print(f"❌ Error: {context} requires Python 3.12+", file=sys.stderr)
        print(f"   Current: Python {sys.version_info.major}.{sys.version_info.minor}", file=sys.stderr)
    
    sys.exit(1)
```

### Version Utilities

Additional version management utilities:

```python
def get_python_version_string() -> str:
    """Get formatted Python version string."""
    return f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"

def is_python_compatible() -> bool:
    """Check if current Python version is compatible."""
    return sys.version_info >= (3, 12)

def get_version_info() -> Dict[str, Any]:
    """Get comprehensive version information."""
    return {
        'python_version': get_python_version_string(),
        'python_compatible': is_python_compatible(),
        'django_cfg_version': get_django_cfg_version(),
        'platform': sys.platform,
        'architecture': platform.architecture()[0],
    }
```

## Performance Utilities

### Configuration Caching

Efficient configuration caching:

```python
class ConfigCache:
    """Configuration caching for performance optimization."""
    
    def __init__(self):
        self._cache = {}
        self._cache_lock = Lock()
        self._cache_timeout = 300  # 5 minutes
    
    def get_cached_config(self, cache_key: str):
        """Get configuration from cache."""
        with self._cache_lock:
            if cache_key in self._cache:
                cached_data, timestamp = self._cache[cache_key]
                if time.time() - timestamp < self._cache_timeout:
                    return cached_data
                else:
                    # Cache expired
                    del self._cache[cache_key]
        
        return None
    
    def set_cached_config(self, cache_key: str, config_data):
        """Set configuration in cache."""
        with self._cache_lock:
            self._cache[cache_key] = (config_data, time.time())
    
    def invalidate_cache(self, cache_key: str = None):
        """Invalidate cache entries."""
        with self._cache_lock:
            if cache_key:
                self._cache.pop(cache_key, None)
            else:
                self._cache.clear()

# Global cache instance
config_cache = ConfigCache()
```

### Lazy Loading

Lazy loading for configuration components:

```python
class LazyConfigProperty:
    """Lazy loading property for configuration values."""
    
    def __init__(self, loader_func, cache_key=None):
        self.loader_func = loader_func
        self.cache_key = cache_key
        self._loaded_value = None
        self._is_loaded = False
    
    def __get__(self, instance, owner):
        if not self._is_loaded:
            if self.cache_key:
                cached_value = config_cache.get_cached_config(self.cache_key)
                if cached_value is not None:
                    self._loaded_value = cached_value
                    self._is_loaded = True
                    return self._loaded_value
            
            self._loaded_value = self.loader_func()
            self._is_loaded = True
            
            if self.cache_key:
                config_cache.set_cached_config(self.cache_key, self._loaded_value)
        
        return self._loaded_value

```

## Best Practices

### 1. Use Smart Defaults

Let Django-CFG configure services automatically:

```python
# Good: Use smart defaults
cache_config = CacheConfig(backend="auto")
email_config = EmailConfig(backend="auto")

# Bad: Manual configuration for every environment
if DEBUG:
    cache_config = CacheConfig(backend="locmem")
elif TESTING:
    cache_config = CacheConfig(backend="dummy")
else:
    cache_config = CacheConfig(backend="redis")
```

### 2. Validate Configuration

Always validate configuration using Pydantic:

```python
# Good: Validate configuration with Pydantic
from .config import config

try:
    # Pydantic automatically validates on creation
    config.model_validate(config.model_dump())
    logger.info("Configuration is valid")
except ValidationError as e:
    for error in e.errors():
        logger.error(f"Configuration error: {error}")

# Bad: No validation
# Configuration errors discovered at runtime
```

### 3. Use Version Checking

Check Python version early:

```python
# Good: Check version at startup
from django_cfg.utils.version_check import check_python_version
check_python_version("myapp")

# Bad: No version checking
# Runtime errors on incompatible Python versions
```

### 4. Cache Configuration

Cache expensive configuration operations:

```python
# Good: Use caching
@cached_property
def expensive_config(self):
    return self._calculate_expensive_config()

# Bad: Recalculate every time
def expensive_config(self):
    return self._calculate_expensive_config()  # Expensive!
```

## Integration Examples

### Django Settings Integration

Complete Django settings.py using utilities:

```python
# settings.py
from django_cfg.utils.version_check import check_python_version
from .config import config

# Check Python version first
check_python_version("MyProject")

# Get all Django settings from Django-CFG
globals().update(config.get_all_settings())

# Additional custom settings
CUSTOM_SETTING = "custom_value"
```

### Environment Detection

Automatic environment detection:

```python
from django_cfg.utils.smart_defaults import SmartDefaults

class EnvironmentDetector:
    @staticmethod
    def detect_environment() -> str:
        """Detect current environment."""
        import os
        
        # Check environment variables
        if os.getenv('IS_PROD', '').lower() == 'true':
            return 'production'
        elif os.getenv('IS_STAGING', '').lower() == 'true':
            return 'staging'
        elif os.getenv('TESTING', '').lower() == 'true':
            return 'testing'
        else:
            return 'development'
    
    @staticmethod
    def configure_for_environment(config):
        """Configure services for detected environment."""
        environment = EnvironmentDetector.detect_environment()
        
        # Apply smart defaults
        if hasattr(config, 'cache'):
            config.cache = SmartDefaults.configure_cache_backend(
                config.cache, environment, config.debug
            )
        
        if hasattr(config, 'email'):
            config.email = SmartDefaults.configure_email_backend(
                config.email, environment, config.debug
            )
        
        return config
```

## Related Documentation

- [**Configuration Guide**](/fundamentals/configuration) - Core configuration
- [**Registry System**](/fundamentals/system/registry) - Component registry
- [**Modules System**](/features/modules/overview) - Available modules
- [**CLI Tools**](/cli/introduction) - Utility commands

The Utilities system provides the foundation for Django-CFG's intelligent, environment-aware configuration management.
