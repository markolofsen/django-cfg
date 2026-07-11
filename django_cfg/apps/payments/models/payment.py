"""Payment — one provider-neutral payment attempt.

Stores the authoritative amount in **integer minor units** (e.g. cents). The
provider (``stripe``) and its external id (``pi_…``) are recorded but the model
shape stays provider-agnostic so a future PayPal/crypto provider is first-class.

Ownership is a seam: payments belong to an "owner" (the billable party) — the
FK target is the ``CFG_PAYMENTS_OWNER_MODEL`` setting (emitted from the host's
``PaymentsConfig.owner_model``), defaulting to ``AUTH_USER_MODEL``. What was
paid FOR is recorded as a loose ``(reference_kind, reference_id)`` pair instead
of a hard FK, so the engine carries no knowledge of the host's order/plan models.
"""

from __future__ import annotations

import uuid

from django.conf import settings
from django.db import models


def get_owner_model_name() -> str:
    """The swappable owner-model target ("app_label.Model") for ``Payment.owner``.

    Resolved from ``CFG_PAYMENTS_OWNER_MODEL`` (emitted by django-cfg's settings
    generation when payments are enabled), falling back to ``AUTH_USER_MODEL``.
    """
    return getattr(settings, "CFG_PAYMENTS_OWNER_MODEL", settings.AUTH_USER_MODEL)


def _char_limits(model_class) -> dict[str, int]:
    """Return {attname: max_length} for all CharFields with a max_length."""
    return {
        f.attname: f.max_length
        for f in model_class._meta.get_fields()
        if isinstance(f, models.CharField) and f.max_length
    }


class TruncatingModelMixin(models.Model):
    """Abstract mixin that truncates CharField values to max_length before save().

    Prevents StringDataRightTruncation (DataError) by silently capping string
    values — provider ids and status strings arrive from external systems.
    Inlined from the source project's ``apps.core.mixins.truncating`` (cmdop),
    trimmed to the save()-path coverage this app needs.
    """

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        for attname, max_len in _char_limits(self.__class__).items():
            val = getattr(self, attname, None)
            if isinstance(val, str) and len(val) > max_len:
                setattr(self, attname, val[:max_len])
        super().save(*args, **kwargs)


class Payment(TruncatingModelMixin, models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        PROCESSING = "processing", "Processing"
        REQUIRES_ACTION = "requires_action", "Requires action"
        SUCCEEDED = "succeeded", "Succeeded"
        FAILED = "failed", "Failed"
        REFUNDED = "refunded", "Refunded"
        CANCELLED = "cancelled", "Cancelled"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    short_id = models.CharField(max_length=24, db_index=True, blank=True)

    # The billable party. Swappable via CFG_PAYMENTS_OWNER_MODEL (owner seam).
    owner = models.ForeignKey(
        get_owner_model_name(),
        on_delete=models.CASCADE,
        related_name="cfg_payments",
    )
    # What was paid for — a loose reference the HOST interprets (e.g.
    # ("order", "ord_abc123")). Blank for standalone payments/top-ups.
    reference_kind = models.CharField(max_length=32, blank=True, default="")
    reference_id = models.CharField(max_length=64, blank=True, default="")

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_cfg_payments",
    )

    provider = models.CharField(max_length=32)  # "stripe"
    # Provider intent/charge id (Stripe PaymentIntent id). Set after create.
    external_id = models.CharField(max_length=128, blank=True, db_index=True)

    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.PENDING,
    )

    # Authoritative amount in MINOR UNITS (cents).
    amount = models.BigIntegerField()
    currency = models.CharField(max_length=8, default="usd")
    # How much has been refunded (minor units).
    amount_refunded = models.BigIntegerField(default=0)

    # Client→server dedupe for double-clicked checkout-create.
    idempotency_key = models.CharField(max_length=128, unique=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = "cfg_payments"
        db_table = "cfg_payments_payment"
        verbose_name = "Payment"
        verbose_name_plural = "Payments"
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["provider", "external_id"],
                condition=models.Q(external_id__gt=""),
                name="uniq_cfg_payment_provider_external_id",
            ),
        ]
        indexes = [
            # Explicit names — they must match the hand-written 0001_initial.
            models.Index(fields=["owner", "status"], name="cfg_pay_owner_status_idx"),
            models.Index(fields=["short_id"], name="cfg_pay_short_id_idx"),
            models.Index(
                fields=["reference_kind", "reference_id"], name="cfg_pay_reference_idx",
            ),
        ]

    def __str__(self) -> str:
        return self.short_id or str(self.id)

    def save(self, *args, **kwargs):
        if not self.short_id:
            self.short_id = f"pay_{uuid.uuid4().hex[:6]}"
        super().save(*args, **kwargs)
