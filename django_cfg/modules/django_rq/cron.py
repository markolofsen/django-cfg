"""
django-cfg schedules on RQ's native cron (``rq.cron`` / django-rq ``DjangoCronScheduler``).

``python manage.py rqcron`` builds :class:`DjangoCfgCronScheduler` from
``DjangoRQConfig.get_all_schedules()`` and runs it. Over the stock scheduler:

1. **No stacked copies.** A due run whose previous copy still waits in the queue,
   or still runs with a fresh heartbeat, is skipped (the next run is booked as
   usual). Stock ``CronJob.enqueue`` pushes a new job every time.
2. **Queue settings apply.** Jobs go through ``django_rq.get_queue``, so
   ``RQ_QUEUES`` ``DEFAULT_TIMEOUT`` / ``DEFAULT_RESULT_TTL`` hold when an entry
   sets none.
3. **Cron in UTC**, as rq-scheduler did and our entries were written for
   (rq 3.0 evaluates cron strings in local time).
4. **Resume from history.** Each schedule has a stable name, so its run history
   (``rq:cron_job:<name>:jobs``) survives restarts; on start, or on taking over
   as leader, the next run is computed from the last one instead of firing every
   interval job at once.
5. **One leader.** ``SET NX`` on :data:`LEADER_KEY`; a second ``rqcron`` stays a
   standby and enqueues nothing.
6. **Delayed jobs.** The same process runs RQ's ``RQScheduler`` for every queue
   (per-queue locks, so it coexists with any worker ``--with-scheduler``):
   ``enqueue_in/at``, ``Retry(interval=...)`` and one-off ``scheduled_time``
   entries are moved into their queues.
"""

from __future__ import annotations

import hashlib
import json
import logging
from collections.abc import Iterable
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Any

from croniter import croniter
from django.utils.module_loading import import_string
from django_rq.cron import DjangoCronScheduler
from rq import cron_job_registry
from rq.cron import CronJob
from rq.exceptions import NoSuchJobError
from rq.job import Job, JobStatus
from rq.queue import Queue
from rq.scheduler import RQScheduler
from rq.utils import as_text, now

if TYPE_CHECKING:
    from redis import Redis

    from django_cfg.models.django.django_rq import RQScheduleConfig

logger = logging.getLogger(__name__)

LEADER_KEY = "djangocfg:rq:cron:leader"
LEADER_TTL_SEC = 30
ONE_OFF_MARKER_PREFIX = "djangocfg:rq:cron:oneoff:"
ONE_OFF_MARKER_TTL_SEC = 400 * 86400
# A running job whose heartbeat is older than this is treated as abandoned
# (rq refreshes it every job_monitoring_interval, 30 s by default).
RUNNING_HEARTBEAT_FRESH_SEC = 120
DEFAULT_POLL_SEC = 1.0

# rq-scheduler's keys, read once at start to remove what this project left there.
_OLD_SCHEDULED_JOBS_KEY = "rq:scheduler:scheduled_jobs"
_OLD_IDS_KEY_PREFIX = "django_cfg:schedule_ids:"


def schedule_name(schedule: RQScheduleConfig) -> str:
    """Stable name of a schedule: ``job_id`` when set, else ``schedule_<func>_<hash>``.

    The hash covers func, queue, the schedule and args/kwargs, so two entries for
    one function with different arguments keep separate histories.
    """
    if schedule.job_id:
        return schedule.job_id
    parts = [schedule.func, schedule.queue or "default"]
    if schedule.cron:
        parts.append(f"cron:{schedule.cron}")
    elif schedule.interval:
        parts.append(f"interval:{schedule.interval}")
    elif schedule.scheduled_time:
        parts.append(f"time:{schedule.scheduled_time}")
    if schedule.args:
        parts.append(f"args:{json.dumps(schedule.args, sort_keys=True)}")
    if schedule.kwargs:
        parts.append(f"kwargs:{json.dumps(schedule.kwargs, sort_keys=True)}")
    digest = hashlib.sha256("|".join(str(p) for p in parts).encode()).hexdigest()[:16]
    return f"schedule_{schedule.func.split('.')[-1]}_{digest}"


def previous_copy_pending(connection: Redis, job_id: str, queue_name: str) -> str | None:
    """Why another copy must not be pushed: ``"queued"``, ``"running"``, or None when it may."""
    queue_key = f"{Queue.redis_queue_namespace_prefix}{queue_name}"
    try:
        if connection.lpos(queue_key, job_id) is not None:
            return "queued"
    except Exception:  # LPOS needs Redis >= 6.0.6
        if any(as_text(i) == job_id for i in connection.lrange(queue_key, 0, -1)):
            return "queued"
    try:
        job = Job.fetch(job_id, connection=connection)
    except NoSuchJobError:
        return None
    if job.get_status(refresh=False) != JobStatus.STARTED:
        return None
    hb = job.last_heartbeat
    if hb is None:
        return None
    if hb.tzinfo is None:
        hb = hb.replace(tzinfo=timezone.utc)
    if (datetime.now(timezone.utc) - hb).total_seconds() < RUNNING_HEARTBEAT_FRESH_SEC:
        return "running"
    return None


class ScheduleCronJob(CronJob):
    """One ``RQScheduleConfig`` cron/interval entry on RQ's cron."""

    def __init__(self, *, description: str | None = None, repeat: int | None = None, **kwargs: Any):
        result_ttl = kwargs.pop("result_ttl", None)
        super().__init__(**kwargs, **({"result_ttl": result_ttl} if result_ttl is not None else {}))
        if result_ttl is None:
            # CronJob always stores rq's 500 s; leave it to the queue's DEFAULT_RESULT_TTL instead.
            self.job_options.pop("result_ttl", None)
        self.description = description
        self.repeat = repeat

    @classmethod
    def from_config(cls, schedule: RQScheduleConfig) -> ScheduleCronJob:
        name = schedule_name(schedule)
        return cls(
            queue_name=schedule.queue or "default",
            func=import_string(schedule.func),
            args=tuple(schedule.args or ()),
            kwargs=dict(schedule.kwargs or {}),
            interval=schedule.interval,
            cron=schedule.cron,
            job_timeout=schedule.timeout,
            result_ttl=schedule.result_ttl,
            meta={"schedule": name},
            name=name,
            description=schedule.description,
            repeat=schedule.repeat,
        )

    def get_next_enqueue_time(self) -> datetime:
        if self.cron:
            base = (self.latest_enqueue_time or now()).astimezone(timezone.utc)
            nxt = croniter(self.cron, base).get_next(datetime)
            return nxt if nxt.tzinfo else nxt.replace(tzinfo=timezone.utc)
        return super().get_next_enqueue_time()

    def resume(self, connection: Redis) -> None:
        """Take the last run from the history, so the next one follows it."""
        last = connection.zrange(self.job_history_key, 0, 0, desc=True, withscores=True)
        if last:
            self.set_enqueue_time(datetime.fromtimestamp(last[0][1], tz=timezone.utc))
        elif self.cron:
            self.latest_enqueue_time = None
            self.next_enqueue_time = self.get_next_enqueue_time()

    def last_job_id(self, connection: Redis) -> str | None:
        ids = connection.zrange(self.job_history_key, 0, 0, desc=True)
        return as_text(ids[0]) if ids else None

    def enqueue(self, connection: Redis) -> Job | None:  # type: ignore[override]
        if self.repeat is not None and connection.zcard(self.job_history_key) >= self.repeat:
            return None
        last_id = self.last_job_id(connection)
        reason = previous_copy_pending(connection, last_id, self.queue_name) if last_id else None
        if reason:
            logger.info(
                "rq cron: skipped %s (%s): previous copy %s still %s in '%s'",
                self.func_name, self.name, last_id, reason, self.queue_name,
                extra={"schedule": self.name, "job_id": last_id, "queue": self.queue_name, "skip_reason": reason},
            )
            return None

        import django_rq
        from django_rq.queues import get_result_ttl

        options = dict(self.job_options)
        if "result_ttl" not in options:
            queue_ttl = get_result_ttl(self.queue_name)
            if queue_ttl is not None:
                options["result_ttl"] = queue_ttl
        if self.description:
            options["description"] = self.description
        queue = django_rq.get_queue(self.queue_name, connection=connection, commit_mode="auto")
        with connection.pipeline() as pipeline:
            job = queue.enqueue(self.func, args=self.args, kwargs=self.kwargs, pipeline=pipeline, **options)
            stamp = job.enqueued_at.timestamp()
            pipeline.zadd(self.job_history_key, {job.id: stamp})
            pipeline.zremrangebyrank(self.job_history_key, 0, -1001)
            pipeline.expire(self.job_history_key, 365 * 86400)
            cron_job_registry.add(self.name, pipeline, enqueue_timestamp=stamp)
            pipeline.execute()
        logger.debug("rq cron: enqueued %s (%s) as %s on '%s'", self.func_name, self.name, job.id, self.queue_name)
        return job


class DjangoCfgCronScheduler(DjangoCronScheduler):
    """RQ cron scheduler for the schedules of one django-cfg project."""

    def __init__(self, connection: Redis, *, poll_interval: float = DEFAULT_POLL_SEC,
                 delayed_queues: Iterable[str] = (), name: str = "", logging_level: int = logging.INFO):
        super().__init__(connection=connection, logging_level=logging_level, name=name)
        self.poll_interval = poll_interval
        self.one_offs: list[RQScheduleConfig] = []
        self.skipped: list[tuple[str, str]] = []  # (func, reason) of entries that could not be registered
        self.is_leader = False
        self._leader_seen: str | None = None
        self._delayed = (
            RQScheduler(list(delayed_queues), connection=connection, interval=max(1, int(poll_interval)),
                        logging_level=logging_level)
            if delayed_queues else None
        )

    # --- building ---------------------------------------------------------

    @classmethod
    def from_config(cls, rq_config=None, **kwargs: Any) -> DjangoCfgCronScheduler:
        """Scheduler with every entry of ``DjangoRQConfig.get_all_schedules()`` registered."""
        import django_rq
        from django.conf import settings

        from .services.config_helper import get_rq_config

        rq_config = rq_config or get_rq_config()
        connection = django_rq.get_connection("default")
        kwargs.setdefault("delayed_queues", _same_redis_queues(connection, list(getattr(settings, "RQ_QUEUES", {}))))
        scheduler = cls(connection, **kwargs)
        for entry in (rq_config.get_all_schedules() if rq_config and rq_config.enabled else []):
            scheduler.add(entry)
        return scheduler

    def add(self, schedule: RQScheduleConfig) -> ScheduleCronJob | None:
        """Register one entry; a one-off ``scheduled_time`` is kept for :meth:`enqueue_one_offs`."""
        from django_rq.connection_utils import get_connection

        from django_cfg.models.django.django_rq import RQScheduleConfig

        if isinstance(schedule, dict):
            schedule = RQScheduleConfig(**schedule)
        queue_name = schedule.queue or "default"
        try:
            queue_conn = get_connection(queue_name)
        except KeyError:
            return self._skip(schedule, f"queue '{queue_name}' is not in RQ_QUEUES")
        if self._get_connection_config(queue_conn) != self._connection_config:
            return self._skip(schedule, f"queue '{queue_name}' is on another Redis")
        if schedule.scheduled_time:
            self.one_offs.append(schedule)
            return None
        try:
            job = ScheduleCronJob.from_config(schedule)
        except ImportError as e:
            return self._skip(schedule, f"cannot import: {e}")
        self._cron_jobs.append(job)
        return job

    def _skip(self, schedule, reason: str) -> None:
        logger.warning("rq cron: schedule %s not registered: %s", schedule.func, reason)
        self.skipped.append((schedule.func, reason))
        return None

    # --- leadership ---------------------------------------------------------

    def _lead(self) -> bool:
        conn = self.connection
        held = conn.set(LEADER_KEY, self.name, nx=True, ex=LEADER_TTL_SEC)
        if not held:
            owner = as_text(conn.get(LEADER_KEY) or b"")
            if owner == self.name:
                conn.expire(LEADER_KEY, LEADER_TTL_SEC)
                held = True
            elif owner != self._leader_seen:
                self._leader_seen = owner
                logger.info("rq cron: standby, leader is %s", owner)
        if held and not self.is_leader:
            logger.info("rq cron: %s leads %d schedules", self.name, len(self._cron_jobs))
            self.take_over()
        self.is_leader = bool(held)
        return self.is_leader

    def take_over(self) -> None:
        """Resume every schedule from its history and book the one-offs."""
        for job in self._cron_jobs:
            job.resume(self.connection)
        self.enqueue_one_offs()
        self.save()

    def release_leadership(self) -> None:
        try:
            if as_text(self.connection.get(LEADER_KEY) or b"") == self.name:
                self.connection.delete(LEADER_KEY)
        except Exception:  # pragma: no cover - shutting down
            logger.debug("rq cron: leader lock release failed", exc_info=True)
        self.is_leader = False

    # --- the loop -----------------------------------------------------------

    def enqueue_jobs(self) -> list[CronJob]:
        if not self._lead():
            return []
        self._move_delayed()
        # As upstream, but one failing schedule (a broken import at run time, a bad argument) does not stop the others.
        enqueue_time = now()
        due: list[CronJob] = []
        for job in self._cron_jobs:
            if job.should_run():
                try:
                    job.enqueue(self.connection)
                except Exception:
                    logger.exception("rq cron: enqueue of %s (%s) failed", job.func_name, job.name)
                job.set_enqueue_time(enqueue_time)
                due.append(job)
        return due

    def calculate_sleep_interval(self) -> float:
        return min(super().calculate_sleep_interval(), self.poll_interval)

    def register_birth(self) -> None:
        drop_rq_scheduler_leftovers(self.connection)
        super().register_birth()
        if self._delayed is not None:
            self._delayed.register_birth()

    def register_death(self, pipeline=None) -> None:
        self.release_leadership()
        if self._delayed is not None:
            try:
                self._delayed.stop()
            except Exception:  # pragma: no cover
                logger.debug("rq cron: delayed-job scheduler stop failed", exc_info=True)
        try:
            super().register_death(pipeline)
        except Exception:  # not in the registry any more (expired)
            logger.debug("rq cron: not in the scheduler registry at shutdown", exc_info=True)

    def _move_delayed(self) -> None:
        d = self._delayed
        if d is None:
            return
        try:
            if d.should_reacquire_locks:
                d.acquire_locks()
            d.heartbeat()
            d.enqueue_scheduled_jobs()
        except Exception:
            logger.warning("rq cron: moving delayed jobs failed", exc_info=True)

    def enqueue_one_offs(self) -> int:
        """``enqueue_at`` each one-off entry once; a marker keeps a restart from repeating it."""
        import django_rq

        done = 0
        for schedule in self.one_offs:
            name = schedule_name(schedule)
            if not self.connection.set(ONE_OFF_MARKER_PREFIX + name, 1, nx=True, ex=ONE_OFF_MARKER_TTL_SEC):
                continue
            at = datetime.fromisoformat(schedule.scheduled_time)
            if at.tzinfo is None:
                at = at.replace(tzinfo=timezone.utc)
            options: dict[str, Any] = {"job_id": name, "meta": {"schedule": name}}
            if schedule.timeout is not None:
                options["job_timeout"] = schedule.timeout
            if schedule.result_ttl is not None:
                options["result_ttl"] = schedule.result_ttl
            if schedule.description:
                options["description"] = schedule.description
            queue = django_rq.get_queue(schedule.queue or "default", connection=self.connection, commit_mode="auto")
            queue.enqueue_at(at, schedule.func, args=tuple(schedule.args), kwargs=dict(schedule.kwargs), **options)
            done += 1
        return done

    # --- reading ------------------------------------------------------------

    def describe(self) -> list[dict[str, Any]]:
        """One row per registered schedule, for ``rqcron --list``."""
        rows = []
        for job in self._cron_jobs:
            rows.append({
                "name": job.name,
                "func": job.func_name,
                "queue": job.queue_name,
                "schedule": f"cron {job.cron} (UTC)" if job.cron else f"every {job.interval}s",
                "job_timeout": job.job_options.get("job_timeout"),
                "result_ttl": job.job_options.get("result_ttl"),
            })
        for s in self.one_offs:
            rows.append({"name": schedule_name(s), "func": s.func, "queue": s.queue, "schedule": f"once at {s.scheduled_time}",
                         "job_timeout": s.timeout, "result_ttl": s.result_ttl})
        return rows


def _same_redis_queues(connection: Redis, names: list[str]) -> list[str]:
    from django_rq.connection_utils import get_connection

    want = connection.connection_pool.connection_kwargs
    keys = ("host", "port", "db", "path")
    same = []
    for n in names:
        kw = get_connection(n).connection_pool.connection_kwargs
        if all(kw.get(k) == want.get(k) for k in keys):
            same.append(n)
    return same


def drop_rq_scheduler_leftovers(connection: Redis, project: str | None = None) -> int:
    """Remove the rq-scheduler registrations this project left in Redis.

    rq-scheduler kept each schedule as a never-expiring job hash plus an entry in
    ``rq:scheduler:scheduled_jobs``; django-cfg listed the ids in
    ``django_cfg:schedule_ids:<project>``. Only those ids are touched. A job hash
    that is queued or running right now keeps living with a one-day TTL.
    Migration code: delete once every project runs ``rqcron``.
    """
    if project is None:
        try:
            from django_cfg.core.state import get_current_config

            project = get_current_config().project_name
        except Exception:
            project = "default"
    ids_key = _OLD_IDS_KEY_PREFIX + project
    ids = [as_text(i) for i in connection.smembers(ids_key)]
    if not ids:
        return 0
    for job_id in ids:
        connection.zrem(_OLD_SCHEDULED_JOBS_KEY, job_id)
        status = as_text(connection.hget(f"rq:job:{job_id}", "status") or b"")
        if status in (JobStatus.QUEUED.value, JobStatus.STARTED.value):
            connection.expire(f"rq:job:{job_id}", 86400)
        else:
            connection.delete(f"rq:job:{job_id}")
    connection.delete(ids_key)
    logger.info("rq cron: removed %d rq-scheduler registrations of %s", len(ids), project)
    return len(ids)


__all__ = [
    "DEFAULT_POLL_SEC",
    "DjangoCfgCronScheduler",
    "LEADER_KEY",
    "ScheduleCronJob",
    "drop_rq_scheduler_leftovers",
    "previous_copy_pending",
    "schedule_name",
]
