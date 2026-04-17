from pathlib import Path
from typing import List, Set

from django.apps import apps
from django.conf import settings
from django.db import connections
from django.db.migrations.recorder import MigrationRecorder

DEFAULT_APPS: Set[str] = {
    "admin", "auth", "contenttypes", "sessions", "messages",
    "staticfiles", "sites", "postgres", "mysql", "sqlite3", "oracle",
}


class AppInspector:
    def get_all_installed_apps(self) -> List[str]:
        result = []
        for app_config in apps.get_app_configs():
            label = app_config.label
            path = Path(app_config.path)
            if (path / "apps.py").exists():
                if label not in DEFAULT_APPS:
                    result.append(label)
            elif (path / "models.py").exists() or (path / "admin.py").exists():
                result.append(label)
        return result

    def get_apps_in_other_databases(self) -> Set[str]:
        routing_rules = getattr(settings, "DATABASE_ROUTING_RULES", {})
        return set(routing_rules.keys())

    def get_apps_for_database(self, db_name: str) -> List[str]:
        if db_name == "default":
            all_apps = self.get_all_installed_apps()
            other = self.get_apps_in_other_databases()
            return [a for a in all_apps if a not in other]
        routing_rules = getattr(settings, "DATABASE_ROUTING_RULES", {})
        return [app for app, db in routing_rules.items() if db == db_name]

    def get_all_database_names(self) -> List[str]:
        return list(settings.DATABASES.keys())

    def app_has_migrations(self, app_label: str) -> bool:
        try:
            app_config = apps.get_app_config(app_label)
            migrations_dir = Path(app_config.path) / "migrations"
            if not migrations_dir.exists():
                return False
            files = [f for f in migrations_dir.glob("*.py") if f.name != "__init__.py"]
            if files:
                return True
            for db_name in settings.DATABASES:
                try:
                    recorder = MigrationRecorder(connections[db_name])
                    if recorder.migration_qs.filter(app=app_label).exists():
                        return True
                except Exception:
                    continue
            return False
        except Exception:
            return False

    def app_has_models(self, app_label: str) -> bool:
        try:
            app_config = apps.get_app_config(app_label)
            if list(app_config.get_models()):
                return True
            path = Path(app_config.path)
            models_dir = path / "models"
            extra = list(models_dir.glob("*.py")) if models_dir.is_dir() else []
            for candidate in [path / "models.py", *extra]:
                if candidate.name == "__init__.py":
                    continue
                content = candidate.read_text()
                if "class " in content and ("models.Model" in content or "(Model)" in content):
                    return True
            return False
        except Exception:
            return False
