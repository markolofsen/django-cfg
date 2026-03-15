"""System metrics chart component for Streamlit admin."""

import streamlit as st

from models.dashboard import SystemMetrics

# Try to import streamlit-echarts, fallback to native chart
try:
    from streamlit_echarts import st_echarts

    HAS_ECHARTS = True
except ImportError:
    HAS_ECHARTS = False


def render_metrics_chart(metrics: SystemMetrics) -> None:
    """Render system metrics charts.

    Args:
        metrics: SystemMetrics model with timeline data.
    """
    # Always show overview stats (even if zero)
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("RQ Jobs", metrics.rq_total)
    with col2:
        delta = f"{metrics.centrifugo_success_rate:.1f}%" if metrics.centrifugo_total > 0 else None
        st.metric("Centrifugo", metrics.centrifugo_total, delta)
    with col3:
        delta = f"{metrics.grpc_success_rate:.1f}%" if metrics.grpc_total > 0 else None
        st.metric("gRPC", metrics.grpc_total, delta)

    # Timeline chart (only if we have data)
    if metrics.centrifugo_timeline:
        st.subheader("Activity Timeline")
        if HAS_ECHARTS:
            _render_echarts_timeline(metrics)
        else:
            _render_fallback_timeline(metrics)


def _render_echarts_timeline(metrics: SystemMetrics) -> None:
    """Render timeline chart using ECharts."""
    # Use centrifugo timeline as primary
    timeline = metrics.centrifugo_timeline
    timestamps = [p.timestamp for p in timeline]
    successful = [p.successful for p in timeline]
    failed = [p.failed for p in timeline]

    options = {
        "tooltip": {"trigger": "axis"},
        "legend": {
            "data": ["Successful", "Failed"],
            "textStyle": {"color": "#888"},
        },
        "xAxis": {
            "type": "category",
            "data": timestamps,
            "axisLine": {"lineStyle": {"color": "#444"}},
            "axisLabel": {"rotate": 45},
        },
        "yAxis": {
            "type": "value",
            "axisLine": {"lineStyle": {"color": "#444"}},
        },
        "series": [
            {
                "name": "Successful",
                "type": "bar",
                "stack": "total",
                "data": successful,
                "itemStyle": {"color": "#22c55e"},
            },
            {
                "name": "Failed",
                "type": "bar",
                "stack": "total",
                "data": failed,
                "itemStyle": {"color": "#ef4444"},
            },
        ],
    }

    st_echarts(options=options, height="250px")


def _render_fallback_timeline(metrics: SystemMetrics) -> None:
    """Render simple fallback chart using native Streamlit."""
    import pandas as pd

    timeline = metrics.centrifugo_timeline
    data = {
        "timestamp": [p.timestamp for p in timeline],
        "Successful": [p.successful for p in timeline],
        "Failed": [p.failed for p in timeline],
    }
    df = pd.DataFrame(data).set_index("timestamp")
    st.bar_chart(df)
