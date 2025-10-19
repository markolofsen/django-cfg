"""
Django-CFG wrapper for test_telegram command.

This is a simple alias for django_telegram.management.commands.test_telegram.
All logic is in django_telegram module.

Usage:
    python manage.py test_telegram
    python manage.py test_telegram --message "Test notification"
"""

from django_cfg.modules.django_telegram.management.commands.test_telegram import (
    Command as TestTelegramCommand,
)


class Command(TestTelegramCommand):
    """
    Alias for test_telegram command.

    Simply inherits from TestTelegramCommand without any changes.
    """
    pass
