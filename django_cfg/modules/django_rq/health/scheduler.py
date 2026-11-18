"""
Scheduler-lag measurement for the queue-health monitor.

Two things can be late, and the lag is the worse of them:

- a recurring schedule: the leading ``rqcron`` saves each cron job's
  ``next_enqueue_time`` in its hash (``rq:cron_scheduler:<name>``); an entry in
  the past is overdue;
- a delayed job (``enqueue_in/at``, ``Retry(interval=...)``, a one-off
  ``scheduled_time``): it waits in ``rq:scheduled:<queue>`` scored by its due
  time until a scheduler moves it.

A large lag means nobody is enqueueing due work on time.
"""

from __future__ import annotations

import json
import time

from rq.utils import as_text, utcparse

SCHEDULED_REGISTRY_PATTERN = "rq:scheduled:*"


def _cron_lag(redis_conn, now: float) -> float | None:
    from django_cfg.modules.django_rq.cron import LEADER_KEY

    leader = redis_conn.get(LEADER_KEY)
    if not leader:
        return None
    raw = redis_conn.hget(f"rq:cron_scheduler:{as_text(leader)}", "cron_jobs")
    if not raw:
        return None
    lags = []
    for job in json.loads(as_text(raw)):
        nxt = job.get("next_enqueue_time")
        if nxt:
            lags.append(now - utcparse(nxt).timestamp())
    return max(lags) if lags else None


def _delayed_lag(redis_conn, now: float) -> float | None:
    lags = []
    for key in redis_conn.scan_iter(match=SCHEDULED_REGISTRY_PATTERN):
        earliest = redis_conn.zrange(key, 0, 0, withscores=True)
        if earliest:
            lags.append(now - float(earliest[0][1]))
    return max(lags) if lags else None


def collect_scheduler_lag(redis_conn) -> float | None:
    """
    Return the lag in seconds of the most-overdue cron run or delayed job.

    Returns ``0.0`` when nothing is overdue, ``None`` when there is nothing to
    measure (no leading ``rqcron`` and no delayed job) or Redis is unavailable.
    """
    now = time.time()
    try:
        found = [lag for lag in (_cron_lag(redis_conn, now), _delayed_lag(redis_conn, now)) if lag is not None]
    except Exception:
        return None
    if not found:
        return None
    return max(0.0, max(found))


__all__ = ["SCHEDULED_REGISTRY_PATTERN", "collect_scheduler_lag"]
