from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("django_cfg_totp", "0002_twofactorsession_remember_me"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="twofactorsession",
            name="remember_me",
        ),
    ]
