from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("django_cfg_accounts", "0018_alter_otpsecret_secret"),
    ]

    operations = [
        migrations.AddField(
            model_name="customuser",
            name="timezone",
            field=models.CharField(
                blank=True,
                default="",
                help_text="IANA timezone name (e.g. 'Asia/Seoul'). Auto-detected from browser via X-Timezone header.",
                max_length=64,
            ),
        ),
    ]
