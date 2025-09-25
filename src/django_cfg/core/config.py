"""
Core DjangoConfig class for django_cfg.

Following CRITICAL_REQUIREMENTS.md:
- No raw Dict/Any usage - everything through Pydantic models
- Proper type annotations for all fields
- No mutable default arguments
- Comprehensive validation and error handling
"""

from typing import Dict, List, Optional, Any, Union
from pathlib import Path
from pydantic import BaseModel, Field, field_validator, model_validator, PrivateAttr
from enum import Enum
import os
from pathlib import Path
from urllib.parse import urlparse

from django_cfg import (
    ConfigurationError, ValidationError, EnvironmentError,
    DatabaseConfig, CacheConfig, EmailConfig, TelegramConfig,
    UnfoldConfig, DRFConfig, SpectacularConfig, LimitsConfig
)
from django_cfg.models.tasks import TaskConfig
from django_cfg.models.payments import PaymentsConfig

# Default apps
DEFAULT_APPS = [
    # Unfold
    "unfold",
    "unfold.contrib.filters",  # optional, if special filters are needed
    "unfold.contrib.forms",  # optional, if special form elements are needed
    "unfold.contrib.inlines",  # optional, if special inlines are needed
    "import_export",  # django-import-export package
    "unfold.contrib.import_export",  # optional, if django-import-export package is used
    "unfold.contrib.guardian",  # optional, if django-guardian package is used
    "unfold.contrib.simple_history",  # optional, if django-simple-history package is used
    "unfold.contrib.location_field",  # optional, if django-location-field package is used
    "unfold.contrib.constance",  # optional, if django-constance package is used
    # Django
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
    # Note: django_dramatiq is added conditionally when tasks are enabled
    # Django CFG
    "django_cfg",
    "django_revolution",
]


class EnvironmentMode(str, Enum):
    """Environment mode enumeration."""
    DEVELOPMENT = "development" 
    PRODUCTION = "production"
    TEST = "test"
    
    @classmethod
    def from_debug(cls, debug: bool) -> "EnvironmentMode":
        """Get environment mode from debug flag."""
        return cls.DEVELOPMENT if debug else cls.PRODUCTION


class DjangoConfig(BaseModel):
    """
    Base configuration class for Django projects.

    This is the core class that all Django project configurations inherit from.
    It provides type-safe configuration management with intelligent defaults
    and automatic Django settings generation.

    Key Features:
    - 100% type safety through Pydantic v2
    - Environment-aware smart defaults
    - Automatic Django settings generation
    - Zero raw dictionary usage
    - Comprehensive validation

    Example:
        ```python
        class MyProjectConfig(DjangoConfig):
            project_name: str = "My Project"
            databases: Dict[str, DatabaseConfig] = {
                "default": DatabaseConfig(
                    engine="django.db.backends.postgresql",
                    name="${DATABASE_URL:mydb}",
                )
            }

        config = MyProjectConfig()
        ```
    """

    model_config = {
        "validate_assignment": True,
        "extra": "forbid",  # Forbid arbitrary fields for type safety
        "env_prefix": "DJANGO_",
        "populate_by_name": True,
        "validate_default": True,
        "str_strip_whitespace": True,
    }

    # === Environment Configuration ===
    env_mode: EnvironmentMode = Field(
        default=EnvironmentMode.PRODUCTION,
        description="Environment mode: development, production, or test",
    )

    # === Project Information ===
    project_name: str = Field(
        ...,
        description="Human-readable project name",
        min_length=1,
        max_length=100,
    )

    project_logo: str = Field(
        default="",
        description="Project logo URL",
    )

    project_version: str = Field(
        default="1.0.0",
        description="Project version",
        pattern=r"^\d+\.\d+\.\d+.*$",
    )

    project_description: str = Field(
        default="",
        description="Project description",
        max_length=500,
    )

    # === Django CFG Features ===
    enable_support: bool = Field(
        default=True,
        description="Enable django-cfg Support application (tickets, messages, chat interface)",
    )
    enable_accounts: bool = Field(
        default=False,
        description="Enable django-cfg Accounts application (advanced user management, OTP, profiles, activity tracking)",
    )
    enable_newsletter: bool = Field(
        default=False,
        description="Enable django-cfg Newsletter application (email campaigns, subscriptions, bulk emails)",
    )
    enable_leads: bool = Field(
        default=False,
        description="Enable django-cfg Leads application (lead collection, contact forms, CRM integration)",
    )
    enable_knowbase: bool = Field(
        default=False,
        description="Enable django-cfg Knowledge Base application (documents, AI chat, embeddings, search)",
    )
    enable_agents: bool = Field(
        default=False,
        description="Enable django-cfg AI Agents application (agent definitions, executions, workflows, tools)",
    )
    enable_maintenance: bool = Field(
        default=False,
        description="Enable django-cfg Maintenance application (multi-site maintenance mode with Cloudflare)",
    )
    # === Payment System Configuration ===
    payments: Optional[PaymentsConfig] = Field(
        default=None,
        description="Universal payment system configuration (providers, subscriptions, API keys, billing)",
    )

    # === URLs ===
    site_url: str = Field(default="http://localhost:3000", description="Frontend site URL")
    api_url: str = Field(default="http://localhost:8000", description="Backend API URL")
    ticket_url: str = Field(default="{site_url}/support/ticket/{uuid}", description="Support ticket URL template. Use {site_url} and {uuid} placeholders")
    otp_url: str = Field(default="{site_url}/auth/otp/{code}", description="OTP verification URL template. Use {site_url} and {code} placeholders")

    # === Core Django Settings ===
    secret_key: str = Field(
        ...,
        description="Django SECRET_KEY",
        min_length=50,
        repr=False,  # Don't show in repr for security
    )

    debug: bool = Field(
        default=False,
        description="Django DEBUG setting",
    )

    # allowed_hosts removed - now auto-generated from security_domains

    # === URL Configuration ===
    root_urlconf: Optional[str] = Field(
        default=None,
        description="Django ROOT_URLCONF setting",
    )

    wsgi_application: Optional[str] = Field(
        default=None,
        description="Django WSGI_APPLICATION setting",
    )

    # === Custom User Model ===
    auth_user_model: Optional[str] = Field(
        default=None,
        description="Custom user model (AUTH_USER_MODEL). If None and enable_accounts=True, uses 'django_cfg.apps.accounts.CustomUser'",
        pattern=r"^[a-zA-Z_][a-zA-Z0-9_]*\.[a-zA-Z_][a-zA-Z0-9_]*$",
    )

    # === Project Applications ===
    project_apps: List[str] = Field(
        default_factory=list,
        description="List of project-specific Django apps",
    )

    # === Database Configuration ===
    databases: Dict[str, DatabaseConfig] = Field(
        default_factory=dict,
        description="Database connections",
    )

    # === Cache Configuration ===
    cache_default: Optional[CacheConfig] = Field(
        default=None,
        description="Default cache backend",
    )

    cache_sessions: Optional[CacheConfig] = Field(
        default=None,
        description="Sessions cache backend",
    )

    # === Security Configuration ===
    security_domains: List[str] = Field(
        default_factory=list,
        description="Domains for automatic security configuration (CORS, SSL, etc.)",
    )
    
    ssl_redirect: Optional[bool] = Field(
        default=None,
        description="Force SSL redirect on/off (None = auto based on domains and environment)",
    )

    # === CORS Configuration ===
    cors_allow_headers: List[str] = Field(
        default_factory=lambda: [
            "accept",
            "accept-encoding", 
            "authorization",
            "content-type",
            "dnt",
            "origin",
            "user-agent",
            "x-csrftoken",
            "x-requested-with",
            "x-api-key",
            "x-api-token",
        ],
        description="CORS allowed headers with common defaults for API usage",
    )

    # === Services Configuration ===
    email: Optional[EmailConfig] = Field(
        default=None,
        description="Email service configuration",
    )

    telegram: Optional[TelegramConfig] = Field(
        default=None,
        description="Telegram service configuration",
    )

    # === Admin Interface Configuration ===
    unfold: Optional[UnfoldConfig] = Field(
        default=None,
        description="Unfold admin interface configuration",
    )

    # === Background Task Processing ===
    tasks: Optional[TaskConfig] = Field(
        default=None,
        description="Background task processing configuration (Dramatiq)",
    )

    # === API Configuration ===
    # Note: DRF base configuration is handled by django-revolution
    # These fields provide additional/extended settings on top of Revolution
    drf: Optional[DRFConfig] = Field(
        default=None,
        description="Extended Django REST Framework configuration (supplements Revolution)",
    )

    spectacular: Optional[SpectacularConfig] = Field(
        default=None,
        description="Extended DRF Spectacular configuration (supplements Revolution)",
    )

    # === Limits Configuration ===
    limits: Optional[LimitsConfig] = Field(
        default=None,
        description="Application limits configuration (file uploads, requests, etc.)",
    )

    # === Middleware Configuration ===
    custom_middleware: List[str] = Field(
        default_factory=list,
        description="Custom middleware classes (standard middleware added automatically)",
    )

    # === Internal State ===
    _environment: Optional[str] = PrivateAttr(default=None)
    _base_dir: Optional[Path] = PrivateAttr(default=None)
    _django_settings: Optional[Dict[str, Any]] = PrivateAttr(default=None)

    def __init__(self, **data):
        """
        Initialize configuration with automatic setup.

        Performs the following setup steps:
        1. Environment detection
        2. Path resolution
        3. Smart defaults application
        4. Environment-specific configuration loading
        """
        super().__init__(**data)

        # Initialize internal state
        self._detect_environment()
        self._resolve_paths()
        self._apply_smart_defaults()
        self._load_environment_config()
        self._validate_configuration()

    @field_validator("project_name")
    @classmethod
    def validate_project_name(cls, v: str) -> str:
        """Validate project name format."""
        if not v.replace(" ", "").replace("-", "").replace("_", "").isalnum():
            raise ValueError("Project name must contain only alphanumeric characters, " "spaces, hyphens, and underscores")

        return v

    @field_validator("secret_key")
    @classmethod
    def validate_secret_key(cls, v: str) -> str:
        """Validate Django SECRET_KEY."""
        if len(v) < 50:
            raise ValueError("SECRET_KEY must be at least 50 characters long")

        # Check for common insecure patterns
        insecure_patterns = [
            "django-insecure",
            "change-me",
            "your-secret-key",
            "dev-key",
            "test-key",
        ]

        v_lower = v.lower()
        for pattern in insecure_patterns:
            if pattern in v_lower:
                # This is a warning, not an error - allow for development
                break

        return v

    # validate_allowed_hosts removed - allowed_hosts now auto-generated from security_domains

    @field_validator("project_apps")
    @classmethod
    def validate_project_apps(cls, v: List[str]) -> List[str]:
        """Validate project apps list."""
        for app in v:
            if not app:
                raise ValueError("Empty app name in project_apps")

            # Basic app name validation
            if not app.replace(".", "").replace("_", "").isalnum():
                raise ValueError(f"Invalid app name '{app}': must contain only letters, numbers, dots, and underscores")

        return v

    @model_validator(mode="after")
    def validate_configuration_consistency(self) -> "DjangoConfig":
        """Validate overall configuration consistency."""
        # Ensure at least one database is configured
        if not self.databases:
            raise ConfigurationError("At least one database must be configured", suggestions=["Add a 'default' database to the databases field"])

        # Ensure 'default' database exists
        if "default" not in self.databases:
            raise ConfigurationError("'default' database is required", context={"available_databases": list(self.databases.keys())}, suggestions=["Add a database with alias 'default'"])


        # Validate database routing consistency - check migrate_to references
        referenced_databases = set()
        for alias, db_config in self.databases.items():
            if db_config.migrate_to:
                referenced_databases.add(db_config.migrate_to)

        missing_databases = referenced_databases - set(self.databases.keys())
        if missing_databases:
            raise ConfigurationError(f"Database routing references non-existent databases: {missing_databases}", context={"available_databases": list(self.databases.keys())}, suggestions=[f"Add database configurations for: {', '.join(missing_databases)}"])

        return self

    # === Environment Mode Properties ===
    @property
    def is_development(self) -> bool:
        """Check if running in development mode."""
        return self.env_mode == EnvironmentMode.DEVELOPMENT

    @property  
    def is_production(self) -> bool:
        """Check if running in production mode."""
        return self.env_mode == EnvironmentMode.PRODUCTION

    @property
    def is_test(self) -> bool:
        """Check if running in test mode."""
        return self.env_mode == EnvironmentMode.TEST

    def _detect_environment(self) -> None:
        """Detect current environment from various sources."""
        from django_cfg.core.environment import EnvironmentDetector

        try:
            self._environment = EnvironmentDetector.detect_environment()
        except Exception as e:
            raise EnvironmentError(f"Failed to detect environment: {e}", suggestions=["Set DJANGO_ENV environment variable explicitly"]) from e

    @property
    def base_dir(self) -> Path:
        """Get the base directory of the project."""
        if self._base_dir is None:

            # Start from current working directory
            current_path = Path(os.path.dirname(os.path.abspath(__file__)))

            # Look for manage.py in current directory and parents
            for path in [current_path] + list(current_path.parents):
                manage_py = path / "manage.py"
                if manage_py.exists() and manage_py.is_file():
                    self._base_dir = path
                    break

            # If still not found, use current directory
            if self._base_dir is None:
                self._base_dir = Path.cwd()

        return self._base_dir

    def _resolve_paths(self) -> None:
        """Resolve project paths and auto-detect missing configuration."""
        from django_cfg.utils.path_resolution import PathResolver

        try:
            # Find project root if not already set
            if self._base_dir is None:
                self._base_dir = PathResolver.find_project_root()

            # Auto-detect URL configuration if not set
            if not self.root_urlconf:
                detected_urlconf = PathResolver.detect_root_urlconf(self._base_dir)
                if detected_urlconf:
                    self.root_urlconf = detected_urlconf

            # Auto-detect WSGI application if not set
            if not self.wsgi_application:
                detected_wsgi = PathResolver.detect_wsgi_application(self._base_dir)
                if detected_wsgi:
                    self.wsgi_application = detected_wsgi

        except Exception as e:
            raise ConfigurationError(f"Failed to resolve project paths: {e}", suggestions=["Ensure manage.py exists in your project root", "Set root_urlconf and wsgi_application explicitly"]) from e

    def _apply_smart_defaults(self) -> None:
        """Apply environment-aware smart defaults."""
        from django_cfg.utils.smart_defaults import SmartDefaults

        try:
            # Apply cache defaults
            if self.cache_default:
                self.cache_default = SmartDefaults.configure_cache_backend(self.cache_default, self._environment, self.debug)

            if self.cache_sessions:
                self.cache_sessions = SmartDefaults.configure_cache_backend(self.cache_sessions, self._environment, self.debug)

            # Apply email defaults
            if self.email:
                self.email = SmartDefaults.configure_email_backend(self.email, self._environment, self.debug)

        except Exception as e:
            raise ConfigurationError(f"Failed to apply smart defaults: {e}", context={"environment": self._environment, "debug": self.debug}) from e

    def _load_environment_config(self) -> None:
        """Load environment-specific configuration from YAML files."""
        # TODO: Implement environment-specific configuration loading
        # This will be implemented when EnvironmentConfig model is created
        pass

    def _validate_configuration(self) -> None:
        """Perform final configuration validation."""
        from django_cfg.core.validation import ConfigurationValidator

        try:
            errors = ConfigurationValidator.validate(self)
            if errors:
                raise ValidationError(f"Configuration validation failed: {len(errors)} errors found", context={"errors": errors}, suggestions=["Fix the validation errors listed in context"])
        except Exception as e:
            if isinstance(e, ValidationError):
                raise
            raise ConfigurationError(f"Configuration validation failed: {e}") from e

    def get_all_settings(self) -> Dict[str, Any]:
        """
        Generate complete Django settings dictionary.

        Returns:
            Complete Django settings ready for use

        Raises:
            ConfigurationError: If settings generation fails
        """
        # Automatically set this config as the current global config
        set_current_config(self)
        
        if self._django_settings is None:
            from django_cfg.core.generation import SettingsGenerator

            try:
                self._django_settings = SettingsGenerator.generate(self)
            except Exception as e:
                raise ConfigurationError(f"Failed to generate Django settings: {e}", context={"config": self.model_dump(exclude={"_django_settings"})}) from e

        return self._django_settings

    def get_ticket_url(self, ticket_uuid: str) -> str:
        """
        Generate ticket URL using the configured template.
        
        Args:
            ticket_uuid: UUID of the support ticket
            
        Returns:
            Complete URL to the ticket
        """
        return self.ticket_url.format(
            site_url=self.site_url,
            uuid=ticket_uuid
        )
    
    def get_otp_url(self, otp_code: str) -> str:
        """
        Generate OTP verification URL using the configured template.
        
        Args:
            otp_code: OTP verification code
            
        Returns:
            Complete URL to the OTP verification page
        """
        return self.otp_url.format(
            site_url=self.site_url,
            code=otp_code
        )

    def should_enable_tasks(self) -> bool:
        """
        Determine if background tasks should be enabled.
        
        Tasks are enabled if:
        1. Explicitly configured via tasks field
        2. Knowledge base is enabled (requires background processing)
        3. Agents are enabled (requires background processing)
        
        Returns:
            True if tasks should be enabled, False otherwise
        """
        # Check if explicitly configured
        if hasattr(self, 'tasks') and self.tasks and self.tasks.enabled:
            return True
        
        # Check if features that require tasks are enabled
        if self.enable_knowbase or self.enable_agents:
            return True
        
        # Check if payments module requires tasks
        if self.payments and self.payments.should_enable_tasks():
            return True

        # Check if agents module requires tasks
        if self.enable_agents:
            return True
        
        return False

    def get_installed_apps(self) -> List[str]:
        """
        Get complete list of installed Django apps.

        Returns:
            List of Django app names
        """
        # Start with DEFAULT_APPS but handle accounts specially
        apps = []
        
        # Add apps before admin
        for app in DEFAULT_APPS:
            if app == "django.contrib.admin":
                # Insert accounts before admin if enabled (for proper migration order)
                if self.enable_accounts:
                    apps.append("django_cfg.apps.accounts")
            apps.append(app)

        # Add other django-cfg built-in apps after standard apps
        if self.enable_support:
            apps.append("django_cfg.apps.support")
        if self.enable_newsletter:
            apps.append("django_cfg.apps.newsletter")
        if self.enable_leads:
            apps.append("django_cfg.apps.leads")
        if self.enable_knowbase:
            apps.append("django_cfg.apps.knowbase")
        if self.enable_agents:
            apps.append("django_cfg.apps.agents")
        if self.enable_maintenance:
            apps.append("django_cfg.apps.maintenance")
        if self.payments and self.payments.enabled:
            apps.append("django_cfg.apps.payments")
        
        # Auto-enable tasks if needed
        if self.should_enable_tasks():
            apps.append("django_dramatiq")  # Add django_dramatiq first
            apps.append("django_cfg.apps.tasks")

        # Auto-detect dashboard apps from Unfold callback
        dashboard_apps = self._get_dashboard_apps_from_callback()
        apps.extend(dashboard_apps)

        # Add project-specific apps
        apps.extend(self.project_apps)

        # Remove duplicates while preserving order
        seen = set()
        apps = [app for app in apps if not (app in seen or seen.add(app))]

        return apps

    def _get_dashboard_apps_from_callback(self) -> List[str]:
        """
        Auto-detect dashboard apps from Unfold dashboard_callback setting.

        Extracts app names from callback paths like:
        - "api.dashboard.callbacks.main_dashboard_callback" -> ["api.dashboard"]
        - "myproject.admin.callbacks.dashboard" -> ["myproject.admin"]

        Returns:
            List of dashboard app names to add to INSTALLED_APPS
        """
        dashboard_apps = []

        if not self.unfold or not self.unfold.theme:
            return dashboard_apps

        callback_path = getattr(self.unfold.theme, "dashboard_callback", None)
        if not callback_path:
            return dashboard_apps

        try:
            # Parse callback path: "api.dashboard.callbacks.main_dashboard_callback"
            # Extract app part: "api.dashboard"
            parts = callback_path.split(".")

            # Look for common callback patterns
            callback_indicators = ["callbacks", "views", "handlers"]

            # Find the callback indicator and extract app path before it
            app_parts = []
            for i, part in enumerate(parts):
                if part in callback_indicators:
                    app_parts = parts[:i]  # Everything before the callback indicator
                    break

            # If no callback indicator found, assume last part is function name
            if not app_parts and len(parts) > 1:
                app_parts = parts[:-1]  # Everything except the last part

            if app_parts:
                app_name = ".".join(app_parts)
                dashboard_apps.append(app_name)

        except Exception:
            # If parsing fails, silently continue - dashboard callback is optional
            pass

        return dashboard_apps

    def get_middleware(self) -> List[str]:
        """
        Get complete middleware stack.

        Returns:
            List of middleware class paths
        """
        # Standard Django middleware (always included)
        middleware = [
            "django.middleware.security.SecurityMiddleware",
            "whitenoise.middleware.WhiteNoiseMiddleware",  # Add WhiteNoise for static files
            "django.contrib.sessions.middleware.SessionMiddleware",
            "django.middleware.common.CommonMiddleware",
            "django.middleware.csrf.CsrfViewMiddleware",
            "django.contrib.auth.middleware.AuthenticationMiddleware",
            "django.contrib.messages.middleware.MessageMiddleware",
            "django.middleware.clickjacking.XFrameOptionsMiddleware",
        ]

        # Add CORS middleware if security domains are configured
        if self.security_domains:
            middleware.insert(1, "corsheaders.middleware.CorsMiddleware")

        # Add Django CFG middleware based on enabled features
        if self.enable_accounts:
            middleware.append("django_cfg.middleware.UserActivityMiddleware")

        # Add payments middleware if enabled
        if self.payments and self.payments.enabled:
            middleware.extend(self.payments.get_middleware_classes())

        # Add custom middleware
        middleware.extend(self.custom_middleware)

        return middleware

    def get_allowed_hosts(self) -> List[str]:
        """
        Generate ALLOWED_HOSTS from security_domains.

        Returns:
            List of allowed hosts including localhost for development
        """
        allowed_hosts = []

        # Add security domains if configured
        if self.security_domains:

            for domain in self.security_domains:
                # Parse URL properly
                if "://" in domain:
                    # Use urlparse to extract hostname correctly
                    parsed_url = urlparse(domain)
                    hostname = parsed_url.netloc.split(":")[0]  # Remove port if present
                else:
                    hostname = domain

                # Add hostname itself
                if hostname not in allowed_hosts:
                    allowed_hosts.append(hostname)

                # Add www subdomain if not already a subdomain and not localhost
                if not hostname.startswith("www.") and not hostname.startswith("*.") and not hostname.startswith("localhost") and not hostname.startswith("127.0.0.1"):
                    www_hostname = f"www.{hostname}"
                    if www_hostname not in allowed_hosts:
                        allowed_hosts.append(www_hostname)

        # Always allow localhost and 127.0.0.1 for development
        localhost_hosts = ["localhost", "127.0.0.1", "0.0.0.0"]
        for host in localhost_hosts:
            if host not in allowed_hosts:
                allowed_hosts.append(host)

        # If no domains configured, allow all (development mode)
        if not self.security_domains:
            allowed_hosts = ["*"]

        return allowed_hosts

    def get_site_url(self, path: str = "") -> str:
        """
        Get the site URL with optional path.

        Args:
            path: Optional path to append to site URL

        Returns:
            Complete URL with path
        """
        if path:
            path = path.lstrip("/")
            return f"{self.site_url.rstrip('/')}/{path}"
        return self.site_url


    def invalidate_cache(self) -> None:
        """Invalidate cached Django settings to force regeneration."""
        self._django_settings = None

    def model_dump_for_django(self) -> Dict[str, Any]:
        """
        Dump model data in format suitable for Django settings.

        Returns:
            Model data with internal fields excluded
        """
        return self.model_dump(exclude={"_environment", "_base_dir", "_django_settings"}, exclude_none=True)


# Global config instance for access from other modules
_current_config = None

def get_current_config():
    """
    Get the current DjangoConfig instance.
    
    Returns:
        The current DjangoConfig instance or None if not set
    """
    global _current_config
    return _current_config

def set_current_config(config: DjangoConfig):
    """
    Set the current DjangoConfig instance.
    
    Args:
        config: The DjangoConfig instance to set as current
    """
    global _current_config
    _current_config = config

# Export the main class
__all__ = [
    "DjangoConfig",
    "get_current_config",
    "set_current_config",
]
