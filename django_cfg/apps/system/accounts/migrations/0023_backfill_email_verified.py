"""Backfill ``is_email_verified`` for users who completed an OTP in the
past — the OTP service hook only flips the flag on new logins, so
without this migration historical verified users would all read as
``is_email_verified=False`` until they next log in.

We use ``last_login IS NOT NULL`` as the proof:

  * The OTP-only auth flow calls Django's ``django.contrib.auth.login()``
    on every successful code verification, which sets ``last_login``.
  * The ``OTPSecret`` table is cleaned periodically (see
    cleanup_service.cleanup_expired_otps schedule), so its history is
    only a few hours wide and CANNOT be relied on.
  * ``last_login`` is permanent unless the user is hard-deleted.

For ``email_verified_at`` we copy ``last_login`` — close enough to
"when we first knew this email worked" for downstream reporting.
"""

from django.db import migrations


def backfill(apps, schema_editor):
    CustomUser = apps.get_model("django_cfg_accounts", "CustomUser")

    qs = CustomUser.objects.filter(
        last_login__isnull=False,
        is_email_verified=False,
    )
    flipped = 0
    for user in qs.iterator():
        # Match the in-service auto-set: only fill email_verified_at if it's still None.
        user.is_email_verified = True
        user.email_verified_at = user.last_login
        user.save(update_fields=["is_email_verified", "email_verified_at"])
        flipped += 1
    print(f"  Backfill: {flipped} users marked is_email_verified=True from last_login history")


def reverse(apps, schema_editor):
    CustomUser = apps.get_model("django_cfg_accounts", "CustomUser")
    CustomUser.objects.update(is_email_verified=False, email_verified_at=None)


class Migration(migrations.Migration):

    dependencies = [
        ("django_cfg_accounts", "0022_customuser_email_verified_at_and_more"),
    ]

    operations = [
        migrations.RunPython(backfill, reverse_code=reverse),
    ]
