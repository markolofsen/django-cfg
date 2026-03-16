"""
django_monitor — Users dashboard (synced from Django via django_cf).

Registered via auto_register() as: Monitor / Users.
"""

from __future__ import annotations


def render_users() -> None:
    import streamlit as st
    import streamlit_antd_components as sac
    import streamlit_shadcn_ui as ui

    from ..services.d1_query import D1MonitorQuery
    from ._utils import (
        aggrid_default_builder, aggrid_render, aggrid_get_selected_row,
        project_selectbox,
    )

    st.title("Users")
    query = D1MonitorQuery()

    # ── Filters ───────────────────────────────────────────────────────────────
    col1, col2, col3 = st.columns([2, 2, 3])
    with col1:
        projects = query.get_projects()
        api_url = project_selectbox(projects, key="usr_project")
    with col2:
        status_filter = st.selectbox("Status", ["All", "Active", "Inactive"], key="usr_status") or "All"
    with col3:
        search = st.text_input("Search", placeholder="email, name, company…", key="usr_search")

    is_active: bool | None = None
    if status_filter == "Active":
        is_active = True
    elif status_filter == "Inactive":
        is_active = False

    # ── Stats ─────────────────────────────────────────────────────────────────
    stats = query.get_user_stats(api_url=api_url)
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        ui.metric_card(title="Total users", content=str(stats.total), description="all time")
    with c2:
        ui.metric_card(title="Active", content=str(stats.active), description="is_active=1")
    with c3:
        ui.metric_card(title="Inactive", content=str(stats.inactive), description="disabled")
    with c4:
        ui.metric_card(title="Projects", content=str(stats.projects), description="in D1")

    sac.divider(label="Users", icon="people", size="xs", color="gray")

    # ── Fetch ─────────────────────────────────────────────────────────────────
    users = query.get_users(
        api_url=api_url,
        is_active=is_active,
        search=search.strip() if search else None,
        limit=500,
    )

    if not users:
        sac.result(label="No users found", description="Try adjusting the filters", status="empty")
        return

    # ── DataFrame ─────────────────────────────────────────────────────────────
    import pandas as pd
    from st_aggrid import JsCode

    df = pd.DataFrame([u.to_display_dict() for u in users])

    row_class_rules = {
        "ag-row-inactive": JsCode("function(p){return p.data.status==='⛔ inactive';}"),
    }
    custom_css = {
        ".ag-row-inactive": {"opacity": "0.45"},
    }

    gb = aggrid_default_builder(df)
    gb.configure_column("status",      header_name="Status",   width=110, pinned="left")
    gb.configure_column("email",       header_name="Email",    flex=2)
    gb.configure_column("name",        header_name="Name",     flex=1)
    gb.configure_column("company",     header_name="Company",  flex=1)
    gb.configure_column("position",    header_name="Position", flex=1)
    gb.configure_column("phone",       header_name="Phone",    width=130)
    gb.configure_column("date_joined", header_name="Joined",   width=100)
    gb.configure_column("synced_at",   header_name="Synced",   width=130)
    gb.configure_grid_options(rowClassRules=row_class_rules)

    grid_response = aggrid_render(df, gb, key="usr_grid", custom_css=custom_css)

    # ── Detail panel ──────────────────────────────────────────────────────────
    row = aggrid_get_selected_row(grid_response)
    if row:
        email = row.get("email", "")
        user = next((u for u in users if u.email == email), None)
        if user:
            sac.divider(label="User detail", icon="person", size="xs", color="gray")
            col_a, col_b = st.columns(2)
            with col_a:
                st.caption("Profile")
                st.json({
                    "id": user.id,
                    "email": user.email,
                    "name": user.full_name,
                    "company": user.company,
                    "position": user.position,
                    "phone": user.phone or "—",
                    "is_active": user.is_active,
                })
            with col_b:
                st.caption("Timestamps")
                st.json({
                    "date_joined": user.date_joined,
                    "updated_at": user.updated_at,
                    "synced_at": user.synced_at,
                    "api_url": user.api_url,
                })
