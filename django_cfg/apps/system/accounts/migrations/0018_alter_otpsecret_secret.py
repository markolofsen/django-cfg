from django.db import migrations, models


def purge_old_otps(apps, schema_editor):
    """Drop all existing OTP rows — old codes were 6 digits and don't fit varchar(4)."""
    OTPSecret = apps.get_model("django_cfg_accounts", "OTPSecret")
    OTPSecret.objects.using(schema_editor.connection.alias).all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ("django_cfg_accounts", "0017_add_object_type_default"),
    ]

    operations = [
        migrations.RunPython(purge_old_otps, reverse_code=migrations.RunPython.noop),
        migrations.AlterField(
            model_name="otpsecret",
            name="secret",
            field=models.CharField(max_length=4),
        ),
    ]
