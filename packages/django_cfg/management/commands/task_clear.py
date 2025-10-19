"""
Django-CFG wrapper for task_clear command.

This is a simple alias for django_tasks.management.commands.task_clear.
All logic is in django_tasks module.

Usage:
    python manage.py task_clear
    python manage.py task_clear --queue default
    python manage.py task_clear --failed-only
    python manage.py task_clear --confirm
"""

from django_cfg.modules.django_tasks.management.commands.task_clear import (
    Command as TaskClearCommand,
)


class Command(TaskClearCommand):
    """
    Alias for task_clear command.

    Simply inherits from TaskClearCommand without any changes.
    """
    pass
