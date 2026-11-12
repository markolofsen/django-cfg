"""
django-cfg scheduler class for rq-scheduler (``RQ["SCHEDULER_CLASS"]``).

Two changes over ``django_rq.queues.DjangoScheduler``:

1. **No duplicate copies.** A recurring schedule keeps one deterministic job id
   (``schedule_<func>_<hash>``). Stock rq-scheduler pushes that id onto the
   queue on every tick, so behind a busy worker the queue fills with N copies
   of the same id, and they all run back to back once the worker frees up.
   Here a tick that finds the previous copy still waiting in the queue, or
   still running (fresh heartbeat), skips the push and only books the next run.

2. **A tick stamp.** Every scheduler loop writes ``SCHEDULER_TICK_KEY`` (unix
   time). ``health.status.scheduler_status`` reads it, so a healthcheck can
   tell "scheduler dead" from "worker busy, jobs waiting".
"""

from __future__ import annotations

import logging
import time
from datetime import datetime, timezone
from typing import Optional

from django_rq.queues import DjangoScheduler
from rq.job import Job, JobStatus
from rq_scheduler.utils import get_next_scheduled_time, to_unix

logger = logging.getLogger(__name__)

SCHEDULER_TICK_KEY = "djangocfg:rq:scheduler:last_tick"
# A running job whose heartbeat is older than this is treated as abandoned
# (rq refreshes it every job_monitoring_interval, 30 s by default).
RUNNING_HEARTBEAT_FRESH_SEC = 120


def _in_queue(connection, queue_key: str, job_id: str) -> bool:
    """True when ``job_id`` is waiting in the queue list."""
    try:
        return connection.lpos(queue_key, job_id) is not None
    except Exception:
        # LPOS needs Redis >= 6.0.6; fall back to a scan.
        ids = connection.lrange(queue_key, 0, -1)
        return any((i.decode() if isinstance(i, bytes) else i) == job_id for i in ids)


def previous_copy_pending(connection, job: Job, queue_key: str) -> Optional[str]:
    """
    Why the next copy of ``job`` must not be pushed, or None when it may.

    Returns ``"queued"`` when the id still waits in ``queue_key``, ``"running"``
    when the job is started with a fresh heartbeat.
    """
    if _in_queue(connection, queue_key, job.id):
        return "queued"
    try:
        status = job.get_status(refresh=True)
    except Exception:
        return None
    if status == JobStatus.STARTED:
        job.refresh()
        hb = job.last_heartbeat
        if hb is not None:
            if hb.tzinfo is None:
                hb = hb.replace(tzinfo=timezone.utc)
            age = (datetime.now(timezone.utc) - hb).total_seconds()
            if age < RUNNING_HEARTBEAT_FRESH_SEC:
                return "running"
    return None


class DjangoCfgScheduler(DjangoScheduler):
    """rq-scheduler that never stacks copies of one recurring job."""

    def enqueue_jobs(self):
        try:
            self.connection.set(SCHEDULER_TICK_KEY, time.time(), ex=86400)
        except Exception:  # pragma: no cover - a stamp must never stop the loop
            logger.debug("scheduler tick stamp failed", exc_info=True)
        return super().enqueue_jobs()

    def enqueue_job(self, job):
        interval = job.meta.get("interval")
        cron_string = job.meta.get("cron_string")
        if not (interval or cron_string):
            return super().enqueue_job(job)

        queue = self.get_queue_for_job(job)
        reason = previous_copy_pending(self.connection, job, queue.key)
        if reason is None:
            return super().enqueue_job(job)

        # Skip this run, keep the schedule: book the next one, push nothing.
        if interval:
            next_at = to_unix(datetime.utcnow()) + int(interval)
        else:
            next_at = to_unix(get_next_scheduled_time(
                cron_string, use_local_timezone=job.meta.get("use_local_timezone")))
        self.connection.zadd(self.scheduled_jobs_key, {job.id: next_at})
        logger.info(
            "rq scheduler: skipped %s (%s): previous copy still %s in '%s'",
            job.func_name, job.id, reason, queue.name,
            extra={"job_id": job.id, "queue": queue.name, "skip_reason": reason},
        )
        return None


__all__ = [
    "DjangoCfgScheduler",
    "SCHEDULER_TICK_KEY",
    "previous_copy_pending",
]
