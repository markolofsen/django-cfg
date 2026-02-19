"""Dashboard page view for Streamlit admin."""

import streamlit as st

from models.dashboard import QuickAction
from services.dashboard import DashboardService
from views.components.health_radial import render_health_radial
from views.components.metrics_chart import render_metrics_chart
from views.components.stat_cards import render_stat_cards


def render_dashboard_page(service: DashboardService) -> None:
    """Render main dashboard overview page.

    Args:
        service: DashboardService instance for data fetching.
    """
    st.title("Admin Dashboard")

    # Row 1: Statistics Cards
    try:
        cards = service.get_stat_cards()
        render_stat_cards(cards)
    except Exception as e:
        st.error(f"Failed to load stat cards: {e}")

    st.divider()

    # Row 2: Health + Metrics
    col1, col2 = st.columns([1, 2])

    with col1:
        st.subheader("System Health")
        try:
            health = service.get_system_health()
            render_health_radial(health)
        except Exception as e:
            st.error(f"Failed to load health: {e}")

    with col2:
        st.subheader("System Metrics")
        try:
            metrics = service.get_system_metrics()
            render_metrics_chart(metrics)
        except Exception as e:
            st.error(f"Failed to load metrics: {e}")

    st.divider()

    # Row 3: Quick Actions
    st.subheader("Quick Actions")
    try:
        actions = service.get_quick_actions()
        _render_quick_actions(actions)
    except Exception as e:
        st.error(f"Failed to load actions: {e}")


def _render_quick_actions(actions: list[QuickAction]) -> None:
    """Render quick action buttons."""
    cols = st.columns(4)
    for i, action in enumerate(actions):
        with cols[i % 4]:
            if st.button(
                action.label,
                key=f"action_{action.label}",
                use_container_width=True,
            ):
                if action.url:
                    st.session_state.page = action.url
                    st.rerun()
                elif action.action:
                    st.toast(f"Action: {action.action}")
