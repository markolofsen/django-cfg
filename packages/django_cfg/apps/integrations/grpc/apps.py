"""
Django app configuration for gRPC integration.
"""

from __future__ import annotations

import os

from django.apps import AppConfig


class GRPCAppConfig(AppConfig):
    """
    Django app config for gRPC integration.

    Provides:
    - gRPC server with Django ORM integration
    - JWT authentication
    - Request logging to database
    - Admin interface for monitoring
    - REST API for metrics
    """

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'django_cfg.apps.integrations.grpc'
    verbose_name = 'gRPC Integration'

    def ready(self):
        """
        Called when Django starts.

        Validates that all required gRPC dependencies are installed.
        """
        # Only check dependencies if we're running a command that needs gRPC
        # (avoid breaking migrations, shell, etc.)
        self._check_dependencies_if_needed()

        # Import signal handlers if needed
        # from . import signals

    def _check_dependencies_if_needed(self):
        """
        Check gRPC dependencies only when running gRPC-related commands.

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

        # Commands that don't need gRPC dependencies
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

        # Skip if DJANGO_SKIP_GRPC_CHECK environment variable is set
        if os.environ.get('DJANGO_SKIP_GRPC_CHECK', '').lower() in ('1', 'true', 'yes'):
            return

        # For 'rungrpc' command, perform strict check
        if command == 'rungrpc':
            from ._cfg import check_grpc_dependencies
            try:
                check_grpc_dependencies(raise_on_missing=True)
            except Exception as e:
                # Print error and exit
                print(str(e))
                sys.exit(1)

        # For other commands, perform silent check (just import validation)
        # This ensures basic imports work but doesn't block the command
        else:
            from ._cfg import check_grpc_dependencies
            try:
                # Silent check - only validates that checker itself works
                check_grpc_dependencies(raise_on_missing=False)
            except Exception:
                # Silently ignore - don't break other commands
                pass
