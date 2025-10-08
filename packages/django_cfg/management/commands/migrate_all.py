"""
Django-CFG wrapper for migrate_all command.

This is a simple alias for django_admin.management.commands.migrate_all.
All logic is in django_admin module.

Usage:
    python manage.py migrate_all
"""

from django_cfg.modules.django_admin.management.commands.migrate_all import Command as MigrateAllCommand


class Command(MigrateAllCommand):
    """
    Alias for migrate_all command.

    Simply inherits from MigrateAllCommand without any changes.
    """
    pass
