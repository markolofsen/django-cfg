# Generated manually for django_cfg 1.5.111 compatibility

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("grpc", "0007_simplify_grpc_models"),
    ]

    operations = [
        migrations.AddField(
            model_name="grpcrequestlog",
            name="error_details",
            field=models.JSONField(blank=True, null=True),
        ),
    ]
