"""Refund a payment from the CLI (admin/support operation)."""

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Refund a payment fully or partially by its short_id."

    def add_arguments(self, parser):
        parser.add_argument("short_id", type=str, help="Payment short_id (e.g. pay_abc123)")
        parser.add_argument(
            "--amount", type=int, default=None,
            help="Partial refund amount in MINOR units (cents). Omit for a full refund.",
        )
        parser.add_argument(
            "--yes", action="store_true",
            help="Skip the confirmation prompt.",
        )

    def handle(self, *args, **options):
        from django_cfg.apps.payments.models import Payment
        from django_cfg.apps.payments.services import RefundService
        from django_cfg.apps.payments.services.refund_service import RefundError

        payment = Payment.objects.filter(short_id=options["short_id"]).first()
        if payment is None:
            self.stderr.write(self.style.ERROR(f"No payment {options['short_id']}."))
            return

        amount = options["amount"]
        refundable = payment.amount - payment.amount_refunded
        scope = f"{amount} minor units" if amount is not None else f"FULL ({refundable} minor units)"
        self.stdout.write(
            f"Payment {payment.short_id}: {payment.provider} {payment.status}, "
            f"amount={payment.amount}, refunded={payment.amount_refunded}"
        )
        self.stdout.write(self.style.WARNING(f"About to refund: {scope}"))

        if not options["yes"]:
            answer = input("Proceed? [y/N] ").strip().lower()
            if answer != "y":
                self.stdout.write("Aborted.")
                return

        try:
            result = RefundService.refund(payment=payment, amount=amount)
        except RefundError as exc:
            self.stderr.write(self.style.ERROR(str(exc)))
            return

        payment.refresh_from_db()
        self.stdout.write(
            self.style.SUCCESS(
                f"Refunded {result.amount} ({result.external_id}); "
                f"payment now {payment.status}, refunded={payment.amount_refunded}."
            )
        )
