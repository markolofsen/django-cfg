"""StripeProvider — the only file importing the ``stripe`` SDK.

Uses an instance-based ``StripeClient`` (no global ``stripe.api_key`` mutation,
safe across concurrent RQ workers). PaymentIntents are the primary flow; the
webhook is the source of truth.

The SDK import is lazy (inside ``__init__``) so the app — and this module's
``parse_event_dict`` / ``_EVENT_MAP``, used by webhook replay and the listen
command — loads even when the ``stripe`` extra isn't installed.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from django.core.exceptions import ImproperlyConfigured

from django_cfg.apps.payments.config import get_payments_config
from django_cfg.apps.payments.providers.base import (
    EVENT_FAILED,
    EVENT_INVOICE_ACTION_REQUIRED,
    EVENT_INVOICE_FAILED,
    EVENT_INVOICE_PAID,
    EVENT_OTHER,
    EVENT_REFUND,
    EVENT_SUB_DELETED,
    EVENT_SUB_UPDATED,
    EVENT_SUCCEEDED,
    STATUS_CANCELLED,
    STATUS_FAILED,
    STATUS_PENDING,
    STATUS_PROCESSING,
    STATUS_REQUIRES_ACTION,
    STATUS_SUCCEEDED,
    SUBSCRIPTION_EVENT_TYPES,
    CheckoutSession,
    ConfirmType,
    PaymentProvider,
    PaymentSnapshot,
    ProviderError,
    ProviderWebhookError,
    RefundResult,
    SubscriptionEventData,
    SubscriptionSession,
    WebhookResult,
)

if TYPE_CHECKING:
    from django_cfg.apps.payments.models import Payment


# Stripe event type → our normalized event type. The SINGLE source of truth for
# event mapping — both live delivery (`verify_and_parse_webhook`) and replay
# (`WebhookService`) go through `parse_event_dict`, so this map can't drift.
_EVENT_MAP = {
    # one-time payment
    "payment_intent.succeeded": EVENT_SUCCEEDED,
    "payment_intent.payment_failed": EVENT_FAILED,
    "charge.refunded": EVENT_REFUND,
    # subscription lifecycle (later phase). created + updated both upsert status.
    "customer.subscription.created": EVENT_SUB_UPDATED,
    "customer.subscription.updated": EVENT_SUB_UPDATED,
    "customer.subscription.deleted": EVENT_SUB_DELETED,
    "invoice.paid": EVENT_INVOICE_PAID,
    "invoice.payment_failed": EVENT_INVOICE_FAILED,
    "invoice.payment_action_required": EVENT_INVOICE_ACTION_REQUIRED,
}


def _to_plain_dict(obj) -> dict:
    """Normalize a stripe.StripeObject (or dict) to a plain nested dict.

    StripeObject overrides `.get`/`__getitem__` in ways that break plain-dict
    access, so convert once at the boundary. Falls back gracefully if a plain
    dict is passed (e.g. from a test mock).
    """
    if isinstance(obj, dict):
        return obj
    to_dict = getattr(obj, "to_dict_recursive", None)
    if callable(to_dict):
        return to_dict()
    to_dict = getattr(obj, "to_dict", None)
    if callable(to_dict):
        return to_dict()
    return dict(obj)


def _sum_item_quantity(sub_obj: dict) -> int | None:
    """Total item quantity on a Subscription object (seat/instance count).

    One item today; sum defensively so distinct items (a future model) still
    yield the right count. Returns None when items aren't present on the payload
    (so a subscription handler leaves the stored count untouched rather than
    zeroing it).
    """
    items = sub_obj.get("items")
    data = items.get("data") if isinstance(items, dict) else None
    if not data:
        return None
    total = 0
    for it in data:
        q = it.get("quantity") if isinstance(it, dict) else None
        total += int(q) if q is not None else 1
    return total


# Stripe PaymentIntent.status → our normalized payment status.
_STATUS_MAP = {
    "requires_payment_method": STATUS_PENDING,
    "requires_confirmation": STATUS_PENDING,
    "requires_action": STATUS_REQUIRES_ACTION,
    "processing": STATUS_PROCESSING,
    "requires_capture": STATUS_REQUIRES_ACTION,
    "succeeded": STATUS_SUCCEEDED,
    "canceled": STATUS_CANCELLED,
}


class StripeProvider(PaymentProvider):
    name = "stripe"

    def __init__(self) -> None:
        # Lazy import so the app installs without the optional SDK; the error
        # only surfaces when a Stripe call is actually attempted.
        try:
            import stripe
        except ImportError as exc:
            raise ImproperlyConfigured(
                "The stripe SDK is required for the stripe provider: "
                "pip install django-cfg[payments]"
            ) from exc

        secret = get_payments_config().stripe_secret_key
        if not secret:
            raise RuntimeError("STRIPE__SECRET_KEY is not configured.")
        # Instance client — no module-global mutation.
        self._stripe = stripe
        self._client = stripe.StripeClient(secret)

    # ── create ──────────────────────────────────────────────────────────────
    def create_checkout(
        self, *, payment: "Payment", idempotency_key: str
    ) -> CheckoutSession:
        try:
            intent = self._client.payment_intents.create(
                {
                    "amount": payment.amount,  # minor units — authoritative
                    "currency": payment.currency,
                    "metadata": {
                        "payment_short_id": payment.short_id,
                        "reference_kind": payment.reference_kind,
                        "reference_id": payment.reference_id,
                        "owner_id": str(payment.owner_id),
                    },
                    "automatic_payment_methods": {"enabled": True},
                },
                options={"idempotency_key": idempotency_key},
            )
        except self._stripe.error.AuthenticationError as exc:
            raise ProviderError("Stripe authentication failed — check STRIPE__SECRET_KEY.") from exc
        except self._stripe.error.StripeError as exc:
            raise ProviderError(f"Stripe error: {exc.user_message or exc}") from exc
        return CheckoutSession(
            provider=self.name,
            external_id=intent.id,
            client_secret=intent.client_secret,
            redirect_url=None,
            amount=payment.amount,
            currency=payment.currency,
        )

    # ── webhook ─────────────────────────────────────────────────────────────
    def verify_and_parse_webhook(
        self, *, payload: bytes, signature: str
    ) -> WebhookResult:
        secrets = get_payments_config().stripe_webhook_secrets
        if not secrets:
            raise ProviderWebhookError("No Stripe webhook secret configured.")

        event = None
        last_error: Exception | None = None
        # Try each secret to support rotation.
        for secret in secrets:
            try:
                event = self._stripe.Webhook.construct_event(payload, signature, secret)
                break
            except self._stripe.error.SignatureVerificationError as exc:
                last_error = exc
            except ValueError as exc:  # malformed payload
                raise ProviderWebhookError(f"Invalid webhook payload: {exc}") from exc

        if event is None:
            raise ProviderWebhookError(
                f"Stripe signature verification failed: {last_error}"
            )

        # `construct_event` returns a stripe.Event (StripeObject), where `.get`
        # does NOT behave like dict.get — normalize to a plain dict first so the
        # rest of the parsing is uniform (and matches a mocked dict in tests).
        return self.parse_event_dict(_to_plain_dict(event))

    @staticmethod
    def parse_event_dict(data: dict) -> WebhookResult:
        """Normalize a Stripe event envelope (already a plain dict) → WebhookResult.

        The ONE parsing path shared by live delivery (after signature verify) and
        replay (``WebhookService``) — so the Stripe→normalized mapping can never
        differ between them. Subscription-lifecycle events additionally get a
        ``subscription`` payload; payment events leave it None.
        """
        event_type = data.get("type", "")
        obj = (data.get("data", {}) or {}).get("object", {}) or {}
        normalized = _EVENT_MAP.get(event_type, EVENT_OTHER)

        subscription = None
        if normalized in SUBSCRIPTION_EVENT_TYPES:
            subscription = StripeProvider._extract_subscription(event_type, obj)

        external_id, amount, currency = StripeProvider._extract_object(event_type, obj)
        return WebhookResult(
            event_id=data.get("id", ""),
            event_type=normalized,
            external_id=external_id,
            amount=amount,
            currency=currency,
            raw=data,
            subscription=subscription,
        )

    @staticmethod
    def _extract_object(
        event_type: str, obj: dict
    ) -> tuple[str, int | None, str | None]:
        """Pull (payment_intent_id, amount, currency) from the event object.

        Subscription/invoice events carry no PaymentIntent id — their ``obj`` is a
        Subscription or Invoice, so this returns an empty external_id for them
        (the subscription payload carries what a subscription handler needs).
        """
        if event_type.startswith("charge."):
            # charge.refunded → object is a Charge; map back to its PaymentIntent.
            external_id = obj.get("payment_intent") or obj.get("id", "")
            amount = obj.get("amount_refunded")
        elif event_type.startswith("payment_intent."):
            external_id = obj.get("id", "")
            amount = obj.get("amount")
        else:
            # subscription / invoice — no PaymentIntent to map to a Payment row.
            return "", None, obj.get("currency")
        return external_id, amount, obj.get("currency")

    @staticmethod
    def _extract_subscription(event_type: str, obj: dict) -> SubscriptionEventData:
        """Pull the subscription-shaped fields from a Subscription or Invoice obj.

        - ``customer.subscription.*`` → ``obj`` is the Subscription itself.
        - ``invoice.*`` → ``obj`` is an Invoice; its ``subscription`` field points
          back to the Subscription id, and ``amount_paid`` is the renewal charge.
        """
        if event_type.startswith("customer.subscription."):
            return SubscriptionEventData(
                stripe_subscription_id=obj.get("id", "") or "",
                stripe_status=obj.get("status", "") or "",
                customer_id=obj.get("customer", "") or "",
                current_period_end=obj.get("current_period_end"),
                # Single-item quantity = seat count. Sum defensively in case a
                # future sub grows distinct items.
                quantity=_sum_item_quantity(obj),
            )
        # invoice.* — the Subscription id can be a string or a nested object.
        sub_ref = obj.get("subscription")
        if isinstance(sub_ref, dict):
            sub_ref = sub_ref.get("id", "")
        return SubscriptionEventData(
            stripe_subscription_id=sub_ref or "",
            stripe_status="",  # invoices don't carry the sub status; don't overwrite
            customer_id=obj.get("customer", "") or "",
            current_period_end=obj.get("period_end") or obj.get("current_period_end"),
            amount_paid=obj.get("amount_paid"),
            currency=obj.get("currency"),
        )

    # ── refund ──────────────────────────────────────────────────────────────
    def refund(
        self, *, payment: "Payment", amount: int | None = None
    ) -> RefundResult:
        params: dict = {"payment_intent": payment.external_id}
        if amount is not None:
            params["amount"] = amount
        refund = self._client.refunds.create(params)
        return RefundResult(
            external_id=refund.id,
            amount=refund.amount,
            currency=refund.currency,
            raw=_to_plain_dict(refund),
        )

    # ── reconcile ─────────────────────────────────────────────────────────────
    def retrieve_payment(self, *, external_id: str) -> PaymentSnapshot:
        intent = self._client.payment_intents.retrieve(external_id)
        refunded = 0
        # amount_received tells how much was captured; refunds reduce it via charges.
        charges = getattr(intent, "charges", None)
        if charges is not None:
            for charge in getattr(charges, "data", []) or []:
                refunded += getattr(charge, "amount_refunded", 0) or 0
        return PaymentSnapshot(
            external_id=intent.id,
            status=_STATUS_MAP.get(intent.status, STATUS_FAILED),
            amount=intent.amount,
            currency=intent.currency,
            amount_refunded=refunded,
            raw=_to_plain_dict(intent),
        )

    # ── subscriptions: customer identity (later phase, no extra coupling) ────
    def ensure_customer(self, *, external_ref: str, email: str, name: str = "") -> str:
        """Create a Stripe Customer for the owner (idempotent by metadata).

        Reuses an existing Customer tagged with our ``cfg_owner_ref`` metadata if
        one is found (guards against duplicate Customers on a retry that raced
        the DB write-back), else creates one.
        """
        try:
            # Prefer an existing Customer carrying our owner ref (search API).
            found = self._client.customers.search(
                {"query": f"metadata['cfg_owner_ref']:'{external_ref}'", "limit": 1}
            )
            existing = (getattr(found, "data", None) or [None])[0]
            if existing is not None:
                return existing.id

            customer = self._client.customers.create(
                {
                    "email": email or None,
                    "name": name or None,
                    "metadata": {"cfg_owner_ref": external_ref},
                },
                options={"idempotency_key": f"cust-{external_ref}"},
            )
        except self._stripe.error.AuthenticationError as exc:
            raise ProviderError("Stripe authentication failed — check STRIPE__SECRET_KEY.") from exc
        except self._stripe.error.StripeError as exc:
            raise ProviderError(f"Stripe error: {exc.user_message or exc}") from exc
        return customer.id

    # ── subscriptions: create (deferred flow) ────────────────────────────────
    def create_subscription(
        self,
        *,
        customer_id: str,
        price_id: str,
        idempotency_key: str,
        quantity: int = 1,
        trial_days: int | None = None,
        metadata: dict[str, str] | None = None,
    ) -> SubscriptionSession:
        """Create an ``incomplete`` subscription; the client confirms it.

        The blessed deferred flow: create with
        ``payment_behavior='default_incomplete'`` and
        ``save_default_payment_method='on_subscription'`` so the card entered to
        pay the first invoice becomes the default for renewals. Expand both the
        first invoice's ``confirmation_secret`` (paid path) and
        ``pending_setup_intent`` ($0 / trial path) so we can hand the client
        exactly one secret + the matching ``confirm_type``.
        """
        params: dict = {
            "customer": customer_id,
            "items": [{"price": price_id, "quantity": quantity}],
            "payment_behavior": "default_incomplete",
            "payment_settings": {"save_default_payment_method": "on_subscription"},
            # Modern field: confirmation_secret, NOT legacy payment_intent.
            "expand": ["latest_invoice.confirmation_secret", "pending_setup_intent"],
        }
        if trial_days:
            params["trial_period_days"] = trial_days
        if metadata:
            params["metadata"] = metadata
        try:
            sub = self._client.subscriptions.create(
                params, options={"idempotency_key": idempotency_key}
            )
        except self._stripe.error.AuthenticationError as exc:
            raise ProviderError("Stripe authentication failed — check STRIPE__SECRET_KEY.") from exc
        except self._stripe.error.StripeError as exc:
            raise ProviderError(f"Stripe error: {exc.user_message or exc}") from exc

        confirm_type, client_secret = self._pick_confirm(sub)
        return SubscriptionSession(
            provider=self.name,
            stripe_subscription_id=sub.id,
            status=getattr(sub, "status", "incomplete"),
            confirm_type=confirm_type,
            client_secret=client_secret,
        )

    @staticmethod
    def _pick_confirm(sub) -> tuple[str, str | None]:
        """Choose (confirm_type, client_secret) from an expanded Subscription.

        A ``pending_setup_intent`` means there's nothing to charge now (trial /
        $0) → the client runs ``confirmSetup`` to save a card. Otherwise the
        first invoice's ``confirmation_secret`` drives ``confirmPayment``.
        """
        setup = getattr(sub, "pending_setup_intent", None)
        if setup is not None:
            secret = getattr(setup, "client_secret", None) if not isinstance(setup, str) else None
            return ConfirmType.SETUP.value, secret

        invoice = getattr(sub, "latest_invoice", None)
        secret = None
        if invoice is not None and not isinstance(invoice, str):
            cs = getattr(invoice, "confirmation_secret", None)
            if cs is not None:
                secret = getattr(cs, "client_secret", None)
        return ConfirmType.PAYMENT.value, secret

    # ── subscriptions: cancel + portal ───────────────────────────────────────
    def cancel_subscription(
        self, *, stripe_subscription_id: str, at_period_end: bool = True
    ) -> None:
        """Cancel at Stripe; the webhook reconciles our DB (never mutated here).

        ``at_period_end`` → update the sub with ``cancel_at_period_end=True`` (the
        customer keeps paid access; Stripe fires ``.updated`` now, ``.deleted``
        when the period lapses). Immediate → ``subscriptions.cancel`` fires
        ``.deleted`` at once.
        """
        try:
            if at_period_end:
                self._client.subscriptions.update(
                    stripe_subscription_id, {"cancel_at_period_end": True}
                )
            else:
                self._client.subscriptions.cancel(stripe_subscription_id)
        except self._stripe.error.AuthenticationError as exc:
            raise ProviderError("Stripe authentication failed — check STRIPE__SECRET_KEY.") from exc
        except self._stripe.error.StripeError as exc:
            raise ProviderError(f"Stripe error: {exc.user_message or exc}") from exc

    def set_subscription_quantity(
        self, *, stripe_subscription_id: str, quantity: int
    ) -> None:
        """Set the single item's quantity, prorated; quantity 0 → cancel.

        Retrieve the sub to find its (one) item id, then update that item's
        quantity with ``proration_behavior='create_prorations'`` so mid-cycle
        add/remove is fairly billed. Quantity ≤ 0 means nothing remains →
        cancel the whole subscription at period end. The webhook reconciles our
        DB; this never touches it.
        """
        try:
            if quantity <= 0:
                self._client.subscriptions.update(
                    stripe_subscription_id, {"cancel_at_period_end": True}
                )
                return
            sub = self._client.subscriptions.retrieve(stripe_subscription_id)
            items = getattr(getattr(sub, "items", None), "data", None) or []
            if not items:
                raise ProviderError(
                    f"subscription {stripe_subscription_id} has no items to adjust."
                )
            item_id = items[0].id
            self._client.subscription_items.update(
                item_id,
                {"quantity": quantity, "proration_behavior": "create_prorations"},
            )
        except self._stripe.error.AuthenticationError as exc:
            raise ProviderError("Stripe authentication failed — check STRIPE__SECRET_KEY.") from exc
        except self._stripe.error.StripeError as exc:
            raise ProviderError(f"Stripe error: {exc.user_message or exc}") from exc

    def create_billing_portal_session(
        self, *, customer_id: str, return_url: str
    ) -> str:
        """Create a Billing Portal session for ``customer_id`` → its URL."""
        try:
            session = self._client.billing_portal.sessions.create(
                {"customer": customer_id, "return_url": return_url}
            )
        except self._stripe.error.AuthenticationError as exc:
            raise ProviderError("Stripe authentication failed — check STRIPE__SECRET_KEY.") from exc
        except self._stripe.error.StripeError as exc:
            raise ProviderError(f"Stripe error: {exc.user_message or exc}") from exc
        return session.url

    def capabilities(self) -> dict[str, bool]:
        caps = super().capabilities()
        caps["reconcile"] = True
        caps["subscriptions"] = True
        return caps
