"""
Configuration utility functions.

Helper functions for working with payment configurations.
"""

from typing import Optional
from django_cfg.modules.django_logger import get_logger

from .module import PaymentsCfgModule
from .settings import PaymentsSettings
from django_cfg.models.payments import PaymentProviderConfig

logger = get_logger("config_utils")

# Global payments configuration instance
_payments_config = PaymentsCfgModule()


def get_payments_config() -> PaymentsSettings:
    """Get current payments configuration."""
    return _payments_config.get_config()


def get_provider_config(provider_name: str) -> Optional[PaymentProviderConfig]:
    """Get configuration for specific payment provider."""
    config = get_payments_config()
    return config.providers.get(provider_name)


def is_payments_enabled() -> bool:
    """Check if payments module is enabled."""
    try:
        config = get_payments_config()
        return config.enabled
    except Exception as e:
        logger.warning(f"Failed to check payments status: {e}")
        return False


def reset_config_cache():
    """Reset configuration cache."""
    global _payments_config
    _payments_config.reset_cache()


__all__ = [
    'get_payments_config',
    'get_provider_config', 
    'is_payments_enabled',
    'reset_config_cache'
]