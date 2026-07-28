"""Trusted server-side product facts.

This is intentionally a service, not a public analytics endpoint.  The caller
owns authentication and tenant/actor derivation; django-cfg owns only durable,
privacy-safe analytics storage and idempotency.
"""

from __future__ import annotations

import hashlib
import hmac
from dataclasses import dataclass
from datetime import datetime
from typing import Any

from django.conf import settings
from django.db import router, transaction
from django.utils import timezone

from ..models import AnalyticsEvent, AnalyticsSession, Channel
from . import identity
from .ingest import _enable_fast_commit, _touch_session
from .sessions import VisitorContext, resolve_session


@dataclass(frozen=True)
class ServerEventResult:
    event: AnalyticsEvent
    created: bool


def record_server_event(
    *,
    site,
    user_id: int,
    event_name: str,
    idempotency_key: str,
    props: dict[str, Any] | None = None,
    now: datetime | None = None,
    fast_commit: bool = True,
) -> ServerEventResult:
    """Write one server-confirmed, non-measurement event exactly once.

    ``idempotency_key`` is never persisted: only an HMAC digest is stored.
    Locking the property row makes a retry race deterministic without adding a
    partition-hostile global unique constraint to the append-only event table.
    Server facts are intentionally low-volume; this lock is not on the browser
    ingest hot path.
    """
    if not idempotency_key:
        raise ValueError("idempotency_key is required")

    now = now or timezone.now()
    source_id_hash = _source_id_hash(idempotency_key)
    using = router.db_for_write(AnalyticsEvent)

    with transaction.atomic(using=using):
        if fast_commit:
            _enable_fast_commit(using)

        # Serialize only trusted facts for this site.  Browser ingestion does
        # not touch this lock, and this preserves idempotency under retries.
        type(site).objects.select_for_update().get(pk=site.pk)
        existing = AnalyticsEvent.objects.filter(
            site=site,
            source_id_hash=source_id_hash,
        ).first()
        if existing is not None:
            return ServerEventResult(event=existing, created=False)

        visitor = identity.server_visitor_id(site_id=site.id, user_id=user_id)
        ctx = VisitorContext(
            site_id=site.id,
            visitor=visitor,
            previous_visitor=visitor,
            user_id=user_id,
            is_measurement=False,
            channel=Channel.DIRECT,
        )
        session = resolve_session(ctx, now=now, pathname="")
        event = AnalyticsEvent.objects.create(
            site=site,
            ts=now,
            visitor_id=visitor,
            session=session,
            user_id=user_id,
            event_name=event_name[:64],
            is_measurement=False,
            source_id_hash=source_id_hash,
            pathname="",
            channel=Channel.DIRECT,
            props=props or {},
        )
        _touch_session(session, rows=[event], now=now)
        return ServerEventResult(event=event, created=True)


def _source_id_hash(key: str) -> str:
    return hmac.new(
        settings.SECRET_KEY.encode(),
        f"analytics:server-event:{key}".encode(),
        hashlib.sha256,
    ).hexdigest()


__all__ = ["ServerEventResult", "record_server_event"]
