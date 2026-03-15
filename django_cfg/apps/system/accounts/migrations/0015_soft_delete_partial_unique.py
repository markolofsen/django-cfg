"""
Migration: replace unique=True on email with a partial unique constraint.

Before: email had a database-level unique index (all rows, including deleted).
After:  email is unique only among active accounts (deleted_at IS NULL).
        Multiple deleted accounts may share the same email address (audit archive).

Partial unique indexes require PostgreSQL. SQLite is not supported in production.
"""

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("django_cfg_accounts", "0014_customuser_language"),
    ]

    operations = [
        # 1. Remove the old unique constraint on email
        migrations.AlterField(
            model_name="customuser",
            name="email",
            field=models.EmailField(max_length=254, verbose_name="email address"),
        ),
        # 2. Add partial unique constraint: unique only when deleted_at IS NULL
        migrations.AddConstraint(
            model_name="customuser",
            constraint=models.UniqueConstraint(
                condition=models.Q(deleted_at__isnull=True),
                fields=["email"],
                name="unique_active_email",
            ),
        ),
    ]
