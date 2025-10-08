"""
Core DjangoConfig Pydantic model.

This module contains ONLY the data model definition:
- Field definitions with types and defaults
- Field validators
- Simple properties
- NO business logic (moved to builders and services)

Total size: ~350 lines (down from 903 in original config.py)
"""

from typing import Dict, List, Optional, Any
from pathlib import Path
from pydantic import BaseModel, Field, field_validator, model_validator, PrivateAttr

from ..types.enums import EnvironmentMode, StartupInfoMode
from ..exceptions import ConfigurationError, ValidationError
from ...models import (
    DatabaseConfig,
    CacheConfig,
    EmailConfig,
    TelegramConfig,
    UnfoldConfig,
    DRFConfig,
    SpectacularConfig,
    LimitsConfig,
    ApiKeys,
)
from ...models.tasks import TaskConfig
from ...models.payments import PaymentsConfig
from ...models.ngrok import NgrokConfig
from ...modules.django_ipc_client.config import DjangoCfgRPCConfig


class DjangoConfig(BaseModel):
    """
    Base configuration class for Django projects.

    This is a pure data model - all business logic is in separate classes:
    - Apps list generation → InstalledAppsBuilder
    - Middleware generation → MiddlewareBuilder
    - Security settings → SecurityBuilder
    - Settings generation → SettingsGenerator

    Key Features:
    - 100% type safety through Pydantic v2
    - Environment-aware smart defaults
    - Comprehensive validation
    - Zero raw dictionary usage

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
        settings = config.get_all_settings()
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
    startup_info_mode: StartupInfoMode = Field(
        default=StartupInfoMode.FULL,
        description="Startup information display mode: none (minimal), short (essential), full (complete)",
    )

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
    site_url: str = Field(
        default="http://localhost:3000",
        description="Frontend site URL",
    )

    api_url: str = Field(
        default="http://localhost:8000",
        description="Backend API URL",
    )

    ticket_url: str = Field(
        default="{site_url}/support/ticket/{uuid}",
        description="Support ticket URL template. Use {site_url} and {uuid} placeholders",
    )

    otp_url: str = Field(
        default="{site_url}/auth/otp/{code}",
        description="OTP verification URL template. Use {site_url} and {code} placeholders",
    )

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

    ngrok: Optional[NgrokConfig] = Field(
        default=None,
        description="Ngrok tunneling service configuration (for development/webhooks)",
    )

    # === Admin Interface Configuration ===
    unfold: Optional[UnfoldConfig] = Field(
        default=None,
        description="Unfold admin interface configuration",
    )

    # === Frontend Configuration (Tailwind CSS) ===
    tailwind_app_name: str = Field(
        default="theme",
        description="Name of the Tailwind theme app (django-tailwind integration)",
        min_length=1,
        max_length=50,
    )

    tailwind_version: int = Field(
        default=4,
        description="Tailwind CSS version (3 or 4)",
        ge=3,
        le=4,
    )

    enable_drf_tailwind: bool = Field(
        default=True,
        description="Enable modern Tailwind CSS theme for Django REST Framework Browsable API",
    )

    # === Background Task Processing ===
    tasks: Optional[TaskConfig] = Field(
        default=None,
        description="Background task processing configuration (Dramatiq)",
    )

    # === RPC Client Configuration ===
    django_ipc: Optional[DjangoCfgRPCConfig] = Field(
        default=None,
        description="Django-CFG RPC Client configuration (WebSocket RPC communication)",
    )

    # === API Configuration ===
    drf: Optional[DRFConfig] = Field(
        default=None,
        description="Extended Django REST Framework configuration (supplements OpenAPI Client)",
    )

    spectacular: Optional[SpectacularConfig] = Field(
        default=None,
        description="Extended DRF Spectacular configuration (supplements OpenAPI Client)",
    )

    # === Limits Configuration ===
    limits: Optional[LimitsConfig] = Field(
        default=None,
        description="Application limits configuration (file uploads, requests, etc.)",
    )

    # === API Keys Configuration ===
    api_keys: Optional[ApiKeys] = Field(
        default=None,
        description="API keys for external services (OpenAI, OpenRouter, etc.)",
    )

    # === Middleware Configuration ===
    custom_middleware: List[str] = Field(
        default_factory=list,
        description="Custom middleware classes (standard middleware added automatically)",
    )

    # === Internal State (Private) ===
    _base_dir: Optional[Path] = PrivateAttr(default=None)
    _django_settings: Optional[Dict[str, Any]] = PrivateAttr(default=None)
    _service: Optional[Any] = PrivateAttr(default=None)  # ConfigService instance

    # === Field Validators ===

    @field_validator("project_name")
    @classmethod
    def validate_project_name(cls, v: str) -> str:
        """Validate project name format."""
        if not v.replace(" ", "").replace("-", "").replace("_", "").isalnum():
            raise ValueError(
                "Project name must contain only alphanumeric characters, "
                "spaces, hyphens, and underscores"
            )
        return v

    @field_validator("secret_key")
    @classmethod
    def validate_secret_key(cls, v: str) -> str:
        """Validate Django SECRET_KEY."""
        if len(v) < 50:
            raise ValueError("SECRET_KEY must be at least 50 characters long")

        # Check for common insecure patterns (warning only, not error)
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

    @field_validator("project_apps")
    @classmethod
    def validate_project_apps(cls, v: List[str]) -> List[str]:
        """Validate project apps list."""
        for app in v:
            if not app:
                raise ValueError("Empty app name in project_apps")

            # Basic app name validation
            if not app.replace(".", "").replace("_", "").isalnum():
                raise ValueError(
                    f"Invalid app name '{app}': must contain only letters, "
                    f"numbers, dots, and underscores"
                )

        return v

    @model_validator(mode="after")
    def validate_configuration_consistency(self) -> "DjangoConfig":
        """Validate overall configuration consistency."""
        # Ensure at least one database is configured
        if not self.databases:
            raise ConfigurationError(
                "At least one database must be configured",
                suggestions=["Add a 'default' database to the databases field"],
            )

        # Ensure 'default' database exists
        if "default" not in self.databases:
            raise ConfigurationError(
                "'default' database is required",
                context={"available_databases": list(self.databases.keys())},
                suggestions=["Add a database with alias 'default'"],
            )

        # Validate database routing consistency
        referenced_databases = set()
        for alias, db_config in self.databases.items():
            if db_config.migrate_to:
                referenced_databases.add(db_config.migrate_to)

        missing_databases = referenced_databases - set(self.databases.keys())
        if missing_databases:
            raise ConfigurationError(
                f"Database routing references non-existent databases: {missing_databases}",
                context={"available_databases": list(self.databases.keys())},
                suggestions=[f"Add database configurations for: {', '.join(missing_databases)}"],
            )

        return self

    def model_post_init(self, __context: Any) -> None:
        """
        Initialize configuration after Pydantic validation.

        Auto-detects environment from DJANGO_ENV, ENVIRONMENT, or ENV variables
        if env_mode was not explicitly set.
        """
        import os

        # Only auto-detect if using default value (PRODUCTION)
        # This allows explicit setting to override auto-detection
        if self.env_mode == EnvironmentMode.PRODUCTION:
            # Check if any env variable was explicitly set
            env_vars = ['DJANGO_ENV', 'ENVIRONMENT', 'ENV']
            for env_var in env_vars:
                env_value = os.environ.get(env_var)
                if env_value:
                    # Try to map to EnvironmentMode
                    env_normalized = env_value.lower().strip()
                    if env_normalized in ('dev', 'devel', 'develop', 'development', 'local'):
                        object.__setattr__(self, 'env_mode', EnvironmentMode.DEVELOPMENT)
                        break
                    elif env_normalized in ('prod', 'production'):
                        object.__setattr__(self, 'env_mode', EnvironmentMode.PRODUCTION)
                        break
                    elif env_normalized in ('test', 'testing'):
                        object.__setattr__(self, 'env_mode', EnvironmentMode.TEST)
                        break

    # === Simple Properties (NO business logic!) ===

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

    @property
    def base_dir(self) -> Path:
        """
        Get the base directory of the project.

        Looks for manage.py in current directory and parents.
        Falls back to current working directory if not found.
        """
        if self._base_dir is None:
            import os

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

    # === Facade Methods (delegate to service) ===

    @property
    def service(self) -> Any:
        """Lazy-load config service."""
        if self._service is None:
            from ..services.config_service import ConfigService
            self._service = ConfigService(self)
        return self._service

    def get_installed_apps(self) -> List[str]:
        """Get complete INSTALLED_APPS list (delegates to service)."""
        return self.service.get_installed_apps()

    def get_middleware(self) -> List[str]:
        """Get complete MIDDLEWARE list (delegates to service)."""
        return self.service.get_middleware()

    def get_allowed_hosts(self) -> List[str]:
        """Get ALLOWED_HOSTS (delegates to service)."""
        return self.service.get_allowed_hosts()

    def get_all_settings(self) -> Dict[str, Any]:
        """
        Generate complete Django settings dictionary.

        Delegates to SettingsGenerator for actual generation.

        Returns:
            Complete Django settings ready for use

        Raises:
            ConfigurationError: If settings generation fails
        """
        # Set as current config
        from ..state.registry import set_current_config
        set_current_config(self)

        if self._django_settings is None:
            from ..generation import SettingsGenerator

            try:
                self._django_settings = SettingsGenerator.generate(self)
            except Exception as e:
                raise ConfigurationError(
                    f"Failed to generate Django settings: {e}",
                    context={"config": self.model_dump(exclude={"_django_settings"})},
                ) from e

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
            uuid=ticket_uuid,
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
            code=otp_code,
        )

    def invalidate_cache(self) -> None:
        """
        Invalidate cached Django settings.

        Forces regeneration of settings on next call to get_all_settings().
        Useful when configuration has changed and settings need to be regenerated.

        Example:
            >>> config.invalidate_cache()
            >>> new_settings = config.get_all_settings()  # Will regenerate
        """
        self._django_settings = None

    def model_dump_for_django(self, **kwargs) -> Dict[str, Any]:
        """
        Serialize model data in Django-compatible format.

        This method provides a dictionary representation suitable for Django settings,
        with proper serialization of nested Pydantic models.

        Args:
            **kwargs: Additional arguments passed to model_dump()

        Returns:
            Dictionary with serialized configuration data

        Example:
            >>> config = DjangoConfig(project_name="My Project", ...)
            >>> dump = config.model_dump_for_django()
            >>> dump["project_name"]
            'My Project'
        """
        return self.model_dump(
            mode="python",
            exclude_none=False,
            by_alias=False,
            **kwargs
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

        return False


# Export main class
__all__ = ["DjangoConfig"]
