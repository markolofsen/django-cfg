"""
django_centrifugo — Centrifugo Channels page.

Per-channel stats: total publishes, success rate, avg duration.
Registered via auto_register() as: Centrifugo / Channels.
"""

from __future__ import annotations

_HOURS_OPTIONS: dict[str, int] = {"1h": 1, "6h": 6, "24h": 24, "72h": 72, "168h": 168}


def render_centrifugo_channels() -> None:
    import pandas as pd
    import streamlit as st
    import streamlit_antd_components as sac

    from ..services.d1_query import D1CentrifugoQuery
    from django_cfg.modules.streamlit_admin.core.utils import (
        chip_filter, aggrid_default_builder, aggrid_render, aggrid_get_selected_row,
        time_ago, live_toggle,
    )

    st.title("Centrifugo Channels")

    ctrl_col, range_col = st.columns([1, 4])
    with ctrl_col:
        live_toggle(key="centrifugo_ch_live", interval_ms=60_000)
    with range_col:
        selected_range = chip_filter(
            list(_HOURS_OPTIONS.keys()), key="centrifugo_ch_hours", color="blue",
        )
    hours = _HOURS_OPTIONS.get(selected_range, 24)

    query = D1CentrifugoQuery()

    try:
        rows_raw = query.get_channel_stats(hours=hours)
    except Exception as exc:
        sac.alert(label="Failed to load channels", description=str(exc), color="error")
        return

    if not rows_raw:
        sac.result(label="No channel data", status="empty")
        return

    df = pd.DataFrame(rows_raw)

    # Compute success rate
    if "success_count" in df.columns and "total" in df.columns:
        df["success_rate"] = df.apply(
            lambda r: f"{100 * r['success_count'] // r['total']}%" if r["total"] else "—",
            axis=1,
        )
    else:
        df["success_rate"] = "—"

    if "avg_duration_ms" in df.columns:
        df["avg_ms"] = df["avg_duration_ms"].apply(
            lambda v: f"{int(v)}ms" if v is not None else "—"
        )
    else:
        df["avg_ms"] = "—"

    if "last_publish_at" in df.columns:
        df["last_publish"] = df["last_publish_at"].apply(time_ago)
    else:
        df["last_publish"] = "—"

    display_cols = ["channel", "total", "success_rate", "failed_count", "avg_ms", "last_publish"]
    display_cols = [c for c in display_cols if c in df.columns or c in ("success_rate", "avg_ms", "last_publish")]

    gb = aggrid_default_builder(df[display_cols])
    gb.configure_column("channel",      header_name="Channel",       flex=3)
    gb.configure_column("total",        header_name="Total",         width=80, type=["numericColumn"])
    gb.configure_column("success_rate", header_name="Success %",     width=100)
    gb.configure_column("failed_count", header_name="Failed",        width=80, type=["numericColumn"])
    gb.configure_column("avg_ms",       header_name="Avg Duration",  width=110)
    gb.configure_column("last_publish", header_name="Last publish",  width=120)

    aggrid_render(df[display_cols], gb, key="centrifugo_ch_grid")
