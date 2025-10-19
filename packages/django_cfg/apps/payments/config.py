"""
Simplified configuration integration for Payments v2.0.

Uses django_cfg.core for centralized configuration access.
"""

import logging
from typing import Optional

from django_cfg.core.state import get_current_config
from django_cfg.models.payments import NowPaymentsConfig, PaymentsConfig

logger = logging.getLogger(__name__)


def get_payments_config() -> Optional[PaymentsConfig]:
    """
    Get payments configuration from django_cfg.

    Returns:
        PaymentsConfig instance from current django_cfg config, or None if not found
    """
    try:
        current_config = get_current_config()
        if current_config and hasattr(current_config, 'payments'):
            return current_config.payments
        else:
            logger.warning("PaymentsConfig not found in current django_cfg config")
            return None
    except Exception as e:
        logger.error(f"Failed to get payments config: {e}")
        return None


def get_nowpayments_config() -> Optional[NowPaymentsConfig]:
    """
    Get NowPayments configuration (simplified for v2.0).

    Returns:
        NowPaymentsConfig instance ready for provider initialization, or None if unavailable
    """
    try:
        payments_config = get_payments_config()
        if not payments_config:
            logger.error("Payments configuration not found in django_cfg")
            return None

        # Get NowPayments config directly
        nowpayments = payments_config.nowpayments

        # Check if enabled and configured
        if not nowpayments.enabled:
            logger.warning("NowPayments provider is disabled in configuration")
            return None

        if not nowpayments.is_configured:
            logger.error("NowPayments API key not configured")
            return None

        return nowpayments

    except Exception as e:
        logger.exception(f"Failed to get NowPayments config: {e}")
        return None


def is_payments_enabled() -> bool:
    """
    Check if payments module is enabled.

    Returns:
        True if payments is enabled in django_cfg config
    """
    try:
        payments_config = get_payments_config()
        if not payments_config:
            return False
        return payments_config.enabled
    except Exception:
        logger.warning("Failed to check payments enabled status, defaulting to False")
        return False


def is_nowpayments_enabled() -> bool:
    """
    Check if NowPayments provider is enabled.

    Returns:
        True if NowPayments is enabled and configured
    """
    try:
        nowpayments_config = get_nowpayments_config()
        return nowpayments_config is not None
    except Exception:
        logger.warning("Failed to check NowPayments enabled status, defaulting to False")
        return False


__all__ = [
    'get_payments_config',
    'get_nowpayments_config',
    'is_payments_enabled',
    'is_nowpayments_enabled',
]
