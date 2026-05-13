import uuid

from django.db import migrations, models
import django.db.models.deletion


def create_api_keys_for_existing_users(apps, schema_editor):
    """Generate API keys for all existing users that don't have one."""
    CustomUser = apps.get_model("django_cfg_accounts", "CustomUser")
    UserAPIKey = apps.get_model("django_cfg_accounts", "UserAPIKey")

    for user in CustomUser.objects.all():
        UserAPIKey.objects.get_or_create(user=user, defaults={"key": uuid.uuid4()})


class Migration(migrations.Migration):

    dependencies = [
        ("django_cfg_accounts", "0019_customuser_timezone"),
    ]

    operations = [
        migrations.CreateModel(
            name="UserAPIKey",
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
                    "key",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        unique=True,
                    ),
                ),
                (
                    "reissued_at",
                    models.DateTimeField(
                        blank=True,
                        null=True,
                        help_text="When the key was last regenerated.",
                    ),
                ),
                (
                    "created_at",
                    models.DateTimeField(auto_now_add=True),
                ),
                (
                    "user",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="api_key",
                        to="django_cfg_accounts.customuser",
                    ),
                ),
            ],
            options={
                "verbose_name": "User API Key",
                "verbose_name_plural": "User API Keys",
            },
        ),
        migrations.RunPython(
            create_api_keys_for_existing_users,
            reverse_code=migrations.RunPython.noop,
        ),
    ]
