"""
django_rq — RQ Jobs history page.

AgGrid table with filters + detail panel (error, stack trace, extra JSON).
Registered via auto_register() as: RQ / RQ Jobs.
"""

from __future__ import annotations

_STATUS_OPTIONS: list[str] = ["All", "finished", "failed", "started", "queued"]
_HOURS_OPTIONS: dict[str, int] = {"1h": 1, "6h": 6, "24h": 24, "72h": 72, "168h": 168}
_STATUS_COLORS: dict[str, str] = {
    "failed":   "rgba(239,68,68,0.12)",
    "finished": "rgba(34,197,94,0.06)",
    "queued":   "rgba(148,163,184,0.10)",
    "started":  "rgba(59,130,246,0.12)",
}
_DETAIL_STATUS_COLOR: dict[str, str] = {
    "finished": "green",
    "failed":   "red",
    "started":  "blue",
    "queued":   "gray",
}


def render_rq_jobs() -> None:
    import pandas as pd
    import streamlit as st
    import streamlit_antd_components as sac
    from st_aggrid import JsCode

    from ..services.d1_query import D1RQQuery
    from ..models import JobEventRow
    from django_cfg.modules.streamlit_admin.core.utils import (
        chip_filter,
        aggrid_default_builder, aggrid_render, aggrid_get_selected_row,
        time_ago, render_extra_json, live_toggle,
    )

    st.title("RQ Jobs")

    # ── Controls ──────────────────────────────────────────────────────────────
    ctrl_col, range_col = st.columns([1, 4])
    with ctrl_col:
        live_toggle(key="rq_jobs_live", interval_ms=60_000)
    with range_col:
        selected_range = chip_filter(
            list(_HOURS_OPTIONS.keys()), key="rq_jobs_hours", color="blue",
        )
    hours = _HOURS_OPTIONS.get(selected_range, 24)

    query = D1RQQuery()

    # ── Status + Queue filter row ─────────────────────────────────────────────
    f_col1, f_col2, f_col3 = st.columns([2, 2, 3])
    with f_col1:
        selected_status = chip_filter(_STATUS_OPTIONS, key="rq_jobs_status", color="green")
    with f_col2:
        try:
            queues = ["All"] + query.get_queues()
        except Exception:
            queues = ["All"]
        selected_queue_chip = chip_filter(queues, key="rq_jobs_queue", color="orange")
    with f_col3:
        search_fn = st.text_input("Function search", placeholder="e.g. send_email", key="rq_jobs_fn", label_visibility="collapsed")

    # ── Fetch ─────────────────────────────────────────────────────────────────
    try:
        rows_raw = query.get_job_events(
            queue=None if selected_queue_chip == "All" else selected_queue_chip,
            status=None if selected_status == "All" else selected_status,
            func_name=search_fn.strip() or None,
            hours=hours,
            limit=300,
        )
    except Exception as exc:
        sac.alert(label="Failed to load jobs", description=str(exc), color="error")
        return

    if not rows_raw:
        sac.result(label="No jobs found", status="empty")
        return

    events = [JobEventRow.from_d1(r) for r in rows_raw]
    df = pd.DataFrame([e.to_display_dict() for e in events])
    df["ago"] = df["created_at"].apply(time_ago)

    # ── AgGrid ────────────────────────────────────────────────────────────────
    row_class_rules = {
        "ag-row-failed":   JsCode("function(p){return p.data.status==='failed';}"),
        "ag-row-finished": JsCode("function(p){return p.data.status==='finished';}"),
        "ag-row-started":  JsCode("function(p){return p.data.status==='started';}"),
        "ag-row-queued":   JsCode("function(p){return p.data.status==='queued';}"),
    }
    custom_css = {
        ".ag-row-failed":   {"background-color": _STATUS_COLORS["failed"] + " !important"},
        ".ag-row-finished": {"background-color": _STATUS_COLORS["finished"] + " !important"},
        ".ag-row-started":  {"background-color": _STATUS_COLORS["started"] + " !important"},
        ".ag-row-queued":   {"background-color": _STATUS_COLORS["queued"] + " !important"},
    }

    display_cols = ["_id", "ago", "queue", "func_name", "status", "duration", "worker_name"]
    gb = aggrid_default_builder(df[display_cols])
    gb.configure_column("_id",         hide=True)
    gb.configure_column("ago",         header_name="When",     width=110)
    gb.configure_column("queue",       header_name="Queue",    width=110)
    gb.configure_column("func_name",   header_name="Function", flex=3)
    gb.configure_column("status",      header_name="Status",   width=100)
    gb.configure_column("duration",    header_name="Duration", width=90)
    gb.configure_column("worker_name", header_name="Worker",   flex=2)
    gb.configure_grid_options(rowClassRules=row_class_rules)

    grid_response = aggrid_render(df[display_cols], gb, key="rq_jobs_grid", custom_css=custom_css)

    # ── Detail panel ──────────────────────────────────────────────────────────
    row = aggrid_get_selected_row(grid_response)
    if row:
        selected_id = row.get("_id", "")
        for evt in events:
            if evt.id == selected_id:
                _render_job_detail(evt)
                break


def _render_job_detail(evt: "JobEventRow") -> None:
    import streamlit as st
    import streamlit_antd_components as sac
    from django_cfg.modules.streamlit_admin.core.utils import render_extra_json, time_ago

    sac.divider(label="Job detail", icon="info-circle", size="xs", color="gray")

    color = _DETAIL_STATUS_COLOR.get(evt.status, "blue")
    sac.tags([evt.status, evt.queue], color=color)
    st.subheader(evt.func_name)

    meta_col, err_col = st.columns([2, 3])
    with meta_col:
        details = {k: v for k, v in {
            "job_id":    evt.job_id,
            "worker":    evt.worker_name or None,
            "duration":  f"{evt.duration_seconds:.1f}s" if evt.duration_seconds else None,
            "created":   time_ago(evt.created_at),
            "finished":  time_ago(evt.finished_at) if evt.finished_at else None,
            "event_type": evt.event_type,
        }.items() if v}
        st.json(details)

    with err_col:
        if evt.error_message:
            st.caption("Error")
            st.error(evt.error_message[:500])
        if evt.stack_trace:
            with st.expander("Stack trace"):
                st.code(evt.stack_trace, language="python")
        render_extra_json(evt.extra)
