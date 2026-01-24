"""
Job cancellation utilities for Django-RQ.

Provides cooperative cancellation for long-running jobs.

Usage in tasks:
    from django_cfg.apps.integrations.rq.services import is_cancellation_requested

    @job("default")
    def my_long_task():
        for item in items:
            if is_cancellation_requested():
                return {"cancelled": True}
            process(item)

Usage in views:
    from django_cfg.apps.integrations.rq.services import request_cancellation

    def cancel_view(request, job_id):
        if request_cancellation(job_id):
            return Response({"status": "cancelled"})
        return Response({"error": "Job not found"}, status=404)
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from rq.job import Job

logger = logging.getLogger("django_cfg.rq.cancellation")

# Redis key prefix for cancellation flags
CANCEL_FLAG_PREFIX = "rq:cancel:"
CANCEL_FLAG_TTL = 3600  # 1 hour


def request_cancellation(job_id: str) -> bool:
    """
    Request cancellation of a job.

    For queued jobs: cancels immediately via RQ.
    For running jobs: sets cancellation flag in Redis.

    Args:
        job_id: RQ job ID

    Returns:
        True if cancellation was requested successfully
    """
    try:
        job, queue = _find_job(job_id)

        if not job:
            logger.warning(f"Job {job_id} not found")
            return False

        status = job.get_status()

        if status == "queued":
            # Job not started yet - cancel directly
            job.cancel()
            logger.info(f"Job {job_id} cancelled (was queued)")
            return True

        elif status == "started":
            # Job is running - set cancellation flag
            _set_cancel_flag(job_id, queue.connection)
            logger.info(f"Cancellation requested for running job {job_id}")
            return True

        else:
            # Job already finished/failed/cancelled
            logger.info(f"Job {job_id} already in terminal state: {status}")
            return False

    except Exception as e:
        logger.error(f"Failed to cancel job {job_id}: {e}")
        return False


def force_stop_job(job_id: str) -> bool:
    """
    Force stop a running job by sending SIGTERM to the worker.

    WARNING: This will kill ALL jobs on the same worker!
    Use only as last resort.

    Args:
        job_id: RQ job ID

    Returns:
        True if stop command was sent
    """
    try:
        from rq.command import send_stop_job_command

        job, queue = _find_job(job_id)

        if not job:
            return False

        if job.get_status() != "started":
            return False

        send_stop_job_command(queue.connection, job_id)
        logger.warning(f"Force stop sent for job {job_id}")
        return True

    except Exception as e:
        logger.error(f"Failed to force stop job {job_id}: {e}")
        return False


def is_cancellation_requested(job_id: str | None = None) -> bool:
    """
    Check if cancellation was requested for current or specified job.

    Call this periodically in long-running tasks to enable
    cooperative cancellation.

    Args:
        job_id: Optional job ID. If None, uses current job.

    Returns:
        True if cancellation was requested

    Usage in tasks:
        @job("default")
        def my_task():
            for item in items:
                if is_cancellation_requested():
                    return {"cancelled": True}
                process(item)
    """
    from rq import get_current_job

    current_job = get_current_job()

    if job_id is None:
        if not current_job:
            return False
        job_id = current_job.id

    # At this point job_id is guaranteed to be a string
    assert job_id is not None

    try:
        # Check RQ's built-in stopped flag first
        if current_job and current_job.is_stopped:
            return True

        # Check our cancellation flag
        return _get_cancel_flag(job_id)

    except Exception:
        return False


def clear_cancellation_flag(job_id: str) -> None:
    """
    Clear cancellation flag after job handles cancellation.

    Args:
        job_id: RQ job ID
    """
    try:
        _, queue = _find_job(job_id)
        if queue:
            key = f"{CANCEL_FLAG_PREFIX}{job_id}"
            queue.connection.delete(key)
    except Exception:
        pass


def get_job_status(job_id: str) -> str | None:
    """
    Get current status of a job.

    Args:
        job_id: RQ job ID

    Returns:
        Job status string or None if not found
    """
    try:
        job, _ = _find_job(job_id)
        if job:
            return job.get_status()
        return None
    except Exception:
        return None


# --- Internal helpers ---


def _find_job(job_id: str) -> tuple["Job | None", any]:
    """Find job across all queues."""
    import django_rq
    from django.conf import settings
    from rq.job import Job

    if not hasattr(settings, "RQ_QUEUES"):
        return None, None

    for queue_name in settings.RQ_QUEUES.keys():
        try:
            queue = django_rq.get_queue(queue_name)
            job = Job.fetch(job_id, connection=queue.connection)
            return job, queue
        except Exception:
            continue

    return None, None


def _set_cancel_flag(job_id: str, connection) -> None:
    """Set cancellation flag in Redis."""
    key = f"{CANCEL_FLAG_PREFIX}{job_id}"
    connection.setex(key, CANCEL_FLAG_TTL, "1")


def _get_cancel_flag(job_id: str) -> bool:
    """Check cancellation flag in Redis."""
    try:
        import django_rq

        queue = django_rq.get_queue("default")
        key = f"{CANCEL_FLAG_PREFIX}{job_id}"
        return bool(queue.connection.exists(key))
    except Exception:
        return False
