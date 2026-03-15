# Generated manually - add TwoFactorSettings model

from django.db import migrations, models


class Migration(migrations.Migration):
    """
    Add TwoFactorSettings model for global 2FA configuration.

    This model uses singleton pattern - only one settings record exists.
    """

    dependencies = [
        ("django_cfg_accounts", "0009_delete_twilioresponse"),
    ]

    operations = [
        migrations.CreateModel(
            name="TwoFactorSettings",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "enabled",
                    models.BooleanField(
                        default=True,
                        help_text="Enable 2FA system-wide",
                    ),
                ),
                (
                    "enforcement",
                    models.CharField(
                        choices=[
                            ("optional", "Optional - Users choose"),
                            ("encouraged", "Encouraged - Prompt but optional"),
                            ("required", "Required - Mandatory for all users"),
                            ("admin_only", "Admin Only - Required for staff/superusers"),
                        ],
                        default="optional",
                        help_text="2FA enforcement policy",
                        max_length=20,
                    ),
                ),
                (
                    "grace_period_days",
                    models.PositiveIntegerField(
                        default=7,
                        help_text="Days before 2FA becomes mandatory (if required)",
                    ),
                ),
                (
                    "session_lifetime_minutes",
                    models.PositiveIntegerField(
                        default=5,
                        help_text="2FA verification session timeout in minutes",
                    ),
                ),
                (
                    "max_failed_attempts",
                    models.PositiveIntegerField(
                        default=5,
                        help_text="Max failed 2FA attempts before session lockout",
                    ),
                ),
                (
                    "allow_totp",
                    models.BooleanField(
                        default=True,
                        help_text="Allow TOTP (authenticator app) verification",
                    ),
                ),
                (
                    "allow_backup_codes",
                    models.BooleanField(
                        default=True,
                        help_text="Allow backup code verification",
                    ),
                ),
                (
                    "created_at",
                    models.DateTimeField(auto_now_add=True),
                ),
                (
                    "updated_at",
                    models.DateTimeField(auto_now=True),
                ),
            ],
            options={
                "verbose_name": "2FA Settings",
                "verbose_name_plural": "2FA Settings",
            },
        ),
    ]
