"""
Pydantic models for RQ Queues.

Internal models for queue validation and business logic.
NO NESTED JSON - all fields are flat!
"""

from typing import Optional

from pydantic import BaseModel, Field


class RQQueueModel(BaseModel):
    """
    Internal model for RQ Queue statistics.

    FLAT STRUCTURE - no nested objects!
    All fields are primitive types.
    """

    # Basic info
    name: str = Field(..., description="Queue name")
    is_async: bool = Field(default=True, description="Queue is in async mode")

    # Job counts by status
    count: int = Field(default=0, ge=0, description="Total jobs in queue")
    queued_jobs: int = Field(default=0, ge=0, description="Jobs waiting to be processed")
    started_jobs: int = Field(default=0, ge=0, description="Jobs currently being processed")
    finished_jobs: int = Field(default=0, ge=0, description="Completed jobs")
    failed_jobs: int = Field(default=0, ge=0, description="Failed jobs")
    deferred_jobs: int = Field(default=0, ge=0, description="Deferred jobs")
    scheduled_jobs: int = Field(default=0, ge=0, description="Scheduled jobs")

    # Worker info
    workers: int = Field(default=0, ge=0, description="Number of workers for this queue")

    # Metadata
    oldest_job_timestamp: Optional[str] = Field(
        None, description="Timestamp of oldest job in queue (ISO 8601)"
    )

    # Connection info (flat!)
    connection_host: Optional[str] = Field(None, description="Redis host")
    connection_port: Optional[int] = Field(None, description="Redis port")
    connection_db: Optional[int] = Field(None, description="Redis DB number")

    @property
    def total_jobs(self) -> int:
        """Calculate total jobs across all statuses."""
        return (
            self.queued_jobs
            + self.started_jobs
            + self.finished_jobs
            + self.failed_jobs
            + self.deferred_jobs
            + self.scheduled_jobs
        )

    @property
    def completed_jobs(self) -> int:
        """Total completed jobs (finished + failed)."""
        return self.finished_jobs + self.failed_jobs

    @property
    def failure_rate(self) -> float:
        """Calculate failure rate percentage (0-100%)."""
        completed = self.completed_jobs
        if completed == 0:
            return 0.0
        return (self.failed_jobs / completed) * 100

    @property
    def is_empty(self) -> bool:
        """Check if queue is empty."""
        return self.count == 0

    @property
    def has_workers(self) -> bool:
        """Check if queue has any workers."""
        return self.workers > 0

    @property
    def is_healthy(self) -> bool:
        """
        Check if queue is healthy.

        Queue is healthy if:
        - Has workers
        - Failure rate < 50%
        - Not too many queued jobs (< 1000)
        """
        return self.has_workers and self.failure_rate < 50 and self.queued_jobs < 1000
