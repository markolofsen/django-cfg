"""The Overview tabs this module contributes; asked for by ``django_dashboard/resolver.py``."""

from __future__ import annotations

from django_cfg.modules.django_dashboard.models import DashboardTab

MCP_SLUG = "mcp"
MODULES_SLUG = "modules"


def get_dashboard_tabs(config=None) -> list[DashboardTab]:
    """"MCP" while MCP is enabled (any staff member: each sees their own key), "Modules" for superusers."""
    from .mcp_connect import enabled_mcp

    if config is None:
        from django_cfg.core.state import get_current_config

        config = get_current_config()
    tabs = []
    if enabled_mcp(config) is not None:
        tabs.append(
            DashboardTab(
                slug=MCP_SLUG,
                title="MCP",
                icon="hub",
                template="django_overview/mcp_tab.html",
                callback="django_cfg.modules.django_overview.views.mcp_tab",
            )
        )
    tabs.append(
        DashboardTab(
            slug=MODULES_SLUG,
            title="Modules",
            icon="widgets",
            template="django_overview/modules_tab.html",
            callback="django_cfg.modules.django_overview.views.modules_tab",
            superuser_only=True,
        )
    )
    return tabs
