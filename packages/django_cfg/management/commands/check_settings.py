"""
Django-CFG wrapper for check_settings command.

This is a simple alias for django_admin.management.commands.check_settings.
All logic is in django_admin module.

Usage:
    python manage.py check_settings
"""

from django_cfg.modules.django_admin.management.commands.check_settings import Command as CheckSettingsCommand


class Command(CheckSettingsCommand):
    """
    Alias for check_settings command.

    Simply inherits from CheckSettingsCommand without any changes.
    """
    pass
