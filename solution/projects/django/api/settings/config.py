"""
Django CFG Sample Project Configuration

Complete example demonstrating all django_cfg features:
- Type-safe configuration with Pydantic v2
- YAML-based environment configuration
- Database, Cache, Email, Telegram
- JWT & OAuth authentication
- Unfold admin interface
- Constance dynamic settings
- DRF API & OpenAPI generation
- Background tasks (Django-RQ)
- Real-time (Centrifugo, gRPC)
- Database backups
"""

from typing import Dict, Optional

from django_cfg import (
    # Core
    DjangoConfig,
    StartupInfoMode,
    set_current_config,
    # Infrastructure
    DatabaseConfig,
    ApiKeys,
    AxesConfig,
    StorageConfig,
    CurrencyConfig,
    FrontendMonitorConfig,
    CloudflareConfig,
    # Services
    EmailConfig,
    TelegramConfig,
    # Auth
    JWTConfig,
    GitHubOAuthConfig,
    # Admin
    UnfoldConfig,
    # Dashboard tabs
    DashboardConfig,
    # API
    OpenAPIClientConfig,
    # Background Tasks
    DjangoRQConfig,
    # Integrations
    DjangoCfgCentrifugoConfig,
    DjangoGrpcModuleConfig,
    NgrokConfig,
    # Dynamic Settings
    ConstanceConfig,
)
from api.environment import env

from .configs.admin import build_unfold_config
from .configs.applications import build_project_apps
from .configs.background import build_rq_config
from .configs.constance import build_constance_config
from .configs.dashboard import build_dashboard_config
from .configs.integrations import (
    build_centrifugo_config,
    build_cloudflare_config,
    build_grpc_module_config,
    build_ngrok_config,
)
from .configs.openapi import build_api_keys, build_openapi_client_config


class DjangoCfgConfig(DjangoConfig):
    """
    Django CFG Demo Project Configuration.

    All settings are organized by logical groups matching DjangoConfig structure.
    """

    # ╔══════════════════════════════════════════════════════════════════════════╗
    # ║                         PROJECT INFORMATION                              ║
    # ╚══════════════════════════════════════════════════════════════════════════╝

    project_name: str = env.app.name
    project_version: str = "1.0.0"
    project_description: str = "Demo Project"
    project_logo: str = env.app.logo_url
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

    jwt: Optional[JWTConfig] = JWTConfig(
        access_token_lifetime_hours=None,  # Max: 1 year
        refresh_token_lifetime_days=None,  # Max: 1 year
    )

    github_oauth: Optional[GitHubOAuthConfig] = (
        GitHubOAuthConfig(
            enabled=True,
            client_id=env.github_oauth.client_id,
            client_secret=env.github_oauth.client_secret,
        )
        if env.github_oauth.client_id and env.github_oauth.client_secret
        else None
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

    centrifugo: Optional[DjangoCfgCentrifugoConfig] = build_centrifugo_config()

    grpc_module: Optional[DjangoGrpcModuleConfig] = build_grpc_module_config()

    ngrok: Optional[NgrokConfig] = build_ngrok_config()

    # ╔══════════════════════════════════════════════════════════════════════════╗
    # ║                        CLOUDFLARE D1                                     ║
    # ╚══════════════════════════════════════════════════════════════════════════╝

    cloudflare: Optional[CloudflareConfig] = build_cloudflare_config()

    # ╔══════════════════════════════════════════════════════════════════════════╗
    # ║                       FRONTEND MONITORING                                ║
    # ╚══════════════════════════════════════════════════════════════════════════╝

    frontend_monitor: FrontendMonitorConfig = FrontendMonitorConfig(
        enabled=True,
        retention_days=90,
        telegram_alerts_enabled=True,
    )

    # ╔══════════════════════════════════════════════════════════════════════════╗
    # ║                          CURRENCY & MONEY                                ║
    # ╚══════════════════════════════════════════════════════════════════════════╝

    currency: CurrencyConfig = CurrencyConfig(
        enabled=True,
        default_currency="USD",
        update_on_startup=False,
    )

    # ╔══════════════════════════════════════════════════════════════════════════╗
    # ║                          STORAGE & FILES                                 ║
    # ╚══════════════════════════════════════════════════════════════════════════╝

    # Automatic file cleanup for FileField/ImageField
    storage: StorageConfig = StorageConfig(
        auto_cleanup=True,
        delete_on_replace=True,
        log_deletions=env.debug,  # Log deletions in development
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
