"""
Project-specific Streamlit Admin extensions.

This file is loaded automatically when Streamlit admin starts.
Register custom pages here that extend the base admin.

Usage:
    from django_cfg.modules.streamlit_admin import page_registry
    import streamlit as st

    @page_registry.register("My Page", icon="star", group="Custom")
    def render_my_page():
        st.title("My Custom Page")
        st.write("Hello from extension!")
"""

import streamlit as st
# Import from core.registry (relative to streamlit_admin module context)
from core.registry import page_registry


# =============================================================================
# Register Custom Menu Groups
# =============================================================================

# Register a custom group for project-specific pages
page_registry.register_group("Project", icon="briefcase", order=50)


# =============================================================================
# Custom Pages
# =============================================================================

@page_registry.register("Analytics", icon="bar-chart-line", group="Project", order=10)
def render_analytics_page():
    """Analytics dashboard with project metrics."""
    st.title("Analytics")
    st.info("Custom analytics page - add your charts here!")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Users", "1,234", "+12%")
    with col2:
        st.metric("Active Today", "567", "+5%")
    with col3:
        st.metric("Revenue", "$12,345", "+8%")


@page_registry.register("Reports", icon="file-earmark-text", group="Project", order=20)
def render_reports_page():
    """Reports generation page."""
    st.title("Reports")
    st.info("Generate and download reports here!")

    report_type = st.selectbox(
        "Report Type",
        ["Daily Summary", "Weekly Report", "Monthly Analytics"]
    )

    if st.button("Generate Report"):
        st.success(f"Generating {report_type}...")


# =============================================================================
# Example: Top-level page (no group)
# =============================================================================

# @page_registry.register("Quick Actions", icon="lightning", order=5)
# def render_quick_actions():
#     st.title("Quick Actions")
#     if st.button("Sync Data"):
#         st.toast("Syncing...")
