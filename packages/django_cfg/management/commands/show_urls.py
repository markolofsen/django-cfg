"""
Django-CFG wrapper for show_urls command.

This is a simple alias for django_admin.management.commands.show_urls.
All logic is in django_admin module.

Usage:
    python manage.py show_urls
"""

from django_cfg.modules.django_admin.management.commands.show_urls import Command as ShowUrlsCommand


class Command(ShowUrlsCommand):
    """
    Alias for show_urls command.

    Simply inherits from ShowUrlsCommand without any changes.
    """
    pass
