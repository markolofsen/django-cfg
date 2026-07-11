"""RefundService — initiate a refund and record it.

Centralizes the CLI/admin-initiated refund path (a ``charge.refunded`` webhook
later confirms it; this service performs the action and updates our models
optimistically). The webhook handler remains idempotent, so a redelivered
refund event won't double-apply.
"""

from __future__ import annotations

import logging

from django.db import transaction

logger = logging.getLogger(__name__)


class RefundError(Exception):
    pass


class RefundService:
    @staticmethod
    @transaction.atomic
    def refund(*, payment, amount: int | None = None):
        """Refund ``payment`` fully (``amount=None``) or partially (minor units).

        Returns the provider ``RefundResult``. Raises ``RefundError`` on an
        invalid request (already refunded, no external id, amount too large).
        """
        from django_cfg.apps.payments.models import Payment
        from django_cfg.apps.payments.providers import get_provider

        if not payment.external_id:
            raise RefundError(f"Payment {payment.short_id} has no provider id.")
        if payment.status not in (Payment.Status.SUCCEEDED, Payment.Status.REFUNDED):
            raise RefundError(
                f"Payment {payment.short_id} is {payment.status}; only succeeded "
                "payments can be refunded."
            )

        already = payment.amount_refunded
        remaining = payment.amount - already
        if remaining <= 0:
            raise RefundError(f"Payment {payment.short_id} is already fully refunded.")
        if amount is not None and amount > remaining:
            raise RefundError(
                f"Refund {amount} exceeds remaining refundable {remaining} "
                f"(minor units) for {payment.short_id}."
            )

        provider = get_provider(payment.provider)
        refund_result = provider.refund(payment=payment, amount=amount)

        payment.amount_refunded = already + refund_result.amount
        if payment.amount_refunded >= payment.amount:
            payment.status = Payment.Status.REFUNDED
        payment.save(update_fields=["amount_refunded", "status", "updated_at"])

        logger.info(
            "refunded %s amount=%s (%s)",
            payment.short_id, refund_result.amount, payment.status,
        )
        return refund_result
