from django.conf import settings
from django.core.management import call_command
from django.db import connections
from django.db.migrations.recorder import MigrationRecorder

from ..postgresql import ensure_postgresql_extensions
from .app_inspector import AppInspector
from .db_inspector import DbInspector
from .fake_handler import FakeMigrationHandler
from .logger import MigrationLogger


class MigrationManager:
    """
    Centralized migration management for Django commands.

    Usage:
        manager = MigrationManager(stdout, style, logger)
        manager.migrate_database("default")
    """

    def __init__(self, stdout=None, style=None, logger=None):
        self._log = MigrationLogger(stdout, style, logger)
        self._apps = AppInspector()
        self._db = DbInspector(self._log)
        self._faker = FakeMigrationHandler(self._db, self._log)

        # Keep legacy attributes so callers that read .stdout / .style still work
        self.stdout = stdout
        self.style = style
        self.logger = logger

    # ── Public API ────────────────────────────────────────────────────────────

    def create_migrations(self):
        self._log.info("📝 Creating migrations...")
        try:
            call_command("makemigrations", verbosity=1)
            for app in self._apps.get_all_installed_apps():
                if self._apps.app_has_models(app) and not self._apps.app_has_migrations(app):
                    try:
                        self._log.info(f"  📝 Creating migrations for {app}...")
                        call_command("makemigrations", app, verbosity=1)
                    except Exception as e:
                        self._log.warning(f"  ⚠️  Could not create migrations for {app}: {e}")
            self._log.success("✅ Migrations created")
        except Exception as e:
            self._log.warning(f"⚠️  Warning creating migrations: {e}")

    def migrate_database(self, db_name: str):
        try:
            self._log.info(f"🔄 Migrating {db_name}...")
            ensure_postgresql_extensions(db_name, self.stdout, self.style, self.logger)

            apps_list = self._apps.get_apps_for_database(db_name)
            if not apps_list:
                return

            self.create_migrations()

            unapplied = self._db.get_unapplied_migrations(db_name)
            self._faker.fake_if_needed(db_name, unapplied)

            for app in apps_list:
                if not self._apps.app_has_migrations(app):
                    continue
                try:
                    self._log.info(f"  📦 Migrating {app}...")
                    call_command("migrate", app, database=db_name, verbosity=1)
                except Exception as e:
                    self._log.raise_error(f"Migration failed for {app} on {db_name}: {e}")

            self._log.success(f"✅ {db_name} migration completed!")
        except Exception as e:
            self._log.raise_error(f"Error migrating {db_name}: {e}")

    def migrate_all_databases(self):
        self._log.success("🔄 Starting full migration...")
        self.migrate_database("default")
        for db_name in self._apps.get_all_database_names():
            if db_name != "default":
                self._log.info(f"🔄 Migrating {db_name}...")
                self.migrate_database(db_name)
        self._log.success("✅ Full migration completed!")

    def migrate_constance_if_needed(self):
        try:
            if "constance" not in settings.INSTALLED_APPS:
                self._log.warning("⚠️  Constance not found in INSTALLED_APPS")
                return
            self._log.success("🔧 Migrating constance (django-cfg requirement)...")
            call_command("migrate", "constance", database="default", verbosity=1)
            self._log.success("✅ Constance migration completed!")
        except Exception as e:
            self._log.raise_error(f"Could not migrate constance: {e}")

    def check_database_connection(self, db_name: str) -> bool:
        return self._db.check_connection(db_name)

    def get_apps_for_database(self, db_name: str):
        return self._apps.get_apps_for_database(db_name)

    def get_all_installed_apps(self):
        return self._apps.get_all_installed_apps()

    def get_all_database_names(self):
        return self._apps.get_all_database_names()

    def get_database_info(self) -> dict:
        try:
            return {
                db_name: {
                    "name": cfg.get("NAME", "unknown"),
                    "engine": cfg.get("ENGINE", "unknown"),
                    "host": cfg.get("HOST", ""),
                    "port": cfg.get("PORT", ""),
                    "apps": [],
                }
                for db_name, cfg in settings.DATABASES.items()
            }
        except Exception as e:
            self._log.warning(f"⚠️  Error getting database info: {e}")
            return {}

    def app_has_migrations(self, app_label: str) -> bool:
        return self._apps.app_has_migrations(app_label)

    def app_has_models(self, app_label: str) -> bool:
        return self._apps.app_has_models(app_label)

    def check_migration_consistency(self, db_name: str) -> bool:
        return self._db.check_consistency(db_name)

    def fix_inconsistent_migrations(self, db_name: str):
        self._log.info(f"🔧 Fixing inconsistent migrations for {db_name}...")
        try:
            recorder = MigrationRecorder(connections[db_name])
            applied = list(recorder.migration_qs.all().values_list("app", "name", "id"))
            if not applied:
                self._log.info("  No migrations to fix")
                return
            admin_ids = [m[2] for m in applied if m[0] == "admin"]
            auth_ids = [m[2] for m in applied if m[0] == "django_cfg_accounts"]
            if admin_ids and auth_ids and min(admin_ids) < min(auth_ids):
                self._log.warning("  ⚠️  Detected: admin migrations before django_cfg_accounts")
                recorder.migration_qs.filter(app="admin").delete()
                self._log.success("  ✅ Removed problematic admin migrations")
        except Exception as e:
            self._log.error(f"  ❌ Could not fix migrations: {e}")
            raise

    def migrate_test_database(self, db_name: str, auto_fix: bool = True):
        self._log.info(f"🧪 Migrating test database {db_name}...")
        try:
            ensure_postgresql_extensions(db_name, self.stdout, self.style, self.logger)
            if self._db.check_consistency(db_name) and auto_fix:
                self._log.warning("⚠️  Inconsistent migrations detected, auto-fixing...")
                self.fix_inconsistent_migrations(db_name)
            self._migrate_with_bypass(db_name)
            self._log.success(f"✅ Test database {db_name} migrated successfully!")
        except Exception as e:
            if auto_fix:
                self._log.warning(f"⚠️  Migration failed, attempting auto-fix: {e}")
                try:
                    self.fix_inconsistent_migrations(db_name)
                    self._migrate_with_bypass(db_name)
                    self._log.success("✅ Auto-fix successful!")
                except Exception as fix_error:
                    self._log.raise_error(f"Auto-fix failed: {fix_error}")
            else:
                self._log.raise_error(f"Migration failed: {e}")

    # ── Private ───────────────────────────────────────────────────────────────

    def _migrate_with_bypass(self, db_name: str):
        from django.db.migrations import loader as migrations_loader

        original = migrations_loader.MigrationLoader.check_consistent_history

        def patched(self, connection):
            try:
                return original(self, connection)
            except Exception as e:
                if "InconsistentMigrationHistory" in type(e).__name__:
                    return
                raise

        migrations_loader.MigrationLoader.check_consistent_history = patched
        try:
            call_command("migrate", database=db_name, verbosity=1)
        finally:
            migrations_loader.MigrationLoader.check_consistent_history = original

    # ── Legacy log helpers (some commands call these directly) ────────────────

    def _log_info(self, message: str): self._log.info(message)
    def _log_success(self, message: str): self._log.success(message)
    def _log_warning(self, message: str): self._log.warning(message)
    def _log_error(self, message: str): self._log.error(message)
    def _raise_error(self, message: str): self._log.raise_error(message)
