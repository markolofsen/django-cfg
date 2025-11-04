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

from .mixins import (
    AdminCommand,
    DestructiveCommand,
    InteractiveCommand,
    SafeCommand,
)

__all__ = [
    'SafeCommand',
    'InteractiveCommand',
    'DestructiveCommand',
    'AdminCommand',
]
