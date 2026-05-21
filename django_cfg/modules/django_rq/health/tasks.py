"""
RQ task entry point for the queue-health monitor.

:func:`run_queue_health_check` is the function ``DjangoRQConfig.get_all_schedules()``
registers as a periodic scheduled job. It is a thin wrapper around
:class:`QueueHealthMonitor` and returns a JSON-friendly summary dict.
"""

from __future__ import annotations

from typing import Dict

from django_cfg.utils import get_logger

from .monitor import QueueHealthMonitor

logger = get_logger("rq.health")


def run_queue_health_check(dry_run: bool = False) -> Dict[str, object]:
    """
    Run one RQ queue-health check cycle.

    This is the scheduled-task entry point — registered automatically when
    ``DjangoRQConfig.health.enabled`` is True.

    Args:
        dry_run: When True, evaluate and log but do not send Telegram alerts
            and do not prune orphan IDs.

    Returns:
        A summary dict (checked / healthy / warning / critical counts, alerts
        sent, etc.). Never raises.
    """
    monitor = QueueHealthMonitor(dry_run=dry_run)
    return monitor.run()


__all__ = [
    "run_queue_health_check",
]
