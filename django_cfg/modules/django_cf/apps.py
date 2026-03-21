"""
django_cf — Django AppConfig.

Wires up signals and capture hooks at Django startup.
"""

from __future__ import annotations

import logging

from django.apps import AppConfig

logger = logging.getLogger("django_cfg.django_cf")


class DjangoCfConfig(AppConfig):
    name = "django_cfg.modules.django_cf"
    label = "django_cf"
    verbose_name = "Cloudflare D1"
    default_auto_field = "django.db.models.BigAutoField"

    def ready(self) -> None:
        # Suppress noisy httpx INFO logs (Cloudflare SDK uses httpx internally)
        logging.getLogger("httpx").setLevel(logging.WARNING)
        logging.getLogger("httpcore").setLevel(logging.WARNING)

        self._connect_user_signals()
        self._connect_monitor_capture()

    def _connect_user_signals(self) -> None:
        try:
            from .users.signals import connect_signals
            connect_signals()
        except Exception as exc:
            logger.warning("django_cf: failed to connect user signals — %s", exc)

    def _connect_monitor_capture(self) -> None:
        """Connect monitor capture hooks when django_cf is ready."""
        try:
            from django_cfg.modules.django_cf import _get_config
            config = _get_config()
            if config is None or not config.is_ready():
                return

            from django_cfg.modules.django_monitor.capture import connect_capture
            connect_capture()
            logger.debug("django_cf: monitor capture hooks connected")
        except ImportError:
            pass  # django_monitor not installed — fine
        except Exception as exc:
            logger.warning("django_cf: failed to connect monitor capture — %s", exc)
