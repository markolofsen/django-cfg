# Generated manually - remove Twilio integration

from django.db import migrations


class Migration(migrations.Migration):
    """
    Remove TwilioResponse model.

    This migration deletes the TwilioResponse table as part of
    removing Twilio integration from django-cfg.
    """

    dependencies = [
        ("django_cfg_accounts", "0008_oauth_models"),
    ]

    operations = [
        migrations.DeleteModel(
            name="TwilioResponse",
        ),
    ]
