"""
Django-CFG wrapper for rundramatiq command.

This is a simple alias for django_tasks.management.commands.rundramatiq.
All logic is in django_tasks module.

Usage:
    python manage.py rundramatiq
    python manage.py rundramatiq --processes 4 --threads 8
    python manage.py rundramatiq --queues default high_priority
"""

from django_cfg.modules.django_tasks.management.commands.rundramatiq import (
    Command as DramatiqCommand,
)


class Command(DramatiqCommand):
    """
    Alias for rundramatiq command.

    Simply inherits from DramatiqCommand without any changes.
    """
    pass
