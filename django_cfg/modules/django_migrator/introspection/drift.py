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
        disk = history.disk_migrations(owned_apps)
        # Per-app forward plan, used to decide whether a recorded_missing
        # incident is actually superseded by a later DeleteModel/RemoveField.
        plans: dict[str, list[str]] = {}
        by_app_migrations: dict[str, dict[str, LoadedMigration]] = {}
        for loaded in disk:
            by_app_migrations.setdefault(loaded.app_label, {})[loaded.name] = loaded
        for app_label in by_app_migrations:
            plans[app_label] = history.forwards_plan_for_app(app_label)

        for loaded in disk:
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
                    if self._is_superseded(
                        loaded,
                        plan=plans.get(loaded.app_label, []),
                        by_name=by_app_migrations.get(loaded.app_label, {}),
                        schema=schema,
                    ):
                        # CreateModel's table is partially present but a
                        # later migration drops it entirely — not drift.
                        continue
                    report.half_applied.append(DriftIncident(
                        app_label=loaded.app_label,
                        migration_name=loaded.name,
                        direction="half_applied",
                        detail=self._describe_missing(loaded, schema),
                    ))
                elif self._is_superseded(
                    loaded,
                    plan=plans.get(loaded.app_label, []),
                    by_name=by_app_migrations.get(loaded.app_label, {}),
                ):
                    # A later migration removes everything this migration
                    # created — the missing DDL is intentional, not drift.
                    continue
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
                if self._is_non_ddl_create(op):
                    continue
                table = self._table_name_for_create(loaded.app_label, op)
                if schema.table_exists(table):
                    return True
        return False

    @staticmethod
    def _is_non_ddl_create(op: dj_migrations.CreateModel) -> bool:
        """True for CreateModel ops that don't produce a real table.

        Proxy and ``managed=False`` models are pure ORM constructs —
        ``schemaeditor.create_model`` no-ops on them. Flagging them as
        drift causes permanent false positives (the table will never
        exist no matter how many migrations run).
        """
        options = op.options or {}
        if options.get("proxy"):
            return True
        if options.get("managed") is False:
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
            # Proxy / managed=False / abstract models don't produce DDL —
            # skip them so we don't flag e.g. authtoken.0003_tokenproxy
            # as recorded_missing forever.
            if self._is_non_ddl_create(op):
                return None
            table = self._table_name_for_create(app_label, op)
            return schema.table_exists(table)
        if isinstance(op, dj_migrations.AddField):
            # M2M fields live in a through-table, not as a column on the
            # parent. column_exists() would always return False → false
            # "recorded_missing" drift. Skip them.
            if self._is_m2m_field(op.field):
                return None
            model = self._resolve_model(app_label, op.model_name)
            if model is None:
                return None
            table = model._meta.db_table
            if not schema.table_exists(table):
                # Parent table not on this DB → AddField presence is moot.
                return None
            return schema.column_exists(table, self._column_name_for_field(op))
        return None

    @staticmethod
    def _is_m2m_field(field) -> bool:
        return bool(getattr(field, "many_to_many", False))

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

    def _is_superseded(
        self,
        loaded: LoadedMigration,
        *,
        plan: list[str],
        by_name: dict[str, LoadedMigration],
        schema: PostgresSchemaInspector | None = None,
    ) -> bool:
        """True if every MISSING DDL-effect of ``loaded`` is undone downstream.

        For each introspectable op (CreateModel / AddField) whose effect
        is NOT present in the live schema, scan migrations that come
        AFTER ``loaded`` in the app's forward plan for a matching
        ``DeleteModel`` / ``RemoveField``. If every missing effect has a
        downstream cancellation, the recorded-but-missing state is
        intentional, not drift.

        Ops whose effect IS already present in the schema are not checked
        — they don't represent drift even without cancellation.

        ``schema=None`` falls back to the strict "all ops must be cancelled"
        rule (used when the caller cannot supply a schema inspector, e.g.
        for plan-only tests).

        Trade-off: we only handle direct cancellation, not rename chains.
        A CreateModel→RenameModel→DeleteModel sequence will still flag
        as drift — acceptable, very rare.
        """
        if not plan:
            return False
        try:
            idx = plan.index(loaded.name)
        except ValueError:
            return False
        later_ops = []
        for later_name in plan[idx + 1:]:
            later = by_name.get(later_name)
            if later is None:
                continue
            later_ops.extend(later.migration.operations)
        if not later_ops:
            return False

        deleted_models = {
            op.name.lower() for op in later_ops
            if isinstance(op, dj_migrations.DeleteModel)
        }
        removed_fields = {
            (op.model_name.lower(), op.name.lower()) for op in later_ops
            if isinstance(op, dj_migrations.RemoveField)
        }
        # A RenameField effectively cancels the *old* name on the parent
        # model — the original column no longer exists under that name.
        # Without this, e.g. token_blacklist.0002 (AddField jti_hex) →
        # 0006 (RenameField jti_hex → jti) is flagged as drift forever.
        renamed_from_fields = {
            (op.model_name.lower(), op.old_name.lower()) for op in later_ops
            if isinstance(op, dj_migrations.RenameField)
        }

        for op in loaded.migration.operations:
            if isinstance(op, dj_migrations.CreateModel):
                if self._is_non_ddl_create(op):
                    continue
                table = self._table_name_for_create(loaded.app_label, op)
                if schema is not None and schema.table_exists(table):
                    continue  # Effect present — nothing to cancel.
                if op.name.lower() not in deleted_models:
                    return False
            elif isinstance(op, dj_migrations.AddField):
                # M2M lives in a through-table; nothing to check on the
                # parent column. Treat as superseded-by-default.
                if self._is_m2m_field(op.field):
                    continue
                model = self._resolve_model(loaded.app_label, op.model_name)
                if schema is not None and model is not None:
                    col = self._column_name_for_field(op)
                    if schema.column_exists(model._meta.db_table, col):
                        continue  # Effect present — nothing to cancel.
                key = (op.model_name.lower(), op.name.lower())
                # AddField is cancelled by RemoveField, RenameField (of
                # the old name), or the parent model being deleted later.
                if (
                    key not in removed_fields
                    and key not in renamed_from_fields
                    and op.model_name.lower() not in deleted_models
                ):
                    return False
        return True

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
