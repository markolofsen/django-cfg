"""The single source of truth for "which dashboard tabs exist".

Before this module, the tab list was assembled in TWO places that disagreed:

  * ``templatetags/django_cfg_dashboard.py`` merged extension tabs into the
    config, so they appeared in the tab bar;
  * ``views/tab.py`` resolved ``config.get_tab(slug)`` against the RAW
    ``config.tabs``, which never contained them.

The result: an extension tab rendered in the navigation and then **404'd when
clicked**. Two code paths answering the same question is how that happens, so
there is now exactly one.

Tab sources, in precedence order (first wins on a slug collision):

  1. ``DashboardConfig.tabs`` — the consumer project stays authoritative.
  2. Built-in django-cfg app tabs (e.g. analytics), for apps that are enabled.
  3. Auto-discovered extension tabs.
"""

from __future__ import annotations

from typing import List, Optional

from django_cfg.utils import get_logger

from .models import DashboardConfig, DashboardTab

logger = get_logger(__name__)


def _builtin_tabs() -> List[DashboardTab]:
    """Tabs contributed by django-cfg's own apps.

    Each built-in app that wants a tab exposes ``get_dashboard_tabs()``; it is
    only consulted when that app is actually enabled, so a disabled app
    contributes nothing rather than rendering a tab that 404s.
    """
    from django_cfg.modules.base import BaseCfgModule

    base = BaseCfgModule()
    tabs: List[DashboardTab] = []

    if base.is_analytics_enabled():
        try:
            from django_cfg.apps.tools.analytics.dashboard import get_dashboard_tabs

            tabs.extend(get_dashboard_tabs())
        except Exception:
            # A broken built-in tab must never take down the whole dashboard.
            logger.exception("Analytics dashboard tab failed to load")

    return tabs


def get_all_tabs(config=None) -> List[DashboardTab]:
    """Every tab visible to this project, deduplicated by slug."""
    if config is None:
        from django_cfg.core.config import get_current_config

        config = get_current_config()

    dashboard = getattr(config, "dashboard", None) if config else None
    tabs: List[DashboardTab] = list(dashboard.tabs) if dashboard else []
    seen = {t.slug for t in tabs}

    def _add(candidates: List[DashboardTab]) -> None:
        for tab in candidates:
            if tab.slug not in seen:
                seen.add(tab.slug)
                tabs.append(tab)

    _add(_builtin_tabs())

    from .extension_tabs import get_extension_dashboard_tabs

    _add(get_extension_dashboard_tabs())

    return tabs


def get_dashboard_config(config=None) -> Optional[DashboardConfig]:
    """The project's DashboardConfig with every tab source merged in.

    Returns None when there are no tabs at all — the dashboard has nothing to
    show, and both the view and the tab bar treat that as "not configured".
    """
    if config is None:
        from django_cfg.core.config import get_current_config

        config = get_current_config()

    dashboard = getattr(config, "dashboard", None) if config else None
    tabs = get_all_tabs(config)

    if not tabs:
        return None

    if dashboard is not None:
        # model_copy, not mutation — the project's config object is shared.
        return dashboard.model_copy(update={"tabs": tabs})
    return DashboardConfig(tabs=tabs)


__all__ = ["get_all_tabs", "get_dashboard_config"]
