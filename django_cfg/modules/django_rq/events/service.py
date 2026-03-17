"""
django_rq.events.service — RQSyncService.

Pushes RQJobEvent and RQWorkerStats records to Cloudflare D1.
Inherits shared client, api_url resolution, and schema management
from BaseD1Service — no separate credentials needed.
"""

from __future__ import annotations

import logging

from django_cfg.modules.django_cf.core import BaseD1Service
from django_cfg.modules.django_cf.core.d1_query import D1Q

from ..exceptions import DjangoRQSyncError
from .schema import RQ_SCHEMA_STATEMENTS, RQ_JOB_EVENTS_TABLE, RQ_WORKER_HEARTBEATS_TABLE
from .types import RQJobEvent, RQWorkerStats

logger = logging.getLogger(__name__)


class RQSyncService(BaseD1Service):
    """Handles RQJobEvent and RQWorkerStats sync to Cloudflare D1."""

    def _get_schema_statements(self) -> list[str]:
        return RQ_SCHEMA_STATEMENTS

    # ─────────────────────────────────────────────────────────────────────────
    # Write interface
    # ─────────────────────────────────────────────────────────────────────────

    def push_job_event(self, event: RQJobEvent) -> None:
        """Insert a job state change event into D1. Append-only — no deduplication."""
        self._ensure_schema()
        sql, params = D1Q.insert_ignore(RQ_JOB_EVENTS_TABLE, event)
        try:
            result = self._get_client().execute(sql, params)
            logger.debug(
                "django_rq: job_event %s %s job=%s (%.1fms)",
                event.event_type, event.queue, event.job_id, result.duration_ms,
            )
        except Exception as exc:
            raise DjangoRQSyncError(
                f"django_rq: push_job_event failed: {exc}",
                original_error=exc,
            ) from exc

    def push_worker_heartbeat(self, stats: RQWorkerStats) -> None:
        """Insert a worker heartbeat snapshot into D1. Append-only."""
        self._ensure_schema()
        sql, params = D1Q.insert_ignore(RQ_WORKER_HEARTBEATS_TABLE, stats)
        try:
            result = self._get_client().execute(sql, params)
            logger.debug(
                "django_rq: worker_heartbeat worker=%s state=%s (%.1fms)",
                stats.worker_name, stats.state, result.duration_ms,
            )
        except Exception as exc:
            raise DjangoRQSyncError(
                f"django_rq: push_worker_heartbeat failed: {exc}",
                original_error=exc,
            ) from exc

    # ─────────────────────────────────────────────────────────────────────────
    # Read interface (for dashboard)
    # ─────────────────────────────────────────────────────────────────────────

    def get_job_events(
        self,
        *,
        queue: str | None = None,
        status: str | None = None,
        hours: int = 24,
        limit: int = 100,
    ) -> list[dict]:
        """Query recent job events for dashboard."""
        self._ensure_schema()
        where_clause = f"created_at > datetime('now', '-{hours} hours')"
        extra_params: list[str] = []
        if queue:
            where_clause += " AND queue = ?"
            extra_params.append(queue)
        if status:
            where_clause += " AND status = ?"
            extra_params.append(status)
        sql, params = D1Q.select_raw(
            RQ_JOB_EVENTS_TABLE,
            where_clause=where_clause,
            params=extra_params,
            order_by="created_at DESC",
            limit=limit,
        )
        try:
            result = self._get_client().execute(sql, params)
            return result.results or []
        except Exception as exc:
            raise DjangoRQSyncError(
                f"django_rq: get_job_events failed: {exc}",
                original_error=exc,
            ) from exc

    def get_worker_stats(self, *, hours: int = 24) -> list[dict]:
        """Query latest heartbeat per worker for dashboard."""
        self._ensure_schema()
        # Get latest heartbeat per worker within the time window
        sql = (
            "SELECT * FROM rq_worker_heartbeats "
            f"WHERE heartbeat_at > datetime('now', '-{hours} hours') "
            "ORDER BY heartbeat_at DESC "
            "LIMIT 200"
        )
        try:
            result = self._get_client().execute(sql)
            return result.results or []
        except Exception as exc:
            raise DjangoRQSyncError(
                f"django_rq: get_worker_stats failed: {exc}",
                original_error=exc,
            ) from exc


__all__ = ["RQSyncService"]
