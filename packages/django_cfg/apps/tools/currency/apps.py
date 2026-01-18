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
        # Skip in migrations, shell_plus, etc.
        if any(cmd in sys.argv for cmd in ["migrate", "makemigrations", "collectstatic"]):
            return

        # Run initial rate update in background thread
        thread = threading.Thread(target=self._run_startup_update, daemon=True)
        thread.start()

    def _run_startup_update(self):
        """Run startup update via service."""
        try:
            from .services import update_rates_if_needed
            update_rates_if_needed()
        except Exception as e:
            logger.warning(f"Initial currency update failed: {e}")
