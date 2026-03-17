"""
django_rq.streamlit — Streamlit UI pages for RQ monitoring.

Call auto_register() once to add RQ pages to streamlit_admin page_registry:

    from django_cfg.modules.django_rq.streamlit import auto_register
    auto_register()

Pages registered:
    RQ / RQ Overview  — KPI cards + timeline + queue/func breakdowns (D1)
    RQ / RQ Jobs      — history AgGrid + filters + detail panel (D1)
    RQ / RQ Workers   — latest heartbeats + timeline chart (D1)
"""

from __future__ import annotations

_registered: bool = False


def auto_register() -> None:
    """Register django_rq pages into streamlit_admin page_registry.

    Idempotent — calling multiple times has no effect.
    """
    global _registered
    if _registered:
        return

    try:
        from core.registry import page_registry  # relative (inside streamlit_admin CWD)
    except ImportError:
        from django_cfg.modules.streamlit_admin.core.registry import page_registry

    from .pages.overview import render_rq_overview
    from .pages.jobs import render_rq_jobs
    from .pages.workers import render_rq_workers

    page_registry.register_page(
        name="RQ Overview",
        render_func=render_rq_overview,
        icon="dashboard",
        group="RQ",
        order=5,
    )
    page_registry.register_page(
        name="RQ Jobs",
        render_func=render_rq_jobs,
        icon="list",
        group="RQ",
        order=10,
    )
    page_registry.register_page(
        name="RQ Workers",
        render_func=render_rq_workers,
        icon="people",
        group="RQ",
        order=20,
    )
    _registered = True


__all__ = ["auto_register"]
