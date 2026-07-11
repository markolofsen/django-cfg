"""PaymentEvent — inbound provider webhook log + idempotency.

The ``event_id`` UNIQUE constraint is the webhook idempotency guard: providers
(Stripe) redeliver events, and ``get_or_create(event_id=…)`` lets the handler
short-circuit a replay. The raw payload is stored verbatim for audit/debug.
"""

from __future__ import annotations

import uuid

from django.db import models


class PaymentEvent(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    provider = models.CharField(max_length=32)
    # Provider event id (Stripe `evt_…`). UNIQUE = webhook idempotency.
    event_id = models.CharField(max_length=128, unique=True)
    event_type = models.CharField(max_length=64, blank=True)

    payment = models.ForeignKey(
        "cfg_payments.Payment",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="events",
    )

    payload = models.JSONField(default=dict, blank=True)

    received_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True, blank=True)
    # Set when handling raised (kept for retry/debug).
    error = models.TextField(blank=True)

    class Meta:
        app_label = "cfg_payments"
        db_table = "cfg_payments_event"
        verbose_name = "Payment Event"
        verbose_name_plural = "Payment Events"
        ordering = ["-received_at"]
        indexes = [
            # Explicit name — must match the hand-written 0001_initial.
            models.Index(fields=["provider", "event_type"], name="cfg_pay_evt_provider_idx"),
        ]

    def __str__(self) -> str:
        return f"{self.provider}:{self.event_id}"
