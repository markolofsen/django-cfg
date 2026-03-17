"""
django_rq.streamlit.services.d1_query — read-only D1 queries for RQ Streamlit pages.

Works both inside Django (reads CloudflareConfig) and standalone Streamlit process
(reads credentials from CLOUDFLARE__ACCOUNT_ID / CLOUDFLARE__API_TOKEN /
CLOUDFLARE__D1_DATABASE_ID environment variables).
"""

from __future__ import annotations

import os
from typing import Any

from django_cfg.modules.django_cf.core import BaseD1Service
from django_cfg.modules.django_cf.core.client import CloudflareD1Client
from django_cfg.modules.django_cf.core.d1_query import D1Q
from django_cfg.modules.django_rq.events.schema import (
    RQ_JOB_EVENTS_TABLE,
    RQ_WORKER_HEARTBEATS_TABLE,
)


class D1RQQuery(BaseD1Service):
    """Read-only D1 query service for RQ Streamlit pages."""

    def _get_client(self) -> CloudflareD1Client:
        """Build D1 client from Django config or env vars (Streamlit standalone mode)."""
        try:
            return super()._get_client()
        except Exception:
            pass

        account_id = os.environ.get("CLOUDFLARE__ACCOUNT_ID", "")
        api_token = os.environ.get("CLOUDFLARE__API_TOKEN", "")
        database_id = os.environ.get("CLOUDFLARE__D1_DATABASE_ID", "")
        if not (account_id and api_token and database_id):
            raise RuntimeError(
                "Cloudflare D1 credentials not found. "
                "Set CLOUDFLARE__ACCOUNT_ID, CLOUDFLARE__API_TOKEN, CLOUDFLARE__D1_DATABASE_ID."
            )
        return CloudflareD1Client(
            account_id=account_id,
            api_token=api_token,
            database_id=database_id,
        )

    # ── Job events ────────────────────────────────────────────────────────────

    def get_job_events(
        self,
        *,
        queue: str | None = None,
        status: str | None = None,
        func_name: str | None = None,
        hours: int = 24,
        limit: int = 200,
    ) -> list[dict[str, Any]]:
        """Fetch job events with optional filters."""
        where_parts = [f"created_at > datetime('now', '-{hours} hours')"]
        params: list[Any] = []
        if queue:
            where_parts.append("queue = ?")
            params.append(queue)
        if status:
            where_parts.append("status = ?")
            params.append(status)
        if func_name:
            where_parts.append("func_name = ?")
            params.append(func_name)
        sql, safe_params = D1Q.select_raw(
            RQ_JOB_EVENTS_TABLE,
            where_clause=" AND ".join(where_parts),
            params=params,
            order_by="created_at DESC",
            limit=limit,
        )
        return list(self._get_client().execute(sql, safe_params).results or [])

    def get_job_event_stats(self, *, hours: int = 24) -> dict[str, Any]:
        """Aggregate KPI stats for the overview page."""
        sql, params = D1Q.aggregate(
            RQ_JOB_EVENTS_TABLE,
            expressions=[
                "COUNT(*) as total",
                "SUM(CASE WHEN status='finished' THEN 1 ELSE 0 END) as finished",
                "SUM(CASE WHEN status='failed' THEN 1 ELSE 0 END) as failed",
                "SUM(CASE WHEN status='queued' THEN 1 ELSE 0 END) as queued",
                "ROUND(AVG(CASE WHEN duration_seconds IS NOT NULL THEN duration_seconds END), 2) as avg_duration",
            ],
            where_clause=f"created_at > datetime('now', '-{hours} hours')",
        )
        rows = self._get_client().execute(sql, params).results or [{}]
        return rows[0]

    def get_job_events_timeline(self, *, hours: int = 24) -> list[dict[str, Any]]:
        """Job events grouped by hour and status — for bar chart."""
        sql, params = D1Q.group_by(
            RQ_JOB_EVENTS_TABLE,
            select_expr="strftime('%Y-%m-%d %H:00', created_at) as hour, status, COUNT(*) as count",
            group_by="hour, status",
            where_clause=f"created_at > datetime('now', '-{hours} hours')",
            order_by="hour",
        )
        return list(self._get_client().execute(sql, params).results or [])

    def get_queue_breakdown(self, *, hours: int = 24) -> list[dict[str, Any]]:
        """Job counts grouped by queue and status."""
        sql, params = D1Q.group_by(
            RQ_JOB_EVENTS_TABLE,
            select_expr="queue, status, COUNT(*) as count",
            group_by="queue, status",
            where_clause=f"created_at > datetime('now', '-{hours} hours')",
            order_by="count DESC",
        )
        return list(self._get_client().execute(sql, params).results or [])

    def get_func_name_breakdown(self, *, hours: int = 24, limit: int = 20) -> list[dict[str, Any]]:
        """Top N functions by total runs."""
        sql, params = D1Q.group_by(
            RQ_JOB_EVENTS_TABLE,
            select_expr="func_name, status, COUNT(*) as count",
            group_by="func_name, status",
            where_clause=f"created_at > datetime('now', '-{hours} hours')",
            order_by="count DESC",
            limit=limit,
        )
        return list(self._get_client().execute(sql, params).results or [])

    # ── Worker heartbeats ─────────────────────────────────────────────────────

    def get_latest_worker_stats(self) -> list[dict[str, Any]]:
        """Latest heartbeat per worker (subquery on MAX(heartbeat_at))."""
        sql = (
            "SELECT w.* FROM rq_worker_heartbeats w "
            "INNER JOIN ("
            "  SELECT worker_name, MAX(heartbeat_at) as latest "
            "  FROM rq_worker_heartbeats GROUP BY worker_name"
            ") latest ON w.worker_name = latest.worker_name AND w.heartbeat_at = latest.latest"
        )
        return list(self._get_client().execute(sql).results or [])

    def get_worker_timeline(
        self,
        *,
        worker_name: str | None = None,
        hours: int = 24,
    ) -> list[dict[str, Any]]:
        """Heartbeat history for uptime chart."""
        where_parts = [f"heartbeat_at > datetime('now', '-{hours} hours')"]
        params: list[Any] = []
        if worker_name:
            where_parts.append("worker_name = ?")
            params.append(worker_name)
        sql, safe_params = D1Q.select_raw(
            RQ_WORKER_HEARTBEATS_TABLE,
            where_clause=" AND ".join(where_parts),
            params=params,
            order_by="heartbeat_at DESC",
            limit=500,
        )
        return list(self._get_client().execute(sql, safe_params).results or [])

    def get_queues(self) -> list[str]:
        """Distinct queue names for filter dropdowns."""
        sql, params = D1Q.group_by(
            RQ_JOB_EVENTS_TABLE,
            select_expr="queue",
            group_by="queue",
            order_by="queue",
        )
        rows = self._get_client().execute(sql, params).results or []
        return [r["queue"] for r in rows if r.get("queue")]

    def get_func_names(self) -> list[str]:
        """Distinct func_name values for filter dropdowns."""
        sql, params = D1Q.group_by(
            RQ_JOB_EVENTS_TABLE,
            select_expr="func_name",
            group_by="func_name",
            order_by="func_name",
        )
        rows = self._get_client().execute(sql, params).results or []
        return [r["func_name"] for r in rows if r.get("func_name")]


__all__ = ["D1RQQuery"]
