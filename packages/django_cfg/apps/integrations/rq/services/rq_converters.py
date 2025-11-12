"""
RQ Object to Pydantic Model Converters.

Converts RQ objects (Job, Queue, Worker) to type-safe Pydantic models
for internal business logic.
"""

import json
from typing import Optional

from rq import Queue, Worker
from rq.job import Job

from .models import RQJobModel, RQQueueModel, RQWorkerModel, JobStatus, WorkerState


def job_to_model(job: Job, queue_name: Optional[str] = None) -> RQJobModel:
    """
    Convert RQ Job to Pydantic RQJobModel.

    Args:
        job: RQ Job instance
        queue_name: Queue name (optional, will try to get from job.origin)

    Returns:
        Validated RQJobModel instance
    """
    # Get queue name
    if not queue_name:
        queue_name = getattr(job, 'origin', 'unknown')

    # Map RQ status to JobStatus enum
    rq_status = job.get_status()
    status_map = {
        'queued': JobStatus.QUEUED,
        'started': JobStatus.STARTED,
        'finished': JobStatus.FINISHED,
        'failed': JobStatus.FAILED,
        'deferred': JobStatus.DEFERRED,
        'scheduled': JobStatus.SCHEDULED,
        'canceled': JobStatus.CANCELED,
    }
    status = status_map.get(rq_status, JobStatus.QUEUED)

    # Serialize args/kwargs/meta to JSON strings (flat!)
    args_json = json.dumps(list(job.args or []))
    kwargs_json = json.dumps(job.kwargs or {})
    meta_json = json.dumps(job.meta or {})

    # Serialize result to JSON string if available
    result_json = None
    if job.result is not None:
        try:
            result_json = json.dumps(job.result)
        except (TypeError, ValueError):
            # If result is not JSON serializable, convert to string
            result_json = json.dumps(str(job.result))

    # Get dependency IDs as comma-separated string
    dependency_ids = ""
    if hasattr(job, '_dependency_ids') and job._dependency_ids:
        dependency_ids = ",".join(job._dependency_ids)

    return RQJobModel(
        id=job.id,
        func_name=job.func_name or "unknown",
        queue=queue_name,
        status=status,
        created_at=job.created_at.isoformat() if job.created_at else "",
        enqueued_at=job.enqueued_at.isoformat() if job.enqueued_at else None,
        started_at=job.started_at.isoformat() if job.started_at else None,
        ended_at=job.ended_at.isoformat() if job.ended_at else None,
        worker_name=job.worker_name,
        timeout=job.timeout,
        result_ttl=job.result_ttl,
        failure_ttl=job.failure_ttl,
        result_json=result_json,
        exc_info=job.exc_info,
        args_json=args_json,
        kwargs_json=kwargs_json,
        meta_json=meta_json,
        dependency_ids=dependency_ids,
    )


def worker_to_model(worker: Worker) -> RQWorkerModel:
    """
    Convert RQ Worker to Pydantic RQWorkerModel.

    Args:
        worker: RQ Worker instance

    Returns:
        Validated RQWorkerModel instance
    """
    # Get worker state
    rq_state = worker.get_state()
    state_map = {
        'idle': WorkerState.IDLE,
        'busy': WorkerState.BUSY,
        'suspended': WorkerState.SUSPENDED,
    }
    state = state_map.get(rq_state, WorkerState.IDLE)

    # Get queues as comma-separated string (flat!)
    queue_names = [q.name for q in worker.queues]
    queues_str = ",".join(queue_names)

    # Get current job ID
    current_job_id = worker.get_current_job_id()

    # Use datetime.now() as fallback if timestamps are missing
    from datetime import datetime as dt
    birth = worker.birth_date if worker.birth_date else dt.now()
    last_heartbeat = worker.last_heartbeat if worker.last_heartbeat else dt.now()

    return RQWorkerModel(
        name=worker.name,
        state=state,
        queues=queues_str,
        current_job_id=current_job_id,
        birth=birth,
        last_heartbeat=last_heartbeat,
        successful_job_count=worker.successful_job_count,
        failed_job_count=worker.failed_job_count,
        total_working_time=worker.total_working_time,
    )


def queue_to_model(queue: Queue, queue_name: str) -> RQQueueModel:
    """
    Convert RQ Queue to Pydantic RQQueueModel.

    Args:
        queue: RQ Queue instance
        queue_name: Queue name

    Returns:
        Validated RQQueueModel instance
    """
    # Get job counts from registries
    queued_jobs = len(queue.get_job_ids())
    started_jobs = len(queue.started_job_registry)
    finished_jobs = len(queue.finished_job_registry)
    failed_jobs = len(queue.failed_job_registry)
    deferred_jobs = len(queue.deferred_job_registry)
    scheduled_jobs = len(queue.scheduled_job_registry)

    # Get worker count
    workers = Worker.all(queue=queue)
    worker_count = len(workers)

    # Get oldest job timestamp
    oldest_job_timestamp = None
    if queue.count > 0:
        try:
            oldest_job = queue.get_jobs(0, 1)[0]
            oldest_job_timestamp = oldest_job.created_at.isoformat() if oldest_job.created_at else None
        except (IndexError, AttributeError):
            pass

    # Get connection info (flat!)
    connection_host = None
    connection_port = None
    connection_db = None
    if hasattr(queue.connection, 'connection_pool'):
        pool = queue.connection.connection_pool
        connection_kwargs = pool.connection_kwargs
        connection_host = connection_kwargs.get('host', 'unknown')
        connection_port = connection_kwargs.get('port', 6379)
        connection_db = connection_kwargs.get('db', 0)

    return RQQueueModel(
        name=queue_name,
        is_async=queue.is_async,
        count=queue.count,
        queued_jobs=queued_jobs,
        started_jobs=started_jobs,
        finished_jobs=finished_jobs,
        failed_jobs=failed_jobs,
        deferred_jobs=deferred_jobs,
        scheduled_jobs=scheduled_jobs,
        workers=worker_count,
        oldest_job_timestamp=oldest_job_timestamp,
        connection_host=connection_host,
        connection_port=connection_port,
        connection_db=connection_db,
    )
