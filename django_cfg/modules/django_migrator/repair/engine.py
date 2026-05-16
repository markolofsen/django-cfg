"""Orchestrate fake-apply and fake-rewind sequences.

The engine takes a ``DriftReport`` and produces side effects on
``django_migrations`` to bring the recorded history in line with the
live schema. After it returns, a plain ``migrate --database=X`` should
succeed without "already exists" or "does not exist" errors.
"""

from __future__ import annotations

from collections import defaultdict

from ..exceptions import RepairFailed
from ..introspection.history import MigrationHistoryReader
from ..introspection.schema import PostgresSchemaInspector
from ..logger import MigratorLogger
from ..types import DbReport, DriftIncident, DriftReport, RewindPlan
from .fake_detector import detector_count, matches_any_detector
from .primitives import fake_apply, fake_rewind


class RepairEngine:
    """Compute and apply repair plans for a single DB at a time."""

    def __init__(self, log: MigratorLogger) -> None:
        self._log = log

    def apply(
        self,
        alias: str,
        drift: DriftReport,
        db_report: DbReport,
    ) -> None:
        """Apply all repairs implied by ``drift``.

        Order matters:
          1. Fake-apply unrecorded-present so the history catches up.
          2. Fake-apply half-applied so plain migrate won't re-create
             existing tables. Report missing columns as a manual fix.
          3. Fake-rewind recorded-missing so plain migrate re-applies
             the missing DDL forward.
        """
        # 1. unrecorded_present
        for incident in drift.unrecorded_present:
            try:
                fake_apply(
                    alias=alias,
                    app_label=incident.app_label,
                    migration_name=incident.migration_name,
                    log=self._log,
                )
                db_report.repairs_applied.append(
                    f"fake-apply {alias}:{incident.app_label}.{incident.migration_name}"
                )
            except RepairFailed as exc:
                db_report.add_error(str(exc))
                raise

        # 2. half_applied
        for incident in drift.half_applied:
            try:
                fake_apply(
                    alias=alias,
                    app_label=incident.app_label,
                    migration_name=incident.migration_name,
                    log=self._log,
                )
                db_report.repairs_applied.append(
                    f"fake-apply (half-applied) {alias}:{incident.app_label}."
                    f"{incident.migration_name}"
                )
                # Surface manual recovery requirement.
                db_report.add_warning(
                    f"{alias}:{incident.app_label}.{incident.migration_name} "
                    f"was half-applied — fake-applied to unblock migrate, but "
                    f"{incident.detail}. Add a follow-up migration to recreate "
                    f"the missing columns, or restore from backup."
                )
            except RepairFailed as exc:
                db_report.add_error(str(exc))
                raise

        # 3. recorded_missing
        rewind_plans = self._plan_rewinds(alias, drift.recorded_missing)
        for plan in rewind_plans:
            try:
                fake_rewind(
                    alias=plan.alias,
                    app_label=plan.app_label,
                    target_before=plan.target_before,
                    log=self._log,
                )
                db_report.repairs_applied.append(
                    f"fake-rewind {plan.alias}:{plan.app_label} → "
                    f"{plan.target_before} "
                    f"(re-applies {len(plan.migrations_to_reapply)})"
                )
            except RepairFailed as exc:
                db_report.add_error(str(exc))
                raise

    def apply_companion_fake(
        self,
        alias: str,
        db_report: DbReport,
    ) -> None:
        """Fake-apply migrations whose AddField ops are all companion fields.

        Independent from drift detection — this targets pending
        migrations whose DDL is implicit because the field's
        ``contribute_to_class`` already added the column.
        """
        if detector_count() == 0:
            return

        history = MigrationHistoryReader(alias)
        applied = history.applied_keys()
        schema = PostgresSchemaInspector(alias)

        for loaded in history.disk_migrations():
            if loaded.key in applied:
                continue
            ops = loaded.migration.operations
            if not ops:
                continue
            if not all(matches_any_detector(op) for op in ops):
                continue

            # All ops match a detector — check every column actually exists.
            from django.db import migrations as dj_migrations
            from django.apps import apps as django_apps

            all_present = True
            for op in ops:
                assert isinstance(op, dj_migrations.AddField)  # detector guarantee
                cfg = django_apps.get_app_config(loaded.app_label)
                model = next(
                    (m for m in cfg.get_models()
                     if m.__name__.lower() == op.model_name.lower()),
                    None,
                )
                if model is None:
                    all_present = False
                    break
                # Resolve actual column name (FK gets _id suffix).
                field = op.field
                db_column = getattr(field, "db_column", None)
                if db_column:
                    col = db_column
                elif getattr(field, "many_to_one", False) or getattr(field, "one_to_one", False):
                    col = f"{op.name}_id"
                else:
                    col = op.name
                if not schema.column_exists(model._meta.db_table, col):
                    all_present = False
                    break
            if not all_present:
                continue

            try:
                fake_apply(
                    alias=alias,
                    app_label=loaded.app_label,
                    migration_name=loaded.name,
                    log=self._log,
                )
                db_report.repairs_applied.append(
                    f"fake-apply-companion {alias}:{loaded.app_label}.{loaded.name}"
                )
            except RepairFailed as exc:
                # Companion fake-apply failures are warnings, not errors —
                # they don't block downstream migrations (those will just
                # try the real DDL and likely succeed if column was added
                # by the parent field, or fail loudly if not).
                db_report.add_warning(str(exc))

    # --- Planning ---

    def _plan_rewinds(
        self,
        alias: str,
        incidents: list[DriftIncident],
    ) -> list[RewindPlan]:
        """Group by app, find earliest drifted, compute rewind target."""
        if not incidents:
            return []
        history = MigrationHistoryReader(alias)

        by_app: dict[str, list[str]] = defaultdict(list)
        for inc in incidents:
            by_app[inc.app_label].append(inc.migration_name)

        plans: list[RewindPlan] = []
        for app_label, drifted_names in by_app.items():
            ordered_plan = history.forwards_plan_for_app(app_label)
            if not ordered_plan:
                # Fallback: lexical min — unlikely to happen with a
                # working graph, but better than crashing.
                earliest = min(drifted_names)
            else:
                earliest = min(
                    drifted_names,
                    key=lambda n: ordered_plan.index(n) if n in ordered_plan else 0,
                )

            target_before = history.previous_migration(app_label, earliest)

            if ordered_plan:
                idx = ordered_plan.index(earliest)
                to_reapply = tuple(ordered_plan[idx:])
            else:
                to_reapply = tuple(sorted(drifted_names))

            plans.append(RewindPlan(
                alias=alias,
                app_label=app_label,
                target_before=target_before,
                migrations_to_reapply=to_reapply,
            ))
        return plans
