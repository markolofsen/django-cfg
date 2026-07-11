"""PaymentService — checkout orchestration + webhook fulfillment.

This is where the provider-neutral models and the provider abstraction meet.
``create_checkout`` mints a Payment for an owner + amount; ``handle_webhook``
is the idempotent fulfillment path.

Fulfillment is a seam, not a hardcoded order flow: on success the service emits
the ``payment_succeeded`` signal and (when configured) invokes the host's
``fulfillment_hook`` dotted path — see ``run_fulfillment``. Reconciliation goes
through the SAME path so a caught-up payment fulfills identically to a
webhook-delivered one.
"""

from __future__ import annotations

import logging
import uuid
from decimal import Decimal

from django.db import IntegrityError, transaction
from django.utils.module_loading import import_string

from django_cfg.apps.payments import signals
from django_cfg.apps.payments.config import get_default_currency, get_payments_config
from django_cfg.apps.payments.models import Payment, PaymentEvent
from django_cfg.apps.payments.providers import (
    CheckoutSession,
    PaymentProvider,
    WebhookResult,
    get_provider,
)
from django_cfg.apps.payments.providers.base import (
    EVENT_FAILED,
    EVENT_REFUND,
    EVENT_SUCCEEDED,
    SUBSCRIPTION_EVENT_TYPES,
    ProviderError,
)

logger = logging.getLogger(__name__)


class PaymentError(Exception):
    pass


def _to_minor_units(amount: Decimal | None, currency: str) -> int:
    """Convert a Decimal major amount to integer minor units.

    Helper for hosts whose prices live as Decimal major units. Stripe-style
    zero-decimal currencies are not multiplied; everything else uses 2 fraction
    digits.
    """
    if amount is None:
        return 0
    zero_decimal = {"jpy", "krw", "vnd", "clp", "xof", "xaf"}
    factor = 1 if currency.lower() in zero_decimal else 100
    return int((amount * factor).quantize(Decimal("1")))


def run_fulfillment(payment: Payment, *, event: PaymentEvent | None = None) -> None:
    """Fulfill a SUCCEEDED payment — the shared success path.

    Called by both the webhook handler and reconciliation so the two can't
    diverge. Two mechanisms, in order:

    1. The ``payment_succeeded`` signal — always emitted. Receiver exceptions
       propagate (they enter the caller's record-and-retry discipline).
    2. The host's ``fulfillment_hook`` dotted path (``fn(payment) -> None``),
       when configured. Hook exceptions are logged and recorded on the
       PaymentEvent's ``error`` field but NOT re-raised — the webhook must
       still return 200 (Stripe already delivered the truth; a broken hook is
       an operator problem, fixed with ``payments_replay_webhook``).
    """
    signals.payment_succeeded.send(sender=Payment, payment=payment)

    hook_path = get_payments_config().fulfillment_hook
    if not hook_path:
        return
    try:
        hook = import_string(hook_path)
        hook(payment)
    except Exception as exc:  # noqa: BLE001 — record, never break the webhook
        logger.exception(
            "fulfillment hook %s failed for payment %s", hook_path, payment.short_id,
        )
        if event is not None:
            event.error = f"fulfillment hook failed: {exc}"
            event.save(update_fields=["error"])


class PaymentService:
    @staticmethod
    @transaction.atomic
    def create_checkout(
        *,
        owner,
        amount: int,
        currency: str | None = None,
        reference_kind: str = "",
        reference_id: str = "",
        created_by=None,
        idempotency_key: str | None = None,
        provider_name: str | None = None,
    ) -> tuple[Payment, CheckoutSession]:
        """Create (or re-use) a Payment + provider checkout for ``owner``.

        - ``amount`` is integer MINOR units (cents) — the host derives it
          server-side from its own frozen source of truth (order, plan, cart);
          never pass raw client input.
        - ``idempotency_key`` dedupes double-clicked checkout-creates: a repeat
          re-uses the existing Payment, and the provider's own idempotency
          returns the SAME intent (same ``client_secret``). Omitted → a random
          key is minted (no cross-request dedupe).
        - ``reference_kind``/``reference_id`` record WHAT was paid for, in the
          host's vocabulary (e.g. ``("order", "ord_abc123")``).

        Returns ``(payment, session)`` so the API can hand the ``client_secret``
        to the frontend without a second provider round-trip in the view.
        """
        if amount is None or amount <= 0:
            raise PaymentError("Checkout has no payable amount.")

        currency = (currency or get_default_currency()).lower()
        if idempotency_key is None:
            idempotency_key = f"chk-{uuid.uuid4().hex}"

        provider: PaymentProvider = get_provider(provider_name)

        def _reissue(existing: Payment) -> tuple[Payment, CheckoutSession]:
            """Re-issue the checkout for an existing Payment (provider
            idempotency yields the SAME intent / client_secret)."""
            try:
                session = provider.create_checkout(
                    payment=existing, idempotency_key=idempotency_key,
                )
            except ProviderError as exc:
                raise PaymentError(str(exc)) from exc
            return existing, session

        existing = Payment.objects.filter(idempotency_key=idempotency_key).first()
        if existing is not None:
            return _reissue(existing)

        # The check-then-create above is a TOCTOU race: two near-simultaneous
        # checkout requests (double-click, or the client firing twice) both see
        # no existing Payment and both try to INSERT the same unique
        # ``idempotency_key`` → one wins, the other hits IntegrityError. Catch it
        # in a savepoint (so the outer atomic block isn't poisoned) and fall back
        # to re-issuing the winner's Payment — same behavior as an early repeat.
        try:
            with transaction.atomic():
                payment = Payment.objects.create(
                    owner=owner,
                    reference_kind=reference_kind,
                    reference_id=reference_id,
                    created_by=created_by,
                    provider=provider.name,
                    status=Payment.Status.PENDING,
                    amount=amount,
                    currency=currency,
                    idempotency_key=idempotency_key,
                )
        except IntegrityError:
            winner = Payment.objects.filter(idempotency_key=idempotency_key).first()
            if winner is None:
                # The unique violation was on some OTHER constraint — don't
                # swallow it as a benign idempotency replay.
                raise
            return _reissue(winner)

        try:
            session = provider.create_checkout(
                payment=payment, idempotency_key=idempotency_key,
            )
        except ProviderError as exc:
            raise PaymentError(str(exc)) from exc
        payment.external_id = session.external_id
        payment.status = Payment.Status.PROCESSING
        payment.save(update_fields=["external_id", "status", "updated_at"])

        return payment, session

    @staticmethod
    def handle_webhook(*, result: WebhookResult, provider_name: str) -> None:
        """Idempotently fulfill a verified provider event.

        Dedupe on ``event_id``; on success run the fulfillment seam
        (``run_fulfillment``). Heavy host-side work belongs in the host's hook
        or signal receiver (ideally deferring via ``on_commit`` → RQ), so this
        returns quickly.
        """
        # Idempotency guard: get_or_create on the UNIQUE event_id.
        event, created = PaymentEvent.objects.get_or_create(
            event_id=result.event_id,
            defaults={
                "provider": provider_name,
                "event_type": result.event_type,
                "payload": result.raw,
            },
        )
        if not created and event.processed_at is not None:
            # Already handled — Stripe redelivery. No-op.
            return

        payment = (
            Payment.objects.filter(
                provider=provider_name, external_id=result.external_id,
            ).first()
            if result.external_id
            else None
        )
        if payment is not None and event.payment_id is None:
            event.payment = payment
            event.save(update_fields=["payment"])

        try:
            PaymentService._apply_event(result=result, payment=payment, event=event)
        except Exception as exc:  # noqa: BLE001 — record + re-raise for retry
            event.error = str(exc)
            event.save(update_fields=["error"])
            logger.exception("payment webhook handling failed: %s", result.event_id)
            raise

        from django.utils import timezone

        event.processed_at = timezone.now()
        event.save(update_fields=["processed_at", "error"])

    @staticmethod
    @transaction.atomic
    def _apply_event(
        *, result: WebhookResult, payment: Payment | None, event: PaymentEvent,
    ) -> None:
        # Subscription-lifecycle events carry a `subscription` payload, not a
        # Payment. The one-time engine acknowledges them (webhook 200s, event
        # marked processed) without acting — a later phase adds the handler.
        if result.event_type in SUBSCRIPTION_EVENT_TYPES:
            logger.debug(
                "subscription event %s (%s): subscription events are handled "
                "in a later phase",
                result.event_id, result.event_type,
            )
            return

        if payment is None:
            logger.warning(
                "webhook %s references unknown payment %s",
                result.event_id, result.external_id,
            )
            return

        if result.event_type == EVENT_SUCCEEDED:
            payment.status = Payment.Status.SUCCEEDED
            payment.save(update_fields=["status", "updated_at"])
            run_fulfillment(payment, event=event)

        elif result.event_type == EVENT_FAILED:
            payment.status = Payment.Status.FAILED
            payment.save(update_fields=["status", "updated_at"])
            signals.payment_failed.send(sender=Payment, payment=payment)

        elif result.event_type == EVENT_REFUND:
            payment.amount_refunded = result.amount or payment.amount
            payment.status = Payment.Status.REFUNDED
            payment.save(update_fields=["amount_refunded", "status", "updated_at"])
