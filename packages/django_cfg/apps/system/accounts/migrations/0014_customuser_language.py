from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("django_cfg_accounts", "0013_add_deleted_at"),
    ]

    operations = [
        migrations.AddField(
            model_name="customuser",
            name="language",
            field=models.CharField(blank=True, default="", max_length=10),
        ),
    ]
