"""Delivering one outbox row: claim, create the page, record the outcome. Never raises."""

from __future__ import annotations

import logging
from datetime import timedelta
from typing import Any, Optional, Tuple

from django.db.models import F
from django.utils import timezone

from . import client as client_mod
from . import conf, keys
from .exceptions import NotionConfigError
from .lead import NotionLead
from .models import NotionOutbox
from .properties import _build, details_children

logger = logging.getLogger("django_cfg.modules.django_notion")

Status = NotionOutbox.Status
PERMANENT_CODES = {"validation_error", "invalid_json", "invalid_request", "invalid_request_url"}


def _classify(exc: Exception) -> Tuple[str, Optional[float], bool]:
    """-> (kind, retry_after_seconds, ambiguous). kind: 'rate' | 'permanent' | 'retry'."""
    status = getattr(exc, "status", None)
    code = str(getattr(exc, "code", "") or "")
    if status == 429 or code == "rate_limited":
        headers = getattr(exc, "headers", None)
        raw = headers.get("retry-after") if headers is not None else None
        try:
            return "rate", max(float(raw), 0.0), False
        except (TypeError, ValueError):
            return "rate", 5.0, False
    if isinstance(status, int) and 400 <= status < 500 and code in PERMANENT_CODES:
        return "permanent", None, False
    if isinstance(status, int) and 400 <= status < 500:
        return "retry", None, False  # 401/403/404/409: config or access, a person may fix it
    return "retry", None, True  # timeouts, 5xx, network: Notion may have created the page


def _safe_message(exc: Exception) -> str:
    text = getattr(exc, "message", None) or str(exc)
    return f"{type(exc).__name__}: {text}"[:2000]


def _claim(row_id: int) -> bool:
    now = timezone.now()
    n = NotionOutbox.objects.filter(
        pk=row_id, status__in=[Status.PENDING, Status.FAILED], next_attempt_at__lte=now
    ).update(status=Status.SENDING, locked_at=now, attempts=F("attempts") + 1)
    return n == 1


def _find_existing(client, data_source_id: str, column: Optional[str], key: str) -> Optional[str]:
    if not column:
        return None
    try:
        res = client.data_sources.query(
            data_source_id, filter={"property": column, "rich_text": {"equals": key}}, page_size=1
        )
        results = res.get("results") or []
        return results[0]["id"] if results else None
    except Exception:
        return None  # no Read content: fall back to at-least-once


def deliver(row_id: int) -> str:
    """Deliver one row. Returns the row's final status for this attempt (or 'skipped')."""
    if not _claim(row_id):
        return "skipped"
    row = NotionOutbox.objects.get(pk=row_id)
    try:
        if row.notion_page_id:  # created earlier, only the bookkeeping was lost
            return _mark_sent(row, row.notion_page_id)
        cfg = conf.get_notion_config()
        target = cfg.targets.get(row.target)
        if target is None:
            raise NotionConfigError(f"target {row.target!r} is not configured")
        client = client_mod.get_client(target)
        data_source_id = client_mod.resolve_data_source(client, target)
        if row.maybe_created and target.lookup_before_retry:
            found = _find_existing(client, data_source_id, target.column("run_id"), row.key)
            if found:
                return _mark_sent(row, found)
        lead = _with_brand(client, data_source_id, target, NotionLead(**row.payload))
        properties = _build(lead, target, row.key)[0]
        kwargs: dict[str, Any] = {
            "parent": {"type": "data_source_id", "data_source_id": data_source_id},
            "properties": properties,
        }
        children = details_children(lead, target)
        if children:
            kwargs["children"] = children
        page = client.pages.create(**kwargs)
        return _mark_sent(row, str(page["id"]))
    except Exception as exc:
        return _mark_failed(row, exc, cfg_max=_max_attempts(), backoff_cap=_backoff_cap())


def _with_brand(client, data_source_id: str, target, lead: NotionLead) -> NotionLead:
    """Brand = the live option matching the project key, unless the adapter named one. No match: Brand stays empty."""
    column = target.column("brand")
    if lead.brand or not lead.project or column is None:
        return lead
    option = keys.brand_option(client, data_source_id, column, lead.project)
    return lead.model_copy(update={"brand": option}) if option else lead


def _max_attempts() -> int:
    try:
        return conf.get_notion_config().max_attempts
    except Exception:
        return 8


def _backoff_cap() -> int:
    try:
        return conf.get_notion_config().max_backoff_seconds
    except Exception:
        return 3600


def _mark_sent(row: NotionOutbox, page_id: str) -> str:
    NotionOutbox.objects.filter(pk=row.pk).update(
        status=Status.SENT, notion_page_id=page_id, sent_at=timezone.now(), last_error="", maybe_created=False, locked_at=None
    )
    _wake_announcement(row.pk)
    return Status.SENT


def _wake_announcement(row_id: int) -> None:
    """The page exists: release a Telegram/email announcement that waits for its link. Never raises."""
    try:
        from . import notify, outbox

        notify.wake(row_id)
        outbox.enqueue_notify(row_id)
    except Exception:
        logger.exception("django_notion: could not wake the announcement of row %s", row_id)


def _mark_failed(row: NotionOutbox, exc: Exception, *, cfg_max: int, backoff_cap: int) -> str:
    kind, retry_after, ambiguous = _classify(exc)
    attempts = row.attempts
    message = _safe_message(exc)
    now = timezone.now()
    if kind == "permanent" or (kind != "rate" and attempts >= cfg_max):
        status, delay = Status.DEAD, 0.0
    elif kind == "rate":
        status = Status.FAILED
        delay = min(retry_after if retry_after else 5.0, backoff_cap)
        attempts = max(attempts - 1, 0)  # a rate limit is not a failure of this row
    else:
        status = Status.FAILED
        delay = min(30 * 2 ** max(attempts - 1, 0), backoff_cap)
    logger.warning("django_notion: row %s %s after attempt %s: %s", row.key, status, row.attempts, message)
    NotionOutbox.objects.filter(pk=row.pk).update(
        status=status, attempts=attempts, last_error=message, next_attempt_at=now + timedelta(seconds=delay),
        locked_at=None, maybe_created=ambiguous or (row.maybe_created and kind == "rate"),
    )
    return status
