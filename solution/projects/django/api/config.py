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
- Payments (NowPayments)
"""

from typing import Dict, Optional

from django_cfg import (
    # Core
    DjangoConfig,
    StartupInfoMode,
    set_current_config,
    # Infrastructure
    DatabaseConfig,
    BackupConfig,
    BackupStorageConfig,
    BackupScheduleConfig,
    BackupRetentionConfig,
    ApiKeys,
    AxesConfig,
    # Services
    EmailConfig,
    TelegramConfig,
    # Auth
    JWTConfig,
    GitHubOAuthConfig,
    # Admin
    UnfoldConfig,
    UnfoldColors,
    UnfoldSidebar,
    SiteDropdownItem,
    NavigationSection,
    NavigationItem,
    Icons,
    # API
    OpenAPIClientConfig,
    OpenAPIGroupConfig,
    WebPushConfig,
    # Background Tasks
    DjangoRQConfig,
    RQQueueConfig,
    RQScheduleConfig,
    # Integrations
    DjangoCfgCentrifugoConfig,
    GRPCConfig,
    NgrokConfig,
    NextJsAdminConfig,
    # Payments
    PaymentsConfig,
    NowPaymentsConfig,
    # Dynamic Settings
    ConstanceConfig,
    ConstanceField,
)

from .environment import env


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

    # Database backup configuration
    backup: Optional[BackupConfig] = BackupConfig(
        enabled=True,
        storage=BackupStorageConfig(
            backend="local",
            local_path="backups/",
        ),
        schedule=BackupScheduleConfig(
            enabled=True,
            cron="0 2 * * *",  # Daily at 2 AM
            queue="default",
        ),
        retention=BackupRetentionConfig(
            enabled=True,
            keep_daily=7,
            keep_weekly=4,
            keep_monthly=3,
        ),
        compression="gzip",
        notify_on_failure=True,
        notify_on_success=False,
    )

    # ╔══════════════════════════════════════════════════════════════════════════╗
    # ║                               CACHE                                      ║
    # ╚══════════════════════════════════════════════════════════════════════════╝

    # Auto-creates Redis cache backend
    redis_url: Optional[str] = env.redis_url

    # ╔══════════════════════════════════════════════════════════════════════════╗
    # ║                            APPLICATIONS                                  ║
    # ╚══════════════════════════════════════════════════════════════════════════╝

    project_apps: list[str] = [
        "core",
        "apps.profiles",
        "apps.trading",
        "apps.crypto",
    ]

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

    unfold: UnfoldConfig = UnfoldConfig(
        # Development autofill (auto-enabled in DEBUG mode)
        dev_autofill_email="admin@example.com",
        dev_autofill_password="admin123",
        dev_autofill_force=True,
        # Branding
        site_title=f"{env.app.name} Admin",
        site_header=env.app.name,
        site_subheader="Demo Project",
        site_url="/",
        site_symbol=Icons.ROCKET_LAUNCH,
        # Theme
        theme="dark",
        colors=UnfoldColors(primary="#3b82f6"),
        # Sidebar
        sidebar=UnfoldSidebar(
            show_search=True,
            show_all_applications=True,
        ),
        # Site dropdown
        site_dropdown=[
            SiteDropdownItem(
                icon=Icons.DEVELOPER_BOARD,
                title="Developer",
                link="https://djangocfg.com",
            ),
        ],
        # Navigation (auto-generated by django-cfg)
        navigation=[
            NavigationSection(
                title="Profiles",
                separator=True,
                collapsible=True,
                items=[
                    NavigationItem(title="User Profiles", icon=Icons.PERSON, link="admin:profiles_userprofile_changelist"),
                ],
            ),
            NavigationSection(
                title="Crypto Exchange",
                separator=True,
                collapsible=True,
                items=[
                    NavigationItem(title="Portfolios", icon=Icons.ACCOUNT_BALANCE_WALLET, link="admin:trading_portfolio_changelist"),
                    NavigationItem(title="Orders", icon=Icons.SHOPPING_CART, link="admin:trading_order_changelist"),
                    NavigationItem(title="Coins", icon=Icons.CURRENCY_BITCOIN, link="admin:crypto_coin_changelist"),
                    NavigationItem(title="Exchanges", icon=Icons.STOREFRONT, link="admin:crypto_exchange_changelist"),
                    NavigationItem(title="Wallets", icon=Icons.ACCOUNT_BALANCE_WALLET, link="admin:crypto_wallet_changelist"),
                    NavigationItem(title="User Profiles", icon=Icons.PERSON, link="admin:profiles_userprofile_changelist"),
                ],
            ),
        ],
    )

    # ╔══════════════════════════════════════════════════════════════════════════╗
    # ║                               API                                        ║
    # ╚══════════════════════════════════════════════════════════════════════════╝

    api_keys: ApiKeys = ApiKeys(
        openai=env.api_keys.openai,
        openrouter=env.api_keys.openrouter,
    )

    openapi_client: OpenAPIClientConfig = OpenAPIClientConfig(
        enabled=True,
        generate_package_files=True,
        generate_zod_schemas=True,
        generate_fetchers=True,
        generate_swr_hooks=True,
        api_prefix="api",
        output_dir="openapi",
        drf_title=f"{env.app.name} API",
        drf_description="Complete API documentation for Django CFG Demo Project",
        drf_version="1.0.0",
        groups=[
            OpenAPIGroupConfig(name="profiles", apps=["apps.profiles"], title="Profiles API", description="User profiles management", version="1.0.0"),
            OpenAPIGroupConfig(name="trading", apps=["apps.trading"], title="Trading API", description="Trading operations management", version="1.0.0"),
            OpenAPIGroupConfig(name="crypto", apps=["apps.crypto"], title="Crypto API", description="Crypto operations management", version="1.0.0"),
        ],
    )

    # ╔══════════════════════════════════════════════════════════════════════════╗
    # ║                          BACKGROUND TASKS                                ║
    # ╚══════════════════════════════════════════════════════════════════════════╝

    django_rq: Optional[DjangoRQConfig] = DjangoRQConfig(
        enabled=True,
        queues=[
            RQQueueConfig(queue="default", default_timeout=360, default_result_ttl=500),
            RQQueueConfig(queue="high", default_timeout=180, default_result_ttl=300),
            RQQueueConfig(queue="low", default_timeout=600, default_result_ttl=800),
            RQQueueConfig(queue="knowledge", default_timeout=600, default_result_ttl=3600),
        ],
        show_admin_link=True,
        prometheus_enabled=True,
        schedules=[
            RQScheduleConfig(func="apps.crypto.tasks.update_coin_prices", interval=300, queue="default", limit=50, verbosity=0, description="Update coin prices (frequent)"),
            RQScheduleConfig(func="apps.crypto.tasks.update_coin_prices", interval=3600, queue="default", limit=100, verbosity=1, description="Update coin prices (hourly)"),
            RQScheduleConfig(func="apps.crypto.tasks.import_coins", interval=86400, queue="low", description="Import new coins (daily)"),
            RQScheduleConfig(func="apps.crypto.tasks.generate_report", interval=86400, queue="low", report_type="daily", description="Generate daily crypto market report"),
        ],
    )

    # ╔══════════════════════════════════════════════════════════════════════════╗
    # ║                           INTEGRATIONS                                   ║
    # ╚══════════════════════════════════════════════════════════════════════════╝

    centrifugo: Optional[DjangoCfgCentrifugoConfig] = (
        DjangoCfgCentrifugoConfig(
            enabled=env.centrifugo.enabled,
            wrapper_url=env.centrifugo.wrapper_url,
            wrapper_api_key=env.centrifugo.wrapper_api_key,
            centrifugo_url=env.centrifugo.centrifugo_url,
            centrifugo_api_url=env.centrifugo.centrifugo_api_url,
            centrifugo_api_key=env.centrifugo.centrifugo_api_key,
            centrifugo_token_hmac_secret=env.centrifugo.centrifugo_token_hmac_secret,
            ack_timeout=env.centrifugo.default_ack_timeout,
            log_level=env.centrifugo.log_level,
            log_all_calls=env.centrifugo.log_all_calls,
            log_only_with_ack=env.centrifugo.log_only_with_ack,
        )
        if env.centrifugo.enabled
        else None
    )

    grpc: Optional[GRPCConfig] = GRPCConfig(
        enabled=True,
        host="0.0.0.0",
        port=50051,
        enabled_apps=[],
        package_prefix="api",
        public_url=env.grpc_url,
        publish_to_telegram=True,
        handlers_hook=[
            # "apps.*.grpc.services.handlers.grpc_handlers",
        ],
    )

    ngrok: Optional[NgrokConfig] = (
        NgrokConfig(enabled=True, compression=True)
        if env.debug
        else None
    )

    webpush: Optional[WebPushConfig] = (
        WebPushConfig(
            enabled=env.webpush.enabled,
            vapid_private_key=env.webpush.vapid_private_key,
            vapid_public_key=env.webpush.vapid_public_key,
            vapid_mailto=env.webpush.vapid_mailto,
        )
        if env.webpush.enabled
        else None
    )

    nextjs_admin: Optional[NextJsAdminConfig] = NextJsAdminConfig(
        project_path="../frontend/apps/admin",
        api_output_path="app/_lib/api/generated",
    )

    # ╔══════════════════════════════════════════════════════════════════════════╗
    # ║                            PAYMENTS                                      ║
    # ╚══════════════════════════════════════════════════════════════════════════╝

    # payments: Optional[PaymentsConfig] = PaymentsConfig(
    #     enabled=True,
    #     providers=[
    #         NowPaymentsConfig(
    #             enabled=True,
    #             api_key=env.nowpayments.api_key,
    #             ipn_secret=env.nowpayments.ipn_secret,
    #             sandbox=env.debug,
    #         ),
    #     ],
    # )

    # ╔══════════════════════════════════════════════════════════════════════════╗
    # ║                         DJANGO-CFG SETTINGS                              ║
    # ╚══════════════════════════════════════════════════════════════════════════╝

    startup_info_mode: StartupInfoMode = StartupInfoMode.SHORT

    # ╔══════════════════════════════════════════════════════════════════════════╗
    # ║                         DYNAMIC SETTINGS                                 ║
    # ╚══════════════════════════════════════════════════════════════════════════╝

    constance: ConstanceConfig = ConstanceConfig(
        fields=[
            ConstanceField(name="SITE_NAME", default=env.app.name, help_text="The name of the site", field_type="str", group="General"),
            ConstanceField(name="SITE_DESCRIPTION", default="A complete demonstration of django_cfg features", help_text="Brief description of the site", field_type="str", group="General"),
        ],
    )


# Create and register configuration
config = DjangoCfgConfig()
set_current_config(config)
