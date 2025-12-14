"""
AppConfig for Django-RQ integration with monitoring and API capabilities.

This app provides REST API endpoints for Django-RQ task queue monitoring,
management, and statistics. It wraps django-rq's functionality with modern
DRF ViewSets and unified django-cfg patterns.

Features:
- REST API for monitoring queues, workers, and jobs
- Prometheus metrics integration
- Enhanced monitoring interfaces
- Job management (view, requeue, delete)
- Integration with django-cfg ecosystem (Centrifugo, auth)
"""

from __future__ import annotations

import os
import sys

from django.apps import AppConfig


class RQAppConfig(AppConfig):
    """
    AppConfig for Django-RQ monitoring and management application.

    Provides:
    - REST API endpoints for monitoring
    - Prometheus metrics export
    - Job and queue management
    - Worker statistics
    - Integration with django-cfg authentication

    Usage:
        Add to INSTALLED_APPS:
        INSTALLED_APPS = [
            ...
            'django_rq',  # Required: django-rq core
            'django_cfg.apps.integrations.rq',  # Django-CFG RQ monitoring
        ]

        Configure in django-cfg config:
        class MyConfig(BaseConfig):
            django_rq: DjangoRQConfig = DjangoRQConfig(
                enabled=True,
                queues={
                    'default': {
                        'host': 'localhost',
                        'port': 6379,
                        'db': 0,
                    }
                },
                prometheus_enabled=True,
            )
    """

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'django_cfg.apps.integrations.rq'
    verbose_name = 'Django-CFG RQ Monitoring'
    label = 'django_cfg_rq'

    def ready(self):
        """
        Initialize the app when Django starts.

        Registers:
        - Admin interfaces (if not already registered)
        - Signal handlers for monitoring
        - Scheduled jobs from config
        - Validates RQ dependencies if needed
        """
        # Check dependencies if running RQ-related commands
        self._check_dependencies_if_needed()

        # Import admin to register custom admin classes
        try:
            from . import admin  # noqa: F401
        except ImportError:
            pass

        # Register scheduled jobs from config (runs once on startup)
        try:
            from .services import register_schedules_from_config
            register_schedules_from_config()
        except Exception as e:
            from django_cfg.utils import get_logger
            logger = get_logger("rq.apps")
            logger.warning(f"Failed to register schedules: {e}")

    def _check_dependencies_if_needed(self):
        """
        Check RQ dependencies only when running RQ-related commands.

        Skips check for:
        - Migrations (makemigrations, migrate)
        - Shell commands (shell, shell_plus)
        - Test discovery (test --help)
        - Django checks (check)
        - Management command listing (help)
        """
        # Get command name from sys.argv
        if len(sys.argv) < 2:
            return

        command = sys.argv[1]

        # Commands that don't need RQ dependencies
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

        # Skip if DJANGO_SKIP_RQ_CHECK environment variable is set
        if os.environ.get('DJANGO_SKIP_RQ_CHECK', '').lower() in ('1', 'true', 'yes'):
            return

        # For RQ-related commands, perform strict check
        rq_commands = ['rqworker', 'rqscheduler', 'rqenqueue', 'rqstats']
        if command in rq_commands:
            from ._cfg import check_rq_dependencies
            try:
                check_rq_dependencies(raise_on_missing=True)
            except Exception as e:
                # Print error and exit
                print(str(e))
                sys.exit(1)

        # For other commands, perform silent check (just import validation)
        # This ensures basic imports work but doesn't block the command
        else:
            from ._cfg import check_rq_dependencies
            try:
                # Silent check - only validates that checker itself works
                check_rq_dependencies(raise_on_missing=False)
            except Exception:
                # Silently ignore - don't break other commands
                pass
