"""
Django-CFG wrapper for test_email command.

This is a simple alias for django_email.management.commands.test_email.
All logic is in django_email module.

Usage:
    python manage.py test_email
    python manage.py test_email --email user@example.com
    python manage.py test_email --subject "Test Subject" --message "Test Message"
"""

from django_cfg.modules.django_email.management.commands.test_email import (
    Command as TestEmailCommand,
)


class Command(TestEmailCommand):
    """
    Alias for test_email command.

    Simply inherits from TestEmailCommand without any changes.
    """
    pass
