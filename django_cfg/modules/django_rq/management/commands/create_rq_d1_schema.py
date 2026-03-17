"""
Management command: create_rq_d1_schema

Applies the rq_job_events and rq_worker_heartbeats DDL to Cloudflare D1.
Idempotent — safe to run multiple times (uses CREATE TABLE IF NOT EXISTS).

Usage:
    python manage.py create_rq_d1_schema
    python manage.py create_rq_d1_schema --dry-run
"""

from __future__ import annotations

from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = "Create RQ D1 tables (rq_job_events, rq_worker_heartbeats) in Cloudflare D1"

    def add_arguments(self, parser) -> None:
        parser.add_argument(
            "--dry-run",
            action="store_true",
            default=False,
            help="Print DDL statements without executing them",
        )

    def handle(self, *args, **options) -> None:
        dry_run: bool = options["dry_run"]

        from django_cfg.modules.django_rq.events.schema import RQ_SCHEMA_STATEMENTS

        if dry_run:
            self.stdout.write(self.style.WARNING("Dry-run mode — no changes applied\n"))
            for sql in RQ_SCHEMA_STATEMENTS:
                self.stdout.write(sql)
                self.stdout.write("\n")
            return

        from django_cfg.modules.django_rq import get_service, is_enabled

        if not is_enabled():
            raise CommandError(
                "django_rq: django_cf is not configured. "
                "Add CloudflareConfig(enabled=True, ...) to DjangoConfig."
            )

        svc = get_service()
        client = svc._get_client()

        self.stdout.write("Applying RQ D1 schema...")
        for sql in RQ_SCHEMA_STATEMENTS:
            try:
                client.execute(sql)
                short = sql[:80].replace("\n", " ")
                self.stdout.write(self.style.SUCCESS(f"  OK  {short}"))
            except Exception as exc:
                raise CommandError(f"Schema migration failed: {exc}\nSQL: {sql}") from exc

        self.stdout.write(self.style.SUCCESS("\nRQ D1 schema applied successfully."))
