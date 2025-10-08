"""
Django-CFG wrapper for create_token command.

This is a simple alias for django_admin.management.commands.create_token.
All logic is in django_admin module.

Usage:
    python manage.py create_token
"""

from django_cfg.modules.django_admin.management.commands.create_token import Command as CreateTokenCommand


class Command(CreateTokenCommand):
    """
    Alias for create_token command.

    Simply inherits from CreateTokenCommand without any changes.
    """
    pass
