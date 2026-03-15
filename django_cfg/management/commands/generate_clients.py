"""
Django-CFG wrapper for generate_client command.

This is a simple alias for django_client.management.commands.generate_client.
All logic is in django_client module.

Usage:
    python manage.py generate_clients --groups blog shop
    python manage.py generate_clients --python
    python manage.py generate_clients --list-groups
"""

from django_cfg.modules.django_client.management.commands.generate_client import (
    Command as DjangoClientCommand,
)


class Command(DjangoClientCommand):
    """
    Alias for generate_client command.

    Simply inherits from DjangoClientCommand without any changes.
    This allows both 'generate_client' and 'generate_clients' to work.
    """
    pass
