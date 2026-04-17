from django.apps import apps
from django.db import connections
from django.db.migrations.loader import MigrationLoader

from .logger import MigrationLogger


class DbInspector:
    def __init__(self, log: MigrationLogger):
        self._log = log

    def column_exists(self, db_name: str, app_label: str, model_name: str, field_name: str) -> bool:
        try:
            app_config = apps.get_app_config(app_label)
            model = next(
                (m for m in app_config.get_models() if m.__name__.lower() == model_name.lower()),
                None,
            )
            if model is None:
                return False
            table = model._meta.db_table
            with connections[db_name].cursor() as cursor:
                cursor.execute(
                    "SELECT 1 FROM information_schema.columns "
                    "WHERE table_name = %s AND column_name = %s",
                    [table, field_name],
                )
                return cursor.fetchone() is not None
        except Exception:
            return False

    def check_connection(self, db_name: str) -> bool:
        try:
            with connections[db_name].cursor() as cursor:
                cursor.execute("SELECT 1")
            return True
        except Exception as e:
            self._log.error(f"  ❌ Connection to {db_name}: FAILED — {e}")
            return False

    def check_consistency(self, db_name: str) -> bool:
        try:
            loader = MigrationLoader(connections[db_name])
            try:
                loader.check_consistent_history(connections[db_name])
                return False
            except Exception as e:
                if "InconsistentMigrationHistory" in type(e).__name__:
                    self._log.warning(f"⚠️  Inconsistent migrations on {db_name}: {e}")
                    return True
                raise
        except Exception as e:
            self._log.warning(f"⚠️  Could not check consistency for {db_name}: {e}")
            return False

    def get_unapplied_migrations(self, db_name: str):
        loader = MigrationLoader(connections[db_name])
        applied = set(loader.applied_migrations or {})
        return [
            (app, name, migration)
            for (app, name), migration in (loader.disk_migrations or {}).items()
            if (app, name) not in applied
        ]
