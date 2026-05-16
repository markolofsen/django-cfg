"""
Multi-database migration command.

Thin CLI wrapper around ``django_migrator.Migrator``. All actual logic
(drift detection, repair, guards) lives in the module — this file is
just argument parsing + report rendering + exit code.
"""

from __future__ import annotations

import sys

from django_cfg.management.utils import AdminCommand
from django_cfg.modules.django_migrator import (
    Migrator,
    MigratorLogger,
    MigratorOptions,
    TextReportFormatter,
)


class Command(AdminCommand):
    """Migrate every database declared via django-cfg's ``DatabaseConfig``.

    Lifecycle per database:
        1. Pre-flight guards (connection live, no concurrent migrate,
           no test-mirror leak in non-test env).
        2. Drift scan — both directions:
             - recorded in django_migrations but DDL missing
             - DDL present but no record in django_migrations
        3. Repair (only with --repair): fake-apply then fake-rewind to
           reconcile records with the live schema.
        4. Companion-field fake-apply (django_currency etc.).
        5. ``migrate --database=X`` — router decides what to apply.
        6. Verification — no pending migrations for owned apps remain.
    """

    command_name = "migrate_all"
    web_executable = False
    is_destructive = True

    help = (
        "State-validated migration of every database in DATABASES. "
        "Detects drift between django_migrations and live schema, then "
        "either reports it or auto-repairs with --repair."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--check",
            action="store_true",
            help="Forensic check only — no DDL, no record changes. Exit 1 if any drift.",
        )
        parser.add_argument(
            "--repair",
            action="store_true",
            help="Auto-repair detected drift via fake-apply / fake-rewind.",
        )
        parser.add_argument(
            "--skip-makemigrations",
            action="store_true",
            help="Skip the makemigrations step.",
        )
        parser.add_argument(
            "--non-interactive",
            action="store_true",
            help="Refuse all interactive prompts (CI mode).",
        )

    def handle(self, *args, **options):
        opts = MigratorOptions(
            repair=bool(options["repair"]),
            dry_run=bool(options["check"]),
            interactive=not bool(options["non_interactive"]),
            skip_makemigrations=bool(options["skip_makemigrations"]),
            verbosity=int(options.get("verbosity", 1)),
        )
        migrator = Migrator(
            options=opts,
            log=MigratorLogger(self.stdout, self.style, self.logger),
        )

        report = migrator.check() if opts.dry_run else migrator.migrate_all()

        self.stdout.write(TextReportFormatter().render(report))

        if not report.all_clean:
            sys.exit(1)
