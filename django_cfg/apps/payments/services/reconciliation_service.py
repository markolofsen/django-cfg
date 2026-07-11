"""ReconciliationService — catch payments up to the provider's truth.

Safety net for missed/late webhooks: poll the provider for a payment's real
status and apply the same transitions the webhook would (succeeded → the shared
fulfillment path, failed → the failed signal). Idempotent: a payment already in
a terminal state is left untouched.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field

from django.db import transaction

logger = logging.getLogger(__name__)


@dataclass
class ReconcileResult:
    checked: int = 0
    updated: int = 0
    #: Payments driven through the fulfillment seam (signal + hook) this run.
    activated: int = 0
    skipped: int = 0
    errors: list[str] = field(default_factory=list)


class ReconciliationService:
    @staticmethod
    def reconcile_stuck(*, older_than_hours: int = 1, limit: int = 100) -> ReconcileResult:
        """Reconcile payments stuck in PROCESSING for too long."""
        from datetime import timedelta

        from django.utils import timezone

        from django_cfg.apps.payments.models import Payment

        cutoff = timezone.now() - timedelta(hours=older_than_hours)
        qs = Payment.objects.filter(
            status=Payment.Status.PROCESSING, updated_at__lt=cutoff,
        ).order_by("created_at")[:limit]

        result = ReconcileResult()
        for payment in qs:
            ReconciliationService._reconcile_one(payment, result)
        return result

    @staticmethod
    def reconcile_payment(payment) -> ReconcileResult:
        """Reconcile a single payment by object."""
        result = ReconcileResult()
        ReconciliationService._reconcile_one(payment, result)
        return result

    @staticmethod
    def _reconcile_one(payment, result: ReconcileResult) -> None:
        from django_cfg.apps.payments.models import Payment
        from django_cfg.apps.payments.providers import (
            ProviderNotSupported,
            get_provider,
        )
        from django_cfg.apps.payments.providers.base import (
            STATUS_FAILED,
            STATUS_SUCCEEDED,
        )

        result.checked += 1
        if not payment.external_id:
            result.skipped += 1
            return

        try:
            provider = get_provider(payment.provider)
            snapshot = provider.retrieve_payment(external_id=payment.external_id)
        except ProviderNotSupported:
            result.skipped += 1
            return
        except Exception as exc:  # noqa: BLE001
            result.errors.append(f"{payment.short_id}: {exc}")
            return

        # Already settled provider-side → apply the matching transition.
        if snapshot.status == STATUS_SUCCEEDED and payment.status != Payment.Status.SUCCEEDED:
            ReconciliationService._mark_succeeded(payment, result)
        elif snapshot.status == STATUS_FAILED and payment.status != Payment.Status.FAILED:
            ReconciliationService._mark_failed(payment, result)
        else:
            result.skipped += 1

    @staticmethod
    @transaction.atomic
    def _mark_succeeded(payment, result: ReconcileResult) -> None:
        from django_cfg.apps.payments.models import Payment
        from django_cfg.apps.payments.services.payment_service import run_fulfillment

        payment.status = Payment.Status.SUCCEEDED
        payment.save(update_fields=["status", "updated_at"])
        result.updated += 1

        # SAME success path as the webhook handler: signal + host hook. No
        # PaymentEvent exists on this path (nothing was delivered), so a hook
        # failure is only logged.
        run_fulfillment(payment)
        result.activated += 1

    @staticmethod
    @transaction.atomic
    def _mark_failed(payment, result: ReconcileResult) -> None:
        from django_cfg.apps.payments import signals
        from django_cfg.apps.payments.models import Payment

        payment.status = Payment.Status.FAILED
        payment.save(update_fields=["status", "updated_at"])
        result.updated += 1

        signals.payment_failed.send(sender=Payment, payment=payment)
