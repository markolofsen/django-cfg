"""
django_centrifugo.events.service — CentrifugoD1Service.

Pushes CentrifugoLogRow records to Cloudflare D1 (append-only).
Provides read queries for the Streamlit dashboard.

Inherits shared client, api_url resolution, and schema management
from BaseD1Service — no separate credentials needed.
"""

from __future__ import annotations

import logging

from django_cfg.modules.django_cf.core import BaseD1Service
from django_cfg.modules.django_cf.core.d1_query import D1Q

from ..exceptions import DjangoCentrifugoSyncError
from .schema import CENTRIFUGO_LOGS_TABLE, CENTRIFUGO_SCHEMA_STATEMENTS
from .types import CentrifugoLogRow

logger = logging.getLogger(__name__)


class CentrifugoD1Service(BaseD1Service):
    """Handles CentrifugoLogRow sync to Cloudflare D1 (append-only)."""

    def _get_schema_statements(self) -> list[str]:
        return CENTRIFUGO_SCHEMA_STATEMENTS

    # ─────────────────────────────────────────────────────────────────────────
    # Write interface
    # ─────────────────────────────────────────────────────────────────────────

    def insert_log(self, row: CentrifugoLogRow) -> None:
        """Insert a centrifugo log row into D1. Append-only — no deduplication."""
        self._ensure_schema()
        sql, params = D1Q.insert_ignore(CENTRIFUGO_LOGS_TABLE, row)
        try:
            result = self._get_client().execute(sql, params)
            logger.debug(
                "django_centrifugo: log channel=%s status=%s msg=%s (%.1fms)",
                row.channel, row.status, row.message_id, result.duration_ms,
            )
        except Exception as exc:
            raise DjangoCentrifugoSyncError(
                f"django_centrifugo: insert_log failed: {exc}",
                original_error=exc,
            ) from exc

    # ─────────────────────────────────────────────────────────────────────────
    # Read interface (for dashboard)
    # ─────────────────────────────────────────────────────────────────────────

    def get_recent(
        self,
        *,
        limit: int = 200,
        offset: int = 0,
        channel: str | None = None,
        status: str | None = None,
        hours: int = 24,
    ) -> list[dict]:
        """Query recent publish logs for the dashboard."""
        self._ensure_schema()
        where_clause = f"created_at > datetime('now', '-{hours} hours')"
        extra_params: list[str] = []
        if channel:
            where_clause += " AND channel = ?"
            extra_params.append(channel)
        if status:
            where_clause += " AND status = ?"
            extra_params.append(status)
        sql, params = D1Q.select_raw(
            CENTRIFUGO_LOGS_TABLE,
            where_clause=where_clause,
            params=extra_params,
            order_by="created_at DESC",
            limit=limit,
        )
        if offset:
            sql += f" OFFSET {int(offset)}"
        try:
            result = self._get_client().execute(sql, params)
            return result.results or []
        except Exception as exc:
            raise DjangoCentrifugoSyncError(
                f"django_centrifugo: get_recent failed: {exc}",
                original_error=exc,
            ) from exc

    def get_overview_stats(self, *, hours: int = 24) -> dict:
        """Return aggregate KPI counts for the overview dashboard."""
        self._ensure_schema()
        sql = (
            "SELECT "
            "  COUNT(*) AS total, "
            "  SUM(CASE WHEN status='success' THEN 1 ELSE 0 END) AS success_count, "
            "  SUM(CASE WHEN status='failed'  THEN 1 ELSE 0 END) AS failed_count, "
            "  SUM(CASE WHEN status='timeout' THEN 1 ELSE 0 END) AS timeout_count, "
            "  SUM(CASE WHEN status='partial' THEN 1 ELSE 0 END) AS partial_count, "
            "  SUM(CASE WHEN status='pending' THEN 1 ELSE 0 END) AS pending_count, "
            "  AVG(duration_ms) AS avg_duration_ms "
            "FROM centrifugo_logs "
            f"WHERE created_at > datetime('now', '-{hours} hours')"
        )
        try:
            result = self._get_client().execute(sql)
            rows = result.results or []
            return rows[0] if rows else {}
        except Exception as exc:
            raise DjangoCentrifugoSyncError(
                f"django_centrifugo: get_overview_stats failed: {exc}",
                original_error=exc,
            ) from exc

    def get_channel_stats(self, *, hours: int = 24) -> list[dict]:
        """Return per-channel aggregate stats for the channels dashboard."""
        self._ensure_schema()
        sql = (
            "SELECT "
            "  channel, "
            "  COUNT(*) AS total, "
            "  SUM(CASE WHEN status='success' THEN 1 ELSE 0 END) AS success_count, "
            "  SUM(CASE WHEN status='failed'  THEN 1 ELSE 0 END) AS failed_count, "
            "  AVG(duration_ms) AS avg_duration_ms, "
            "  MAX(created_at) AS last_publish_at "
            "FROM centrifugo_logs "
            f"WHERE created_at > datetime('now', '-{hours} hours') "
            "GROUP BY channel "
            "ORDER BY total DESC "
            "LIMIT 200"
        )
        try:
            result = self._get_client().execute(sql)
            return result.results or []
        except Exception as exc:
            raise DjangoCentrifugoSyncError(
                f"django_centrifugo: get_channel_stats failed: {exc}",
                original_error=exc,
            ) from exc

    def get_timeline(self, *, hours: int = 24, bucket: str = "hour") -> list[dict]:
        """Return publish count bucketed by time for the timeline chart.

        Args:
            hours: look-back window
            bucket: 'hour' or 'day' — SQL strftime format string fragment
        """
        self._ensure_schema()
        fmt = "%Y-%m-%dT%H:00" if bucket == "hour" else "%Y-%m-%d"
        sql = (
            f"SELECT strftime('{fmt}', created_at) AS bucket, COUNT(*) AS count "
            "FROM centrifugo_logs "
            f"WHERE created_at > datetime('now', '-{hours} hours') "
            "GROUP BY bucket "
            "ORDER BY bucket ASC"
        )
        try:
            result = self._get_client().execute(sql)
            return result.results or []
        except Exception as exc:
            raise DjangoCentrifugoSyncError(
                f"django_centrifugo: get_timeline failed: {exc}",
                original_error=exc,
            ) from exc

    def get_channels(self, *, hours: int = 24) -> list[str]:
        """Return distinct channel names active within the time window."""
        self._ensure_schema()
        sql = (
            "SELECT DISTINCT channel FROM centrifugo_logs "
            f"WHERE created_at > datetime('now', '-{hours} hours') "
            "ORDER BY channel"
        )
        try:
            result = self._get_client().execute(sql)
            return [r["channel"] for r in (result.results or [])]
        except Exception as exc:
            raise DjangoCentrifugoSyncError(
                f"django_centrifugo: get_channels failed: {exc}",
                original_error=exc,
            ) from exc


__all__ = ["CentrifugoD1Service"]
