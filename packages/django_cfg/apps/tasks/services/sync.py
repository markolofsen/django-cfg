"""
ReArq to TaskLog sync utilities.

Helpers for syncing data from ReArq (Tortoise ORM) to TaskLog (Django ORM).
"""
from typing import Optional
from django.utils import timezone
from ..models import TaskLog


def create_task_log_from_job(
    job_id: str,
    task_name: str,
    queue_name: str = "default",
    args: list = None,
    kwargs: dict = None,
    job_retry: int = 0,
    job_retry_after: int = 60,
    enqueue_time = None,
    expire_time = None,
    status: str = "queued",
    user=None,
) -> TaskLog:
    """
    Create TaskLog entry from ReArq Job data.

    Args:
        job_id: Unique job identifier from ReArq
        task_name: Name of the task function
        queue_name: Queue name (default: "default")
        args: Positional arguments
        kwargs: Keyword arguments
        job_retry: Max retry count from task definition
        job_retry_after: Seconds to wait before retry
        enqueue_time: When job was enqueued (Job.enqueue_time)
        expire_time: When job will expire (Job.expire_time)
        status: Job status (default: "queued")
        user: Django User who triggered the task

    Returns:
        Created TaskLog instance
    """
    return TaskLog.objects.create(
        job_id=job_id,
        task_name=task_name,
        queue_name=queue_name,
        args=args or [],
        kwargs=kwargs or {},
        job_retry=job_retry,
        job_retry_after=job_retry_after,
        enqueue_time=enqueue_time or timezone.now(),
        expire_time=expire_time,
        status=status,
        user=user,
    )


def update_task_log_from_result(
    job_id: str,
    worker: str,
    success: bool,
    result: str = None,
    start_time = None,
    finish_time = None,
) -> Optional[TaskLog]:
    """
    Update TaskLog with JobResult data.

    Args:
        job_id: Job identifier
        worker: Worker that processed the task
        success: Whether task succeeded
        result: Task result (JSON string)
        start_time: When execution started (JobResult.start_time)
        finish_time: When execution finished (JobResult.finish_time)

    Returns:
        Updated TaskLog instance or None if not found
    """
    try:
        task_log = TaskLog.objects.get(job_id=job_id)
    except TaskLog.DoesNotExist:
        return None

    # Update fields from JobResult
    task_log.worker_id = worker
    task_log.success = success
    task_log.start_time = start_time
    task_log.finish_time = finish_time

    if result is not None:
        task_log.result = result

    # Calculate duration
    if start_time and finish_time:
        delta = finish_time - start_time
        task_log.duration_ms = int(delta.total_seconds() * 1000)

    # Update status based on success
    if success:
        task_log.status = TaskLog.StatusChoices.SUCCESS
    else:
        task_log.status = TaskLog.StatusChoices.FAILED

    task_log.save()
    return task_log


def sync_job_status(job_id: str, status: str, job_retries: int = None) -> Optional[TaskLog]:
    """
    Sync Job status to TaskLog.

    Args:
        job_id: Job identifier
        status: ReArq JobStatus value
        job_retries: Current retry count

    Returns:
        Updated TaskLog instance or None if not found
    """
    try:
        task_log = TaskLog.objects.get(job_id=job_id)
    except TaskLog.DoesNotExist:
        return None

    task_log.status = status
    if job_retries is not None:
        task_log.job_retries = job_retries

    task_log.save(update_fields=["status", "job_retries", "updated_at"])
    return task_log


async def sync_from_rearq_job(rearq_job):
    """
    Sync TaskLog from ReArq Job instance (Tortoise model).

    Usage:
        from rearq.server.models import Job
        job = await Job.get(job_id="...")
        await sync_from_rearq_job(job)

    Args:
        rearq_job: ReArq Job instance (Tortoise ORM)

    Returns:
        TaskLog instance
    """
    from asgiref.sync import sync_to_async

    # Extract queue name from full queue path
    queue_name = rearq_job.task.split(':')[-1] if ':' in rearq_job.task else "default"

    # Check if TaskLog exists
    task_log = await sync_to_async(TaskLog.objects.filter(job_id=rearq_job.job_id).first)()

    if task_log:
        # Update existing
        task_log.status = rearq_job.status
        task_log.job_retries = rearq_job.job_retries
        await sync_to_async(task_log.save)(update_fields=["status", "job_retries", "updated_at"])
    else:
        # Create new
        task_log = await sync_to_async(create_task_log_from_job)(
            job_id=rearq_job.job_id,
            task_name=rearq_job.task,
            queue_name=queue_name,
            args=rearq_job.args or [],
            kwargs=rearq_job.kwargs or {},
            job_retry=rearq_job.job_retry,
            job_retry_after=rearq_job.job_retry_after,
            enqueue_time=rearq_job.enqueue_time,
            expire_time=rearq_job.expire_time,
            status=rearq_job.status,
        )

    return task_log


async def sync_from_rearq_result(rearq_result):
    """
    Sync TaskLog from ReArq JobResult instance (Tortoise model).

    Usage:
        from rearq.server.models import JobResult
        result = await JobResult.get(job_id="...").prefetch_related("job")
        await sync_from_rearq_result(result)

    Args:
        rearq_result: ReArq JobResult instance (Tortoise ORM)

    Returns:
        TaskLog instance or None
    """
    from asgiref.sync import sync_to_async

    return await sync_to_async(update_task_log_from_result)(
        job_id=rearq_result.job_id,
        worker=rearq_result.worker,
        success=rearq_result.success,
        result=rearq_result.result,
        start_time=rearq_result.start_time,
        finish_time=rearq_result.finish_time,
    )
