"""
Shared helpers for Monitor Streamlit pages.

Generic utilities re-exported from streamlit_admin.core.utils.
Monitor-specific helpers (TYPE_COLOR, project_selectbox) defined here.
"""

from __future__ import annotations

from typing import Any

from django_cfg.modules.streamlit_admin.core.utils import (
    time_ago,
    aggrid_get_selected_row,
    aggrid_default_builder,
    aggrid_render,
    chip_filter,
    search_input,
    plotly_dark_layout,
    render_extra_json,
    live_toggle,
    KpiItem,
    kpi_row,
    EVENT_TYPE_COLORS,
    CHART_PALETTE,
    STATUS_COLORS,
)

# Backwards-compatible alias used throughout monitor pages
TYPE_COLOR = EVENT_TYPE_COLORS


def project_selectbox(projects: list[dict[str, Any]], *, key: str) -> str | None:
    """Render Project selectbox and return the selected api_url or None for All."""
    import streamlit as st
    project_names = ["All"] + [p["project_name"] for p in projects]
    selected = st.selectbox("Project", project_names, key=key) or "All"
    if selected == "All":
        return None
    for p in projects:
        if p.get("project_name") == selected:
            return p.get("api_url")
    return None


__all__ = [
    "time_ago",
    "TYPE_COLOR",
    "EVENT_TYPE_COLORS",
    "CHART_PALETTE",
    "STATUS_COLORS",
    "aggrid_get_selected_row",
    "aggrid_default_builder",
    "aggrid_render",
    "chip_filter",
    "search_input",
    "plotly_dark_layout",
    "render_extra_json",
    "live_toggle",
    "KpiItem",
    "kpi_row",
    "project_selectbox",
]
