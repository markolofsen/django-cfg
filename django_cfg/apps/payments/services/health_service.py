"""HealthService — config + provider + data health for the payments app.

Backs the ``payments_doctor`` command (and could feed a /health endpoint).
Read-only: it never mutates payments, only reports.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import timedelta

from django.conf import settings
from django.utils import timezone


@dataclass
class HealthCheck:
    name: str
    ok: bool
    detail: str


@dataclass
class HealthReport:
    checks: list[HealthCheck] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return all(c.ok for c in self.checks)

    def add(self, name: str, ok: bool, detail: str) -> None:
        self.checks.append(HealthCheck(name=name, ok=ok, detail=detail))


class HealthService:
    @staticmethod
    def run(*, stuck_after_hours: int = 1) -> HealthReport:
        from django_cfg.apps.payments.config import get_payments_config
        from django_cfg.apps.payments.models import Payment, PaymentEvent
        from django_cfg.apps.payments.providers import (
            ProviderNotSupported,
            get_provider,
        )

        cfg = get_payments_config()
        report = HealthReport()

        # 1. Default provider resolves (settings override wins, like get_provider).
        provider_name = (
            getattr(settings, "PAYMENTS_DEFAULT_PROVIDER", None) or cfg.default_provider
        )
        try:
            provider = get_provider(provider_name)
            report.add("provider", True, f"resolved '{provider.name}'")
        except Exception as exc:  # noqa: BLE001
            report.add("provider", False, f"cannot resolve '{provider_name}': {exc}")
            provider = None

        # 2. Stripe secrets present (only meaningful when stripe is default).
        if provider_name == "stripe":
            report.add(
                "stripe_secret_key",
                bool(cfg.stripe_secret_key),
                "set" if cfg.stripe_secret_key else "MISSING (STRIPE__SECRET_KEY)",
            )
            report.add(
                "stripe_webhook_secret",
                bool(cfg.stripe_webhook_secrets),
                f"{len(cfg.stripe_webhook_secrets)} configured"
                if cfg.stripe_webhook_secrets
                else "MISSING (STRIPE__WEBHOOK_SECRET)",
            )
            report.add(
                "stripe_publishable_key",
                bool(cfg.stripe_publishable_key),
                "set" if cfg.stripe_publishable_key else "missing (frontend can't init)",
            )

        # 3. Reconcile capability.
        if provider is not None:
            try:
                can_reconcile = provider.capabilities().get("reconcile", False)
            except ProviderNotSupported:
                can_reconcile = False
            report.add(
                "reconcile_capable",
                True,  # informational, not a failure
                "yes" if can_reconcile else "no (missed webhooks need manual sync)",
            )

        # 4. Stuck payments (processing too long).
        cutoff = timezone.now() - timedelta(hours=stuck_after_hours)
        stuck = Payment.objects.filter(
            status=Payment.Status.PROCESSING, updated_at__lt=cutoff,
        ).count()
        report.add(
            "stuck_payments",
            stuck == 0,
            "none" if stuck == 0 else f"{stuck} payment(s) PROCESSING > {stuck_after_hours}h",
        )

        # 5. Unprocessed webhook events (received but never handled).
        unprocessed = PaymentEvent.objects.filter(processed_at__isnull=True).count()
        report.add(
            "unprocessed_events",
            unprocessed == 0,
            "none" if unprocessed == 0 else f"{unprocessed} event(s) never processed",
        )

        return report
