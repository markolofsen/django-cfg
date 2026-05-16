"""Introspect which apps belong to which database.

Single source of truth: ``settings.DATABASE_ROUTING_RULES`` (built by
django_cfg from each ``DatabaseConfig.apps`` field). Everything else
in this module derives from that mapping.
"""

from __future__ import annotations

from pathlib import Path

from django.apps import apps
from django.conf import settings


# These ship with every Django project and don't need routing.
_BUILTIN_APP_LABELS: frozenset[str] = frozenset({
    "admin", "auth", "contenttypes", "sessions", "messages",
    "staticfiles", "sites", "postgres", "mysql", "sqlite3", "oracle",
})


class AppInspector:
    """Resolve apps ↔ databases based on Django settings.

    Stateless and cheap — instantiate freely.
    """

    # --- Database names ---

    def all_database_names(self) -> list[str]:
        """All aliases declared in ``settings.DATABASES``."""
        return list(settings.DATABASES.keys())

    # --- App enumeration ---

    def all_installed_apps(self) -> list[str]:
        """Installed apps that have their own models/admin/apps.py.

        Filters out Django built-ins and apps without local files —
        their migration story is fully managed by Django itself.
        """
        result: list[str] = []
        for app_config in apps.get_app_configs():
            label = app_config.label
            path = Path(app_config.path)
            if (path / "apps.py").exists():
                if label not in _BUILTIN_APP_LABELS:
                    result.append(label)
            elif (path / "models.py").exists() or (path / "admin.py").exists():
                result.append(label)
        return result

    def routed_app_labels(self) -> set[str]:
        """App labels that have an explicit routing rule."""
        rules: dict[str, str] = getattr(settings, "DATABASE_ROUTING_RULES", {})
        return set(rules.keys())

    def apps_for_database(self, alias: str) -> list[str]:
        """Apps whose tables *should* live on ``alias``.

        - For non-default aliases: only apps explicitly routed here.
        - For ``default``: every installed app NOT routed elsewhere.
        """
        rules: dict[str, str] = getattr(settings, "DATABASE_ROUTING_RULES", {})
        if alias == "default":
            elsewhere = set(rules.keys())
            return [a for a in self.all_installed_apps() if a not in elsewhere]
        return sorted(app for app, db in rules.items() if db == alias)

    # --- Migration / model presence ---

    def app_has_migrations(self, app_label: str) -> bool:
        """True if the app's ``migrations/`` dir has anything beyond ``__init__``."""
        try:
            cfg = apps.get_app_config(app_label)
        except LookupError:
            return False
        migrations_dir = Path(cfg.path) / "migrations"
        if not migrations_dir.exists():
            return False
        return any(
            f.is_file() and f.name != "__init__.py" and f.suffix == ".py"
            for f in migrations_dir.iterdir()
        )

    def app_has_models(self, app_label: str) -> bool:
        """True if the app declares at least one Django model.

        Falls back to file inspection when ``get_models()`` is empty —
        catches apps where models live in nested modules that haven't
        been imported by Django's autodiscover yet at call time.
        """
        try:
            cfg = apps.get_app_config(app_label)
        except LookupError:
            return False
        if list(cfg.get_models()):
            return True

        path = Path(cfg.path)
        models_dir = path / "models"
        candidates: list[Path] = []
        if models_dir.is_dir():
            candidates.extend(models_dir.glob("*.py"))
        if (path / "models.py").exists():
            candidates.append(path / "models.py")

        for candidate in candidates:
            if candidate.name == "__init__.py":
                continue
            try:
                content = candidate.read_text()
            except OSError:
                continue
            if "class " in content and ("models.Model" in content or "(Model)" in content):
                return True
        return False
