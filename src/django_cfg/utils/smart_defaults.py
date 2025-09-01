"""
Smart defaults system for django_cfg.

Following CRITICAL_REQUIREMENTS.md:
- No raw Dict/Any usage
- Proper type annotations
- Environment-aware configuration
- No mutable default arguments
"""

from typing import Dict, Any, Optional, List
from pathlib import Path

from django_cfg.models.cache import CacheBackend
from django_cfg.models.services import EmailConfig
from django_cfg.exceptions import ConfigurationError


class SmartDefaults:
    """
    Environment-aware smart defaults for Django configuration.
    
    Automatically selects appropriate defaults based on:
    - Environment (development, production, testing, staging)
    - DEBUG flag
    - Available services (Redis, SMTP, etc.)
    - Security requirements
    """
    
    @classmethod
    def configure_cache_backend(
        cls,
        cache_config: CacheBackend,
        environment: Optional[str] = None,
        debug: bool = False
    ) -> CacheBackend:
        """
        Configure cache backend with environment-aware defaults.
        
        Args:
            cache_config: Base cache configuration
            environment: Current environment
            debug: Django DEBUG setting
            
        Returns:
            Configured cache backend
            
        Raises:
            ConfigurationError: If configuration cannot be applied
        """
        try:
            # Create a copy to avoid modifying the original
            config = cache_config.model_copy()
            
            # Environment-specific adjustments
            if environment == "testing":
                # Testing: Use dummy cache with very short timeouts
                config.backend_override = "django.core.cache.backends.dummy.DummyCache"
                config.timeout = min(config.timeout, 1)  # Max 1 second for tests
                
            elif environment == "development" or debug:
                # Development: Prefer memory cache, shorter timeouts
                if not config.redis_url:
                    # No Redis configured - use memory cache
                    config.timeout = min(config.timeout, 300)  # Max 5 minutes
                else:
                    # Redis available - use it but with shorter timeouts
                    config.timeout = min(config.timeout, 600)  # Max 10 minutes
                    config.max_connections = min(config.max_connections, 20)  # Fewer connections
                    
            elif environment in ("production", "staging"):
                # Production: Use Redis if available, longer timeouts
                if config.redis_url:
                    config.timeout = max(config.timeout, 300)  # Min 5 minutes
                    config.max_connections = max(config.max_connections, 50)  # More connections
                else:
                    # Production without Redis - warn but use file cache
                    config.backend_override = "django.core.cache.backends.filebased.FileBasedCache"
            
            # Apply compression for production
            if environment == "production" and config.redis_url:
                config.compress = True
            
            return config
            
        except Exception as e:
            raise ConfigurationError(
                f"Failed to configure cache backend: {e}",
                context={
                    'environment': environment,
                    'debug': debug,
                    'cache_config': cache_config.model_dump()
                }
            ) from e
    
    @classmethod
    def configure_email_backend(
        cls,
        email_config: EmailConfig,
        environment: Optional[str] = None,
        debug: bool = False
    ) -> EmailConfig:
        """
        Configure email backend with environment-aware defaults.
        
        Args:
            email_config: Base email configuration
            environment: Current environment
            debug: Django DEBUG setting
            
        Returns:
            Configured email backend
            
        Raises:
            ConfigurationError: If configuration cannot be applied
        """
        try:
            # Create a copy to avoid modifying the original
            config = email_config.model_copy()
            
            # Environment-specific adjustments
            if environment == "testing":
                # Testing: Use in-memory backend
                config.backend_override = "django.core.mail.backends.locmem.EmailBackend"
                config.timeout = min(config.timeout, 5)  # Very short timeout
                
            elif environment == "development":
                # Development: Use SMTP if configured, otherwise console
                if not config.username or not config.password:
                    # No SMTP credentials - use console backend
                    config.backend_override = "django.core.mail.backends.console.EmailBackend"
                else:
                    # SMTP configured - use SMTP backend
                    config.backend_override = "django.core.mail.backends.smtp.EmailBackend"
                    
            elif environment in ("production", "staging"):
                # Production: Use SMTP if properly configured
                if config.username and config.password:
                    config.backend_override = "django.core.mail.backends.smtp.EmailBackend"
                    
                    # Production email security
                    if config.port == 587:
                        config.use_tls = True
                        config.use_ssl = False
                    elif config.port == 465:
                        config.use_tls = False
                        config.use_ssl = True
                    
                    # Longer timeout for production
                    config.timeout = max(config.timeout, 30)
                else:
                    # Production without SMTP - fallback to console with warning
                    config.backend_override = "django.core.mail.backends.console.EmailBackend"
            
            return config
            
        except Exception as e:
            raise ConfigurationError(
                f"Failed to configure email backend: {e}",
                context={
                    'environment': environment,
                    'debug': debug,
                    'email_config': email_config.model_dump(exclude={'password'})
                }
            ) from e
    
    @classmethod
    def get_security_defaults(
        cls,
        domains: List[str],
        environment: Optional[str] = None,
        debug: bool = False
    ) -> Dict[str, Any]:
        """
        Get security defaults based on environment and domains.
        
        Args:
            domains: List of domains for CORS/security configuration
            environment: Current environment
            debug: Django DEBUG setting
            
        Returns:
            Security settings dictionary
        """
        try:
            settings = {}
            
            # CORS settings
            if domains:
                if environment == "development" or debug:
                    # Development: Allow all origins for convenience
                    settings['CORS_ALLOW_ALL_ORIGINS'] = True
                    settings['CORS_ALLOW_CREDENTIALS'] = True
                else:
                    # Production: Restrict to specified domains
                    allowed_origins = []
                    for domain in domains:
                        allowed_origins.extend([
                            f"https://{domain}",
                            f"https://www.{domain}",
                        ])
                    
                    settings['CORS_ALLOWED_ORIGINS'] = allowed_origins
                    settings['CORS_ALLOW_CREDENTIALS'] = True
            
            # Security headers for production
            if environment == "production":
                settings.update({
                    'SECURE_BROWSER_XSS_FILTER': True,
                    'SECURE_CONTENT_TYPE_NOSNIFF': True,
                    'SECURE_HSTS_SECONDS': 31536000,  # 1 year
                    'SECURE_HSTS_INCLUDE_SUBDOMAINS': True,
                    'SECURE_HSTS_PRELOAD': True,
                    'X_FRAME_OPTIONS': 'DENY',
                })
                
                # SSL settings if domains are HTTPS
                if domains:
                    settings.update({
                        'SECURE_SSL_REDIRECT': True,
                        'SESSION_COOKIE_SECURE': True,
                        'CSRF_COOKIE_SECURE': True,
                    })
            
            return settings
            
        except Exception as e:
            raise ConfigurationError(
                f"Failed to generate security defaults: {e}",
                context={
                    'domains': domains,
                    'environment': environment,
                    'debug': debug
                }
            ) from e
    
    @classmethod
    def get_database_defaults(
        cls,
        environment: Optional[str] = None,
        debug: bool = False,
        engine: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get database defaults based on environment and engine.
        
        Args:
            environment: Current environment
            debug: Django DEBUG setting
            engine: Database engine (to determine which options to apply)
            
        Returns:
            Database settings dictionary
        """
        try:
            defaults = {}
            
            if environment == "testing":
                # Testing: Use in-memory SQLite
                defaults = {
                    'ENGINE': 'django.db.backends.sqlite3',
                    'NAME': ':memory:',
                    'OPTIONS': {
                        'timeout': 1,  # Very short timeout for tests
                    }
                }
                
            elif environment == "development" or debug:
                # Development: Only add PostgreSQL/MySQL specific options
                if engine and engine in ("django.db.backends.postgresql", "django.db.backends.mysql"):
                    defaults = {
                        'OPTIONS': {
                            'connect_timeout': 5,  # Short timeout for dev
                        }
                    }
                    # Add sslmode only for PostgreSQL
                    if engine == "django.db.backends.postgresql":
                        defaults['OPTIONS']['sslmode'] = 'prefer'
                else:
                    # For SQLite, no special options needed
                    defaults = {}
                
            elif environment in ("production", "staging"):
                # Production: Only add PostgreSQL/MySQL specific options
                if engine and engine in ("django.db.backends.postgresql", "django.db.backends.mysql"):
                    if engine == "django.db.backends.postgresql":
                        # psycopg3 supports connection pooling with proper parameters
                        defaults = {
                            'OPTIONS': {
                                'connect_timeout': 10,
                                # psycopg3 connection pool parameters
                                'pool': {
                                    'min_size': 1,
                                    'max_size': 20,
                                    'timeout': 30.0,
                                }
                            }
                        }
                    else:
                        # MySQL
                        defaults = {
                            'OPTIONS': {
                                'connect_timeout': 10,
                            }
                        }
                    # Add sslmode only for PostgreSQL
                    if engine == "django.db.backends.postgresql":
                        defaults['OPTIONS']['sslmode'] = 'require'  # Require SSL in production
                else:
                    # For SQLite, no special options needed
                    defaults = {}
            
            return defaults
            
        except Exception as e:
            raise ConfigurationError(
                f"Failed to generate database defaults: {e}",
                context={
                    'environment': environment,
                    'debug': debug
                }
            ) from e
    
    @classmethod
    def get_logging_defaults(
        cls,
        environment: Optional[str] = None,
        debug: bool = False
    ) -> Dict[str, Any]:
        """
        Get logging defaults based on environment.
        
        Args:
            environment: Current environment
            debug: Django DEBUG setting
            
        Returns:
            Logging configuration dictionary
        """
        try:
            if environment == "testing":
                # Testing: Minimal logging
                return {
                    'version': 1,
                    'disable_existing_loggers': False,
                    'handlers': {
                        'null': {
                            'class': 'logging.NullHandler',
                        },
                    },
                    'root': {
                        'handlers': ['null'],
                    },
                }
                
            elif environment == "development" or debug:
                # Development: Console logging with colors
                return {
                    'version': 1,
                    'disable_existing_loggers': False,
                    'formatters': {
                        'verbose': {
                            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
                            'style': '{',
                        },
                    },
                    'handlers': {
                        'console': {
                            'class': 'logging.StreamHandler',
                            'formatter': 'verbose',
                        },
                    },
                    'root': {
                        'handlers': ['console'],
                        'level': 'DEBUG',
                    },
                    'loggers': {
                        'django': {
                            'handlers': ['console'],
                            'level': 'INFO',
                            'propagate': False,
                        },
                    },
                }
                
            elif environment in ("production", "staging"):
                # Production: File and structured logging
                return {
                    'version': 1,
                    'disable_existing_loggers': False,
                    'formatters': {
                        'json': {
                            'class': 'pythonjsonlogger.jsonlogger.JsonFormatter',
                            'format': '%(asctime)s %(name)s %(levelname)s %(message)s'
                        },
                        'standard': {
                            'format': '{levelname} {asctime} {name} {message}',
                            'style': '{',
                        },
                    },
                    'handlers': {
                        'file': {
                            'class': 'logging.handlers.RotatingFileHandler',
                            'filename': 'logs/django.log',
                            'maxBytes': 1024*1024*10,  # 10MB
                            'backupCount': 5,
                            'formatter': 'json' if environment == "production" else 'standard',
                        },
                        'console': {
                            'class': 'logging.StreamHandler',
                            'formatter': 'standard',
                        },
                    },
                    'root': {
                        'handlers': ['file', 'console'],
                        'level': 'WARNING' if environment == "production" else 'INFO',
                    },
                    'loggers': {
                        'django': {
                            'handlers': ['file'],
                            'level': 'INFO',
                            'propagate': False,
                        },
                    },
                }
            
            # Fallback
            return {}
            
        except Exception as e:
            raise ConfigurationError(
                f"Failed to generate logging defaults: {e}",
                context={
                    'environment': environment,
                    'debug': debug
                }
            ) from e


# Export the main class
__all__ = [
    "SmartDefaults",
]
