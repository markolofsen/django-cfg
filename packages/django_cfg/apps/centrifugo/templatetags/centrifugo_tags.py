"""
Centrifugo Template Tags.

Provides template tags for accessing Centrifugo configuration in templates.
"""

from django import template
from ..services import get_centrifugo_config

register = template.Library()


@register.simple_tag
def centrifugo_admin_url():
    """
    Get Centrifugo admin UI URL from configuration.

    Returns the HTTP admin URL from centrifugo_api_url.
    Example: http://localhost:8002

    Usage in template:
        {% load centrifugo_tags %}
        {% centrifugo_admin_url %}
    """
    config = get_centrifugo_config()
    if not config or not config.centrifugo_api_url:
        return ""

    # Return HTTP API URL (admin UI is on same host)
    url = config.centrifugo_api_url

    # Remove /api suffix if present
    if url.endswith('/api'):
        url = url[:-len('/api')]

    # Remove trailing slash
    url = url.rstrip('/')

    return url


@register.simple_tag
def centrifugo_is_configured():
    """
    Check if Centrifugo is configured.
    
    Returns True if Centrifugo config exists and has URL.
    
    Usage in template:
        {% load centrifugo_tags %}
        {% centrifugo_is_configured as is_configured %}
        {% if is_configured %}...{% endif %}
    """
    config = get_centrifugo_config()
    return bool(config and config.centrifugo_url)


@register.simple_tag
def centrifugo_wrapper_url():
    """
    Get Centrifugo wrapper URL from configuration.
    
    Returns the wrapper URL (our Django proxy).
    Example: http://localhost:8080
    
    Usage in template:
        {% load centrifugo_tags %}
        {% centrifugo_wrapper_url %}
    """
    config = get_centrifugo_config()
    if not config or not config.wrapper_url:
        return ""
    
    return config.wrapper_url.rstrip('/')


__all__ = [
    "centrifugo_admin_url",
    "centrifugo_is_configured",
    "centrifugo_wrapper_url",
]
