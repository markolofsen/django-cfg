"""
django_rq — RQ module for django-cfg.

Full replacement for apps/integrations/rq/. All RQ logic lives here:
- Services (Redis): job_service, cancellation, config_helper, rq_converters
- Tasks: maintenance, demo_tasks
- Management commands: rqworker, rqworker_pool, rqscheduler, rqstats, rq_cleanup_locks
- D1 persistence: job events + worker heartbeats via Cloudflare D1
- Streamlit dashboard: RQ Overview, RQ Jobs, RQ Workers

Data storage:
- Redis  — real-time state (queues, workers, active jobs)
- D1     — historical events (rq_job_events, rq_worker_heartbeats)

No PostgreSQL used.

Usage — connect hooks at startup:
    from django_cfg.modules.django_rq.capture import connect_rq_hooks
    connect_rq_hooks()

Or use AppConfig (DjangoRQMetricsConfig) which calls connect_rq_hooks() in ready().
"""

from __future__ import annotations

default_app_config = "django_cfg.modules.django_rq.apps.DjangoRQMetricsConfig"

from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from .events.service import RQSyncService

from .exceptions import DjangoRQConfigError, DjangoRQError, DjangoRQSyncError

_service_instance: Optional["RQSyncService"] = None


def is_enabled() -> bool:
    """Return True when django_cf is configured and ready."""
    try:
        from django_cfg.modules.django_cf import is_ready
        return is_ready()
    except Exception:
        return False


def get_service() -> "RQSyncService":
    """Return (cached) RQSyncService instance.

    Raises DjangoRQConfigError if django_cf is not configured.
    """
    global _service_instance
    if _service_instance is None:
        if not is_enabled():
            raise DjangoRQConfigError(
                "django_rq: django_cf is not configured",
                suggestion="Add CloudflareConfig(enabled=True, ...) to DjangoConfig",
            )
        from .events.service import RQSyncService
        _service_instance = RQSyncService()
    return _service_instance


def reset_service() -> None:
    """Reset cached service instance (useful in tests)."""
    global _service_instance
    _service_instance = None


__all__ = [
    # Exceptions
    "DjangoRQError",
    "DjangoRQConfigError",
    "DjangoRQSyncError",
    # Helpers
    "is_enabled",
    "get_service",
    "reset_service",
]
