"""
django_monitor — Django AppConfig.

Connects capture hooks at startup (log pipeline + Telegram alerts).
"""

from __future__ import annotations

import logging

from django.apps import AppConfig

logger = logging.getLogger("django_cfg.django_monitor")


class DjangoMonitorConfig(AppConfig):
    name = "django_cfg.modules.django_monitor"
    label = "django_monitor"
    verbose_name = "Monitor"
    default_auto_field = "django.db.models.BigAutoField"

    def ready(self) -> None:
        try:
            from .capture import connect_capture
            connect_capture()
        except Exception as exc:
            logger.warning("django_monitor: failed to connect capture hooks — %s", exc)
