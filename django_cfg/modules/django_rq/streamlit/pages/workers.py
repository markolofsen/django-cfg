"""
django_rq — RQ Workers page.

AgGrid with latest heartbeat per worker + heartbeat timeline chart on row select.
Registered via auto_register() as: RQ / RQ Workers.
"""

from __future__ import annotations

_STATE_COLORS: dict[str, str] = {
    "busy":      "rgba(59,130,246,0.12)",
    "suspended": "rgba(249,115,22,0.12)",
}
_STALE_MINUTES: int = 10


def render_rq_workers() -> None:
    import pandas as pd
    import plotly.express as px
    import streamlit as st
    import streamlit_antd_components as sac
    from st_aggrid import JsCode
    from datetime import datetime, timezone, timedelta

    from ..services.d1_query import D1RQQuery
    from ..models import WorkerRow
    from django_cfg.modules.streamlit_admin.core.utils import (
        aggrid_default_builder, aggrid_render, aggrid_get_selected_row,
        time_ago, plotly_dark_layout, live_toggle,
    )

    st.title("RQ Workers")

    live_toggle(key="rq_workers_live", interval_ms=30_000)

    query = D1RQQuery()

    # ── Fetch latest heartbeats ────────────────────────────────────────────────
    try:
        rows_raw = query.get_latest_worker_stats()
    except Exception as exc:
        sac.alert(label="Failed to load workers", description=str(exc), color="error")
        return

    if not rows_raw:
        sac.result(label="No workers found", description="No heartbeats recorded yet", status="empty")
        return

    workers = [WorkerRow.from_d1(r) for r in rows_raw]

    # Mark stale workers (no heartbeat in last N minutes)
    stale_cutoff = (datetime.now(timezone.utc) - timedelta(minutes=_STALE_MINUTES)).isoformat()

    df = pd.DataFrame([w.to_display_dict() for w in workers])
    df["ago"] = df["last_heartbeat"].apply(time_ago)
    df["stale"] = df["last_heartbeat"].apply(lambda ts: ts < stale_cutoff[:19] if ts else True)

    # ── AgGrid ────────────────────────────────────────────────────────────────
    row_class_rules = {
        "ag-row-busy":      JsCode("function(p){return p.data.state==='busy';}"),
        "ag-row-suspended": JsCode("function(p){return p.data.state==='suspended';}"),
        "ag-row-stale":     JsCode("function(p){return p.data.stale===true;}"),
    }
    custom_css = {
        ".ag-row-busy":      {"background-color": _STATE_COLORS["busy"] + " !important"},
        ".ag-row-suspended": {"background-color": _STATE_COLORS["suspended"] + " !important"},
        ".ag-row-stale":     {"background-color": "rgba(239,68,68,0.10) !important"},
    }

    display_cols = ["worker_name", "state", "queues", "current_job_id", "successful", "failed", "ago", "stale"]
    gb = aggrid_default_builder(df[display_cols])
    gb.configure_column("worker_name",    header_name="Worker",      flex=3)
    gb.configure_column("state",          header_name="State",       width=100)
    gb.configure_column("queues",         header_name="Queues",      flex=2)
    gb.configure_column("current_job_id", header_name="Current job", flex=2)
    gb.configure_column("successful",     header_name="OK",          width=70, type=["numericColumn"])
    gb.configure_column("failed",         header_name="Fail",        width=70, type=["numericColumn"])
    gb.configure_column("ago",            header_name="Heartbeat",   width=110)
    gb.configure_column("stale",          hide=True)
    gb.configure_grid_options(rowClassRules=row_class_rules)

    grid_response = aggrid_render(df[display_cols], gb, key="rq_workers_grid", custom_css=custom_css)

    # ── Detail: heartbeat timeline ─────────────────────────────────────────────
    row = aggrid_get_selected_row(grid_response)
    if not row:
        return

    worker_name = row.get("worker_name", "")
    if not worker_name:
        return

    sac.divider(label=f"Timeline — {worker_name}", icon="activity", size="xs", color="gray")

    try:
        timeline_raw = query.get_worker_timeline(worker_name=worker_name, hours=24)
        if not timeline_raw:
            sac.result(label="No heartbeat history", status="empty")
            return

        df_t = pd.DataFrame(timeline_raw)
        fig = px.line(
            df_t,
            x="heartbeat_at",
            y="successful_job_count",
            title=f"{worker_name} — cumulative successful jobs (24h)",
            labels={"heartbeat_at": "", "successful_job_count": "Successful jobs"},
            color_discrete_sequence=["#22c55e"],
        )
        st.plotly_chart(plotly_dark_layout(fig, height=220), use_container_width=True)

        # Worker meta
        for w in workers:
            if w.worker_name == worker_name:
                st.json({
                    "queues":     w.queues,
                    "state":      w.state,
                    "successful": w.successful_job_count,
                    "failed":     w.failed_job_count,
                    "uptime_s":   round(w.total_working_time_seconds, 1),
                    "heartbeat":  time_ago(w.heartbeat_at),
                })
                break
    except Exception as exc:
        sac.alert(label="Timeline unavailable", description=str(exc), color="warning", size="sm")
