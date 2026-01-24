"""
Job management service for Django-RQ.

Provides business logic for job operations: list, get, cancel, requeue, delete.
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from rq.job import Job

from .cancellation import request_cancellation, force_stop_job
from .rq_converters import job_to_model

logger = logging.getLogger("django_cfg.rq.job_service")


@dataclass
class JobActionResult:
    """Result of a job action (cancel, requeue, delete)."""

    success: bool
    job_id: str | None
    action: str
    message: str
    error: str | None = None


@dataclass
class JobInfo:
    """Basic job information for list view."""

    id: str
    func_name: str
    status: str
    queue: str
    created_at: str | None
    started_at: str | None
    ended_at: str | None


@dataclass
class JobDetail:
    """Detailed job information."""

    id: str
    func_name: str
    args: list
    kwargs: dict
    created_at: str | None
    enqueued_at: str | None
    started_at: str | None
    ended_at: str | None
    status: str
    queue: str
    worker_name: str | None
    timeout: int | None
    result_ttl: int | None
    failure_ttl: int | None
    result: any
    exc_info: str | None
    meta: dict
    dependency_ids: list[str]


class JobService:
    """Service for managing RQ jobs."""

    def find_job(self, job_id: str) -> tuple["Job | None", str | None]:
        """
        Find a job by ID across all queues.

        Returns:
            Tuple of (Job, queue_name) or (None, None) if not found.
        """
        import django_rq
        from django.conf import settings
        from rq.job import Job

        if not hasattr(settings, "RQ_QUEUES"):
            return None, None

        for queue_name in settings.RQ_QUEUES.keys():
            try:
                queue = django_rq.get_queue(queue_name)
                job = Job.fetch(job_id, connection=queue.connection)
                return job, queue_name
            except Exception:
                continue

        return None, None

    def get_job_detail(self, job_id: str) -> JobDetail | None:
        """
        Get detailed information about a job.

        Returns:
            JobDetail or None if job not found.
        """
        job, queue_name = self.find_job(job_id)

        if not job:
            return None

        job_model = job_to_model(job, queue_name)

        return JobDetail(
            id=job_model.id,
            func_name=job_model.func_name,
            args=json.loads(job_model.args_json),
            kwargs=json.loads(job_model.kwargs_json),
            created_at=job_model.created_at,
            enqueued_at=job_model.enqueued_at,
            started_at=job_model.started_at,
            ended_at=job_model.ended_at,
            status=job_model.status,
            queue=job_model.queue,
            worker_name=job_model.worker_name,
            timeout=job_model.timeout,
            result_ttl=job_model.result_ttl,
            failure_ttl=job_model.failure_ttl,
            result=json.loads(job_model.result_json) if job_model.result_json else None,
            exc_info=job_model.exc_info,
            meta=json.loads(job_model.meta_json) if job_model.meta_json else {},
            dependency_ids=job_model.dependency_ids.split(",") if job_model.dependency_ids else [],
        )

    def list_jobs(
        self,
        queue_filter: str | None = None,
        status_filter: str | None = None,
        limit_per_registry: int = 100,
    ) -> list[JobInfo]:
        """
        List all jobs across all registries.

        Args:
            queue_filter: Only return jobs from this queue
            status_filter: Only return jobs with this status
            limit_per_registry: Max jobs per registry (default 100)

        Returns:
            List of JobInfo objects
        """
        import django_rq
        from django.conf import settings
        from rq.job import Job
        from rq.registry import (
            FinishedJobRegistry,
            FailedJobRegistry,
            StartedJobRegistry,
            DeferredJobRegistry,
            ScheduledJobRegistry,
        )

        all_jobs = []

        if not hasattr(settings, "RQ_QUEUES"):
            return all_jobs

        for queue_name in settings.RQ_QUEUES.keys():
            if queue_filter and queue_filter != queue_name:
                continue

            try:
                queue = django_rq.get_queue(queue_name)

                registries = {
                    "queued": {"jobs": queue.job_ids, "status": "queued"},
                    "started": {
                        "registry": StartedJobRegistry(queue_name, connection=queue.connection),
                        "status": "started",
                    },
                    "finished": {
                        "registry": FinishedJobRegistry(queue_name, connection=queue.connection),
                        "status": "finished",
                    },
                    "failed": {
                        "registry": FailedJobRegistry(queue_name, connection=queue.connection),
                        "status": "failed",
                    },
                    "deferred": {
                        "registry": DeferredJobRegistry(queue_name, connection=queue.connection),
                        "status": "deferred",
                    },
                    "scheduled": {
                        "registry": ScheduledJobRegistry(queue_name, connection=queue.connection),
                        "status": "scheduled",
                    },
                }

                for reg_data in registries.values():
                    if status_filter and status_filter != reg_data["status"]:
                        continue

                    if "registry" in reg_data:
                        job_ids = reg_data["registry"].get_job_ids()
                    else:
                        job_ids = reg_data["jobs"]

                    for job_id in job_ids[:limit_per_registry]:
                        try:
                            job = Job.fetch(job_id, connection=queue.connection)
                            job_model = job_to_model(job, queue_name)

                            all_jobs.append(
                                JobInfo(
                                    id=job_model.id,
                                    func_name=job_model.func_name,
                                    status=job_model.status,
                                    queue=queue_name,
                                    created_at=job_model.created_at,
                                    started_at=job_model.started_at,
                                    ended_at=job_model.ended_at,
                                )
                            )
                        except Exception:
                            continue

            except Exception as e:
                logger.debug(f"Failed to get jobs from queue {queue_name}: {e}")
                continue

        return all_jobs

    def cancel_job(self, job_id: str, force: bool = False) -> JobActionResult:
        """
        Cancel a job.

        For queued jobs: cancels immediately.
        For running jobs: sets cancellation flag (or force kills worker if force=True).

        Args:
            job_id: Job ID to cancel
            force: If True, send SIGTERM to worker (dangerous!)

        Returns:
            JobActionResult with success status
        """
        if force:
            success = force_stop_job(job_id)
            action = "force_stop"
        else:
            success = request_cancellation(job_id)
            action = "cancel"

        if not success:
            return JobActionResult(
                success=False,
                job_id=job_id,
                action=action,
                message=f"Job {job_id} not found or already finished",
                error="Job not found or already in terminal state",
            )

        return JobActionResult(
            success=True,
            job_id=job_id,
            action=action,
            message=f"Job {job_id} {action} requested",
        )

    def requeue_job(self, job_id: str) -> JobActionResult:
        """
        Requeue a failed job.

        Args:
            job_id: Job ID to requeue

        Returns:
            JobActionResult with success status
        """
        import django_rq
        from django.conf import settings

        job, _ = self.find_job(job_id)

        if not job:
            return JobActionResult(
                success=False,
                job_id=job_id,
                action="requeue",
                message=f"Job {job_id} not found",
                error="Job not found",
            )

        try:
            # Find queue and requeue
            for queue_name in settings.RQ_QUEUES.keys():
                try:
                    queue = django_rq.get_queue(queue_name)
                    queue.failed_job_registry.requeue(job_id)

                    return JobActionResult(
                        success=True,
                        job_id=job_id,
                        action="requeue",
                        message=f"Job {job_id} requeued successfully",
                    )
                except Exception:
                    continue

            return JobActionResult(
                success=False,
                job_id=job_id,
                action="requeue",
                message=f"Job {job_id} not found in failed registry",
                error="Job not in failed registry",
            )

        except Exception as e:
            logger.error(f"Failed to requeue job {job_id}: {e}")
            return JobActionResult(
                success=False,
                job_id=job_id,
                action="requeue",
                message=f"Failed to requeue job: {e}",
                error=str(e),
            )

    def delete_job(self, job_id: str) -> JobActionResult:
        """
        Delete a job.

        Args:
            job_id: Job ID to delete

        Returns:
            JobActionResult with success status
        """
        job, _ = self.find_job(job_id)

        if not job:
            return JobActionResult(
                success=False,
                job_id=job_id,
                action="delete",
                message=f"Job {job_id} not found",
                error="Job not found",
            )

        try:
            job.delete()
            return JobActionResult(
                success=True,
                job_id=job_id,
                action="delete",
                message=f"Job {job_id} deleted successfully",
            )
        except Exception as e:
            logger.error(f"Failed to delete job {job_id}: {e}")
            return JobActionResult(
                success=False,
                job_id=job_id,
                action="delete",
                message=f"Failed to delete job: {e}",
                error=str(e),
            )

    def list_jobs_by_registry(
        self,
        registry_name: str,
        queue_filter: str | None = None,
    ) -> list[JobInfo]:
        """
        List jobs from a specific registry.

        Args:
            registry_name: One of 'failed', 'finished', 'deferred', 'started'
            queue_filter: Only return jobs from this queue

        Returns:
            List of JobInfo objects
        """
        import django_rq
        from django.conf import settings
        from rq.job import Job
        from rq.registry import (
            FinishedJobRegistry,
            FailedJobRegistry,
            StartedJobRegistry,
            DeferredJobRegistry,
        )

        registry_classes = {
            "failed": FailedJobRegistry,
            "finished": FinishedJobRegistry,
            "started": StartedJobRegistry,
            "deferred": DeferredJobRegistry,
        }

        if registry_name not in registry_classes:
            return []

        all_jobs = []
        queue_names = list(settings.RQ_QUEUES.keys()) if hasattr(settings, "RQ_QUEUES") else []

        if queue_filter:
            queue_names = [q for q in queue_names if q == queue_filter]

        for queue_name in queue_names:
            try:
                queue = django_rq.get_queue(queue_name)
                registry = registry_classes[registry_name](queue_name, connection=queue.connection)
                job_ids = registry.get_job_ids()

                for job_id in job_ids:
                    try:
                        job = Job.fetch(job_id, connection=queue.connection)
                        job_model = job_to_model(job, queue_name)

                        all_jobs.append(
                            JobInfo(
                                id=job_model.id,
                                func_name=job_model.func_name,
                                status=job_model.status,
                                queue=queue_name,
                                created_at=job_model.created_at,
                                started_at=job_model.started_at,
                                ended_at=job_model.ended_at,
                            )
                        )
                    except Exception:
                        continue

            except Exception as e:
                logger.debug(f"Failed to get {registry_name} jobs for queue {queue_name}: {e}")

        return all_jobs

    def requeue_all_failed(self, queue_name: str) -> JobActionResult:
        """
        Requeue all failed jobs in a queue.

        Args:
            queue_name: Queue name

        Returns:
            JobActionResult with count of requeued jobs
        """
        import django_rq

        try:
            queue = django_rq.get_queue(queue_name)
            failed_registry = queue.failed_job_registry
            job_ids = failed_registry.get_job_ids()
            count = len(job_ids)

            for job_id in job_ids:
                try:
                    failed_registry.requeue(job_id)
                except Exception as e:
                    logger.debug(f"Failed to requeue job {job_id}: {e}")

            return JobActionResult(
                success=True,
                job_id=None,
                action="requeue_all",
                message=f"Requeued {count} failed jobs from queue '{queue_name}'",
            )

        except Exception as e:
            logger.error(f"Failed to requeue all failed jobs: {e}")
            return JobActionResult(
                success=False,
                job_id=None,
                action="requeue_all",
                message=f"Failed to requeue jobs: {e}",
                error=str(e),
            )

    def clear_registry(self, registry_name: str, queue_name: str) -> JobActionResult:
        """
        Clear all jobs from a registry.

        Args:
            registry_name: One of 'failed', 'finished'
            queue_name: Queue name

        Returns:
            JobActionResult with count of cleared jobs
        """
        import django_rq
        from rq.job import Job
        from rq.registry import FailedJobRegistry, FinishedJobRegistry

        registry_classes = {
            "failed": FailedJobRegistry,
            "finished": FinishedJobRegistry,
        }

        if registry_name not in registry_classes:
            return JobActionResult(
                success=False,
                job_id=None,
                action=f"clear_{registry_name}",
                message=f"Unknown registry: {registry_name}",
                error="Invalid registry name",
            )

        try:
            queue = django_rq.get_queue(queue_name)
            registry = registry_classes[registry_name](queue_name, connection=queue.connection)
            job_ids = registry.get_job_ids()
            count = len(job_ids)

            for job_id in job_ids:
                try:
                    job = Job.fetch(job_id, connection=queue.connection)
                    registry.remove(job, delete_job=True)
                except Exception as e:
                    logger.debug(f"Failed to delete job {job_id}: {e}")

            return JobActionResult(
                success=True,
                job_id=None,
                action=f"clear_{registry_name}",
                message=f"Cleared {count} {registry_name} jobs from queue '{queue_name}'",
            )

        except Exception as e:
            logger.error(f"Failed to clear {registry_name} registry: {e}")
            return JobActionResult(
                success=False,
                job_id=None,
                action=f"clear_{registry_name}",
                message=f"Failed to clear registry: {e}",
                error=str(e),
            )
