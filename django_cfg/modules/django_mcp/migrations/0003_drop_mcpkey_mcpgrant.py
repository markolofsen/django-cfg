from django.db import migrations


class Migration(migrations.Migration):
    """The MCP credential is the user's UserAPIKey; the key and grant tables (2.3.352 to 2.3.354) go."""

    dependencies = [
        ("django_cfg_mcp", "0002_mcpkey_mcpgrant"),
    ]

    operations = [
        migrations.DeleteModel(name="McpGrant"),
        migrations.DeleteModel(name="McpKey"),
    ]
