"""Public test doubles for the payments engine.

Host projects (and django-cfg's own suite) test payment flows without the
Stripe SDK or network by registering ``FakeProvider`` through Django settings
— the settings override wins over the pydantic config in ``get_provider``:

    # conftest.py
    import pytest
    from django_cfg.apps.payments.testing import fake_provider_settings, FakeProvider

    @pytest.fixture
    def fake_provider(settings):
        for key, value in fake_provider_settings().items():
            setattr(settings, key, value)
        FakeProvider.reset()
        return FakeProvider

Drive outcomes with the class-level knobs (``get_provider`` builds a fresh
instance per call, so cross-call state lives on the CLASS):

- ``FakeProvider.snapshot_status`` — what ``retrieve_payment`` reports
  (drives reconciliation tests).
- ``FakeProvider.can_reconcile`` — the ``reconcile`` capability flag.
- ``succeeded_webhook(payment)`` — a ready-made SUCCEEDED ``WebhookResult``
  for ``PaymentService.handle_webhook``.
"""

from __future__ import annotations

from django_cfg.apps.payments.providers.base import (
    EVENT_SUCCEEDED,
    STATUS_SUCCEEDED,
    CheckoutSession,
    ConfirmType,
    PaymentProvider,
    PaymentSnapshot,
    RefundResult,
    SubscriptionSession,
    WebhookResult,
)

__all__ = ["FakeProvider", "fake_provider_settings", "succeeded_webhook"]


class FakeProvider(PaymentProvider):
    """In-memory provider for service tests — no SDK, deterministic ids."""

    name = "fake"

    # Class-level knobs (reconciliation tests set these).
    snapshot_status: str = STATUS_SUCCEEDED
    can_reconcile: bool = True

    def create_checkout(self, *, payment, idempotency_key: str) -> CheckoutSession:
        return CheckoutSession(
            provider=self.name,
            external_id=f"ext_{payment.short_id}",
            client_secret=f"secret_{payment.short_id}",
            redirect_url=None,
            amount=payment.amount,
            currency=payment.currency,
        )

    def verify_and_parse_webhook(self, *, payload: bytes, signature: str) -> WebhookResult:
        raise NotImplementedError

    def refund(self, *, payment, amount=None) -> RefundResult:
        amt = amount if amount is not None else payment.amount
        return RefundResult(
            external_id=f"re_{payment.short_id}",
            amount=amt,
            currency=payment.currency,
        )

    def retrieve_payment(self, *, external_id: str) -> PaymentSnapshot:
        return PaymentSnapshot(
            external_id=external_id,
            status=type(self).snapshot_status,
            amount=None,
            currency="usd",
        )

    # ── subscriptions (later phase; kept because they're trivial and let the
    # contract stay exercised) ───────────────────────────────────────────────
    # Class-level knobs let tests drive the confirm branch without Stripe.
    sub_confirm_type: str = "payment"
    sub_status: str = "incomplete"

    def ensure_customer(self, *, external_ref: str, email: str = "", name: str = "") -> str:
        return f"cus_{external_ref}"

    def create_subscription(
        self, *, customer_id, price_id, idempotency_key, quantity=1,
        trial_days=None, metadata=None,
    ) -> SubscriptionSession:
        setup = type(self).sub_confirm_type == ConfirmType.SETUP.value
        return SubscriptionSession(
            provider=self.name,
            stripe_subscription_id=f"sub_{price_id}",
            status=type(self).sub_status,
            confirm_type=ConfirmType.SETUP.value if setup else ConfirmType.PAYMENT.value,
            client_secret=f"seti_secret_{price_id}" if setup else f"pi_secret_{price_id}",
        )

    # Recording knobs for cancel/portal tests (class-level so a fresh
    # get_provider() instance still sees what the previous call recorded).
    cancel_calls: list[tuple[str, bool]] = []
    portal_calls: list[tuple[str, str]] = []

    def cancel_subscription(self, *, stripe_subscription_id: str, at_period_end: bool = True) -> None:
        type(self).cancel_calls.append((stripe_subscription_id, at_period_end))

    def create_billing_portal_session(self, *, customer_id: str, return_url: str) -> str:
        type(self).portal_calls.append((customer_id, return_url))
        return f"https://billing.stripe.test/p/session/{customer_id}"

    def capabilities(self) -> dict[str, bool]:
        caps = super().capabilities()
        caps["reconcile"] = type(self).can_reconcile
        caps["subscriptions"] = True
        return caps

    @classmethod
    def reset(cls) -> None:
        """Reset the class-level knobs so cross-test state can't leak."""
        cls.snapshot_status = STATUS_SUCCEEDED
        cls.can_reconcile = True
        cls.sub_confirm_type = "payment"
        cls.sub_status = "incomplete"
        cls.cancel_calls = []
        cls.portal_calls = []


def fake_provider_settings() -> dict:
    """Django-settings overrides that make ``FakeProvider`` the default provider.

    Apply with pytest-django's ``settings`` fixture (or ``override_settings``);
    ``get_provider`` consults these settings before the pydantic config.
    """
    return {
        "PAYMENTS_DEFAULT_PROVIDER": "fake",
        "PAYMENTS_PROVIDER_REGISTRY": {
            "fake": "django_cfg.apps.payments.testing.FakeProvider",
        },
    }


def succeeded_webhook(payment) -> WebhookResult:
    """A SUCCEEDED webhook result for ``payment``, as the fake provider would emit."""
    return WebhookResult(
        event_id=f"evt_{payment.short_id}",
        event_type=EVENT_SUCCEEDED,
        external_id=payment.external_id,
        amount=payment.amount,
        currency=payment.currency,
        raw={"id": f"evt_{payment.short_id}", "type": "payment_intent.succeeded"},
    )
