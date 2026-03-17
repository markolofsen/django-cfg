"""
django_centrifugo — Centrifugo Overview page.

KPI cards + publish timeline + status breakdown.
Registered via auto_register() as: Centrifugo / Overview.
"""

from __future__ import annotations

_HOURS_OPTIONS: dict[str, int] = {"1h": 1, "6h": 6, "24h": 24, "72h": 72, "168h": 168}
_STATUS_COLORS: dict[str, str] = {
    "success": "rgba(34,197,94,0.12)",
    "failed":  "rgba(239,68,68,0.12)",
    "timeout": "rgba(249,115,22,0.12)",
    "partial": "rgba(148,163,184,0.12)",
    "pending": "rgba(59,130,246,0.10)",
}


def render_centrifugo_overview() -> None:
    import streamlit as st
    import streamlit_antd_components as sac

    from ..services.d1_query import D1CentrifugoQuery
    from django_cfg.modules.streamlit_admin.core.utils import (
        chip_filter, kpi_row, KpiItem, live_toggle,
    )

    st.title("Centrifugo Overview")

    ctrl_col, range_col = st.columns([1, 4])
    with ctrl_col:
        live_toggle(key="centrifugo_overview_live", interval_ms=60_000)
    with range_col:
        selected_range = chip_filter(
            list(_HOURS_OPTIONS.keys()), key="centrifugo_overview_hours", color="blue",
        )
    hours = _HOURS_OPTIONS.get(selected_range, 24)

    query = D1CentrifugoQuery()

    try:
        stats = query.get_overview(hours=hours)
    except Exception as exc:
        sac.alert(label="Failed to load overview", description=str(exc), color="error")
        return

    if not stats:
        sac.result(label="No data", description="No publish logs found", status="empty")
        return

    total       = stats.get("total", 0) or 0
    success     = stats.get("success_count", 0) or 0
    failed      = stats.get("failed_count", 0) or 0
    timeout     = stats.get("timeout_count", 0) or 0
    pending     = stats.get("pending_count", 0) or 0
    avg_ms      = stats.get("avg_duration_ms")
    success_pct = f"{100 * success // total}%" if total else "—"

    kpi_row([
        KpiItem(title="Total publishes",  content=str(total),     description=f"Last {hours}h"),
        KpiItem(title="Success rate",     content=success_pct,    description=f"{success} succeeded"),
        KpiItem(title="Failed",           content=str(failed),    description=f"{timeout} timeout"),
        KpiItem(title="Avg duration",     content=f"{int(avg_ms)}ms" if avg_ms else "—", description="per publish"),
        KpiItem(title="Pending",          content=str(pending),   description="awaiting completion"),
    ])

    # ── Timeline ──────────────────────────────────────────────────────────────
    try:
        import pandas as pd
        import plotly.express as px
        from django_cfg.modules.streamlit_admin.core.utils import plotly_dark_layout

        bucket = "hour" if hours <= 72 else "day"
        timeline = query.get_timeline(hours=hours, bucket=bucket)
        if timeline:
            df = pd.DataFrame(timeline)
            fig = px.bar(
                df, x="bucket", y="count",
                title=f"Publishes per {'hour' if bucket == 'hour' else 'day'} (last {hours}h)",
                color_discrete_sequence=["#22c55e"],
                labels={"bucket": "", "count": "Publishes"},
            )
            st.plotly_chart(plotly_dark_layout(fig, height=220), use_container_width=True)
    except Exception:
        pass

    # ── Status breakdown ──────────────────────────────────────────────────────
    try:
        import pandas as pd
        import plotly.express as px
        from django_cfg.modules.streamlit_admin.core.utils import plotly_dark_layout

        status_data = {k: v for k, v in {
            "success": success, "failed": failed,
            "timeout": timeout, "pending": pending,
        }.items() if v}
        if status_data:
            df_s = pd.DataFrame({"status": list(status_data.keys()), "count": list(status_data.values())})
            fig2 = px.pie(
                df_s, names="status", values="count",
                title="Status distribution",
                color="status",
                color_discrete_map={
                    "success": "#22c55e", "failed": "#ef4444",
                    "timeout": "#f97316", "pending": "#3b82f6",
                },
            )
            col1, col2 = st.columns([1, 2])
            with col1:
                st.plotly_chart(plotly_dark_layout(fig2, height=260), use_container_width=True)
    except Exception:
        pass
