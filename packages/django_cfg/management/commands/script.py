"""
Django-CFG wrapper for script command.

This is a simple alias for django_admin.management.commands.script.
All logic is in django_admin module.

Usage:
    python manage.py script <script_name>
"""

from django_cfg.modules.django_admin.management.commands.script import Command as ScriptCommand


class Command(ScriptCommand):
    """
    Alias for script command.

    Simply inherits from ScriptCommand without any changes.
    """
    pass
