"""
Django app configuration for django_centrifugo module.

No database models. No migrations. No REST API.
Data is stored in Cloudflare D1 (centrifugo_logs append-only table).
"""

from __future__ import annotations

import logging
import os

from django.apps import AppConfig

logger = logging.getLogger(__name__)


class DjangoCentrifugoConfig(AppConfig):
    """
    Centrifugo application configuration.

    Provides:
    - Async client for publishing messages to Centrifugo
    - ACK tracking for delivery confirmation
    - D1-backed append-only publish log (centrifugo_logs)
    - Streamlit dashboard for publish history
    - Multi-language code generation (codegen/)
    """

    default_auto_field = "django.db.models.BigAutoField"
    name = "django_cfg.modules.django_centrifugo"
    label = "django_cfg_centrifugo"
    verbose_name = "Centrifugo WebSocket"

    def ready(self) -> None:
        """Initialize app when Django starts."""
        self._check_dependencies_if_needed()
        self._register_handlers()

    def _check_dependencies_if_needed(self) -> None:
        """Silently validate dependencies — skip for maintenance commands."""
        import sys

        if len(sys.argv) < 2:
            return

        command = sys.argv[1]
        skip_commands = {
            "makemigrations", "migrate", "shell", "shell_plus",
            "check", "help", "test", "collectstatic",
            "createsuperuser", "changepassword",
            "showmigrations", "sqlmigrate", "inspectdb",
        }

        if command in skip_commands:
            return
        if "test" in sys.argv or "pytest" in getattr(sys, "argv", [""])[0]:
            return
        if os.environ.get("DJANGO_SKIP_CENTRIFUGO_CHECK", "").lower() in ("1", "true", "yes"):
            return

        from ._deps import check_centrifugo_available
        try:
            check_centrifugo_available()
        except Exception:
            pass  # Silently ignore — don't break other commands

    def _register_handlers(self) -> None:
        """Load built-in RPC handlers."""
        try:
            from . import handlers  # noqa: F401
            logger.debug("django_centrifugo: built-in RPC handlers registered")
        except ImportError as exc:
            logger.debug("django_centrifugo: handlers not loaded — %s", exc)

        logger.info("django_centrifugo: app initialized (D1-backed publish log)")
