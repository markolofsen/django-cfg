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

    # Limits models
    "LimitsConfig": ("django_cfg.models.api.limits", "LimitsConfig"),

    # API Keys models
    "ApiKeys": ("django_cfg.models.api.keys", "ApiKeys"),

    # JWT models
    "JWTConfig": ("django_cfg.models.api.jwt", "JWTConfig"),
    
    # Task and queue models
    "TaskConfig": ("django_cfg.models.tasks.config", "TaskConfig"),
    "DramatiqConfig": ("django_cfg.models.tasks.config", "DramatiqConfig"),

    # Payment system models (BaseCfgAutoModule)
    "PaymentsConfig": ("django_cfg.models.payments.config", "PaymentsConfig"),
    "ProviderAPIKeysConfig": ("django_cfg.models.payments.api_keys", "ProviderAPIKeysConfig"),
    "BaseProviderConfig": ("django_cfg.models.payments.providers", "BaseProviderConfig"),
    "NowPaymentsProviderConfig": ("django_cfg.models.payments.providers", "NowPaymentsProviderConfig"),
    
    # Pagination classes
    "DefaultPagination": ("django_cfg.middleware.pagination", "DefaultPagination"),
    "LargePagination": ("django_cfg.middleware.pagination", "LargePagination"),
    "SmallPagination": ("django_cfg.middleware.pagination", "SmallPagination"),
    "NoPagination": ("django_cfg.middleware.pagination", "NoPagination"),
    "CursorPaginationEnhanced": ("django_cfg.middleware.pagination", "CursorPaginationEnhanced"),
    
    # Utils
    "version_check": ("django_cfg.utils.version_check", "version_check"),

    # Routing
    "DynamicRouter": ("django_cfg.routing.routers", "DynamicRouter"),
    "health_callback": ("django_cfg.routing.callbacks", "health_callback"),
    
    # Health module
    "HealthService": ("django_cfg.modules.django_health", "HealthService"),
    
    # Library configuration
    "LIB_NAME": ("django_cfg.config", "LIB_NAME"),
    "LIB_SITE_URL": ("django_cfg.config", "LIB_SITE_URL"),
    "LIB_HEALTH_URL": ("django_cfg.config", "LIB_HEALTH_URL"),
    "get_default_dropdown_items": ("django_cfg.config", "get_default_dropdown_items"),
}
