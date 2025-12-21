"""
Core DjangoConfig Pydantic model.

This module contains ONLY the data model definition:
- Field definitions with types and defaults
- Field validators
- Simple properties
- NO business logic (moved to builders and services)
"""

from pathlib import Path
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, PrivateAttr, field_validator, model_validator

from django_cfg.apps.integrations.centrifugo.services.client.config import DjangoCfgCentrifugoConfig
from ...models import (
    ApiKeys,
    AxesConfig,
    CacheConfig,
    CryptoFieldsConfig,
    DatabaseConfig,
    DjangoRQConfig,
    DRFConfig,
    EmailConfig,
    GitHubOAuthConfig,
    LimitsConfig,
    SpectacularConfig,
    TelegramConfig,
    TwoFactorConfig,
    UnfoldConfig,
)
from ...models.api.grpc import GRPCConfig
from ...models.api.webpush import WebPushConfig
from ...models.ngrok import NgrokConfig
from ...modules.nextjs_admin import NextJsAdminConfig
from ..exceptions import ConfigurationError
from ..types.enums import EnvironmentMode, StartupInfoMode


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

    # ╔══════════════════════════════════════════════════════════════════════════╗
    # ║                         PROJECT INFORMATION                               ║
    # ╚══════════════════════════════════════════════════════════════════════════╝

    project_name: str = Field(
        ...,
        description="Human-readable project name",
        min_length=1,
        max_length=100,
    )

    project_version: str = Field(
        default="1.0.0",
        description="Project version (semver format)",
        pattern=r"^\d+\.\d+\.\d+.*$",
    )

    project_description: str = Field(
        default="",
        description="Project description",
        max_length=500,
    )

    project_logo: str = Field(
        default="",
        description="Project logo URL",
    )

    # ╔══════════════════════════════════════════════════════════════════════════╗
    # ║                         ENVIRONMENT & DEBUG                               ║
    # ╚══════════════════════════════════════════════════════════════════════════╝

    env_mode: EnvironmentMode = Field(
        default=EnvironmentMode.PRODUCTION,
        description="Environment mode: development, production, or test",
    )

    debug: bool = Field(
        default=False,
        description="Django DEBUG setting",
    )

    debug_warnings: bool = Field(
        default=False,
        description="Enable detailed warnings traceback for debugging",
    )

    # ╔══════════════════════════════════════════════════════════════════════════╗
    # ║                              SECURITY                                     ║
    # ╚══════════════════════════════════════════════════════════════════════════╝

    secret_key: str = Field(
        ...,
        description="Django SECRET_KEY (min 50 chars)",
        min_length=50,
        repr=False,  # Don't show in repr for security
    )

    security_domains: List[str] = Field(
        default_factory=lambda: ["localhost", "127.0.0.1"],
        description="Domains for ALLOWED_HOSTS, CORS, CSRF (auto-configured)",
    )

    ssl_redirect: Optional[bool] = Field(
        default=None,
        description="Force SSL redirect. None = disabled (proxy handles SSL)",
    )

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

            # File transfer / chunked upload headers
            # For the django_client module, the typescript generator will add the following headers to the request.
            # These headers are used to track the progress of the file upload.
            "x-chunk-index",
            "x-chunk-checksum",
            "x-is-last",
            "x-total-chunks",

        ],
        description="CORS allowed headers",
    )

    axes: Optional[AxesConfig] = Field(
        default=None,
        description="Django-Axes brute-force protection (None = smart defaults)",
    )

    crypto_fields: Optional[CryptoFieldsConfig] = Field(
        default=None,
        description="Django Crypto Fields encryption for sensitive data",
    )

    # ╔══════════════════════════════════════════════════════════════════════════╗
    # ║                               URLS                                        ║
    # ╚══════════════════════════════════════════════════════════════════════════╝

    site_url: str = Field(
        default="http://localhost:3000",
        description="Frontend site URL",
    )

    api_url: str = Field(
        default="http://localhost:8000",
        description="Backend API URL",
    )

    media_url: str = Field(
        default="/media/",
        description="Media URL. Use '__auto__' to derive from api_url",
    )

    root_urlconf: Optional[str] = Field(
        default=None,
        description="Django ROOT_URLCONF (e.g., 'api.urls')",
    )

    wsgi_application: Optional[str] = Field(
        default=None,
        description="Django WSGI_APPLICATION (e.g., 'api.wsgi.application')",
    )

    # ╔══════════════════════════════════════════════════════════════════════════╗
    # ║                             DATABASE                                      ║
    # ╚══════════════════════════════════════════════════════════════════════════╝

    databases: Dict[str, DatabaseConfig] = Field(
        default_factory=dict,
        description="Database connections. 'default' is required",
    )

    enable_pool_cleanup: bool = Field(
        default=False,
        description="Enable explicit connection pool cleanup middleware",
    )

    # ╔══════════════════════════════════════════════════════════════════════════╗
    # ║                               CACHE                                       ║
    # ╚══════════════════════════════════════════════════════════════════════════╝

    redis_url: Optional[str] = Field(
        default=None,
        description="Redis URL (redis://host:port/db). Auto-creates cache backend",
    )

    cache_default: Optional[CacheConfig] = Field(
        default=None,
        description="Default cache backend (auto-created from redis_url if not set)",
    )

    cache_sessions: Optional[CacheConfig] = Field(
        default=None,
        description="Sessions cache backend",
    )

    # ╔══════════════════════════════════════════════════════════════════════════╗
    # ║                            APPLICATIONS                                   ║
    # ╚══════════════════════════════════════════════════════════════════════════╝

    project_apps: List[str] = Field(
        default_factory=list,
        description="Project-specific Django apps",
    )

    custom_middleware: List[str] = Field(
        default_factory=list,
        description="Custom middleware classes",
    )

    # ╔══════════════════════════════════════════════════════════════════════════╗
    # ║                             SERVICES                                      ║
    # ╚══════════════════════════════════════════════════════════════════════════╝

    email: Optional[EmailConfig] = Field(
        default=None,
        description="Email service (SMTP/console backend)",
    )

    telegram: Optional[TelegramConfig] = Field(
        default=None,
        description="Telegram bot notifications",
    )

    admin_emails: List[str] = Field(
        default_factory=list,
        description="Admin email addresses for notifications (email + telegram)",
    )

    # ╔══════════════════════════════════════════════════════════════════════════╗
    # ║                        AUTHENTICATION & OAUTH                             ║
    # ╚══════════════════════════════════════════════════════════════════════════╝

    github_oauth: Optional[GitHubOAuthConfig] = Field(
        default=None,
        description="GitHub OAuth for social authentication",
    )

    two_factor: Optional[TwoFactorConfig] = Field(
        default=None,
        description="Two-Factor Authentication (TOTP) configuration",
    )

    # ╔══════════════════════════════════════════════════════════════════════════╗
    # ║                          ADMIN INTERFACE                                  ║
    # ╚══════════════════════════════════════════════════════════════════════════╝

    unfold: Optional[UnfoldConfig] = Field(
        default=None,
        description="Unfold admin interface configuration",
    )

    admin_timezone: Optional[str] = Field(
        default=None,
        description="Admin timezone (e.g., 'Asia/Seoul'). None = auto-detect",
    )

    # ╔══════════════════════════════════════════════════════════════════════════╗
    # ║                               API                                         ║
    # ╚══════════════════════════════════════════════════════════════════════════╝

    drf: Optional[DRFConfig] = Field(
        default=None,
        description="Django REST Framework configuration",
    )

    spectacular: Optional[SpectacularConfig] = Field(
        default=None,
        description="DRF Spectacular OpenAPI configuration",
    )

    grpc: Optional[GRPCConfig] = Field(
        default=None,
        description="gRPC server configuration",
    )

    webpush: Optional["WebPushConfig"] = Field(
        default=None,
        description="Web Push notifications (VAPID protocol)",
    )

    api_keys: Optional[ApiKeys] = Field(
        default=None,
        description="External API keys (OpenAI, OpenRouter, etc.)",
    )

    limits: Optional[LimitsConfig] = Field(
        default=None,
        description="Application limits (file uploads, requests, etc.)",
    )

    # ╔══════════════════════════════════════════════════════════════════════════╗
    # ║                          BACKGROUND TASKS                                 ║
    # ╚══════════════════════════════════════════════════════════════════════════╝

    django_rq: Optional[DjangoRQConfig] = Field(
        default=None,
        description="Django-RQ task queue and scheduler",
    )

    # ╔══════════════════════════════════════════════════════════════════════════╗
    # ║                           INTEGRATIONS                                    ║
    # ╚══════════════════════════════════════════════════════════════════════════╝

    centrifugo: Optional[DjangoCfgCentrifugoConfig] = Field(
        default=None,
        description="Centrifugo WebSocket pub/sub",
    )

    ngrok: Optional[NgrokConfig] = Field(
        default=None,
        description="Ngrok tunneling for development/webhooks",
    )

    nextjs_admin: Optional[NextJsAdminConfig] = Field(
        default=None,
        description="Next.js admin panel integration",
    )

    # ╔══════════════════════════════════════════════════════════════════════════╗
    # ║                          FRONTEND / UI                                    ║
    # ╚══════════════════════════════════════════════════════════════════════════╝

    enable_frontend: bool = Field(
        default=True,
        description="Enable Next.js admin panel static serving",
    )

    tailwind_app_name: str = Field(
        default="theme",
        description="Tailwind theme app name",
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
        description="Enable Tailwind CSS theme for DRF Browsable API",
    )

    # ╔══════════════════════════════════════════════════════════════════════════╗
    # ║                         DJANGO-CFG SETTINGS                               ║
    # ╚══════════════════════════════════════════════════════════════════════════╝

    startup_info_mode: StartupInfoMode = Field(
        default=StartupInfoMode.FULL,
        description="Startup info: NONE, SHORT, or FULL",
    )

    show_ai_hints: bool = Field(
        default=True,
        description="Show AI development hints in startup output",
    )

    # ╔══════════════════════════════════════════════════════════════════════════╗
    # ║                          INTERNAL STATE                                   ║
    # ╚══════════════════════════════════════════════════════════════════════════╝

    _base_dir: Optional[Path] = PrivateAttr(default=None)
    _django_settings: Optional[Dict[str, Any]] = PrivateAttr(default=None)
    _service: Optional[Any] = PrivateAttr(default=None)

    # ╔══════════════════════════════════════════════════════════════════════════╗
    # ║                            VALIDATORS                                     ║
    # ╚══════════════════════════════════════════════════════════════════════════╝

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

        # Check for common insecure patterns (warning only)
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
                break  # Warning only, allow for development

        return v

    @field_validator("project_apps")
    @classmethod
    def validate_project_apps(cls, v: List[str]) -> List[str]:
        """Validate project apps list."""
        for app in v:
            if not app:
                raise ValueError("Empty app name in project_apps")

            if not app.replace(".", "").replace("_", "").isalnum():
                raise ValueError(
                    f"Invalid app name '{app}': must contain only letters, "
                    f"numbers, dots, and underscores"
                )

        return v

    @field_validator("media_url", mode="before")
    @classmethod
    def validate_media_url(cls, v: str, info) -> str:
        """Validate and transform media_url."""
        if v == "__auto__":
            api_url = info.data.get("api_url", "http://localhost:8000")
            return f"{api_url.rstrip('/')}/media/"

        if v and not v.endswith("/"):
            return f"{v}/"

        return v

    @model_validator(mode="after")
    def validate_configuration_consistency(self) -> "DjangoConfig":
        """Validate overall configuration consistency."""
        # In development mode, force media_url to use api_url
        if self.is_development:
            dev_media_url = f"{self.api_url.rstrip('/')}/media/"
            if self.media_url != dev_media_url:
                object.__setattr__(self, 'media_url', dev_media_url)

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
        for _alias, db_config in self.databases.items():
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

    @model_validator(mode="after")
    def enforce_production_security(self) -> "DjangoConfig":
        """
        Enforce security best practices in production mode.

        SECURITY: Production mode ALWAYS disables debug, regardless of configuration.
        This prevents:
        - Sensitive data exposure in tracebacks (SECRET_KEY, credentials, paths)
        - Memory leaks from SQL query logging
        - Performance degradation
        - Accidental deployment with debug enabled

        If debug logging is needed in production, use proper logging configuration
        instead of DEBUG=True.
        """
        if self.is_production and self.debug:
            import warnings
            warnings.warn(
                "⚠️  SECURITY: DEBUG=True is not allowed in production!\n"
                f"   Environment: {self.env_mode}\n"
                "   Forcing DEBUG=False to prevent:\n"
                "   - Sensitive data exposure in error pages\n"
                "   - Memory leaks from query logging\n"
                "   - Performance issues\n"
                "\n"
                "   For production debugging, use:\n"
                "   - LOGGING config for detailed logs\n"
                "   - Sentry/error tracking services\n"
                "   - Django Debug Toolbar in staging (not production)",
                UserWarning,
                stacklevel=2
            )
            # Forcefully disable debug in production
            object.__setattr__(self, 'debug', False)

        return self

    def model_post_init(self, _context: Any) -> None:
        """Initialize configuration after Pydantic validation."""
        import os

        # Auto-detect environment from env variables
        if self.env_mode == EnvironmentMode.PRODUCTION:
            env_vars = ['DJANGO_ENV', 'ENVIRONMENT', 'ENV']
            for env_var in env_vars:
                env_value = os.environ.get(env_var)
                if env_value:
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

    # ╔══════════════════════════════════════════════════════════════════════════╗
    # ║                            PROPERTIES                                     ║
    # ╚══════════════════════════════════════════════════════════════════════════╝

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
        """Get the base directory of the project."""
        if self._base_dir is None:
            current_path = Path.cwd().resolve()

            for path in [current_path] + list(current_path.parents):
                manage_py = path / "manage.py"
                if manage_py.exists() and manage_py.is_file():
                    self._base_dir = path
                    break

            if self._base_dir is None:
                self._base_dir = current_path

        return self._base_dir

    # ╔══════════════════════════════════════════════════════════════════════════╗
    # ║                              METHODS                                      ║
    # ╚══════════════════════════════════════════════════════════════════════════╝

    @property
    def service(self) -> Any:
        """Lazy-load config service."""
        if self._service is None:
            from ..services.config_service import ConfigService
            self._service = ConfigService(self)
        return self._service

    def get_installed_apps(self) -> List[str]:
        """Get complete INSTALLED_APPS list."""
        return self.service.get_installed_apps()

    def get_middleware(self) -> List[str]:
        """Get complete MIDDLEWARE list."""
        return self.service.get_middleware()

    def get_allowed_hosts(self) -> List[str]:
        """Get ALLOWED_HOSTS."""
        return self.service.get_allowed_hosts()

    def get_all_settings(self) -> Dict[str, Any]:
        """Generate complete Django settings dictionary."""
        from ..state.registry import set_current_config
        set_current_config(self)

        from ..debug import setup_warnings_debug
        setup_warnings_debug()

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

    def invalidate_cache(self) -> None:
        """Invalidate cached Django settings."""
        self._django_settings = None

    def model_dump_for_django(self, **kwargs) -> Dict[str, Any]:
        """Serialize model data in Django-compatible format."""
        return self.model_dump(
            mode="python",
            exclude_none=False,
            by_alias=False,
            **kwargs
        )

    def should_enable_rq(self) -> bool:
        """Determine if Django-RQ should be enabled."""
        if hasattr(self, 'django_rq') and self.django_rq and self.django_rq.enabled:
            return True
        return False


__all__ = ["DjangoConfig"]
