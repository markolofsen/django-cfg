"""RQ service for Streamlit admin.

Provides queue, worker, and job management.
"""

from api.generated.cfg.cfg__rq__rq_jobs.models import JobListRequest
from models.rq import JobInfo, QueueStats, ScheduledJob, WorkerInfo
from services.base import BaseService


class RQService(BaseService):
    """RQ job queue service."""

    def get_queues(self) -> list[QueueStats]:
        """Get all queue statistics."""

        def fetch() -> list[QueueStats]:
            queues = self.api.cfg_rq_queues.list()
            return [
                QueueStats(
                    name=q.name,
                    count=q.count,
                    queued=q.queued_jobs or 0,
                    started=q.started_jobs or 0,
                    finished=q.finished_jobs or 0,
                    failed=q.failed_jobs or 0,
                    workers=q.workers or 0,
                )
                for q in queues
            ]

        return self._safe_call("get_queues", fetch, [])

    def get_workers(self) -> list[WorkerInfo]:
        """Get all workers."""

        def fetch() -> list[WorkerInfo]:
            workers = self.api.cfg_rq_workers.list()
            return [
                WorkerInfo(
                    name=w.name,
                    state=w.state,
                    queues=w.queues or [],
                    current_job=w.current_job,
                    successful_jobs=w.successful_job_count or 0,
                    failed_jobs=w.failed_job_count or 0,
                    birth_date=w.birth,
                )
                for w in workers
            ]

        return self._safe_call("get_workers", fetch, [])

    def get_queue_jobs(self, queue: str, status: str = "all") -> list[JobInfo]:
        """Get jobs for a specific queue."""

        def fetch() -> list[JobInfo]:
            # list() returns PaginatedJobListList with .results
            paginated = self.api.cfg_rq_jobs.list(queue=queue, status=status if status != "all" else None)
            return [
                JobInfo(
                    id=j.id,
                    func_name=j.func_name,
                    created_at=j.created_at,
                    status=j.status,
                    queue=j.queue,
                    timeout=j.timeout,
                )
                for j in paginated.results
            ]

        return self._safe_call("get_queue_jobs", fetch, [])

    def get_schedules(self) -> list[ScheduledJob]:
        """Get scheduled jobs."""

        def fetch() -> list[ScheduledJob]:
            # list() returns PaginatedScheduledJobList with .results
            paginated = self.api.cfg_rq_schedules.list()
            return [
                ScheduledJob(
                    id=s.id,
                    func=s.func,
                    queue_name=s.queue_name,
                    scheduled_time=s.scheduled_time,
                    interval=s.interval,
                    cron=s.cron,
                    description=s.description,
                )
                for s in paginated.results
            ]

        return self._safe_call("get_schedules", fetch, [])

    def cancel_job(self, job_id: str) -> bool:
        """Cancel a job by ID."""

        def fetch() -> bool:
            # cancel_create requires JobListRequest with all required fields
            from datetime import datetime

            request = JobListRequest(
                id=job_id,
                func_name="unknown",
                created_at=datetime.now(),
                status="queued",
                queue="default",
                timeout=None,
            )
            self.api.cfg_rq_jobs.cancel_create(id=job_id, data=request)
            return True

        return self._safe_call("cancel_job", fetch, False)

    def requeue_job(self, job_id: str) -> bool:
        """Requeue a failed job."""

        def fetch() -> bool:
            from datetime import datetime

            request = JobListRequest(
                id=job_id,
                func_name="unknown",
                created_at=datetime.now(),
                status="failed",
                queue="default",
                timeout=None,
            )
            self.api.cfg_rq_jobs.requeue_create(id=job_id, data=request)
            return True

        return self._safe_call("requeue_job", fetch, False)
