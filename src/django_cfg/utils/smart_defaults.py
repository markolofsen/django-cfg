"""
Smart defaults system for django_cfg.

Following KISS principle:
- Simple, clear configuration
- No complex environment logic
- Logging handled by django_logger module
"""

from typing import Dict, Any, Optional, List
from pathlib import Path

from django_cfg.models.cache import CacheConfig
from django_cfg.models.services import EmailConfig
from django_cfg.core.exceptions import ConfigurationError


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


class SmartDefaults:
    """
    Environment-aware smart defaults for Django configuration.
    
    Provides intelligent defaults based on environment detection
    with comprehensive type safety and validation.
    """
    
    @staticmethod
    def get_database_defaults(environment: str = "development", debug: bool = False, engine: str = "sqlite3") -> Dict[str, Any]:
        """Get database configuration defaults."""
        defaults = {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': Path('db') / 'db.sqlite3',
            'ATOMIC_REQUESTS': True,
            'CONN_MAX_AGE': 60,
            'OPTIONS': {}
        }
        
        # Add engine-specific options
        if engine == "django.db.backends.postgresql":
            defaults['OPTIONS']['connect_timeout'] = 20
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
        """Get security configuration defaults."""
        from ..models.security import SecurityConfig
        
        # Base security settings
        base_settings = {
            'USE_TZ': True,
            'USE_I18N': True,
            'USE_L10N': True,
            'SECURE_BROWSER_XSS_FILTER': not debug,
            'SECURE_CONTENT_TYPE_NOSNIFF': not debug,
            'X_FRAME_OPTIONS': 'DENY' if not debug else 'SAMEORIGIN',
            'SECURE_HSTS_SECONDS': 31536000 if not debug else 0,
            'SECURE_HSTS_INCLUDE_SUBDOMAINS': not debug,
            'SECURE_HSTS_PRELOAD': not debug,
        }
        
        # Add CORS settings if security domains are configured
        if security_domains:
            # Combine default CORS headers with custom ones
            default_headers = SecurityConfig().cors_allow_headers
            if cors_allow_headers:
                # Combine and deduplicate headers
                all_headers = default_headers + cors_allow_headers
                seen = set()
                unique_headers = []
                for header in all_headers:
                    if header.lower() not in seen:
                        seen.add(header.lower())
                        unique_headers.append(header)
                final_headers = unique_headers
            else:
                final_headers = default_headers
            
            # Create SecurityConfig with appropriate settings
            security_config = SecurityConfig(
                cors_enabled=True,
                cors_allow_all_origins=debug or environment == "development",
                cors_allowed_origins=security_domains if not (debug or environment == "development") else [],
                cors_allow_credentials=True,
                cors_allow_headers=final_headers,
                ssl_redirect=ssl_redirect or False,
            )
            
            # Configure for development if needed
            if debug or environment == "development":
                security_config.configure_for_development()
            
            # Get Django settings from SecurityConfig
            cors_settings = security_config.to_django_settings()
            base_settings.update(cors_settings)
        
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
        """Get middleware configuration defaults."""
        return [
            'corsheaders.middleware.CorsMiddleware',
            'django.middleware.security.SecurityMiddleware',
            'django.contrib.sessions.middleware.SessionMiddleware',
            'django.middleware.common.CommonMiddleware',
            'django.middleware.csrf.CsrfViewMiddleware',
            'django.contrib.auth.middleware.AuthenticationMiddleware',
            'django.contrib.messages.middleware.MessageMiddleware',
            'django.middleware.clickjacking.XFrameOptionsMiddleware',
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
                'rest_framework_simplejwt.authentication.JWTAuthentication',
                'rest_framework.authentication.SessionAuthentication',
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
            return CacheConfig()
        return cache_config
    
    @staticmethod
    def configure_email_backend(email_config, environment: str, debug: bool):
        """Configure email backend - simplified."""
        if email_config is None:
            return EmailConfig()
        return email_config


# Export the main class
__all__ = [
    "SmartDefaults",
    "get_log_filename",
]
