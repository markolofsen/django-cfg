"""
django_monitor — Django AppConfig.

Connects capture hooks at startup if django_cf is ready.
Can be used standalone (without django_cf AppConfig) — e.g. when
django_monitor is added to INSTALLED_APPS explicitly.
"""

from __future__ import annotations

import logging

from django.apps import AppConfig

logger = logging.getLogger("django_cfg.django_monitor")


class DjangoMonitorConfig(AppConfig):
    name = "django_cfg.modules.django_monitor"
    label = "django_monitor"
    verbose_name = "Monitor (D1)"
    default_auto_field = "django.db.models.BigAutoField"

    def ready(self) -> None:
        try:
            from .capture import connect_capture
            connect_capture()
        except Exception as exc:
            logger.warning("django_monitor: failed to connect capture hooks — %s", exc)
