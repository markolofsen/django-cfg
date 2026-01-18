"""Currency app configuration."""

import sys
import threading

from django.apps import AppConfig

from django_cfg.modules.django_logging import get_logger

logger = get_logger(__name__)


class CurrencyConfig(AppConfig):
    """Currency rates management app."""

    name = "django_cfg.apps.tools.currency"
    label = "cfg_currency"
    verbose_name = "Currency"
    default_auto_field = "django.db.models.BigAutoField"

    def ready(self):
        """Initialize app on Django startup."""
        import time
        start = time.time()

        # Skip in migrations, shell_plus, etc.
        if any(cmd in sys.argv for cmd in ["migrate", "makemigrations", "collectstatic"]):
            return

        # Run initial rate update in background thread (NON-BLOCKING)
        thread = threading.Thread(target=self._run_startup_update, daemon=True)
        thread.start()

        # This should return IMMEDIATELY (< 1ms)
        elapsed = (time.time() - start) * 1000
        logger.info(f"Currency app ready() completed in {elapsed:.1f}ms (thread spawned)")

    def _run_startup_update(self):
        """
        Run startup sync via service in background thread.

        This runs in a DAEMON THREAD - does NOT block Django startup.
        Django continues serving requests while this syncs.
        """
        import time
        start = time.time()

        try:
            from .services import sync_all
            result = sync_all()  # Syncs currencies if needed + rates if needed

            elapsed = time.time() - start
            logger.info(f"Background currency sync completed in {elapsed:.1f}s")
        except Exception as e:
            logger.warning(f"Background currency sync failed: {e}")
