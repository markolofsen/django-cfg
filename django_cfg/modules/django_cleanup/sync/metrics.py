"""Outbox health as a plain dataclass, for the command, a dashboard or an alert."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Optional

from django.utils import timezone


@dataclass
class OutboxMetrics:
    pending: int = 0
    purge: int = 0
    failed: int = 0
    refused: int = 0
    done: int = 0
    external: int = 0
    oldest_pending_seconds: Optional[int] = None

    def as_dict(self) -> dict:
        return asdict(self)


def collect() -> OutboxMetrics:
    from django.db.models import Count, Min

    from ..models import StorageDeletion

    counts = {
        row["status"]: row["n"]
        for row in StorageDeletion.objects.filter(claimed_by="").values("status").annotate(n=Count("id"))
    }
    queue = StorageDeletion.objects.filter(
        claimed_by="", status__in=[StorageDeletion.Status.PENDING, StorageDeletion.Status.PURGE]
    ).aggregate(oldest=Min("created_at"))
    oldest = queue["oldest"]
    return OutboxMetrics(
        pending=counts.get("pending", 0),
        purge=counts.get("purge", 0),
        failed=counts.get("failed", 0),
        refused=counts.get("refused", 0),
        done=counts.get("done", 0),
        external=StorageDeletion.objects.exclude(claimed_by="").count(),
        oldest_pending_seconds=int((timezone.now() - oldest).total_seconds()) if oldest else None,
    )
