"""
Management command: create_centrifugo_d1_schema

Applies the centrifugo_logs DDL to Cloudflare D1.
Idempotent — safe to run multiple times (uses CREATE TABLE IF NOT EXISTS).

Usage:
    python manage.py create_centrifugo_d1_schema
    python manage.py create_centrifugo_d1_schema --dry-run
"""

from __future__ import annotations

from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = "Create Centrifugo D1 table (centrifugo_logs) in Cloudflare D1"

    def add_arguments(self, parser) -> None:
        parser.add_argument(
            "--dry-run",
            action="store_true",
            default=False,
            help="Print DDL statements without executing them",
        )

    def handle(self, *args, **options) -> None:
        dry_run: bool = options["dry_run"]

        from django_cfg.modules.django_centrifugo.events.schema import CENTRIFUGO_SCHEMA_STATEMENTS

        if dry_run:
            self.stdout.write(self.style.WARNING("Dry-run mode — no changes applied\n"))
            for sql in CENTRIFUGO_SCHEMA_STATEMENTS:
                self.stdout.write(sql)
                self.stdout.write("\n")
            return

        from django_cfg.modules.django_cf import is_ready

        if not is_ready():
            raise CommandError(
                "django_centrifugo: django_cf is not configured. "
                "Add CloudflareConfig(enabled=True, ...) to DjangoConfig."
            )

        from django_cfg.modules.django_centrifugo.events.service import CentrifugoD1Service

        svc = CentrifugoD1Service()
        client = svc._get_client()

        self.stdout.write("Applying Centrifugo D1 schema...")
        for sql in CENTRIFUGO_SCHEMA_STATEMENTS:
            try:
                client.execute(sql)
                short = sql[:80].replace("\n", " ")
                self.stdout.write(self.style.SUCCESS(f"  OK  {short}"))
            except Exception as exc:
                raise CommandError(f"Schema migration failed: {exc}\nSQL: {sql}") from exc

        self.stdout.write(self.style.SUCCESS("\nCentrifugo D1 schema applied successfully."))
