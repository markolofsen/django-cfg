"""
django_monitor — Server Events triage dashboard.

Registered via auto_register() as: Monitor / Server Events.
"""

from __future__ import annotations

import streamlit as st  # noqa: E402  (module-level needed for @st.dialog)


# ── True module-level dialogs (query via session_state["srv_query"]) ──────────

@st.dialog("Mark as resolved?")
def _resolve_dialog() -> None:
    action = st.session_state.get("srv_dialog_action")
    if not action:
        return
    _, fingerprint, api_url, message = action
    query = st.session_state.get("srv_query")

    st.write(f"**{message[:100]}**")
    st.caption(f"fingerprint: `{fingerprint}`")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("✅ Confirm", type="primary", use_container_width=True):
            if query:
                query.mark_server_event_resolved(fingerprint=fingerprint, api_url=api_url)
            st.session_state["srv_selected_fp"] = None
            st.session_state.pop("srv_dialog_action", None)
            st.rerun()
    with col2:
        if st.button("Cancel", use_container_width=True):
            st.session_state.pop("srv_dialog_action", None)
            st.rerun()


@st.dialog("Reopen this event?")
def _reopen_dialog() -> None:
    action = st.session_state.get("srv_dialog_action")
    if not action:
        return
    _, fingerprint, api_url, message = action
    query = st.session_state.get("srv_query")

    st.write(f"**{message[:100]}**")
    st.caption(f"fingerprint: `{fingerprint}`")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("↩️ Confirm reopen", type="primary", use_container_width=True):
            if query:
                query.reopen_server_event(fingerprint=fingerprint, api_url=api_url)
            st.session_state["srv_selected_fp"] = None
            st.session_state.pop("srv_dialog_action", None)
            st.rerun()
    with col2:
        if st.button("Cancel", use_container_width=True):
            st.session_state.pop("srv_dialog_action", None)
            st.rerun()


# ── Main page ─────────────────────────────────────────────────────────────────

def render_server_events() -> None:
    import streamlit_antd_components as sac
    import streamlit_shadcn_ui as ui
    from st_aggrid import JsCode

    from ..services.d1_query import D1MonitorQuery
    from ._utils import (
        time_ago,
        aggrid_default_builder, aggrid_render, aggrid_get_selected_row,
        chip_filter, project_selectbox, live_toggle,
    )

    st.title("Server Events")

    query = D1MonitorQuery()
    st.session_state["srv_query"] = query

    # ── Filters ───────────────────────────────────────────────────────────────
    col_live, col1, col2, col3 = st.columns([1, 1, 2, 2])
    with col_live:
        live_toggle(key="srv_live", interval_ms=30_000)
    with col1:
        show_resolved = st.checkbox("Show resolved", value=False)
    with col2:
        projects = query.get_projects()
        api_url = project_selectbox(projects, key="srv_project")
    with col3:
        limit = st.selectbox("Show last", [50, 100, 250, 500], index=1, key="srv_limit") or 100

    # ── Event type chips ──────────────────────────────────────────────────────
    selected_type = chip_filter(
        ["All", "SERVER_ERROR", "LOG_ERROR", "SLOW_QUERY",
         "RQ_FAILURE", "OOM_KILL", "UNHANDLED_EXCEPTION"],
        key="srv_type_chip",
    )

    # ── Metric cards ──────────────────────────────────────────────────────────
    stats = query.get_server_event_stats(api_url=api_url)
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        ui.metric_card(title="Open errors", content=str(stats.open_errors), description="unresolved")
    with c2:
        ui.metric_card(title="Resolved", content=str(stats.resolved), description="marked done")
    with c3:
        ui.metric_card(title="Total occurrences", content=str(stats.total_occurrences), description="all time")
    with c4:
        ui.metric_card(title="Slow queries", content=str(stats.slow_queries), description="performance")

    sac.divider(label="Events", icon="list-ul", size="xs", color="gray")

    # ── Fetch ─────────────────────────────────────────────────────────────────
    events = query.get_server_events(
        is_resolved=show_resolved,
        event_type=None if selected_type == "All" else selected_type,
        api_url=api_url,
        limit=int(limit),
    )

    if not events:
        sac.result(
            label="No events",
            description="Everything looks clean" if not show_resolved else "No resolved events",
            status="success" if not show_resolved else "empty",
        )
        return

    # ── DataFrame ─────────────────────────────────────────────────────────────
    import pandas as pd
    df = pd.DataFrame([e.to_display_dict() for e in events])
    df["ago"] = df["last_seen"].apply(time_ago)

    fp_to_event = {e.fingerprint: e for e in events}

    # ── AgGrid ────────────────────────────────────────────────────────────────
    row_class_rules = {
        "ag-row-error":    JsCode("function(p){return p.data.level==='error'&&p.data.status==='🔴 open';}"),
        "ag-row-warning":  JsCode("function(p){return p.data.level==='warning';}"),
        "ag-row-resolved": JsCode("function(p){return p.data.status==='✅ resolved';}"),
    }
    custom_css = {
        ".ag-row-error":    {"background-color": "rgba(255,60,60,0.08) !important"},
        ".ag-row-warning":  {"background-color": "rgba(255,160,0,0.08) !important"},
        ".ag-row-resolved": {"opacity": "0.45"},
    }

    display_cols = ["status", "event_type", "level", "message", "module", "count", "ago"]
    gb = aggrid_default_builder(df[display_cols])
    gb.configure_column("status",     header_name="Status",    width=120, pinned="left")
    gb.configure_column("event_type", header_name="Type",      width=160)
    gb.configure_column("level",      header_name="Level",     width=90)
    gb.configure_column("message",    header_name="Message",   flex=3, tooltipField="message")
    gb.configure_column("module",     header_name="Module",    flex=1)
    gb.configure_column("count",      header_name="#",         width=60, type=["numericColumn"])
    gb.configure_column("ago",        header_name="Last seen", width=110)
    gb.configure_grid_options(rowClassRules=row_class_rules)

    grid_response = aggrid_render(df[display_cols], gb, key="srv_grid", custom_css=custom_css)

    # ── Selection ─────────────────────────────────────────────────────────────
    row = aggrid_get_selected_row(grid_response)
    if row:
        msg = row.get("message", "")
        etype = row.get("event_type", "")
        for e in events:
            if e.message[:120] == msg and e.event_type == etype:
                st.session_state["srv_selected_fp"] = e.fingerprint
                break

    selected_fp = st.session_state.get("srv_selected_fp")
    if selected_fp and selected_fp in fp_to_event:
        _render_event_detail(fp_to_event[selected_fp])
    elif selected_fp:
        st.session_state["srv_selected_fp"] = None


def _render_event_detail(event) -> None:
    import streamlit_antd_components as sac
    from ._utils import TYPE_COLOR, time_ago, render_extra_json

    is_resolved = event.is_resolved
    fp = event.fingerprint
    api_url = event.api_url
    message = event.message

    sac.divider(label="Event detail", icon="info-circle", size="xs", color="gray")

    action_col, step_col, _ = st.columns([2, 3, 3])
    with action_col:
        if not is_resolved:
            if st.button("✅ Mark as resolved", type="primary",
                         use_container_width=True, key=f"btn_resolve_{fp}"):
                st.session_state["srv_dialog_action"] = ("resolve", fp, api_url, message)
                st.rerun()
        else:
            if st.button("↩️ Reopen", use_container_width=True, key=f"btn_reopen_{fp}"):
                st.session_state["srv_dialog_action"] = ("reopen", fp, api_url, message)
                st.rerun()

    with step_col:
        sac.steps(
            items=["Open", "Triaging", "Resolved"],
            index=2 if is_resolved else 0,
            size="xs",
            color="green" if is_resolved else "red",
        )

    action = st.session_state.get("srv_dialog_action")
    if action:
        if action[0] == "resolve":
            _resolve_dialog()
        else:
            _reopen_dialog()

    type_color = TYPE_COLOR.get(event.event_type, "blue")
    sac.tags([event.event_type, event.level], color=type_color)
    st.subheader(message[:120])

    col1, col2 = st.columns([3, 2])
    with col1:
        st.caption("Stack trace")
        st.code(event.stack_trace or "No stack trace",
                language="python" if event.module else "text")
    with col2:
        st.caption("Details")
        details = {k: v for k, v in {
            "fingerprint":  event.fingerprint,
            "module":       event.module,
            "func_name":    event.func_name,
            "url":          event.url,
            "http_method":  event.http_method,
            "occurrences":  event.occurrence_count,
            "first_seen":   time_ago(event.first_seen),
            "last_seen":    time_ago(event.last_seen),
        }.items() if v}
        st.json(details)
        render_extra_json(event.extra)
