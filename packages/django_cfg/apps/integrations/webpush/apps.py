"""
Django app configuration for Web Push integration.

Simple push notification service with VAPID support.
"""

from __future__ import annotations

import os
import sys

from django.apps import AppConfig


class WebPushConfig(AppConfig):
    """
    Web Push application configuration.

    Provides:
    - Push notification service using VAPID protocol
    - Subscription storage (user + device)
    - Simple API endpoints for Next.js
    - Admin interface for testing
    """

    default_auto_field = "django.db.models.BigAutoField"
    name = "django_cfg.apps.integrations.webpush"
    label = "django_cfg_webpush"
    verbose_name = "Web Push Notifications"

    def ready(self):
        """Initialize app when Django starts."""
        from django_cfg.utils import get_logger

        logger = get_logger("webpush.apps")

        # Check dependencies if needed
        self._check_dependencies_if_needed()

        logger.info("Web Push app initialized")

    def _check_dependencies_if_needed(self):
        """
        Check Web Push dependencies only when needed.

        Skips check for migrations, shell, test commands.
        """
        # Get command name from sys.argv
        if len(sys.argv) < 2:
            return

        command = sys.argv[1]

        # Commands that don't need webpush dependencies
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

        # Also skip if running tests
        if 'test' in sys.argv or 'pytest' in sys.argv[0]:
            return

        # Skip if env variable is set
        if os.environ.get('DJANGO_SKIP_WEBPUSH_CHECK', '').lower() in ('1', 'true', 'yes'):
            return

        # For test_push command, perform strict check
        if command == 'test_push':
            from ._cfg import check_webpush_dependencies
            try:
                check_webpush_dependencies(raise_on_missing=True)
            except Exception as e:
                print(str(e))
                sys.exit(1)

        # For other commands, silent check
        else:
            from ._cfg import check_webpush_dependencies
            try:
                check_webpush_dependencies(raise_on_missing=False)
            except Exception:
                pass
