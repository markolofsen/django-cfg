"""Provider abstraction — the contract every payment provider implements.

An ABC plus a ``get_provider()`` factory that resolves a dotted path from the
registry via ``import_string``. Hosts register additional providers through
``PaymentsConfig.provider_registry`` (or, in tests, the
``PAYMENTS_PROVIDER_REGISTRY`` Django setting, which wins).

Provider code is the ONLY place a vendor SDK (``stripe``) is imported. The rest
of the app — models, services, API — depends on these neutral DTOs.

The subscription-shaped DTOs/constants below are part of the provider contract
even though the service layer only fulfills one-time payments today: the Stripe
provider still parses subscription-lifecycle events, and the service marks them
processed for a later phase (see ``PaymentService._apply_event``).
"""

from __future__ import annotations

import abc
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from django.conf import settings
from django.db import models
from django.utils.module_loading import import_string

if TYPE_CHECKING:
    from django_cfg.apps.payments.models import Payment


class ConfirmType(models.TextChoices):
    """Which client-side confirm the deferred subscription flow needs.

    Lives in the provider layer (the lowest of the payment modules) so both the
    Stripe impl that produces it and any serializer that exposes it read ONE
    source — a value can't drift between them.
    """

    #: First invoice is due → ``stripe.confirmPayment``.
    PAYMENT = 'payment', 'Payment'
    #: $0 / trial card-on-file → ``stripe.confirmSetup``.
    SETUP = 'setup', 'Setup'


class ProviderError(Exception):
    """Raised by a provider when an upstream API call fails (auth, rate-limit, etc.)."""


class ProviderWebhookError(Exception):
    """Raised when a webhook payload fails signature verification or parsing."""


@dataclass(frozen=True)
class CheckoutSession:
    """Result of creating a payment with the provider."""

    provider: str
    external_id: str  # Stripe PaymentIntent / Checkout Session id
    client_secret: str | None  # for client-side confirm (Stripe Elements)
    redirect_url: str | None  # for hosted/redirect checkout
    amount: int  # minor units
    currency: str


@dataclass(frozen=True)
class SubscriptionEventData:
    """Subscription-shaped fields pulled from a lifecycle webhook.

    ``customer.subscription.*`` and ``invoice.*`` events don't map to a
    ``Payment`` row — they carry a Stripe Subscription id + status. This DTO is
    the neutral shape a subscription handler (later phase) upserts from.
    ``current_period_end`` guards out-of-order delivery; ``amount_paid`` records
    a renewal charge on ``invoice.paid``.
    """

    stripe_subscription_id: str
    stripe_status: str  # raw Stripe status (active/past_due/…); '' on invoice events
    customer_id: str  # cus_… — for reconciliation / lookup fallback
    current_period_end: int | None  # unix seconds, or None
    amount_paid: int | None = None  # minor units, on invoice.paid (renewal)
    currency: str | None = None
    quantity: int | None = None  # single-item quantity (seat/instance count); None if absent


@dataclass(frozen=True)
class WebhookResult:
    """Normalized provider event, ready for ``PaymentService.handle_webhook``."""

    event_id: str  # provider event id — idempotency dedupe key
    event_type: str  # normalized: EVENT_* below
    external_id: str  # payment intent / charge id → maps to Payment.external_id
    amount: int | None  # minor units, when present
    currency: str | None
    raw: dict = field(default_factory=dict)  # full provider payload (stored verbatim)
    #: Present only on subscription-lifecycle events; None otherwise.
    subscription: "SubscriptionEventData | None" = None


@dataclass(frozen=True)
class SubscriptionSession:
    """Result of creating a Stripe Billing subscription (deferred flow).

    The subscription is created ``incomplete``; the client finishes it by
    confirming the returned secret. ``confirm_type`` tells the frontend which
    Stripe.js call to make:

      - ``'payment'`` — a first invoice is due; ``client_secret`` is the
        invoice's ``confirmation_secret`` → ``stripe.confirmPayment``.
      - ``'setup'``   — nothing to charge now (trial / future card-on-file);
        ``client_secret`` is the ``pending_setup_intent`` → ``stripe.confirmSetup``.
    """

    provider: str
    stripe_subscription_id: str
    status: str  # incomplete | incomplete_expired | trialing | active | ...
    confirm_type: str  # 'payment' | 'setup'
    client_secret: str | None


@dataclass(frozen=True)
class RefundResult:
    external_id: str  # provider refund id
    amount: int  # minor units refunded
    currency: str
    raw: dict = field(default_factory=dict)


@dataclass(frozen=True)
class PaymentSnapshot:
    """Authoritative state of a payment as the provider currently sees it.

    Used by reconciliation to catch up after a missed/late webhook.
    """

    external_id: str
    status: str  # normalized: one of STATUS_* below
    amount: int | None  # minor units
    currency: str | None
    amount_refunded: int = 0
    raw: dict = field(default_factory=dict)


class ProviderNotSupported(Exception):
    """Raised when a provider does not implement an optional capability."""


# Normalized webhook event types the service layer branches on.
EVENT_SUCCEEDED = "payment.succeeded"
EVENT_FAILED = "payment.failed"
EVENT_REFUND = "refund"
EVENT_OTHER = "other"

# Subscription-lifecycle events (handled in a later phase). These carry a
# ``WebhookResult.subscription`` payload and do NOT map to a Payment row.
EVENT_SUB_UPDATED = "subscription.updated"  # created + updated (upsert status)
EVENT_SUB_DELETED = "subscription.deleted"  # canceled → revoke entitlements
EVENT_INVOICE_PAID = "invoice.paid"  # renewal charge succeeded
EVENT_INVOICE_FAILED = "invoice.failed"  # renewal charge failed → past_due
EVENT_INVOICE_ACTION_REQUIRED = "invoice.action_required"  # SCA re-auth needed

#: The subscription-lifecycle set, for callers that need to branch payment-vs-sub.
SUBSCRIPTION_EVENT_TYPES = frozenset(
    {
        EVENT_SUB_UPDATED,
        EVENT_SUB_DELETED,
        EVENT_INVOICE_PAID,
        EVENT_INVOICE_FAILED,
        EVENT_INVOICE_ACTION_REQUIRED,
    }
)

# Normalized payment statuses (mirror Payment.Status values).
STATUS_PENDING = "pending"
STATUS_PROCESSING = "processing"
STATUS_REQUIRES_ACTION = "requires_action"
STATUS_SUCCEEDED = "succeeded"
STATUS_FAILED = "failed"
STATUS_CANCELLED = "cancelled"


class PaymentProvider(abc.ABC):
    """Provider-agnostic payment contract.

    Implementations hold their own SDK client (no global mutation) and translate
    between the provider's wire shape and these neutral DTOs.
    """

    #: Stable provider identifier, e.g. "stripe".
    name: str = "base"

    @abc.abstractmethod
    def create_checkout(
        self, *, payment: "Payment", idempotency_key: str
    ) -> CheckoutSession:
        """Create a provider payment for ``payment`` (amount is authoritative)."""

    @abc.abstractmethod
    def verify_and_parse_webhook(
        self, *, payload: bytes, signature: str
    ) -> WebhookResult:
        """Verify the signature on the RAW body and normalize the event.

        Must raise ``ProviderWebhookError`` on a bad/absent signature.
        """

    @abc.abstractmethod
    def refund(
        self, *, payment: "Payment", amount: int | None = None
    ) -> RefundResult:
        """Refund ``payment`` fully (``amount=None``) or partially (minor units)."""

    def retrieve_payment(self, *, external_id: str) -> PaymentSnapshot:
        """Fetch the provider's current view of a payment (for reconciliation).

        Optional capability — providers that can't poll raise
        ``ProviderNotSupported``. Stripe implements it via PaymentIntent retrieve.
        """
        raise ProviderNotSupported(
            f"{self.name} does not support retrieve_payment."
        )

    def ensure_customer(self, *, external_ref: str, email: str, name: str = "") -> str:
        """Get-or-create the provider Customer, return its id (e.g. ``cus_…``).

        ``external_ref`` is a stable idempotency handle (the host's owner id)
        the provider stores in metadata so retries don't duplicate the Customer.
        Optional capability (subscription providers) — others raise
        ``ProviderNotSupported``.
        """
        raise ProviderNotSupported(f"{self.name} does not support ensure_customer.")

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
        """Create a recurring subscription for ``customer_id`` at ``price_id``.

        The deferred / ``default_incomplete`` flow: the subscription is created
        ``incomplete`` and the client confirms the returned secret. ``quantity``
        supports a single-item seats model — one item of N quantity. Optional
        capability — non-subscription providers raise ``ProviderNotSupported``.
        """
        raise ProviderNotSupported(
            f"{self.name} does not support create_subscription."
        )

    def cancel_subscription(
        self, *, stripe_subscription_id: str, at_period_end: bool = True
    ) -> None:
        """Cancel a subscription at the provider.

        ``at_period_end=True`` (the default) schedules cancellation for the end of
        the paid period — the customer keeps access they've paid for and Stripe
        fires ``customer.subscription.updated`` (``cancel_at_period_end=True``),
        then ``.deleted`` when the period lapses. The webhook is what flips the
        host's internal status; this call NEVER mutates our DB. Immediate
        cancellation (``at_period_end=False``) fires ``.deleted`` right away.
        Optional capability — non-subscription providers raise ``ProviderNotSupported``.
        """
        raise ProviderNotSupported(
            f"{self.name} does not support cancel_subscription."
        )

    def set_subscription_quantity(
        self, *, stripe_subscription_id: str, quantity: int
    ) -> None:
        """Adjust the subscription's item quantity, prorated.

        The single-item model: ONE Stripe item with a quantity = the number of
        billable seats/instances. Adding or removing one mid-cycle moves this
        quantity, prorated so the customer is fairly credited/charged for the
        unused/used remainder. A ``quantity`` of 0 means "nothing left" → the
        whole subscription is canceled at period end.

        Like every provider subscription call this NEVER mutates our DB — the
        provider fires ``customer.subscription.updated`` and the webhook
        reconciles. Optional capability — non-subscription providers raise
        ``ProviderNotSupported``.
        """
        raise ProviderNotSupported(
            f"{self.name} does not support set_subscription_quantity."
        )

    def create_billing_portal_session(
        self, *, customer_id: str, return_url: str
    ) -> str:
        """Create a provider-hosted Billing Portal session → its one-time URL.

        The portal is the self-serve surface for update-card / cancel / view
        invoices. Any change the customer makes there arrives back as a
        lifecycle webhook. Optional capability — non-subscription providers
        raise ``ProviderNotSupported``.
        """
        raise ProviderNotSupported(
            f"{self.name} does not support create_billing_portal_session."
        )

    def capabilities(self) -> dict[str, bool]:
        """Hints so callers branch without leaking provider identity."""
        return {
            "client_confirm": True,  # returns a client_secret for frontend confirm
            "hosted_redirect": False,  # returns a redirect_url for a hosted page
            "partial_refund": True,
            "reconcile": False,  # can poll provider for status (retrieve_payment)
            "subscriptions": False,  # ensure_customer / create_subscription
        }


def get_provider(name: str | None = None) -> PaymentProvider:
    """Resolve a provider instance from the registry (default: ``stripe``).

    Django settings win over the pydantic config so tests can inject fakes with
    the ``settings`` fixture (``PAYMENTS_PROVIDER_REGISTRY`` /
    ``PAYMENTS_DEFAULT_PROVIDER``) without touching the host's ``PaymentsConfig``.
    """
    from django_cfg.apps.payments.config import get_payments_config

    registry = getattr(settings, "PAYMENTS_PROVIDER_REGISTRY", None)
    provider_name = name or getattr(settings, "PAYMENTS_DEFAULT_PROVIDER", None)
    if registry is None or provider_name is None:
        cfg = get_payments_config()
        if registry is None:
            registry = cfg.provider_registry
        if provider_name is None:
            provider_name = cfg.default_provider

    dotted = registry.get(provider_name)
    if not dotted:
        raise ValueError(f"Unknown payment provider: {provider_name!r}")
    provider_cls = import_string(dotted)
    return provider_cls()
