"""
Optimized Signals for the Universal Payment System v2.0.

Minimal signals that only handle:
- Cache invalidation
- Event notifications
- Audit logging

All business logic is in managers to avoid duplication.
"""

from django.apps import apps
from django_cfg.modules.django_logger import get_logger

logger = get_logger("payment_signals")


def register_signals():
    """
    Register all payment system signals.
    
    Called from apps.py when Django starts.
    """
    try:
        # Import signal modules to register them
        from . import payment_signals
        from . import balance_signals
        from . import subscription_signals
        from . import api_key_signals
        
        logger.info("Payment signals registered successfully")
        
    except ImportError as e:
        logger.error(f"Failed to register payment signals: {e}")


# Auto-register signals when module is imported
register_signals()
