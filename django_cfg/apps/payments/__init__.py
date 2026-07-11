"""django_cfg.apps.payments — provider-agnostic one-time checkout engine.

Stripe-first payments with webhook-driven fulfillment:

- ``models`` — provider-neutral ``Payment`` + ``PaymentEvent`` (webhook log).
- ``providers`` — the ``PaymentProvider`` contract and the Stripe implementation
  (the ONLY place the ``stripe`` SDK is imported).
- ``services`` — checkout orchestration, webhook fulfillment, refunds,
  reconciliation, health.
- ``api`` — DRF views mounted at ``cfg/payments/`` (webhook, checkout, list).

Enable it on the host config:

    from django_cfg import DjangoConfig, PaymentsConfig

    class MyConfig(DjangoConfig):
        payments = PaymentsConfig(
            owner_model="organizations.Organization",   # default: AUTH_USER_MODEL
            fulfillment_hook="apps.orders.hooks.activate_order",
        )

Subscriptions are a later phase — the provider contract already carries the
subscription DTOs/events, but the service layer only fulfills one-time payments.
"""
