"""
Django-CFG wrapper for list_urls command.

This is a simple alias for django_admin.management.commands.list_urls.
All logic is in django_admin module.

Usage:
    python manage.py list_urls
"""

from django_cfg.modules.django_admin.management.commands.list_urls import Command as ListUrlsCommand


class Command(ListUrlsCommand):
    """
    Alias for list_urls command.

    Simply inherits from ListUrlsCommand without any changes.
    """
    pass
