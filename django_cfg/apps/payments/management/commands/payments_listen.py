"""Forward Stripe webhooks to the local server (wraps `stripe listen`).

Fetches the CLI signing secret via `stripe listen --print-secret`, prints it
with instructions (set STRIPE__WEBHOOK_SECRET yourself — django-cfg doesn't
write host env files), then streams `stripe listen --forward-to …` in the
foreground. Local-dev only — never used in production.
"""

from __future__ import annotations

import subprocess

from django.core.management.base import BaseCommand
from django.urls import reverse

SECRET_KEY_NAME = "STRIPE__WEBHOOK_SECRET"


def _forwarded_events() -> list[str]:
    """The Stripe event types the engine handles — the keys of the provider's
    event map, so the dev forwarder can never drift from the handler."""
    from django_cfg.apps.payments.providers.stripe import _EVENT_MAP

    return sorted(_EVENT_MAP.keys())


class Command(BaseCommand):
    help = (
        "Forward Stripe webhooks to the local server via the Stripe CLI. "
        "Prints the CLI signing secret to set as STRIPE__WEBHOOK_SECRET."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--host", default="localhost:8000",
            help="host:port the webhook is forwarded to (default: localhost:8000)",
        )
        parser.add_argument(
            "--events", default=None,
            help="Comma-separated event filter (default: the events the engine handles).",
        )

    def handle(self, *args, **options):
        # Resolve the webhook path from urls so it can't drift.
        try:
            path = reverse("cfg_payments:webhook-stripe")
        except Exception:
            path = "/cfg/payments/webhook/stripe/"
        forward_url = f"http://{options['host']}{path}"

        if not _stripe_cli_available():
            self.stderr.write(self.style.ERROR(
                "stripe CLI not found. Install: brew install stripe/stripe-cli/stripe"
            ))
            return

        # 1. Fetch the CLI signing secret (also surfaces 'not logged in' early).
        self.stdout.write("Fetching webhook signing secret…")
        secret = _print_secret()
        if not secret:
            self.stderr.write(self.style.ERROR(
                "Could not get a signing secret. Run `stripe login` first."
            ))
            return

        # 2. Hand it to the operator — the running server must verify forwarded
        #    events with it. (The cmdop source wrote this into a dev .env;
        #    django-cfg has no such file to own, so setting it is on the host.)
        self.stdout.write(self.style.SUCCESS(f"{SECRET_KEY_NAME}={secret}"))
        self.stdout.write(
            "Set this in your environment (or PaymentsConfig.stripe_webhook_secret) "
            "and restart the Django server so forwarded events verify."
        )

        # 3. Stream the forwarder in the foreground.
        cmd = ["stripe", "listen", "--forward-to", forward_url]
        events = options["events"] or ",".join(_forwarded_events())
        cmd += ["--events", events]

        self.stdout.write("")
        self.stdout.write(self.style.MIGRATE_HEADING(f"Forwarding → {forward_url}"))
        self.stdout.write(f"Events: {events}")
        self.stdout.write("Press Ctrl+C to stop.\n")
        try:
            subprocess.run(cmd, check=False)
        except KeyboardInterrupt:
            self.stdout.write("\nStopped.")


def _stripe_cli_available() -> bool:
    import shutil

    return shutil.which("stripe") is not None


def _print_secret() -> str | None:
    try:
        out = subprocess.run(
            ["stripe", "listen", "--print-secret"],
            capture_output=True, text=True, timeout=20,
        )
    except Exception:
        return None
    secret = (out.stdout or "").strip()
    return secret if secret.startswith("whsec_") else None
