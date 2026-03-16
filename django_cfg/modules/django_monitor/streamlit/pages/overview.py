"""
django_monitor — Monitor Overview dashboard.

Registered via auto_register() as: Monitor / Overview (order=5, first).
Single-glance health summary: server error KPIs, top errors, frontend 24h trend.
"""

from __future__ import annotations


def render_overview() -> None:
    import pandas as pd
    import plotly.express as px
    import streamlit as st
    import streamlit_antd_components as sac
    import streamlit_shadcn_ui as ui
    from ..services.d1_query import D1MonitorQuery
    from ._utils import time_ago, TYPE_COLOR, plotly_dark_layout, live_toggle

    st.title("Monitor Overview")

    query = D1MonitorQuery()

    # ── Live toggle ───────────────────────────────────────────────────────────
    live_toggle(key="ov_live", interval_ms=60_000)

    # ── Combined stats (1 round-trip) ─────────────────────────────────────────
    try:
        stats = query.get_combined_stats()
    except Exception as exc:
        sac.alert(label="Failed to load stats", description=str(exc), color="error")
        return

    # ── Health banner ─────────────────────────────────────────────────────────
    open_errors = stats.open_errors
    if open_errors == 0:
        sac.alert(
            label="All clear — no open server errors",
            color="success",
            variant="light",
            icon=True,
        )
    else:
        sac.alert(
            label=f"{open_errors} open server error{'s' if open_errors != 1 else ''} need attention",
            color="error",
            variant="filled",
            icon=True,
        )

    # ── KPI row: server ───────────────────────────────────────────────────────
    sac.divider(label="Server", icon="server", size="xs", color="gray")
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        ui.metric_card(title="Open errors", content=str(stats.open_errors), description="unresolved")
    with c2:
        ui.metric_card(title="Resolved", content=str(stats.resolved), description="all time")
    with c3:
        ui.metric_card(title="Total hits", content=str(stats.total_occurrences), description="all occurrences")
    with c4:
        total = stats.resolved + stats.open_errors
        score = int(stats.resolved / total * 100) if total > 0 else 100
        ui.metric_card(title="Health", content=f"{score}%", description="resolved / total")

    # ── KPI row: frontend ─────────────────────────────────────────────────────
    sac.divider(label="Frontend (last 24h)", icon="globe", size="xs", color="gray")
    fc1, fc2, fc3, _ = st.columns(4)
    with fc1:
        ui.metric_card(title="Events", content=str(stats.fe_total_24h), description="last 24h")
    with fc2:
        ui.metric_card(title="JS Errors", content=str(stats.fe_js_errors_24h), description="JS_ERROR")
    with fc3:
        ui.metric_card(title="Network errors", content=str(stats.fe_network_errors_24h), description="NETWORK_ERROR")

    # ── Two-column charts ─────────────────────────────────────────────────────
    sac.divider(label="Activity", icon="activity", size="xs", color="gray")
    chart_col1, chart_col2 = st.columns(2)

    with chart_col1:
        # Frontend events timeline (last 24h)
        try:
            timeline = query.get_frontend_events_timeline(hours=24)
            if timeline:
                df_t = pd.DataFrame(timeline)
                fig = px.area(
                    df_t, x="period", y="count",
                    title="Frontend events (24h)",
                    color_discrete_sequence=["#0070F3"],
                    labels={"period": "", "count": ""},
                )
                st.plotly_chart(plotly_dark_layout(fig, height=200), use_container_width=True)
            else:
                sac.result(label="No frontend events", status="empty")
        except Exception:
            sac.result(label="Chart unavailable", status="error")

    with chart_col2:
        # Frontend event type breakdown
        try:
            breakdown = query.get_frontend_event_type_breakdown(hours=24)
            if breakdown:
                df_br = pd.DataFrame(breakdown)
                palette = ["#ef4444", "#f97316", "#eab308", "#22c55e", "#3b82f6", "#8b5cf6", "#06b6d4", "#ec4899"]
                fig2 = px.pie(
                    df_br, names="event_type", values="count",
                    title="Frontend by type (24h)",
                    hole=0.45,
                    color_discrete_sequence=palette,
                )
                plotly_dark_layout(fig2, height=200)
                fig2.update_layout(legend=dict(orientation="v", x=1.0, y=0.5, font=dict(size=10)))
                fig2.update_traces(textposition="inside", textinfo="percent")
                st.plotly_chart(fig2, use_container_width=True)
        except Exception:
            pass

    # ── Top open server errors ────────────────────────────────────────────────
    sac.divider(label="Top open errors", icon="bug", size="xs", color="gray")
    try:
        top_errors = query.get_top_server_errors(limit=5)
        if not top_errors:
            sac.result(label="No open errors", status="success")
        else:
            for err in top_errors:
                event_type = err.event_type
                message = err.message[:100]
                module = err.module
                count = err.occurrence_count
                ago = time_ago(err.last_seen)
                color = TYPE_COLOR.get(event_type, "blue")

                with st.container():
                    row_l, row_r = st.columns([6, 1])
                    with row_l:
                        sac.tags([event_type], color=color)
                        st.markdown(f"**{message}**")
                        if module:
                            st.caption(f"module: `{module}` · last seen: {ago}")
                    with row_r:
                        st.metric("hits", count)
                    st.divider()
    except Exception as exc:
        sac.alert(label="Failed to load top errors", description=str(exc), color="warning", size="sm")
