"""
Threshold evaluation for the RQ queue-health monitor.

:func:`evaluate` turns a :class:`QueueMetrics` snapshot plus a
:class:`QueueHealthThresholds` config into a :class:`QueueStatus` — the overall
severity, the list of per-metric breaches, and the ``overflow`` / ``stuck``
booleans used in alert text.

Severity rule: the overall status is the maximum severity across all
per-metric statuses. A queue that is merely deep but actively draining (small
oldest-job age, workers alive) stays healthy — only depth combined with stale
jobs or no workers escalates to critical.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import IntEnum
from typing import List

from django_cfg.models.django.rq_health import QueueHealthThresholds

from .metrics import QueueMetrics


class Severity(IntEnum):
    """Ordered health severity. Higher is worse; ``max()`` gives overall status."""

    HEALTHY = 0
    WARNING = 1
    CRITICAL = 2

    @property
    def label(self) -> str:
        return self.name.lower()


@dataclass
class MetricBreach:
    """A single metric that crossed a warning/critical threshold."""

    metric: str
    value: float
    threshold: float
    severity: Severity

    def as_dict(self) -> dict:
        return {
            "metric": self.metric,
            "value": self.value,
            "threshold": self.threshold,
            "status": self.severity.label,
        }


@dataclass
class QueueStatus:
    """Result of evaluating one queue's metrics against its thresholds."""

    queue: str
    severity: Severity = Severity.HEALTHY
    breaches: List[MetricBreach] = field(default_factory=list)
    overflow: bool = False
    stuck: bool = False
    metrics: QueueMetrics = None  # type: ignore[assignment]

    @property
    def is_healthy(self) -> bool:
        return self.severity == Severity.HEALTHY

    @property
    def label(self) -> str:
        return self.severity.label

    def summary(self) -> str:
        """One-line human summary, e.g. 'crm: critical (stuck) — depth, oldest_job_age'."""
        flags = []
        if self.overflow:
            flags.append("overflow")
        if self.stuck:
            flags.append("stuck")
        flag_str = f" ({', '.join(flags)})" if flags else ""
        breach_str = ", ".join(b.metric for b in self.breaches)
        tail = f" — {breach_str}" if breach_str else ""
        return f"{self.queue}: {self.label}{flag_str}{tail}"


# Depth that is "non-trivial" — below this a queue is never considered stuck,
# regardless of age, so a tiny backlog blip does not page anyone.
_STUCK_MIN_DEPTH = 5


def evaluate(metrics: QueueMetrics, thresholds: QueueHealthThresholds) -> QueueStatus:
    """
    Evaluate a queue's metrics against thresholds.

    Args:
        metrics: Collected :class:`QueueMetrics` for the queue.
        thresholds: :class:`QueueHealthThresholds` to evaluate against.

    Returns:
        A :class:`QueueStatus` with the overall severity, per-metric breaches,
        and the ``overflow`` / ``stuck`` flags.
    """
    status = QueueStatus(queue=metrics.queue, metrics=metrics)
    breaches: List[MetricBreach] = []

    # A collection failure is itself a critical condition (we are blind).
    if metrics.collection_error:
        breaches.append(
            MetricBreach("collection_error", 1, 1, Severity.CRITICAL)
        )

    # --- Depth ---
    if metrics.depth >= thresholds.depth_critical:
        breaches.append(
            MetricBreach("depth", metrics.depth, thresholds.depth_critical, Severity.CRITICAL)
        )
    elif metrics.depth >= thresholds.depth_warning:
        breaches.append(
            MetricBreach("depth", metrics.depth, thresholds.depth_warning, Severity.WARNING)
        )

    # --- Oldest queued job age ---
    age = metrics.oldest_job_age_sec
    if age is not None:
        if age >= thresholds.oldest_job_age_critical_sec:
            breaches.append(
                MetricBreach(
                    "oldest_job_age", age, thresholds.oldest_job_age_critical_sec, Severity.CRITICAL
                )
            )
        elif age >= thresholds.oldest_job_age_warning_sec:
            breaches.append(
                MetricBreach(
                    "oldest_job_age", age, thresholds.oldest_job_age_warning_sec, Severity.WARNING
                )
            )

    # --- Failed count ---
    if metrics.failed_count >= thresholds.failed_count_critical:
        breaches.append(
            MetricBreach(
                "failed_count", metrics.failed_count, thresholds.failed_count_critical, Severity.CRITICAL
            )
        )
    elif metrics.failed_count >= thresholds.failed_count_warning:
        breaches.append(
            MetricBreach(
                "failed_count", metrics.failed_count, thresholds.failed_count_warning, Severity.WARNING
            )
        )

    # --- Worker liveness ---
    # No workers + non-empty queue is always critical. Otherwise a stale
    # heartbeat is a warning.
    if metrics.worker_count == 0 and metrics.depth > 0:
        breaches.append(
            MetricBreach("worker_count", 0, 1, Severity.CRITICAL)
        )
    else:
        hb_age = metrics.worker_heartbeat_age_sec
        if hb_age is not None and hb_age >= thresholds.worker_heartbeat_warning_sec:
            breaches.append(
                MetricBreach(
                    "worker_heartbeat_age", hb_age, thresholds.worker_heartbeat_warning_sec, Severity.WARNING
                )
            )

    # --- Orphan-id ratio ---
    # Only meaningful when we actually sampled some IDs.
    if metrics.orphan_sampled > 0:
        ratio = metrics.orphan_id_ratio
        if ratio >= thresholds.orphan_ratio_critical:
            breaches.append(
                MetricBreach("orphan_id_ratio", ratio, thresholds.orphan_ratio_critical, Severity.CRITICAL)
            )
        elif ratio >= thresholds.orphan_ratio_warning:
            breaches.append(
                MetricBreach("orphan_id_ratio", ratio, thresholds.orphan_ratio_warning, Severity.WARNING)
            )

    # --- Scheduler lag ---
    lag = metrics.scheduler_lag_sec
    if lag is not None:
        if lag >= thresholds.scheduler_lag_critical_sec:
            breaches.append(
                MetricBreach("scheduler_lag", lag, thresholds.scheduler_lag_critical_sec, Severity.CRITICAL)
            )
        elif lag >= thresholds.scheduler_lag_warning_sec:
            breaches.append(
                MetricBreach("scheduler_lag", lag, thresholds.scheduler_lag_warning_sec, Severity.WARNING)
            )

    status.breaches = breaches
    status.severity = max((b.severity for b in breaches), default=Severity.HEALTHY)

    # --- Derived flags ---
    # overflow: depth crossed any depth threshold.
    status.overflow = any(b.metric == "depth" for b in breaches)

    # stuck: a non-trivial backlog that is NOT draining — either the oldest job
    # is over its age threshold, or there are no workers at all.
    age_breach = age is not None and age >= thresholds.oldest_job_age_warning_sec
    no_workers = metrics.worker_count == 0
    status.stuck = metrics.depth >= _STUCK_MIN_DEPTH and (age_breach or no_workers)

    return status


__all__ = [
    "Severity",
    "MetricBreach",
    "QueueStatus",
    "evaluate",
]
