"""
django_logging.streamlit — Streamlit UI pages for D1 log events.

Call auto_register() once to add Logging pages to streamlit_admin page_registry:

    from django_cfg.modules.django_logging.streamlit import auto_register
    auto_register()

Pages registered:
    Logging / Log Events  — triage dashboard: level filters, AgGrid, resolve/reopen
"""

from __future__ import annotations

_registered: bool = False


def auto_register() -> None:
    """Register django_logging pages into streamlit_admin page_registry.

    Idempotent — calling multiple times has no effect.
    """
    global _registered
    if _registered:
        return

    try:
        from core.registry import page_registry
    except ImportError:
        from django_cfg.modules.streamlit_admin.core.registry import page_registry

    from .pages.log_events import render_log_events

    page_registry.register_page(
        name="Log Events",
        render_func=render_log_events,
        icon="article",
        group="Logging",
        order=10,
    )
    _registered = True


__all__ = ["auto_register"]
