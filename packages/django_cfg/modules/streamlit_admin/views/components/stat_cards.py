"""Statistics cards component for Streamlit admin."""

import streamlit as st

from models.dashboard import ChangeType, StatCard


def render_stat_cards(cards: list[StatCard], columns: int = 4) -> None:
    """Render statistics cards in a grid.

    Args:
        cards: List of StatCard models to display.
        columns: Number of columns in the grid (default: 4).
    """
    if not cards:
        return

    cols = st.columns(columns)
    for i, card in enumerate(cards):
        with cols[i % columns]:
            _render_card(card)


def _render_card(card: StatCard) -> None:
    """Render a single stat card."""
    delta_color = _get_delta_color(card.change_type)
    st.metric(
        label=card.title,
        value=card.value,
        delta=card.change,
        delta_color=delta_color,
    )


def _get_delta_color(change_type: ChangeType) -> str:
    """Map change type to Streamlit delta color."""
    mapping = {
        ChangeType.UP: "normal",
        ChangeType.DOWN: "inverse",
        ChangeType.NEUTRAL: "off",
    }
    return mapping.get(change_type, "off")
