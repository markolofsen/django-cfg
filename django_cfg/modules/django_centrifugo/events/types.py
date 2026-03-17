"""
django_centrifugo.events.types — Pydantic v2 types for D1 sync.

Field names match D1 column names exactly so D1Q._extract() pulls
values directly from model_dump() — no manual to_params() methods.

CentrifugoLogRow  — append-only insert for every publish / status transition
CentrifugoLogStatus — allowed status values
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


# ─────────────────────────────────────────────────────────────────────────────
# Status enum
# ─────────────────────────────────────────────────────────────────────────────

class CentrifugoLogStatus(str, Enum):
    """Allowed values for centrifugo_logs.status column."""

    PENDING  = "pending"
    SUCCESS  = "success"
    FAILED   = "failed"
    TIMEOUT  = "timeout"
    PARTIAL  = "partial"


# ─────────────────────────────────────────────────────────────────────────────
# Log row model
# ─────────────────────────────────────────────────────────────────────────────

class CentrifugoLogRow(BaseModel):
    """Typed model for one centrifugo_logs row → D1 append-only insert.

    All fields match CENTRIFUGO_LOGS_TABLE column names.
    Each row gets its own UUID id — no deduplication, no upsert.

    Status transitions (pending → success/failed/timeout/partial) are tracked
    by inserting a new row with the updated status — never UPDATE.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    id:             str = Field(default_factory=lambda: str(uuid.uuid4()))
    message_id:     str = Field(..., description="Unique publish identifier (app-generated UUID)")
    channel:        str = Field(..., description="Centrifugo channel name")
    data:           str = Field(default="{}", description="JSON payload as TEXT")

    wait_for_ack:   int = Field(default=0, description="0=fire-and-forget, 1=ACK mode")
    ack_timeout:    Optional[int] = None
    acks_received:  int = 0
    acks_expected:  Optional[int] = None

    status:         str = Field(default=CentrifugoLogStatus.PENDING.value)
    error_code:     Optional[str] = None
    error_message:  Optional[str] = None
    duration_ms:    Optional[int] = None

    is_notification: int = Field(default=1, description="1=notification publish")
    user_id:         Optional[str] = None
    caller_ip:       Optional[str] = None
    user_agent:      Optional[str] = None

    created_at:     str = Field(default_factory=_now_iso)
    completed_at:   Optional[str] = None

    @classmethod
    def create_pending(
        cls,
        *,
        message_id: str,
        channel: str,
        data: str = "{}",
        wait_for_ack: bool = False,
        ack_timeout: int | None = None,
        acks_expected: int | None = None,
        is_notification: bool = True,
        user_id: str | None = None,
        caller_ip: str | None = None,
        user_agent: str | None = None,
    ) -> "CentrifugoLogRow":
        """Create an initial pending log row when a publish is initiated."""
        return cls(
            message_id=message_id,
            channel=channel,
            data=data,
            wait_for_ack=int(wait_for_ack),
            ack_timeout=ack_timeout,
            acks_expected=acks_expected,
            status=CentrifugoLogStatus.PENDING.value,
            is_notification=int(is_notification),
            user_id=user_id,
            caller_ip=caller_ip,
            user_agent=user_agent,
        )

    @classmethod
    def create_transition(
        cls,
        *,
        message_id: str,
        channel: str,
        status: CentrifugoLogStatus,
        data: str = "{}",
        wait_for_ack: bool = False,
        acks_received: int = 0,
        acks_expected: int | None = None,
        error_code: str | None = None,
        error_message: str | None = None,
        duration_ms: int | None = None,
        is_notification: bool = True,
        user_id: str | None = None,
        caller_ip: str | None = None,
        user_agent: str | None = None,
    ) -> "CentrifugoLogRow":
        """Create a status-transition row (success/failed/timeout/partial).

        Inserts a new row — does NOT update the original pending row.
        """
        now = _now_iso()
        return cls(
            message_id=message_id,
            channel=channel,
            data=data,
            wait_for_ack=int(wait_for_ack),
            acks_received=acks_received,
            acks_expected=acks_expected,
            status=status.value,
            error_code=error_code,
            error_message=error_message[:500] if error_message else None,
            duration_ms=duration_ms,
            is_notification=int(is_notification),
            user_id=user_id,
            caller_ip=caller_ip,
            user_agent=user_agent,
            created_at=now,
            completed_at=now,
        )


__all__ = [
    "CentrifugoLogRow",
    "CentrifugoLogStatus",
]
