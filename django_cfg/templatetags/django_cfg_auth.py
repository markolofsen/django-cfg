"""
Template tags: JWT tokens, user authentication helpers.
"""

from django import template
from django.utils.safestring import mark_safe

register = template.Library()


def _get_refresh_token(user):
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


@register.simple_tag(takes_context=True)
def user_jwt_token(context):
    """
    Return JWT access token for the current authenticated user.

    Usage:
        {% load django_cfg_auth %}
        <script>window.TOKEN = '{% user_jwt_token %}';</script>
    """
    user = _authenticated_user(context)
    if not user:
        return ''
    return str(_get_refresh_token(user).access_token)


@register.simple_tag(takes_context=True)
def user_jwt_refresh_token(context):
    """
    Return JWT refresh token for the current authenticated user.

    Usage:
        {% load django_cfg_auth %}
        <script>window.REFRESH = '{% user_jwt_refresh_token %}';</script>
    """
    user = _authenticated_user(context)
    if not user:
        return ''
    return str(_get_refresh_token(user))


@register.simple_tag(takes_context=True)
def inject_jwt_tokens_script(context):
    """
    Render a <script> that injects JWT tokens into localStorage.

    Usage:
        {% load django_cfg_auth %}
        {% inject_jwt_tokens_script %}
    """
    user = _authenticated_user(context)
    if not user:
        return ''
    refresh = _get_refresh_token(user)
    access = str(refresh.access_token)
    ref = str(refresh)
    script = f"""<script>
(function() {{
    try {{
        localStorage.setItem('auth_token', '{access}');
        localStorage.setItem('refresh_token', '{ref}');
    }} catch (e) {{
        console.error('Failed to inject JWT tokens:', e);
    }}
}})();
</script>"""
    return mark_safe(script)


@register.simple_tag(takes_context=True)
def generate_jwt_tokens(context):
    """
    Return dict with 'access' and 'refresh' JWT tokens.

    Usage:
        {% load django_cfg_auth %}
        {% generate_jwt_tokens as jwt %}
        localStorage.setItem('auth_token', '{{ jwt.access }}');
    """
    user = _authenticated_user(context)
    if not user:
        return {'access': '', 'refresh': ''}
    try:
        refresh = _get_refresh_token(user)
        return {'access': str(refresh.access_token), 'refresh': str(refresh)}
    except Exception:
        return {'access': '', 'refresh': ''}


@register.simple_tag(takes_context=True)
def can_view_admin_dashboard(context):
    """
    Return True if the current user is a superuser.

    Usage:
        {% load django_cfg_auth %}
        {% can_view_admin_dashboard as ok %}
        {% if ok %}...{% endif %}
    """
    from django.contrib.auth.models import AnonymousUser
    request = context.get('request')
    if not request:
        return False
    user = getattr(request, 'user', None)
    if not user or isinstance(user, AnonymousUser) or not user.is_authenticated:
        return False
    return user.is_superuser
