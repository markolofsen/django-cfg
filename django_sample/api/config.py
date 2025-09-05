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

from typing import Dict, Optional
from pathlib import Path
from django_cfg import (
    DjangoConfig,
    DatabaseConnection,
    CacheBackend,
    EmailConfig,
    TelegramConfig,
    JWTConfig,
    UnfoldConfig,
    UnfoldTheme,
    UnfoldColors,
    UnfoldSidebar,
    NavigationGroup,
    NavigationItem,
    DRFConfig,
    SpectacularConfig,
    ConstanceConfig,
    ConstanceField,
    RevolutionConfig,
    ZoneConfig,
)
from django_cfg.models.limits import LimitsConfig

# Import environment configuration
from .environment import env




class SampleProjectConfig(DjangoConfig):
    """
    Complete django_cfg sample configuration.

    Demonstrates all features and best practices with YAML environment loading.
    """

    # === Project Information ===
    project_name: str = env.app.name
    project_logo: str = env.app.logo_url
    project_version: str = "1.0.0"
    project_description: str = "Complete demonstration of django_cfg features"

    # === Security ===
    secret_key: str = env.secret_key
    debug: bool = env.debug
    ssl_redirect: Optional[bool] = env.ssl_redirect

    # === Django CFG Features ===
    enable_support: bool = True
    enable_accounts: bool = True

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
        "apps.core",
        # "apps.users",
        "apps.blog",
        "apps.shop",
    ]

    # === Database Configuration with Routing ===
    databases: Dict[str, DatabaseConnection] = {
        # Main application database - engine auto-detected from URL
        "default": DatabaseConnection.from_url(url=env.database.url),
        
        # Blog database with routing - engine auto-detected
        "blog_db": DatabaseConnection.from_url(
            url=env.database.url_blog,
            apps=["apps.blog"],
            operations=["read", "write", "migrate"],  # Allow migrations
            routing_description="Blog posts and comments",
        ),
        
        # Shop database with routing - engine auto-detected
        "shop_db": DatabaseConnection.from_url(
            url=env.database.url_shop,
            apps=["apps.shop"],
            operations=["read", "write", "migrate"],  # Allow migrations
            routing_description="Products, orders, and inventory",
        ),
    }

    # === Cache Configuration ===
    cache_default: Optional[CacheBackend] = CacheBackend(
        redis_url=env.redis_url if env.redis_url else None,
        timeout=300,
        key_prefix="sample_default",
    )

    cache_sessions: Optional[CacheBackend] = CacheBackend(
        redis_url=env.redis_url if env.redis_url else None,
        timeout=3600,
        key_prefix="sample_sessions",
    )

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
        if env.email.backend != "console"
        else None
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

    # === JWT Configuration ===
    jwt: Optional[JWTConfig] = JWTConfig(
        # Environment-aware token lifetimes
        # access_token_lifetime_hours=1 if debug else 24,
        # refresh_token_lifetime_days=7 if debug else 30,
        access_token_lifetime_hours=None, # If None = maximum: 8760 hours/1 year
        refresh_token_lifetime_days=None, # If None = maximum: 365 days/1 year
        
        # Security settings
        rotate_refresh_tokens=True,
        blacklist_after_rotation=True,
        update_last_login=True,
        
        # Optional: Custom claims for sample project
        audience="django-cfg-sample",
        issuer="django-cfg",
    )

    # === Unfold Admin Configuration ===
    unfold: UnfoldConfig = UnfoldConfig(
        theme=UnfoldTheme(
            site_title=f"{env.app.name} Admin",
            site_header=env.app.name,
            site_url="/",
            theme="auto",  # auto, light, dark, or None for switcher
            colors=UnfoldColors(
                primary="#3b82f6",
            ),
            # Sidebar configuration
            sidebar=UnfoldSidebar(
                show_search=True,
                show_all_applications=True,
            ),
            # Navigation
            navigation=[
                NavigationGroup(
                    title="Dashboard",
                    items=[
                        NavigationItem(title="Overview", icon="dashboard", link="admin:index"),
                    ],
                ),
                NavigationGroup(
                    title="Content",
                    items=[
                        NavigationItem(title="Blog Posts", icon="article", link="admin:blog_post_changelist"),
                        NavigationItem(title="Comments", icon="comment", link="admin:blog_comment_changelist"),
                    ],
                ),
                NavigationGroup(
                    title="E-commerce",
                    items=[
                        NavigationItem(title="Products", icon="inventory", link="admin:shop_product_changelist"),
                        NavigationItem(title="Orders", icon="shopping_cart", link="admin:shop_order_changelist"),
                        NavigationItem(title="Categories", icon="category", link="admin:shop_category_changelist"),
                    ],
                ),
                # NavigationGroup(
                #     title="Users",
                #     items=[
                #         NavigationItem(title="Users", icon="people", link="admin:users_user_changelist"),
                #         NavigationItem(title="User Profiles", icon="person", link="admin:users_userprofile_changelist"),
                #         NavigationItem(title="User Activity", icon="history", link="admin:users_useractivity_changelist"),
                #         NavigationItem(title="Groups", icon="group", link="admin:auth_group_changelist"),
                #     ],
                # ),
            ],
            # Dashboard callback for custom metrics
            dashboard_callback="api.config.dashboard_callback",
        ),
    )

    # === DRF Configuration ===
    # DRF is automatically configured by django_cfg
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
    #     # Spectacular (OpenAPI) configuration
    #     spectacular=SpectacularConfig(
    #         title=f"{env.app.name} API",
    #         description="Complete API documentation for Django CFG sample project",
    #         version="1.0.0",
    #         contact_email="admin@sample.local",
    #         license_name="MIT",
    #         serve_include_schema=False,
    #     ),
    # )

    # === Application Limits Configuration ===
    limits: LimitsConfig = LimitsConfig(
        max_upload_mb=20.0,  # 20MB for sample project
        max_memory_mb=5.0,   # 5MB in memory
        max_request_mb=25.0, # 25MB total request
        allowed_extensions=["jpg", "jpeg", "png", "gif", "pdf", "txt", "docx"],
        blocked_extensions=["exe", "bat", "cmd", "php", "js", "py"],
        request_timeout=60,  # 60 seconds timeout for sample
        enabled=True,
        strict_mode=debug,  # Strict mode only in development
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
            ConstanceField(
                name="MAINTENANCE_MODE",
                default=False,
                help_text="Enable maintenance mode",
                field_type="bool",
                group="General",
            ),
            ConstanceField(
                name="MAX_POSTS_PER_PAGE",
                default=10,
                help_text="Number of blog posts per page",
                field_type="int",
                group="Blog",
            ),
            ConstanceField(
                name="FEATURED_PRODUCT_COUNT",
                default=6,
                help_text="Number of featured products to display",
                field_type="int",
                group="Shop",
            ),
        ],
    )

    # === Django Revolution API Configuration ===
    revolution: RevolutionConfig = RevolutionConfig(
        api_prefix="api",
        debug=debug,
        auto_install_deps=True,
        # DRF Configuration
        drf_title=f"{env.app.name} API",
        drf_description="Complete API documentation for Django CFG sample project",
        drf_version="1.0.0",
        drf_schema_path_prefix="/apix/",  # Match api_prefix
        drf_enable_browsable_api=True,
        drf_enable_throttling=False,  # Disable for sample

        zones={
            "blog": ZoneConfig(
                apps=["apps.blog"],
                title="Blog API",
                description="Blog posts and comments management",
                public=True,
                auth_required=False,
                version="v1",
            ),
            "shop": ZoneConfig(
                apps=["apps.shop"],
                title="Shop API", 
                description="E-commerce products, orders and categories",
                public=True,
                auth_required=False,
                version="v1",
            ),
            # "users": ZoneConfig(
            #     apps=["apps.users"],
            #     title="Users API",
            #     description="User management and authentication",
            #     public=False,
            #     auth_required=True,
            #     version="v1",
            # ),
        },
    )


# Create configuration instance
config = SampleProjectConfig()


def dashboard_callback(request, context):
    """
    Django CFG Sample dashboard callback.
    
    Uses Django CFG's base system monitoring and adds sample-specific metrics.
    """
    from django_cfg.modules.unfold.callbacks import UnfoldCallbacks
    from django_cfg.modules.unfold.models import StatCard

    try:
        # Use Django CFG's base callback for system metrics, quick actions, etc.
        unfold_callbacks = UnfoldCallbacks()
        context = unfold_callbacks.main_dashboard_callback(request, context)

        # Get real data from models
        from apps.blog.models import Post, Comment
        from apps.shop.models import Product, Order, Category
        from apps.users.models import User
        from django.utils import timezone
        from datetime import timedelta

        # Calculate real metrics
        total_users = User.objects.count()
        total_posts = Post.objects.filter(status='published').count()
        total_comments = Comment.objects.count()
        total_products = Product.objects.filter(status='active').count()
        total_categories = Category.objects.count()
        total_orders = Order.objects.count()
        
        # Orders today
        today = timezone.now().date()
        orders_today = Order.objects.filter(created_at__date=today).count()
        
        # Recent activity (last 7 days for comparison)
        week_ago = timezone.now() - timedelta(days=7)
        recent_users = User.objects.filter(created_at__gte=week_ago).count()
        recent_posts = Post.objects.filter(created_at__gte=week_ago, status='published').count()
        recent_orders = Order.objects.filter(created_at__gte=week_ago).count()

        # Add real metrics cards
        sample_cards = [
            StatCard(
                title="Total Users", 
                value=str(total_users), 
                icon="people", 
                change=f"+{recent_users}" if recent_users > 0 else "0", 
                change_type="positive" if recent_users > 0 else "neutral", 
                description="Registered users", 
                color="primary"
            ),
            StatCard(
                title="Blog Posts", 
                value=str(total_posts), 
                icon="article", 
                change=f"+{recent_posts}" if recent_posts > 0 else "0", 
                change_type="positive" if recent_posts > 0 else "neutral", 
                description="Published posts", 
                color="success"
            ),
            StatCard(
                title="Comments", 
                value=str(total_comments), 
                icon="comment", 
                change="", 
                change_type="neutral", 
                description="Total comments", 
                color="info"
            ),
            StatCard(
                title="Products", 
                value=str(total_products), 
                icon="inventory", 
                change="", 
                change_type="neutral", 
                description="Active products", 
                color="info"
            ),
            StatCard(
                title="Categories", 
                value=str(total_categories), 
                icon="category", 
                change="", 
                change_type="neutral", 
                description="Product categories", 
                color="secondary"
            ),
            StatCard(
                title="Total Orders", 
                value=str(total_orders), 
                icon="shopping_cart", 
                change=f"+{recent_orders}" if recent_orders > 0 else "0", 
                change_type="positive" if recent_orders > 0 else "neutral", 
                description="All time orders", 
                color="warning"
            ),
            StatCard(
                title="Orders Today", 
                value=str(orders_today), 
                icon="today", 
                change="", 
                change_type="neutral", 
                description="Orders placed today", 
                color="warning"
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
