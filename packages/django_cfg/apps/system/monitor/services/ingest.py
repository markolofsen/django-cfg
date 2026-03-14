"""
Core ingest service — validates, deduplicates, and persists frontend events.
"""

import logging
from datetime import timedelta
from typing import Any

from django.utils import timezone

logger = logging.getLogger(__name__)


class IngestService:
    """
    Handles a batch of frontend events from a single request.

    Usage:
        result = IngestService().ingest_batch(validated_events, ip_address, user)
    """

    def ingest_batch(
        self,
        events_data: list[dict[str, Any]],
        ip_address: str,
        user=None,
    ) -> dict[str, int]:
        """
        Process a batch of validated event dicts.

        Returns a summary: {"saved": N, "skipped": N, "rate_limited": bool}
        """
        from django_cfg.apps.system.monitor.models import AnonymousSession, FrontendEvent
        from django_cfg.apps.system.monitor.services.notifications import NotificationService
        from django_cfg.apps.system.monitor.__cfg__ import get_settings

        settings = get_settings()
        saved = 0
        skipped = 0

        # All events in batch share the same session_id (first event wins)
        session_id = events_data[0].get("session_id") if events_data else None
        session = self._resolve_session(session_id, ip_address, events_data, user)

        # Per-session hourly cap
        if session and self._session_over_hourly_limit(session, settings.max_events_per_session_per_hour):
            logger.warning("Frontend monitor: session %s exceeded hourly limit", session_id)
            return {"saved": 0, "skipped": len(events_data), "rate_limited": True}

        notifications = NotificationService()

        for data in events_data:
            try:
                if self._is_duplicate(data, settings.dedup_window_seconds):
                    skipped += 1
                    continue

                event = self._save_event(data, ip_address, session, user)
                saved += 1

                # Telegram alerts (fire-and-forget, silently)
                notifications.maybe_notify(event, ip_address)

            except Exception:
                logger.exception("Frontend monitor: error saving event")
                skipped += 1

        return {"saved": saved, "skipped": skipped, "rate_limited": False}

    # ── Private helpers ───────────────────────────────────────────────────────

    def _resolve_session(
        self,
        session_id,
        ip_address: str,
        events_data: list[dict],
        user,
    ):
        """Get or create AnonymousSession. Returns None if session_id missing."""
        if not session_id:
            return None

        from django_cfg.apps.system.monitor.models import AnonymousSession

        user_agent = events_data[0].get("user_agent", "") if events_data else ""
        fingerprint = events_data[0].get("fingerprint", "") if events_data else ""

        try:
            session, _ = AnonymousSession.objects.get_or_create(
                session_id=session_id,
                defaults={
                    "ip_address": ip_address,
                    "user_agent": user_agent,
                    "fingerprint": fingerprint,
                    "user": user if user and user.is_authenticated else None,
                },
            )
            session.last_seen = timezone.now()
            session.save(update_fields=["last_seen"])
            return session
        except Exception:
            logger.exception("Frontend monitor: error resolving session %s", session_id)
            return None

    def _is_duplicate(self, data: dict, window_seconds: int) -> bool:
        """
        Return True if an identical event (fingerprint+message+url) was already
        saved within the dedup window.
        """
        fingerprint = data.get("fingerprint", "")
        if not fingerprint:
            return False  # No fingerprint → can't dedup, always save

        from django_cfg.apps.system.monitor.models import FrontendEvent

        cutoff = timezone.now() - timedelta(seconds=window_seconds)
        return FrontendEvent.objects.filter(
            fingerprint=fingerprint,
            url=data.get("url", ""),
            created_at__gte=cutoff,
        ).exists()

    def _session_over_hourly_limit(self, session, max_per_hour: int) -> bool:
        """Return True if session has already sent max_per_hour events this hour."""
        from django_cfg.apps.system.monitor.models import FrontendEvent

        cutoff = timezone.now() - timedelta(hours=1)
        count = FrontendEvent.objects.filter(
            anonymous_session=session,
            created_at__gte=cutoff,
        ).count()
        return count >= max_per_hour

    def _save_event(self, data: dict, ip_address: str, session, user) -> "FrontendEvent":
        from django_cfg.apps.system.monitor.models import FrontendEvent

        ua = data.get("user_agent", "")
        return FrontendEvent.objects.create(
            event_type=data.get("event_type", FrontendEvent.EventType.INFO),
            level=data.get("level", FrontendEvent.Level.INFO),
            message=data.get("message", ""),
            stack_trace=data.get("stack_trace", ""),
            url=data.get("url", ""),
            http_status=data.get("http_status"),
            http_method=data.get("http_method", ""),
            http_url=data.get("http_url", ""),
            user_agent=ua,
            ip_address=ip_address,
            device_type=self._device_type(ua),
            os=self._parse_os(ua),
            browser=self._parse_browser(ua),
            fingerprint=data.get("fingerprint", ""),
            user=user if user and user.is_authenticated else None,
            anonymous_session=session,
            extra=data.get("extra", {}),
            project_name=data.get("project_name", ""),
            environment=data.get("environment", ""),
        )

    @staticmethod
    def _device_type(ua: str) -> str:
        ua_lower = ua.lower()
        if "mobile" in ua_lower:
            return "mobile"
        if "tablet" in ua_lower or "ipad" in ua_lower:
            return "tablet"
        return "desktop"

    @staticmethod
    def _parse_os(ua: str) -> str:
        if "Android" in ua:
            return "Android"
        if "iPhone" in ua or "iPad" in ua or "iOS" in ua:
            return "iOS"
        if "Windows" in ua:
            return "Windows"
        if "Macintosh" in ua or "Mac OS" in ua:
            return "macOS"
        if "Linux" in ua:
            return "Linux"
        return ""

    @staticmethod
    def _parse_browser(ua: str) -> str:
        if "Edg/" in ua or "Edge/" in ua:
            return "Edge"
        if "Chrome/" in ua:
            return "Chrome"
        if "Firefox/" in ua:
            return "Firefox"
        if "Safari/" in ua and "Chrome" not in ua:
            return "Safari"
        if "OPR/" in ua or "Opera" in ua:
            return "Opera"
        return ""
