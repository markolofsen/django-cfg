"""
django_monitor — RQ tasks for fire-and-forget D1 sync.

Tasks are enqueued from capture hooks after local PostgreSQL write succeeds.
D1 sync is async — capture never blocks on Cloudflare.
"""

from __future__ import annotations

import logging

logger = logging.getLogger(__name__)


def push_server_event_task(event_id: int) -> None:
    """RQ task: reserved for future dual-write scenarios.

    In D1-only mode capture is synchronous via capture hooks — this task
    is not used in normal operation. Left for compatibility with external callers.
    """
    logger.debug("django_monitor: push_server_event_task called for id=%s (no-op in D1-only mode)", event_id)


def push_frontend_event_task(event_id: int) -> None:
    """RQ task: reserved for future dual-write scenarios.

    In D1-only mode capture is synchronous via capture hooks — this task
    is not used in normal operation. Left for compatibility with external callers.
    """
    logger.debug("django_monitor: push_frontend_event_task called for id=%s (no-op in D1-only mode)", event_id)


# ─────────────────────────────────────────────────────────────────────────────
# Convenience: .delay() shim — works with or without django-rq installed
# ─────────────────────────────────────────────────────────────────────────────

class _Delayable:
    """Wraps a callable and adds a .delay() method for RQ enqueue with sync fallback."""

    def __init__(self, fn) -> None:
        self._fn = fn
        self.__name__ = fn.__name__
        self.__doc__ = fn.__doc__

    def __call__(self, *args, **kwargs):
        return self._fn(*args, **kwargs)

    def delay(self, *args, **kwargs) -> None:
        try:
            import django_rq
            django_rq.get_queue("default").enqueue(self._fn, *args, **kwargs)
        except Exception:
            self._fn(*args, **kwargs)


push_server_event_task = _Delayable(push_server_event_task)
push_frontend_event_task = _Delayable(push_frontend_event_task)


def cleanup_d1_events(
    server_events_days: int = 90,
    frontend_events_days: int = 30,
) -> dict:
    """
    RQ task — delete old resolved server events and old frontend events from D1.

    Args:
        server_events_days: delete resolved server_events older than N days (default 90)
        frontend_events_days: delete frontend_events older than N days (default 30)

    Returns dict with counts of deleted rows (best-effort, D1 may not return affected rows).
    """
    from django_cfg.modules.django_monitor import get_service

    svc = get_service()
    client = svc._get_client()
    result = {}

    try:
        r = client.execute(
            "DELETE FROM server_events WHERE is_resolved = 1 "
            "AND last_seen < datetime('now', ? || ' days')",
            [f"-{server_events_days}"],
        )
        result["server_events_deleted"] = getattr(r, "rows_written", None)
        logger.info("django_monitor: cleanup deleted resolved server_events older than %sd", server_events_days)
    except Exception as exc:
        logger.warning("django_monitor: cleanup server_events failed — %s", exc)
        result["server_events_error"] = str(exc)

    try:
        r = client.execute(
            "DELETE FROM frontend_events WHERE created_at < datetime('now', ? || ' days')",
            [f"-{frontend_events_days}"],
        )
        result["frontend_events_deleted"] = getattr(r, "rows_written", None)
        logger.info("django_monitor: cleanup deleted frontend_events older than %sd", frontend_events_days)
    except Exception as exc:
        logger.warning("django_monitor: cleanup frontend_events failed — %s", exc)
        result["frontend_events_error"] = str(exc)

    return result


cleanup_d1_events = _Delayable(cleanup_d1_events)


__all__ = [
    "push_server_event_task",
    "push_frontend_event_task",
    "cleanup_d1_events",
]
