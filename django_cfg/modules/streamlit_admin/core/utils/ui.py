"""Misc UI helpers for Streamlit pages."""

from __future__ import annotations

from typing import TypedDict


class KpiItem(TypedDict, total=False):
    """Shape of a single KPI card passed to kpi_row()."""
    title: str
    content: str
    description: str


def render_extra_json(extra: str) -> None:
    """Display extra JSON field if non-empty. Renders st.caption + st.json."""
    import json
    import streamlit as st
    if not extra or extra == "{}":
        return
    st.caption("Extra")
    try:
        st.json(json.loads(extra))
    except Exception:
        st.text(extra)


def live_toggle(*, key: str, interval_ms: int = 30_000, columns: list[int] | None = None) -> bool:
    """Render Live toggle. If enabled, starts st_autorefresh. Returns bool."""
    import streamlit as st
    from streamlit_autorefresh import st_autorefresh
    col_widths = columns or [1, 5]
    live_col, _ = st.columns(col_widths)
    with live_col:
        live_mode = st.toggle("Live", value=False, help=f"Auto-refresh every {interval_ms // 1000}s", key=key)
    if live_mode:
        st_autorefresh(interval=interval_ms, debounce=True, key=f"{key}_refresh")
    return live_mode


def kpi_row(items: list[KpiItem]) -> None:
    """Render a row of metric cards from a list of KpiItem dicts.

    Usage:
        kpi_row([
            {"title": "Total", "content": "42", "description": "last 24h"},
            {"title": "Failed", "content": "3", "description": "last 24h"},
        ])
    """
    import streamlit as st
    import streamlit_shadcn_ui as ui
    cols = st.columns(len(items))
    for col, item in zip(cols, items):
        with col:
            ui.metric_card(
                title=item.get("title", ""),
                content=str(item.get("content", "")),
                description=item.get("description", ""),
            )


__all__ = ["KpiItem", "render_extra_json", "live_toggle", "kpi_row"]
