"""
Django-CFG wrapper for migrator command.

This is a simple alias for django_admin.management.commands.migrator.
All logic is in django_admin module.

Usage:
    python manage.py migrator
"""

from django_cfg.modules.django_admin.management.commands.migrator import Command as MigratorCommand


class Command(MigratorCommand):
    """
    Alias for migrator command.

    Simply inherits from MigratorCommand without any changes.
    """
    pass
