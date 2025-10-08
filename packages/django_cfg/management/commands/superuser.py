"""
Django-CFG wrapper for superuser command.

This is a simple alias for django_admin.management.commands.superuser.
All logic is in django_admin module.

Usage:
    python manage.py superuser
    python manage.py superuser --interactive
    python manage.py superuser --username admin --email admin@example.com --password secret
"""

from django_cfg.modules.django_admin.management.commands.superuser import Command as SuperuserCommand


class Command(SuperuserCommand):
    """
    Alias for superuser command.

    Simply inherits from SuperuserCommand without any changes.
    """
    pass
