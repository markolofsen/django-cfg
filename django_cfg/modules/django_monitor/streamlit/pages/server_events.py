"""
django_monitor — Server Events triage dashboard.

Registered via auto_register() as: Monitor / Server Events.

## Selection flow

1. Events load into AgGrid (SELECTION_CHANGED mode, single row)
2. Clicking a row → AgGrid returns selected_rows → session_state["srv_selected_fp"]
3. Detail panel renders below: stack trace, metadata, action buttons
4. "Mark resolved" / "Reopen" buttons set srv_dialog_action → st.rerun()
5. Module-level @st.dialog fires → D1 UPDATE → st.rerun() refreshes the table
"""

from __future__ import annotations

import streamlit as st  # noqa: E402  (module-level needed for @st.dialog)


def _resolve_api_url(selected_project: str, projects: list[dict]) -> str | None:
    if selected_project == "All":
        return None
    for p in projects:
        if p.get("project_name") == selected_project:
            return p.get("api_url")
    return None


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
    import pandas as pd
    import streamlit_antd_components as sac
    import streamlit_shadcn_ui as ui
    from streamlit_autorefresh import st_autorefresh
    from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode, DataReturnMode, JsCode

    from ..services.d1_query import D1MonitorQuery
    from ._utils import time_ago, TYPE_COLOR

    st.title("Server Events")

    query = D1MonitorQuery()
    st.session_state["srv_query"] = query  # dialogs read this

    # ── Filters ───────────────────────────────────────────────────────────────
    col_live, col1, col2, col3 = st.columns([1, 2, 2, 2])
    with col_live:
        live_mode = st.toggle("Live", value=False, help="Auto-refresh every 30s")
    if live_mode:
        st_autorefresh(interval=30_000, debounce=True, key="srv_autorefresh")
    with col1:
        show_resolved = st.checkbox("Show resolved", value=False)
    with col2:
        projects = query.get_projects()
        project_names = ["All"] + [p["project_name"] for p in projects]
        selected_project = st.selectbox("Project", project_names, key="srv_project")
    with col3:
        limit = st.selectbox("Show last", [50, 100, 250, 500], index=1, key="srv_limit")

    api_url = _resolve_api_url(selected_project, projects)

    # ── Event type chips ──────────────────────────────────────────────────────
    event_type_options = [
        "All", "SERVER_ERROR", "LOG_ERROR", "SLOW_QUERY",
        "RQ_FAILURE", "OOM_KILL", "UNHANDLED_EXCEPTION",
    ]
    selected_type_idx = sac.chip(
        items=event_type_options, index=0, size="sm",
        radius="md", variant="outline", color="blue", key="srv_type_chip",
    )
    selected_type = (
        event_type_options[selected_type_idx] if isinstance(selected_type_idx, int)
        else (selected_type_idx if isinstance(selected_type_idx, str) else "All")
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

    # ── Build DataFrame from typed objects ────────────────────────────────────
    df = pd.DataFrame([e.to_display_dict() for e in events])
    df["ago"] = df["last_seen"].apply(time_ago)

    # fingerprint → event index map for selection lookup
    fp_to_event = {e.fingerprint: e for e in events}

    # ── AgGrid (SELECTION_CHANGED — click row → detail) ───────────────────────
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
    gb = GridOptionsBuilder.from_dataframe(df[display_cols])
    gb.configure_default_column(resizable=True, sortable=True, filter=True, min_width=80)
    gb.configure_selection("single", use_checkbox=False, pre_selected_rows=[])
    gb.configure_column("status",     header_name="Status",    width=120, pinned="left")
    gb.configure_column("event_type", header_name="Type",      width=160)
    gb.configure_column("level",      header_name="Level",     width=90)
    gb.configure_column("message",    header_name="Message",   flex=3, tooltipField="message")
    gb.configure_column("module",     header_name="Module",    flex=1)
    gb.configure_column("count",      header_name="#",         width=60, type=["numericColumn"])
    gb.configure_column("ago",        header_name="Last seen", width=110)
    gb.configure_grid_options(rowHeight=36, suppressMovableColumns=True, rowClassRules=row_class_rules)

    grid_response = AgGrid(
        df[display_cols],
        gridOptions=gb.build(),
        height=min(420, 60 + len(df) * 37),
        update_mode=GridUpdateMode.SELECTION_CHANGED,
        data_return_mode=DataReturnMode.AS_INPUT,
        allow_unsafe_jscode=True,
        theme="alpine",
        custom_css=custom_css,
        use_container_width=True,
        key="srv_grid",
    )

    # ── Selection: grid click takes priority, session_state persists across reruns
    selected_rows = grid_response.get("selected_rows")
    if selected_rows is not None and len(selected_rows) > 0:
        # AgGrid returns a DataFrame or list depending on version
        if hasattr(selected_rows, "iloc"):
            row = selected_rows.iloc[0].to_dict()
        else:
            row = selected_rows[0]
        # Match by message+type (display_cols don't include fingerprint)
        # Find the matching event in our typed list
        msg = row.get("message", "")
        etype = row.get("event_type", "")
        for e in events:
            if e.message[:120] == msg and e.event_type == etype:
                st.session_state["srv_selected_fp"] = e.fingerprint
                break

    selected_fp = st.session_state.get("srv_selected_fp")

    # ── Detail ────────────────────────────────────────────────────────────────
    if selected_fp and selected_fp in fp_to_event:
        _render_event_detail(fp_to_event[selected_fp])
    elif selected_fp:
        # fingerprint from previous load, not in current filter — clear it
        st.session_state["srv_selected_fp"] = None


def _render_event_detail(event) -> None:
    import json
    import streamlit_antd_components as sac
    from ._utils import time_ago, TYPE_COLOR

    is_resolved = event.is_resolved
    fp = event.fingerprint
    api_url = event.api_url
    message = event.message

    sac.divider(label="Event detail", icon="info-circle", size="xs", color="gray")

    # ── Action buttons ────────────────────────────────────────────────────────
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

    # ── Fire dialog if action pending ─────────────────────────────────────────
    action = st.session_state.get("srv_dialog_action")
    if action:
        kind = action[0]
        if kind == "resolve":
            _resolve_dialog()
        else:
            _reopen_dialog()

    # ── Event header ──────────────────────────────────────────────────────────
    type_color = TYPE_COLOR.get(event.event_type, "blue")
    sac.tags([event.event_type, event.level], color=type_color)
    st.subheader(message[:120])

    # ── Body ──────────────────────────────────────────────────────────────────
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

        if event.extra and event.extra != "{}":
            st.caption("Extra")
            try:
                st.json(json.loads(event.extra))
            except Exception:
                st.text(event.extra)
