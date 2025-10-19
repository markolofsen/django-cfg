"""
Django-CFG wrapper for runserver_ngrok command.

This is a simple alias for django_ngrok.management.commands.runserver_ngrok.
All logic is in django_ngrok module.

Usage:
    python manage.py runserver_ngrok
    python manage.py runserver_ngrok --domain example.com
    python manage.py runserver_ngrok --no-ngrok
"""

from django_cfg.modules.django_ngrok.management.commands.runserver_ngrok import (
    Command as NgrokCommand,
)


class Command(NgrokCommand):
    """
    Alias for runserver_ngrok command.

    Simply inherits from NgrokCommand without any changes.
    """
    pass
