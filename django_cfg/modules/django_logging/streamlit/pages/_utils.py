"""Shared helpers for Logging Streamlit pages."""

from __future__ import annotations

from typing import Any

from django_cfg.modules.streamlit_admin.core.utils import (
    time_ago,
    aggrid_get_selected_row,
    aggrid_default_builder,
    aggrid_render,
    chip_filter,
    search_input,
    render_extra_json,
    live_toggle,
    KpiItem,
    kpi_row,
    STATUS_COLORS,
)

LEVEL_COLORS = {
    "critical": "red",
    "error": "red",
    "warning": "orange",
    "info": "blue",
    "debug": "gray",
}


def project_selectbox(projects: list[dict[str, Any]], *, key: str) -> str | None:
    """Render Project selectbox and return selected api_url or None for All."""
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
    "LEVEL_COLORS",
    "STATUS_COLORS",
    "aggrid_get_selected_row",
    "aggrid_default_builder",
    "aggrid_render",
    "chip_filter",
    "search_input",
    "render_extra_json",
    "live_toggle",
    "KpiItem",
    "kpi_row",
    "project_selectbox",
]
