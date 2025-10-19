"""
Django-CFG wrapper for test_twilio command.

This is a simple alias for django_twilio.management.commands.test_twilio.
All logic is in django_twilio module.

Usage:
    python manage.py test_twilio --to +1234567890
    python manage.py test_twilio --to +1234567890 --whatsapp
    python manage.py test_twilio --to +1234567890 --message "Test SMS"
"""

from django_cfg.modules.django_twilio.management.commands.test_twilio import (
    Command as TestTwilioCommand,
)


class Command(TestTwilioCommand):
    """
    Alias for test_twilio command.

    Simply inherits from TestTwilioCommand without any changes.
    """
    pass
