"""
django_grpc.events.tasks — D1 maintenance tasks.

cleanup_old_grpc_request_logs() — purge old request log rows

Wrapped with _Delayable so it can be enqueued via RQ:
    tasks.cleanup_old_grpc_request_logs.delay()
Or called directly (synchronous fallback):
    tasks.cleanup_old_grpc_request_logs()

Scheduled via DjangoGrpcModuleConfig.schedules (3am daily).

Removed: cleanup_old_grpc_connection_data() — deleted together with
grpc_connection_states / grpc_connection_events / grpc_connection_metrics
tables. Those tables were always empty because the write path
(services/connection_state/ CAS manager) was dead code.
"""

from __future__ import annotations

import logging

logger = logging.getLogger(__name__)


def cleanup_old_grpc_request_logs(days: int = 90) -> dict:
    """Delete grpc_request_logs rows older than N days.

    Args:
        days: retention period in days (default 90)

    Returns dict with deletion stats (best-effort).
    """
    from django_cfg.modules.django_grpc.events.service import GrpcD1Service

    svc = GrpcD1Service()
    client = svc._get_client()
    result = {}

    try:
        r = client.execute(
            f"DELETE FROM grpc_request_logs "
            f"WHERE created_at < datetime('now', '-{int(days)} days')"
        )
        result["grpc_request_logs_deleted"] = getattr(r, "rows_written", None)
        logger.info("django_grpc: cleanup deleted request_logs older than %sd", days)
    except Exception as exc:
        logger.warning("django_grpc: cleanup request_logs failed — %s", exc)
        result["grpc_request_logs_error"] = str(exc)

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


cleanup_old_grpc_request_logs = _Delayable(cleanup_old_grpc_request_logs)

# cleanup_old_grpc_connection_data removed — the 3 connection tables it
# cleaned up were dropped (always empty, write path was dead code).

__all__ = [
    "cleanup_old_grpc_request_logs",
]
