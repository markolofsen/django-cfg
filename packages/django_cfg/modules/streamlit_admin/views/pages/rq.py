"""RQ management page view for Streamlit admin."""

import streamlit as st

from models.dashboard import ChangeType, StatCard
from models.rq import QueueStats, WorkerInfo
from services.rq import RQService
from views.components.data_table import render_data_table
from views.components.stat_cards import render_stat_cards

# Try to import streamlit-antd-components for tabs
try:
    import streamlit_antd_components as sac

    HAS_SAC = True
except ImportError:
    HAS_SAC = False


def render_rq_page(service: RQService) -> None:
    """Render RQ management page.

    Args:
        service: RQService instance for data fetching.
    """
    st.title("Redis Queue Management")

    # Stats row
    queues = service.get_queues()
    workers = service.get_workers()
    _render_stats_row(queues, workers)

    st.divider()

    # Tabs
    if HAS_SAC:
        _render_sac_tabs(service, queues, workers)
    else:
        _render_native_tabs(service, queues, workers)


def _render_stats_row(queues: list[QueueStats], workers: list[WorkerInfo]) -> None:
    """Render statistics row."""
    total_jobs = sum(q.count for q in queues)
    total_failed = sum(q.failed for q in queues)

    cards = [
        StatCard(title="Total Queues", value=str(len(queues)), icon="database"),
        StatCard(title="Total Jobs", value=str(total_jobs), icon="list"),
        StatCard(title="Active Workers", value=str(len(workers)), icon="cpu"),
        StatCard(
            title="Failed Jobs",
            value=str(total_failed),
            icon="alert-triangle",
            change_type=ChangeType.DOWN if total_failed > 0 else ChangeType.NEUTRAL,
        ),
    ]
    render_stat_cards(cards)


def _render_sac_tabs(
    service: RQService,
    queues: list[QueueStats],
    workers: list[WorkerInfo],
) -> None:
    """Render tabs using streamlit-antd-components."""
    tab = sac.tabs(
        [
            sac.TabsItem("Queues", icon="database"),
            sac.TabsItem("Workers", icon="cpu"),
            sac.TabsItem("Jobs", icon="list"),
        ]
    )

    if tab == "Queues":
        _render_queues_tab(queues)
    elif tab == "Workers":
        _render_workers_tab(workers)
    elif tab == "Jobs":
        _render_jobs_tab(service)


def _render_native_tabs(
    service: RQService,
    queues: list[QueueStats],
    workers: list[WorkerInfo],
) -> None:
    """Render tabs using native Streamlit."""
    tabs = st.tabs(["Queues", "Workers", "Jobs"])

    with tabs[0]:
        _render_queues_tab(queues)
    with tabs[1]:
        _render_workers_tab(workers)
    with tabs[2]:
        _render_jobs_tab(service)


def _render_queues_tab(queues: list[QueueStats]) -> None:
    """Render queues tab content."""
    st.subheader("Queue Statistics")
    render_data_table(queues)


def _render_workers_tab(workers: list[WorkerInfo]) -> None:
    """Render workers tab content."""
    st.subheader("Active Workers")
    render_data_table(workers)


def _render_jobs_tab(service: RQService) -> None:
    """Render jobs tab content."""
    st.subheader("Job Browser")

    col1, col2 = st.columns(2)
    with col1:
        queue = st.selectbox("Queue", ["default", "high", "low"])
    with col2:
        status = st.selectbox("Status", ["all", "queued", "started", "failed"])

    jobs = service.get_queue_jobs(queue, status)
    selected = render_data_table(jobs, selection=True)

    if selected:
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Cancel Selected", type="secondary"):
                for job in selected:
                    service.cancel_job(job["id"])
                st.rerun()
        with col2:
            if st.button("Requeue Selected", type="primary"):
                for job in selected:
                    service.requeue_job(job["id"])
                st.rerun()
