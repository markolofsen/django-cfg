"""Detect drift between django_migrations and live PostgreSQL schema."""

from __future__ import annotations

from django.apps import apps as django_apps
from django.db import migrations as dj_migrations
from django.db.migrations.operations.base import Operation

from ..types import DriftIncident, DriftReport, LoadedMigration
from .apps import AppInspector
from .history import MigrationHistoryReader
from .schema import PostgresSchemaInspector


# Operations whose effects we can introspect cheaply. Anything else is
# skipped — see _check_operation.
_INTROSPECTABLE_OPS = (
    dj_migrations.CreateModel,
    dj_migrations.AddField,
)


# Tables Django creates on every DB regardless of routing rules.
_ALWAYS_GLOBAL_TABLES: frozenset[str] = frozenset({
    "django_migrations",
    "django_content_type",
    "django_session",
    "auth_permission",
    "auth_user",
    "auth_group",
    "auth_user_groups",
    "auth_user_user_permissions",
    "auth_group_permissions",
})


class DriftDetector:
    """Compare what ``django_migrations`` says vs what the DB actually has.

    Produces a typed ``DriftReport``. Pure read-only; never mutates the
    history table or live schema.
    """

    def __init__(self, app_inspector: AppInspector) -> None:
        self._apps = app_inspector

    def scan(self, alias: str) -> DriftReport:
        owned_apps = set(self._apps.apps_for_database(alias))
        schema = PostgresSchemaInspector(alias)
        history = MigrationHistoryReader(alias)

        report = DriftReport(alias=alias)

        applied = history.applied_keys()
        for loaded in history.disk_migrations(owned_apps):
            ddl_status = self._operations_effect_status(loaded, schema)
            if ddl_status is None:
                continue  # Pure data migration — can't introspect.

            recorded = loaded.key in applied
            create_present = self._has_create_model_present(loaded, schema)

            if recorded and ddl_status is False:
                # Recorded but DDL absent. Two sub-cases:
                # (a) genuinely no DDL present (full rewind safe)
                # (b) CreateModel ran but AddField didn't (half-applied
                #     but somehow recorded — extremely rare, treat as
                #     half_applied for safety).
                if create_present:
                    report.half_applied.append(DriftIncident(
                        app_label=loaded.app_label,
                        migration_name=loaded.name,
                        direction="half_applied",
                        detail=self._describe_missing(loaded, schema),
                    ))
                else:
                    report.recorded_missing.append(DriftIncident(
                        app_label=loaded.app_label,
                        migration_name=loaded.name,
                        direction="recorded_missing",
                        detail=self._describe_missing(loaded, schema),
                    ))
            elif not recorded and ddl_status is True:
                report.unrecorded_present.append(DriftIncident(
                    app_label=loaded.app_label,
                    migration_name=loaded.name,
                    direction="unrecorded_present",
                    detail=self._describe_present(loaded, schema),
                ))
            elif not recorded and ddl_status is False and create_present:
                # Unrecorded, half-applied: CreateModel tables exist but
                # follow-up AddFields are missing AND django_migrations
                # has no row. Plain `migrate` would try to re-create the
                # existing tables and fail with "already exists".
                # Repair: fake-apply the migration so it's marked done,
                # and report the missing columns as a manual fix.
                report.half_applied.append(DriftIncident(
                    app_label=loaded.app_label,
                    migration_name=loaded.name,
                    direction="half_applied",
                    detail=self._describe_missing(loaded, schema),
                ))

        report.foreign_tables.extend(
            self._foreign_tables(alias, schema, owned_apps)
        )
        return report

    def _has_create_model_present(
        self,
        loaded: LoadedMigration,
        schema: PostgresSchemaInspector,
    ) -> bool:
        """True if any CreateModel op in this migration's table already exists.

        Used to detect "half-applied" migrations where the CreateModel
        ran but follow-up AddFields did not. These can't be safely
        rewound because the table is still there.
        """
        for op in loaded.migration.operations:
            if isinstance(op, dj_migrations.CreateModel):
                table = self._table_name_for_create(loaded.app_label, op)
                if schema.table_exists(table):
                    return True
        return False

    # --- Per-operation effect check ---

    def _operations_effect_status(
        self,
        loaded: LoadedMigration,
        schema: PostgresSchemaInspector,
    ) -> bool | None:
        """Tri-state: True (effects present), False (missing), None (skip).

        ``None`` means no operation in this migration is introspectable
        — typically pure RunPython/RunSQL. Such migrations are trusted to
        be applied iff ``django_migrations`` says so.
        """
        checks: list[bool] = []
        for op in loaded.migration.operations:
            check = self._check_operation(loaded.app_label, op, schema)
            if check is not None:
                checks.append(check)
        if not checks:
            return None
        return all(checks)

    def _check_operation(
        self,
        app_label: str,
        op: Operation,
        schema: PostgresSchemaInspector,
    ) -> bool | None:
        if isinstance(op, dj_migrations.CreateModel):
            table = self._table_name_for_create(app_label, op)
            return schema.table_exists(table)
        if isinstance(op, dj_migrations.AddField):
            model = self._resolve_model(app_label, op.model_name)
            if model is None:
                return None
            table = model._meta.db_table
            if not schema.table_exists(table):
                # Parent table not on this DB → AddField presence is moot.
                return None
            return schema.column_exists(table, self._column_name_for_field(op))
        return None

    # --- Helpers ---

    def _table_name_for_create(self, app_label: str, op: dj_migrations.CreateModel) -> str:
        explicit = (op.options or {}).get("db_table")
        if explicit:
            return explicit
        # Django's default: <app_label>_<modelname_lower>
        return f"{app_label}_{op.name.lower()}"

    def _column_name_for_field(self, op: dj_migrations.AddField) -> str:
        """Resolve the actual DB column name for an AddField operation.

        Django adds an ``_id`` suffix to ForeignKey field columns and
        respects an explicit ``db_column`` keyword. Mirror both so the
        column existence check matches reality.
        """
        field = op.field
        # Explicit db_column wins.
        db_column = getattr(field, "db_column", None)
        if db_column:
            return db_column
        # ForeignKey / OneToOneField / ManyToOneRel etc. get _id appended.
        if getattr(field, "many_to_one", False) or getattr(field, "one_to_one", False):
            return f"{op.name}_id"
        return op.name

    def _resolve_model(self, app_label: str, model_name: str):
        try:
            cfg = django_apps.get_app_config(app_label)
        except LookupError:
            return None
        for m in cfg.get_models():
            if m.__name__.lower() == model_name.lower():
                return m
        return None

    def _describe_missing(
        self, loaded: LoadedMigration, schema: PostgresSchemaInspector
    ) -> str:
        for op in loaded.migration.operations:
            if isinstance(op, _INTROSPECTABLE_OPS):
                if isinstance(op, dj_migrations.AddField):
                    model = self._resolve_model(loaded.app_label, op.model_name)
                    if model:
                        col = self._column_name_for_field(op)
                        if not schema.column_exists(model._meta.db_table, col):
                            return (
                                f"column {model._meta.db_table}.{col} missing "
                                f"(expected by {op.__class__.__name__})"
                            )
                if isinstance(op, dj_migrations.CreateModel):
                    table = self._table_name_for_create(loaded.app_label, op)
                    if not schema.table_exists(table):
                        return f"table {table} missing (expected by CreateModel)"
        return "DDL effects not present in DB"

    def _describe_present(
        self, loaded: LoadedMigration, schema: PostgresSchemaInspector
    ) -> str:
        for op in loaded.migration.operations:
            if isinstance(op, dj_migrations.CreateModel):
                table = self._table_name_for_create(loaded.app_label, op)
                if schema.table_exists(table):
                    return f"table {table} already exists in DB"
        return "DDL effects already present in DB"

    def _foreign_tables(
        self,
        alias: str,
        schema: PostgresSchemaInspector,
        owned_apps: set[str],
    ) -> list[str]:
        """Tables present here whose owning app is routed elsewhere."""
        existing = schema.tables()

        owned_tables: set[str] = set()
        for app_label in owned_apps:
            try:
                cfg = django_apps.get_app_config(app_label)
            except LookupError:
                continue
            for m in cfg.get_models():
                owned_tables.add(m._meta.db_table)

        return sorted(
            t for t in existing
            if t not in owned_tables and t not in _ALWAYS_GLOBAL_TABLES
        )
