"""
Per-queue metric collection for the RQ queue-health monitor.

``collect_queue_metrics`` reads a single queue's live state from Redis/RQ and
returns a plain :class:`QueueMetrics` dataclass. It never raises — on failure
it returns a ``QueueMetrics`` with ``collection_error`` set so the caller can
still log/alert sensibly.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import List, Optional

from django_cfg.utils import get_logger

from .scheduler import collect_scheduler_lag

logger = get_logger("rq.health")


@dataclass
class QueueMetrics:
    """
    Live health metrics for a single RQ queue.

    All ``*_age_sec`` / ``*_lag_sec`` values are non-negative seconds. ``None``
    means the metric could not be determined (e.g. no jobs, no workers).
    """

    queue: str

    # Depth
    depth: int = 0

    # Oldest queued job age (seconds)
    oldest_job_age_sec: Optional[float] = None

    # Failed registry size
    failed_count: int = 0

    # Worker liveness
    worker_count: int = 0
    worker_heartbeat_age_sec: Optional[float] = None

    # Scheduler lag (most-overdue scheduled job, seconds)
    scheduler_lag_sec: Optional[float] = None

    # Orphan-id ratio: sampled queued IDs whose rq:job:<id> hash is missing
    orphan_id_ratio: float = 0.0
    orphan_sampled: int = 0
    orphan_missing: int = 0
    orphan_missing_ids: List[str] = field(default_factory=list)

    # Set when collection failed; metrics above are then best-effort/defaults
    collection_error: Optional[str] = None

    def as_context(self) -> dict:
        """Return a compact dict suitable for Telegram context / log extra."""
        ctx: dict = {
            "queue": self.queue,
            "depth": self.depth,
            "failed": self.failed_count,
            "workers": self.worker_count,
            "orphan_ratio": round(self.orphan_id_ratio, 3),
        }
        if self.oldest_job_age_sec is not None:
            ctx["oldest_job_age_sec"] = round(self.oldest_job_age_sec, 1)
        if self.worker_heartbeat_age_sec is not None:
            ctx["worker_heartbeat_age_sec"] = round(self.worker_heartbeat_age_sec, 1)
        if self.scheduler_lag_sec is not None:
            ctx["scheduler_lag_sec"] = round(self.scheduler_lag_sec, 1)
        if self.collection_error:
            ctx["collection_error"] = self.collection_error
        return ctx


def _aware(dt: datetime) -> datetime:
    """Coerce a naive datetime to UTC-aware."""
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt


def _age_seconds(dt: Optional[datetime]) -> Optional[float]:
    """Return age of ``dt`` in seconds (clamped >= 0), or None."""
    if dt is None:
        return None
    now = datetime.now(timezone.utc)
    delta = (now - _aware(dt)).total_seconds()
    return max(0.0, delta)


def _collect_orphan_ratio(redis_conn, queue_name: str, sample_size: int) -> tuple[float, int, int, List[str]]:
    """
    Sample up to ``sample_size`` queued job IDs and check ``rq:job:<id>`` existence.

    Returns ``(ratio, sampled, missing, missing_ids)``. An "orphan" is a queued
    ID whose job hash has TTL-expired or never existed.
    """
    queue_key = f"rq:queue:{queue_name}"
    try:
        raw_ids = redis_conn.lrange(queue_key, 0, max(0, sample_size - 1))
    except Exception as exc:  # pragma: no cover - defensive
        logger.warning(f"orphan sample failed for queue '{queue_name}': {exc}")
        return 0.0, 0, 0, []

    ids = [k.decode("utf-8") if isinstance(k, bytes) else k for k in raw_ids]
    if not ids:
        return 0.0, 0, 0, []

    missing_ids: List[str] = []
    for job_id in ids:
        try:
            exists = redis_conn.exists(f"rq:job:{job_id}")
        except Exception:  # pragma: no cover - defensive
            exists = True  # treat unknowable as present, do not over-report
        if not exists:
            missing_ids.append(job_id)

    sampled = len(ids)
    missing = len(missing_ids)
    ratio = missing / sampled if sampled else 0.0
    return ratio, sampled, missing, missing_ids


def collect_queue_metrics(queue_name: str, orphan_sample_size: int = 200) -> QueueMetrics:
    """
    Collect live health metrics for a single queue.

    Args:
        queue_name: Name of the queue to inspect.
        orphan_sample_size: Number of queued IDs to sample for the orphan ratio.

    Returns:
        A :class:`QueueMetrics`. Never raises — failures set ``collection_error``.
    """
    metrics = QueueMetrics(queue=queue_name)

    try:
        import django_rq
        from rq import Worker

        queue = django_rq.get_queue(queue_name)
        redis_conn = queue.connection

        # Depth
        metrics.depth = len(queue)

        # Oldest queued job age — use ``enqueued_at`` (time the job entered
        # *this* queue), not ``created_at`` (time the Job object was first
        # instantiated). For RQ-scheduled periodic jobs ``created_at`` is
        # frozen at scheduler-startup time, so the metric would falsely
        # report an age of "process uptime" on every fire. ``enqueued_at``
        # reflects the current iteration. Falls back to ``created_at`` only
        # for one-shot legacy jobs that pre-date ``enqueued_at`` being set.
        if metrics.depth > 0:
            try:
                jobs = queue.get_jobs(0, 1)
                if jobs:
                    job = jobs[0]
                    ref_ts = getattr(job, "enqueued_at", None) or job.created_at
                    metrics.oldest_job_age_sec = _age_seconds(ref_ts)
            except Exception as exc:
                logger.warning(f"oldest-job lookup failed for '{queue_name}': {exc}")

        # Failed registry
        try:
            metrics.failed_count = len(queue.failed_job_registry)
        except Exception as exc:
            logger.warning(f"failed-registry lookup failed for '{queue_name}': {exc}")

        # Worker liveness
        try:
            workers = Worker.all(queue=queue)
            metrics.worker_count = len(workers)
            heartbeats = [w.last_heartbeat for w in workers if w.last_heartbeat]
            if heartbeats:
                newest = max(_aware(hb) for hb in heartbeats)
                metrics.worker_heartbeat_age_sec = max(
                    0.0, (datetime.now(timezone.utc) - newest).total_seconds()
                )
        except Exception as exc:
            logger.warning(f"worker lookup failed for '{queue_name}': {exc}")

        # Scheduler lag (global, but reported per-queue for context)
        try:
            metrics.scheduler_lag_sec = collect_scheduler_lag(redis_conn)
        except Exception as exc:
            logger.warning(f"scheduler-lag lookup failed for '{queue_name}': {exc}")

        # Orphan-id ratio
        ratio, sampled, missing, missing_ids = _collect_orphan_ratio(
            redis_conn, queue_name, orphan_sample_size
        )
        metrics.orphan_id_ratio = ratio
        metrics.orphan_sampled = sampled
        metrics.orphan_missing = missing
        metrics.orphan_missing_ids = missing_ids

    except Exception as exc:
        metrics.collection_error = str(exc)
        logger.error(
            f"failed to collect metrics for queue '{queue_name}': {exc}",
            exc_info=True,
            extra={"queue": queue_name, "metric": "collection", "status": "critical"},
        )

    return metrics


__all__ = [
    "QueueMetrics",
    "collect_queue_metrics",
]
