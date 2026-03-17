"""
django_centrifugo.streamlit.models.d1 — display dataclasses for Streamlit pages.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class PublishLogRow:
    """Single row from centrifugo_logs for Streamlit display."""

    id: str
    message_id: str
    channel: str
    status: str
    wait_for_ack: bool
    acks_received: int
    duration_ms: int | None
    error_code: str
    error_message: str
    is_notification: bool
    user_id: str | None
    caller_ip: str | None
    created_at: str
    completed_at: str | None

    @classmethod
    def from_d1(cls, row: dict[str, Any]) -> "PublishLogRow":
        return cls(
            id=row.get("id", ""),
            message_id=row.get("message_id", ""),
            channel=row.get("channel", ""),
            status=row.get("status", ""),
            wait_for_ack=bool(row.get("wait_for_ack", 0)),
            acks_received=int(row.get("acks_received") or 0),
            duration_ms=row.get("duration_ms"),
            error_code=row.get("error_code") or "",
            error_message=row.get("error_message") or "",
            is_notification=bool(row.get("is_notification", 1)),
            user_id=row.get("user_id"),
            caller_ip=row.get("caller_ip"),
            created_at=row.get("created_at", ""),
            completed_at=row.get("completed_at"),
        )

    def to_display_dict(self) -> dict[str, Any]:
        dur = f"{self.duration_ms}ms" if self.duration_ms is not None else ""
        return {
            "_id":        self.id,
            "created_at": self.created_at[:19] if self.created_at else "",
            "channel":    self.channel,
            "status":     self.status,
            "ack":        "✓" if self.wait_for_ack else "",
            "acks":       self.acks_received,
            "duration":   dur,
            "message_id": self.message_id[:16] + "…" if len(self.message_id) > 16 else self.message_id,
        }


__all__ = ["PublishLogRow"]
