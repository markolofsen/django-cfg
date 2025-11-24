"""
Django CFG Sample Project Configuration

This is a complete example showing all django_cfg features:
- Type-safe configuration with Pydantic v2
- YAML-based environment configuration  
- Multiple databases with routing
- Cache configuration
- Email and Telegram services
- JWT authentication configuration
- Unfold admin interface
- Constance dynamic settings
- DRF API configuration
- Automatic URL integration
"""

from typing import Dict, List, Optional
from django_cfg import (
    DjangoConfig,
    StartupInfoMode,
    DatabaseConfig,
    EmailConfig,
    TelegramConfig,
    JWTConfig,
    UnfoldConfig,
    UnfoldColors,
    UnfoldSidebar,
    SiteDropdownItem,
    NavigationSection,
    NavigationItem,
    OpenAPIClientConfig,
    OpenAPIGroupConfig,
    NgrokConfig,
    ConstanceConfig,
    ConstanceField,
    Icons,
    set_current_config,
    PaymentsConfig,
    NowPaymentsConfig,
    ApiKeys,
    AxesConfig,
    DjangoCfgCentrifugoConfig,
    GRPCConfig,
    NextJsAdminConfig,
    DjangoRQConfig,
    RQQueueConfig,
    RQScheduleConfig,
)

# Import environment configuration
from .environment import env


class DjangoCfgConfig(DjangoConfig):
    """
    Django CFG configuration.

    Demonstrates all features and best practices with YAML environment loading.
    """

    # Keep env_mode as string like stockapis - prevents Pydantic enum conversion
    env_mode: str = env.env.env_mode
    debug_warnings: bool = True

    # === Project Information ===
    project_name: str = env.app.name
    project_logo: str = env.app.logo_url
    project_version: str = "1.0.0"
    project_description: str = "Demo Project"

    # === Admin Configuration ===
    admin_emails: List[str] = ["admin@sample.local"]

    # === Security ===
    secret_key: str = env.secret_key
    debug: bool = env.debug

    # === Django-Axes: Brute-force Protection ===
    # Custom configuration (optional - smart defaults used if None)
    axes: AxesConfig = AxesConfig(
        failure_limit=3,  # Only 3 attempts (stricter than default)
        cooloff_time=48,  # 48 hours lockout (stricter than default)
        lockout_template=None,  # Use default lockout page
        # Whitelist your admin IPs if needed
        # allowed_ips=['192.168.1.100'],
    )

    # === URL Configuration ===
    root_urlconf: str = "api.urls"
    wsgi_application: str = "api.wsgi.application"

    # === Django CFG Features ===
    startup_info_mode: StartupInfoMode = StartupInfoMode.SHORT  # FULL shows all info, SHORT for essential, NONE for minimal
    
    enable_support: bool = True
    enable_accounts: bool = True
    enable_newsletter: bool = True
    enable_leads: bool = True
    enable_knowbase: bool = True  # Requires tasks - auto-generates "knowledge" queue
    enable_agents: bool = True     # Enable agents for app generation
    enable_maintenance: bool = True

    # === Payments Configuration ===
    payments: PaymentsConfig = PaymentsConfig(
        enabled=True,
        nowpayments=NowPaymentsConfig(
            api_key=env.payments_api_keys.nowpayments_api_key,
            ipn_secret=env.payments_api_keys.nowpayments_ipn_secret or "",
            sandbox=env.payments_api_keys.nowpayments_sandbox_mode,
            enabled=bool(env.payments_api_keys.nowpayments_api_key),
        )
    )
    
    # === Centrifugo Configuration ===
    centrifugo: Optional[DjangoCfgCentrifugoConfig] = (
        DjangoCfgCentrifugoConfig(
            enabled=env.centrifugo.enabled,
            # Wrapper configuration
            wrapper_url=env.centrifugo.wrapper_url,
            wrapper_api_key=env.centrifugo.wrapper_api_key,
            # Centrifugo server configuration
            centrifugo_url=env.centrifugo.centrifugo_url,
            centrifugo_api_url=env.centrifugo.centrifugo_api_url,
            centrifugo_api_key=env.centrifugo.centrifugo_api_key,
            centrifugo_token_hmac_secret=env.centrifugo.centrifugo_token_hmac_secret,
            # Timeouts and behavior
            ack_timeout=env.centrifugo.default_ack_timeout,
            log_level=env.centrifugo.log_level,
            # Database logging configuration
            log_all_calls=env.centrifugo.log_all_calls,
            log_only_with_ack=env.centrifugo.log_only_with_ack,
        )
        if env.centrifugo.enabled
        else None
    )

    # === gRPC Configuration ===
    grpc: Optional[GRPCConfig] = GRPCConfig(
        enabled=True,
        host="0.0.0.0",
        port=50051,
        enabled_apps=["crypto"],
        package_prefix="api",  # Flatten field - no GRPCProtoConfig import needed!
        public_url=env.grpc_url,  # Flatten field from environment - simpler!
        publish_to_telegram=True,
        handlers_hook=[
            "apps.crypto.grpc.services.handlers.grpc_handlers",  # Auto-register CryptoService (NEW PATH!)
        ]
    )

    # === Django-RQ Background Tasks Configuration ===
    # MAGIC: redis_url is automatically used from DjangoConfig.redis_url! 🎉
    # NOTE: Auto-tasks are ENABLED BY DEFAULT (v1.5.35+)
    #       Production & Development:
    #       - cleanup_old_jobs runs daily (removes jobs older than 7 days)
    #       - cleanup_orphaned_job_keys runs weekly
    #       Development Only:
    #       - demo_scheduler_heartbeat runs every minute (verifies scheduler works)
    #       To customize: enable_auto_cleanup=True, cleanup_max_age_days=7
    django_rq: Optional[DjangoRQConfig] = DjangoRQConfig(
        enabled=True,
        queues=[
            # Default queue for general tasks
            RQQueueConfig(
                queue="default",
                default_timeout=360,
                default_result_ttl=500,
            ),
            # High priority queue for urgent tasks
            RQQueueConfig(
                queue="high",
                default_timeout=180,
                default_result_ttl=300,
            ),
            # Low priority queue for background tasks
            RQQueueConfig(
                queue="low",
                default_timeout=600,
                default_result_ttl=800,
            ),
            # Knowledge base queue (for enable_knowbase)
            RQQueueConfig(
                queue="knowledge",
                default_timeout=600,
                default_result_ttl=3600,
            ),
        ],
        show_admin_link=True,
        prometheus_enabled=True,
        # RQ Scheduler - scheduled jobs (cron-like tasks)
        schedules=[
            # Update cryptocurrency prices every 5 minutes
            RQScheduleConfig(
                func="apps.crypto.tasks.update_coin_prices",
                interval=300,  # Every 5 minutes
                queue="default",
                limit=50,
                verbosity=0,
                description="Update coin prices (frequent)",
            ),
            # Update all coin prices hourly with verbose output
            RQScheduleConfig(
                func="apps.crypto.tasks.update_coin_prices",
                interval=3600,  # Every hour
                queue="default",
                limit=100,
                verbosity=1,
                description="Update coin prices (hourly)",
            ),
            # Import new coins daily
            RQScheduleConfig(
                func="apps.crypto.tasks.import_coins",
                interval=86400,  # Every 24 hours
                queue="low",
                description="Import new coins (daily)",
            ),
            # Generate daily crypto market report
            RQScheduleConfig(
                func="apps.crypto.tasks.generate_report",
                interval=86400,  # Every 24 hours
                queue="low",
                report_type="daily",
                description="Generate daily crypto market report",
            ),
        ],
    )

    # === API Keys Configuration ===
    api_keys: ApiKeys = ApiKeys(
        openai=env.api_keys.openai,
        openrouter=env.api_keys.openrouter
    )

    # === URLs ===
    site_url: str = env.app.site_url
    api_url: str = env.app.api_url
    
    # === Security Domains ===
    security_domains: list[str] = env.security_domains or []

    # === Project Applications ===
    project_apps: list[str] = [
        "core",
        "apps.profiles",
        "apps.trading",
        "apps.crypto",
    ]

    # === Database Configuration with Routing ===
    # CRITICAL: Connection management to prevent connection exhaustion
    # Note: NOT using CONN_MAX_AGE because:
    # 1. RQ workers explicitly close connections with connection.close()
    # 2. Django pooling + persistent connections = ImproperlyConfigured error
    # 3. For production pooling, use external solution (PgBouncer)
    databases: Dict[str, DatabaseConfig] = {
        "default": DatabaseConfig.from_url(
            url=env.database.url,
            conn_max_age=0,             # Close connections immediately (no persistence)
            conn_health_checks=False,   # Not needed without pooling
        ),
    }

    # === Cache Configuration ===
    # MAGIC: Django-cfg auto-creates Redis cache from redis_url!
    # No need for explicit cache_default - it's handled automatically in CacheSettingsGenerator
    redis_url: Optional[str] = env.redis_url  # That's it! 🎉

    # === Email Configuration ===
    email: Optional[EmailConfig] = EmailConfig(
        backend=env.email.backend,  # "smtp" for real emails, "console" for development
        host=env.email.host,
        port=env.email.port,
        username=env.email.username,  # SMTP username
        password=env.email.password,  # SMTP password
        use_tls=env.email.use_tls,
        use_ssl=env.email.use_ssl,
        ssl_verify=env.email.ssl_verify,  # Verify SSL certs (False for self-signed in dev)
        default_from=env.email.default_from,  # Correct parameter name
    )

    # === Telegram Configuration ===
    telegram: Optional[TelegramConfig] = (
        TelegramConfig(
            bot_token=env.telegram.bot_token,
            chat_id=env.telegram.chat_id,
        )
        if env.telegram.bot_token and env.telegram.chat_id != 0
        else None
    )

    # === Unfold Admin Configuration ===
    unfold: UnfoldConfig = UnfoldConfig(
            site_title=f"{env.app.name} Admin",
            site_header=env.app.name,
            site_subheader="Demo Project",
            site_url="/",
            site_symbol=Icons.ROCKET_LAUNCH,
            theme='dark',  # None enables theme switcher, "light"/"dark" forces theme or None for auto detection
            colors=UnfoldColors(
                primary="#3b82f6",
            ),
            # Sidebar configuration
            sidebar=UnfoldSidebar(
                show_search=True,
                show_all_applications=True,
            ),
            # Site dropdown menu
            site_dropdown=[
                SiteDropdownItem(
                    icon=Icons.DEVELOPER_BOARD,
                    title="Developer",
                    link="https://djangocfg.com",
                ),
            ],
            # Navigation is auto-generated by django-cfg! 🎉
            # System sections (Dashboard, Operations, Accounts, Support, etc.) are automatically added
            # To add custom project-specific sections, add them via navigation parameter
            # You can use URL names (auto-resolved via reverse()) or direct URLs
            navigation=[
                NavigationSection(
                    title="Crypto Exchange",
                    separator=True,
                    collapsible=True,
                    items=[
                        # URL names are auto-resolved via reverse()
                        NavigationItem(title="Portfolios", icon=Icons.ACCOUNT_BALANCE_WALLET, link="admin:trading_portfolio_changelist"),
                        NavigationItem(title="Orders", icon=Icons.SHOPPING_CART, link="admin:trading_order_changelist"),
                        NavigationItem(title="Coins", icon=Icons.CURRENCY_BITCOIN, link="admin:crypto_coin_changelist"),
                        NavigationItem(title="Exchanges", icon=Icons.STOREFRONT, link="admin:crypto_exchange_changelist"),
                        NavigationItem(title="Wallets", icon=Icons.ACCOUNT_BALANCE_WALLET, link="admin:crypto_wallet_changelist"),
                        NavigationItem(title="User Profiles", icon=Icons.PERSON, link="admin:profiles_userprofile_changelist"),
                    ]
                ),
            ],
    )

    # === JWT Configuration ===
    jwt: Optional[JWTConfig] = JWTConfig(
        access_token_lifetime_hours=None,  # If None = maximum: 8760 hours/1 year
        refresh_token_lifetime_days=None,  # If None = maximum: 365 days/1 year
    )

    # === Ngrok Development Configuration ===
    ngrok: Optional[NgrokConfig] = None if not env.debug else NgrokConfig(
        enabled=True,
        compression=True,
    )

    # === Constance Dynamic Settings ===
    constance: ConstanceConfig = ConstanceConfig(
        fields=[
            ConstanceField(
                name="SITE_NAME",
                default=env.app.name,
                help_text="The name of the site",
                field_type="str",
                group="General",
            ),
            ConstanceField(
                name="SITE_DESCRIPTION",
                default="A complete demonstration of django_cfg features",
                help_text="Brief description of the site",
                field_type="str",
                group="General",
            ),
        ],
    )

    # === Django Client (OpenAPI) Configuration ===
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
            OpenAPIGroupConfig(
                name="profiles",
                apps=["apps.profiles"],
                title="Profiles API",
                description="User profiles management",
                version="1.0.0",
            ),
            OpenAPIGroupConfig(
                name="trading",
                apps=["apps.trading"],
                title="Trading API",
                description="Trading operations management",
                version="1.0.0",
            ),
            OpenAPIGroupConfig(
                name="crypto",
                apps=["apps.crypto"],
                title="Crypto API",
                description="Crypto operations management",
                version="1.0.0",
            ),
        ],
    )


    # === Next.js Admin Integration ===
    nextjs_admin: Optional[NextJsAdminConfig] = NextJsAdminConfig(
        # Path to Next.js admin project (relative to manage.py directory)
        project_path="../frontend/apps/admin",
        # Customize where TypeScript clients are copied
        api_output_path="src/api/generated",
        # Optional: static files URL prefix (default: /cfg/admin/)
        # static_url="/cfg/admin/",
        # Optional: Next.js dev server URL (default: http://localhost:3001)
        # dev_url="http://localhost:3001",
        # Optional: iframe route for default view (default: /private)
        # iframe_route="/private",
        # Optional: tab title in admin (default: Next.js Admin)
        # tab_title="Dashboard",
    )


# Create configuration instance
config = DjangoCfgConfig()

# Set as current config for global access
set_current_config(config)
