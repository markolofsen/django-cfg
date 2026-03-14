from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("django_cfg_monitor", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="frontendevent",
            name="build_id",
            field=models.CharField(
                blank=True,
                db_index=True,
                default="",
                help_text="Next.js BUILD_ID — links event to the exact deploy for source map deminification",
                max_length=100,
            ),
        ),
    ]
