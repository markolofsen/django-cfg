"""Shared helpers for Monitor Streamlit pages."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any


def time_ago(ts: str) -> str:
    """Convert ISO timestamp string to human-readable 'X ago' string."""
    if not ts:
        return ""
    try:
        dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        diff = datetime.now(timezone.utc) - dt
        total = int(diff.total_seconds())
        if total < 60:
            return f"{total}s ago"
        if total < 3600:
            return f"{total // 60}m ago"
        if total < 86400:
            return f"{total // 3600}h ago"
        days = total // 86400
        if days < 30:
            return f"{days}d ago"
        return dt.strftime("%b %d")
    except Exception:
        return ts[:16] if len(ts) > 16 else ts


# Colour maps reused across pages
TYPE_COLOR: dict[str, str] = {
    "SERVER_ERROR": "red",
    "SLOW_QUERY": "orange",
    "RQ_FAILURE": "volcano",
    "OOM_KILL": "magenta",
    "LOG_ERROR": "gold",
    "UNHANDLED_EXCEPTION": "red",
    "JS_ERROR": "red",
    "NETWORK_ERROR": "orange",
    "ERROR": "volcano",
    "WARNING": "gold",
    "CONSOLE": "blue",
    "PAGE_VIEW": "green",
    "PERFORMANCE": "cyan",
}


# ─── AgGrid helpers ───────────────────────────────────────────────────────────

def aggrid_get_selected_row(grid_response: Any) -> dict[str, Any] | None:
    """Extract the first selected row dict from an AgGrid response.

    Handles both DataFrame (newer st-aggrid) and list (older) return formats.
    Returns None if nothing is selected.
    """
    selected_rows = grid_response.get("selected_rows")
    if selected_rows is None or len(selected_rows) == 0:
        return None
    if hasattr(selected_rows, "iloc"):
        return selected_rows.iloc[0].to_dict()
    return selected_rows[0]


def aggrid_default_builder(df: Any, *, row_height: int = 36) -> Any:
    """Return a GridOptionsBuilder pre-configured with project defaults.

    Caller must still call .configure_column() for page-specific columns,
    then .build() to get gridOptions.
    """
    from st_aggrid import GridOptionsBuilder
    gb = GridOptionsBuilder.from_dataframe(df)
    gb.configure_default_column(resizable=True, sortable=True, filter=True, min_width=80)
    gb.configure_selection("single", use_checkbox=False, pre_selected_rows=[])
    gb.configure_grid_options(rowHeight=row_height, suppressMovableColumns=True)
    return gb


def aggrid_render(df: Any, gb: Any, *, key: str, custom_css: dict | None = None) -> Any:
    """Render AgGrid with project-standard settings.

    Returns the full grid_response dict.
    Height is auto-calculated: min(500, 60 + rows*37).
    """
    from st_aggrid import AgGrid, GridUpdateMode, DataReturnMode
    return AgGrid(
        df,
        gridOptions=gb.build(),
        height=min(500, 60 + len(df) * 37),
        update_mode=GridUpdateMode.SELECTION_CHANGED,
        data_return_mode=DataReturnMode.AS_INPUT,
        allow_unsafe_jscode=True,
        theme="alpine",
        custom_css=custom_css or {},
        use_container_width=True,
        key=key,
    )


# ─── Chip filter helper ───────────────────────────────────────────────────────

def chip_filter(
    options: list[str],
    *,
    key: str,
    color: str = "blue",
    variant: str = "outline",
) -> str:
    """Render a sac.chip filter and return the selected option string.

    Always returns a str — never int or None.
    index=0 → first option selected by default.
    """
    import streamlit_antd_components as sac
    idx = sac.chip(
        items=options,
        index=0,
        size="sm",
        radius="md",
        variant=variant,
        color=color,
        key=key,
    )
    if isinstance(idx, int):
        return options[idx]
    if isinstance(idx, str):
        return idx
    return options[0]


# ─── Project selectbox helper ─────────────────────────────────────────────────

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


# ─── Plotly chart helpers ─────────────────────────────────────────────────────

def plotly_dark_layout(fig: Any, *, height: int = 220, title: str = "") -> Any:
    """Apply project-standard dark layout to a plotly figure. Returns the figure."""
    fig.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font_color="#EDEDED",
        margin=dict(l=0, r=0, t=30 if title else 10, b=0),
        height=height,
    )
    fig.update_xaxes(showgrid=False, tickangle=-30)
    fig.update_yaxes(gridcolor="rgba(255,255,255,0.08)")
    return fig


# ─── Extra JSON display ───────────────────────────────────────────────────────

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


# ─── Live toggle + autorefresh ────────────────────────────────────────────────

def live_toggle(*, key: str, interval_ms: int = 30_000) -> bool:
    """Render Live toggle. If enabled, starts st_autorefresh. Returns bool."""
    import streamlit as st
    from streamlit_autorefresh import st_autorefresh
    live_col, _ = st.columns([1, 5])
    with live_col:
        live_mode = st.toggle("Live", value=False, help=f"Auto-refresh every {interval_ms // 1000}s", key=key)
    if live_mode:
        st_autorefresh(interval=interval_ms, debounce=True, key=f"{key}_refresh")
    return live_mode


__all__ = [
    "time_ago",
    "TYPE_COLOR",
    # AgGrid
    "aggrid_get_selected_row",
    "aggrid_default_builder",
    "aggrid_render",
    # Filters
    "chip_filter",
    "project_selectbox",
    # Charts
    "plotly_dark_layout",
    # UI
    "render_extra_json",
    "live_toggle",
]
