"""
django_monitor — Frontend Events page.

Registered via auto_register() as: Monitor / Frontend Events.
"""

from __future__ import annotations


def render_frontend_events() -> None:
    import pandas as pd
    import plotly.express as px
    import streamlit as st
    import streamlit_antd_components as sac
    import streamlit_shadcn_ui as ui
    from st_aggrid import JsCode

    from ..services.d1_query import D1MonitorQuery
    from ._utils import (
        time_ago, TYPE_COLOR,
        aggrid_default_builder, aggrid_render, aggrid_get_selected_row,
        chip_filter, plotly_dark_layout, live_toggle, render_extra_json,
    )

    st.title("Frontend Events")
    query = D1MonitorQuery()

    # ── Top row: Live + time range + limit ────────────────────────────────────
    col_live, col1, col2 = st.columns([1, 2, 2])
    with col_live:
        live_toggle(key="fe_live", interval_ms=30_000)
    with col1:
        hours = st.selectbox(
            "Time range",
            [1, 6, 24, 72, 168],
            index=3,
            format_func=lambda h: f"Last {h}h",
            key="fe_hours",
        ) or 72
    with col2:
        limit = st.selectbox("Show last", [100, 200, 500], index=1, key="fe_limit") or 200

    # ── Chip filters ──────────────────────────────────────────────────────────
    selected_type = chip_filter(
        ["All", "JS_ERROR", "NETWORK_ERROR", "ERROR", "WARNING",
         "PAGE_VIEW", "PERFORMANCE", "CONSOLE"],
        key="fe_type_chip",
    )
    selected_browser = chip_filter(
        ["All", "Chrome", "Firefox", "Safari", "Edge"],
        key="fe_browser_chip",
        color="gray",
        variant="light",
    )

    # ── Metric cards ──────────────────────────────────────────────────────────
    stats = query.get_frontend_event_stats(hours=int(hours))
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        ui.metric_card(title="Total events", content=str(stats.total), description=f"last {hours}h")
    with c2:
        ui.metric_card(title="JS Errors", content=str(stats.js_errors), description="JS_ERROR")
    with c3:
        ui.metric_card(title="Network errors", content=str(stats.network_errors), description="NETWORK_ERROR")
    with c4:
        ui.metric_card(title="Unique IPs", content=str(stats.unique_ips), description="distinct visitors")

    sac.divider(label="Charts", icon="bar-chart", size="xs", color="gray")

    # ── Charts ────────────────────────────────────────────────────────────────
    timeline = query.get_frontend_events_timeline(hours=int(hours))
    breakdown = query.get_frontend_event_type_breakdown(hours=int(hours))

    chart_col1, chart_col2, chart_col3 = st.columns([3, 2, 2])

    with chart_col1:
        if timeline:
            df_time = pd.DataFrame(timeline)
            fig = px.bar(
                df_time, x="period", y="count",
                title="Events over time",
                color_discrete_sequence=["#0070F3"],
                labels={"period": "", "count": "Events"},
            )
            st.plotly_chart(plotly_dark_layout(fig, height=220), use_container_width=True)
        else:
            sac.result(label="No timeline data", description=f"No events in last {hours}h", status="empty")

    with chart_col2:
        if breakdown:
            df_br = pd.DataFrame(breakdown)
            palette = ["#ef4444", "#f97316", "#eab308", "#22c55e",
                       "#3b82f6", "#8b5cf6", "#06b6d4", "#ec4899"]
            fig2 = px.pie(
                df_br, names="event_type", values="count",
                title="By type", hole=0.4,
                color_discrete_sequence=palette,
            )
            fig2.update_layout(
                showlegend=True,
                legend=dict(orientation="v", x=1.0, y=0.5, font=dict(size=10)),
            )
            fig2.update_traces(textposition="inside", textinfo="percent")
            st.plotly_chart(plotly_dark_layout(fig2, height=220), use_container_width=True)

    with chart_col3:
        events_all = query.get_frontend_events(hours=int(hours), limit=500)
        if events_all:
            bc_data: dict[str, int] = {}
            for e in events_all:
                b = e.browser or "Unknown"
                bc_data[b] = bc_data.get(b, 0) + 1
            df_brow = pd.DataFrame(list(bc_data.items()), columns=["browser", "count"])
            fig3 = px.pie(
                df_brow, names="browser", values="count",
                title="By browser", hole=0.4,
                color_discrete_sequence=px.colors.qualitative.Set2,
            )
            fig3.update_layout(
                showlegend=True,
                legend=dict(orientation="v", x=1.0, y=0.5, font=dict(size=10)),
            )
            fig3.update_traces(textposition="inside", textinfo="percent")
            st.plotly_chart(plotly_dark_layout(fig3, height=220), use_container_width=True)

    sac.divider(label="Events", icon="list-ul", size="xs", color="gray")

    # ── Events fetch ──────────────────────────────────────────────────────────
    events = query.get_frontend_events(
        event_type=None if selected_type == "All" else selected_type,
        browser=None if selected_browser == "All" else selected_browser,
        hours=int(hours),
        limit=int(limit),
    )

    if not events:
        sac.result(label="No events", description=f"No frontend events in the last {hours}h", status="empty")
        return

    # ── DataFrame ─────────────────────────────────────────────────────────────
    df = pd.DataFrame([e.to_display_dict() for e in events])
    df["ago"] = df["last_seen"].apply(time_ago)
    id_to_event = {e.id: e for e in events}
    if "id" not in df.columns:
        df["id"] = [e.id for e in events]

    # ── AgGrid ────────────────────────────────────────────────────────────────
    row_class_rules = {
        "ag-row-fe-error":   JsCode("function(p){return p.data.level==='error';}"),
        "ag-row-fe-warning": JsCode("function(p){return p.data.level==='warning';}"),
    }
    custom_css = {
        ".ag-row-fe-error":   {"background-color": "rgba(255,60,60,0.08) !important"},
        ".ag-row-fe-warning": {"background-color": "rgba(255,160,0,0.08) !important"},
    }

    display_cols = [c for c in [
        "id", "event_type", "level", "message", "browser",
        "os", "device_type", "ip_address", "url", "ago",
    ] if c in df.columns]

    gb = aggrid_default_builder(df[display_cols])
    gb.configure_column("id",          hide=True)
    gb.configure_column("event_type",  header_name="Type",    width=140)
    gb.configure_column("level",       header_name="Level",   width=85)
    gb.configure_column("message",     header_name="Message", flex=3, tooltipField="message")
    gb.configure_column("browser",     header_name="Browser", width=95)
    gb.configure_column("os",          header_name="OS",      width=90)
    gb.configure_column("device_type", header_name="Device",  width=85)
    gb.configure_column("ip_address",  header_name="IP",      width=120)
    gb.configure_column("url",         header_name="URL",     flex=2, tooltipField="url")
    gb.configure_column("ago",         header_name="Time",    width=100)
    gb.configure_grid_options(
        rowClassRules=row_class_rules,
        getRowId=JsCode("function(p){return String(p.data.id);}"),
    )

    grid_response = aggrid_render(df[display_cols], gb, key="fe_grid", custom_css=custom_css)

    # ── Selection ─────────────────────────────────────────────────────────────
    selected_row = aggrid_get_selected_row(grid_response)
    if selected_row is not None:
        raw_id = selected_row.get("id")
        if raw_id is not None and str(raw_id).strip():
            st.session_state["fe_selected_id"] = str(raw_id)

    # Fallback: scan nodes directly
    if not selected_row and hasattr(grid_response, "grid_response"):
        nodes = grid_response.grid_response.get("nodes", []) if isinstance(grid_response.grid_response, dict) else []
        for node in nodes:
            if node.get("isSelected"):
                raw_id = node.get("data", {}).get("id")
                if raw_id is not None and str(raw_id).strip():
                    st.session_state["fe_selected_id"] = str(raw_id)
                break

    selected_id = st.session_state.get("fe_selected_id")
    if selected_id and selected_id in id_to_event:
        _render_fe_detail(id_to_event[selected_id])
    elif selected_id:
        st.session_state["fe_selected_id"] = None


def _render_fe_detail(event) -> None:
    import streamlit as st
    import streamlit_antd_components as sac
    from ._utils import TYPE_COLOR, time_ago, render_extra_json

    sac.divider(label="Event detail", icon="info-circle", size="xs", color="gray")
    st.subheader(event.message[:120])

    type_color = TYPE_COLOR.get(event.event_type, "blue")
    sac.tags(
        [t for t in [event.event_type, event.browser, event.os] if t],
        color=type_color,
    )

    col1, col2 = st.columns([3, 2])
    with col1:
        if event.stack_trace:
            st.caption("Stack trace")
            st.code(event.stack_trace, language="javascript")
        else:
            sac.alert(label="No stack trace available", color="warning", size="sm")

    with col2:
        request = {k: v for k, v in {
            "url":         event.url,
            "http_method": event.http_method,
            "http_status": event.http_status or None,
            "http_url":    event.http_url,
        }.items() if v}
        if request:
            st.caption("Request")
            st.json(request)

        client = {k: v for k, v in {
            "user_agent":  event.user_agent,
            "ip_address":  event.ip_address,
            "device_type": event.device_type,
            "environment": event.environment,
            "build_id":    event.build_id,
            "time":        time_ago(event.last_seen),
        }.items() if v}
        if client:
            st.caption("Client")
            st.json(client)

        render_extra_json(event.extra)
