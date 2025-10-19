"""
Django-CFG wrapper for rundramatiq_simulator command.

This is a simple alias for django_tasks.management.commands.rundramatiq_simulator.
All logic is in django_tasks module.

Usage:
    python manage.py rundramatiq_simulator
"""

from django_cfg.modules.django_tasks.management.commands.rundramatiq_simulator import (
    Command as SimulatorCommand,
)


class Command(SimulatorCommand):
    """
    Alias for rundramatiq_simulator command.

    Simply inherits from SimulatorCommand without any changes.
    """
    pass
