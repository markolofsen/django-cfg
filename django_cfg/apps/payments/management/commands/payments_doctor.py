"""Diagnose the payments app — config, provider, and data health."""

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Check payments config (Stripe keys), provider, and stuck payments/events."

    def add_arguments(self, parser):
        parser.add_argument(
            "--stuck-hours", type=int, default=1,
            help="Flag payments PROCESSING longer than this many hours (default: 1)",
        )

    def handle(self, *args, **options):
        from django_cfg.apps.payments.services import HealthService

        report = HealthService.run(stuck_after_hours=options["stuck_hours"])

        self.stdout.write("")
        self.stdout.write(self.style.MIGRATE_HEADING("Payments doctor"))
        self.stdout.write("")
        for check in report.checks:
            mark = self.style.SUCCESS("ok ") if check.ok else self.style.ERROR("err")
            self.stdout.write(f"  [{mark}] {check.name:<24} {check.detail}")

        self.stdout.write("")
        if report.ok:
            self.stdout.write(self.style.SUCCESS("All checks passed."))
        else:
            failed = [c.name for c in report.checks if not c.ok]
            self.stdout.write(self.style.ERROR(f"Problems: {', '.join(failed)}"))
