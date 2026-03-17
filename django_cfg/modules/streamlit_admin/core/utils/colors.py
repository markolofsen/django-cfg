"""Color palettes for Streamlit pages."""

from __future__ import annotations

# RQ job/worker status colors (for AgGrid row coloring and charts)
STATUS_COLORS: dict[str, str] = {
    "finished":  "#22c55e",
    "failed":    "#ef4444",
    "queued":    "#94a3b8",
    "started":   "#3b82f6",
    "busy":      "#3b82f6",
    "suspended": "#f97316",
    "idle":      "#94a3b8",
}

# Event type colors for django_monitor (sac.tags, chip colors)
EVENT_TYPE_COLORS: dict[str, str] = {
    "SERVER_ERROR":          "red",
    "SLOW_QUERY":            "orange",
    "RQ_FAILURE":            "volcano",
    "OOM_KILL":              "magenta",
    "LOG_ERROR":             "gold",
    "UNHANDLED_EXCEPTION":   "red",
    "JS_ERROR":              "red",
    "NETWORK_ERROR":         "orange",
    "ERROR":                 "volcano",
    "WARNING":               "gold",
    "CONSOLE":               "blue",
    "PAGE_VIEW":             "green",
    "PERFORMANCE":           "cyan",
}

# General chart color sequence (plotly)
CHART_PALETTE: list[str] = [
    "#3b82f6", "#8b5cf6", "#06b6d4", "#22c55e",
    "#f97316", "#ef4444", "#eab308", "#ec4899",
]

__all__ = ["STATUS_COLORS", "EVENT_TYPE_COLORS", "CHART_PALETTE"]
