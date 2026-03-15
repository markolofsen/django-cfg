"""
django_monitor.streamlit — Streamlit UI pages for monitor events.

Call auto_register() once to add Monitor pages to streamlit_admin page_registry:

    # admin_app/extensions.py
    from django_cfg.modules.django_monitor.streamlit import auto_register
    auto_register()

Pages registered:
    Monitor / Overview        — combined KPIs, health banner, top errors, 24h charts
    Monitor / Server Events   — triage dashboard: chip filters, AgGrid, row colours, resolve
    Monitor / Frontend Events — chip filters, 3 charts, AgGrid, detail panel
"""

from __future__ import annotations

_registered: bool = False


def auto_register() -> None:
    """Register django_monitor pages into streamlit_admin page_registry.

    Idempotent — calling multiple times has no effect.
    """
    global _registered
    if _registered:
        return

    try:
        from core.registry import page_registry  # relative (when running inside streamlit_admin CWD)
    except ImportError:
        from django_cfg.modules.streamlit_admin.core.registry import page_registry
    from .pages.overview import render_overview
    from .pages.server_events import render_server_events
    from .pages.frontend_events import render_frontend_events

    page_registry.register_page(
        name="Summary",
        render_func=render_overview,
        icon="dashboard",
        group="Monitor",
        order=5,
    )
    page_registry.register_page(
        name="Server Events",
        render_func=render_server_events,
        icon="bug_report",
        group="Monitor",
        order=10,
    )
    page_registry.register_page(
        name="Frontend Events",
        render_func=render_frontend_events,
        icon="web",
        group="Monitor",
        order=20,
    )
    _registered = True


__all__ = ["auto_register"]
