"""
django_rq — RQ tasks for D1 maintenance.

cleanup_old_rq_events() — scheduled daily at 3am via RQScheduleConfig.
"""

from __future__ import annotations

import logging

logger = logging.getLogger(__name__)


def cleanup_old_rq_events(days: int = 30) -> dict:
    """
    RQ task — delete rq_job_events older than N days from D1.

    Args:
        days: delete events older than N days (default 30)

    Returns dict with deletion result (best-effort).
    """
    from django_cfg.modules.django_rq import get_service
    from .schema import RQ_JOB_EVENTS_TABLE, RQ_WORKER_HEARTBEATS_TABLE

    svc = get_service()
    client = svc._get_client()
    result = {}

    try:
        r = client.delete(
            RQ_JOB_EVENTS_TABLE,
            "created_at < datetime('now', ? || ' days')",
            [f"-{days}"],
        )
        result["rq_job_events_deleted"] = getattr(r, "rows_written", None)
        logger.info("django_rq: cleanup deleted rq_job_events older than %sd", days)
    except Exception as exc:
        logger.warning("django_rq: cleanup rq_job_events failed — %s", exc)
        result["rq_job_events_error"] = str(exc)

    # Keep worker heartbeats for 7 days (shorter retention)
    heartbeat_days = min(days, 7)
    try:
        r = client.delete(
            RQ_WORKER_HEARTBEATS_TABLE,
            "heartbeat_at < datetime('now', ? || ' days')",
            [f"-{heartbeat_days}"],
        )
        result["rq_worker_heartbeats_deleted"] = getattr(r, "rows_written", None)
        logger.info("django_rq: cleanup deleted rq_worker_heartbeats older than %sd", heartbeat_days)
    except Exception as exc:
        logger.warning("django_rq: cleanup rq_worker_heartbeats failed — %s", exc)
        result["rq_worker_heartbeats_error"] = str(exc)

    return result


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


cleanup_old_rq_events = _Delayable(cleanup_old_rq_events)


__all__ = ["cleanup_old_rq_events"]
