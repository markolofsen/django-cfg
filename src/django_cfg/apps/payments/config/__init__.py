"""
Configuration module for the Universal Payment System v2.0.

Provides clean separation between:
- django-cfg integration (static config)
- Constance integration (dynamic config)
- Configuration utilities and helpers
"""

# Django-cfg integration
from .django_cfg_integration import (
    PaymentsConfigMixin,
    get_payments_config,
    is_payments_enabled,
)

# Constance integration (safe - no Django models)
from .constance import (
    get_django_cfg_payments_constance_fields,
    PaymentConstanceSettings,
)

# Configuration helpers
from .helpers import (
    MiddlewareConfigHelper,
    CacheConfigHelper,
)

__all__ = [
    # Django-cfg integration
    'PaymentsConfigMixin',
    'get_payments_config',
    'is_payments_enabled',
    
    # Constance integration
    'get_django_cfg_payments_constance_fields',
    'PaymentConstanceSettings',
    
    # Configuration helpers
    'MiddlewareConfigHelper',
    'CacheConfigHelper',
]
