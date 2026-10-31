from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="StorageDeletion",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("storage_alias", models.CharField(default="default", max_length=64)),
                ("key", models.CharField(help_text="Object key, or a prefix ending in '/'", max_length=1024)),
                ("is_prefix", models.BooleanField(default=False)),
                ("model_label", models.CharField(blank=True, max_length=128)),
                ("object_pk", models.CharField(blank=True, max_length=64)),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("pending", "Pending"),
                            ("purge", "Deleted, CDN purge pending"),
                            ("done", "Done"),
                            ("failed", "Failed (attempts exhausted)"),
                            ("refused", "Refused by the guard"),
                        ],
                        default="pending",
                        max_length=16,
                    ),
                ),
                ("attempts", models.PositiveIntegerField(default=0)),
                ("next_attempt_at", models.DateTimeField(db_index=True)),
                ("last_error", models.TextField(blank=True)),
                ("purge_urls", models.JSONField(blank=True, default=list, help_text="URLs still to purge from the CDN")),
                (
                    "claimed_by",
                    models.CharField(blank=True, help_text="Set by an external consumer in queue_only mode", max_length=64),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={
                "verbose_name": "storage deletion",
                "verbose_name_plural": "storage deletions",
                "ordering": ["id"],
                "indexes": [models.Index(fields=["status", "next_attempt_at"], name="cleanup_outbox_due_idx")],
            },
        ),
    ]
