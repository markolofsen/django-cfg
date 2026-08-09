"""Add ``welcome_email_sent_at`` and stamp it for already-verified users.

The field is the one-time guard for the welcome letter, which now fires from the
``user_email_verified`` signal. That signal fires on **every** verification, so
without a stamp the deploy would mail every historical verified user on their
next login — a batch of "welcome to the service" letters to people who have been
using it for months.

Stamping them is the deliberate choice, matching the existing decision in
cmdop_cf ``@dev/active/registration-consent-capture/PLAN.md`` — "no backfill of
existing users; Mark may write individual personal emails outside the pipeline".
``email_verified_at`` is copied where known so the stamp reads as "considered
already welcomed at the moment we knew the address worked", rather than
pretending the letter was sent at migration time.

Reverse clears the column, which would re-arm the send for everyone. That is the
honest inverse of this migration, not a safe operation — do not reverse on a
production database unless you intend those letters to go out.
"""

from django.db import migrations, models
from django.utils import timezone


def stamp_existing_verified_users(apps, schema_editor):
    CustomUser = apps.get_model("django_cfg_accounts", "CustomUser")

    now = timezone.now()
    stamped = 0
    for user in CustomUser.objects.filter(
        is_email_verified=True, welcome_email_sent_at__isnull=True
    ).iterator():
        user.welcome_email_sent_at = user.email_verified_at or user.last_login or now
        user.save(update_fields=["welcome_email_sent_at"])
        stamped += 1
    print(
        f"  Welcome email: {stamped} already-verified users stamped as "
        f"welcomed (they will NOT be mailed)"
    )


def unstamp(apps, schema_editor):
    CustomUser = apps.get_model("django_cfg_accounts", "CustomUser")
    CustomUser.objects.update(welcome_email_sent_at=None)


class Migration(migrations.Migration):

    dependencies = [
        ("django_cfg_accounts", "0024_otpsecret_consent_capture"),
    ]

    operations = [
        migrations.AddField(
            model_name="customuser",
            name="welcome_email_sent_at",
            field=models.DateTimeField(
                blank=True,
                null=True,
                help_text="When the one-time welcome email was sent. Null means not yet sent.",
            ),
        ),
        migrations.RunPython(
            stamp_existing_verified_users, reverse_code=unstamp
        ),
    ]
