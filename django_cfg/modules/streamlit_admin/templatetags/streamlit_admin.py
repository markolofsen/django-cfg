"""
Template tags for Streamlit Admin integration.

Usage:
    {% load streamlit_admin %}

    {% has_streamlit_admin as is_enabled %}
    {% streamlit_admin_url %}
    {% streamlit_admin_tab_title %}
"""

from django import template

register = template.Library()


def _get_streamlit_config():
    """Get Streamlit admin configuration."""
    try:
        from django_cfg.core.config import get_current_config
        config = get_current_config()
        return config.streamlit_admin if config else None
    except Exception:
        return None


@register.simple_tag
def has_streamlit_admin() -> bool:
    """Check if Streamlit admin is configured."""
    return _get_streamlit_config() is not None


@register.simple_tag
def streamlit_admin_url(route: str = "") -> str:
    """
    Get Streamlit admin URL (uses runtime URL if available).

    Args:
        route: Optional route to append

    Returns:
        Full URL to Streamlit admin
    """
    config = _get_streamlit_config()
    if not config:
        return ""

    # Use runtime URL (handles auto-assigned ports)
    base_url = config.get_runtime_url()
    if route:
        if not route.startswith("/"):
            route = f"/{route}"
        return f"{base_url}{route}"
    return base_url


@register.simple_tag
def streamlit_admin_tab_title() -> str:
    """Get tab title for Streamlit admin."""
    config = _get_streamlit_config()
    if not config:
        return "Streamlit Admin"
    return config.get_tab_title()


@register.simple_tag
def streamlit_admin_iframe_url() -> str:
    """Get iframe URL for embedding (uses runtime URL if available)."""
    config = _get_streamlit_config()
    if not config:
        return ""

    # Use runtime URL for iframe
    route = config.get_iframe_route()
    if not route.startswith("/"):
        route = f"/{route}"
    return f"{config.get_runtime_url()}{route}"


@register.simple_tag
def streamlit_admin_iframe_sandbox() -> str:
    """Get iframe sandbox attributes."""
    config = _get_streamlit_config()
    if not config:
        return ""
    return config.get_iframe_sandbox()


@register.simple_tag
def streamlit_admin_is_configured() -> bool:
    """Check if Streamlit admin is properly configured."""
    config = _get_streamlit_config()
    return config is not None


@register.simple_tag
def streamlit_admin_port() -> int:
    """Get Streamlit server port (uses runtime port if available)."""
    config = _get_streamlit_config()
    if not config:
        return 8501
    return config.get_runtime_port()


@register.simple_tag(takes_context=True)
def streamlit_admin_iframe_url_with_token(context) -> str:
    """
    Get iframe URL with JWT token for authenticated users.

    Automatically injects JWT token as query parameter for authentication.
    This is needed when iframe loads Streamlit directly (not via proxy).

    Usage:
        {% load streamlit_admin %}
        <iframe src="{% streamlit_admin_iframe_url_with_token %}"></iframe>
    """
    config = _get_streamlit_config()
    if not config:
        return ""

    # Get base iframe URL
    route = config.get_iframe_route()
    if not route.startswith("/"):
        route = f"/{route}"
    base_url = f"{config.get_runtime_url()}{route}"

    # Inject JWT token for authenticated users
    request = context.get('request')
    if request and hasattr(request, 'user') and request.user.is_authenticated:
        try:
            from rest_framework_simplejwt.tokens import RefreshToken
            refresh = RefreshToken.for_user(request.user)
            token = str(refresh.access_token)
            separator = "&" if "?" in base_url else "?"
            return f"{base_url}{separator}token={token}"
        except Exception:
            pass

    return base_url


@register.inclusion_tag("streamlit_admin/iframe.html", takes_context=True)
def streamlit_admin_iframe(context, height: str = "800px", width: str = "100%"):
    """
    Render Streamlit admin iframe with JWT token injection.

    Args:
        height: iframe height (default: 800px)
        width: iframe width (default: 100%)
    """
    config = _get_streamlit_config()
    if not config:
        return {
            "enabled": False,
            "url": "",
            "sandbox": "",
            "height": height,
            "width": width,
            "title": "Streamlit Admin",
        }

    # Get URL with token
    url = streamlit_admin_iframe_url_with_token(context)

    return {
        "enabled": True,
        "url": url,
        "sandbox": config.get_iframe_sandbox(),
        "height": height,
        "width": width,
        "title": config.get_tab_title(),
    }
