"""
Telegram notifications for frontend monitor:
- Error spike detection (N errors/minute from same IP)
- Unhandled JS errors
"""

import logging
from datetime import timedelta

from django.core.cache import cache
from django.utils import timezone

logger = logging.getLogger(__name__)


class NotificationService:
    """
    Checks spike conditions and sends Telegram alerts.
    All methods fail silently — must never break the ingest flow.
    """

    def maybe_notify(self, event, ip_address: str) -> None:
        try:
            from django_cfg.apps.system.monitor.__cfg__ import get_settings
            settings = get_settings()

            if not settings.telegram_alerts_enabled:
                return

            # Unhandled JS error → immediate alert
            if (
                event.event_type == "JS_ERROR"
                and event.level == "error"
            ):
                self._notify_js_error(event)

            # Spike detection (errors/minute per IP)
            if event.event_type in ("ERROR", "JS_ERROR", "NETWORK_ERROR"):
                self._check_spike(event, ip_address, settings.spike_threshold)

        except Exception:
            logger.exception("Frontend monitor notifications: unexpected error")

    def _notify_js_error(self, event) -> None:
        try:
            from django_cfg.modules.django_telegram import send_alert
            send_alert(
                "Unhandled JS Error",
                context={
                    "message": event.message[:300],
                    "url": event.url[:200],
                    "browser": event.browser,
                    "os": event.os,
                    "stack": event.stack_trace[:500] if event.stack_trace else "",
                    "project": event.project_name,
                    "env": event.environment,
                },
            )
        except Exception:
            logger.exception("Frontend monitor: failed to send JS error alert")

    def _check_spike(self, event, ip_address: str, threshold: int) -> None:
        """Send one spike alert per IP per minute at most."""
        try:
            from django_cfg.apps.system.monitor.models import FrontendEvent

            minute_bucket = timezone.now().strftime("%Y%m%d%H%M")
            cache_key = f"fm_spike:{ip_address}:{minute_bucket}"

            if cache.get(cache_key):
                return  # Already alerted this minute for this IP

            cutoff = timezone.now() - timedelta(minutes=1)
            count = FrontendEvent.objects.filter(
                ip_address=ip_address,
                event_type__in=["ERROR", "JS_ERROR", "NETWORK_ERROR"],
                created_at__gte=cutoff,
            ).count()

            if count >= threshold:
                cache.set(cache_key, True, timeout=60)
                from django_cfg.modules.django_telegram import send_error
                send_error(
                    f"Frontend Error Spike ({count} errors/min)",
                    context={
                        "ip": ip_address,
                        "errors_last_minute": count,
                        "threshold": threshold,
                        "last_url": event.url[:200],
                        "project": event.project_name,
                        "env": event.environment,
                    },
                )
        except Exception:
            logger.exception("Frontend monitor: failed spike check for %s", ip_address)
