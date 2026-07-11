"""
django_monitor.services.ingest — frontend event ingestion.

Takes validated ingest payloads (from IngestBatchSerializer), enriches them
with request context (IP, user, parsed user-agent) and hands them to the
capture pipeline (log pipeline + Telegram alerts).

Never raises toward the view — ingest must always answer 202.
"""

from __future__ import annotations

import logging
from typing import Optional

logger = logging.getLogger(__name__)


def ingest_frontend_events(
    events: list[dict],
    *,
    ip_address: str = "",
    user_id: Optional[str] = None,
) -> int:
    """Enrich and store a batch of validated frontend events.

    Returns the number of events accepted (0 when monitoring is disabled).
    """
    from django_cfg.modules.django_monitor import capture_frontend_events, is_enabled
    from django_cfg.modules.django_monitor.utils import parse_user_agent

    if not is_enabled():
        return 0

    batch: list[dict] = []
    for ev in events:
        try:
            normalized = dict(ev)
            ua = (ev.get("user_agent") or "")[:500]
            browser, os_name, device_type = parse_user_agent(ua)
            normalized.update(
                ip_address=ip_address,
                user_id=user_id,
                browser=browser,
                os=os_name,
                device_type=device_type,
            )
            batch.append(normalized)
        except Exception:
            logger.exception("django_monitor: failed to normalize ingest event")

    if batch:
        try:
            capture_frontend_events(batch)
        except Exception:
            logger.exception("django_monitor: failed to store frontend events")

    return len(batch)


__all__ = ["ingest_frontend_events"]
