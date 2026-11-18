"""Carry the request id from the enqueuing request into the RQ job's log lines.

At enqueue the current request id is written into ``job.meta["request_id"]``; before the
job runs the worker restores it (and ``job_id``) into the same contextvars the request
middleware uses, so a worker line carries the id of the request that caused it.
Installed once, from ``django_rq`` app ready. No external source documents this: it is
proved by ``tests/core/test_logging_context.py``.
"""
from __future__ import annotations

import functools

from .context import job_id_var, request_id_var

_INSTALLED = False
META_KEY = "request_id"


def install() -> bool:
    """Patch ``rq.Queue.create_job`` and ``BaseWorker.perform_job``. Idempotent; False without rq."""
    global _INSTALLED
    if _INSTALLED:
        return True
    try:
        from rq.queue import Queue
        from rq.worker import BaseWorker as Worker  # Worker and SimpleWorker are siblings under it
    except Exception:
        return False

    orig_create = Queue.create_job

    @functools.wraps(orig_create)
    def create_job(self, *args, **kwargs):
        job = orig_create(self, *args, **kwargs)
        rid = request_id_var.get()
        if rid:
            try:
                job.meta.setdefault(META_KEY, rid)
            except Exception:
                pass
        return job

    orig_perform = Worker.perform_job

    @functools.wraps(orig_perform)
    def perform_job(self, job, queue, *args, **kwargs):
        # rq 2.x passes (job, queue); rq 3.0 adds `execution`. Forward whatever the installed rq sends.
        try:
            rid = (job.meta or {}).get(META_KEY)
        except Exception:
            rid = None
        t1 = request_id_var.set(rid)
        t2 = job_id_var.set(getattr(job, "id", None))
        try:
            return orig_perform(self, job, queue, *args, **kwargs)
        finally:
            job_id_var.reset(t2)
            request_id_var.reset(t1)

    Queue.create_job = create_job
    Worker.perform_job = perform_job
    _INSTALLED = True
    return True
