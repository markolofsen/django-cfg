"""LogSyncService — push log events to D1."""

from __future__ import annotations

import logging

from django_cfg.modules.django_cf.core import BaseD1Service, D1Q

from .schema import LOG_EVENTS_TABLE, SCHEMA_STATEMENTS
from .types import LogEventSyncData

logger = logging.getLogger(__name__)


class LogSyncService(BaseD1Service):
    """Push structured log events to D1 with upsert-increment dedup."""

    def _get_schema_statements(self) -> list[str]:
        return SCHEMA_STATEMENTS

    def push_log_event(self, data: LogEventSyncData) -> None:
        """Upsert a log event — increments occurrence_count on duplicate fingerprint."""
        self._ensure_schema()
        client = self._get_client()
        sql, params = D1Q.upsert_increment(
            LOG_EVENTS_TABLE,
            data,
            increment_col="occurrence_count",
            reset_cols=["last_seen", "stack_trace", "extra"],
        )
        client.execute(sql, params)

    def get_stats(self) -> dict[str, int]:
        """Return event counts by level."""
        self._ensure_schema()
        client = self._get_client()
        api_url = self._get_api_url()
        sql, params = D1Q.group_by(
            LOG_EVENTS_TABLE,
            select_expr="level, COUNT(*) as count, SUM(occurrence_count) as total",
            group_by="level",
            where_clause="api_url = ?",
            params=[api_url],
        )
        result = client.execute(sql, params)
        return {row["level"]: row["total"] for row in (result.results or [])}


__all__ = ["LogSyncService"]
