"""Filter widget helpers for Streamlit pages."""

from __future__ import annotations

from typing import Any


def chip_filter(
    options: list[str],
    *,
    key: str,
    color: str = "blue",
    variant: str = "outline",
) -> str:
    """Render a sac.chip filter and return the selected option string.

    Always returns a str — never int or None.
    index=0 → first option selected by default.
    """
    import streamlit_antd_components as sac
    idx = sac.chip(
        items=options,
        index=0,
        size="sm",
        radius="md",
        variant=variant,
        color=color,
        key=key,
    )
    if isinstance(idx, int):
        return options[idx]
    if isinstance(idx, str):
        return idx
    return options[0]


def search_input(
    placeholder: str = "Search...",
    *,
    key: str,
    label: str = "",
) -> str:
    """Render a text search input. Returns stripped string (never None)."""
    import streamlit as st
    value = st.text_input(
        label or placeholder,
        placeholder=placeholder,
        key=key,
        label_visibility="collapsed" if not label else "visible",
    )
    return (value or "").strip()


__all__ = ["chip_filter", "search_input"]
