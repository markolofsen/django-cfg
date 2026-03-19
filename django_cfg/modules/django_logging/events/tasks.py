"""RQ tasks for D1 log event cleanup."""

from __future__ import annotations

import logging

logger = logging.getLogger(__name__)


def cleanup_old_log_events(days: int = 90) -> dict[str, int]:
    """Delete resolved log events older than N days from D1.

    Intended to run as a scheduled RQ task.
    """
    from django_cfg.modules.django_logging import is_enabled, get_service

    if not is_enabled():
        return {"deleted": 0, "skipped": True}

    service = get_service()
    client = service._get_client()
    api_url = service._get_api_url()

    result = client.delete(
        "log_events",
        f"is_resolved = 1 AND last_seen < datetime('now', ? || ' days') AND api_url = ?",
        [f"-{days}", api_url],
    )

    deleted = result.changes
    logger.info(f"Cleaned up {deleted} resolved log events older than {days} days")
    return {"deleted": deleted}


__all__ = ["cleanup_old_log_events"]
