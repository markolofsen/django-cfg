"""
django_centrifugo — Centrifugo Publishes page.

Paginated publish log with AgGrid + filters (status, channel, date) + detail panel.
Registered via auto_register() as: Centrifugo / Publishes.
"""

from __future__ import annotations

_STATUS_OPTIONS: list[str] = ["All", "success", "failed", "timeout", "partial", "pending"]
_HOURS_OPTIONS:  dict[str, int] = {"1h": 1, "6h": 6, "24h": 24, "72h": 72, "168h": 168}
_STATUS_COLORS:  dict[str, str] = {
    "success": "rgba(34,197,94,0.06)",
    "failed":  "rgba(239,68,68,0.12)",
    "timeout": "rgba(249,115,22,0.12)",
    "partial": "rgba(148,163,184,0.10)",
    "pending": "rgba(59,130,246,0.10)",
}
_DETAIL_STATUS_COLOR: dict[str, str] = {
    "success": "green",
    "failed":  "red",
    "timeout": "orange",
    "partial": "blue",
    "pending": "gray",
}


def render_centrifugo_publishes() -> None:
    import pandas as pd
    import streamlit as st
    import streamlit_antd_components as sac
    from st_aggrid import JsCode

    from ..services.d1_query import D1CentrifugoQuery
    from ..models.d1 import PublishLogRow
    from django_cfg.modules.streamlit_admin.core.utils import (
        chip_filter, aggrid_default_builder, aggrid_render, aggrid_get_selected_row,
        time_ago, live_toggle,
    )

    st.title("Centrifugo Publishes")

    ctrl_col, range_col = st.columns([1, 4])
    with ctrl_col:
        live_toggle(key="centrifugo_pub_live", interval_ms=60_000)
    with range_col:
        selected_range = chip_filter(
            list(_HOURS_OPTIONS.keys()), key="centrifugo_pub_hours", color="blue",
        )
    hours = _HOURS_OPTIONS.get(selected_range, 24)

    query = D1CentrifugoQuery()

    # ── Filters ───────────────────────────────────────────────────────────────
    f_col1, f_col2, f_col3 = st.columns([2, 2, 3])
    with f_col1:
        selected_status = chip_filter(_STATUS_OPTIONS, key="centrifugo_pub_status", color="green")
    with f_col2:
        try:
            channels = ["All"] + query.get_channels(hours=hours)
        except Exception:
            channels = ["All"]
        selected_channel = chip_filter(channels, key="centrifugo_pub_channel", color="orange")
    with f_col3:
        search_msg = st.text_input(
            "Message ID / channel search", placeholder="e.g. user#123",
            key="centrifugo_pub_search", label_visibility="collapsed",
        )

    # ── Fetch ─────────────────────────────────────────────────────────────────
    try:
        rows_raw = query.get_publishes(
            hours=hours,
            limit=300,
            channel=None if selected_channel == "All" else selected_channel,
            status=None if selected_status == "All" else selected_status,
        )
    except Exception as exc:
        sac.alert(label="Failed to load publishes", description=str(exc), color="error")
        return

    if not rows_raw:
        sac.result(label="No publishes found", status="empty")
        return

    # Optional: client-side search filter on message_id / channel
    if search_msg.strip():
        term = search_msg.strip().lower()
        rows_raw = [r for r in rows_raw if term in r.get("channel", "").lower()
                    or term in r.get("message_id", "").lower()]

    rows = [PublishLogRow.from_d1(r) for r in rows_raw]
    df = pd.DataFrame([r.to_display_dict() for r in rows])
    df["ago"] = df["created_at"].apply(time_ago)

    # ── AgGrid ────────────────────────────────────────────────────────────────
    row_class_rules = {f"ag-row-{s}": JsCode(f"function(p){{return p.data.status==='{s}';}}")
                       for s in ("success", "failed", "timeout", "partial", "pending")}
    custom_css = {f".ag-row-{s}": {"background-color": c + " !important"}
                  for s, c in _STATUS_COLORS.items()}

    display_cols = ["_id", "ago", "channel", "status", "ack", "acks", "duration", "message_id"]
    gb = aggrid_default_builder(df[display_cols])
    gb.configure_column("_id",        hide=True)
    gb.configure_column("ago",        header_name="When",      width=110)
    gb.configure_column("channel",    header_name="Channel",   flex=3)
    gb.configure_column("status",     header_name="Status",    width=100)
    gb.configure_column("ack",        header_name="ACK",       width=60)
    gb.configure_column("acks",       header_name="ACKs",      width=65, type=["numericColumn"])
    gb.configure_column("duration",   header_name="Duration",  width=90)
    gb.configure_column("message_id", header_name="Msg ID",    flex=2)
    gb.configure_grid_options(rowClassRules=row_class_rules)

    grid_response = aggrid_render(df[display_cols], gb, key="centrifugo_pub_grid", custom_css=custom_css)

    # ── Detail panel ──────────────────────────────────────────────────────────
    row = aggrid_get_selected_row(grid_response)
    if row:
        selected_id = row.get("_id", "")
        for pub in rows:
            if pub.id == selected_id:
                _render_publish_detail(pub)
                break


def _render_publish_detail(pub: "PublishLogRow") -> None:
    import streamlit as st
    import streamlit_antd_components as sac
    from django_cfg.modules.streamlit_admin.core.utils import time_ago

    sac.divider(label="Publish detail", icon="info-circle", size="xs", color="gray")

    color = _DETAIL_STATUS_COLOR.get(pub.status, "gray")
    sac.tags([pub.status, pub.channel], color=color)
    st.subheader(pub.message_id)

    meta_col, err_col = st.columns([2, 3])
    with meta_col:
        details = {k: v for k, v in {
            "channel":    pub.channel,
            "status":     pub.status,
            "ack_mode":   "wait_for_ack" if pub.wait_for_ack else "fire-and-forget",
            "acks":       pub.acks_received if pub.wait_for_ack else None,
            "duration":   f"{pub.duration_ms}ms" if pub.duration_ms else None,
            "created":    time_ago(pub.created_at),
            "completed":  time_ago(pub.completed_at) if pub.completed_at else None,
            "user_id":    pub.user_id,
            "caller_ip":  pub.caller_ip,
        }.items() if v is not None}
        st.json(details)

    with err_col:
        if pub.error_code:
            st.caption("Error code")
            st.code(pub.error_code)
        if pub.error_message:
            st.caption("Error message")
            st.error(pub.error_message[:500])
