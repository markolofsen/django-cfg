"""
django_rq — RQ module for django-cfg.

Full replacement for apps/integrations/rq/. All RQ logic lives here:
- Services (Redis): job_service, cancellation, config_helper, rq_converters
- Tasks: maintenance, demo_tasks
- Management commands: rqworker, rqworker_pool, rqscheduler, rqstats, rq_cleanup_locks

Data storage:
- Redis — real-time state (queues, workers, active jobs)

Job failures are captured by django_monitor (JSONL + Telegram alerts).
"""

from __future__ import annotations

default_app_config = "django_cfg.modules.django_rq.apps.DjangoRQMetricsConfig"

from .exceptions import DjangoRQConfigError, DjangoRQError, DjangoRQSyncError


__all__ = [
    # Exceptions
    "DjangoRQError",
    "DjangoRQConfigError",
    "DjangoRQSyncError",
]
