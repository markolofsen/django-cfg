"""Reconcile payments against the provider — catch up missed/late webhooks."""

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = (
        "Poll the provider for payments stuck in PROCESSING and apply the real "
        "status (succeeded → fulfillment seam, failed → failed signal)."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--hours", type=int, default=1,
            help="Only reconcile payments PROCESSING longer than this (default: 1)",
        )
        parser.add_argument(
            "--limit", type=int, default=100,
            help="Max payments to reconcile in one run (default: 100)",
        )
        parser.add_argument(
            "--short-id", type=str, default=None,
            help="Reconcile a single payment by its short_id (ignores --hours).",
        )

    def handle(self, *args, **options):
        from django_cfg.apps.payments.models import Payment
        from django_cfg.apps.payments.services import ReconciliationService

        short_id = options["short_id"]
        if short_id:
            payment = Payment.objects.filter(short_id=short_id).first()
            if payment is None:
                self.stderr.write(self.style.ERROR(f"No payment {short_id}."))
                return
            result = ReconciliationService.reconcile_payment(payment)
        else:
            result = ReconciliationService.reconcile_stuck(
                older_than_hours=options["hours"], limit=options["limit"],
            )

        self.stdout.write("")
        self.stdout.write(f"  Checked:   {result.checked}")
        self.stdout.write(f"  Updated:   {result.updated}")
        self.stdout.write(f"  Activated: {result.activated}")
        self.stdout.write(f"  Skipped:   {result.skipped}")
        if result.errors:
            self.stdout.write(self.style.ERROR(f"  Errors ({len(result.errors)}):"))
            for err in result.errors[:20]:
                self.stdout.write(f"    - {err}")

        self.stdout.write("")
        self.stdout.write(self.style.SUCCESS("Reconcile complete."))
