"""
django_monitor.events.service — MonitorSyncService.

Pushes ServerEvent and FrontendEvent records to Cloudflare D1.
Inherits shared client, api_url resolution, and schema management
from BaseD1Service — no separate credentials needed.
"""

from __future__ import annotations

import logging
from typing import Any

from django_cfg.modules.django_cf.core import BaseD1Service
from django_cfg.modules.django_cf.core.d1_query import D1Q

from ..capture.notify import notify_server_event
from ..exceptions import MonitorConfigError, MonitorSyncError
from .schema import MONITOR_SCHEMA_STATEMENTS, SERVER_EVENTS_TABLE, FRONTEND_EVENTS_TABLE
from .types import ServerEventSyncData

logger = logging.getLogger(__name__)


class MonitorSyncService(BaseD1Service):
    """Handles ServerEvent and FrontendEvent sync to Cloudflare D1."""

    def _get_schema_statements(self) -> list[str]:
        return MONITOR_SCHEMA_STATEMENTS

    # ─────────────────────────────────────────────────────────────────────────
    # Public interface
    # ─────────────────────────────────────────────────────────────────────────

    def push_server_event(self, event: Any) -> None:
        """Upsert a ServerEvent into D1 (dedup by fingerprint + api_url)."""
        self._ensure_schema()
        try:
            api_url = self._get_api_url()
        except Exception as exc:
            raise MonitorConfigError(
                "django_monitor: cannot resolve api_url",
                original_error=exc,
            ) from exc

        data = ServerEventSyncData.from_event(event, api_url)
        sql, params = D1Q.upsert_increment(
            SERVER_EVENTS_TABLE,
            data,
            increment_col="occurrence_count",
            reset_cols={"is_resolved": "0"},
        )
        try:
            result = self._get_client().execute(sql, params)
            logger.debug(
                "django_monitor: server_event %s @ %s (count+1, %.1fms)",
                data.fingerprint, api_url, result.duration_ms,
            )
        except Exception as exc:
            raise MonitorSyncError(
                f"django_monitor: push_server_event failed: {exc}",
                original_error=exc,
            ) from exc

        notify_server_event(
            data.event_type,
            data.message,
            {},
            fingerprint=data.fingerprint,
            api_url=data.api_url,
        )

    def push_frontend_event(self, event: Any) -> None:
        """Upsert a single FrontendEvent into D1. Prefer push_frontend_events_batch for multiple."""
        self.push_frontend_events_batch([event])

    def push_frontend_events_batch(self, events: list[Any]) -> None:
        """Upsert multiple FrontendEvents in a single SQL statement (one HTTP request).

        Error-type events increment occurrence_count on conflict.
        Append-only types (PAGE_VIEW, PERFORMANCE) have a UUID fingerprint
        so they always create new rows.
        """
        if not events:
            return
        self._ensure_schema()
        sql, params = D1Q.upsert_increment_batch(
            FRONTEND_EVENTS_TABLE,
            events,
            increment_col="occurrence_count",
        )
        try:
            result = self._get_client().execute(sql, params)
            logger.debug(
                "django_monitor: frontend_events batch=%d (%.1fms)",
                len(events), result.duration_ms,
            )
        except Exception as exc:
            raise MonitorSyncError(
                f"django_monitor: push_frontend_events_batch failed: {exc}",
                original_error=exc,
            ) from exc


__all__ = ["MonitorSyncService"]
