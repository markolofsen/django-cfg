"""Plotly chart helpers for Streamlit pages."""

from __future__ import annotations

try:
    from plotly.graph_objects import Figure as _Figure
except ImportError:  # plotly not installed (non-Streamlit context)
    from typing import Any as _Figure  # type: ignore[assignment]


def plotly_dark_layout(fig: "_Figure", *, height: int = 220, title: str = "") -> "_Figure":
    """Apply project-standard dark layout to a plotly figure. Returns the figure."""
    fig.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font_color="#EDEDED",
        margin=dict(l=0, r=0, t=30 if title else 10, b=0),
        height=height,
    )
    fig.update_xaxes(showgrid=False, tickangle=-30)
    fig.update_yaxes(gridcolor="rgba(255,255,255,0.08)")
    return fig


__all__ = ["plotly_dark_layout"]
