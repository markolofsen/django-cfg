"""
django_centrifugo — D1 maintenance task.

cleanup_old_centrifugo_logs() — scheduled daily to purge stale log rows.
"""

from __future__ import annotations

import logging

logger = logging.getLogger(__name__)


def cleanup_old_centrifugo_logs(days: int = 30) -> dict:
    """
    Delete centrifugo_logs older than N days from D1.

    Args:
        days: delete rows older than N days (default 30)

    Returns dict with deletion result (best-effort).
    """
    from django_cfg.modules.django_centrifugo.events.service import CentrifugoD1Service
    from .schema import CENTRIFUGO_LOGS_TABLE

    svc = CentrifugoD1Service()
    client = svc._get_client()
    result = {}

    try:
        r = client.delete(
            CENTRIFUGO_LOGS_TABLE,
            "created_at < datetime('now', ? || ' days')",
            [f"-{days}"],
        )
        result["centrifugo_logs_deleted"] = getattr(r, "rows_written", None)
        logger.info("django_centrifugo: cleanup deleted centrifugo_logs older than %sd", days)
    except Exception as exc:
        logger.warning("django_centrifugo: cleanup centrifugo_logs failed — %s", exc)
        result["centrifugo_logs_error"] = str(exc)

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


cleanup_old_centrifugo_logs = _Delayable(cleanup_old_centrifugo_logs)


__all__ = ["cleanup_old_centrifugo_logs"]
