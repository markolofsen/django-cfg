"""
Interactive migration command.

Wraps ``django_migrator.Migrator`` with a questionary-based menu for
day-to-day developer flow. CI/automation should prefer ``migrate_all``
directly.
"""

from __future__ import annotations

import sys

import questionary
from django.conf import settings
from django.core.management import call_command
from django.db import connections

from django_cfg.management.utils import DestructiveCommand
from django_cfg.modules.django_migrator import (
    AppInspector,
    Migrator,
    MigratorLogger,
    MigratorOptions,
    TextReportFormatter,
)


class Command(DestructiveCommand):
    command_name = "migrator"
    help = "Interactive migration tool — multi-DB aware."

    def add_arguments(self, parser):
        parser.add_argument("--auto", action="store_true", help="Run full migration non-interactively")
        parser.add_argument("--database", type=str, help="Migrate one database alias only")
        parser.add_argument("--app", type=str, help="Migrate one app across every DB that owns it")
        parser.add_argument("--repair", action="store_true", help="Allow auto-repair of drift")

    def handle(self, *args, **options):
        self._log = MigratorLogger(self.stdout, self.style, self.logger)
        self._apps = AppInspector()

        if options["auto"]:
            self._run_full(repair=bool(options["repair"]))
            return
        if options["database"]:
            self._run_full(repair=bool(options["repair"]), only_alias=options["database"])
            return
        if options["app"]:
            self._migrate_app(options["app"])
            return
        self._interactive_menu()

    # ---- High-level flows ----

    def _run_full(self, *, repair: bool, only_alias: str | None = None) -> None:
        opts = MigratorOptions(repair=repair, interactive=False)
        migrator = Migrator(options=opts, log=self._log)
        report = migrator.migrate_all() if only_alias is None else self._run_single(
            migrator, only_alias
        )
        self.stdout.write(TextReportFormatter().render(report))
        if not report.all_clean:
            sys.exit(1)

    def _run_single(self, migrator: Migrator, alias: str):
        # Single-DB run via the same lifecycle — just don't iterate.
        from django_cfg.modules.django_migrator import MigrationReport
        report = MigrationReport()
        report.add(migrator._migrate_one(alias))  # type: ignore[attr-defined]
        return report

    def _migrate_app(self, app_name: str) -> None:
        """Migrate one app on every DB that owns it.

        Sanity-checks routing rules first so we don't push DDL to the
        wrong connection by accident.
        """
        targets = [
            db for db in self._apps.all_database_names()
            if app_name in self._apps.apps_for_database(db)
        ]
        if not targets:
            self.stdout.write(self.style.ERROR(
                f"App '{app_name}' has no routing rule — refusing to guess a DB."
            ))
            sys.exit(1)

        for alias in targets:
            self.stdout.write(f"📊 Migrating {app_name} on {alias}…")
            try:
                call_command("migrate", app_name, database=alias, verbosity=1)
            except Exception as exc:
                self.stdout.write(self.style.ERROR(
                    f"❌ {app_name} on {alias}: {exc}"
                ))
                sys.exit(1)

    # ---- Interactive menu ----

    def _interactive_menu(self) -> None:
        self.stdout.write(self.style.SUCCESS("\n🚀 django-cfg Migration Tool\n"))
        databases = self._apps.all_database_names()

        choices: list[questionary.Choice] = [
            questionary.Choice("🔄 Run Full Migration (all DBs)", value="full"),
            questionary.Choice("🩹 Run Full Migration with --repair", value="full_repair"),
            questionary.Choice("🔍 Check (forensic only, no DDL)", value="check"),
            questionary.Choice("📝 Create Migrations Only", value="makemigrations"),
            questionary.Choice("📊 Show DB Status", value="status"),
            questionary.Choice("❌ Exit", value="exit"),
        ]
        for db in databases:
            choices.insert(
                -1,
                questionary.Choice(f"📦 Migrate {db} Only", value=f"db:{db}"),
            )

        choice = questionary.select("Select an action:", choices=choices).ask()
        if choice == "exit" or choice is None:
            self.stdout.write("Goodbye 👋")
            return

        if choice == "full":
            self._run_full(repair=False)
        elif choice == "full_repair":
            self._run_full(repair=True)
        elif choice == "check":
            self._run_check()
        elif choice == "makemigrations":
            Migrator(log=self._log).create_migrations()
        elif choice == "status":
            self._show_status()
        elif choice.startswith("db:"):
            self._run_full(repair=False, only_alias=choice.split(":", 1)[1])

    def _run_check(self) -> None:
        opts = MigratorOptions(dry_run=True, interactive=False)
        report = Migrator(options=opts, log=self._log).check()
        self.stdout.write(TextReportFormatter().render(report))
        if not report.all_clean:
            sys.exit(1)

    # ---- Status ----

    def _show_status(self) -> None:
        self.stdout.write(self.style.SUCCESS("\n📊 Database Status\n"))
        for alias in self._apps.all_database_names():
            cfg = settings.DATABASES.get(alias, {})
            self.stdout.write(f"\n🗄️  {alias}")
            self.stdout.write(f"   engine: {cfg.get('ENGINE', '?')}")
            self.stdout.write(f"   name:   {cfg.get('NAME', '?')}")

            try:
                with connections[alias].cursor() as cur:
                    cur.execute("SELECT 1")
                self.stdout.write("   conn:   ✅")
            except Exception as exc:
                self.stdout.write(self.style.ERROR(f"   conn:   ❌ {exc}"))

            apps_here = self._apps.apps_for_database(alias)
            self.stdout.write(
                f"   apps:   {', '.join(apps_here) if apps_here else '<none>'}"
            )

        rules = getattr(settings, "DATABASE_ROUTING_RULES", {})
        if rules:
            self.stdout.write("\n🔀 Routing rules:")
            for app, db in sorted(rules.items()):
                self.stdout.write(f"   {app} → {db}")
