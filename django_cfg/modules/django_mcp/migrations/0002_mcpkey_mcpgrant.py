import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("django_cfg_mcp", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="McpKey",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=40)),
                ("prefix", models.CharField(help_text="First characters of the key, for the user's list", max_length=12)),
                ("key_hash", models.CharField(editable=False, max_length=64, unique=True)),
                ("scopes", models.JSONField(blank=True, default=list)),
                ("expires_at", models.DateTimeField()),
                ("revoked_at", models.DateTimeField(blank=True, null=True)),
                ("last_used_at", models.DateTimeField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="mcp_keys", to=settings.AUTH_USER_MODEL)),
            ],
            options={
                "ordering": ["-created_at", "-id"],
                "indexes": [models.Index(fields=["user", "revoked_at"], name="mcp_key_user_revoked_idx")],
            },
        ),
        migrations.CreateModel(
            name="McpGrant",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("client_name", models.CharField(max_length=80)),
                ("scopes", models.JSONField(blank=True, default=list)),
                ("refresh_gen", models.PositiveIntegerField(default=0, help_text="Generation of the one refresh token that is valid")),
                ("last_used_at", models.DateTimeField(blank=True, null=True)),
                ("revoked_at", models.DateTimeField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="mcp_grants", to=settings.AUTH_USER_MODEL)),
            ],
            options={
                "ordering": ["-created_at", "-id"],
                "indexes": [models.Index(fields=["user", "revoked_at"], name="mcp_grant_user_revoked_idx")],
            },
        ),
    ]
