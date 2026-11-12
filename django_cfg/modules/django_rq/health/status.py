"""
Scheduler-vs-worker status for healthchecks.

One read of Redis that answers "why is my scheduled job late?":

- ``scheduler_dead``: no live ``rq:scheduler_instance:*`` key, or the last
  scheduler tick (``DjangoCfgScheduler``) is older than ``max_tick_age``.
- ``starved``: the scheduler ticks, but a queue's oldest job has waited longer
  than ``max_wait``; ``busy`` names what the workers are running instead.
- ``ok`` otherwise.

``python manage.py rq_scheduler_status`` prints it and exits 1 when not ok,
so a compose healthcheck can use it directly.
"""

from __future__ import annotations

import time
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Iterable, List, Optional

SCHEDULER_INSTANCE_PREFIX = "rq:scheduler_instance:"


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
class SchedulerStatus:
    verdict: str  # "ok" | "scheduler_dead" | "starved"
    scheduler_alive: bool
    last_tick_age_sec: Optional[float]
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


def _scheduler_alive(conn) -> bool:
    for key in conn.scan_iter(match=SCHEDULER_INSTANCE_PREFIX + "*"):
        if not conn.hexists(key, "death"):
            return True
    return False


def _last_tick_age(conn) -> Optional[float]:
    from django_cfg.modules.django_rq.scheduler import SCHEDULER_TICK_KEY

    raw = conn.get(SCHEDULER_TICK_KEY)
    if raw is None:
        return None
    return max(0.0, time.time() - float(_s(raw)))


def scheduler_status(
    queue_names: Optional[Iterable[str]] = None,
    max_tick_age: float = 120.0,
    max_wait: float = 120.0,
    connection=None,
) -> SchedulerStatus:
    """
    Read scheduler liveness, per-queue wait and busy workers.

    Args:
        queue_names: queues to judge (default: every queue in ``RQ_QUEUES``).
        max_tick_age: seconds without a scheduler tick before ``scheduler_dead``.
        max_wait: seconds a queued job may wait before ``starved``.
        connection: Redis connection (default: django_rq's for the first queue).
    """
    import django_rq
    from rq import Worker

    if queue_names:
        names = list(queue_names)
    else:
        from django_rq.settings import QUEUES

        names = list(QUEUES.keys())
    queues = [django_rq.get_queue(n) for n in names]
    conn = connection or queues[0].connection

    alive = _scheduler_alive(conn)
    tick_age = _last_tick_age(conn)

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

    status = SchedulerStatus(
        verdict="ok", scheduler_alive=alive, last_tick_age_sec=tick_age,
        queues=waits, busy=busy,
    )
    if not alive:
        status.verdict, status.reason = "scheduler_dead", "no live rq:scheduler_instance key"
    elif tick_age is not None and tick_age > max_tick_age:
        status.verdict, status.reason = "scheduler_dead", f"last tick {tick_age:.0f}s ago"
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


__all__ = ["BusyWorker", "QueueWait", "SchedulerStatus", "scheduler_status"]
