"""
django_rq.capture.hooks — RQ job lifecycle event capture.

Hooks are registered via RQ Worker on_* callbacks (RQ 1.16+ / django-rq 4.0+).
Each job state transition (queued → started → finished/failed/canceled) is
pushed to D1 as an RQJobEvent. Worker heartbeats are pushed as RQWorkerStats.

NOTE: JOB_FAILED is NOT captured here — it is already captured by
django_monitor/capture/rq.py as RQ_FAILURE → SERVER_EVENTS table.
This module captures the complement: success and queued/started events.

On D1 write failure: silently suppressed — never blocks job execution.
"""

from __future__ import annotations

import logging

logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────────────────────────────────────
# Hook functions — called by RQ worker lifecycle
# ─────────────────────────────────────────────────────────────────────────────

def on_job_queued(job, queue, **kwargs) -> None:
    """Called when a job is enqueued. Push JOB_QUEUED event to D1."""
    _push_job_event(job, "JOB_QUEUED")


def on_job_started(job, queue, worker=None, **kwargs) -> None:
    """Called when a worker picks up a job. Push JOB_STARTED event to D1."""
    worker_name = _get_worker_name(worker)
    _push_job_event(job, "JOB_STARTED", worker_name=worker_name)


def on_job_finished(job, queue, result=None, worker=None, **kwargs) -> None:
    """Called on successful job completion. Push JOB_FINISHED event to D1."""
    worker_name = _get_worker_name(worker)
    _push_job_event(job, "JOB_FINISHED", worker_name=worker_name)


def on_job_canceled(job, queue=None, **kwargs) -> None:
    """Called when a job is canceled. Push JOB_CANCELED event to D1."""
    _push_job_event(job, "JOB_CANCELED")


def on_worker_heartbeat(worker, **kwargs) -> None:
    """
    Called periodically by the worker. Push worker state snapshot to D1.

    Wire this into Worker.heartbeat() via monkey-patching in register_hooks(),
    or use it from a custom management command / periodic task.
    """
    _push_worker_heartbeat(worker)


# ─────────────────────────────────────────────────────────────────────────────
# Internal helpers
# ─────────────────────────────────────────────────────────────────────────────

def _get_worker_name(worker) -> str | None:
    if worker is None:
        return None
    try:
        return str(worker.name)
    except Exception:
        return None


def _push_job_event(job, event_type: str, *, worker_name: str | None = None) -> None:
    """Push a single job event to D1. Silently suppressed on any error."""
    try:
        from django_cfg.modules.django_rq import is_enabled, get_service
        if not is_enabled():
            return
        from django_cfg.modules.django_rq.events.types import RQJobEvent
        event = RQJobEvent.from_rq_job(job, event_type, worker_name=worker_name)
        get_service().push_job_event(event)
    except Exception as exc:
        logger.debug("django_rq: _push_job_event suppressed — %s", exc)


def _push_job_failed(job, *, worker=None) -> None:
    """Push JOB_FAILED event to D1. Separate from django_monitor's RQ_FAILURE capture."""
    worker_name = _get_worker_name(worker)
    _push_job_event(job, "JOB_FAILED", worker_name=worker_name)


def _push_worker_heartbeat(worker) -> None:
    """Push a worker heartbeat to D1. Silently suppressed on any error."""
    try:
        from django_cfg.modules.django_rq import is_enabled, get_service
        if not is_enabled():
            return
        from django_cfg.modules.django_rq.events.types import RQWorkerStats
        stats = RQWorkerStats.from_rq_worker(worker)
        get_service().push_worker_heartbeat(stats)
    except Exception as exc:
        logger.debug("django_rq: _push_worker_heartbeat suppressed — %s", exc)


# ─────────────────────────────────────────────────────────────────────────────
# Registration
# ─────────────────────────────────────────────────────────────────────────────

def register_hooks() -> None:
    """
    Register RQ job lifecycle hooks into the Worker class.

    RQ 1.16+ (django-rq 4.0+) supports on_job_queued, on_job_started,
    on_job_success, on_job_failure, on_job_stopped callbacks on the Queue.

    We patch them at the Worker class level so all workers across all queues
    get the hooks automatically, without requiring changes to queue definitions.

    Strategy:
    - on_job_started / on_job_finished / JOB_FAILED → patch Worker.perform_job()
    - on_job_queued → patch Queue.enqueue_job() + Queue.enqueue_many()
    - Worker heartbeat → patch Worker.heartbeat()
    """
    _register_worker_callbacks()
    _register_queue_callbacks()
    _patch_worker_heartbeat()
    logger.debug("django_rq: hooks registered")


def _register_worker_callbacks() -> None:
    """Patch Worker.perform_job to fire started/finished/failed hooks."""
    try:
        from rq import Worker

        _original_perform_job = Worker.perform_job

        def _patched_perform_job(self, job, queue, *args, **kwargs):
            on_job_started(job, queue, worker=self)
            try:
                result = _original_perform_job(self, job, queue, *args, **kwargs)
                # perform_job returns True on success, False on failure
                if result:
                    on_job_finished(job, queue, worker=self)
                else:
                    # Job failed — also write JOB_FAILED to rq_job_events
                    # (django_monitor writes the same failure to server_events separately)
                    _push_job_failed(job, worker=self)
                return result
            except Exception:
                # Unexpected exception in the worker harness itself — still capture
                _push_job_failed(job, worker=self)
                raise

        Worker.perform_job = _patched_perform_job
        logger.debug("django_rq: Worker.perform_job patched")
    except Exception as exc:
        logger.warning("django_rq: failed to patch Worker.perform_job — %s", exc)


def _register_queue_callbacks() -> None:
    """Patch Queue.enqueue_job and Queue.enqueue_many to fire queued hooks."""
    try:
        from rq import Queue

        _original_enqueue_job = Queue.enqueue_job

        def _patched_enqueue_job(self, job, *args, **kwargs):
            result = _original_enqueue_job(self, job, *args, **kwargs)
            on_job_queued(job, self)
            return result

        Queue.enqueue_job = _patched_enqueue_job
        logger.debug("django_rq: Queue.enqueue_job patched")
    except Exception as exc:
        logger.warning("django_rq: failed to patch Queue.enqueue_job — %s", exc)

    # Also patch enqueue_many so bulk enqueues are captured
    # enqueue_many(job_datas, pipeline=None, group_id=None) → list[Job]
    try:
        from rq import Queue

        _original_enqueue_many = Queue.enqueue_many

        def _patched_enqueue_many(self, job_datas, pipeline=None, group_id=None):
            results = _original_enqueue_many(self, job_datas, pipeline=pipeline, group_id=group_id)
            for job in results:
                on_job_queued(job, self)
            return results

        Queue.enqueue_many = _patched_enqueue_many
        logger.debug("django_rq: Queue.enqueue_many patched")
    except Exception as exc:
        logger.warning("django_rq: failed to patch Queue.enqueue_many — %s", exc)


def _patch_worker_heartbeat() -> None:
    """Patch Worker.heartbeat to fire heartbeat hook (optional, called separately)."""
    try:
        from rq import Worker

        _original_heartbeat = Worker.heartbeat

        def _patched_heartbeat(self, *args, **kwargs):
            result = _original_heartbeat(self, *args, **kwargs)
            on_worker_heartbeat(self)
            return result

        Worker.heartbeat = _patched_heartbeat
        logger.debug("django_rq: Worker.heartbeat patched")
    except Exception as exc:
        logger.warning("django_rq: failed to patch Worker.heartbeat — %s", exc)


__all__ = [
    "on_job_queued",
    "on_job_started",
    "on_job_finished",
    "on_job_canceled",
    "on_worker_heartbeat",
    "register_hooks",
]
