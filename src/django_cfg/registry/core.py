"""
Core Django-CFG components registry.
"""

CORE_REGISTRY = {
    # Core configuration
    "DjangoConfig": ("django_cfg.core.config", "DjangoConfig"),
    
    # Core exceptions
    "ConfigurationError": ("django_cfg.core.exceptions", "ConfigurationError"),
    "ValidationError": ("django_cfg.core.exceptions", "ValidationError"),
    "DatabaseError": ("django_cfg.core.exceptions", "DatabaseError"),
    "CacheError": ("django_cfg.core.exceptions", "CacheError"),
    "EnvironmentError": ("django_cfg.core.exceptions", "EnvironmentError"),
    
    # Core integration
    "DjangoIntegration": ("django_cfg.core.integration", "DjangoIntegration"),
    
    # Database models
    "DatabaseConfig": ("django_cfg.models.database", "DatabaseConfig"),
    
    # Cache models  
    "CacheConfig": ("django_cfg.models.cache", "CacheConfig"),
    
    # Security models
    "SecuritySettings": ("django_cfg.models.security", "SecuritySettings"),
    
    # Logging models
    "LoggingConfig": ("django_cfg.models.logging", "LoggingConfig"),
    
    # Environment models
    "EnvironmentConfig": ("django_cfg.models.environment", "EnvironmentConfig"),
    
    # Limits models
    "LimitsConfig": ("django_cfg.models.limits", "LimitsConfig"),
    
    # JWT models
    "JWTConfig": ("django_cfg.models.jwt", "JWTConfig"),
    
    # Task and queue models
    "TaskConfig": ("django_cfg.models.tasks", "TaskConfig"),
    "DramatiqConfig": ("django_cfg.models.tasks", "DramatiqConfig"),
    
    # Payment system models
    "PaymentsConfig": ("django_cfg.models.payments", "PaymentsConfig"),
    "PaymentProviderConfig": ("django_cfg.models.payments", "PaymentProviderConfig"),
    "NowPaymentsConfig": ("django_cfg.models.payments", "NowPaymentsConfig"),
    "CryptAPIConfig": ("django_cfg.models.payments", "CryptAPIConfig"),
    "StripeConfig": ("django_cfg.models.payments", "StripeConfig"),
    "create_nowpayments_config": ("django_cfg.models.payments", "create_nowpayments_config"),
    "create_cryptapi_config": ("django_cfg.models.payments", "create_cryptapi_config"),
    "create_stripe_config": ("django_cfg.models.payments", "create_stripe_config"),
    "create_cryptomus_config": ("django_cfg.models.payments", "create_cryptomus_config"),
    
    # Pagination classes
    "DefaultPagination": ("django_cfg.middleware.pagination", "DefaultPagination"),
    "LargePagination": ("django_cfg.middleware.pagination", "LargePagination"),
    "SmallPagination": ("django_cfg.middleware.pagination", "SmallPagination"),
    "NoPagination": ("django_cfg.middleware.pagination", "NoPagination"),
    "CursorPaginationEnhanced": ("django_cfg.middleware.pagination", "CursorPaginationEnhanced"),
    
    # Utils
    "version_check": ("django_cfg.utils.version_check", "version_check"),
    "toolkit": ("django_cfg.utils.toolkit", "toolkit"),
    "ConfigToolkit": ("django_cfg.utils.toolkit", "ConfigToolkit"),
    
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
