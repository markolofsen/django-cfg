"""RQ (Redis Queue) data models for Streamlit admin.

Pydantic v2 models for queues, workers, and jobs.
"""

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


class JobStatus(str, Enum):
    """Job execution status."""

    QUEUED = "queued"
    STARTED = "started"
    FINISHED = "finished"
    FAILED = "failed"
    DEFERRED = "deferred"
    SCHEDULED = "scheduled"


class QueueStats(BaseModel):
    """Queue statistics."""

    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid",
        use_enum_values=True,
    )

    name: str
    count: int = Field(ge=0, default=0)
    queued: int = Field(ge=0, default=0)
    started: int = Field(ge=0, default=0)
    finished: int = Field(ge=0, default=0)
    failed: int = Field(ge=0, default=0)
    workers: int = Field(ge=0, default=0)


class WorkerInfo(BaseModel):
    """Worker information."""

    model_config = ConfigDict(validate_assignment=True, extra="forbid")

    name: str
    state: str
    queues: list[str] = []
    current_job: str | None = None
    successful_jobs: int = Field(ge=0, default=0)
    failed_jobs: int = Field(ge=0, default=0)
    birth_date: datetime | None = None


class JobInfo(BaseModel):
    """Job information."""

    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid",
        use_enum_values=True,
    )

    id: str
    func_name: str
    status: str  # Use str to match API (queued/started/finished/failed)
    queue: str
    created_at: datetime
    timeout: int | None = None


class ScheduledJob(BaseModel):
    """Scheduled job information."""

    model_config = ConfigDict(validate_assignment=True, extra="forbid")

    id: str
    func: str
    queue_name: str
    scheduled_time: datetime | None = None
    interval: int | None = None
    cron: str | None = None
    description: str | None = None
