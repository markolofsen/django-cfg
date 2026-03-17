"""
django_rq — RQ Overview dashboard.

KPI cards (total / failed / success rate / avg duration) + timeline + queue/func breakdowns.
Registered via auto_register() as: RQ / RQ Overview.
"""

from __future__ import annotations

_HOURS_OPTIONS = {"1h": 1, "6h": 6, "24h": 24, "72h": 72, "168h": 168}


def render_rq_overview() -> None:
    import pandas as pd
    import plotly.express as px
    import streamlit as st
    import streamlit_antd_components as sac

    from ..services.d1_query import D1RQQuery
    from django_cfg.modules.streamlit_admin.core.utils import (
        plotly_dark_layout,
        live_toggle,
        chip_filter,
        KpiItem,
        kpi_row,
        STATUS_COLORS,
    )

    st.title("RQ Overview")

    # ── Live toggle + time range ───────────────────────────────────────────────
    ctrl_col, range_col = st.columns([1, 4])
    with ctrl_col:
        live_toggle(key="rq_ov_live", interval_ms=60_000)
    with range_col:
        selected_range = chip_filter(
            list(_HOURS_OPTIONS.keys()),
            key="rq_ov_hours",
            color="blue",
        )
    hours = _HOURS_OPTIONS.get(selected_range, 24)

    query = D1RQQuery()

    # ── KPI cards ─────────────────────────────────────────────────────────────
    try:
        stats = query.get_job_event_stats(hours=hours)
    except Exception as exc:
        sac.alert(label="Failed to load stats", description=str(exc), color="error")
        return

    total = int(stats.get("total") or 0)
    finished = int(stats.get("finished") or 0)
    failed = int(stats.get("failed") or 0)
    avg_dur = stats.get("avg_duration")
    avg_dur_str = f"{avg_dur:.1f}s" if avg_dur is not None else "—"
    success_rate = f"{int(finished / total * 100)}%" if total > 0 else "—"

    kpi_row([
        KpiItem(title="Total jobs",   content=str(total),      description=f"last {selected_range}"),
        KpiItem(title="Failed",       content=str(failed),     description=f"last {selected_range}"),
        KpiItem(title="Success rate", content=success_rate,    description=f"last {selected_range}"),
        KpiItem(title="Avg duration", content=avg_dur_str,     description="finished jobs"),
    ])

    # ── Timeline bar chart ────────────────────────────────────────────────────
    sac.divider(label="Jobs over time", icon="bar-chart", size="xs", color="gray")
    try:
        timeline = query.get_job_events_timeline(hours=hours)
        if timeline:
            df_t = pd.DataFrame(timeline)
            fig = px.bar(
                df_t, x="hour", y="count", color="status",
                color_discrete_map=STATUS_COLORS,
                title="",
                labels={"hour": "", "count": ""},
                barmode="stack",
            )
            st.plotly_chart(plotly_dark_layout(fig, height=220), use_container_width=True)
        else:
            sac.result(label="No data", status="empty")
    except Exception as exc:
        sac.alert(label="Timeline unavailable", description=str(exc), color="warning", size="sm")

    # ── Two-column breakdowns ─────────────────────────────────────────────────
    sac.divider(label="Breakdown", icon="pie-chart", size="xs", color="gray")
    bc1, bc2 = st.columns(2)

    with bc1:
        st.caption("Top functions by run count")
        try:
            func_data = query.get_func_name_breakdown(hours=hours, limit=10)
            if func_data:
                df_f = pd.DataFrame(func_data)
                df_agg = df_f.groupby("func_name")["count"].sum().reset_index()
                df_agg = df_agg.sort_values("count", ascending=True).tail(10)
                df_agg["func_short"] = df_agg["func_name"].apply(lambda x: x.split(".")[-1])
                fig_f = px.bar(
                    df_agg, x="count", y="func_short", orientation="h",
                    labels={"count": "", "func_short": ""},
                    color_discrete_sequence=["#3b82f6"],
                )
                st.plotly_chart(plotly_dark_layout(fig_f, height=250), use_container_width=True)
        except Exception:
            sac.result(label="No data", status="empty")

    with bc2:
        st.caption("By queue")
        try:
            queue_data = query.get_queue_breakdown(hours=hours)
            if queue_data:
                df_q = pd.DataFrame(queue_data)
                df_q_agg = df_q.groupby("queue")["count"].sum().reset_index()
                fig_q = px.pie(
                    df_q_agg, names="queue", values="count",
                    hole=0.45,
                    color_discrete_sequence=["#3b82f6", "#8b5cf6", "#06b6d4", "#22c55e", "#f97316"],
                )
                plotly_dark_layout(fig_q, height=250)
                fig_q.update_traces(textposition="inside", textinfo="percent+label")
                fig_q.update_layout(showlegend=False)
                st.plotly_chart(fig_q, use_container_width=True)
        except Exception:
            sac.result(label="No data", status="empty")
