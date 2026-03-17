"""
django_rq.events.types — Pydantic v2 types for D1 sync.

Field names match D1 column names exactly so D1Q._extract() pulls
values directly from model_dump() — no manual to_params() methods.

RQJobEvent     — append-only insert for every job state transition
RQWorkerStats  — append-only insert for every worker heartbeat
"""

from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


# ─────────────────────────────────────────────────────────────────────────────
# Job events
# ─────────────────────────────────────────────────────────────────────────────

class RQJobEvent(BaseModel):
    """Typed model for one RQ job state-change event → D1 append-only insert.

    All fields match RQ_JOB_EVENTS_TABLE column names.
    Each event gets its own UUID id — no deduplication, no upsert.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    id:         str = Field(default_factory=lambda: str(uuid.uuid4()))
    job_id:     str = Field(..., description="RQ job.id")
    queue:      str = Field(..., description="Queue name (job.origin)")
    func_name:  str = ""

    event_type: str = Field(..., description="JOB_QUEUED|JOB_STARTED|JOB_FINISHED|JOB_FAILED|JOB_CANCELED")
    status:     str = Field(..., description="queued|started|finished|failed|canceled")

    worker_name:      Optional[str] = None
    error_message:    Optional[str] = None   # max 2KB
    stack_trace:      Optional[str] = None   # max 10KB
    duration_seconds: Optional[float] = None
    timeout_seconds:  Optional[int] = None

    extra:      str = "{}"   # JSON string: args_preview, meta

    created_at:  str = Field(default_factory=_now_iso)
    finished_at: Optional[str] = None

    @classmethod
    def from_rq_job(
        cls,
        job: Any,
        event_type: str,
        *,
        worker_name: str | None = None,
        exc_value: Any = None,
        exc_tb: Any = None,
    ) -> "RQJobEvent":
        """Build from an RQ Job object."""
        import traceback as tb_module

        now = _now_iso()

        try:
            func_name: str = job.func_name or ""
        except Exception:
            func_name = "<DeserializationError>"

        try:
            job_id: str = job.id or ""
        except Exception:
            job_id = ""

        try:
            queue: str = job.origin or "default"
        except Exception:
            queue = "default"

        # Determine status from event_type
        _STATUS_MAP = {
            "JOB_QUEUED":   "queued",
            "JOB_STARTED":  "started",
            "JOB_FINISHED": "finished",
            "JOB_FAILED":   "failed",
            "JOB_CANCELED": "canceled",
        }
        status = _STATUS_MAP.get(event_type, "unknown")

        # Duration (only meaningful for FINISHED/FAILED)
        duration_seconds: Optional[float] = None
        finished_at: Optional[str] = None
        if event_type in ("JOB_FINISHED", "JOB_FAILED"):
            finished_at = now
            try:
                if job.started_at and job.ended_at:
                    delta = job.ended_at - job.started_at
                    duration_seconds = delta.total_seconds()
            except Exception:
                pass

        # Timeout
        timeout_seconds: Optional[int] = None
        try:
            timeout_seconds = int(job.timeout) if job.timeout else None
        except Exception:
            pass

        # Error info
        error_message: Optional[str] = None
        stack_trace: Optional[str] = None
        if exc_value is not None:
            error_message = str(exc_value)[:2000]
        if exc_tb is not None:
            stack_trace = "".join(tb_module.format_exception(type(exc_value), exc_value, exc_tb))[:10000]

        # Extra: args preview + meta
        extra_dict: dict = {}
        try:
            meta = getattr(job, "meta", {}) or {}
            if meta:
                extra_dict["meta"] = dict(meta)
        except Exception:
            pass
        try:
            desc = job.description or ""
            if desc:
                extra_dict["description"] = desc[:200]
        except Exception:
            pass

        extra_str = json.dumps(extra_dict, ensure_ascii=False, default=str)[:3000]

        return cls(
            job_id=job_id,
            queue=queue,
            func_name=func_name[:300],
            event_type=event_type,
            status=status,
            worker_name=(worker_name or "")[:200] or None,
            error_message=error_message,
            stack_trace=stack_trace,
            duration_seconds=duration_seconds,
            timeout_seconds=timeout_seconds,
            extra=extra_str,
            created_at=now,
            finished_at=finished_at,
        )


# ─────────────────────────────────────────────────────────────────────────────
# Worker heartbeats
# ─────────────────────────────────────────────────────────────────────────────

class RQWorkerStats(BaseModel):
    """Typed model for one worker heartbeat snapshot → D1 append-only insert.

    All fields match RQ_WORKER_HEARTBEATS_TABLE column names.
    Each heartbeat gets its own UUID id.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    id:          str = Field(default_factory=lambda: str(uuid.uuid4()))
    worker_name: str = Field(..., description="Worker.name")
    queues:      str = Field(..., description="Comma-separated queue names")
    state:       str = Field(..., description="idle|busy|suspended")

    current_job_id:             Optional[str] = None
    successful_job_count:       int = 0
    failed_job_count:           int = 0
    total_working_time_seconds: float = 0.0

    heartbeat_at: str = Field(default_factory=_now_iso)

    @classmethod
    def from_rq_worker(cls, worker: Any) -> "RQWorkerStats":
        """Build from an RQ Worker object."""
        try:
            worker_name: str = worker.name or ""
        except Exception:
            worker_name = ""

        try:
            queue_names = [q.name for q in worker.queues]
            queues_str = ",".join(queue_names)
        except Exception:
            queues_str = ""

        try:
            state_raw = worker.get_state()
            state: str = str(state_raw) if state_raw else "idle"
        except Exception:
            state = "idle"

        try:
            current_job_id: Optional[str] = worker.get_current_job_id()
        except Exception:
            current_job_id = None

        try:
            successful_job_count = int(worker.successful_job_count or 0)
        except Exception:
            successful_job_count = 0

        try:
            failed_job_count = int(worker.failed_job_count or 0)
        except Exception:
            failed_job_count = 0

        try:
            total_working_time = float(worker.total_working_time or 0.0)
        except Exception:
            total_working_time = 0.0

        return cls(
            worker_name=worker_name[:200],
            queues=queues_str[:500],
            state=state[:20],
            current_job_id=(current_job_id or None),
            successful_job_count=successful_job_count,
            failed_job_count=failed_job_count,
            total_working_time_seconds=total_working_time,
        )


__all__ = [
    "RQJobEvent",
    "RQWorkerStats",
]
