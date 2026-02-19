"""gRPC page view for Streamlit admin."""

import streamlit as st

from models.dashboard import ChangeType, StatCard
from models.grpc import GRPCHealth, ServiceInfo
from services.grpc import GRPCService
from views.components.data_table import render_data_table
from views.components.stat_cards import render_stat_cards


def render_grpc_page(service: GRPCService) -> None:
    """Render gRPC management page.

    Args:
        service: GRPCService instance for data fetching.
    """
    st.title("gRPC Services")

    # Health stats
    health = service.get_health()
    _render_health_stats(health)

    st.divider()

    # Tabs
    tabs = st.tabs(["Services", "Methods", "Errors"])

    with tabs[0]:
        _render_services_tab(service)

    with tabs[1]:
        _render_methods_tab(service)

    with tabs[2]:
        _render_errors_tab(service)


def _render_health_stats(health: GRPCHealth) -> None:
    """Render health statistics row."""
    status_icon = "✅" if health.status == "healthy" else "⚠️"
    error_type = ChangeType.DOWN if health.error_rate > 1 else ChangeType.NEUTRAL

    cards = [
        StatCard(
            title="Status",
            value=f"{status_icon} {health.status.title()}",
            icon="activity",
            change_type=(
                ChangeType.UP if health.status == "healthy" else ChangeType.DOWN
            ),
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


def _render_services_tab(service: GRPCService) -> None:
    """Render services tab content."""
    st.subheader("Registered Services")

    services = service.get_services()
    if services:
        render_data_table(services)
    else:
        st.info("No gRPC services registered")


def _render_methods_tab(service: GRPCService) -> None:
    """Render methods tab content."""
    st.subheader("Method Statistics")

    services = service.get_services()
    if not services:
        st.info("No services available")
        return

    service_names = [s.name for s in services]
    selected = st.selectbox("Select Service", service_names)

    if selected:
        methods = service.get_method_stats(selected)
        if methods:
            render_data_table(methods)
        else:
            st.info("No method statistics available")


def _render_errors_tab(service: GRPCService) -> None:
    """Render errors tab content."""
    st.subheader("Recent Errors")

    errors = service.get_recent_errors(limit=20)
    if errors:
        for error in errors:
            with st.expander(
                f"{error['service']}.{error['method']} - {error['code']}"
            ):
                st.code(error["message"])
                if error["timestamp"]:
                    st.caption(f"Time: {error['timestamp']}")
    else:
        st.success("No recent errors")
