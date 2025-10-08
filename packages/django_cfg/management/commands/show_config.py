"""
Django-CFG wrapper for show_config command.

This is a simple alias for django_admin.management.commands.show_config.
All logic is in django_admin module.

Usage:
    python manage.py show_config
    python manage.py show_config --format json
    python manage.py show_config --include-secrets
"""

from django_cfg.modules.django_admin.management.commands.show_config import Command as ShowConfigCommand


class Command(ShowConfigCommand):
    """
    Alias for show_config command.

    Simply inherits from ShowConfigCommand without any changes.
    """
    pass
