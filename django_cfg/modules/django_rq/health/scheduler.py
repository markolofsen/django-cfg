"""
RQ scheduler-lag measurement for the queue-health monitor.

rq-scheduler stores scheduled jobs in the ``rq:scheduler:scheduled_jobs`` Redis
sorted set, scored by their next-run UNIX timestamp. The "scheduler lag" is how
far in the past the most-overdue entry is — a large lag means the scheduler is
not enqueueing due jobs on time.
"""

from __future__ import annotations

import time
from typing import Optional

SCHEDULED_JOBS_KEY = "rq:scheduler:scheduled_jobs"


def collect_scheduler_lag(redis_conn) -> Optional[float]:
    """
    Return the lag in seconds of the most-overdue scheduled job.

    Args:
        redis_conn: A Redis connection.

    Returns:
        Lag in seconds (>= 0) for the earliest-scored entry that is in the past,
        ``0.0`` when no scheduled job is overdue, or ``None`` when there are no
        scheduled jobs at all / the ZSET is unavailable.
    """
    try:
        # The lowest score is the soonest (most overdue) scheduled time.
        earliest = redis_conn.zrange(SCHEDULED_JOBS_KEY, 0, 0, withscores=True)
    except Exception:
        return None

    if not earliest:
        return None

    _job_id, score = earliest[0]
    now = time.time()
    lag = now - float(score)
    return max(0.0, lag)


__all__ = [
    "SCHEDULED_JOBS_KEY",
    "collect_scheduler_lag",
]
