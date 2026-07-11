"""RQ tasks for payments (lazy imports inside, safe to enqueue by dotted path)."""

from __future__ import annotations

import logging

logger = logging.getLogger(__name__)


def process_webhook_event(
    provider_name: str,
    event_id: str,
    event_type: str,
    external_id: str,
    amount: int | None,
    currency: str | None,
    raw: dict,
) -> None:
    """Fulfill a verified provider webhook event (enqueued by StripeWebhookView).

    Reconstructs the normalized ``WebhookResult`` and delegates to the
    idempotent ``PaymentService.handle_webhook``.
    """
    from django_cfg.apps.payments.providers.base import WebhookResult
    from django_cfg.apps.payments.services import PaymentService

    result = WebhookResult(
        event_id=event_id,
        event_type=event_type,
        external_id=external_id,
        amount=amount,
        currency=currency,
        raw=raw,
    )
    PaymentService.handle_webhook(result=result, provider_name=provider_name)


def reconcile_pending_payments() -> None:
    """Scheduled job: catch payments stuck in PROCESSING up to the provider.

    Stripe webhooks are the source of truth; this is the safety net for missed
    deliveries — it polls the provider and applies the real status. Providers
    that can't poll (no ``retrieve_payment``) are skipped automatically.
    """
    from django_cfg.apps.payments.services import ReconciliationService

    result = ReconciliationService.reconcile_stuck(older_than_hours=1, limit=200)
    if result.updated or result.errors:
        logger.warning(
            "payments reconcile: checked=%d updated=%d activated=%d skipped=%d errors=%d",
            result.checked, result.updated, result.activated,
            result.skipped, len(result.errors),
        )
