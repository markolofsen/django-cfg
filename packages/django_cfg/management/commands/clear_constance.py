"""
Django-CFG wrapper for clear_constance command.

This is a simple alias for django_admin.management.commands.clear_constance.
All logic is in django_admin module.

Usage:
    python manage.py clear_constance
"""

from django_cfg.modules.django_admin.management.commands.clear_constance import Command as ClearConstanceCommand


class Command(ClearConstanceCommand):
    """
    Alias for clear_constance command.

    Simply inherits from ClearConstanceCommand without any changes.
    """
    pass
