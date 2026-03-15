"""System page view for Streamlit admin."""

import streamlit as st

from services.system import SystemService
from views.components.health_radial import render_health_radial
from views.components.stat_cards import render_stat_cards


def render_system_page(service: SystemService) -> None:
    """Render system health page.

    Args:
        service: SystemService instance for data fetching.
    """
    st.title("System Health")

    # Stats row
    stats = service.get_overview_stats()
    render_stat_cards(stats)

    st.divider()

    # Health section
    col1, col2 = st.columns([1, 2])

    with col1:
        st.subheader("Overall Health")
        health = service.get_system_health()
        render_health_radial(health)

    with col2:
        st.subheader("Component Status")
        for component in health.components:
            _render_component_status(component)

    st.divider()

    # Refresh button
    if st.button("🔄 Refresh", use_container_width=True):
        st.rerun()


def _render_component_status(component) -> None:
    """Render single component status."""
    status_colors = {
        "healthy": "🟢",
        "warning": "🟡",
        "error": "🔴",
    }
    icon = status_colors.get(component.status.value, "⚪")

    col1, col2, col3 = st.columns([1, 2, 3])
    with col1:
        st.write(icon)
    with col2:
        st.write(f"**{component.name}**")
    with col3:
        st.caption(component.message or "")
