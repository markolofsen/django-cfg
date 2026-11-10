from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("cfg_chat", "0003_attachment"),
    ]

    operations = [
        migrations.AddField(
            model_name="message",
            name="trace",
            field=models.JSONField(
                blank=True,
                default=None,
                help_text="TraceDoc v1: how the answer was reached, at the kind's `trace_level` (see `agent/trace`); null when the kind records none. At most 24 KB.",
                null=True,
            ),
        ),
    ]
