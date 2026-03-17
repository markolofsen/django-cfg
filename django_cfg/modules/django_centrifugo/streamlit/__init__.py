"""
django_centrifugo.streamlit — Streamlit UI pages for Centrifugo monitoring.

Call auto_register() once to add Centrifugo pages to streamlit_admin page_registry:

    from django_cfg.modules.django_centrifugo.streamlit import auto_register
    auto_register()

Pages registered:
    Centrifugo / Overview   — KPI cards + timeline + status breakdown (D1)
    Centrifugo / Publishes  — paginated publish log AgGrid + filters + detail panel (D1)
    Centrifugo / Channels   — per-channel stats table (D1)
"""

from __future__ import annotations

_registered: bool = False


def auto_register() -> None:
    """Register django_centrifugo pages into streamlit_admin page_registry.

    Idempotent — calling multiple times has no effect.
    """
    global _registered
    if _registered:
        return

    try:
        from core.registry import page_registry  # relative (inside streamlit_admin CWD)
    except ImportError:
        from django_cfg.modules.streamlit_admin.core.registry import page_registry

    from .pages.overview import render_centrifugo_overview
    from .pages.publishes import render_centrifugo_publishes
    from .pages.channels import render_centrifugo_channels

    page_registry.register_page(
        name="Centrifugo Overview",
        render_func=render_centrifugo_overview,
        icon="broadcast",
        group="Centrifugo",
        order=5,
    )
    page_registry.register_page(
        name="Centrifugo Publishes",
        render_func=render_centrifugo_publishes,
        icon="list",
        group="Centrifugo",
        order=10,
    )
    page_registry.register_page(
        name="Centrifugo Channels",
        render_func=render_centrifugo_channels,
        icon="diagram-3",
        group="Centrifugo",
        order=20,
    )
    _registered = True


__all__ = ["auto_register"]
