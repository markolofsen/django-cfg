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
            "finished_total": 0,
            "failed_total": 0,
        }

        logger.info(
            f"=== Starting cleanup of jobs older than {max_age_days} days "
            f"(cutoff: {cutoff_date}) [dry_run={dry_run}] ==="
        )

        # Clean up finished jobs
        finished_registry = FinishedJobRegistry(queue=queue)
        finished_job_ids = finished_registry.get_job_ids()
        stats["finished_total"] = len(finished_job_ids)
        logger.info(f"Checking {len(finished_job_ids)} finished jobs in queue '{queue_name}'")

        for job_id in finished_job_ids:
            try:
                job = Job.fetch(job_id, connection=redis_conn)
                if job.created_at and job.created_at < cutoff_date:
                    logger.debug(
                        f"Deleting old finished job: {job_id} | func={job.func_name} | "
                        f"created={job.created_at}"
                    )
                    if not dry_run:
                        finished_registry.remove(job, delete_job=True)
                    stats["finished_deleted"] += 1
            except Exception as e:
                logger.warning(f"Failed to process finished job {job_id}: {e}")

        # Clean up failed jobs
        failed_registry = FailedJobRegistry(queue=queue)
        failed_job_ids = failed_registry.get_job_ids()
        stats["failed_total"] = len(failed_job_ids)
        logger.info(f"Checking {len(failed_job_ids)} failed jobs in queue '{queue_name}'")

        for job_id in failed_job_ids:
            try:
                job = Job.fetch(job_id, connection=redis_conn)
                if job.created_at and job.created_at < cutoff_date:
                    logger.debug(
                        f"Deleting old failed job: {job_id} | func={job.func_name} | "
                        f"created={job.created_at}"
                    )
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
            f"=== Cleanup completed: {stats['total_deleted']} jobs deleted "
            f"(finished: {stats['finished_deleted']}/{stats['finished_total']}, "
            f"failed: {stats['failed_deleted']}/{stats['failed_total']}) "
            f"[dry_run={dry_run}] ==="
        )
        logger.info(f"Stats: {stats}")

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

    IMPORTANT: This function checks ALL configured queues, not just the one specified.
    The queue_name parameter is only used to get the Redis connection.

    Args:
        dry_run: If True, only count keys without deleting them
        queue_name: Queue name to get Redis connection (default: "default")

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
        # Get Redis connection from default queue
        default_queue = django_rq.get_queue(queue_name)
        redis_conn = default_queue.connection

        stats = {
            "orphaned_deleted": 0,
            "dry_run": dry_run,
            "total_job_keys": 0,
            "valid_job_ids": 0,
            "scheduled_job_ids": 0,
            "queued_job_ids": 0,
            "registry_job_ids": 0,
        }

        logger.info(f"=== Starting orphaned job key cleanup [dry_run={dry_run}] ===")

        # Get all job keys (decode bytes to strings for comparison)
        all_job_keys_raw = redis_conn.keys("rq:job:*")
        all_job_keys = set(
            k.decode("utf-8") if isinstance(k, bytes) else k
            for k in all_job_keys_raw
        )
        stats["total_job_keys"] = len(all_job_keys)
        logger.info(f"Total rq:job:* keys in Redis: {len(all_job_keys)}")

        # Get all valid job IDs from ALL queues' registries
        valid_job_ids = set()
        queued_count = 0
        registry_count = 0

        # Get all configured queue names from Django settings
        from django.conf import settings
        queue_names = list(getattr(settings, "RQ_QUEUES", {}).keys())
        if not queue_names:
            queue_names = ["default"]

        logger.info(f"Checking jobs from queues: {queue_names}")

        # Collect valid jobs from ALL queues
        for qname in queue_names:
            try:
                queue = django_rq.get_queue(qname)

                # Add queued jobs
                queue_job_ids = list(queue.job_ids)
                for job_id in queue_job_ids:
                    valid_job_ids.add(f"rq:job:{job_id}")
                    queued_count += 1

                logger.debug(f"Queue '{qname}': {len(queue_job_ids)} queued jobs")

                # Add jobs from registries
                for registry_class in [FinishedJobRegistry, FailedJobRegistry, StartedJobRegistry]:
                    registry = registry_class(queue=queue)
                    registry_job_ids = registry.get_job_ids()
                    for job_id in registry_job_ids:
                        valid_job_ids.add(f"rq:job:{job_id}")
                        registry_count += 1

                    if registry_job_ids:
                        logger.debug(
                            f"Queue '{qname}' {registry_class.__name__}: "
                            f"{len(registry_job_ids)} jobs"
                        )

            except Exception as e:
                logger.warning(f"Failed to get jobs from queue {qname}: {e}")

        stats["queued_job_ids"] = queued_count
        stats["registry_job_ids"] = registry_count

        # Add scheduled jobs from rq-scheduler
        # Scheduled jobs are stored in rq:scheduler:scheduled_jobs sorted set
        # and should not be considered orphaned
        scheduled_job_ids_raw = redis_conn.zrange("rq:scheduler:scheduled_jobs", 0, -1)
        scheduled_count = 0
        for job_id in scheduled_job_ids_raw:
            if isinstance(job_id, bytes):
                job_id = job_id.decode("utf-8")
            valid_job_ids.add(f"rq:job:{job_id}")
            scheduled_count += 1

        stats["scheduled_job_ids"] = scheduled_count
        stats["valid_job_ids"] = len(valid_job_ids)

        logger.info(
            f"Valid job IDs: {len(valid_job_ids)} total "
            f"(queued={queued_count}, registries={registry_count}, scheduled={scheduled_count})"
        )

        # Find orphaned keys
        orphaned_keys = all_job_keys - valid_job_ids
        stats["orphaned_deleted"] = len(orphaned_keys)

        if orphaned_keys:
            logger.warning(f"Found {len(orphaned_keys)} ORPHANED job keys!")

            # Log details of orphaned keys (limit to first 20 to avoid log spam)
            orphaned_list = sorted(orphaned_keys)
            for key in orphaned_list[:20]:
                # Try to get job info before deletion
                try:
                    job_id = key.replace("rq:job:", "")
                    job = Job.fetch(job_id, connection=redis_conn)
                    logger.warning(
                        f"  ORPHANED: {key} | func={job.func_name} | "
                        f"status={job.get_status()} | created={job.created_at} | "
                        f"result_ttl={job.result_ttl} | meta={job.meta}"
                    )
                except Exception as e:
                    # Job data might be corrupted or partially deleted
                    ttl = redis_conn.ttl(key)
                    key_type = redis_conn.type(key)
                    if isinstance(key_type, bytes):
                        key_type = key_type.decode()
                    logger.warning(
                        f"  ORPHANED: {key} | type={key_type} | ttl={ttl} | "
                        f"fetch_error={e}"
                    )

            if len(orphaned_keys) > 20:
                logger.warning(f"  ... and {len(orphaned_keys) - 20} more orphaned keys")

            # Delete orphaned keys
            if not dry_run:
                logger.info(f"Deleting {len(orphaned_keys)} orphaned keys...")
                redis_conn.delete(*orphaned_keys)
                logger.info("Deletion complete")
            else:
                logger.info(f"DRY RUN: Would delete {len(orphaned_keys)} orphaned keys")
        else:
            logger.info("No orphaned job keys found")

        logger.info(
            f"=== Orphaned key cleanup completed: {stats['orphaned_deleted']} keys "
            f"[dry_run={dry_run}] ==="
        )
        logger.info(f"Stats: {stats}")

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


def diagnose_scheduled_jobs(queue_name: str = "default") -> Dict[str, any]:
    """
    Diagnose scheduled jobs health - check if job keys exist for all scheduled jobs.

    This function helps identify issues where scheduled job IDs are in
    rq:scheduler:scheduled_jobs but their job keys (rq:job:*) are missing.

    Args:
        queue_name: Queue name to get Redis connection (default: "default")

    Returns:
        Dictionary with diagnosis results:
        {
            "total_scheduled": 12,
            "healthy": 10,
            "missing_keys": 2,
            "missing_job_ids": ["job_id_1", "job_id_2"],
            "jobs": [...]
        }

    Example:
        >>> from django_cfg.apps.integrations.rq.tasks.maintenance import diagnose_scheduled_jobs
        >>> result = diagnose_scheduled_jobs()
        >>> if result["missing_keys"] > 0:
        >>>     print(f"WARNING: {result['missing_keys']} scheduled jobs have missing keys!")
    """
    try:
        queue = django_rq.get_queue(queue_name)
        redis_conn = queue.connection

        result = {
            "total_scheduled": 0,
            "healthy": 0,
            "missing_keys": 0,
            "missing_job_ids": [],
            "jobs": [],
        }

        logger.info("=== Diagnosing scheduled jobs ===")

        # Get all scheduled job IDs with their scores (scheduled times)
        scheduled_jobs = redis_conn.zrange(
            "rq:scheduler:scheduled_jobs", 0, -1, withscores=True
        )
        result["total_scheduled"] = len(scheduled_jobs)

        logger.info(f"Total scheduled jobs: {len(scheduled_jobs)}")

        for job_data in scheduled_jobs:
            job_id, score = job_data
            if isinstance(job_id, bytes):
                job_id = job_id.decode("utf-8")

            # Convert score to datetime
            from datetime import datetime
            scheduled_time = datetime.utcfromtimestamp(score)

            job_key = f"rq:job:{job_id}"
            key_exists = redis_conn.exists(job_key)
            key_ttl = redis_conn.ttl(job_key) if key_exists else -2

            job_info = {
                "job_id": job_id,
                "scheduled_time": scheduled_time.isoformat(),
                "key_exists": bool(key_exists),
                "key_ttl": key_ttl,
            }

            if key_exists:
                try:
                    job = Job.fetch(job_id, connection=redis_conn)
                    job_info.update({
                        "func": job.func_name,
                        "status": str(job.get_status()),
                        "result_ttl": job.result_ttl,
                        "ttl": job.ttl,
                        "created_at": job.created_at.isoformat() if job.created_at else None,
                        "interval": job.meta.get("interval"),
                        "cron_string": job.meta.get("cron_string"),
                        "repeat": job.meta.get("repeat"),
                    })
                    result["healthy"] += 1
                    logger.debug(
                        f"✓ {job_id[:50]}... | {job.func_name} | "
                        f"scheduled={scheduled_time} | result_ttl={job.result_ttl}"
                    )
                except Exception as e:
                    job_info["fetch_error"] = str(e)
                    result["missing_keys"] += 1
                    result["missing_job_ids"].append(job_id)
                    logger.warning(
                        f"✗ {job_id[:50]}... | KEY EXISTS but FETCH FAILED: {e}"
                    )
            else:
                result["missing_keys"] += 1
                result["missing_job_ids"].append(job_id)
                logger.warning(
                    f"✗ {job_id[:50]}... | KEY MISSING! scheduled={scheduled_time}"
                )

            result["jobs"].append(job_info)

        # Summary
        logger.info(
            f"=== Diagnosis complete: {result['healthy']} healthy, "
            f"{result['missing_keys']} missing keys ==="
        )

        if result["missing_keys"] > 0:
            logger.warning(
                f"ACTION REQUIRED: {result['missing_keys']} scheduled jobs have missing keys. "
                f"These jobs will be removed from scheduler on next check cycle. "
                f"Missing IDs: {result['missing_job_ids']}"
            )

        return result

    except Exception as e:
        logger.error(f"Failed to diagnose scheduled jobs: {e}", exc_info=True)
        raise
