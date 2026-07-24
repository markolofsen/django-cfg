from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("django_cfg_totp", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="twofactorsession",
            name="remember_me",
            field=models.BooleanField(
                default=False,
                help_text="Whether the completed login should persist for 30 days",
            ),
        ),
    ]
