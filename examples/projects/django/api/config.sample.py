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
from decimal import Decimal
from django_cfg import (
    DjangoConfig,
    StartupInfoMode,
    DatabaseConfig,
    CacheConfig,
    EmailConfig,
    TelegramConfig,
    JWTConfig,
    UnfoldConfig,
    UnfoldThemeConfig,
    UnfoldColors,
    UnfoldSidebar,
    UnfoldTheme,
    SiteDropdownItem,
    NavigationSection,
    NavigationItem,
    OpenAPIClientConfig,
    OpenAPIGroupConfig,
    LimitsConfig,
    TaskConfig,
    DramatiqConfig,
    NgrokConfig,
    DRFConfig,
    SpectacularConfig,
    ConstanceConfig,
    ConstanceField,
    Icons,
    IconCategories,
    set_current_config,
    PaymentsConfig,
    NowPaymentsConfig,
    ApiKeys,
    DjangoCfgRPCConfig,
)

# Import environment configuration
from .environment import env


class DjangoCfgConfig(DjangoConfig):
    """
    Django CFG configuration.

    Demonstrates all features and best practices with YAML environment loading.
    """
    
    env_mode: str = env.env.env_mode

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

    # ssl_redirect: Optional[bool] = None  # Auto: disabled (assumes reverse proxy handles SSL)
    # Uncomment and set to True ONLY if Django handles SSL directly (rare: bare metal without nginx/traefik)

    # === URL Configuration ===
    root_urlconf: str = "api.urls"
    wsgi_application: str = "api.wsgi.application"

    # === Django CFG Features ===
    startup_info_mode: StartupInfoMode = StartupInfoMode.FULL  # FULL shows all info, SHORT for essential, NONE for minimal
    
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
    
    # === RPC Configuration ===
    django_ipc: Optional[DjangoCfgRPCConfig] = (
        DjangoCfgRPCConfig(
            enabled=env.rpc.enabled,
            redis_url=env.rpc.redis_url,
            redis_max_connections=env.rpc.redis_max_connections,
            rpc_timeout=env.rpc.rpc_timeout,
            request_stream=env.rpc.request_stream,
            consumer_group=env.rpc.consumer_group,
            stream_maxlen=env.rpc.stream_maxlen,
            response_key_prefix=env.rpc.response_key_prefix,
            response_key_ttl=env.rpc.response_key_ttl,
            log_rpc_calls=env.rpc.log_rpc_calls,
            log_level=env.rpc.log_level,
        )
        if env.rpc.enabled
        else None
    )

    # === API Keys Configuration ===
    api_keys: ApiKeys = ApiKeys(
        openai=env.api_keys.openai,
        openrouter=env.api_keys.openrouter
    )

    # === URLs ===
    site_url: str = env.app.site_url
    api_url: str = env.app.api_url
    ticket_url: str = env.app.ticket_url
    otp_url: str = env.app.otp_url
    
    # === Security Domains ===
    security_domains: list[str] = env.security_domains or []

    # === Custom User Model ===
    # auth_user_model: str = "users.User"

    # === Project Applications ===
    project_apps: list[str] = [
        "core",
        "apps.profiles",
        "apps.trading",
        "apps.crypto",
    ]

    # === Database Configuration with Routing ===
    databases: Dict[str, DatabaseConfig] = {
        # Main application database - engine auto-detected from URL
        "default": DatabaseConfig.from_url(url=env.database.url),

    #     # Demo database with routing - engine auto-detected
    #    "demo_db": DatabaseConfig.from_url(
    #         url=env.database.url_demo,
    #         apps=["trading"],  # Use app_label, not full Python path
    #         operations=["read", "write", "migrate"],  # Allow migrations
    #         routing_description="Demo portfolios and orders",
    #    ),
    }

    # === Cache Configuration ===
    # cache_default: Optional[CacheConfig] = CacheConfig(
    #     redis_url=env.redis_url if env.redis_url else None,
    #     timeout=300,
    #     key_prefix="sample_default",
    # )

    # cache_sessions: Optional[CacheConfig] = CacheConfig(
    #     redis_url=env.redis_url if env.redis_url else None,
    #     timeout=3600,
    #     key_prefix="sample_sessions",
    # )


    # === Email Configuration ===
    email: Optional[EmailConfig] = (
        EmailConfig(
            host=env.email.host,
            port=env.email.port,
            use_tls=env.email.use_tls,
            use_ssl=env.email.use_ssl,
            default_from_email=env.email.default_from,
            default_from_name=env.app.name,
        )
        # if env.env.is_prod
        # else None
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

            # Dashboard callback for custom metrics
            dashboard_callback="api.config.dashboard_callback",
    )

    # === JWT Configuration ===
    jwt: Optional[JWTConfig] = JWTConfig(
        # Environment-aware token lifetimes
        # access_token_lifetime_hours=1 if debug else 24,
        # refresh_token_lifetime_days=7 if debug else 30,
        access_token_lifetime_hours=None, # If None = maximum: 8760 hours/1 year
        refresh_token_lifetime_days=None, # If None = maximum: 365 days/1 year
        
        # Security settings
        # rotate_refresh_tokens=True,
        # blacklist_after_rotation=True,
        # update_last_login=True,
        
        # # Optional: Custom claims for sample project
        # audience="django-cfg-sample",
        # issuer="django-cfg",
    )

    # === DRF Configuration ===
    # DRF with Tailwind CSS theme
    # drf: Optional[DRFConfig] = DRFConfig(
    #     default_authentication_classes=[
    #         "rest_framework.authentication.SessionAuthentication",
    #         "rest_framework.authentication.TokenAuthentication",
    #     ],
    #     default_permission_classes=[
    #         "rest_framework.permissions.IsAuthenticated",
    #     ],
    #     default_pagination_class="rest_framework.pagination.PageNumberPagination",
    #     page_size=20,
    #     # Use Tailwind Browsable API renderer
    #     renderer_classes=[
    #         'rest_framework.renderers.JSONRenderer',
    #         'django_cfg.modules.django_drf_theme.renderers.TailwindBrowsableAPIRenderer',
    #     ],
    #     # Spectacular (OpenAPI) configuration - disabled temporarily
    #     # spectacular=SpectacularConfig(
    #     #     title=f"{env.app.name} API",
    #     #     description="Complete API documentation for Django CFG sample project",
    #     #     version="1.0.0",
    #     #     contact_email="admin@sample.local",
    #     #     license_name="MIT",
    #     #     serve_include_schema=False,
    #     # ),
    # )

    # === Application Limits Configuration ===
    # limits: LimitsConfig = LimitsConfig(
    #     max_upload_mb=20.0,  # 20MB for sample project
    #     max_memory_mb=5.0,   # 5MB in memory
    #     max_request_mb=25.0, # 25MB total request
    #     allowed_extensions=["jpg", "jpeg", "png", "gif", "pdf", "txt", "docx"],
    #     blocked_extensions=["exe", "bat", "cmd", "php", "js", "py"],
    #     request_timeout=60,  # 60 seconds timeout for sample
    #     enabled=True,
    #     strict_mode=debug,  # Strict mode only in development
    # )

    # === Ngrok Development Configuration ===
    # Super simple! Domain/schemes auto-detected from api_url
    # Run with: python manage.py runserver_ngrok
    # Uses NGROK_AUTHTOKEN environment variable
    ngrok: Optional[NgrokConfig] = NgrokConfig(
        enabled=True,
        compression=True,  # Optional: enable gzip
    ) if env.debug else None

    # === Background Task Processing (Dramatiq) ===
    # TaskConfig is AUTO-INITIALIZED by django-cfg! 🚀
    # 
    # Smart detection automatically enables tasks when:
    # ✅ enable_knowbase = True → adds "knowbase" queue  
    # ✅ payments.enabled = True → adds "payments" queue
    # ✅ enable_agents = True → adds "agents" queue
    #
    # Generated queues: ["default", "knowbase", "payments"] (debug mode)
    # Generated queues: ["critical", "high", "default", "low", "background", "knowbase", "payments"] (production)
    #
    # To override, uncomment and customize:
    # tasks: Optional[TaskConfig] = TaskConfig(
    #     enabled=True,
    #     dramatiq=DramatiqConfig(
    #         redis_db=2,  # Matches test scripts
    #         queues=["default", "high", "low", "knowbase", "payments"],
    #     ),
    # )

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


# Create configuration instance
config = DjangoCfgConfig()

# Set as current config for global access
set_current_config(config)


def dashboard_callback(request, context):
    """
    Django CFG dashboard callback.
    
    Uses Django CFG's base system monitoring and adds sample-specific metrics.
    """
    from django_cfg.modules.django_unfold.callbacks import UnfoldCallbacks
    from django_cfg.modules.django_unfold.models.dashboard import StatCard

    try:
        # Use Django CFG's base callback for system metrics, quick actions, etc.
        unfold_callbacks = UnfoldCallbacks()
        context = unfold_callbacks.main_dashboard_callback(request, context)

        # Get real data from models
        from apps.profiles.models import UserProfile
        from django_cfg.apps.accounts.models import CustomUser
        from django.utils import timezone
        from datetime import timedelta
        from apps.trading.models import Order
        from apps.crypto.models import Coin, Exchange, Wallet

        # Calculate real metrics
        total_users = CustomUser.objects.count()
        total_profiles = UserProfile.objects.count()

        # Orders today
        today = timezone.now().date()
        orders_today = Order.objects.filter(created_at__date=today).count()

        # Recent activity (last 7 days for comparison)
        week_ago = timezone.now() - timedelta(days=7)
        recent_users = CustomUser.objects.filter(date_joined__gte=week_ago).count()
        recent_orders = Order.objects.filter(created_at__gte=week_ago).count()
        total_coins = Coin.objects.filter(is_active=True).count()
        total_exchanges = Exchange.objects.filter(is_active=True).count()
        total_wallets = Wallet.objects.count()
        total_orders = Order.objects.count()

        # Add real metrics cards
        sample_cards = [
            StatCard(
                title="Total Users",
                value=str(total_users),
                icon=Icons.PEOPLE,
                change=f"+{recent_users}" if recent_users > 0 else "0",
                change_type="positive" if recent_users > 0 else "neutral",
                description="Registered users",
                color="primary"
            ),
            StatCard(
                title="User Profiles",
                value=str(total_profiles),
                icon=Icons.PERSON,
                change="",
                change_type="neutral",
                description="Active profiles",
                color="primary"
            ),
            StatCard(
                title="Total Orders",
                value=str(total_orders),
                icon=Icons.SHOPPING_CART,
                change="",
                change_type="neutral",
                description="Total orders",
                color="primary"
            ),
            StatCard(
                title="Total Coins",
                value=str(total_coins),
                icon=Icons.CURRENCY_BITCOIN,
                change="",
                change_type="neutral",
                description="Total coins",
                color="primary"
            ),
            StatCard(
                title="Total Exchanges",
                value=str(total_exchanges),
                icon=Icons.STOREFRONT,
                change="",
                change_type="neutral",
                description="Total exchanges",
                color="primary"
            ),
            StatCard(
                title="Total Wallets",
                value=str(total_wallets),
                icon=Icons.ACCOUNT_BALANCE_WALLET,
                change="",
                change_type="neutral",
                description="Total wallets",
                color="primary"
            ),
        ]

        # Convert to dict and add to existing cards
        existing_cards = context.get("cards", [])
        sample_cards_dict = [card.model_dump() for card in sample_cards]

        # Update context with combined data
        context.update({
            "cards": existing_cards + sample_cards_dict,
            "dashboard_title": f"{env.app.name} Dashboard",
            "dashboard_subtitle": "Django CFG Sample Project",
            "sample_version": "1.0.0",
        })

        return context

    except Exception as e:
        # Fallback in case of error
        context.update({
            "dashboard_title": f"{env.app.name} Dashboard",
            "error": f"Dashboard error: {str(e)}",
        })
        return context
