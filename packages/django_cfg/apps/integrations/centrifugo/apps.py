"""
Django app configuration for Centrifugo module.

Provides Centrifugo pub/sub client with ACK tracking.
"""

from __future__ import annotations

import os

from django.apps import AppConfig


class CentrifugoConfig(AppConfig):
    """
    Centrifugo application configuration.

    Provides:
    - Async client for publishing messages to Centrifugo
    - ACK tracking for delivery confirmation
    - Logging of all publish operations
    - Migration-friendly API (mirrors legacy WebSocket solution patterns)
    """

    default_auto_field = "django.db.models.BigAutoField"
    name = "django_cfg.apps.integrations.centrifugo"
    label = "django_cfg_centrifugo"
    verbose_name = "Centrifugo WebSocket"

    def ready(self):
        """
        Initialize app when Django starts.

        Validates that all required Centrifugo dependencies are installed.
        Registers signal handlers for JWT token customization.
        Loads built-in RPC handlers.
        """
        from django_cfg.utils import get_logger

        logger = get_logger("centrifugo.apps")

        # Check dependencies if needed (only when using Centrifugo features)
        self._check_dependencies_if_needed()

        # Register built-in RPC handlers (system.check_version, etc.)
        try:
            from . import handlers  # noqa: F401
            logger.debug("Built-in Centrifugo RPC handlers registered")
        except ImportError as e:
            logger.warning(f"Could not load Centrifugo handlers: {e}")

        logger.info("Centrifugo app initialized (middleware will inject JWT tokens)")

    def _check_dependencies_if_needed(self):
        """
        Check Centrifugo dependencies only when needed.

        Skips check for:
        - Migrations (makemigrations, migrate)
        - Shell commands (shell, shell_plus)
        - Test discovery (test --help)
        - Django checks (check)
        - Management command listing (help)
        """
        import sys

        # Get command name from sys.argv
        if len(sys.argv) < 2:
            return

        command = sys.argv[1]

        # Commands that don't need Centrifugo dependencies
        skip_commands = [
            'makemigrations',
            'migrate',
            'shell',
            'shell_plus',
            'check',
            'help',
            'test',
            'collectstatic',
            'createsuperuser',
            'changepassword',
            'showmigrations',
            'sqlmigrate',
            'inspectdb',
        ]

        # Skip check for these commands
        if command in skip_commands:
            return

        # Also skip if running tests (pytest, nose, etc.)
        if 'test' in sys.argv or 'pytest' in sys.argv[0]:
            return

        # Skip if DJANGO_SKIP_CENTRIFUGO_CHECK environment variable is set
        if os.environ.get('DJANGO_SKIP_CENTRIFUGO_CHECK', '').lower() in ('1', 'true', 'yes'):
            return

        # For commands that may use Centrifugo, perform silent check
        from ._cfg import check_centrifugo_dependencies
        try:
            # Silent check - only validates that checker itself works
            check_centrifugo_dependencies(raise_on_missing=False)
        except Exception:
            # Silently ignore - don't break other commands
            pass
