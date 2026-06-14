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

        request = context.get('request')
        if not request or not getattr(request.user, 'is_staff', False):
            return None

        dashboard = getattr(config, 'dashboard', None)
        config_tabs = list(dashboard.tabs) if dashboard else []

        # Merge tabs declared by auto-discovered extensions. Config-level tabs
        # win on slug collision (the consumer project stays authoritative).
        from django_cfg.modules.django_dashboard.extension_tabs import (
            get_extension_dashboard_tabs,
        )
        known_slugs = {t.slug for t in config_tabs}
        ext_tabs = [t for t in get_extension_dashboard_tabs() if t.slug not in known_slugs]

        merged_tabs = config_tabs + ext_tabs
        if not merged_tabs:
            return None

        if not ext_tabs:
            return dashboard

        # Build a merged DashboardConfig without mutating the project config.
        from django_cfg.modules.django_dashboard.models import DashboardConfig
        if dashboard:
            return dashboard.model_copy(update={"tabs": merged_tabs})
        return DashboardConfig(tabs=merged_tabs)
    except Exception:
        return None
