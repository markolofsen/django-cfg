from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("cfg_analytics", "0005_server_event_idempotency"),
    ]

    operations = [
        migrations.AddField(
            model_name="analyticssession",
            name="interacted",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="analyticssession",
            name="engaged_sec",
            field=models.PositiveIntegerField(default=0),
        ),
    ]
