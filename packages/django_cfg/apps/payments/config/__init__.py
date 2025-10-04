"""
Configuration module for the Universal Payment System v2.0.

Provides unified configuration through BaseCfgAutoModule:
- django-cfg integration (all configuration)
- Configuration utilities and helpers
"""

# Django-cfg integration (BaseCfgAutoModule)
from .django_cfg_integration import (
    PaymentsConfigManager,
    PaymentsConfigMixin,
    get_payments_config,
    is_payments_enabled,
    is_payments_configured,
    get_config_summary,
    reset_payments_config_cache,
)

# Configuration helpers
from .helpers import (
    MiddlewareConfigHelper,
    CacheConfigHelper,
    RedisConfigHelper,
)

__all__ = [
    # Django-cfg integration (BaseCfgAutoModule)
    'PaymentsConfigManager',
    'PaymentsConfigMixin',
    'get_payments_config',
    'is_payments_enabled',
    'is_payments_configured',
    'get_config_summary',
    'reset_payments_config_cache',
    
    # Configuration helpers
    'MiddlewareConfigHelper',
    'CacheConfigHelper',
    'RedisConfigHelper',
]
