"""
Cron-vs-worker status for healthchecks.

One read of Redis that answers "why is my scheduled job late?":

- ``cron_dead``: no ``rqcron`` process has sent a heartbeat to RQ's cron
  scheduler registry (``rq:cron_schedulers``) within ``max_heartbeat_age``.
- ``starved``: cron is alive, but a queue's oldest job has waited longer than
  ``max_wait``; ``busy`` names what the workers are running instead.
- ``ok`` otherwise.

``python manage.py rq_cron_status`` prints it and exits 1 when not ok, so a
compose healthcheck can use it directly.
"""

from __future__ import annotations

import time
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Iterable, List, Optional



@dataclass
class QueueWait:
    queue: str
    depth: int
    wait_sec: Optional[float]  # age of the oldest queued job (enqueued_at)


@dataclass
class BusyWorker:
    worker: str
    queues: List[str]
    job_id: Optional[str]
    func: Optional[str]
    running_sec: Optional[float]


@dataclass
class CronStatus:
    verdict: str  # "ok" | "cron_dead" | "starved"
    cron_alive: bool
    heartbeat_age_sec: Optional[float]  # newest rqcron heartbeat
    leader: Optional[str] = None  # the rqcron that enqueues (others are standby)
    queues: List[QueueWait] = field(default_factory=list)
    busy: List[BusyWorker] = field(default_factory=list)
    reason: str = ""

    def as_dict(self) -> dict:
        return asdict(self)


def _s(v) -> str:
    return v.decode() if isinstance(v, bytes) else v


def _age(dt: Optional[datetime]) -> Optional[float]:
    if dt is None:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return max(0.0, (datetime.now(timezone.utc) - dt).total_seconds())


def _heartbeat_age(conn) -> Optional[float]:
    """Age of the newest heartbeat in RQ's cron scheduler registry, None when empty."""
    from rq import cron_scheduler_registry

    newest = conn.zrange(cron_scheduler_registry.get_registry_key(), -1, -1, withscores=True)
    if not newest:
        return None
    return max(0.0, time.time() - float(newest[0][1]))


def _leader(conn) -> Optional[str]:
    from django_cfg.modules.django_rq.cron import LEADER_KEY

    raw = conn.get(LEADER_KEY)
    return _s(raw) if raw else None


class UnknownQueueError(ValueError):
    """A queue asked for is not declared in ``RQ_QUEUES``."""

    def __init__(self, unknown: List[str], declared: List[str]):
        self.unknown, self.declared = unknown, declared
        super().__init__(
            f"unknown RQ queue {', '.join(repr(q) for q in unknown)}; "
            f"declared: {', '.join(declared) or 'none'}"
        )


def cron_status(
    queue_names: Optional[Iterable[str]] = None,
    max_heartbeat_age: float = 120.0,
    max_wait: float = 120.0,
    connection=None,
) -> CronStatus:
    """
    Read cron liveness, per-queue wait and busy workers.

    Args:
        queue_names: queues to judge (default: every queue in ``RQ_QUEUES``).
        max_heartbeat_age: seconds without an ``rqcron`` heartbeat before ``cron_dead``.
        max_wait: seconds a queued job may wait before ``starved``.
        connection: Redis connection (default: django_rq's for the first queue).

    Raises:
        UnknownQueueError: a name in ``queue_names`` is not in ``RQ_QUEUES``.
    """
    import django_rq
    from django.conf import settings
    from rq import Worker

    declared = list(getattr(settings, "RQ_QUEUES", None) or {})
    if queue_names:
        names = list(queue_names)
        unknown = [n for n in names if n not in declared]
        if unknown:
            raise UnknownQueueError(unknown, declared)
    else:
        names = declared
    queues = [django_rq.get_queue(n) for n in names]
    conn = connection or queues[0].connection

    hb_age = _heartbeat_age(conn)
    alive = hb_age is not None and hb_age <= max_heartbeat_age

    waits: List[QueueWait] = []
    for q in queues:
        depth = len(q)
        wait = None
        if depth:
            jobs = q.get_jobs(0, 1)
            if jobs:
                wait = _age(getattr(jobs[0], "enqueued_at", None) or jobs[0].created_at)
        waits.append(QueueWait(queue=q.name, depth=depth, wait_sec=wait))

    busy: List[BusyWorker] = []
    seen = set()
    for q in queues:
        for w in Worker.all(queue=q):
            if w.name in seen:
                continue
            seen.add(w.name)
            job = w.get_current_job()
            if job is None:
                continue
            busy.append(BusyWorker(
                worker=w.name,
                queues=w.queue_names(),
                job_id=job.id,
                func=job.func_name,
                running_sec=_age(job.started_at),
            ))

    status = CronStatus(
        verdict="ok", cron_alive=alive, heartbeat_age_sec=hb_age, leader=_leader(conn),
        queues=waits, busy=busy,
    )
    if hb_age is None:
        status.verdict, status.reason = "cron_dead", "no rqcron heartbeat in rq:cron_schedulers"
    elif not alive:
        status.verdict, status.reason = "cron_dead", f"last rqcron heartbeat {hb_age:.0f}s ago"
    else:
        late = [w for w in waits if w.wait_sec is not None and w.wait_sec > max_wait]
        if late:
            jobs = ", ".join(f"{b.func} {b.running_sec or 0:.0f}s" for b in busy) or "no busy worker"
            status.verdict = "starved"
            status.reason = (
                "; ".join(f"{w.queue} waits {w.wait_sec:.0f}s ({w.depth} queued)" for w in late)
                + f"; workers busy: {jobs}"
            )
    return status


__all__ = ["BusyWorker", "CronStatus", "QueueWait", "UnknownQueueError", "cron_status"]
