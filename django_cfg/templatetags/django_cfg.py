"""
Django-CFG template tags: lib metadata, environment,
JWT tokens, admin dashboard tabs. Load with ``{% load django_cfg %}``.
"""

from django import template
from django.utils.safestring import mark_safe

register = template.Library()

# ---------------------------------------------------------------------------
# Internals (shared)
# ---------------------------------------------------------------------------

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
    from django_cfg.core.state import get_current_config
    config = get_current_config()
    if config and hasattr(config, 'project_name'):
        return config.project_name
    return ""


@register.simple_tag
def is_dev():
    try:
        from django_cfg.core.config import get_current_config
        config = get_current_config()
        return config and config.is_development
    except Exception:
        return False


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
    """Every dashboard tab, from every source. See django_dashboard/resolver.py.

    This used to read `config.dashboard` DIRECTLY, which returned only the tabs
    the consumer project declared in its Pydantic config — silently omitting
    tabs contributed by extensions and by built-in django-cfg apps. Those tabs
    existed, resolved, and rendered when visited by URL; they just never appeared
    in the tab bar, so nobody could reach them.

    `admin/cfg_overview.html` (the admin index) loads {% load django_cfg %}, so THIS is the tag that
    actually renders the admin tab bar — not the identically-named one in
    django_cfg_dashboard.py. Both now delegate to the one resolver.
    """
    try:
        request = context.get('request')
        if not request or not getattr(request.user, 'is_staff', False):
            return None

        from django_cfg.modules.django_dashboard.resolver import (
            get_dashboard_config as _resolve,
        )
        from django_cfg.modules.django_dashboard.registry import TabRegistry

        # Only the tabs this user may open: a superuser-only tab in the bar of a
        # staff member was a button that answered 403.
        config = _resolve()
        if config is None:
            return None
        registry = TabRegistry()
        visible = [t for t in config.tabs if registry.has_permission(t, request)]
        return config.model_copy(update={"tabs": visible}) if visible else None
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
