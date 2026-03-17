"""
django_rq.streamlit.models — dataclasses for D1-backed RQ Streamlit pages.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class JobEventRow:
    """A single row from rq_job_events D1 table."""

    id: str
    job_id: str
    queue: str
    func_name: str
    event_type: str
    status: str
    worker_name: str
    error_message: str
    stack_trace: str
    duration_seconds: float | None
    created_at: str
    finished_at: str | None

    @classmethod
    def from_d1(cls, row: dict[str, Any]) -> "JobEventRow":
        return cls(
            id=row.get("id", ""),
            job_id=row.get("job_id", ""),
            queue=row.get("queue", ""),
            func_name=row.get("func_name", ""),
            event_type=row.get("event_type", ""),
            status=row.get("status", ""),
            worker_name=row.get("worker_name") or "",
            error_message=row.get("error_message") or "",
            stack_trace=row.get("stack_trace") or "",
            duration_seconds=row.get("duration_seconds"),
            created_at=row.get("created_at", ""),
            finished_at=row.get("finished_at"),
        )

    def to_display_dict(self) -> dict[str, Any]:
        dur = f"{self.duration_seconds:.1f}s" if self.duration_seconds is not None else ""
        return {
            "_id": self.id,  # hidden key for deterministic row matching
            "created_at": self.created_at[:19] if self.created_at else "",
            "queue": self.queue,
            "func_name": self.func_name.split(".")[-1] if self.func_name else "",
            "status": self.status,
            "duration": dur,
            "worker_name": self.worker_name,
        }


@dataclass
class WorkerRow:
    """A single row from rq_worker_heartbeats D1 table."""

    worker_name: str
    queues: str
    state: str
    current_job_id: str | None
    successful_job_count: int
    failed_job_count: int
    total_working_time_seconds: float
    heartbeat_at: str

    @classmethod
    def from_d1(cls, row: dict[str, Any]) -> "WorkerRow":
        return cls(
            worker_name=row.get("worker_name", ""),
            queues=row.get("queues", ""),
            state=row.get("state", "idle"),
            current_job_id=row.get("current_job_id"),
            successful_job_count=int(row.get("successful_job_count") or 0),
            failed_job_count=int(row.get("failed_job_count") or 0),
            total_working_time_seconds=float(row.get("total_working_time_seconds") or 0),
            heartbeat_at=row.get("heartbeat_at", ""),
        )

    def to_display_dict(self) -> dict[str, Any]:
        return {
            "worker_name": self.worker_name,
            "state": self.state,
            "queues": self.queues,
            "current_job_id": self.current_job_id or "",
            "successful": self.successful_job_count,
            "failed": self.failed_job_count,
            "last_heartbeat": self.heartbeat_at[:19] if self.heartbeat_at else "",
        }


__all__ = ["JobEventRow", "WorkerRow"]
