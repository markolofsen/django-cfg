"""
Smart defaults system for django_cfg.

Following KISS principle:
- Simple, clear configuration
- No complex environment logic
- Logging handled by django_logger module
"""

import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional


def get_log_filename() -> str:
    """
    Determine the correct log filename based on project type.

    Returns:
        - 'django-cfg.log' for django-cfg projects
        - 'django.log' for regular Django projects
    """
    try:
        # Check for django-cfg in installed apps
        from django.conf import settings
        if hasattr(settings, 'INSTALLED_APPS'):
            for app in settings.INSTALLED_APPS:
                if 'django_cfg' in app:
                    return 'django-cfg.log'

        # Default to regular Django log
        return 'django.log'

    except Exception:
        # Fallback to django-cfg filename (since we're in django-cfg module)
        return 'django-cfg.log'


def _detect_asgi_mode() -> bool:
    """
    Detect if Django is running in ASGI or WSGI mode.

    Detection priority:
    1. DJANGO_ASGI environment variable (explicit override)
    2. ASGI_APPLICATION setting (if Django is configured)
    3. Command-line arguments (uvicorn, daphne, hypercorn)
    4. Default: False (WSGI mode)

    Returns:
        True if ASGI mode, False if WSGI mode

    Examples:
        >>> os.environ['DJANGO_ASGI'] = 'true'
        >>> _detect_asgi_mode()
        True

        >>> 'uvicorn' in sys.argv[0]
        >>> _detect_asgi_mode()
        True
    """
    # 1. Check explicit env var override
    asgi_env = os.environ.get('DJANGO_ASGI', '').lower()
    if asgi_env in ('true', '1', 'yes'):
        return True
    elif asgi_env in ('false', '0', 'no'):
        return False

    # 2. Check Django settings for ASGI_APPLICATION
    try:
        from django.conf import settings
        if hasattr(settings, 'ASGI_APPLICATION') and settings.ASGI_APPLICATION:
            return True
    except (ImportError, Exception):
        pass

    # 3. Check command-line arguments for ASGI servers
    command_line = ' '.join(sys.argv).lower()
    asgi_servers = ['uvicorn', 'daphne', 'hypercorn']
    for server in asgi_servers:
        if server in command_line:
            return True

    # Default: WSGI mode
    return False


def get_pool_config(environment: str = "development", is_asgi: Optional[bool] = None) -> Dict[str, Any]:
    """
    Get connection pool configuration.

    By default, uses simple environment-based configuration. Set AUTO_POOL_SIZE=true
    to enable automatic ASGI/WSGI detection and optimization.

    Args:
        environment: Environment name ('development', 'testing', 'staging', 'production')
        is_asgi: Deployment mode. If None and AUTO_POOL_SIZE=true, auto-detects mode

    Returns:
        Dict with pool configuration:
        {
            'min_size': int,      # Minimum pool size
            'max_size': int,      # Maximum pool size
            'timeout': int,       # Connection timeout (seconds)
            'max_lifetime': int,  # Max connection lifetime (seconds)
            'max_idle': int,      # Max idle time before closing (seconds)
        }

    Environment Variables:
        DB_POOL_MIN_SIZE: Minimum pool size (default: 10)
        DB_POOL_MAX_SIZE: Maximum pool size (default: 50)
        DB_POOL_TIMEOUT: Connection timeout in seconds (default: 30)
        AUTO_POOL_SIZE: Enable automatic ASGI/WSGI detection (default: false)

    Examples:
        # Simple static config (default):
        >>> get_pool_config('production')
        {'min_size': 10, 'max_size': 50, ...}

        # With auto-detection:
        >>> os.environ['AUTO_POOL_SIZE'] = 'true'
        >>> get_pool_config('production', is_asgi=True)
        {'min_size': 5, 'max_size': 20, ...}  # Optimized for ASGI
    """
    # Check if auto-detection is enabled
    auto_detect = os.environ.get('AUTO_POOL_SIZE', 'false').lower() in ('true', '1', 'yes')

    # Simple static configuration (default)
    if not auto_detect and is_asgi is None:
        # Use simple env var based config
        try:
            min_size = int(os.environ.get('DB_POOL_MIN_SIZE', 10))
        except ValueError:
            min_size = 10

        try:
            max_size = int(os.environ.get('DB_POOL_MAX_SIZE', 50))
        except ValueError:
            max_size = 50

        try:
            timeout = int(os.environ.get('DB_POOL_TIMEOUT', 30))
        except ValueError:
            timeout = 30

        # Validate
        if min_size >= max_size:
            min_size = max(1, max_size - 1)

        return {
            'min_size': min_size,
            'max_size': max_size,
            'timeout': timeout,
            'max_lifetime': 3600,  # 1 hour
            'max_idle': 600,       # 10 minutes
        }

    # Auto-detect ASGI mode if enabled and not specified
    if is_asgi is None:
        is_asgi = _detect_asgi_mode()

    # Pool configuration matrix
    # Format: (min_size, max_size, timeout)
    pool_configs = {
        'development': {
            'asgi': (2, 10, 10),
            'wsgi': (3, 15, 20),
        },
        'testing': {
            'asgi': (1, 5, 5),
            'wsgi': (2, 10, 10),
        },
        'staging': {
            'asgi': (3, 15, 10),
            'wsgi': (5, 30, 20),
        },
        'production': {
            'asgi': (5, 20, 10),
            'wsgi': (10, 50, 30),
        },
    }

    # Get base configuration
    env_key = environment.lower()
    if env_key not in pool_configs:
        # Fallback to development for unknown environments
        env_key = 'development'

    mode_key = 'asgi' if is_asgi else 'wsgi'
    min_size, max_size, timeout = pool_configs[env_key][mode_key]

    # Allow environment variable overrides
    try:
        min_size = int(os.environ.get('DB_POOL_MIN_SIZE', min_size))
    except ValueError:
        pass  # Keep default if invalid

    try:
        max_size = int(os.environ.get('DB_POOL_MAX_SIZE', max_size))
    except ValueError:
        pass

    try:
        timeout = int(os.environ.get('DB_POOL_TIMEOUT', timeout))
    except ValueError:
        pass

    # Validate: min_size must be < max_size
    if min_size >= max_size:
        min_size = max(1, max_size - 1)

    # Build and return pool configuration
    return {
        'min_size': min_size,
        'max_size': max_size,
        'timeout': timeout,
        'max_lifetime': 3600,  # 1 hour
        'max_idle': 600,       # 10 minutes
    }


class SmartDefaults:
    """
    Environment-aware smart defaults for Django configuration.
    
    Provides intelligent defaults based on environment detection
    with comprehensive type safety and validation.
    """

    @staticmethod
    def get_database_defaults(environment: str = "development", debug: bool = False, engine: str = "sqlite3") -> Dict[str, Any]:
        """
        Get database configuration defaults.

        For PostgreSQL with Django 5.1+:
        - Uses native connection pooling (recommended for ASGI/async apps)
        - CONN_MAX_AGE = 0 (required with native pooling)
        - ATOMIC_REQUESTS = True (default - safe and works with pooling)
        - Pool sizes: Auto-configured based on environment and ASGI/WSGI mode
        - Health checks: Handled automatically by psycopg3 pool

        Note on Transaction Safety:
        ATOMIC_REQUESTS=True is enabled by default, which wraps each request
        in a database transaction. This adds ~5-10ms overhead but ensures data
        integrity without manual transaction management.

        This works perfectly fine with connection pooling. If you need to optimize
        for read-heavy workloads, you can disable ATOMIC_REQUESTS and use selective
        transactions via Django's @transaction.atomic decorator on write views.

        References:
        - Django 5.1+ native pooling: https://docs.djangoproject.com/en/5.2/ref/databases/#connection-pooling
        - ASGI best practices: persistent connections should be disabled with ASGI
        """
        defaults = {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': Path('db') / 'db.sqlite3',
            'ATOMIC_REQUESTS': True,  # Safe default - ~5-10ms overhead acceptable for data integrity
            'CONN_MAX_AGE': 0,  # Set to 0 for native pooling (Django 5.1+)
            'CONN_HEALTH_CHECKS': True,  # Enable health checks to prevent stale connections
            'OPTIONS': {}
        }

        # Add engine-specific options
        if engine == "django.db.backends.postgresql":
            # Native connection pooling for Django 5.1+ with psycopg >= 3.1
            # See: https://docs.djangoproject.com/en/5.2/ref/databases/#postgresql-connection-pooling

            # Get dynamic pool configuration based on environment and deployment mode
            pool_config = get_pool_config(environment=environment, is_asgi=None)

            defaults['OPTIONS'] = {
                'connect_timeout': 20,
                'pool': pool_config,  # Dynamic pool config (ASGI/WSGI aware)
            }
        elif engine == "django.db.backends.sqlite3":
            defaults['OPTIONS']['timeout'] = 20  # SQLite uses 'timeout'

        return defaults

    @staticmethod
    def get_cache_defaults() -> Dict[str, Any]:
        """Get cache configuration defaults."""
        return {
            'default': {
                'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
                'LOCATION': 'default-cache',
                'TIMEOUT': 300,
                'OPTIONS': {
                    'MAX_ENTRIES': 1000,
                }
            }
        }

    @staticmethod
    def get_security_defaults(
        security_domains=None,
        environment: str = "development",
        debug: bool = False,
        ssl_redirect=None,
        cors_allow_headers=None
    ) -> Dict[str, Any]:
        """
        Get security configuration defaults.

        DEPRECATED: This method is kept for backward compatibility.
        New code should use SecurityBuilder.build_security_settings() directly.

        Note: This method now returns minimal settings. Full security configuration
        is handled by SecurityBuilder which has Docker awareness and better logic.
        """
        # Base Django settings (non-security specific)
        base_settings = {
            'USE_TZ': True,
            'USE_I18N': True,
            'USE_L10N': True,
        }

        # Return minimal settings - SecurityBuilder handles the rest
        return base_settings

    @classmethod
    def get_logging_defaults(
        cls,
        environment: Optional[str] = None,
        debug: bool = False
    ) -> Dict[str, Any]:
        """
        Simple logging configuration.
        
        NOTE: Real logging setup is handled by django_cfg.modules.django_logger
        This provides minimal fallback configuration only.
        
        Args:
            environment: Environment name (ignored - for compatibility)
            debug: Debug mode (ignored - for compatibility)
            
        Returns:
            Minimal Django logging configuration
        """
        # Minimal fallback - actual logging is configured by django_logger module
        return {
            'version': 1,
            'disable_existing_loggers': False,
            'handlers': {
                'console': {
                    'class': 'logging.StreamHandler',
                },
            },
            'root': {
                    'handlers': ['console'],
                    'level': 'INFO',
            },
        }

    @staticmethod
    def get_middleware_defaults() -> List[str]:
        """
        Get middleware configuration defaults.

        Note:
            ConnectionPoolCleanupMiddleware is automatically added LAST if
            enable_pool_cleanup=True in DjangoConfig (default).

            This middleware prevents connection leaks when using native
            connection pooling with ATOMIC_REQUESTS=False.
        """
        return [
            'corsheaders.middleware.CorsMiddleware',
            'django.middleware.security.SecurityMiddleware',
            'django.contrib.sessions.middleware.SessionMiddleware',
            'django.middleware.common.CommonMiddleware',
            'django.middleware.csrf.CsrfViewMiddleware',
            'django.contrib.auth.middleware.AuthenticationMiddleware',
            'django.contrib.messages.middleware.MessageMiddleware',
            'django.middleware.clickjacking.XFrameOptionsMiddleware',
            # ConnectionPoolCleanupMiddleware added in DjangoConfig.get_middleware()
        ]

    @staticmethod
    def get_installed_apps_defaults() -> List[str]:
        """Get default installed apps."""
        return [
            # Unfold admin
            "unfold",
            "unfold.contrib.filters",
            "unfold.contrib.forms",
            "unfold.contrib.inlines",
            "import_export",
            "unfold.contrib.import_export",
            "unfold.contrib.guardian",
            "unfold.contrib.simple_history",
            "unfold.contrib.location_field",
            "unfold.contrib.constance",

            # Django core
            "django.contrib.admin",
            "django.contrib.auth",
            "django.contrib.contenttypes",
            "django.contrib.sessions",
            "django.contrib.messages",
            "django.contrib.staticfiles",
            "django.contrib.humanize",

            # Third-party
            "corsheaders",
            "rest_framework",
            "rest_framework.authtoken",
            "rest_framework_simplejwt",
            "rest_framework_simplejwt.token_blacklist",
            "rest_framework_nested",
            "rangefilter",
            "django_filters",
            "drf_spectacular",
            "drf_spectacular_sidecar",
            "django_json_widget",
            "django_extensions",
            "constance",
            "constance.backends.database",

            # Django CFG
            "django_cfg",
        ]

    @staticmethod
    def get_templates_defaults() -> List[Dict[str, Any]]:
        """Get templates configuration defaults."""
        return [
            {
                'BACKEND': 'django.template.backends.django.DjangoTemplates',
                'DIRS': ['templates'],
                'APP_DIRS': True,
                'OPTIONS': {
                    'context_processors': [
                        'django.template.context_processors.debug',
                        'django.template.context_processors.request',
                        'django.contrib.auth.context_processors.auth',
                        'django.contrib.messages.context_processors.messages',
                    ],
                },
            },
        ]

    @staticmethod
    def get_static_files_defaults() -> Dict[str, Any]:
        """Get static files configuration defaults."""
        return {
            'STATIC_URL': '/static/',
            'STATIC_ROOT': Path('staticfiles'),
            'STATICFILES_DIRS': [
                Path('static'),
            ],
            'MEDIA_URL': '/media/',
            'MEDIA_ROOT': Path('media'),
        }

    @staticmethod
    def get_rest_framework_defaults() -> Dict[str, Any]:
        """Get Django REST Framework defaults."""
        return {
            'DEFAULT_AUTHENTICATION_CLASSES': [
                'django_cfg.middleware.authentication.JWTAuthenticationWithLastLogin',
                # SessionAuthentication removed (requires CSRF)
            ],
            'DEFAULT_PERMISSION_CLASSES': [
                'rest_framework.permissions.IsAuthenticated',
            ],
            'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
            'PAGE_SIZE': 20,
            'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
        }

    @staticmethod
    def get_cors_defaults() -> Dict[str, Any]:
        """Get CORS configuration defaults."""
        return {
            'CORS_ALLOWED_ORIGINS': [
                "http://localhost:3000",
                "http://127.0.0.1:3000",
            ],
            'CORS_ALLOW_CREDENTIALS': True,
            'CORS_ALLOW_ALL_ORIGINS': False,
        }

    @staticmethod
    def configure_cache_backend(cache_config, environment: str, debug: bool):
        """Configure cache backend - simplified."""
        if cache_config is None:
            from django_cfg.models.infrastructure.cache import CacheConfig
            return CacheConfig()
        return cache_config

    @staticmethod
    def configure_email_backend(email_config, environment: str, debug: bool):
        """Configure email backend - simplified."""
        if email_config is None:
            from django_cfg.models.services.email import EmailConfig
            return EmailConfig()
        return email_config


# Export the main class
__all__ = [
    "SmartDefaults",
    "get_log_filename",
]
