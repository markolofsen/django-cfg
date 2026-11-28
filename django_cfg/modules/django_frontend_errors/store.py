"""Persist browser events grouped by signature. Never raises toward the caller."""

from __future__ import annotations

import datetime as _dt
import hashlib
import logging
import time
from typing import Any, Dict, Iterable
from urllib.parse import urlsplit

from django.db import IntegrityError, transaction
from django.db.models import F
from django.utils import timezone

logger = logging.getLogger(__name__)

STORED_EVENT_TYPES = frozenset({"JS_ERROR", "NETWORK_ERROR", "ERROR", "WARNING"})
MAX_MESSAGE_CHARS = 5_000
MAX_STACK_CHARS = 10_000
MAX_URL_CHARS = 2_000
MAX_EXTRA_CHARS = 4_000
PURGE_EVERY_SECONDS = 3600

_last_purge = 0.0


def _clip(value: Any, limit: int) -> str:
    return str(value)[:limit] if value else ""


def signature(event: Dict[str, Any]) -> str:
    """The client's fingerprint, or a stable one made from the event itself."""
    given = _clip(event.get("fingerprint"), 64)
    if given:
        return given
    path = urlsplit(str(event.get("url") or "")).path
    raw = f"{event.get('event_type', '')}|{str(event.get('message') or '')[:200]}|{path}"
    # Grouping fingerprint only; clients may already supply their own fingerprint.
    return "srv-" + hashlib.sha1(raw.encode(), usedforsecurity=False).hexdigest()[:16]


def _extra(event: Dict[str, Any]) -> dict:
    import json

    extra = event.get("extra")
    if not isinstance(extra, dict) or not extra:
        return {}
    try:
        return extra if len(json.dumps(extra, default=str)) <= MAX_EXTRA_CHARS else {"truncated": True}
    except (TypeError, ValueError):
        return {}


def _wanted(event: Dict[str, Any], store_warnings: bool) -> bool:
    if (event.get("event_type") or "") not in STORED_EVENT_TYPES:
        return False
    level = event.get("level") or "error"
    return level == "error" or (store_warnings and level == "warning")


def store_events(events: Iterable[Dict[str, Any]], *, store_warnings: bool = True, retention_days: int = 30) -> int:
    """Upsert one row per signature; returns the number of events recorded."""
    from .models import FrontendError

    recorded = 0
    now = timezone.now()
    for event in events:
        try:
            if not _wanted(event, store_warnings):
                continue
            fingerprint = signature(event)
            environment = _clip(event.get("environment"), 20)
            project_name = _clip(event.get("project_name"), 100)
            fields = dict(
                event_type=event["event_type"],
                level=_clip(event.get("level") or "error", 16),
                last_seen=now,
                message=_clip(event.get("message"), MAX_MESSAGE_CHARS),
                stack_trace=_clip(event.get("stack_trace"), MAX_STACK_CHARS),
                url=_clip(event.get("url"), MAX_URL_CHARS),
                http_status=event.get("http_status") or None,
                http_method=_clip(event.get("http_method"), 10),
                http_url=_clip(event.get("http_url"), MAX_URL_CHARS),
                browser=_clip(event.get("browser"), 100),
                os=_clip(event.get("os"), 100),
                user_agent=_clip(event.get("user_agent"), 500),
                session_id=_clip(event.get("session_id"), 64),
                build_id=_clip(event.get("build_id"), 100),
                extra=_extra(event),
            )
            lookup = dict(fingerprint=fingerprint, environment=environment, project_name=project_name)
            with transaction.atomic():
                # A repeat that carries no stack, browser, ... must not blank what an earlier one had.
                refresh = {k: v for k, v in fields.items() if v not in ("", None, {})}
                updated = FrontendError.objects.filter(**lookup).update(count=F("count") + 1, **refresh)
                if not updated:
                    try:
                        with transaction.atomic():
                            FrontendError.objects.create(first_seen=now, **lookup, **fields)
                    except IntegrityError:  # another worker created it first
                        FrontendError.objects.filter(**lookup).update(count=F("count") + 1, **refresh)
            recorded += 1
        except Exception:
            logger.exception("django_frontend_errors: could not store an event")
    if recorded:
        _maybe_purge(retention_days)
    return recorded


def purge(days: int = 30, *, batch_size: int = 5000, dry_run: bool = False) -> int:
    """Delete rows not seen for ``days`` days, in bounded batches."""
    from .models import FrontendError

    cutoff = timezone.now() - _dt.timedelta(days=days)
    if dry_run:
        return FrontendError.objects.filter(last_seen__lt=cutoff).count()
    total = 0
    while True:
        pks = list(FrontendError.objects.filter(last_seen__lt=cutoff).values_list("pk", flat=True)[:batch_size])
        if not pks:
            return total
        FrontendError.objects.filter(pk__in=pks).delete()
        total += len(pks)


def _maybe_purge(retention_days: int) -> None:
    global _last_purge
    if time.monotonic() - _last_purge < PURGE_EVERY_SECONDS:
        return
    _last_purge = time.monotonic()
    try:
        purge(retention_days)
    except Exception:
        logger.exception("django_frontend_errors: retention sweep failed")


def record_from_monitor(events: Iterable[Dict[str, Any]]) -> None:
    """Hook called by ``django_monitor.capture_frontend_events``. No-op unless enabled."""
    from django_cfg.core.state import get_current_config

    config = get_current_config()
    cfg = getattr(config, "frontend_errors", None) if config else None
    if cfg is None or not cfg.enabled:
        return
    store_events(events, store_warnings=cfg.store_warnings, retention_days=cfg.retention_days)
