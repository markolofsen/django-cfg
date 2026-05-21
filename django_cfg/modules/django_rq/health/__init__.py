"""
RQ queue-health monitor for django-cfg.

A periodic check that collects per-queue metrics (depth, oldest-job age, failed
count, worker liveness, scheduler lag, orphan-id ratio), evaluates them against
:class:`~django_cfg.models.django.rq_health.QueueHealthThresholds`, and raises
Telegram alerts when a queue degrades.

Public API:

- :class:`QueueHealthMonitor` — orchestrates one check cycle.
- :func:`run_queue_health_check` — scheduled-task entry point.
- :class:`QueueMetrics` / :func:`collect_queue_metrics` — metric collection.
- :class:`QueueStatus` / :class:`Severity` / :func:`evaluate` — evaluation.

The monitor runs automatically when ``DjangoRQConfig.health.enabled`` is True
and is also exposed as the ``rq_health_check`` management command.
"""

from __future__ import annotations

from .evaluator import MetricBreach, QueueStatus, Severity, evaluate
from .metrics import QueueMetrics, collect_queue_metrics
from .monitor import QueueHealthMonitor
from .tasks import run_queue_health_check

__all__ = [
    "QueueHealthMonitor",
    "run_queue_health_check",
    "QueueMetrics",
    "collect_queue_metrics",
    "QueueStatus",
    "Severity",
    "MetricBreach",
    "evaluate",
]
