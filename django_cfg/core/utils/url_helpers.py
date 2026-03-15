"""
URL generation utilities for django-cfg.

Provides helper functions to generate URLs dynamically from site_url configuration.
"""

import logging
from typing import Optional

logger = logging.getLogger(__name__)


def get_ticket_url(ticket_uuid: str, fallback: str = "#ticket") -> str:
    """
    Generate support ticket URL on the fly from site_url.

    Args:
        ticket_uuid: UUID of the support ticket
        fallback: Fallback URL if config is not available (default: "#ticket")

    Returns:
        Complete URL to the ticket

    Example:
        >>> get_ticket_url("abc-123-def")
        "https://yoursite.com/support/ticket/abc-123-def"
    """
    try:
        from django_cfg.core.state import get_current_config
        config = get_current_config()

        if config and hasattr(config, 'site_url'):
            return f"{config.site_url}/support/ticket/{ticket_uuid}"
        else:
            logger.warning("Config or site_url not available for ticket URL generation")
            return f"{fallback}-{ticket_uuid}"

    except Exception as e:
        logger.warning(f"Could not generate ticket URL: {e}")
        return f"{fallback}-{ticket_uuid}"


def get_otp_url(otp_code: str, fallback: str = "#otp") -> str:
    """
    Generate OTP verification URL on the fly from site_url.

    Args:
        otp_code: OTP verification code
        fallback: Fallback URL if config is not available (default: "#otp")

    Returns:
        Complete URL to the OTP verification page

    Example:
        >>> get_otp_url("123456")
        "https://yoursite.com/auth/?otp=123456"
    """
    try:
        from django_cfg.core.state import get_current_config
        config = get_current_config()

        if config and hasattr(config, 'site_url'):
            return f"{config.site_url}/auth/?otp={otp_code}"
        else:
            logger.warning("Config or site_url not available for OTP URL generation")
            return f"{fallback}-{otp_code}"

    except Exception as e:
        logger.warning(f"Could not generate OTP URL: {e}")
        return f"{fallback}-{otp_code}"


__all__ = ["get_ticket_url", "get_otp_url"]
