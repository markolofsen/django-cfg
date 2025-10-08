"""
Django-CFG wrapper for tree command.

This is a simple alias for django_admin.management.commands.tree.
All logic is in django_admin module.

Usage:
    python manage.py tree
"""

from django_cfg.modules.django_admin.management.commands.tree import Command as TreeCommand


class Command(TreeCommand):
    """
    Alias for tree command.

    Simply inherits from TreeCommand without any changes.
    """
    pass
