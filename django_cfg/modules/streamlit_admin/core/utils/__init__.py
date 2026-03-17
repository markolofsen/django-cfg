"""
streamlit_admin.core.utils — shared UI helpers for Streamlit pages.

Usage:
    from django_cfg.modules.streamlit_admin.core.utils import (
        time_ago,
        aggrid_default_builder, aggrid_render, aggrid_get_selected_row,
        chip_filter, search_input,
        plotly_dark_layout,
        render_extra_json, live_toggle, kpi_row,
        STATUS_COLORS, EVENT_TYPE_COLORS, CHART_PALETTE,
    )
"""

from .time import time_ago
from .aggrid import aggrid_get_selected_row, aggrid_default_builder, aggrid_render
from .filters import chip_filter, search_input
from .charts import plotly_dark_layout
from .ui import KpiItem, render_extra_json, live_toggle, kpi_row
from .colors import STATUS_COLORS, EVENT_TYPE_COLORS, CHART_PALETTE

__all__ = [
    # time
    "time_ago",
    # aggrid
    "aggrid_get_selected_row",
    "aggrid_default_builder",
    "aggrid_render",
    # filters
    "chip_filter",
    "search_input",
    # charts
    "plotly_dark_layout",
    # ui
    "KpiItem",
    "render_extra_json",
    "live_toggle",
    "kpi_row",
    # colors
    "STATUS_COLORS",
    "EVENT_TYPE_COLORS",
    "CHART_PALETTE",
]
