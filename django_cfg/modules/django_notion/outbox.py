"""Writing outbox rows and queueing them. Nothing here may raise into the code that saved the lead."""

from __future__ import annotations

import logging
from typing import Optional

from django.db import transaction

from . import conf
from .enrich import enrich, with_project
from .lead import NotionLead

logger = logging.getLogger("django_cfg.modules.django_notion")

DELIVER_TASK = "django_cfg.modules.django_notion.tasks.deliver_outbox"
NOTIFY_TASK = "django_cfg.modules.django_notion.tasks.notify_outbox"


def make_key(project: str, instance) -> str:
    return f"{project}:{instance._meta.label_lower}:{instance.pk}"


def record(key: str, target: str, lead: NotionLead):
    """Create the outbox row (idempotent on ``key``). Runs in a savepoint so a failure cannot poison the caller's transaction."""
    from .models import NotionOutbox

    with transaction.atomic():
        row, _ = NotionOutbox.objects.get_or_create(
            key=key, defaults={"target": target, "payload": lead.model_dump(mode="json")}
        )
    return row


def enqueue(row_id: int) -> bool:
    """Queue a delivery job. False when Redis/RQ is down: the sweeper picks the row up later."""
    try:
        import django_rq

        cfg = conf.get_notion_config()
        django_rq.get_queue(cfg.queue).enqueue(DELIVER_TASK, row_id, job_timeout=120)
        return True
    except Exception as exc:
        logger.warning("django_notion: could not queue outbox row %s (%s); the sweeper will retry", row_id, type(exc).__name__)
        return False


def enqueue_notify(row_id: int) -> bool:
    """Queue the Telegram / admin-email job (independent of delivery). False when off or Redis is down: the sweeper retries."""
    try:
        import django_rq

        cfg = conf.get_notion_config()
        if not (cfg.notify_telegram or cfg.notify_email or cfg.acknowledge):
            return False
        django_rq.get_queue(cfg.queue).enqueue(NOTIFY_TASK, row_id, job_timeout=120)
        return True
    except Exception as exc:
        logger.warning("django_notion: could not queue notification for row %s (%s); the sweeper will retry", row_id, type(exc).__name__)
        return False


def _after_commit(row_id: int) -> None:
    enqueue(row_id)
    enqueue_notify(row_id)


def capture(instance, lead: NotionLead, target: Optional[str], *, project: Optional[str] = None) -> None:
    """Record ``lead`` for ``target`` and queue delivery after the surrounding transaction commits. Never raises."""
    try:
        cfg = conf.get_notion_config()
        if target not in cfg.targets:
            raise ValueError(f"unknown Notion target {target!r}; configured: {sorted(cfg.targets)}")
        key = make_key(project or conf.project_name(cfg), instance)
        row = record(key, target, enrich(lead) if cfg.enrich else with_project(lead))
        transaction.on_commit(lambda: _after_commit(row.pk))
    except Exception:
        logger.exception("django_notion: lead %s was NOT recorded for Notion (the lead itself is saved)", getattr(instance, "pk", "?"))
