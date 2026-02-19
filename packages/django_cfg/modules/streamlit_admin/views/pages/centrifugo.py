"""Centrifugo page view for Streamlit admin."""

import streamlit as st

from models.centrifugo import CentrifugoHealth, ChannelInfo
from models.dashboard import ChangeType, StatCard
from services.centrifugo import CentrifugoService
from views.components.data_table import render_data_table
from views.components.stat_cards import render_stat_cards


def render_centrifugo_page(service: CentrifugoService) -> None:
    """Render Centrifugo management page.

    Args:
        service: CentrifugoService instance for data fetching.
    """
    st.title("Centrifugo WebSocket")

    # Health stats
    health = service.get_health()
    _render_health_stats(health)

    st.divider()

    # Tabs
    tabs = st.tabs(["Channels", "Publishes", "Actions"])

    with tabs[0]:
        _render_channels_tab(service)

    with tabs[1]:
        _render_publishes_tab(service)

    with tabs[2]:
        _render_actions_tab(service)


def _render_health_stats(health: CentrifugoHealth) -> None:
    """Render health statistics row."""
    status_icon = "✅" if health.status == "healthy" else "⚠️"
    cards = [
        StatCard(
            title="Status",
            value=f"{status_icon} {health.status.title()}",
            icon="activity",
            change_type=(
                ChangeType.UP if health.status == "healthy" else ChangeType.DOWN
            ),
        ),
        StatCard(title="Nodes", value=str(health.nodes), icon="server"),
        StatCard(title="Clients", value=str(health.clients), icon="users"),
        StatCard(title="Channels", value=str(health.channels), icon="radio"),
    ]
    render_stat_cards(cards)


def _render_channels_tab(service: CentrifugoService) -> None:
    """Render channels tab content."""
    st.subheader("Active Channels")

    channels = service.get_channels()
    if channels:
        render_data_table(channels)
    else:
        st.info("No active channels")


def _render_publishes_tab(service: CentrifugoService) -> None:
    """Render publishes tab content."""
    st.subheader("Recent Publishes")

    publishes = service.get_publishes(limit=50)
    if publishes:
        render_data_table(publishes)
    else:
        st.info("No recent publishes")


def _render_actions_tab(service: CentrifugoService) -> None:
    """Render actions tab content."""
    st.subheader("Publish Message")

    col1, col2 = st.columns(2)
    with col1:
        channel = st.text_input("Channel", placeholder="user:123")
    with col2:
        message = st.text_area("Message (JSON)", placeholder='{"event": "test"}')

    if st.button("Publish", type="primary", disabled=not channel):
        import json

        try:
            data = json.loads(message) if message else {}
            if service.publish_message(channel, data):
                st.success(f"Published to {channel}")
            else:
                st.error("Failed to publish")
        except json.JSONDecodeError:
            st.error("Invalid JSON")

    st.divider()

    st.subheader("Disconnect User")
    user_id = st.text_input("User ID", placeholder="123")
    if st.button("Disconnect", type="secondary", disabled=not user_id):
        if service.disconnect_user(user_id):
            st.success(f"Disconnected user {user_id}")
        else:
            st.error("Failed to disconnect")
