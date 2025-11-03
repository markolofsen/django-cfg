"""
Pydantic models for RQ Jobs.

Internal models for job validation and business logic.
NO NESTED JSON - all fields are flat!
"""

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class JobStatus(str, Enum):
    """Job status enumeration."""

    QUEUED = "queued"
    STARTED = "started"
    FINISHED = "finished"
    FAILED = "failed"
    DEFERRED = "deferred"
    SCHEDULED = "scheduled"
    CANCELED = "canceled"


class RQJobModel(BaseModel):
    """
    Internal model for RQ Job with validation.

    FLAT STRUCTURE - no nested objects!
    All timestamps are ISO strings, all complex types are flattened.
    """

    # Basic info
    id: str = Field(..., description="Job ID")
    func_name: str = Field(..., description="Function name (e.g., 'myapp.tasks.send_email')")
    queue: str = Field(..., description="Queue name")

    # Status
    status: JobStatus = Field(..., description="Current job status")

    # Timestamps (as ISO strings for flat JSON)
    created_at: str = Field(..., description="Creation timestamp (ISO 8601)")
    enqueued_at: Optional[str] = Field(None, description="Enqueue timestamp (ISO 8601)")
    started_at: Optional[str] = Field(None, description="Start timestamp (ISO 8601)")
    ended_at: Optional[str] = Field(None, description="End timestamp (ISO 8601)")

    # Worker info
    worker_name: Optional[str] = Field(None, description="Worker name if job is/was running")

    # Configuration (flat!)
    timeout: Optional[int] = Field(None, description="Job timeout in seconds")
    result_ttl: Optional[int] = Field(None, description="Result TTL in seconds")
    failure_ttl: Optional[int] = Field(None, description="Failure TTL in seconds")

    # Result/Error (as strings, not nested!)
    result_json: Optional[str] = Field(None, description="Job result as JSON string")
    exc_info: Optional[str] = Field(None, description="Exception info if failed")

    # Args/Kwargs (as JSON strings for flat structure)
    args_json: str = Field(default="[]", description="Function args as JSON string")
    kwargs_json: str = Field(default="{}", description="Function kwargs as JSON string")
    meta_json: str = Field(default="{}", description="Job metadata as JSON string")

    # Dependencies (comma-separated for flat structure)
    dependency_ids: str = Field(default="", description="Comma-separated dependency job IDs")

    @property
    def is_success(self) -> bool:
        """Check if job succeeded."""
        return self.status == JobStatus.FINISHED

    @property
    def is_failed(self) -> bool:
        """Check if job failed."""
        return self.status == JobStatus.FAILED

    @property
    def is_running(self) -> bool:
        """Check if job is running."""
        return self.status == JobStatus.STARTED

    def get_duration_seconds(self) -> Optional[float]:
        """Calculate job duration in seconds."""
        if not self.started_at or not self.ended_at:
            return None

        try:
            start = datetime.fromisoformat(self.started_at)
            end = datetime.fromisoformat(self.ended_at)
            return (end - start).total_seconds()
        except (ValueError, TypeError):
            return None

    class Config:
        """Pydantic config."""

        use_enum_values = True
