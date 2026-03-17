"""
Django management command: create_grpc_d1_schema

Runs all gRPC D1 DDL statements idempotently (CREATE TABLE IF NOT EXISTS).
Safe to run multiple times — never drops or modifies existing tables.

Usage:
    uv run manage.py create_grpc_d1_schema
    uv run manage.py create_grpc_d1_schema --dry-run
"""

from __future__ import annotations

import logging

from django.core.management.base import BaseCommand, CommandError

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Create all gRPC D1 tables idempotently (CREATE TABLE IF NOT EXISTS)"

    def add_arguments(self, parser) -> None:
        parser.add_argument(
            "--dry-run",
            action="store_true",
            default=False,
            help="Print DDL statements without executing them.",
        )

    def handle(self, *args, **options) -> None:
        from django_cfg.modules.django_grpc.events.schema import GRPC_SCHEMA_STATEMENTS
        from django_cfg.modules.django_grpc.events.service import GrpcD1Service

        dry_run: bool = options["dry_run"]
        total = len(GRPC_SCHEMA_STATEMENTS)

        if dry_run:
            self.stdout.write(self.style.WARNING(f"[dry-run] {total} statements:"))
            for i, stmt in enumerate(GRPC_SCHEMA_STATEMENTS, 1):
                self.stdout.write(f"\n-- [{i}/{total}]\n{stmt}")
            return

        self.stdout.write(f"Running {total} DDL statement(s) against gRPC D1 database…")

        try:
            service = GrpcD1Service()
            client = service._get_client()
        except Exception as exc:
            raise CommandError(f"Failed to connect to D1: {exc}") from exc

        ok = 0
        errors = 0
        for i, stmt in enumerate(GRPC_SCHEMA_STATEMENTS, 1):
            try:
                client.execute(stmt)
                ok += 1
                self.stdout.write(f"  [{i}/{total}] OK")
            except Exception as exc:
                errors += 1
                self.stderr.write(f"  [{i}/{total}] ERROR: {exc}")
                logger.error("D1 DDL failed [%d/%d]: %s\n%s", i, total, exc, stmt)

        if errors:
            raise CommandError(
                f"Schema creation finished with {errors} error(s). "
                f"{ok}/{total} statements succeeded."
            )

        self.stdout.write(
            self.style.SUCCESS(f"gRPC D1 schema ready — {ok} statement(s) executed.")
        )
