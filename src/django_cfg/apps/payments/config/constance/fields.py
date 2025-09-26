"""
Constance fields configuration for Payments app.

This module defines ONLY dynamic settings that need to be changed at runtime.
Static configuration is handled by PaymentsConfig Pydantic model.

Note: This file MUST NOT import Django models or anything that requires
Django apps to be loaded, as it's imported during settings generation.
"""

from typing import List
from django_cfg.models.constance import ConstanceField


def get_django_cfg_payments_constance_fields() -> List[ConstanceField]:
    """
    Get Constance field definitions for Payments app.
    
    Only includes settings that need runtime configuration:
    - API keys and secrets (change per environment)
    - Rate limits (admins need to adjust)
    - Usage tracking preferences
    - Currency update intervals
    
    Static settings (enabled flags, middleware, cache timeouts) are handled
    by PaymentsConfig Pydantic model and auto-detection.
    
    Returns:
        List of ConstanceField objects for runtime-configurable settings
    """
    # Import PaymentsConfigManager for consistent config access
    from ..django_cfg_integration import PaymentsConfigManager
    
    # Get default values from initialized Pydantic config using PaymentsConfigManager
    default_config = PaymentsConfigManager.get_payments_config()
    
    return [
        # === 📊 Usage Tracking ===
        ConstanceField(
            name='PAYMENTS_TRACK_ANONYMOUS_USAGE',
            default=default_config.track_anonymous_usage,
            help_text="📊 Usage Tracking: Track usage for anonymous users (privacy setting)",
            field_type='bool',
            group='Payments'
        ),
        
        # === 🔌 NowPayments Provider ===
        ConstanceField(
            name='PAYMENTS_NOWPAYMENTS_API_KEY',
            default='',
            help_text="🔌 NowPayments: API key for production (sensitive)",
            field_type='str',
            group='Payments'
        ),
        ConstanceField(
            name='PAYMENTS_NOWPAYMENTS_IPN_SECRET',
            default='',
            help_text="🔌 NowPayments: IPN secret for webhook verification (sensitive)",
            field_type='str',
            group='Payments'
        ),
        ConstanceField(
            name='PAYMENTS_NOWPAYMENTS_SANDBOX_MODE',
            default=True,
            help_text="🔌 NowPayments: Use sandbox mode for testing",
            field_type='bool',
            group='Payments'
        ),
    ]