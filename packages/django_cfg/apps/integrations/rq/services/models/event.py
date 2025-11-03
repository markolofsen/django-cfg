"""
Pydantic models for RQ Events (Centrifugo WebSocket).

Internal models for event validation before publishing to Centrifugo.
NO NESTED JSON - all fields are flat!
"""

from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class EventType(str, Enum):
    """Event type enumeration for WebSocket events."""

    # Job events
    JOB_QUEUED = "job_queued"
    JOB_STARTED = "job_started"
    JOB_FINISHED = "job_finished"
    JOB_FAILED = "job_failed"
    JOB_CANCELED = "job_canceled"
    JOB_REQUEUED = "job_requeued"
    JOB_DELETED = "job_deleted"

    # Queue events
    QUEUE_PURGED = "queue_purged"
    QUEUE_EMPTIED = "queue_emptied"

    # Worker events
    WORKER_STARTED = "worker_started"
    WORKER_STOPPED = "worker_stopped"
    WORKER_HEARTBEAT = "worker_heartbeat"


class JobEventModel(BaseModel):
    """
    Job event for Centrifugo publishing.

    FLAT STRUCTURE - no nested objects!
    Published to channel: rq:jobs
    """

    # Event meta
    event_type: EventType = Field(..., description="Event type")
    timestamp: str = Field(..., description="Event timestamp (ISO 8601)")

    # Job info
    job_id: str = Field(..., description="Job ID")
    queue: str = Field(..., description="Queue name")
    func_name: Optional[str] = Field(None, description="Function name")

    # Status info
    status: Optional[str] = Field(None, description="Job status")
    worker_name: Optional[str] = Field(None, description="Worker name")

    # Result/Error (as JSON strings for flat structure)
    result_json: Optional[str] = Field(None, description="Job result as JSON string")
    error: Optional[str] = Field(None, description="Error message if failed")

    # Timing
    duration_seconds: Optional[float] = Field(None, description="Job duration in seconds")

    class Config:
        """Pydantic config."""

        use_enum_values = True


class QueueEventModel(BaseModel):
    """
    Queue event for Centrifugo publishing.

    FLAT STRUCTURE - no nested objects!
    Published to channel: rq:queues
    """

    # Event meta
    event_type: EventType = Field(..., description="Event type")
    timestamp: str = Field(..., description="Event timestamp (ISO 8601)")

    # Queue info
    queue: str = Field(..., description="Queue name")

    # Event-specific data
    purged_count: Optional[int] = Field(None, description="Number of jobs purged")
    job_count: Optional[int] = Field(None, description="Current job count")

    class Config:
        """Pydantic config."""

        use_enum_values = True


class WorkerEventModel(BaseModel):
    """
    Worker event for Centrifugo publishing.

    FLAT STRUCTURE - no nested objects!
    Published to channel: rq:workers
    """

    # Event meta
    event_type: EventType = Field(..., description="Event type")
    timestamp: str = Field(..., description="Event timestamp (ISO 8601)")

    # Worker info
    worker_name: str = Field(..., description="Worker name")
    queues: str = Field(..., description="Comma-separated queue names")

    # State info
    state: Optional[str] = Field(None, description="Worker state (idle/busy/suspended)")
    current_job_id: Optional[str] = Field(None, description="Current job ID if busy")

    # Stats
    successful_job_count: Optional[int] = Field(None, description="Successful job count")
    failed_job_count: Optional[int] = Field(None, description="Failed job count")
    total_working_time: Optional[float] = Field(None, description="Total working time in seconds")

    class Config:
        """Pydantic config."""

        use_enum_values = True
