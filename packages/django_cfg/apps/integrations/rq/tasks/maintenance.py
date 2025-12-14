"""
RQ Maintenance Tasks

Tasks for cleaning up old jobs, managing Redis keys, and maintaining RQ health.
"""
from datetime import datetime, timedelta, timezone
from typing import Dict

import django_rq
from django_cfg.utils import get_logger
from rq.job import Job, JobStatus
from rq.queue import Queue
from rq.registry import (
    FailedJobRegistry,
    FinishedJobRegistry,
    StartedJobRegistry,
)

logger = get_logger("rq.maintenance")


def _make_aware(dt: datetime) -> datetime:
    """Make datetime timezone-aware if it's naive."""
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt


def cleanup_old_jobs(
    max_age_days: int = 7,
    dry_run: bool = False,
    queue_name: str = "default",
) -> Dict[str, int]:
    """
    Clean up old finished and failed jobs from Redis.

    This task removes jobs older than max_age_days to prevent Redis
    from accumulating too many job keys over time.

    Args:
        max_age_days: Maximum age in days for jobs to keep (default: 7)
        dry_run: If True, only count jobs without deleting them
        queue_name: Queue name to clean up (default: "default")

    Returns:
        Dictionary with cleanup statistics:
        {
            "finished_deleted": 10,
            "failed_deleted": 5,
            "total_deleted": 15,
            "dry_run": False
        }

    Example:
        >>> from django_cfg.apps.integrations.rq.tasks.maintenance import cleanup_old_jobs
        >>> # Dry run to see what would be deleted
        >>> stats = cleanup_old_jobs(max_age_days=7, dry_run=True)
        >>> print(f"Would delete {stats['total_deleted']} jobs")
        >>>
        >>> # Actually delete old jobs
        >>> stats = cleanup_old_jobs(max_age_days=7, dry_run=False)
        >>> print(f"Deleted {stats['total_deleted']} jobs")
    """
    try:
        queue = django_rq.get_queue(queue_name)
        redis_conn = queue.connection

        cutoff_date = _make_aware(datetime.utcnow()) - timedelta(days=max_age_days)
        stats = {
            "finished_deleted": 0,
            "failed_deleted": 0,
            "total_deleted": 0,
            "dry_run": dry_run,
        }

        logger.info(
            f"Starting cleanup of jobs older than {max_age_days} days "
            f"(cutoff: {cutoff_date}) [dry_run={dry_run}]"
        )

        # Clean up finished jobs
        finished_registry = FinishedJobRegistry(queue=queue)
        for job_id in finished_registry.get_job_ids():
            try:
                job = Job.fetch(job_id, connection=redis_conn)
                if job.created_at and job.created_at < cutoff_date:
                    if not dry_run:
                        finished_registry.remove(job, delete_job=True)
                    stats["finished_deleted"] += 1
            except Exception as e:
                logger.warning(f"Failed to process finished job {job_id}: {e}")

        # Clean up failed jobs
        failed_registry = FailedJobRegistry(queue=queue)
        for job_id in failed_registry.get_job_ids():
            try:
                job = Job.fetch(job_id, connection=redis_conn)
                if job.created_at and job.created_at < cutoff_date:
                    if not dry_run:
                        failed_registry.remove(job, delete_job=True)
                    stats["failed_deleted"] += 1
            except Exception as e:
                # If job doesn't exist, remove it from registry anyway
                logger.warning(f"Failed to process failed job {job_id}: {e}")
                if not dry_run and "No such job" in str(e):
                    try:
                        # Remove from registry even if job doesn't exist
                        redis_conn.zrem(failed_registry.key, job_id)
                        stats["failed_deleted"] += 1
                    except Exception:
                        pass

        stats["total_deleted"] = stats["finished_deleted"] + stats["failed_deleted"]

        logger.info(
            f"Cleanup completed: {stats['total_deleted']} jobs "
            f"(finished: {stats['finished_deleted']}, failed: {stats['failed_deleted']}) "
            f"[dry_run={dry_run}]"
        )

        return stats

    except Exception as e:
        logger.error(f"Cleanup failed: {e}", exc_info=True)
        raise


def cleanup_orphaned_job_keys(
    dry_run: bool = False,
    queue_name: str = "default",
) -> Dict[str, int]:
    """
    Clean up orphaned job keys that don't belong to any queue or registry.

    Orphaned keys can accumulate when jobs are improperly cancelled or
    when RQ crashes. This task finds and removes such keys.

    Args:
        dry_run: If True, only count keys without deleting them
        queue_name: Queue name to check (default: "default")

    Returns:
        Dictionary with cleanup statistics:
        {
            "orphaned_deleted": 15,
            "dry_run": False
        }

    Example:
        >>> from django_cfg.apps.integrations.rq.tasks.maintenance import cleanup_orphaned_job_keys
        >>> stats = cleanup_orphaned_job_keys(dry_run=True)
        >>> print(f"Found {stats['orphaned_deleted']} orphaned keys")
    """
    try:
        queue = django_rq.get_queue(queue_name)
        redis_conn = queue.connection

        stats = {
            "orphaned_deleted": 0,
            "dry_run": dry_run,
        }

        logger.info(f"Scanning for orphaned job keys [dry_run={dry_run}]")

        # Get all job keys
        all_job_keys = set(redis_conn.keys("rq:job:*"))

        # Get all valid job IDs from registries and queues
        valid_job_ids = set()

        # Add queued jobs
        for job_id in queue.job_ids:
            valid_job_ids.add(f"rq:job:{job_id}")

        # Add jobs from registries
        for registry_class in [FinishedJobRegistry, FailedJobRegistry, StartedJobRegistry]:
            registry = registry_class(queue=queue)
            for job_id in registry.get_job_ids():
                valid_job_ids.add(f"rq:job:{job_id}")

        # Find orphaned keys
        orphaned_keys = all_job_keys - valid_job_ids

        logger.info(f"Found {len(orphaned_keys)} orphaned job keys")

        # Delete orphaned keys
        if orphaned_keys and not dry_run:
            redis_conn.delete(*orphaned_keys)

        stats["orphaned_deleted"] = len(orphaned_keys)

        logger.info(
            f"Orphaned key cleanup completed: {stats['orphaned_deleted']} keys "
            f"[dry_run={dry_run}]"
        )

        return stats

    except Exception as e:
        logger.error(f"Orphaned key cleanup failed: {e}", exc_info=True)
        raise


def get_rq_stats(queue_name: str = "default") -> Dict[str, any]:
    """
    Get statistics about RQ queues and jobs.

    Returns detailed statistics about job counts, queue sizes, and Redis usage.

    Args:
        queue_name: Queue name to get stats for (default: "default")

    Returns:
        Dictionary with statistics:
        {
            "queue": {...},
            "jobs": {...},
            "redis": {...}
        }

    Example:
        >>> from django_cfg.apps.integrations.rq.tasks.maintenance import get_rq_stats
        >>> stats = get_rq_stats()
        >>> print(f"Queued jobs: {stats['queue']['queued']}")
        >>> print(f"Total Redis keys: {stats['redis']['total_keys']}")
    """
    try:
        queue = django_rq.get_queue(queue_name)
        redis_conn = queue.connection

        # Queue stats
        finished_registry = FinishedJobRegistry(queue=queue)
        failed_registry = FailedJobRegistry(queue=queue)
        started_registry = StartedJobRegistry(queue=queue)

        stats = {
            "queue": {
                "name": queue_name,
                "queued": len(queue),
                "finished": len(finished_registry),
                "failed": len(failed_registry),
                "started": len(started_registry),
            },
            "jobs": {
                "total": len(redis_conn.keys("rq:job:*")),
            },
            "redis": {
                "total_keys": len(redis_conn.keys("rq:*")),
                "queue_keys": len(redis_conn.keys("rq:queue:*")),
                "worker_keys": len(redis_conn.keys("rq:worker:*")),
            },
        }

        logger.info(f"RQ Stats: {stats}")
        return stats

    except Exception as e:
        logger.error(f"Failed to get RQ stats: {e}", exc_info=True)
        raise
