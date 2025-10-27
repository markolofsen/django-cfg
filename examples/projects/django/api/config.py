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
    databases: Dict[str, DatabaseConfig] = {
        "default": DatabaseConfig.from_url(url=env.database.url),
    }

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

            # Dashboard callback for custom metrics
            dashboard_callback="api.config.dashboard_callback",
    )

    # === JWT Configuration ===
    jwt: Optional[JWTConfig] = JWTConfig(
        access_token_lifetime_hours=None,  # If None = maximum: 8760 hours/1 year
        refresh_token_lifetime_days=None,  # If None = maximum: 365 days/1 year
    )

    # === Ngrok Development Configuration ===
    ngrok: Optional[NgrokConfig] = NgrokConfig(
        enabled=True,
        compression=True,
    ) if env.debug else None

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

    NEW: Supports custom widgets via context["custom_widgets"] for Widgets tab!
    """
    from django_cfg.modules.django_unfold.callbacks import UnfoldCallbacks
    from django_cfg.modules.django_unfold.models.dashboard import StatCard, StatsCardsWidget

    try:
        # Get real data from models FIRST (before calling base callback)
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

        # Create widgets for Widgets tab using template variables
        # IMPORTANT: Do this BEFORE calling main_dashboard_callback!
        custom_widgets = [
            StatsCardsWidget(
                title="User & Activity Metrics",
                cards=[
                    StatCard(
                        title="Total Users",
                        value="{{ total_users }}",
                        icon=Icons.PEOPLE,
                        change="{{ recent_users_change }}",
                        change_type="positive" if recent_users > 0 else "neutral",
                        description="Registered users",
                        color="primary"
                    ),
                    StatCard(
                        title="User Profiles",
                        value="{{ total_profiles }}",
                        icon=Icons.PERSON,
                        description="Active profiles",
                        color="primary"
                    ),
                    StatCard(
                        title="Orders Today",
                        value="{{ orders_today }}",
                        icon=Icons.TODAY,
                        description="Orders placed today",
                        color="green"
                    ),
                    StatCard(
                        title="Recent Orders (7d)",
                        value="{{ recent_orders }}",
                        icon=Icons.TRENDING_UP,
                        description="Orders last 7 days",
                        color="blue"
                    ),
                ]
            ),
            StatsCardsWidget(
                title="Crypto Exchange Metrics",
                cards=[
                    StatCard(
                        title="Total Orders",
                        value="{{ total_orders }}",
                        icon=Icons.SHOPPING_CART,
                        description="All time orders",
                        color="primary"
                    ),
                    StatCard(
                        title="Active Coins",
                        value="{{ total_coins }}",
                        icon=Icons.CURRENCY_BITCOIN,
                        description="Tradeable coins",
                        color="orange"
                    ),
                    StatCard(
                        title="Exchanges",
                        value="{{ total_exchanges }}",
                        icon=Icons.STOREFRONT,
                        description="Connected exchanges",
                        color="purple"
                    ),
                    StatCard(
                        title="Total Wallets",
                        value="{{ total_wallets }}",
                        icon=Icons.ACCOUNT_BALANCE_WALLET,
                        description="User wallets",
                        color="green"
                    ),
                ]
            ),
        ]

        # Add custom widgets and metrics to context BEFORE calling main_dashboard_callback
        context.update({
            # Widgets tab widgets (MUST be added before main_dashboard_callback!)
            "custom_widgets": custom_widgets,

            # Template variables for widgets
            "total_users": total_users,
            "total_profiles": total_profiles,
            "orders_today": orders_today,
            "recent_orders": recent_orders,
            "recent_users_change": f"+{recent_users}" if recent_users > 0 else "0",
            "total_orders": total_orders,
            "total_coins": total_coins,
            "total_exchanges": total_exchanges,
            "total_wallets": total_wallets,
        })

        # NOW call base callback - it will pick up custom_widgets from context!
        unfold_callbacks = UnfoldCallbacks()
        context = unfold_callbacks.main_dashboard_callback(request, context)

        # Add dashboard metadata
        context.update({
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
