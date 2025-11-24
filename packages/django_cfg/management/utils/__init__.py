"""
Django Management Command Utilities

Ready-to-use base classes for Django management commands.

Quick Start:
    from django_cfg.management.utils import SafeCommand

    class Command(SafeCommand):
        help = 'My safe command'

        def handle(self, *args, **options):
            self.logger.info("Running command")
            # Your code here
"""

from .migration_manager import MigrationManager
from .mixins import (
    AdminCommand,
    DestructiveCommand,
    InteractiveCommand,
    SafeCommand,
)
from .postgresql import (
    PostgreSQLExtensionManager,
    ensure_postgresql_extensions,
)

__all__ = [
    'SafeCommand',
    'InteractiveCommand',
    'DestructiveCommand',
    'AdminCommand',
    'PostgreSQLExtensionManager',
    'ensure_postgresql_extensions',
    'MigrationManager',
]
