"""Main entry point — ``Migrator`` orchestrates the per-DB lifecycle."""

from __future__ import annotations

from django.conf import settings
from django.core.management import call_command
from django.db import connections
from django.db.migrations.executor import MigrationExecutor

from ..introspection.apps import AppInspector
from ..introspection.drift import DriftDetector
from ..logger import MigratorLogger
from ..repair.engine import RepairEngine
from ..types import DbReport, MigrationReport, MigratorOptions
from .extensions import ensure_postgresql_extensions
from .guards import GuardSet


class Migrator:
    """State-validated multi-database migration orchestrator.

    Lifecycle per DB:

    1. Guards: connection live, test-mirror not leaking, no concurrent
       migrate.
    2. Drift scan: detect ``recorded_missing`` and ``unrecorded_present``
       in both directions.
    3. Repair (optional): fake-apply + fake-rewind to reconcile records
       with reality.
    4. Companion fake-apply: handle ``django_currency``-style auto-
       columns that don't need a real ALTER TABLE.
    5. Execute: plain ``migrate --database=X`` — Django + router decide
       what to apply.
    6. Verify: post-flight check that no migrations remain pending for
       apps owned by this DB.

    Step 3 only runs when ``options.repair=True``. Otherwise drift
    surfaces as an error and the orchestrator stops for that DB.
    """

    def __init__(
        self,
        *,
        options: MigratorOptions | None = None,
        log: MigratorLogger | None = None,
    ) -> None:
        self._options = options or MigratorOptions()
        self._log = log or MigratorLogger()
        self._apps = AppInspector()
        self._drift = DriftDetector(self._apps)
        self._repair = RepairEngine(self._log)
        self._guards = GuardSet(self._log)

    # --- Public ---

    def migrate_all(self) -> MigrationReport:
        """Process every database alias declared in ``settings.DATABASES``."""
        report = MigrationReport()

        if not self._options.skip_makemigrations and not self._options.dry_run:
            self.create_migrations()

        # default first so cross-DB FK targets exist before routed apps
        # try to reference them. Within a non-default group, order is
        # alphabetical for determinism.
        aliases = self._ordered_aliases()
        for alias in aliases:
            report.add(self._migrate_one(alias))
        return report

    def check(self) -> MigrationReport:
        """Forensic-only run — no DDL, no record changes."""
        report = MigrationReport()
        for alias in self._ordered_aliases():
            report.add(self._check_one(alias))
        return report

    def create_migrations(self) -> None:
        """Run ``makemigrations`` once for the whole project."""
        self._log.info("📝 Creating migrations…")
        try:
            call_command(
                "makemigrations",
                verbosity=self._options.verbosity,
                interactive=self._options.interactive,
            )
        except Exception as exc:
            self._log.warning(f"makemigrations: {exc}")
            return

        # Pick up apps that have models but no migrations dir yet —
        # makemigrations alone doesn't always catch these in older Djangos.
        for app in self._apps.all_installed_apps():
            if self._apps.app_has_models(app) and not self._apps.app_has_migrations(app):
                try:
                    self._log.info(f"  📝 makemigrations {app}")
                    call_command("makemigrations", app, verbosity=self._options.verbosity)
                except Exception as exc:
                    self._log.warning(f"  ⚠️  makemigrations {app}: {exc}")

    # --- Per-DB lifecycle ---

    def _migrate_one(self, alias: str) -> DbReport:
        db_report = DbReport(alias=alias)

        with self._log.section(f"Database: {alias}"):
            if self._run_guards(alias, db_report) is False:
                return db_report

            # Drift scan
            drift = self._drift.scan(alias)
            db_report.drift = drift

            if drift.has_issues():
                if self._options.repair and not self._options.dry_run:
                    self._log.notice(
                        f"Drift detected — running auto-repair "
                        f"({drift.total_drift_count()} incidents)"
                    )
                    try:
                        self._repair.apply(alias, drift, db_report)
                    except Exception as exc:
                        db_report.add_error(f"repair failed: {exc}")
                        return db_report
                else:
                    db_report.add_error(
                        f"Drift detected on {alias}. "
                        f"Re-run with --repair to fix automatically, or "
                        f"see the report for manual intervention."
                    )
                    # In dry-run we just report. In normal mode we leave
                    # the report's errors as the signal — the command
                    # layer maps non-clean reports to exit 1.
                    return db_report

            if self._options.dry_run:
                self._verify_in_sync(alias, db_report, post_migrate=False)
                return db_report

            # Companion-field auto-fake (currency, etc.)
            self._repair.apply_companion_fake(alias, db_report)

            # Plain migrate via Django's executor
            self._execute_migrate(alias, db_report)

            # Verify
            self._verify_in_sync(alias, db_report, post_migrate=True)

        return db_report

    def _check_one(self, alias: str) -> DbReport:
        db_report = DbReport(alias=alias)
        with self._log.section(f"Check: {alias}"):
            if self._run_guards(alias, db_report) is False:
                return db_report
            db_report.drift = self._drift.scan(alias)
            self._verify_in_sync(alias, db_report, post_migrate=False)
        return db_report

    # --- Steps ---

    def _run_guards(self, alias: str, db_report: DbReport) -> bool:
        """Run all guards. Returns False if a fatal one tripped."""
        results = self._guards.run(alias)
        db_report.guard_results = results
        for r in results:
            if r.passed:
                continue
            if r.fatal:
                db_report.aborted = True
                db_report.add_error(f"[{r.name}] {r.message}")
                return False
            db_report.add_warning(f"[{r.name}] {r.message}")
        return True

    def _execute_migrate(self, alias: str, db_report: DbReport) -> None:
        """Plain migrate — router's ``allow_migrate`` is the decision point."""
        try:
            ensure_postgresql_extensions(alias, self._log)
        except Exception as exc:
            self._log.warning(f"PG extensions on {alias}: {exc}")

        try:
            call_command(
                "migrate",
                database=alias,
                interactive=self._options.interactive,
                verbosity=self._options.verbosity,
            )
            db_report.migration_executed = True
        except Exception as exc:
            db_report.add_error(f"migrate on {alias}: {exc}")
            raise

    def _verify_in_sync(
        self,
        alias: str,
        db_report: DbReport,
        *,
        post_migrate: bool,
    ) -> None:
        """Post-flight: are there still pending migrations for owned apps?"""
        executor = MigrationExecutor(connections[alias])
        leaves = executor.loader.graph.leaf_nodes()
        plan = executor.migration_plan(leaves)
        owned = set(self._apps.apps_for_database(alias))
        pending = [(m, b) for m, b in plan if m.app_label in owned]

        db_report.pending_after_migrate = len(pending)
        if pending and post_migrate:
            preview = ", ".join(
                f"{m.app_label}.{m.name}" for m, _ in pending[:5]
            )
            db_report.add_error(
                f"{alias}: {len(pending)} pending migration(s) for owned "
                f"apps after migrate (first: {preview}). Router or "
                f"DATABASE_ROUTING_RULES misconfigured."
            )

    # --- Helpers ---

    def _ordered_aliases(self) -> list[str]:
        names = list(settings.DATABASES.keys())
        if "default" in names:
            names.remove("default")
            return ["default"] + sorted(names)
        return sorted(names)
