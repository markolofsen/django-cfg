from django.db import migrations, models


def settle_existing(apps, schema_editor):
    """Leads from before this migration get no acknowledgement now."""
    from django.db.models import F

    apps.get_model("django_cfg_notion", "NotionOutbox").objects.update(ack_notified_at=F("created_at"))


class Migration(migrations.Migration):

    dependencies = [("django_cfg_notion", "0002_notify_flags")]

    operations = [
        migrations.AddField(
            model_name="notionoutbox",
            name="ack_notified_at",
            field=models.DateTimeField(blank=True, null=True, help_text="Acknowledgement letter to the lead's author: sent, or skipped on purpose"),
        ),
        migrations.AddField(
            model_name="notionoutbox",
            name="ack_email",
            field=models.CharField(blank=True, db_index=True, max_length=254, help_text="Address an acknowledgement was actually sent to (24 h per-address limit)"),
        ),
        migrations.RunPython(settle_existing, migrations.RunPython.noop),
    ]
