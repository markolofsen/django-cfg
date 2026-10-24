"""Sample project configuration: one typed ``DjangoConfig`` built from ``api.environment``; declarations live in ``builders/``."""

from typing import Dict, Optional

from django_cfg import (
    IndexNowConfig,
    # Core
    DjangoConfig,
    StartupInfoMode,
    set_current_config,
    # Infrastructure
    DatabaseConfig,
    ApiKeys,
    AxesConfig,
    FileCleanupConfig,
    StorageConfig,
    CurrencyConfig,
    # Services
    EmailConfig,
    TelegramConfig,
    # Auth
    JWTConfig,
    GitHubOAuthConfig,
    TwoFactorConfig,
    # Admin
    UnfoldConfig,
    # Dashboard tabs
    DashboardConfig,
    # API
    OpenAPIClientConfig,
    # Background Tasks
    DjangoRQConfig,
    # Dynamic Settings
    ConstanceConfig,
    # MCP (Model Context Protocol for AI agents)
    DjangoMCPModuleConfig,
)
from api.environment import env

from .builders.admin import build_unfold_config
from .builders.applications import build_project_apps
from .builders.background import build_rq_config
from .builders.constance import build_constance_config
from .builders.dashboard import build_dashboard_config
from .builders.openapi import build_api_keys, build_openapi_client_config
from .builders.mcp import build_mcp_config


class DjangoCfgConfig(DjangoConfig):
    """Sample settings, grouped like ``DjangoConfig``."""

    # ╔══════════════════════════════════════════════════════════════════════════╗
    # ║                         PROJECT INFORMATION                              ║
    # ╚══════════════════════════════════════════════════════════════════════════╝

    project_name: str = env.app.name
    project_version: str = "1.0.0"
    project_description: str = "Django CFG Project"
    admin_emails: list[str] = env.admin_emails

    # ╔══════════════════════════════════════════════════════════════════════════╗
    # ║                         ENVIRONMENT & DEBUG                              ║
    # ╚══════════════════════════════════════════════════════════════════════════╝

    env_mode: str = env.env.env_mode
    debug: bool = env.debug
    debug_warnings: bool = True

    # ╔══════════════════════════════════════════════════════════════════════════╗
    # ║                              SECURITY                                    ║
    # ╚══════════════════════════════════════════════════════════════════════════╝

    secret_key: str = env.secret_key
    security_domains: list[str] = env.security_domains or []

    # Django-Axes: Brute-force protection
    axes: AxesConfig = AxesConfig(
        failure_limit=3,
        cooloff_time=48,
        lockout_template=None,
    )

    # ╔══════════════════════════════════════════════════════════════════════════╗
    # ║                               URLS                                       ║
    # ╚══════════════════════════════════════════════════════════════════════════╝

    site_url: str = env.app.site_url
    api_url: str = env.app.api_url
    media_url: str = "/media/"
    root_urlconf: str = "api.urls"
    wsgi_application: str = "api.wsgi.application"

    # ╔══════════════════════════════════════════════════════════════════════════╗
    # ║                             DATABASE                                     ║
    # ╚══════════════════════════════════════════════════════════════════════════╝

    databases: Dict[str, DatabaseConfig] = {
        "default": DatabaseConfig.from_url(
            url=env.database.url,
            conn_max_age=0,
            conn_health_checks=False,
        ),
    }

    # ╔══════════════════════════════════════════════════════════════════════════╗
    # ║                               CACHE                                      ║
    # ╚══════════════════════════════════════════════════════════════════════════╝

    # Auto-creates Redis cache backend
    redis_url: Optional[str] = env.redis_url

    # ╔══════════════════════════════════════════════════════════════════════════╗
    # ║                            APPLICATIONS                                  ║
    # ╚══════════════════════════════════════════════════════════════════════════╝

    project_apps: list[str] = build_project_apps()

    # ╔══════════════════════════════════════════════════════════════════════════╗
    # ║                             SERVICES                                     ║
    # ╚══════════════════════════════════════════════════════════════════════════╝

    email: Optional[EmailConfig] = EmailConfig(
        backend=env.email.backend,
        host=env.email.host,
        port=env.email.port,
        username=env.email.username,
        password=env.email.password,
        use_tls=env.email.use_tls,
        use_ssl=env.email.use_ssl,
        ssl_verify=env.email.ssl_verify,
        default_from=env.email.default_from,
    )

    telegram: Optional[TelegramConfig] = (
        TelegramConfig(
            bot_token=env.telegram.bot_token,
            chat_id=env.telegram.chat_id,
        )
        if env.telegram.bot_token and env.telegram.chat_id != 0
        else None
    )

    # ╔══════════════════════════════════════════════════════════════════════════╗
    # ║                        AUTHENTICATION & OAUTH                            ║
    # ╚══════════════════════════════════════════════════════════════════════════╝

    # Secure defaults (short access + long refresh) live in JWTConfig — inherit them.
    # DPoP (RFC 9449) ON: tokens are bound to the client's non-extractable key
    # (frontend sets `dpop: true` in next.config) so a stolen token is useless.
    jwt: Optional[JWTConfig] = JWTConfig(dpop_enabled=True)

    github_oauth: Optional[GitHubOAuthConfig] = (
        GitHubOAuthConfig(
            enabled=True,
            client_id=env.github_oauth.client_id,
            client_secret=env.github_oauth.client_secret,
        )
        if env.github_oauth.client_id and env.github_oauth.client_secret
        else None
    )

    # Two-Factor Authentication (TOTP)
    two_factor: TwoFactorConfig = TwoFactorConfig(
        enabled=True,
        enforcement="required",  # optional, encouraged, required, admin_only
        session_lifetime_minutes=5,
        max_failed_attempts=5,
        grace_period_days=7,
        allow_totp=True,
        allow_backup_codes=True,
        backup_codes_count=10,
        issuer_name=env.app.name,
    )

    # ╔══════════════════════════════════════════════════════════════════════════╗
    # ║                          ADMIN INTERFACE                                 ║
    # ╚══════════════════════════════════════════════════════════════════════════╝

    unfold: UnfoldConfig = build_unfold_config()

    # ╔══════════════════════════════════════════════════════════════════════════╗
    # ║                          ADMIN DASHBOARD TABS                            ║
    # ╚══════════════════════════════════════════════════════════════════════════╝

    dashboard: DashboardConfig = build_dashboard_config()

    # ╔══════════════════════════════════════════════════════════════════════════╗
    # ║                               API                                        ║
    # ╚══════════════════════════════════════════════════════════════════════════╝

    api_keys: ApiKeys = build_api_keys()
    openapi_client: OpenAPIClientConfig = build_openapi_client_config()

    # ╔══════════════════════════════════════════════════════════════════════════╗
    # ║                          BACKGROUND TASKS                                ║
    # ╚══════════════════════════════════════════════════════════════════════════╝

    django_rq: Optional[DjangoRQConfig] = build_rq_config()

    # ╔══════════════════════════════════════════════════════════════════════════╗
    # ║                           INTEGRATIONS                                   ║
    # ╚══════════════════════════════════════════════════════════════════════════╝

    # ╔══════════════════════════════════════════════════════════════════════════╗
    # ║                     AI AGENTS & MCP                                      ║
    # ╚══════════════════════════════════════════════════════════════════════════╝

    # Declared in `api/settings/builders/mcp.py` — see that module for why it is
    # one declaration rather than an auto-discovered `mcp/` package.
    mcp: Optional[DjangoMCPModuleConfig] = build_mcp_config()

    # ╔══════════════════════════════════════════════════════════════════════════╗
    # ║                          CURRENCY & MONEY                                ║
    # ╚══════════════════════════════════════════════════════════════════════════╝

    currency: CurrencyConfig = CurrencyConfig(
        enabled=True,
        default_currency="USD",
        update_on_startup=False,
    )

    # ╔══════════════════════════════════════════════════════════════════════════╗
    # ║                          SEARCH ENGINES                                  ║
    # ╚══════════════════════════════════════════════════════════════════════════╝

    # IndexNow: every sitemap source row whose lastmod changed in the last 25 h
    # goes to Bing, Yandex, Seznam and Naver once a day. Off until
    # INDEXNOW__KEY is set; the key is served at /cfg/sitemap/indexnow/<key>.txt
    # and the frontend rewrites /<key>.txt there (indexNowKeyRewrite).
    # Try it: `manage.py indexnow_submit --dry-run`.
    indexnow: Optional[IndexNowConfig] = (
        IndexNowConfig(
            key=env.indexnow.key,
            host=env.indexnow.host or env.app.domain,
            trailing_slash=True,
        )
        if env.indexnow.key
        else None
    )

    # ╔══════════════════════════════════════════════════════════════════════════╗
    # ║                          STORAGE & FILES                                 ║
    # ╚══════════════════════════════════════════════════════════════════════════╝

    # Automatic file cleanup for FileField/ImageField
    storage: StorageConfig = StorageConfig(
        cleanup=FileCleanupConfig(
            auto_cleanup=True,
            delete_on_replace=True,
            log_deletions=env.debug,  # Log deletions in development
        )
    )

    # ╔══════════════════════════════════════════════════════════════════════════╗
    # ║                         DJANGO-CFG SETTINGS                              ║
    # ╚══════════════════════════════════════════════════════════════════════════╝

    startup_info_mode: StartupInfoMode = StartupInfoMode.SHORT

    # ╔══════════════════════════════════════════════════════════════════════════╗
    # ║                         DYNAMIC SETTINGS                                 ║
    # ╚══════════════════════════════════════════════════════════════════════════╝

    constance: ConstanceConfig = build_constance_config()


# Create and register configuration
config = DjangoCfgConfig()
set_current_config(config)
