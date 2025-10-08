"""
Django-CFG wrapper for check_endpoints command.

This is a simple alias for django_admin.management.commands.check_endpoints.
All logic is in django_admin module.

Usage:
    python manage.py check_endpoints
"""

from django_cfg.modules.django_admin.management.commands.check_endpoints import Command as CheckEndpointsCommand


class Command(CheckEndpointsCommand):
    """
    Alias for check_endpoints command.

    Simply inherits from CheckEndpointsCommand without any changes.
    """
    pass
