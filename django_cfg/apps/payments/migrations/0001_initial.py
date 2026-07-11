# Hand-written initial migration for django_cfg.apps.payments.
#
# The Payment.owner FK targets the swappable CFG_PAYMENTS_OWNER_MODEL setting
# (emitted by django-cfg's settings generation; defaults to the accounts user
# model) — the same mechanism AUTH_USER_MODEL uses, hence the
# swappable_dependency entries below.

import uuid

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.CFG_PAYMENTS_OWNER_MODEL),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Payment",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                (
                    "short_id",
                    models.CharField(blank=True, db_index=True, max_length=24),
                ),
                ("reference_kind", models.CharField(blank=True, default="", max_length=32)),
                ("reference_id", models.CharField(blank=True, default="", max_length=64)),
                ("provider", models.CharField(max_length=32)),
                (
                    "external_id",
                    models.CharField(blank=True, db_index=True, max_length=128),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("pending", "Pending"),
                            ("processing", "Processing"),
                            ("requires_action", "Requires action"),
                            ("succeeded", "Succeeded"),
                            ("failed", "Failed"),
                            ("refunded", "Refunded"),
                            ("cancelled", "Cancelled"),
                        ],
                        default="pending",
                        max_length=20,
                    ),
                ),
                ("amount", models.BigIntegerField()),
                ("currency", models.CharField(default="usd", max_length=8)),
                ("amount_refunded", models.BigIntegerField(default=0)),
                ("idempotency_key", models.CharField(max_length=128, unique=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "owner",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="cfg_payments",
                        to=settings.CFG_PAYMENTS_OWNER_MODEL,
                    ),
                ),
                (
                    "created_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="created_cfg_payments",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "db_table": "cfg_payments_payment",
                "verbose_name": "Payment",
                "verbose_name_plural": "Payments",
                "ordering": ["-created_at"],
            },
        ),
        migrations.CreateModel(
            name="PaymentEvent",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("provider", models.CharField(max_length=32)),
                ("event_id", models.CharField(max_length=128, unique=True)),
                ("event_type", models.CharField(blank=True, max_length=64)),
                ("payload", models.JSONField(blank=True, default=dict)),
                ("received_at", models.DateTimeField(auto_now_add=True)),
                ("processed_at", models.DateTimeField(blank=True, null=True)),
                ("error", models.TextField(blank=True)),
                (
                    "payment",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="events",
                        to="cfg_payments.payment",
                    ),
                ),
            ],
            options={
                "db_table": "cfg_payments_event",
                "verbose_name": "Payment Event",
                "verbose_name_plural": "Payment Events",
                "ordering": ["-received_at"],
            },
        ),
        migrations.AddConstraint(
            model_name="payment",
            constraint=models.UniqueConstraint(
                condition=models.Q(("external_id__gt", "")),
                fields=("provider", "external_id"),
                name="uniq_cfg_payment_provider_external_id",
            ),
        ),
        migrations.AddIndex(
            model_name="payment",
            index=models.Index(
                fields=["owner", "status"], name="cfg_pay_owner_status_idx",
            ),
        ),
        migrations.AddIndex(
            model_name="payment",
            index=models.Index(fields=["short_id"], name="cfg_pay_short_id_idx"),
        ),
        migrations.AddIndex(
            model_name="payment",
            index=models.Index(
                fields=["reference_kind", "reference_id"], name="cfg_pay_reference_idx",
            ),
        ),
        migrations.AddIndex(
            model_name="paymentevent",
            index=models.Index(
                fields=["provider", "event_type"], name="cfg_pay_evt_provider_idx",
            ),
        ),
    ]
