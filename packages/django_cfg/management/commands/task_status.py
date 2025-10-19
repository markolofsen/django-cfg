"""
Django-CFG wrapper for task_status command.

This is a simple alias for django_tasks.management.commands.task_status.
All logic is in django_tasks module.

Usage:
    python manage.py task_status
    python manage.py task_status --format json
    python manage.py task_status --verbose
"""

from django_cfg.modules.django_tasks.management.commands.task_status import (
    Command as TaskStatusCommand,
)


class Command(TaskStatusCommand):
    """
    Alias for task_status command.

    Simply inherits from TaskStatusCommand without any changes.
    """
    pass
