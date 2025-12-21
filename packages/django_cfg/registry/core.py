"""
Core Django-CFG components registry.
"""

CORE_REGISTRY = {
    # Core configuration
    "DjangoConfig": ("django_cfg.core.config", "DjangoConfig"),
    "StartupInfoMode": ("django_cfg.core.config", "StartupInfoMode"),

    # Core exceptions
    "ConfigurationError": ("django_cfg.core.exceptions", "ConfigurationError"),
    "ValidationError": ("django_cfg.core.exceptions", "ValidationError"),
    "DatabaseError": ("django_cfg.core.exceptions", "DatabaseError"),
    "CacheError": ("django_cfg.core.exceptions", "CacheError"),
    "EnvironmentError": ("django_cfg.core.exceptions", "EnvironmentError"),

    # Core integration
    "DjangoIntegration": ("django_cfg.core.integration", "DjangoIntegration"),

    # Database models
    "DatabaseConfig": ("django_cfg.models.infrastructure.database", "DatabaseConfig"),

    # Cache models
    "CacheConfig": ("django_cfg.models.infrastructure.cache", "CacheConfig"),

    # Security models
    "SecurityConfig": ("django_cfg.models.infrastructure.security", "SecurityConfig"),

    # Logging models
    "LoggingConfig": ("django_cfg.models.infrastructure.logging", "LoggingConfig"),

    # Environment models
    "EnvironmentConfig": ("django_cfg.models.django.environment", "EnvironmentConfig"),

    # Security - Django-Axes
    "AxesConfig": ("django_cfg.models.django.axes", "AxesConfig"),

    # Security - Django Crypto Fields
    "CryptoFieldsConfig": ("django_cfg.models.django.crypto_fields", "CryptoFieldsConfig"),

    # Limits models
    "LimitsConfig": ("django_cfg.models.api.limits", "LimitsConfig"),

    # API Keys models
    "ApiKeys": ("django_cfg.models.api.keys", "ApiKeys"),

    # JWT models
    "JWTConfig": ("django_cfg.models.api.jwt", "JWTConfig"),

    # OAuth models
    "GitHubOAuthConfig": ("django_cfg.models.api.oauth", "GitHubOAuthConfig"),
    "OAuthConfig": ("django_cfg.models.api.oauth", "OAuthConfig"),

    # Two-Factor Authentication
    "TwoFactorConfig": ("django_cfg.models.api.twofactor", "TwoFactorConfig"),

    # Django-RQ models
    "DjangoRQConfig": ("django_cfg.models.django.django_rq", "DjangoRQConfig"),
    "RQQueueConfig": ("django_cfg.models.django.django_rq", "RQQueueConfig"),
    "RQScheduleConfig": ("django_cfg.models.django.django_rq", "RQScheduleConfig"),

    # Payment system models (BaseCfgAutoModule)
    "PaymentsConfig": ("django_cfg.models.payments.config", "PaymentsConfig"),
    "NowPaymentsConfig": ("django_cfg.models.payments.config", "NowPaymentsConfig"),

    # Pagination classes
    "DefaultPagination": ("django_cfg.middleware.pagination", "DefaultPagination"),
    "LargePagination": ("django_cfg.middleware.pagination", "LargePagination"),
    "SmallPagination": ("django_cfg.middleware.pagination", "SmallPagination"),
    "NoPagination": ("django_cfg.middleware.pagination", "NoPagination"),
    "CursorPaginationEnhanced": ("django_cfg.middleware.pagination", "CursorPaginationEnhanced"),

    # Utils
    "version_check": ("django_cfg.utils.version_check", "version_check"),
    "get_ticket_url": ("django_cfg.core.utils.url_helpers", "get_ticket_url"),
    "get_otp_url": ("django_cfg.core.utils.url_helpers", "get_otp_url"),

    # Routing
    "DynamicRouter": ("django_cfg.routing.routers", "DynamicRouter"),
    "health_callback": ("django_cfg.routing.callbacks", "health_callback"),

    # Testing
    "SmartTestRunner": ("django_cfg.testing.runners", "SmartTestRunner"),
    "FastTestRunner": ("django_cfg.testing.runners", "FastTestRunner"),

    # Health module
    "HealthService": ("django_cfg.modules.django_health", "HealthService"),

    # Library configuration
    "LIB_NAME": ("django_cfg.config", "LIB_NAME"),
    "LIB_SITE_URL": ("django_cfg.config", "LIB_SITE_URL"),
    "LIB_HEALTH_URL": ("django_cfg.config", "LIB_HEALTH_URL"),
    "get_default_dropdown_items": ("django_cfg.config", "get_default_dropdown_items"),
}
