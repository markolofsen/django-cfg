"""
Core DjangoConfig Pydantic model.

This module contains ONLY the data model definition:
- Field definitions with types and defaults
- Field validators
- Simple properties
- NO business logic (moved to builders and services)
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, List, Optional

from pydantic import BaseModel, Field, PrivateAttr, field_validator, model_validator

if TYPE_CHECKING:
    from django_cfg.modules.django_mcp.__cfg__ import DjangoMCPModuleConfig

# MCP module is always available within django_cfg
from django_cfg.modules.django_mcp.__cfg__ import DjangoMCPModuleConfig  # noqa: F401

from ...models import (
    ApiKeys,
    AxesConfig,
    CacheConfig,
    AnalyticsConfig,
    CurrencyConfig,
    DatabaseConfig,
    DjangoRQConfig,
    DRFConfig,
    EmailConfig,
    GeoConfig,
    IndexNowConfig,
    AccountEmailsConfig,
    AdminAccessConfig,
    PaymentsConfig,
    SimpleHistoryConfig,
    GitHubOAuthConfig,
    GoogleOAuthConfig,
    LimitsConfig,
    SpectacularConfig,
    StorageConfig,
    TelegramConfig,
    TwoFactorConfig,
    UnfoldConfig,
)
from ...modules.django_dashboard.models import DashboardConfig
from ..utils.display_name import normalize_display_name, slugify_name
from ..exceptions import ConfigurationError
from ..site import SiteConfig, _netloc, check_email, check_locale, check_logo_url, normalize_origin
from ..types.enums import EnvironmentMode, StartupInfoMode

# Brand fields a site owns once `sites` is declared: DjangoConfig field -> SiteConfig field.
_SITE_OWNED_FIELDS = {
    "site_url": "site_url",
    "support_email": "support_email",
    "logo_url": "logo_url",
    "default_locale": "locale",
}


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
        description=(
            "Extra hosts for ALLOWED_HOSTS, CORS, CSRF: mcp.*, internal names, wildcards. "
            "Single-site: the project's own hosts too. Declared sites add theirs automatically."
        ),
    )

    accept_subdomains: bool = Field(
        default=True,
        description=(
            "Accept every subdomain of each declared site/API domain in ALLOWED_HOSTS, CORS and CSRF "
            "(my.example.com, studio.example.com for example.com). Set False when a subdomain "
            "belongs to someone else."
        ),
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
            "x-auth-retry",  # generated TS SDK marks refresh-and-retry requests
            "x-mcp-access-key",  # MCP agent access key
            "dpop",  # RFC 9449 DPoP proof — sent per-request when dpop_enabled

            # Client locale/timezone headers
            # Sent by the generated TS SDK auth interceptor on every request so
            # Django can apply user-local timezone (via TimezoneMiddleware) and
            # format dates correctly server-side without any per-view changes.
            "x-timezone",    # IANA timezone string, e.g. "Europe/Moscow"
            "x-client-time", # ISO-8601 timestamp at request origin, e.g. "2026-05-05T12:00:00.000Z"

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

    # ╔══════════════════════════════════════════════════════════════════════════╗
    # ║                               URLS                                        ║
    # ╚══════════════════════════════════════════════════════════════════════════╝

    site_url: str = Field(
        default="http://localhost:3000",
        description="Frontend site URL (single-site; with `sites`, set it per SiteConfig).",
    )

    api_url: str = Field(
        default="http://localhost:8000",
        description="Backend API URL: where this Django answers. A site without its own api_url inherits it.",
    )

    sites: List[SiteConfig] = Field(
        default_factory=list,
        description=(
            "Sites this Django serves, first is the default. Empty = one site built from "
            "project_name, site_url and api_url. With sites, site_url, support_email, logo_url and "
            "default_locale must stay unset: each site owns them. See django_cfg.core.site."
        ),
    )

    support_email: Optional[str] = Field(
        default=None, description="Support address shown to users (single-site; per site: SiteConfig).",
    )

    logo_url: Optional[str] = Field(
        default=None, description="Absolute URL of the logo for mail (single-site; per site: SiteConfig).",
    )

    default_locale: Optional[str] = Field(
        default=None, description="Default locale for mail and copy, e.g. 'en'. Default 'en'.",
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

    search_indexing: bool = Field(
        default=False,
        description=(
            "Let search engines index this backend. Off by default: every "
            "response carries X-Robots-Tag noindex (NoIndexMiddleware)"
        ),
    )

    # An instance, not None: env (ADMIN_ACCESS__*) must work for a project that
    # never mentions it, so an operator can move or close the admin per deploy.
    admin_access: AdminAccessConfig = Field(
        default_factory=AdminAccessConfig,
        description="Django admin availability, URL prefix and optional CIDR allowlist",
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
        description=(
            "GitHub sign-in. None = built from GITHUB_OAUTH__CLIENT_ID / GITHUB_OAUTH__CLIENT_SECRET "
            "when both are set; otherwise off."
        ),
    )

    google_oauth: Optional[GoogleOAuthConfig] = Field(
        default=None,
        description=(
            "Google sign-in. None = built from GOOGLE_OAUTH__CLIENT_ID / GOOGLE_OAUTH__CLIENT_SECRET "
            "when both are set; otherwise off."
        ),
    )

    two_factor: Optional[TwoFactorConfig] = Field(
        default=None,
        description="Two-Factor Authentication (TOTP) configuration",
    )

    account_emails: AccountEmailsConfig = Field(
        default_factory=AccountEmailsConfig,
        description=(
            "Opt-in security emails: profile_change_email, new_sign_in_email. Both default to off; "
            "Telegram and admin notifications are not affected."
        ),
    )

    # ╔══════════════════════════════════════════════════════════════════════════╗
    # ║                          ADMIN INTERFACE                                  ║
    # ╚══════════════════════════════════════════════════════════════════════════╝

    unfold: Optional[UnfoldConfig] = Field(
        default=None,
        description="Unfold admin interface configuration",
    )

    dashboard: Optional[DashboardConfig] = Field(
        default=None,
        description="Custom admin dashboard tabs configuration",
    )

    admin_timezone: Optional[str] = Field(
        default=None,
        description="Admin timezone (e.g., 'Asia/Seoul'). None = auto-detect",
    )

    # ╔══════════════════════════════════════════════════════════════════════════╗
    # ║                               API                                         ║
    # ╚══════════════════════════════════════════════════════════════════════════╝

    extra_authentication_classes: List[str] = Field(
        default_factory=lambda: [
            "django_cfg.apps.system.accounts.authentication.APIKeyAuthentication",
        ],
        description="Extra DRF authentication classes prepended before defaults (e.g., custom API key auth)",
    )

    drf: Optional[DRFConfig] = Field(
        default=None,
        description="Django REST Framework configuration",
    )

    # Always materialize a SpectacularConfig so its default
    # ``enum_name_overrides`` (pinning django-cfg's own enums like
    # SystemHealthStatusEnum) reach SPECTACULAR_SETTINGS even when the
    # project never explicitly sets `spectacular=...`.
    spectacular: SpectacularConfig = Field(
        default_factory=SpectacularConfig,
        description="DRF Spectacular OpenAPI configuration",
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
    # ║                          CURRENCY & MONEY                                 ║
    # ╚══════════════════════════════════════════════════════════════════════════╝

    currency: Optional[CurrencyConfig] = Field(
        default=None,
        description="Currency conversion and exchange rates",
    )

    payments: Optional[PaymentsConfig] = Field(
        default=None,
        description="Payments engine: provider-agnostic checkout, webhooks, refunds (Stripe-first)",
    )

    # ╔══════════════════════════════════════════════════════════════════════════╗
    # ║                          GEOGRAPHIC DATA                                  ║
    # ╚══════════════════════════════════════════════════════════════════════════╝

    geo: Optional[GeoConfig] = Field(
        default=None,
        description="Geographic data (countries, states, cities)",
    )

    indexnow: Optional[IndexNowConfig] = Field(
        default=None,
        description="IndexNow: push changed sitemap URLs to Bing, Yandex and others",
    )

    # ALWAYS ON. Unlike every other app here, this defaults to an *instance*, not
    # None — analytics is a built-in capability, not an opt-in integration, and a
    # project that has to remember to switch it on will simply have no data for
    # the period before someone remembered. Ingest costs ~0.1ms and adds no
    # process, so there is nothing to protect the user from.
    # Opt out explicitly with `analytics = AnalyticsConfig(enabled=False)`.
    analytics: AnalyticsConfig = Field(
        default_factory=AnalyticsConfig,
        description="First-party analytics: pageviews, sessions, user attribution",
    )

    simple_history: Optional[SimpleHistoryConfig] = Field(
        default=None,
        description="django-simple-history audit log: field-level diff tracking with admin integration",
    )

    # ╔══════════════════════════════════════════════════════════════════════════╗
    # ║                          STORAGE & FILES                                  ║
    # ╚══════════════════════════════════════════════════════════════════════════╝

    storage: Optional[StorageConfig] = Field(
        default_factory=StorageConfig,
        description="Media storage backend and automatic file cleanup",
    )

    # ╔══════════════════════════════════════════════════════════════════════════╗
    # ║                           INTEGRATIONS                                    ║
    # ╚══════════════════════════════════════════════════════════════════════════╝

    # ╔══════════════════════════════════════════════════════════════════════════╗
    # ║                     AI AGENTS & MCP                                       ║
    # ╚══════════════════════════════════════════════════════════════════════════╝

    mcp: Optional["DjangoMCPModuleConfig"] = Field(
        default=None,
        description="Model Context Protocol (MCP) integration for AI agents",
    )

    # ╔══════════════════════════════════════════════════════════════════════════╗
    # ║                          FRONTEND / UI                                    ║
    # ╚══════════════════════════════════════════════════════════════════════════╝

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
    _sites: Optional[tuple] = PrivateAttr(default=None)

    # ╔══════════════════════════════════════════════════════════════════════════╗
    # ║                            VALIDATORS                                     ║
    # ╚══════════════════════════════════════════════════════════════════════════╝

    @field_validator("project_name")
    @classmethod
    def validate_project_name(cls, v: str) -> str:
        """Validate and normalise the project name.

        A display name, not an identifier: a domain (``gptkino.com``) or ``Acme, Inc.``
        is fine. Identifier use goes through ``project_slug()``, never the raw name.
        """
        return normalize_display_name(v)

    @field_validator("support_email")
    @classmethod
    def validate_support_email(cls, v: Optional[str]) -> Optional[str]:
        return check_email(v)

    @field_validator("logo_url")
    @classmethod
    def validate_logo_url(cls, v: Optional[str]) -> Optional[str]:
        return check_logo_url(v)

    @field_validator("default_locale")
    @classmethod
    def validate_default_locale(cls, v: Optional[str]) -> Optional[str]:
        return check_locale(v)

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
                import warnings
                warnings.warn(
                    f"SECRET_KEY contains an insecure pattern ('{pattern}'). "
                    "Generate a strong random key for production.",
                    UserWarning,
                    stacklevel=2,
                )
                break  # warn only — still allowed (e.g. development)

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

        # A sending backend with no sender would mail from Django's built-in
        # placeholder address.
        if (
            self.is_production
            and self.email
            and self.email.backend in ("smtp", "gateway")
            and not self.email.default_from
        ):
            raise ConfigurationError(
                f"EmailConfig(backend={self.email.backend!r}) needs default_from in production",
                suggestions=["Set EmailConfig(default_from='noreply@your-domain')"],
            )

        return self

    def _set_explicitly(self, name: str) -> bool:
        """True when the project gave ``name`` a value: an init argument, or a subclass that
        redefines the field (the way env-built consumers write ``site_url: str = env.app.site_url``).
        ``None`` on an optional field is no value."""
        redefined = type(self).model_fields[name].default != DjangoConfig.model_fields[name].default
        if getattr(self, name) is None:
            return False
        return name in self.model_fields_set or redefined

    @model_validator(mode="after")
    def validate_sites(self) -> "DjangoConfig":
        """Site keys and origins are unique; the brand fields live on the sites only.
        (The https rule runs in model_post_init, once the environment is known.)"""
        keys = [s.key for s in self.sites]
        dup_keys = sorted({k for k in keys if keys.count(k) > 1})
        if dup_keys:
            raise ConfigurationError(
                f"Duplicate site keys: {dup_keys}", suggestions=["Give each SiteConfig its own key"],
            )
        owner: Dict[str, str] = {}
        for site in self.sites:
            for origin in (site.site_url, *site.extra_origins):
                if owner.setdefault(origin, site.key) != site.key:
                    raise ConfigurationError(
                        f"Origin {origin} belongs to both sites {owner[origin]!r} and {site.key!r}",
                        suggestions=["An origin picks one site: remove it from one of them"],
                    )
        if self.sites:
            self._reject_deployment_brand_fields()
            for site in self.sites:
                if site.api_url is None and _netloc(site.site_url) == _netloc(self.api_url):
                    raise ConfigurationError(
                        f"site {site.key!r}: site_url and the deployment api_url share the host "
                        f"{_netloc(site.site_url)!r}",
                        suggestions=["Give the site its own api_url, or point DjangoConfig.api_url at the API host"],
                    )
        return self

    def _reject_deployment_brand_fields(self) -> None:
        """With `sites`, the sites own site_url, support_email, logo_url and the locale."""
        misplaced = [name for name in _SITE_OWNED_FIELDS if self._set_explicitly(name)]
        if not misplaced:
            return
        moves = [f"{name} -> SiteConfig({_SITE_OWNED_FIELDS[name]}=...)" for name in misplaced]
        raise ConfigurationError(
            f"DjangoConfig.{', DjangoConfig.'.join(misplaced)} set while `sites` is declared; "
            f"the sites own these fields. Move: {'; '.join(moves)}.",
            suggestions=[
                "Delete the field from DjangoConfig and set it on the SiteConfig that owns it, "
                f"for example sites=[SiteConfig(key={self.sites[0].key!r}, ...)]",
                "A value built from the environment (site_url=env.app.site_url) moves with it: "
                "give it to the SiteConfig instead",
                "project_name and api_url stay on DjangoConfig: they describe the deployment, not a site",
            ],
        )

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

        self._require_https_sites()

    def _require_https_sites(self) -> None:
        """Declared sites and the logo are https outside development and tests."""
        if self.is_development or self.is_test:
            return
        urls = [
            u for s in self.sites
            for u in (s.site_url, s.api_url or self.api_url, *s.extra_origins, s.logo_url) if u
        ]
        if self.logo_url:
            urls.append(self.logo_url)
        insecure = [u for u in urls if normalize_origin(u) and not u.lower().startswith("https://")]
        if insecure:
            raise ConfigurationError(
                f"Sites must use https outside development: {insecure}",
                suggestions=["Use https:// URLs, or set env_mode='development'"],
            )

    # ╔══════════════════════════════════════════════════════════════════════════╗
    # ║                            PROPERTIES                                     ║
    # ╚══════════════════════════════════════════════════════════════════════════╝

    @property
    def project_slug(self) -> str:
        """``project_name`` as an identifier: ``gptkino.com`` → ``gptkino_com``."""
        return slugify_name(self.project_name)

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

        # Reload DRF api_settings to pick up REST_FRAMEWORK
        # Must happen here before settings are applied to Django
        from ..integration.drf import reload_drf_api_settings
        reload_drf_api_settings(self._django_settings.get('REST_FRAMEWORK', {}))

        return self._django_settings

    def invalidate_cache(self) -> None:
        """Invalidate cached Django settings."""
        self._django_settings = None
        self._sites = None

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

    def build_media_url(
        self,
        path: Optional[str],
        fallback: Optional[str] = None,
    ) -> Optional[str]:
        """
        Build an absolute URL for a media file from its storage path.

        Combines ``api_url`` + ``media_url`` + *path*, handling both relative
        and absolute (CDN) ``media_url`` values automatically.

        Args:
            path: Relative path as stored in a model field, e.g.
                  ``"avatars/user_42.jpg"``.  Returns *fallback* if falsy.
            fallback: Value returned when *path* is empty/None (default ``None``).

        Returns:
            Absolute URL string, or *fallback*.

        Examples::

            config.build_media_url("avatars/user_42.jpg")
            # media_url="/media/"  → "https://api.example.com/media/avatars/user_42.jpg"
            # media_url="https://cdn.example.com/media/"
            #                      → "https://cdn.example.com/media/avatars/user_42.jpg"

            config.build_media_url(None, fallback="/static/no-avatar.png")
            # → "/static/no-avatar.png"
        """
        from ..utils.url_helpers import build_media_url as _build
        return _build(path, api_url=self.api_url, media_url=self.media_url, fallback=fallback)

    def build_api_url(self, path: str) -> str:
        """
        Build an absolute URL relative to *api_url*.

        Useful for constructing API proxy URLs (not media files).
        Strips leading/trailing slashes from *path* before joining so
        double-slashes are never produced.

        Args:
            path: URL path segment, e.g. ``"apix/catalog_photos/photo/abc.jpg"``.

        Returns:
            Absolute URL string.

        Examples::

            config.build_api_url("apix/catalog_photos/photo/abc.jpg")
            # → "https://api.example.com/apix/catalog_photos/photo/abc.jpg"

            config.build_api_url(f"{config.openapi_client.api_prefix}/catalog_photos/photo/{photo_id}.jpg")
            # → "https://api.example.com/apix/catalog_photos/photo/<uuid>.jpg"
        """
        return f"{self.api_url.rstrip('/')}/{path.lstrip('/')}"


__all__ = ["DjangoConfig"]

# Rebuild after optional imports are resolved
try:
    DjangoConfig.model_rebuild()
except Exception:
    pass
