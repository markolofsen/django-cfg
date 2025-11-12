"""
Pydantic models for RQ Workers.

Internal models for worker validation and business logic.
NO NESTED JSON - all fields are flat!
"""

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class WorkerState(str, Enum):
    """Worker state enumeration."""

    IDLE = "idle"
    BUSY = "busy"
    SUSPENDED = "suspended"


class RQWorkerModel(BaseModel):
    """
    Internal model for RQ Worker.

    FLAT STRUCTURE - no nested objects!
    Queues are comma-separated string, timestamps are datetime objects.
    Use model_dump(mode='json') to serialize timestamps to ISO 8601 strings.
    """

    # Basic info
    name: str = Field(..., description="Worker name/ID")
    state: WorkerState = Field(..., description="Worker state (idle/busy/suspended)")

    # Queues (comma-separated for flat structure)
    queues: str = Field(..., description="Comma-separated queue names (e.g., 'default,high,low')")

    # Current job
    current_job_id: Optional[str] = Field(None, description="Current job ID if busy")

    # Timestamps (as datetime objects for proper type safety)
    birth: datetime = Field(..., description="Worker start time")
    last_heartbeat: datetime = Field(..., description="Last heartbeat timestamp")

    # Statistics
    successful_job_count: int = Field(default=0, ge=0, description="Total successful jobs")
    failed_job_count: int = Field(default=0, ge=0, description="Total failed jobs")
    total_working_time: float = Field(default=0.0, ge=0.0, description="Total working time in seconds")

    @property
    def is_alive(self) -> bool:
        """
        Check if worker is alive.

        Worker is considered alive if heartbeat was within last 60 seconds.
        """
        try:
            now = datetime.now(self.last_heartbeat.tzinfo) if self.last_heartbeat.tzinfo else datetime.now()
            delta = (now - self.last_heartbeat).total_seconds()
            return delta < 60
        except (ValueError, TypeError, AttributeError):
            return False

    @property
    def is_busy(self) -> bool:
        """Check if worker is busy."""
        return self.state == WorkerState.BUSY

    @property
    def is_idle(self) -> bool:
        """Check if worker is idle."""
        return self.state == WorkerState.IDLE

    def get_uptime_seconds(self) -> Optional[float]:
        """Calculate worker uptime in seconds."""
        try:
            now = datetime.now(self.birth.tzinfo) if self.birth.tzinfo else datetime.now()
            return (now - self.birth).total_seconds()
        except (ValueError, TypeError, AttributeError):
            return None

    def get_queue_list(self) -> list[str]:
        """Get list of queue names."""
        return [q.strip() for q in self.queues.split(",") if q.strip()]

    @property
    def total_job_count(self) -> int:
        """Total jobs processed (successful + failed)."""
        return self.successful_job_count + self.failed_job_count

    @property
    def success_rate(self) -> float:
        """Calculate success rate (0-100%)."""
        total = self.total_job_count
        if total == 0:
            return 0.0
        return (self.successful_job_count / total) * 100

    class Config:
        """Pydantic config."""

        use_enum_values = True
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }
