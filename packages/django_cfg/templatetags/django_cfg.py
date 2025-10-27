"""
Django-CFG Template Tags

Provides template tags for accessing django-cfg configuration constants.
"""

import os
from django import template
from django.utils.safestring import mark_safe
from rest_framework_simplejwt.tokens import RefreshToken

register = template.Library()


@register.simple_tag
def lib_name():
    """Get the library name."""
    # Lazy import to avoid AppRegistryNotReady error
    from django_cfg import __version__
    from django_cfg.config import LIB_NAME
    return f"{LIB_NAME} ({__version__})"


@register.simple_tag
def lib_site_url():
    """Get the library site URL."""
    # Lazy import to avoid AppRegistryNotReady error
    from django_cfg.config import LIB_SITE_URL
    return LIB_SITE_URL


@register.simple_tag
def lib_health_url():
    """Get the library health URL."""
    # Lazy import to avoid AppRegistryNotReady error
    from django_cfg.config import LIB_HEALTH_URL
    return LIB_HEALTH_URL


@register.simple_tag
def lib_subtitle():
    """Get the library subtitle/tagline."""
    return "The AI-First Django Framework That Thinks For You"


@register.simple_tag
def project_name():
    """Get the project name from current config."""
    # Lazy import to avoid AppRegistryNotReady error
    from django_cfg.config import LIB_NAME
    from django_cfg.core.state import get_current_config

    # Try to get project name from current config
    config = get_current_config()
    if config and hasattr(config, 'project_name'):
        return config.project_name

    # Fallback to library name
    return LIB_NAME


@register.simple_tag(takes_context=True)
def user_jwt_token(context):
    """
    Generate JWT access token for the current authenticated user.

    Returns JWT token that can be used for API authentication.
    Uses Authorization: Bearer <token> header.

    Usage in template:
        {% load django_cfg %}
        <script>
            window.USER_JWT_TOKEN = '{% user_jwt_token %}';
        </script>
    """
    request = context.get('request')
    if not request or not request.user or not request.user.is_authenticated:
        return ''

    refresh = RefreshToken.for_user(request.user)
    return str(refresh.access_token)


@register.simple_tag(takes_context=True)
def user_jwt_refresh_token(context):
    """
    Generate JWT refresh token for the current authenticated user.

    Returns JWT refresh token that can be used to obtain new access tokens.

    Usage in template:
        {% load django_cfg %}
        <script>
            window.USER_JWT_REFRESH_TOKEN = '{% user_jwt_refresh_token %}';
        </script>
    """
    request = context.get('request')
    if not request or not request.user or not request.user.is_authenticated:
        return ''

    refresh = RefreshToken.for_user(request.user)
    return str(refresh)


@register.simple_tag(takes_context=True)
def inject_jwt_tokens_script(context):
    """
    Generate complete script tag that injects JWT tokens into localStorage.

    Automatically stores auth_token and refresh_token in localStorage
    for the current authenticated user.

    Usage in template (usually in <head> or before </body>):
        {% load django_cfg %}
        {% inject_jwt_tokens_script %}
    """
    request = context.get('request')
    if not request or not request.user or not request.user.is_authenticated:
        return ''

    refresh = RefreshToken.for_user(request.user)
    access_token = str(refresh.access_token)
    refresh_token = str(refresh)

    script = f"""<script>
(function() {{
    try {{
        // Store JWT tokens in localStorage for Next.js app
        localStorage.setItem('auth_token', '{access_token}');
        localStorage.setItem('refresh_token', '{refresh_token}');
        console.log('JWT tokens injected successfully');
    }} catch (e) {{
        console.error('Failed to inject JWT tokens:', e);
    }}
}})();
</script>"""
    return mark_safe(script)


@register.simple_tag
def nextjs_admin_url(path=''):
    """
    Get the URL for Next.js Admin Panel.

    In development mode (when DJANGO_CFG_FRONTEND_DEV_MODE=true):
        Returns http://localhost:3000/{path}

    In production mode:
        Returns /cfg/admin/{path}

    Usage in template:
        {% load django_cfg %}
        <iframe src="{% nextjs_admin_url 'private' %}"></iframe>

    Environment variable:
        DJANGO_CFG_FRONTEND_DEV_MODE=true    # Enable dev mode
        DJANGO_CFG_FRONTEND_DEV_PORT=3000    # Custom dev port (default: 3000)
    """
    # Check if frontend dev mode is enabled
    is_dev_mode = os.environ.get('DJANGO_CFG_FRONTEND_DEV_MODE', '').lower() in ('true', '1', 'yes')

    # Normalize path - ensure trailing slash for Django static view
    if path and not path.endswith('/'):
        path = f'{path}/'

    if is_dev_mode:
        # Development mode: use Next.js dev server
        dev_port = os.environ.get('DJANGO_CFG_FRONTEND_DEV_PORT', '3000')
        base_url = f'http://localhost:{dev_port}'
        return f'{base_url}/{path}' if path else base_url
    else:
        # Production mode: use Django static files
        return f'/cfg/admin/{path}' if path else '/cfg/admin/'


@register.simple_tag
def is_frontend_dev_mode():
    """
    Check if frontend is in development mode.

    Returns True if DJANGO_CFG_FRONTEND_DEV_MODE environment variable is set to true.

    Usage in template:
        {% load django_cfg %}
        {% if is_frontend_dev_mode %}
            <div class="dev-badge">Dev Mode</div>
        {% endif %}
    """
    return os.environ.get('DJANGO_CFG_FRONTEND_DEV_MODE', '').lower() in ('true', '1', 'yes')
