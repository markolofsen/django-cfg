"""
Django-CFG Template Tags — backward-compatibility shim.

All tags are implemented in:
  - django_cfg_lib       → lib metadata, env, frontend detection
  - django_cfg_auth      → JWT tokens, user permissions
  - django_cfg_dashboard → custom admin dashboard tabs

This file re-exports all of them so existing {% load django_cfg %} keeps working.
New templates should {% load django_cfg_lib %} / {% load django_cfg_auth %} etc. directly.
"""

import socket
from django import template
from django.conf import settings
from django.utils.safestring import mark_safe

register = template.Library()

# ---------------------------------------------------------------------------
# Internals (shared)
# ---------------------------------------------------------------------------

def _is_port_available(host: str, port: int, timeout: float = 0.1, retries: int = 3, retry_delay: float = 0.05) -> bool:
    import time
    for attempt in range(retries):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            result = sock.connect_ex((host, port))
            sock.close()
            if result == 0:
                return True
            if attempt < retries - 1:
                time.sleep(retry_delay)
        except Exception:
            if attempt < retries - 1:
                time.sleep(retry_delay)
            continue
    return False


def _get_jwt_refresh(user):
    from rest_framework_simplejwt.tokens import RefreshToken
    return RefreshToken.for_user(user)


def _authenticated_user(context):
    from django.contrib.auth.models import AnonymousUser
    request = context.get('request')
    if not request:
        return None
    user = getattr(request, 'user', None)
    if not user or isinstance(user, AnonymousUser) or not user.is_authenticated:
        return None
    return user


# ---------------------------------------------------------------------------
# Lib tags
# ---------------------------------------------------------------------------

@register.simple_tag
def lib_name():
    from django_cfg import __version__
    from django_cfg.config import LIB_NAME
    return f"{LIB_NAME} ({__version__})"


@register.simple_tag
def lib_site_url():
    from django_cfg.config import LIB_SITE_URL
    return LIB_SITE_URL


@register.simple_tag
def lib_docs_url():
    from django_cfg.config import LIB_SITE_URL
    return LIB_SITE_URL


@register.simple_tag
def lib_health_url():
    from django_cfg.config import LIB_HEALTH_URL
    return LIB_HEALTH_URL


@register.simple_tag
def lib_subtitle():
    return "The AI-First Django Framework That Thinks For You"


@register.simple_tag
def version_update_info():
    try:
        from django_cfg.core.integration.version_checker import get_version_info
        return get_version_info()
    except Exception:
        return {'current_version': None, 'latest_version': None, 'update_available': False, 'update_url': None}


@register.simple_tag
def project_name():
    from django_cfg.config import LIB_NAME
    from django_cfg.core.state import get_current_config
    config = get_current_config()
    if config and hasattr(config, 'project_name'):
        return config.project_name
    return LIB_NAME


@register.simple_tag
def is_dev():
    try:
        from django_cfg.core.config import get_current_config
        config = get_current_config()
        return config and config.is_development
    except Exception:
        return False


@register.simple_tag
def is_frontend_dev_mode():
    if not settings.DEBUG:
        return False
    return _is_port_available('localhost', 3000) or _is_port_available('localhost', 3777)


@register.simple_tag
def nextjs_admin_url(path=''):
    path = path.strip('/')
    if not settings.DEBUG:
        return f'/cfg/admin/admin/{path}' if path else '/cfg/admin/admin/'
    if _is_port_available('localhost', 3777):
        base_url = 'http://localhost:3777/admin'
        return f'{base_url}/{path}' if path else base_url
    return f'/cfg/admin/admin/{path}' if path else '/cfg/admin/admin/'


@register.simple_tag
def has_nextjs_external_admin():
    return False


@register.simple_tag
def nextjs_external_admin_url(route=''):
    return ''


@register.simple_tag
def nextjs_external_admin_title():
    return ''


# ---------------------------------------------------------------------------
# Auth / JWT tags
# ---------------------------------------------------------------------------

@register.simple_tag(takes_context=True)
def user_jwt_token(context):
    user = _authenticated_user(context)
    if not user:
        return ''
    return str(_get_jwt_refresh(user).access_token)


@register.simple_tag(takes_context=True)
def user_jwt_refresh_token(context):
    user = _authenticated_user(context)
    if not user:
        return ''
    return str(_get_jwt_refresh(user))


@register.simple_tag(takes_context=True)
def inject_jwt_tokens_script(context):
    user = _authenticated_user(context)
    if not user:
        return ''
    refresh = _get_jwt_refresh(user)
    access = str(refresh.access_token)
    ref = str(refresh)
    return mark_safe(f"""<script>
(function() {{
    try {{
        localStorage.setItem('auth_token', '{access}');
        localStorage.setItem('refresh_token', '{ref}');
    }} catch (e) {{
        console.error('Failed to inject JWT tokens:', e);
    }}
}})();
</script>""")


@register.simple_tag(takes_context=True)
def generate_jwt_tokens(context):
    user = _authenticated_user(context)
    if not user:
        return {'access': '', 'refresh': ''}
    try:
        refresh = _get_jwt_refresh(user)
        return {'access': str(refresh.access_token), 'refresh': str(refresh)}
    except Exception:
        return {'access': '', 'refresh': ''}


@register.simple_tag(takes_context=True)
def can_view_admin_dashboard(context):
    from django.contrib.auth.models import AnonymousUser
    request = context.get('request')
    if not request:
        return False
    user = getattr(request, 'user', None)
    if not user or isinstance(user, AnonymousUser) or not user.is_authenticated:
        return False
    return user.is_superuser


# ---------------------------------------------------------------------------
# Dashboard tags
# ---------------------------------------------------------------------------

@register.simple_tag(takes_context=True)
def get_dashboard_config(context):
    try:
        from django_cfg.core.config import get_current_config
        config = get_current_config()
        if not config:
            return None
        dashboard = getattr(config, 'dashboard', None)
        if not dashboard or not dashboard.tabs:
            return None
        request = context.get('request')
        if not request or not getattr(request.user, 'is_staff', False):
            return None
        return dashboard
    except Exception:
        return None


@register.simple_tag(takes_context=True)
def has_mcp_chat(context):
    """True if MCP module is configured AND current user can see the chat."""
    try:
        from django_cfg.core.config import get_current_config
        config = get_current_config()
        if not config:
            return False
        if not getattr(config, 'mcp', None):
            return False
        request = context.get('request')
        if not request:
            return False
        return bool(getattr(request.user, 'is_superuser', False))
    except Exception:
        return False
