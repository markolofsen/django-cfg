"""
ConfigToolkit - Amazing Django Configuration Experience

The main interface for type-safe, environment-aware Django configuration.
"""

import os
import time
import logging
from pathlib import Path
from typing import Dict, Any, Optional, Type, TypeVar
from threading import Lock

from ..models.environment import EnvironmentConfig
from ..models.database import DatabaseConfig
from ..models.security import SecurityConfig
from ..models.api import APIConfig
from ..models.cache import CacheConfig
from ..models.email import EmailConfig
from ..modules.django_unfold.models.config import UnfoldConfig
from ..models.constance import ConstanceConfig
from ..models.logging import LoggingConfig

logger = logging.getLogger(__name__)

T = TypeVar('T')


class ConfigToolkit:
    """
    🚀 ConfigToolkit - Amazing Django Configuration Experience
    
    Features:
    - Type-safe configuration access with properties
    - Automatic environment detection
    - One-line Django settings integration  
    - Smart defaults and validation
    - Amazing developer experience
    
    Usage:
        # Django settings.py
        from django_cfg import ConfigToolkit
        globals().update(ConfigToolkit.get_django_settings())
        
        # Anywhere in your code
        if ConfigToolkit.debug:
            print("Debug mode active")
        
        db_url = ConfigToolkit.database_url
        page_size = ConfigToolkit.api_page_size
    """
    
    _instance: Optional['ConfigToolkit'] = None
    _lock = Lock()
    _initialized = False
    
    # Configuration instances
    _env_config: Optional[EnvironmentConfig] = None
    _db_config: Optional[DatabaseConfig] = None
    _security_config: Optional[SecurityConfig] = None
    _api_config: Optional[APIConfig] = None
    _cache_config: Optional[CacheConfig] = None
    _email_config: Optional[EmailConfig] = None
    _unfold_config: Optional[UnfoldConfig] = None
    # Revolution config removed - use django_revolution directly
    _constance_config: Optional[ConstanceConfig] = None
    _logging_config: Optional[LoggingConfig] = None
    
    # Performance tracking
    _init_time_ms = 0
    _config_cache = {}
    
    def __new__(cls, *args, **kwargs):
        """Singleton pattern for configuration."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self, 
                 database_config: Optional[DatabaseConfig] = None,
                 security_config: Optional[SecurityConfig] = None,
                 cache_config: Optional[CacheConfig] = None,
                 email_config: Optional[EmailConfig] = None,
                 unfold_config: Optional[UnfoldConfig] = None,
                 constance_config: Optional[ConstanceConfig] = None,
                 logging_config: Optional[LoggingConfig] = None):
        """
        Initialize ConfigToolkit with configuration models.
        
        Args:
            database_config: Custom database configuration
            security_config: Custom security configuration  
            cache_config: Custom cache configuration
            email_config: Custom email configuration
            unfold_config: Custom Unfold configuration
            constance_config: Custom Constance configuration
            logging_config: Custom logging configuration
        """
        if self._initialized:
            return
        
        start_time = time.perf_counter()
        
        try:
            # Load configurations (use provided configs or create defaults)
            self._load_configurations(
                database_config=database_config,
                security_config=security_config,
                cache_config=cache_config,
                email_config=email_config,
                unfold_config=unfold_config,
                constance_config=constance_config,
                logging_config=logging_config,
            )
            
            # Configure security based on environment
            self._configure_security()
            
            # Cache performance info
            self._init_time_ms = (time.perf_counter() - start_time) * 1000
            self._initialized = True
            
            # Show developer-friendly info
            if self.debug:
                print(f"🚀 ConfigToolkit initialized in {self._init_time_ms:.2f}ms")
                print(f"🌍 Environment: {self.environment}")
                
        except Exception as e:
            logger.error(f"❌ ConfigToolkit initialization failed: {e}")
            raise
    
    def _load_configurations(self,
                            database_config: Optional[DatabaseConfig] = None,
                            security_config: Optional[SecurityConfig] = None,
                            cache_config: Optional[CacheConfig] = None,
                            email_config: Optional[EmailConfig] = None,
                            unfold_config: Optional[UnfoldConfig] = None,
                            constance_config: Optional[ConstanceConfig] = None,
                            logging_config: Optional[LoggingConfig] = None):
        """Load all Pydantic configuration models."""
        # Core configurations (always loaded)
        self._env_config = EnvironmentConfig()
        self._db_config = database_config or DatabaseConfig()
        self._security_config = security_config or SecurityConfig()
        self._api_config = APIConfig()  # Keep default for now
        self._cache_config = cache_config or CacheConfig()
        self._email_config = email_config or EmailConfig()
        
        # Extended configurations (optional, loaded if dependencies available)
        self._load_extended_configurations(
            unfold_config=unfold_config,
            constance_config=constance_config,
            logging_config=logging_config,
        )
        
        logger.info("✅ All configuration models loaded")
    
    def _load_extended_configurations(self,
                                     unfold_config: Optional[UnfoldConfig] = None,
                                     constance_config: Optional[ConstanceConfig] = None,
                                     logging_config: Optional[LoggingConfig] = None):
        """Load extended configurations if dependencies are available."""
        config_count = 6  # Core configs
        
        # Unfold configuration
        if unfold_config:
            self._unfold_config = unfold_config
            config_count += 1
            logger.info("✅ Custom Unfold configuration loaded")
        else:
            self._unfold_config = UnfoldConfig()
            config_count += 1
            logger.info("✅ Default Unfold configuration loaded")
        
        # Revolution config removed - configure directly in Django settings
        
        # Constance configuration
        if constance_config:
            self._constance_config = constance_config
            config_count += 1
            logger.info("✅ Custom Constance configuration loaded")
        else:
            self._constance_config = ConstanceConfig()
            config_count += 1
            logger.info("✅ Default Constance configuration loaded")
        
        # Logging configuration (always available)
        self._logging_config = logging_config or LoggingConfig()
        config_count += 1
        
        self._config_count = config_count
    
    def _configure_security(self):
        """Configure security settings based on environment."""
        if self._env_config.is_production:
            self._security_config.configure_for_production()
        else:
            self._security_config.configure_for_development()
    
    # ===============================================
    # 🔥 CLASS METHODS - Main API
    # ===============================================
    
    @classmethod
    def get_django_settings(cls) -> Dict[str, Any]:
        """
        🔥 Get complete Django settings dictionary
        
        This is the main method for Django integration.
        Use in settings.py like this:
        
            from django_cfg import ConfigToolkit
            globals().update(ConfigToolkit.get_django_settings())
        """
        instance = cls()
        settings = {}
        
        # Merge all configuration settings
        settings.update(instance._env_config.to_django_settings())
        settings.update(instance._db_config.to_django_settings())
        settings.update(instance._security_config.to_django_settings())
        settings.update(instance._api_config.to_django_settings())
        settings.update(instance._cache_config.to_django_settings())
        settings.update(instance._email_config.to_django_settings())
        
        # Extended configurations
        if instance._unfold_config:
            settings.update(instance._unfold_config.to_django_settings())
        
        # Revolution settings applied directly in Django settings
        
        if instance._constance_config:
            settings.update(instance._constance_config.to_django_settings())
        
        if instance._logging_config:
            settings.update(instance._logging_config.to_django_settings())
        
        # Add third-party apps to INSTALLED_APPS if needed
        cls._extend_installed_apps(settings)
        cls._extend_middleware(settings)
        cls._extend_templates(settings)
        
        return settings
    
    @classmethod
    def _extend_installed_apps(cls, settings: Dict[str, Any]):
        """Extend INSTALLED_APPS with required third-party packages."""
        installed_apps = settings.get('INSTALLED_APPS', [])
        
        # Add common third-party apps
        third_party_apps = [
            'rest_framework',
            'rest_framework.authtoken',
            'rest_framework_simplejwt',
            'django_filters',
            'corsheaders',
        ]
        
        # Add API documentation if enabled
        instance = cls()
        if instance._api_config.docs_enabled:
            third_party_apps.extend([
                'drf_spectacular',
                'drf_spectacular_sidecar',
            ])
        
        # Handle special Unfold apps that need to be BEFORE django.contrib.admin
        unfold_apps = []
        if '_UNFOLD_APPS' in settings:
            unfold_apps = settings['_UNFOLD_APPS']
            del settings['_UNFOLD_APPS']
        
        # Add other extended apps
        for app_key in ['_REVOLUTION_APPS', '_CONSTANCE_APPS']:
            if app_key in settings:
                third_party_apps.extend(settings[app_key])
                del settings[app_key]  # Remove helper key
        
        # Insert Unfold apps BEFORE django.contrib.admin
        if unfold_apps:
            admin_index = None
            for i, app in enumerate(installed_apps):
                if app == 'django.contrib.admin':
                    admin_index = i
                    break
            
            if admin_index is not None:
                # Insert unfold apps before admin
                for app in reversed(unfold_apps):
                    if app not in installed_apps:
                        installed_apps.insert(admin_index, app)
            else:
                # If no admin app found, add at the beginning
                for app in unfold_apps:
                    if app not in installed_apps:
                        installed_apps.insert(0, app)
        
        # Add other apps that aren't already present
        for app in third_party_apps:
            if app not in installed_apps:
                installed_apps.append(app)
        
        settings['INSTALLED_APPS'] = installed_apps
    
    @classmethod
    def _extend_middleware(cls, settings: Dict[str, Any]):
        """Extend MIDDLEWARE with required middleware."""
        middleware = settings.get('MIDDLEWARE', [])
        
        # Add CORS middleware at the beginning if CORS is enabled
        instance = cls()
        if instance._security_config.cors_enabled:
            cors_middleware = 'corsheaders.middleware.CorsMiddleware'
            if cors_middleware not in middleware:
                middleware.insert(0, cors_middleware)
        
        settings['MIDDLEWARE'] = middleware
    
    @classmethod
    def _extend_templates(cls, settings: Dict[str, Any]):
        """Extend TEMPLATES with django-config-toolkit template directories."""
        import os
        from pathlib import Path
        
        # Get toolkit's template directory
        toolkit_dir = Path(__file__).parent
        template_dir = toolkit_dir / 'templates'
        
        if template_dir.exists():
            templates = settings.get('TEMPLATES', [])
            
            # Find the first Django template backend and add our template directory
            for template_config in templates:
                if template_config.get('BACKEND') == 'django.template.backends.django.DjangoTemplates':
                    dirs = template_config.get('DIRS', [])
                    
                    # Add toolkit template directory if not already present
                    if str(template_dir) not in [str(d) for d in dirs]:
                        dirs.append(str(template_dir))
                        template_config['DIRS'] = dirs
                    break
            
            settings['TEMPLATES'] = templates
    
    # ===============================================
    # 🌍 ENVIRONMENT PROPERTIES
    # ===============================================
    
    @classmethod
    @property
    def debug(cls) -> bool:
        """Django DEBUG setting."""
        return cls()._env_config.debug
    
    @classmethod
    @property
    def secret_key(cls) -> str:
        """Django SECRET_KEY."""
        return cls()._env_config.secret_key
    
    @classmethod
    @property
    def allowed_hosts(cls) -> list:
        """Django ALLOWED_HOSTS."""
        return cls()._env_config.allowed_hosts
    
    @classmethod
    @property
    def is_production(cls) -> bool:
        """True if running in production."""
        return cls()._env_config.is_production
    
    @classmethod
    @property
    def is_development(cls) -> bool:
        """True if running in development."""
        return cls()._env_config.is_development
    
    @classmethod
    @property
    def is_docker(cls) -> bool:
        """True if running in Docker."""
        return cls()._env_config.is_docker
    
    @classmethod
    @property
    def environment(cls) -> str:
        """Environment name."""
        return cls()._env_config.environment
    
    # ===============================================
    # 🗄️ DATABASE PROPERTIES
    # ===============================================
    
    @classmethod
    @property
    def database_url(cls) -> str:
        """Primary database URL."""
        return cls()._db_config.database_url
    
    @classmethod
    @property
    def database_max_connections(cls) -> int:
        """Database max connections."""
        return cls()._db_config.max_connections
    
    @classmethod
    @property
    def database_engine(cls) -> str:
        """Database engine type."""
        return cls()._db_config.database_engine
    
    @classmethod
    @property
    def is_sqlite(cls) -> bool:
        """True if using SQLite."""
        return cls()._db_config.is_sqlite
    
    @classmethod
    @property
    def is_postgresql(cls) -> bool:
        """True if using PostgreSQL."""
        return cls()._db_config.is_postgresql
    
    # ===============================================
    # 🔒 SECURITY PROPERTIES
    # ===============================================
    
    @classmethod
    @property
    def cors_enabled(cls) -> bool:
        """True if CORS is enabled."""
        return cls()._security_config.cors_enabled
    
    @classmethod
    @property
    def csrf_enabled(cls) -> bool:
        """True if CSRF is enabled."""
        return cls()._security_config.csrf_enabled
    
    @classmethod
    @property
    def ssl_enabled(cls) -> bool:
        """True if SSL redirect is enabled."""
        return cls()._security_config.ssl_redirect
    
    # ===============================================
    # 🌐 API PROPERTIES
    # ===============================================
    
    @classmethod
    @property
    def api_page_size(cls) -> int:
        """API pagination page size."""
        return cls()._api_config.page_size
    
    @classmethod
    @property
    def api_max_page_size(cls) -> int:
        """API max page size."""
        return cls()._api_config.max_page_size
    
    @classmethod
    @property
    def api_rate_limit_enabled(cls) -> bool:
        """True if API rate limiting is enabled."""
        return cls()._api_config.rate_limit_enabled
    
    @classmethod
    @property
    def api_docs_enabled(cls) -> bool:
        """True if API docs are enabled."""
        return cls()._api_config.docs_enabled
    
    # ===============================================
    # 💾 CACHE PROPERTIES
    # ===============================================
    
    @classmethod
    @property
    def cache_backend(cls) -> str:
        """Cache backend type."""
        return cls()._cache_config.backend
    
    @classmethod
    @property
    def cache_timeout(cls) -> int:
        """Default cache timeout."""
        return cls()._cache_config.default_timeout
    
    # ===============================================
    # 🎨 UNFOLD PROPERTIES  
    # ===============================================
    
    @classmethod
    @property
    def unfold_enabled(cls) -> bool:
        """True if Unfold admin is enabled."""
        return cls()._unfold_config is not None
    
    @classmethod
    @property
    def site_title(cls) -> str:
        """Site title from Unfold config."""
        instance = cls()
        return instance._unfold_config.site_title if instance._unfold_config else "Admin"
    
    # ===============================================
    # 🚀 REVOLUTION PROPERTIES
    # ===============================================
    
    @classmethod
    @property
    def revolution_enabled(cls) -> bool:
        """True if Django Revolution is enabled."""
        instance = cls()
        return False  # Revolution configured directly in Django settings
    
    @classmethod
    @property
    def api_prefix(cls) -> str:
        """API prefix from Revolution config."""
        instance = cls()
        return "api"  # Revolution configured directly in Django settings
    
    # ===============================================
    # ⚙️ CONSTANCE PROPERTIES
    # ===============================================
    
    @classmethod
    @property
    def constance_enabled(cls) -> bool:
        """True if Constance is enabled."""
        return cls()._constance_config is not None
    
    @classmethod
    @property
    def constance_backend(cls) -> str:
        """Constance backend."""
        instance = cls()
        return instance._constance_config.backend if instance._constance_config else "database"
    
    # ===============================================
    # 📝 LOGGING PROPERTIES
    # ===============================================
    
    @classmethod
    @property
    def logging_enabled(cls) -> bool:
        """True if logging is configured."""
        return cls()._logging_config is not None
    
    @classmethod
    @property
    def log_level(cls) -> str:
        """Root log level."""
        instance = cls()
        return instance._logging_config.root_level if instance._logging_config else "INFO"
    
    # ===============================================
    # 📧 EMAIL PROPERTIES
    # ===============================================
    
    @classmethod
    @property
    def email_backend(cls) -> str:
        """Email backend."""
        return cls()._email_config.backend
    
    @classmethod
    @property
    def email_host(cls) -> str:
        """Email host."""
        return cls()._email_config.host
    
    @classmethod
    @property
    def email_from(cls) -> str:
        """Default from email."""
        return cls()._email_config.default_from
    
    # ===============================================
    # 🛠️ DEVELOPER EXPERIENCE METHODS
    # ===============================================
    
    @classmethod
    def print_config_summary(cls):
        """Print helpful configuration summary for developers."""
        instance = cls()
        
        print("🚀 Django Config Toolkit - Configuration Summary")
        print("=" * 60)
        print(f"🌍 Environment: {cls.environment.upper()}")
        print(f"🔧 Debug: {cls.debug}")
        print(f"🗄️ Database: {cls.database_engine}")
        print(f"💾 Cache: {cls.cache_backend}")
        print(f"📧 Email: {cls.email_backend}")
        print(f"🔒 Security: CORS={cls.cors_enabled}, CSRF={cls.csrf_enabled}, SSL={cls.ssl_enabled}")
        print(f"🌐 API: Docs={cls.api_docs_enabled}, Rate Limit={cls.api_rate_limit_enabled}")
        print(f"⚡ Init Time: {instance._init_time_ms:.2f}ms")
        print("=" * 60)
        print("💡 Access anywhere: ConfigToolkit.debug, ConfigToolkit.database_url, etc.")
        print("📚 Docs: https://django-config-toolkit.readthedocs.io/")
        print("=" * 60)
    
    @classmethod
    def validate_configuration(cls) -> bool:
        """Validate all configurations for current environment."""
        try:
            instance = cls()
            
            # Validate each configuration
            env_valid = instance._env_config.validate_for_environment(cls.environment)
            db_valid = instance._db_config.validate_for_environment(cls.environment)
            
            return env_valid and db_valid
            
        except Exception as e:
            print(f"❌ Configuration validation failed: {e}")
            return False
    
    @classmethod
    def create_env_examples(cls):
        """Create .env.example files for all configurations."""
        configs = [
            ('environment', EnvironmentConfig),
            ('database', DatabaseConfig),
            ('security', SecurityConfig),
            ('api', APIConfig),
            ('cache', CacheConfig),
            ('email', EmailConfig),
        ]
        
        print("🚀 Creating environment configuration examples...")
        
        for name, config_class in configs:
            filename = f".env.{name}.example"
            config_class.create_env_example(filename)
        
        # Create combined example
        print("📋 Creating combined .env.example...")
        EnvironmentConfig.create_env_example(".env.example")
        
        print("✅ All environment examples created!")
        print("💡 Copy .env.example to .env and customize your settings")


# Convenience functions for developers
def show_config():
    """Show configuration summary - helpful for debugging."""
    ConfigToolkit.print_config_summary()


def validate_config() -> bool:
    """Validate current configuration."""
    return ConfigToolkit.validate_configuration()


def create_env_examples():
    """Create .env example files."""
    ConfigToolkit.create_env_examples()
