"""
django_grpc.streamlit — Streamlit UI pages for gRPC monitoring.

Call auto_register() once to add gRPC pages to streamlit_admin page_registry:

    from django_cfg.modules.django_grpc.streamlit import auto_register
    auto_register()

Pages registered:
    gRPC / Overview      — KPI cards + request rate chart + server status
    gRPC / Connections   — connection states table + event timeline
    gRPC / Request Logs  — paginated request logs with filters
"""

from __future__ import annotations

_registered: bool = False


def auto_register() -> None:
    """Register django_grpc pages into streamlit_admin page_registry.

    Idempotent — calling multiple times has no effect.
    """
    global _registered
    if _registered:
        return

    try:
        from core.registry import page_registry  # relative (inside streamlit_admin CWD)
    except ImportError:
        from django_cfg.modules.streamlit_admin.core.registry import page_registry

    from .pages.overview import render_grpc_overview
    from .pages.connections import render_grpc_connections
    from .pages.request_logs import render_grpc_request_logs

    page_registry.register_page(
        name="gRPC Overview",
        render_func=render_grpc_overview,
        icon="server",
        group="gRPC",
        order=5,
    )
    page_registry.register_page(
        name="gRPC Connections",
        render_func=render_grpc_connections,
        icon="diagram-3",
        group="gRPC",
        order=10,
    )
    page_registry.register_page(
        name="gRPC Request Logs",
        render_func=render_grpc_request_logs,
        icon="list-ul",
        group="gRPC",
        order=20,
    )
    _registered = True


__all__ = ["auto_register"]
