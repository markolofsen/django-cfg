"""Charts page for Streamlit admin."""

import streamlit as st

from services.charts import ChartsService

# Try to import streamlit-echarts for better charts
try:
    from streamlit_echarts import st_echarts

    HAS_ECHARTS = True
except ImportError:
    HAS_ECHARTS = False


def render_charts_page(service: ChartsService) -> None:
    """Render the charts page."""
    st.title("Analytics Charts")

    # Period selector
    col1, col2 = st.columns([1, 4])
    with col1:
        days = st.selectbox("Period", [7, 14, 30, 60, 90], index=2, format_func=lambda x: f"{x} days")

    st.divider()

    # Activity and Registrations charts
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("User Activity")
        activity_data = service.get_activity_chart(days=days)
        if activity_data:
            _render_line_chart(activity_data, "activity")
        else:
            st.info("No activity data available")

    with col2:
        st.subheader("User Registrations")
        reg_data = service.get_registrations_chart(days=days)
        if reg_data:
            _render_bar_chart(reg_data, "registrations")
        else:
            st.info("No registration data available")

    st.divider()

    # Activity Tracker (GitHub-style)
    st.subheader("Activity Tracker")
    col1, col2 = st.columns([1, 4])
    with col1:
        weeks = st.selectbox("Weeks", [4, 8, 12, 24, 52], index=2)

    tracker_data = service.get_activity_tracker(weeks=weeks)
    if tracker_data:
        _render_activity_tracker(tracker_data)
    else:
        st.info("No tracker data available")

    st.divider()

    # Recent Users table
    st.subheader("Recent Users")
    col1, col2 = st.columns([1, 4])
    with col1:
        limit = st.selectbox("Show", [5, 10, 20, 50], index=1)

    recent_users = service.get_recent_users(limit=limit)
    if recent_users:
        _render_users_table(recent_users)
    else:
        st.info("No recent users")


def _render_line_chart(data, key: str) -> None:
    """Render line chart using ECharts or fallback."""
    if HAS_ECHARTS and data.datasets:
        ds = data.datasets[0]
        options = {
            "tooltip": {"trigger": "axis"},
            "xAxis": {
                "type": "category",
                "data": data.labels,
                "axisLabel": {"rotate": 45},
            },
            "yAxis": {"type": "value"},
            "series": [
                {
                    "name": ds.get("label", "Activity"),
                    "type": "line",
                    "data": ds.get("data", []),
                    "smooth": True,
                    "areaStyle": {"opacity": 0.3},
                    "itemStyle": {"color": ds.get("borderColor", "#0070F3")},
                }
            ],
        }
        st_echarts(options=options, height="300px", key=key)
    else:
        _render_fallback_chart(data, key)


def _render_bar_chart(data, key: str) -> None:
    """Render bar chart using ECharts or fallback."""
    if HAS_ECHARTS and data.datasets:
        ds = data.datasets[0]
        options = {
            "tooltip": {"trigger": "axis"},
            "xAxis": {
                "type": "category",
                "data": data.labels,
                "axisLabel": {"rotate": 45},
            },
            "yAxis": {"type": "value"},
            "series": [
                {
                    "name": ds.get("label", "Registrations"),
                    "type": "bar",
                    "data": ds.get("data", []),
                    "itemStyle": {"color": ds.get("backgroundColor", "#22c55e")},
                }
            ],
        }
        st_echarts(options=options, height="300px", key=key)
    else:
        _render_fallback_chart(data, key)


def _render_fallback_chart(data, key: str) -> None:
    """Render simple chart using native Streamlit."""
    import pandas as pd

    if not data.datasets:
        st.info("No data")
        return

    ds = data.datasets[0]
    df = pd.DataFrame({"date": data.labels, "value": ds.get("data", [])}).set_index("date")
    st.line_chart(df)


def _render_activity_tracker(tracker_data: list) -> None:
    """Render GitHub-style activity tracker."""
    if HAS_ECHARTS:
        # Convert to heatmap format
        data = [[d.date, d.count] for d in tracker_data]
        colors = list(set(d.color for d in tracker_data))

        options = {
            "tooltip": {
                "formatter": lambda params: f"{params['data'][0]}: {params['data'][1]} activities"
            },
            "visualMap": {
                "min": 0,
                "max": max(d.count for d in tracker_data) if tracker_data else 10,
                "calculable": True,
                "orient": "horizontal",
                "left": "center",
                "bottom": "0%",
                "inRange": {"color": ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353"]},
            },
            "calendar": {
                "top": 50,
                "left": 30,
                "right": 30,
                "cellSize": ["auto", 15],
                "range": [tracker_data[-1].date if tracker_data else "2024-01-01", tracker_data[0].date if tracker_data else "2024-12-31"],
                "itemStyle": {"borderWidth": 2, "borderColor": "#1a1a1a"},
                "yearLabel": {"show": False},
                "dayLabel": {"color": "#888"},
                "monthLabel": {"color": "#888"},
            },
            "series": [
                {
                    "type": "heatmap",
                    "coordinateSystem": "calendar",
                    "data": data,
                }
            ],
        }
        st_echarts(options=options, height="200px", key="tracker")
    else:
        # Fallback: simple metrics
        total = sum(d.count for d in tracker_data)
        active_days = sum(1 for d in tracker_data if d.count > 0)
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Activities", total)
        with col2:
            st.metric("Active Days", active_days)
        with col3:
            st.metric("Avg per Day", f"{total / len(tracker_data):.1f}" if tracker_data else "0")


def _render_users_table(users: list) -> None:
    """Render recent users table."""
    import pandas as pd

    data = [
        {
            "ID": u.id,
            "Username": u.username,
            "Email": u.email,
            "Joined": u.date_joined[:10] if u.date_joined else "",
            "Active": "✓" if u.is_active else "✗",
            "Last Login": u.last_login[:10] if u.last_login else "Never",
        }
        for u in users
    ]
    df = pd.DataFrame(data)
    st.dataframe(df, use_container_width=True, hide_index=True)
