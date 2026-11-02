from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("django_cfg_accounts", "0027_oauth_google_email_key"),
    ]

    operations = [
        migrations.AddField(
            model_name="customuser",
            name="tokens_valid_after",
            field=models.DateTimeField(
                blank=True,
                editable=False,
                help_text="Access tokens issued before this time are rejected.",
                null=True,
            ),
        ),
    ]
