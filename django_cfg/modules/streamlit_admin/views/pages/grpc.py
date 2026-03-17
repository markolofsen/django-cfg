"""gRPC monitoring page for Streamlit admin."""

from __future__ import annotations

import streamlit as st

from models.dashboard import ChangeType, StatCard
from models.grpc import GRPCHealth, MethodStats, ServiceInfo
from services.grpc import GRPCService
from views.components.data_table import render_data_table
from views.components.stat_cards import render_stat_cards

try:
    import streamlit_antd_components as sac
    HAS_SAC = True
except ImportError:
    HAS_SAC = False

try:
    import plotly.graph_objects as go
    HAS_PLOTLY = True
except ImportError:
    HAS_PLOTLY = False

# Import shared utils (available inside Streamlit process path)
try:
    from core.utils import (
        chip_filter, search_input, time_ago,
        live_toggle, kpi_row, KpiItem,
        plotly_dark_layout, CHART_PALETTE,
    )
    HAS_UTILS = True
except ImportError:
    HAS_UTILS = False


# ─────────────────────────────────────────────────────────────
# Main entry point
# ─────────────────────────────────────────────────────────────

def render_grpc_page(service: GRPCService) -> None:
    """Render gRPC monitoring page."""
    st.title("gRPC Monitoring")

    # Live toggle (auto-refresh every N seconds)
    if HAS_UTILS:
        live_toggle(interval=30, key="grpc_live")

    # Period selector
    col_period, col_spacer = st.columns([2, 8])
    with col_period:
        period_hours = st.selectbox(
            "Period",
            options=[1, 6, 24, 48, 168],
            index=2,
            format_func=lambda h: {1: "1h", 6: "6h", 24: "24h", 48: "2d", 168: "7d"}[h],
            label_visibility="collapsed",
            key="grpc_period",
        )

    # Health overview
    health = service.get_health()
    _render_health_stats(health)

    st.divider()

    # Overview statistics + timeline
    overview = service.get_overview_stats()
    _render_overview_kpis(overview)

    if HAS_PLOTLY:
        _render_timeline(service)

    st.divider()

    # Tabs
    if HAS_SAC:
        _render_sac_tabs(service)
    else:
        _render_native_tabs(service)


# ─────────────────────────────────────────────────────────────
# Health stats row
# ─────────────────────────────────────────────────────────────

def _render_health_stats(health: GRPCHealth) -> None:
    status_icon = "✅" if health.status == "healthy" else "⚠️"
    error_type = ChangeType.DOWN if health.error_rate > 1 else ChangeType.NEUTRAL

    cards = [
        StatCard(
            title="Server",
            value=f"{status_icon} {health.status.title()}",
            icon="activity",
            change_type=ChangeType.UP if health.status == "healthy" else ChangeType.DOWN,
        ),
        StatCard(title="Services", value=str(health.services_count), icon="server"),
        StatCard(title="Methods", value=str(health.methods_count), icon="code"),
        StatCard(
            title="Error Rate",
            value=f"{health.error_rate:.1f}%",
            icon="alert-triangle",
            change_type=error_type,
        ),
    ]
    render_stat_cards(cards)


# ─────────────────────────────────────────────────────────────
# Overview KPIs
# ─────────────────────────────────────────────────────────────

def _render_overview_kpis(overview: dict) -> None:
    total = overview.get("total", 0)
    successful = overview.get("successful", 0)
    errors = overview.get("errors", 0)
    avg_ms = overview.get("avg_duration_ms", 0.0)
    p95_ms = overview.get("p95_duration_ms", 0.0)
    success_rate = overview.get("success_rate", 0.0)

    if HAS_UTILS:
        kpi_row([
            KpiItem(title="Total Requests", content=f"{total:,}"),
            KpiItem(title="Successful", content=f"{successful:,}"),
            KpiItem(title="Errors", content=str(errors)),
            KpiItem(title="Success Rate", content=f"{success_rate:.1f}%"),
            KpiItem(title="Avg Latency", content=f"{avg_ms:.0f} ms"),
            KpiItem(title="p95 Latency", content=f"{p95_ms:.0f} ms"),
        ])
    else:
        c1, c2, c3, c4, c5, c6 = st.columns(6)
        c1.metric("Total", f"{total:,}")
        c2.metric("OK", f"{successful:,}")
        c3.metric("Errors", str(errors))
        c4.metric("Success Rate", f"{success_rate:.1f}%")
        c5.metric("Avg ms", f"{avg_ms:.0f}")
        c6.metric("p95 ms", f"{p95_ms:.0f}")


# ─────────────────────────────────────────────────────────────
# Timeline chart
# ─────────────────────────────────────────────────────────────

def _render_timeline(service: GRPCService) -> None:
    st.subheader("Request Timeline")
    try:
        timeline = service.get_timeline()
    except Exception:
        st.caption("Timeline data unavailable")
        return

    if not timeline:
        st.caption("No data for selected period")
        return

    timestamps = [p.get("timestamp", "") for p in timeline]
    totals = [p.get("total", 0) for p in timeline]
    errors = [p.get("errors", 0) for p in timeline]
    avg_ms = [p.get("avg_duration_ms", 0.0) for p in timeline]

    fig = go.Figure()

    # Total requests bars
    fig.add_trace(go.Bar(
        name="Total",
        x=timestamps,
        y=totals,
        marker_color=CHART_PALETTE[0] if HAS_UTILS else "#0070F3",
        opacity=0.85,
    ))

    # Errors bars
    fig.add_trace(go.Bar(
        name="Errors",
        x=timestamps,
        y=errors,
        marker_color="#ef4444",
        opacity=0.85,
    ))

    # Avg latency line on secondary Y axis
    fig.add_trace(go.Scatter(
        name="Avg ms",
        x=timestamps,
        y=avg_ms,
        mode="lines+markers",
        line=dict(color="#f59e0b", width=2),
        marker=dict(size=4),
        yaxis="y2",
    ))

    layout_kwargs = dict(
        barmode="overlay",
        height=280,
        legend=dict(orientation="h", y=1.1),
        yaxis=dict(title="Requests"),
        yaxis2=dict(title="Latency (ms)", overlaying="y", side="right"),
        margin=dict(l=0, r=0, t=20, b=0),
    )

    if HAS_UTILS:
        plotly_dark_layout(fig, **layout_kwargs)
    else:
        fig.update_layout(**layout_kwargs)

    st.plotly_chart(fig, use_container_width=True)


# ─────────────────────────────────────────────────────────────
# Tab renders (sac version)
# ─────────────────────────────────────────────────────────────

def _render_sac_tabs(service: GRPCService) -> None:
    tab = sac.tabs([
        sac.TabsItem("Services", icon="server"),
        sac.TabsItem("Methods", icon="code"),
        sac.TabsItem("Requests", icon="list"),
        sac.TabsItem("Errors", icon="alert-triangle"),
    ], key="grpc_tabs")

    if tab == "Services":
        _render_services_tab(service)
    elif tab == "Methods":
        _render_methods_tab(service)
    elif tab == "Requests":
        _render_requests_tab(service)
    elif tab == "Errors":
        _render_errors_tab(service)


def _render_native_tabs(service: GRPCService) -> None:
    tabs = st.tabs(["Services", "Methods", "Requests", "Errors"])
    with tabs[0]:
        _render_services_tab(service)
    with tabs[1]:
        _render_methods_tab(service)
    with tabs[2]:
        _render_requests_tab(service)
    with tabs[3]:
        _render_errors_tab(service)


# ─────────────────────────────────────────────────────────────
# Services tab
# ─────────────────────────────────────────────────────────────

def _render_services_tab(service: GRPCService) -> None:
    st.subheader("Registered Services")

    services = service.get_services()

    if not services:
        st.info("No gRPC services registered")
        return

    # Search filter
    query = search_input("Search services…", key="grpc_svc_search") if HAS_UTILS else ""
    if query:
        services = [s for s in services if query.lower() in s.name.lower()]

    # Status chip filter
    if HAS_UTILS:
        status_filter = chip_filter(
            items=["all", "active", "idle"],
            key="grpc_svc_status",
            default="all",
        )
        if status_filter != "all":
            services = [s for s in services if s.status == status_filter]

    render_data_table(services, key="grpc_services_table")

    # Service detail drill-down
    if services:
        with st.expander("Service Detail"):
            selected_name = st.selectbox(
                "Select service",
                [s.name for s in services],
                key="grpc_svc_detail_select",
            )
            if selected_name:
                detail = service.get_service_detail(selected_name)
                if detail:
                    c1, c2, c3 = st.columns(3)
                    c1.metric("Total Calls", f"{detail.total_calls:,}")
                    c2.metric("Errors", str(detail.error_count))
                    c3.metric("Avg Latency", f"{detail.avg_latency_ms:.0f} ms")
                    st.caption(f"Package: `{detail.package or '—'}`  |  Methods: {detail.methods_count}")


# ─────────────────────────────────────────────────────────────
# Methods tab
# ─────────────────────────────────────────────────────────────

def _render_methods_tab(service: GRPCService) -> None:
    st.subheader("Method Statistics")

    services = service.get_services()
    if not services:
        st.info("No services available")
        return

    selected = st.selectbox(
        "Service",
        [s.name for s in services],
        key="grpc_method_svc_select",
    )

    if not selected:
        return

    methods = service.get_method_stats(selected)
    if not methods:
        st.info("No method statistics available")
        return

    # Latency bar chart
    if HAS_PLOTLY and methods:
        names = [m.name for m in methods]
        avg_vals = [m.avg_latency_ms for m in methods]
        p99_vals = [m.p99_latency_ms for m in methods]

        fig = go.Figure()
        fig.add_trace(go.Bar(name="Avg ms", x=names, y=avg_vals,
                             marker_color=CHART_PALETTE[0] if HAS_UTILS else "#0070F3"))
        fig.add_trace(go.Bar(name="p99 ms", x=names, y=p99_vals,
                             marker_color=CHART_PALETTE[2] if HAS_UTILS else "#f59e0b"))
        layout_kwargs = dict(barmode="group", height=220, margin=dict(l=0, r=0, t=10, b=0))
        if HAS_UTILS:
            plotly_dark_layout(fig, **layout_kwargs)
        else:
            fig.update_layout(**layout_kwargs)
        st.plotly_chart(fig, use_container_width=True)

    render_data_table(methods, key="grpc_methods_table")


# ─────────────────────────────────────────────────────────────
# Requests tab
# ─────────────────────────────────────────────────────────────

def _render_requests_tab(service: GRPCService) -> None:
    st.subheader("Recent Requests")

    col1, col2, col3 = st.columns([3, 2, 2])
    with col1:
        svc_query = search_input("Filter by service…", key="grpc_req_svc") if HAS_UTILS else ""
    with col2:
        status_chip = (
            chip_filter(["all", "success", "error", "pending"], key="grpc_req_status", default="all")
            if HAS_UTILS else "all"
        )
    with col3:
        limit = st.selectbox("Show", [20, 50, 100], key="grpc_req_limit")

    try:
        # Use service_name filter if provided
        requests_data = service.get_recent_requests(
            service_name=svc_query or None,
            status=status_chip if status_chip != "all" else None,
            limit=limit,
        )
    except Exception:
        # Fallback: basic call without extra params
        requests_data = service.get_recent_errors(limit=limit)

    if not requests_data:
        st.info("No requests found")
        return

    # Build display list
    rows = []
    for r in requests_data:
        if isinstance(r, dict):
            rows.append({
                "Service": r.get("service_name") or r.get("service", ""),
                "Method": r.get("method_name") or r.get("method", ""),
                "Status": r.get("status", ""),
                "Duration ms": r.get("duration_ms") or "",
                "Time": time_ago(r.get("created_at") or r.get("timestamp", "")) if HAS_UTILS else r.get("created_at", ""),
            })
        else:
            rows.append(r)

    if rows and isinstance(rows[0], dict):
        import pandas as pd
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
    else:
        render_data_table(rows, key="grpc_requests_table")


# ─────────────────────────────────────────────────────────────
# Errors tab
# ─────────────────────────────────────────────────────────────

def _render_errors_tab(service: GRPCService) -> None:
    st.subheader("Recent Errors")

    errors = service.get_recent_errors(limit=50)

    if not errors:
        st.success("No recent errors")
        return

    # Summary metric
    st.caption(f"Showing {len(errors)} most recent errors")

    for err in errors:
        svc = err.get("service", "")
        method = err.get("method", "")
        code = err.get("code", "")
        message = err.get("message", "")
        ts = err.get("timestamp", "")

        label = f"**{svc}.{method}** — `{code}`"
        if ts and HAS_UTILS:
            label += f"  ·  {time_ago(ts)}"

        with st.expander(f"{svc}.{method}  [{code}]"):
            if message:
                st.code(message, language="text")
            c1, c2 = st.columns(2)
            c1.caption(f"Service: `{svc}`")
            c2.caption(f"Method: `{method}`")
            if ts:
                st.caption(f"Time: {ts}")
