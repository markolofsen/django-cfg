"""Currency app configuration."""

import sys

from django.apps import AppConfig

from django_cfg.modules.django_logging import get_logger

logger = get_logger(__name__)


class CurrencyConfig(AppConfig):
    """Currency rates management app."""

    name = "django_cfg.apps.tools.currency"
    label = "cfg_currency"
    verbose_name = "Currency"
    default_auto_field = "django.db.models.BigAutoField"
    _sync_done = False

    def ready(self):
        """Register lazy sync on first request."""
        if any(cmd in sys.argv for cmd in ["migrate", "makemigrations", "collectstatic"]):
            return

        from django.core.signals import request_started
        request_started.connect(self._lazy_sync)

    def _lazy_sync(self, **kwargs):
        """Run currency sync on first HTTP request."""
        if CurrencyConfig._sync_done:
            return
        CurrencyConfig._sync_done = True

        # Disconnect - run only once
        from django.core.signals import request_started
        request_started.disconnect(self._lazy_sync)

        # Run sync in background thread (non-blocking for first request)
        import threading
        thread = threading.Thread(target=self._do_sync, daemon=True)
        thread.start()

    def _do_sync(self):
        """Perform currency sync."""
        import time
        start = time.time()

        try:
            from .services import sync_all
            sync_all()

            elapsed = time.time() - start
            logger.info(f"Currency sync completed in {elapsed:.1f}s")
        except Exception as e:
            logger.warning(f"Currency sync failed: {e}")
