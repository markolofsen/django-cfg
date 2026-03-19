"""
django_logging — Log Events triage dashboard.

Registered via auto_register() as: Logging / Log Events.
"""

from __future__ import annotations

import streamlit as st


# ── Dialogs ───────────────────────────────────────────────────────────────────

@st.dialog("Mark as resolved?")
def _resolve_dialog() -> None:
    action = st.session_state.get("log_dialog_action")
    if not action:
        return
    _, fingerprint, api_url, message = action
    query = st.session_state.get("log_query")

    st.write(f"**{message[:100]}**")
    st.caption(f"fingerprint: `{fingerprint}`")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Confirm", type="primary", use_container_width=True):
            if query:
                query.mark_resolved(fingerprint=fingerprint, api_url=api_url)
            st.session_state["log_selected_fp"] = None
            st.session_state.pop("log_dialog_action", None)
            st.rerun()
    with col2:
        if st.button("Cancel", use_container_width=True):
            st.session_state.pop("log_dialog_action", None)
            st.rerun()


@st.dialog("Reopen this event?")
def _reopen_dialog() -> None:
    action = st.session_state.get("log_dialog_action")
    if not action:
        return
    _, fingerprint, api_url, message = action
    query = st.session_state.get("log_query")

    st.write(f"**{message[:100]}**")
    st.caption(f"fingerprint: `{fingerprint}`")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Confirm reopen", type="primary", use_container_width=True):
            if query:
                query.reopen_event(fingerprint=fingerprint, api_url=api_url)
            st.session_state["log_selected_fp"] = None
            st.session_state.pop("log_dialog_action", None)
            st.rerun()
    with col2:
        if st.button("Cancel", use_container_width=True):
            st.session_state.pop("log_dialog_action", None)
            st.rerun()


# ── Main page ─────────────────────────────────────────────────────────────────

def render_log_events() -> None:
    import pandas as pd
    import streamlit_antd_components as sac
    import streamlit_shadcn_ui as ui
    from st_aggrid import JsCode

    from ..services.d1_query import D1LoggingQuery
    from ._utils import (
        time_ago,
        LEVEL_COLORS,
        aggrid_default_builder,
        aggrid_render,
        aggrid_get_selected_row,
        chip_filter,
        project_selectbox,
        live_toggle,
        render_extra_json,
    )

    st.title("Log Events")

    query = D1LoggingQuery()
    st.session_state["log_query"] = query

    # ── Filters ───────────────────────────────────────────────────────────────
    col_live, col1, col2, col3 = st.columns([1, 1, 2, 2])
    with col_live:
        live_toggle(key="log_live", interval_ms=30_000)
    with col1:
        show_resolved = st.checkbox("Show resolved", value=False, key="log_resolved")
    with col2:
        try:
            projects = query.get_projects()
        except Exception:
            projects = []
        api_url = project_selectbox(projects, key="log_project")
    with col3:
        limit = st.selectbox("Show last", [50, 100, 250, 500], index=1, key="log_limit") or 100

    # ── Level chips ───────────────────────────────────────────────────────────
    selected_level = chip_filter(
        ["All", "critical", "error", "warning"],
        key="log_level_chip",
    )
    level_filter = None if selected_level == "All" else selected_level

    # ── Search ────────────────────────────────────────────────────────────────
    search = st.text_input("Search messages", key="log_search", placeholder="e.g. timeout, connection refused")

    # ── Metric cards ──────────────────────────────────────────────────────────
    try:
        stats = query.get_log_event_stats(api_url=api_url)
    except Exception:
        stats = None

    if stats:
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            ui.metric_card(title="Open errors", content=str(stats.open_errors), description="unresolved")
        with c2:
            ui.metric_card(title="Open warnings", content=str(stats.open_warnings), description="unresolved")
        with c3:
            ui.metric_card(title="Resolved", content=str(stats.resolved), description="marked done")
        with c4:
            ui.metric_card(title="Total occurrences", content=str(stats.total_occurrences), description="all time")

    sac.divider(label="Events", icon="list-ul", size="xs", color="gray")

    # ── Fetch ─────────────────────────────────────────────────────────────────
    try:
        events = query.get_log_events(
            is_resolved=show_resolved,
            level=level_filter,
            api_url=api_url,
            search=search or None,
            limit=int(limit),
        )
    except Exception as e:
        st.error(f"Failed to query D1: {e}")
        return

    if not events:
        sac.result(
            label="No events",
            description="Everything looks clean" if not show_resolved else "No resolved events",
            status="success" if not show_resolved else "empty",
        )
        return

    # ── DataFrame ─────────────────────────────────────────────────────────────
    df = pd.DataFrame(events)

    # Add display columns
    df["status"] = df["is_resolved"].apply(lambda x: "resolved" if str(x) == "1" else "open")
    df["count"] = df["occurrence_count"]
    df["ago"] = df["last_seen"].apply(time_ago)
    df["msg_short"] = df["message"].str[:120]

    # ── AgGrid ────────────────────────────────────────────────────────────────
    row_class_rules = {
        "ag-row-error":    JsCode("function(p){return p.data.level==='error'&&p.data.status==='open';}"),
        "ag-row-critical": JsCode("function(p){return p.data.level==='critical';}"),
        "ag-row-warning":  JsCode("function(p){return p.data.level==='warning'&&p.data.status==='open';}"),
        "ag-row-resolved": JsCode("function(p){return p.data.status==='resolved';}"),
    }
    custom_css = {
        ".ag-row-error":    {"background-color": "rgba(255,60,60,0.08) !important"},
        ".ag-row-critical": {"background-color": "rgba(255,0,0,0.15) !important"},
        ".ag-row-warning":  {"background-color": "rgba(255,160,0,0.08) !important"},
        ".ag-row-resolved": {"opacity": "0.45"},
    }

    display_cols = ["status", "level", "logger_name", "msg_short", "count", "ago"]
    gb = aggrid_default_builder(df[display_cols])
    gb.configure_column("status",      header_name="Status",  width=100, pinned="left")
    gb.configure_column("level",       header_name="Level",   width=90)
    gb.configure_column("logger_name", header_name="Logger",  width=180)
    gb.configure_column("msg_short",   header_name="Message", flex=3, tooltipField="msg_short")
    gb.configure_column("count",       header_name="#",        width=60, type=["numericColumn"])
    gb.configure_column("ago",         header_name="Last seen", width=110)
    gb.configure_grid_options(rowClassRules=row_class_rules)

    grid_response = aggrid_render(df[display_cols], gb, key="log_grid", custom_css=custom_css)

    # ── Selection → Detail ────────────────────────────────────────────────────
    row = aggrid_get_selected_row(grid_response)
    if row:
        msg = row.get("msg_short", "")
        logger_name = row.get("logger_name", "")
        for evt in events:
            if evt.get("message", "")[:120] == msg and evt.get("logger_name") == logger_name:
                st.session_state["log_selected_fp"] = evt.get("fingerprint")
                break

    selected_fp = st.session_state.get("log_selected_fp")
    if selected_fp:
        fp_to_event = {e.get("fingerprint"): e for e in events}
        if selected_fp in fp_to_event:
            _render_event_detail(fp_to_event[selected_fp])
        else:
            st.session_state["log_selected_fp"] = None

    # ── Dialog triggers ───────────────────────────────────────────────────────
    action = st.session_state.get("log_dialog_action")
    if action:
        if action[0] == "resolve":
            _resolve_dialog()
        else:
            _reopen_dialog()


def _render_event_detail(event: dict) -> None:
    """Render detail panel for a selected log event."""
    import streamlit_antd_components as sac
    from ._utils import time_ago, LEVEL_COLORS, render_extra_json

    is_resolved = str(event.get("is_resolved")) == "1"
    fp = event.get("fingerprint", "")
    api_url = event.get("api_url", "")
    message = event.get("message", "")

    sac.divider(label="Event detail", icon="info-circle", size="xs", color="gray")

    # Action buttons
    action_col, step_col, _ = st.columns([2, 3, 3])
    with action_col:
        if not is_resolved:
            if st.button("Mark as resolved", type="primary",
                         use_container_width=True, key=f"btn_resolve_{fp}"):
                st.session_state["log_dialog_action"] = ("resolve", fp, api_url, message)
                st.rerun()
        else:
            if st.button("Reopen", use_container_width=True, key=f"btn_reopen_{fp}"):
                st.session_state["log_dialog_action"] = ("reopen", fp, api_url, message)
                st.rerun()

    with step_col:
        sac.steps(
            items=["Open", "Triaging", "Resolved"],
            index=2 if is_resolved else 0,
            size="xs",
            color="green" if is_resolved else "red",
        )

    # Tags
    level = event.get("level", "")
    level_color = LEVEL_COLORS.get(level, "gray")
    sac.tags([level, event.get("logger_name", "")], color=level_color)

    st.subheader(message[:120])

    col1, col2 = st.columns([3, 2])
    with col1:
        st.caption("Stack trace")
        stack = event.get("stack_trace", "")
        st.code(stack or "No stack trace", language="python" if stack else "text")
    with col2:
        st.caption("Details")
        details = {k: v for k, v in {
            "fingerprint":  fp,
            "logger_name":  event.get("logger_name"),
            "module":       event.get("module"),
            "func_name":    event.get("func_name"),
            "pathname":     event.get("pathname"),
            "lineno":       event.get("lineno"),
            "occurrences":  event.get("occurrence_count"),
            "first_seen":   time_ago(event.get("first_seen", "")),
            "last_seen":    time_ago(event.get("last_seen", "")),
        }.items() if v}
        st.json(details)
        render_extra_json(event.get("extra", "{}"))
