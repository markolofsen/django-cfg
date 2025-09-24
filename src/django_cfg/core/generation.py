"""
Django settings generation for django_cfg.

Following CRITICAL_REQUIREMENTS.md:
- No raw Dict/Any usage
- Proper type annotations
- Comprehensive error handling
- Performance-aware generation
"""

from typing import Dict, List, Any, TYPE_CHECKING
from pathlib import Path
import logging

from django_cfg.core.exceptions import ConfigurationError
from django_cfg.utils.smart_defaults import SmartDefaults

if TYPE_CHECKING:
    from django_cfg.core.config import DjangoConfig

logger = logging.getLogger(__name__)


class SettingsGenerator:
    """
    Generates complete Django settings from DjangoConfig instances.

    Converts type-safe Pydantic configuration models into Django-compatible
    settings dictionaries with intelligent defaults and validation.
    """

    @classmethod
    def generate(cls, config: "DjangoConfig") -> Dict[str, Any]:
        """
        Generate complete Django settings dictionary.

        Args:
            config: DjangoConfig instance

        Returns:
            Complete Django settings dictionary

        Raises:
            ConfigurationError: If settings generation fails
        """
        try:
            settings = {}

            # Generate core Django settings
            settings.update(cls._generate_core_settings(config))

            # Generate database settings
            settings.update(cls._generate_database_settings(config))

            # Generate cache settings
            settings.update(cls._generate_cache_settings(config))

            # Generate security settings
            settings.update(cls._generate_security_settings(config))

            # Generate email settings
            settings.update(cls._generate_email_settings(config))

            # Generate logging settings
            settings.update(cls._generate_logging_settings(config))

            # Generate static files settings
            settings.update(cls._generate_static_settings(config))

            # Generate internationalization settings
            settings.update(cls._generate_i18n_settings(config))

            # Generate limits settings
            settings.update(cls._generate_limits_settings(config))

            # Generate third-party integration settings
            settings.update(cls._generate_integration_settings(config))

            return settings

        except Exception as e:
            raise ConfigurationError(f"Failed to generate Django settings: {e}", context={"config_type": type(config).__name__, "project_name": getattr(config, "project_name", "unknown")}) from e

    @classmethod
    def _generate_core_settings(cls, config: "DjangoConfig") -> Dict[str, Any]:
        """Generate core Django settings."""
        try:
            settings = {
                "SECRET_KEY": config.secret_key,
                "DEBUG": config.debug,
                "ALLOWED_HOSTS": config.get_allowed_hosts(),
                "INSTALLED_APPS": config.get_installed_apps(),
                "MIDDLEWARE": config.get_middleware(),
            }

            # Add URL configuration
            if config.root_urlconf:
                settings["ROOT_URLCONF"] = config.root_urlconf

            # Add WSGI application
            if config.wsgi_application:
                settings["WSGI_APPLICATION"] = config.wsgi_application

            # Add custom user model
            if config.auth_user_model:
                settings["AUTH_USER_MODEL"] = config.auth_user_model
            elif config.enable_accounts:
                # Auto-use django-cfg accounts CustomUser if accounts is enabled
                settings["AUTH_USER_MODEL"] = "django_cfg_accounts.CustomUser"

            # Add base directory
            if config._base_dir:
                settings["BASE_DIR"] = config._base_dir

            # Add templates configuration
            django_cfg_templates = Path(__file__).parent.parent / "templates"
            settings["TEMPLATES"] = [
                {
                    "BACKEND": "django.template.backends.django.DjangoTemplates",
                    "DIRS": [
                        config.base_dir / "templates",
                        django_cfg_templates,  # Add django_cfg templates
                    ],
                    "APP_DIRS": True,
                    "OPTIONS": {
                        "context_processors": [
                            "django.template.context_processors.debug",
                            "django.template.context_processors.request",
                            "django.contrib.auth.context_processors.auth",
                            "django.contrib.messages.context_processors.messages",
                        ],
                    },
                },
            ]

            # Add default auto field
            settings["DEFAULT_AUTO_FIELD"] = "django.db.models.BigAutoField"

            return settings

        except Exception as e:
            raise ConfigurationError(f"Failed to generate core settings: {e}") from e

    @classmethod
    def _generate_database_settings(cls, config: "DjangoConfig") -> Dict[str, Any]:
        """Generate database settings."""
        try:
            settings = {}

            if config.databases:
                # Convert database configurations
                django_databases = {}
                for alias, db_config in config.databases.items():
                    django_databases[alias] = db_config.to_django_config()

                settings["DATABASES"] = django_databases

                # Apply database defaults for each database based on its engine
                for alias, db_config in config.databases.items():
                    db_defaults = SmartDefaults.get_database_defaults(
                        config._environment, 
                        config.debug, 
                        db_config.engine
                    )
                    if db_defaults:
                        # Merge defaults with existing configuration
                        for key, value in db_defaults.items():
                            if key == "OPTIONS":
                                # Merge OPTIONS dictionaries
                                existing_options = django_databases[alias].get("OPTIONS", {})
                                merged_options = {**value, **existing_options}
                                django_databases[alias]["OPTIONS"] = merged_options
                            elif key not in django_databases[alias]:
                                django_databases[alias][key] = value

            # Database routing - check if any database has routing rules
            routing_rules = {}
            for alias, db_config in config.databases.items():
                if db_config.has_routing_rules():
                    for app in db_config.apps:
                        routing_rules[app] = alias
            
            if routing_rules:
                settings["DATABASE_ROUTERS"] = ["django_cfg.routing.routers.DatabaseRouter"]
                settings["DATABASE_ROUTING_RULES"] = routing_rules

            return settings

        except Exception as e:
            raise ConfigurationError(f"Failed to generate database settings: {e}") from e

    @classmethod
    def _generate_cache_settings(cls, config: "DjangoConfig") -> Dict[str, Any]:
        """Generate cache settings."""
        try:
            settings = {}
            caches = {}

            # Default cache - always provide one
            if config.cache_default:
                caches["default"] = config.cache_default.to_django_config(config._environment, config.debug, "default")
            else:
                # Create default cache backend
                from django_cfg.models.cache import CacheConfig

                default_cache = CacheConfig()
                caches["default"] = default_cache.to_django_config(config._environment, config.debug, "default")

            # Sessions cache
            if config.cache_sessions:
                caches["sessions"] = config.cache_sessions.to_django_config(config._environment, config.debug, "sessions")

                # Configure Django to use cache for sessions (can be overridden)
                settings["SESSION_ENGINE"] = "django.contrib.sessions.backends.cache"
                settings["SESSION_CACHE_ALIAS"] = "sessions"

            # Add any additional cache backends found as attributes
            for attr_name in dir(config):
                if attr_name.startswith("cache_") and attr_name not in ["cache_default", "cache_sessions"]:
                    cache_obj = getattr(config, attr_name)
                    if hasattr(cache_obj, "to_django_config"):
                        cache_alias = attr_name.replace("cache_", "")
                        caches[cache_alias] = cache_obj.to_django_config(config._environment, config.debug, cache_alias)

            if caches:
                settings["CACHES"] = caches

            return settings

        except Exception as e:
            raise ConfigurationError(f"Failed to generate cache settings: {e}") from e

    @classmethod
    def _generate_security_settings(cls, config: "DjangoConfig") -> Dict[str, Any]:
        """Generate security settings."""
        try:
            settings = {}

            # Generate security defaults based on domains and ssl_redirect
            if config.security_domains or config.ssl_redirect is not None:
                security_defaults = SmartDefaults.get_security_defaults(
                    config.security_domains, 
                    config._environment, 
                    config.debug,
                    config.ssl_redirect,
                    config.cors_allow_headers
                )
                settings.update(security_defaults)

                # Add CORS to installed apps if domains are configured
                installed_apps = settings.get("INSTALLED_APPS", config.get_installed_apps())
                if "corsheaders" not in installed_apps:
                    # This will be handled by the core settings generation
                    pass

            # Additional security settings for production
            if config._environment == "production":
                settings.update(
                    {
                        "SESSION_COOKIE_AGE": 86400,  # 24 hours
                        "SESSION_SAVE_EVERY_REQUEST": True,
                        "SESSION_EXPIRE_AT_BROWSER_CLOSE": True,
                    }
                )

            return settings

        except Exception as e:
            raise ConfigurationError(f"Failed to generate security settings: {e}") from e

    @classmethod
    def _generate_email_settings(cls, config: "DjangoConfig") -> Dict[str, Any]:
        """Generate email settings."""
        try:
            settings = {}

            if config.email:
                email_settings = config.email.to_django_config(config._environment, config.debug)
                settings.update(email_settings)

            return settings

        except Exception as e:
            raise ConfigurationError(f"Failed to generate email settings: {e}") from e

    @classmethod
    def _generate_logging_settings(cls, config: "DjangoConfig") -> Dict[str, Any]:
        """Generate logging settings."""
        try:
            settings = {}

            # Generate logging defaults
            logging_defaults = SmartDefaults.get_logging_defaults(config._environment, config.debug)

            if logging_defaults:
                settings["LOGGING"] = logging_defaults

            return settings

        except Exception as e:
            raise ConfigurationError(f"Failed to generate logging settings: {e}") from e

    @classmethod
    def _generate_static_settings(cls, config: "DjangoConfig") -> Dict[str, Any]:
        """Generate static files settings."""
        try:
            settings = {
                "STATIC_URL": "/static/",
                "MEDIA_URL": "/media/",
                # WhiteNoise configuration
                "STATICFILES_STORAGE": "whitenoise.storage.CompressedManifestStaticFilesStorage",
                "WHITENOISE_USE_FINDERS": True,
                "WHITENOISE_AUTOREFRESH": config.debug,
                "WHITENOISE_MAX_AGE": 31536000,  # 1 year
            }

            # Set paths relative to base directory
            if config._base_dir:
                settings.update(
                    {
                        "STATIC_ROOT": config._base_dir / "staticfiles",
                        "MEDIA_ROOT": config._base_dir / "media",
                        "STATICFILES_DIRS": [
                            config._base_dir / "static",
                        ],
                    }
                )

            # Static files finders
            settings["STATICFILES_FINDERS"] = [
                "django.contrib.staticfiles.finders.FileSystemFinder",
                "django.contrib.staticfiles.finders.AppDirectoriesFinder",
            ]

            return settings

        except Exception as e:
            raise ConfigurationError(f"Failed to generate static settings: {e}") from e

    @classmethod
    def _generate_i18n_settings(cls, config: "DjangoConfig") -> Dict[str, Any]:
        """Generate internationalization settings."""
        try:
            settings = {
                "LANGUAGE_CODE": "en-us",
                "TIME_ZONE": "UTC",
                "USE_I18N": True,
                "USE_TZ": True,
            }

            # Adjust for different environments
            if config._environment == "development":
                settings["USE_L10N"] = True  # Deprecated but sometimes needed

            return settings

        except Exception as e:
            raise ConfigurationError(f"Failed to generate i18n settings: {e}") from e

    @classmethod
    def _generate_limits_settings(cls, config: "DjangoConfig") -> Dict[str, Any]:
        """Generate application limits settings."""
        try:
            settings = {}

            if config.limits:
                # Get Django settings from limits configuration
                limits_settings = config.limits.to_django_settings()
                settings.update(limits_settings)

            return settings

        except Exception as e:
            raise ConfigurationError(f"Failed to generate limits settings: {e}") from e

    @classmethod
    def _generate_integration_settings(cls, config: "DjangoConfig") -> Dict[str, Any]:
        """Generate third-party integration settings."""
        try:
            settings = {}

            # Session configuration - use database for persistence by default
            settings.update(
                {
                    "SESSION_ENGINE": "django.contrib.sessions.backends.db",
                    "SESSION_COOKIE_AGE": 86400 * 7,  # 7 days
                    "SESSION_SAVE_EVERY_REQUEST": True,
                }
            )

            # Placeholder for future integrations
            integrations = []

            # Check for telegram configuration
            if config.telegram:
                telegram_settings = config.telegram.to_config_dict()
                settings["TELEGRAM_CONFIG"] = telegram_settings
                integrations.append("telegram")

            # Check for unfold configuration
            if config.unfold:
                unfold_settings = config.unfold.to_django_settings()
                settings.update(unfold_settings)
                integrations.append("unfold")

            # Check for Constance configuration
            if hasattr(config, "constance") and config.constance:
                # Set config reference for app fields detection
                config.constance.set_config(config)
                constance_settings = config.constance.to_django_settings()
                settings.update(constance_settings)
                integrations.append("constance")

            # Check for JWT configuration
            if hasattr(config, "jwt") and config.jwt:
                jwt_settings = config.jwt.to_django_settings(config.secret_key)
                settings.update(jwt_settings)
                integrations.append("jwt")

            # Check for Tasks/Dramatiq configuration
            try:
                # Use the config's computed method to determine if tasks should be enabled
                if config.should_enable_tasks():
                    from django_cfg.models.tasks import TaskConfig
                    from django_cfg.modules.django_tasks import generate_dramatiq_settings_from_config

                    # Auto-initialize TaskConfig if needed and generate settings
                    task_config = TaskConfig.auto_initialize_if_needed()
                    if task_config is not None:
                        dramatiq_settings = generate_dramatiq_settings_from_config()
                        if dramatiq_settings:
                            settings.update(dramatiq_settings)
                            integrations.append("dramatiq")
                            logger.info("✅ Dramatiq enabled (tasks/knowbase/agents required)")
                else:
                    logger.debug("⏭️  Dramatiq disabled (no tasks/knowbase/agents)")
                        
            except ImportError as e:
                logger.warning(f"Failed to import django_tasks module: {e}")
            except Exception as e:
                logger.error(f"Failed to generate Dramatiq settings: {e}")

            # Check for Django Revolution configuration
            if hasattr(config, "revolution") and config.revolution:
                revolution_settings = {
                    "DJANGO_REVOLUTION": {
                        "api_prefix": config.revolution.api_prefix,
                        "debug": getattr(config.revolution, "debug", config.debug),
                        "auto_install_deps": getattr(config.revolution, "auto_install_deps", True),

                        "zones": {zone_name: zone_config.model_dump() for zone_name, zone_config in config.revolution.get_zones_with_defaults().items()},
                    }
                }
                settings.update(revolution_settings)
                integrations.append("django_revolution")

                # Automatically generate DRF configuration using Revolution's core_config
                try:
                    from django_revolution import create_drf_spectacular_config

                    # Extract DRF parameters from RevolutionConfig
                    drf_kwargs = {
                        "title": getattr(config.revolution, "drf_title", "API"),
                        "description": getattr(config.revolution, "drf_description", "RESTful API"),
                        "version": getattr(config.revolution, "drf_version", "1.0.0"),
                        "schema_path_prefix": f"/{config.revolution.api_prefix}/",
                        "enable_browsable_api": getattr(config.revolution, "drf_enable_browsable_api", False),
                        "enable_throttling": getattr(config.revolution, "drf_enable_throttling", False),
                    }

                    # Create DRF + Spectacular config with Revolution's comprehensive settings (includes proper enum config)
                    drf_settings = create_drf_spectacular_config(**drf_kwargs)
                    settings.update(drf_settings)
                    logger.info("🚀 Generated DRF + Spectacular settings using Revolution's create_drf_spectacular_config")
                    integrations.append("drf_spectacular")

                except ImportError as e:
                    logger.warning(f"Could not import django_revolution.create_drf_spectacular_config: {e}")
                except Exception as e:
                    logger.warning(f"Could not generate DRF config from Revolution: {e}")

            # Apply django-cfg DRF/Spectacular extensions
            try:
                # Always apply project name to Spectacular settings if they exist
                if "SPECTACULAR_SETTINGS" in settings:
                    if config.spectacular:
                        # User provided explicit spectacular config
                        spectacular_extensions = config.spectacular.get_spectacular_settings(project_name=config.project_name)
                        settings["SPECTACULAR_SETTINGS"].update(spectacular_extensions)
                        logger.info("🔧 Extended SPECTACULAR_SETTINGS with django-cfg Spectacular config")
                    else:
                        # Auto-create minimal spectacular config to set project name
                        from django_cfg.models.drf import SpectacularConfig
                        auto_spectacular = SpectacularConfig()
                        spectacular_extensions = auto_spectacular.get_spectacular_settings(project_name=config.project_name)
                        settings["SPECTACULAR_SETTINGS"].update(spectacular_extensions)
                        logger.info(f"🚀 Auto-configured API title as '{config.project_name} API'")
                    
                    integrations.append("drf_spectacular_extended")
                
                # Always apply django-cfg DRF settings (create REST_FRAMEWORK if needed)
                if config.drf:
                    # User provided explicit DRF config
                    drf_extensions = config.drf.get_rest_framework_settings()
                    if "REST_FRAMEWORK" in settings:
                        settings["REST_FRAMEWORK"].update(drf_extensions)
                    else:
                        settings["REST_FRAMEWORK"] = drf_extensions
                    logger.info("🔧 Extended REST_FRAMEWORK settings with django-cfg DRF config")
                else:
                    # Auto-create minimal DRF config to set default pagination
                    from django_cfg.models.drf import DRFConfig
                    auto_drf = DRFConfig()
                    drf_extensions = auto_drf.get_rest_framework_settings()
                    
                    if "REST_FRAMEWORK" in settings:
                        # Only apply pagination and page_size, don't override other settings
                        pagination_settings = {
                            'DEFAULT_PAGINATION_CLASS': drf_extensions['DEFAULT_PAGINATION_CLASS'],
                            'PAGE_SIZE': drf_extensions['PAGE_SIZE'],
                        }
                        settings["REST_FRAMEWORK"].update(pagination_settings)
                    else:
                        # Create new REST_FRAMEWORK settings with our defaults
                        settings["REST_FRAMEWORK"] = drf_extensions
                    
                    logger.info(f"🚀 Auto-configured default pagination: {drf_extensions['DEFAULT_PAGINATION_CLASS']}")
                    
            except Exception as e:
                logger.warning(f"Could not apply DRF/Spectacular extensions from django-cfg: {e}")

            # Add integration info for debugging
            if integrations:
                settings["DJANGO_CFG_INTEGRATIONS"] = integrations

            # Apply additional settings from config if available (for overrides)
            if hasattr(config, "get_additional_settings"):
                additional_settings = config.get_additional_settings()
                settings.update(additional_settings)

            return settings

        except Exception as e:
            raise ConfigurationError(f"Failed to generate integration settings: {e}") from e

    @classmethod
    def validate_generated_settings(cls, settings: Dict[str, Any]) -> List[str]:
        """
        Validate generated Django settings.

        Args:
            settings: Generated Django settings

        Returns:
            List of validation errors (empty if valid)
        """
        errors = []

        # Required settings validation
        required_settings = ["SECRET_KEY", "DEBUG", "ALLOWED_HOSTS", "INSTALLED_APPS", "MIDDLEWARE", "DATABASES"]

        for setting in required_settings:
            if setting not in settings:
                errors.append(f"Missing required setting: {setting}")

        # SECRET_KEY validation
        if "SECRET_KEY" in settings:
            secret_key = settings["SECRET_KEY"]
            if not secret_key or len(secret_key) < 50:
                errors.append("SECRET_KEY must be at least 50 characters long")

        # DATABASES validation
        if "DATABASES" in settings:
            databases = settings["DATABASES"]
            if not isinstance(databases, dict) or not databases:
                errors.append("DATABASES must be a non-empty dictionary")
            elif "default" not in databases:
                errors.append("DATABASES must contain a 'default' database")

        # INSTALLED_APPS validation
        if "INSTALLED_APPS" in settings:
            installed_apps = settings["INSTALLED_APPS"]
            if not isinstance(installed_apps, list):
                errors.append("INSTALLED_APPS must be a list")
            else:
                required_apps = [
                    "django.contrib.contenttypes",
                    "django.contrib.auth",
                ]
                for app in required_apps:
                    if app not in installed_apps:
                        errors.append(f"Missing required app: {app}")

        return errors


# Export the main class
__all__ = [
    "SettingsGenerator",
]
