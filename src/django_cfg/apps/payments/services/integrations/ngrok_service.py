"""
Ngrok utilities for webhook development.

Simple helper functions using django_ngrok module.
"""

from typing import Dict
from .providers_config import get_supported_providers


def get_webhook_url_for_provider(provider: str) -> str:
    """
    Get webhook URL for specific provider.
    
    Uses django_ngrok if available, otherwise localhost fallback.
    """
    try:
        from django_cfg.modules.django_ngrok import get_webhook_url
        return get_webhook_url(f"{provider}/")
    except ImportError:
        return f"http://localhost:8000/api/webhooks/{provider}/"


def get_all_webhook_urls() -> Dict[str, str]:
    """Get webhook URLs for all supported providers."""
    return {
        provider: get_webhook_url_for_provider(provider)
        for provider in get_supported_providers()
    }


def get_api_base_url() -> str:
    """Get API base URL (ngrok tunnel or localhost)."""
    try:
        from django_cfg.modules.django_ngrok import get_api_url
        return get_api_url()
    except ImportError:
        return "http://localhost:8000"


def is_ngrok_available() -> bool:
    """Check if ngrok tunnel is actually active."""
    try:
        from django_cfg.modules.django_ngrok import is_tunnel_active
        return is_tunnel_active()
    except ImportError:
        return False
