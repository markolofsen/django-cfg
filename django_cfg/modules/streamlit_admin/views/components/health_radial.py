"""System health radial gauge component for Streamlit admin."""

import streamlit as st

from models.dashboard import HealthStatus, SystemHealth

# Try to import streamlit-echarts, fallback to simple display
try:
    from streamlit_echarts import st_echarts

    HAS_ECHARTS = True
except ImportError:
    HAS_ECHARTS = False


def render_health_radial(health: SystemHealth) -> None:
    """Render system health radial gauge.

    Args:
        health: SystemHealth model with percentage and status.
    """
    if HAS_ECHARTS:
        _render_echarts_gauge(health)
    else:
        _render_fallback(health)

    _render_status_badge(health.status)


def _render_echarts_gauge(health: SystemHealth) -> None:
    """Render gauge using ECharts."""
    color = _get_health_color(health.status)

    options = {
        "series": [
            {
                "type": "gauge",
                "startAngle": 90,
                "endAngle": -270,
                "pointer": {"show": False},
                "progress": {
                    "show": True,
                    "overlap": False,
                    "roundCap": True,
                    "clip": False,
                    "itemStyle": {"color": color},
                },
                "axisLine": {"lineStyle": {"width": 20, "color": [[1, "#2a2a2a"]]}},
                "splitLine": {"show": False},
                "axisTick": {"show": False},
                "axisLabel": {"show": False},
                "data": [{"value": health.percentage}],
                "title": {"show": False},
                "detail": {"fontSize": 32, "color": color, "formatter": "{value}%"},
            }
        ]
    }

    st_echarts(options=options, height="250px")


def _render_fallback(health: SystemHealth) -> None:
    """Render simple fallback when ECharts unavailable."""
    color = _get_health_color(health.status)
    st.markdown(
        f"<div style='text-align:center;font-size:48px;color:{color}'>"
        f"{health.percentage:.0f}%</div>",
        unsafe_allow_html=True,
    )


def _render_status_badge(status: HealthStatus | str) -> None:
    """Render status badge below gauge."""
    status_str = _status_to_str(status)
    color = _get_health_color(status)
    label = status_str.upper()

    st.markdown(
        f"<div style='text-align:center'>"
        f"<span style='background:{color};padding:4px 12px;border-radius:4px;"
        f"color:white;font-size:12px'>{label}</span></div>",
        unsafe_allow_html=True,
    )


def _status_to_str(status: HealthStatus | str) -> str:
    """Convert status to string."""
    if isinstance(status, str):
        return status
    return status.value


def _get_health_color(status: HealthStatus | str) -> str:
    """Get color for health status."""
    status_str = _status_to_str(status)
    colors = {
        "healthy": "#22c55e",
        "warning": "#eab308",
        "error": "#ef4444",
    }
    return colors.get(status_str.lower(), "#6b7280")
