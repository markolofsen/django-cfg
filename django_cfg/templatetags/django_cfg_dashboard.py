"""
Template tags: custom admin dashboard tabs.
"""

from django import template

register = template.Library()


@register.simple_tag(takes_context=True)
def get_dashboard_config(context):
    """
    Return DashboardConfig for the current staff user, or None if not configured.

    Usage:
        {% load django_cfg_dashboard %}
        {% get_dashboard_config as dashboard %}
        {% if dashboard %}
            {% include "django_dashboard/tabs_bar.html" with all_tabs=dashboard.tabs current_tab=dashboard.tabs.0 dashboard_config=dashboard %}
        {% endif %}
    """
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
