"""RQ jobs. Importable by dotted path: ``django_cfg.modules.django_notion.tasks.<name>``."""

from __future__ import annotations

import logging
from datetime import timedelta

from django.utils import timezone

from . import conf, delivery, notify, outbox
from .models import NotionOutbox

logger = logging.getLogger("django_cfg.modules.django_notion")


def deliver_outbox(row_id: int) -> str:
    return delivery.deliver(row_id)


def notify_outbox(row_id: int) -> str:
    return notify.notify(row_id)


def sweep_outbox(limit: int = 200) -> dict:
    """Re-queue due rows and rows stuck in 'sending', purge old sent rows."""
    cfg = conf.get_notion_config()
    now = timezone.now()
    Status = NotionOutbox.Status
    stuck = NotionOutbox.objects.filter(
        status=Status.SENDING, locked_at__lt=now - timedelta(seconds=cfg.stuck_after_seconds)
    ).update(status=Status.FAILED, next_attempt_at=now, locked_at=None, maybe_created=True)
    due = list(
        NotionOutbox.objects.filter(status__in=[Status.PENDING, Status.FAILED], next_attempt_at__lte=now)
        .order_by("next_attempt_at").values_list("pk", flat=True)[:limit]
    )
    queued = sum(1 for pk in due if outbox.enqueue(pk))
    notify_due = notify.due_ids(cfg, limit)
    notify_queued = sum(1 for pk in notify_due if outbox.enqueue_notify(pk))
    purged, _ = NotionOutbox.objects.filter(
        status=Status.SENT, sent_at__lt=now - timedelta(days=cfg.retention_days)
    ).delete()
    return {"stuck": stuck, "due": len(due), "queued": queued, "notify_due": len(notify_due), "notify_queued": notify_queued, "purged": purged}
