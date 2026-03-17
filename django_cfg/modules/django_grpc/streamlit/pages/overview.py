"""
gRPC Overview page — KPI cards + request rate chart + server status.
"""

from __future__ import annotations

import streamlit as st

try:
    from core.utils import (
        KpiItem, kpi_row, live_toggle,
        plotly_dark_layout, CHART_PALETTE,
    )
    _HAS_UTILS = True
except ImportError:
    _HAS_UTILS = False

try:
    import plotly.graph_objects as go
    _HAS_PLOTLY = True
except ImportError:
    _HAS_PLOTLY = False


def _monitoring():
    from django_cfg.modules.django_grpc.services.monitoring.monitoring import MonitoringService
    return MonitoringService()


def render_grpc_overview() -> None:
    st.title("gRPC Overview")

    if _HAS_UTILS:
        live_toggle(interval=30, key="grpc_ov_live")

    col_period, _ = st.columns([2, 8])
    with col_period:
        hours = st.selectbox(
            "Period",
            options=[1, 6, 24, 48, 168],
            index=2,
            format_func=lambda h: {1: "1h", 6: "6h", 24: "24h", 48: "2d", 168: "7d"}[h],
            label_visibility="collapsed",
            key="grpc_ov_period",
        )

    svc = _monitoring()

    # ── Health ───────────────────────────────────────────────────
    try:
        health = svc.get_health_status()
    except Exception as exc:
        st.error(f"Failed to load health data: {exc}")
        health = {}

    is_running = health.get("status") == "healthy"
    status_label = "Running" if is_running else "Stopped"
    status_icon = "✅" if is_running else "⚠️"

    # ── Overview stats ────────────────────────────────────────────
    try:
        overview = svc.get_overview_statistics(hours=hours)
    except Exception:
        overview = {}

    total = overview.get("total", 0)
    successful = overview.get("successful", 0)
    errors = overview.get("errors", 0)
    avg_ms = overview.get("avg_duration_ms", 0.0)
    success_rate = round(successful / total * 100, 1) if total else 100.0

    server = overview.get("server", {})
    services_count = len(server.get("services", []))

    if _HAS_UTILS:
        kpi_row([
            KpiItem(title="Server", content=f"{status_icon} {status_label}"),
            KpiItem(title="Services", content=str(services_count)),
            KpiItem(title="Total Requests", content=f"{total:,}"),
            KpiItem(title="Errors", content=str(errors)),
            KpiItem(title="Success Rate", content=f"{success_rate:.1f}%"),
            KpiItem(title="Avg Latency", content=f"{avg_ms:.0f} ms"),
        ])
    else:
        c1, c2, c3, c4, c5, c6 = st.columns(6)
        c1.metric("Server", f"{status_icon} {status_label}")
        c2.metric("Services", str(services_count))
        c3.metric("Requests", f"{total:,}")
        c4.metric("Errors", str(errors))
        c5.metric("Success Rate", f"{success_rate:.1f}%")
        c6.metric("Avg ms", f"{avg_ms:.0f}")

    # ── Server info ───────────────────────────────────────────────
    if server:
        with st.expander("Server Details", expanded=False):
            col1, col2, col3 = st.columns(3)
            col1.caption(f"**Address:** `{server.get('address', '—')}`")
            col2.caption(f"**PID:** {server.get('pid', '—')}")
            col3.caption(f"**Uptime:** {int(server.get('uptime_seconds', 0))}s")

    st.divider()

    # ── Timeline chart ────────────────────────────────────────────
    if _HAS_PLOTLY:
        try:
            timeline = svc.get_timeline_data(hours=hours)
        except Exception:
            timeline = []

        if timeline:
            st.subheader("Request Timeline")
            timestamps = [p.get("timestamp", "") for p in timeline]
            totals = [p.get("total", 0) for p in timeline]
            errs = [p.get("errors", 0) for p in timeline]
            avg_ms_line = [p.get("avg_duration_ms", 0.0) for p in timeline]

            fig = go.Figure()
            color0 = CHART_PALETTE[0] if _HAS_UTILS else "#0070F3"
            fig.add_trace(go.Bar(name="Total", x=timestamps, y=totals,
                                 marker_color=color0, opacity=0.85))
            fig.add_trace(go.Bar(name="Errors", x=timestamps, y=errs,
                                 marker_color="#ef4444", opacity=0.85))
            fig.add_trace(go.Scatter(name="Avg ms", x=timestamps, y=avg_ms_line,
                                     mode="lines+markers",
                                     line=dict(color="#f59e0b", width=2),
                                     marker=dict(size=4), yaxis="y2"))
            layout_kw = dict(
                barmode="overlay", height=260,
                legend=dict(orientation="h", y=1.1),
                yaxis=dict(title="Requests"),
                yaxis2=dict(title="Latency (ms)", overlaying="y", side="right"),
                margin=dict(l=0, r=0, t=20, b=0),
            )
            if _HAS_UTILS:
                plotly_dark_layout(fig, **layout_kw)
            else:
                fig.update_layout(**layout_kw)
            st.plotly_chart(fig, use_container_width=True)

    # ── Services table ────────────────────────────────────────────
    services_list = server.get("services", [])
    if services_list:
        st.subheader("Services")
        import pandas as pd
        df = pd.DataFrame(services_list)
        cols = [c for c in ["name", "methods_count", "request_count", "error_count", "success_rate"] if c in df.columns]
        st.dataframe(df[cols], use_container_width=True, hide_index=True)
