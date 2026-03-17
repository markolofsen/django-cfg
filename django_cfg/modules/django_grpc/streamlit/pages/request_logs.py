"""
gRPC Request Logs page — paginated request logs with filters.
"""

from __future__ import annotations

import streamlit as st

try:
    from core.utils import chip_filter, search_input, time_ago, live_toggle
    _HAS_UTILS = True
except ImportError:
    _HAS_UTILS = False


def _monitoring():
    from django_cfg.modules.django_grpc.services.monitoring.monitoring import MonitoringService
    return MonitoringService()


def render_grpc_request_logs() -> None:
    st.title("gRPC Request Logs")

    if _HAS_UTILS:
        live_toggle(interval=15, key="grpc_logs_live")

    # ── Filters ───────────────────────────────────────────────────
    col1, col2, col3, col4 = st.columns([3, 2, 2, 2])
    with col1:
        svc_query = search_input("Service…", key="grpc_logs_svc") if _HAS_UTILS else st.text_input("Service", key="grpc_logs_svc")
    with col2:
        status_filter = (
            chip_filter(["all", "success", "error"], key="grpc_logs_status", default="all")
            if _HAS_UTILS else "all"
        )
    with col3:
        hours = st.selectbox(
            "Window",
            options=[1, 6, 24, 48, 168],
            index=2,
            format_func=lambda h: {1: "1h", 6: "6h", 24: "24h", 48: "2d", 168: "7d"}[h],
            label_visibility="collapsed",
            key="grpc_logs_hours",
        )
    with col4:
        limit = st.selectbox("Show", [20, 50, 100, 200], key="grpc_logs_limit")

    # ── Data ──────────────────────────────────────────────────────
    try:
        rows = _monitoring().get_recent_requests(
            service_name=svc_query or None,
            status_filter=status_filter if status_filter != "all" else None,
            hours=hours,
            limit=limit,
        )
    except Exception as exc:
        st.error(f"Failed to load logs: {exc}")
        rows = []

    st.caption(f"Showing {len(rows)} records")

    if not rows:
        st.info("No requests found for the selected filters")
        return

    import pandas as pd
    df = pd.DataFrame(rows)

    # Prettify timestamps
    if "created_at" in df.columns and _HAS_UTILS:
        df["ago"] = df["created_at"].apply(lambda x: time_ago(x) if x else "—")

    display_cols = [c for c in [
        "service_name", "method_name", "status", "duration_ms",
        "ago" if _HAS_UTILS else "created_at",
        "peer_address",
    ] if c in df.columns]

    st.dataframe(df[display_cols], use_container_width=True, hide_index=True)

    # ── Detail expander ────────────────────────────────────────────
    with st.expander("Row Detail"):
        row_idx = st.number_input("Row index", min_value=0, max_value=max(0, len(rows) - 1),
                                  step=1, key="grpc_logs_row_idx")
        if rows and 0 <= row_idx < len(rows):
            st.json(rows[int(row_idx)])
