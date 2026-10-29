import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    """The reverse names (`mcp_keys` / `mcp_grants`) and the index names are ones a project's own MCP models commonly use too."""

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("django_cfg_mcp", "0002_mcpkey_mcpgrant"),
    ]

    operations = [
        migrations.RenameIndex(model_name="mcpkey", new_name="dcfg_mcpkey_user_revoked_idx", old_name="mcp_key_user_revoked_idx"),
        migrations.RenameIndex(model_name="mcpgrant", new_name="dcfg_mcpgrant_user_revoked_idx", old_name="mcp_grant_user_revoked_idx"),
        migrations.AlterField(
            model_name="mcpkey",
            name="user",
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="django_cfg_mcp_keys", to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name="mcpgrant",
            name="user",
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="django_cfg_mcp_grants", to=settings.AUTH_USER_MODEL),
        ),
    ]
