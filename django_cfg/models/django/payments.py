"""
Payments configuration model.

Config for the built-in payments engine (`django_cfg.apps.payments`):
provider-agnostic one-time checkout (Stripe-first), webhook ingestion with
idempotency, refunds and reconciliation.

The Stripe SDK is an optional extra — `pip install django-cfg[payments]`.
"""

import os
from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class PaymentsConfig(BaseModel):
    """
    Payments app configuration.

    Example:
        ```python
        from django_cfg import DjangoConfig, PaymentsConfig

        class MyConfig(DjangoConfig):
            payments = PaymentsConfig(
                owner_model="organizations.Organization",
                fulfillment_hook="apps.orders.hooks.activate_order",
            )
        ```

    Secrets default from the environment (`STRIPE__SECRET_KEY`,
    `STRIPE__PUBLISHABLE_KEY`, `STRIPE__WEBHOOK_SECRET`) so hosts that already
    follow that convention need no explicit values here.
    """

    enabled: bool = Field(default=True, description="Enable payments app")

    default_provider: str = Field(
        default="stripe",
        description="Provider key used when none is specified",
    )

    provider_registry: Dict[str, str] = Field(
        default_factory=lambda: {
            "stripe": "django_cfg.apps.payments.providers.stripe.StripeProvider",
        },
        description="Provider key → dotted class path (hosts may add/override)",
    )

    default_currency: str = Field(
        default="usd",
        description="ISO currency code used when a checkout omits one",
    )

    # --- Ownership seam -----------------------------------------------------
    # Payments belong to an "owner" (the billable party). Defaults to
    # AUTH_USER_MODEL; hosts with org-level billing point it at their org
    # model ("app_label.Model"). Emitted as the CFG_PAYMENTS_OWNER_MODEL
    # setting so the Payment FK and migrations resolve it lazily.
    owner_model: Optional[str] = Field(
        default=None,
        description='Billable owner model as "app_label.Model" (default: AUTH_USER_MODEL)',
    )

    # Resolves the billable owner for API requests: fn(request) -> owner
    # instance. Defaults to `request.user` when owner_model is the user model;
    # REQUIRED when owner_model points elsewhere (e.g. an Organization).
    owner_resolver: Optional[str] = Field(
        default=None,
        description="Dotted path to fn(request) -> owner instance for API views",
    )

    # --- Fulfillment seam ---------------------------------------------------
    # Called after a payment SUCCEEDS (webhook- or reconciliation-driven):
    # fn(payment) -> None. The engine also emits payment_succeeded /
    # payment_failed signals regardless of this hook.
    fulfillment_hook: Optional[str] = Field(
        default=None,
        description="Dotted path to fn(payment) invoked on payment success",
    )

    # --- Dunning seam (subscriptions land in a later phase; hook is stable) --
    dunning_mailer: Optional[str] = Field(
        default=None,
        description="Dotted path to fn(subscription_data) for failed-renewal email; None = built-in no-op",
    )

    # --- Stripe credentials (env-fallback: STRIPE__*) ------------------------
    stripe_secret_key: str = Field(
        default_factory=lambda: os.environ.get("STRIPE__SECRET_KEY", ""),
        description="sk_test_… / sk_live_… (backend only)",
    )

    stripe_publishable_key: str = Field(
        default_factory=lambda: os.environ.get("STRIPE__PUBLISHABLE_KEY", ""),
        description="pk_test_… / pk_live_… (safe client-side)",
    )

    stripe_webhook_secret: str = Field(
        default_factory=lambda: os.environ.get("STRIPE__WEBHOOK_SECRET", ""),
        description="whsec_…; comma-separate to rotate (old+new verified)",
    )

    @property
    def stripe_webhook_secrets(self) -> List[str]:
        """Webhook secrets as a list (comma-separated value → rotation)."""
        return [s.strip() for s in self.stripe_webhook_secret.split(",") if s.strip()]


__all__ = ["PaymentsConfig"]
