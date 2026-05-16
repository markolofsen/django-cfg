"""Shared types for django_migrator.

We deliberately use plain dataclasses (not pydantic) because:
  - This module runs at deploy time and during management commands; we
    want zero extra import cost beyond stdlib + Django.
  - No external I/O boundary needs Pydantic's validation — all inputs
    come from Django's introspection APIs which are already typed.
  - Dataclasses keep the module testable with simple ``replace()`` and
    direct construction in unit tests.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Literal

if TYPE_CHECKING:
    from django.db.migrations import Migration


# --- Identifiers ---

#: A migration is uniquely identified by (app_label, migration_name).
MigrationKey = tuple[str, str]


# --- Drift classification ---

DriftDirection = Literal[
    "recorded_missing", "unrecorded_present", "half_applied",
]
"""Direction of a single drift incident.

- ``recorded_missing``: ``django_migrations`` thinks the migration ran,
  but its DDL effect (table/column) is not present in the live DB.
- ``unrecorded_present``: every DDL effect IS present, but
  ``django_migrations`` has no record of the migration running.
- ``half_applied``: SOME DDL effects (typically CreateModel tables) are
  present while others (typically AddField columns) are missing —
  AND the migration is unrecorded. Auto-repair fake-applies it but
  surfaces a manual step: re-create the missing columns.
"""


@dataclass(frozen=True, slots=True)
class DriftIncident:
    """One specific (app, migration) mismatch with the live schema."""

    app_label: str
    migration_name: str
    direction: DriftDirection
    detail: str = ""
    """Human-readable description of WHY this was flagged.

    e.g. "column catalog_vehicle_photo.source_meta missing" or
    "table catalog_vehicle exists but no migration record".
    """

    @property
    def key(self) -> MigrationKey:
        return (self.app_label, self.migration_name)


@dataclass(slots=True)
class DriftReport:
    """All drift detected on a single database alias."""

    alias: str
    recorded_missing: list[DriftIncident] = field(default_factory=list)
    unrecorded_present: list[DriftIncident] = field(default_factory=list)
    half_applied: list[DriftIncident] = field(default_factory=list)
    """Unrecorded migrations where CreateModel ran but later AddFields
    did not. Auto-repair fake-applies them; manual SQL/migration needed
    to recover the missing columns.
    """
    foreign_tables: list[str] = field(default_factory=list)
    """Tables present on this DB whose owning app is routed elsewhere.

    Not an error — could be legacy from before routing rules existed.
    Surfaced for visibility; never auto-dropped.
    """

    def has_issues(self) -> bool:
        return bool(
            self.recorded_missing
            or self.unrecorded_present
            or self.half_applied
        )

    def total_drift_count(self) -> int:
        return (
            len(self.recorded_missing)
            + len(self.unrecorded_present)
            + len(self.half_applied)
        )


# --- Guard results ---


@dataclass(frozen=True, slots=True)
class GuardResult:
    """Outcome of a single pre-flight check."""

    name: str
    passed: bool
    message: str = ""
    fatal: bool = True
    """Whether failure aborts the per-DB lifecycle.

    Non-fatal failures are surfaced as warnings; fatal ones abort.
    """


# --- Per-DB report ---


@dataclass(slots=True)
class DbReport:
    """Outcome of running the orchestrator against one database alias."""

    alias: str
    aborted: bool = False
    migration_executed: bool = False
    pending_after_migrate: int = 0
    drift: DriftReport | None = None
    repairs_applied: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    guard_results: list[GuardResult] = field(default_factory=list)

    @property
    def is_clean(self) -> bool:
        return (
            not self.aborted
            and not self.errors
            and not self.warnings
            and (self.drift is None or not self.drift.has_issues())
            and self.pending_after_migrate == 0
        )

    def add_warning(self, msg: str) -> None:
        self.warnings.append(msg)

    def add_error(self, msg: str) -> None:
        self.errors.append(msg)


@dataclass(slots=True)
class MigrationReport:
    """Aggregate of every DB processed in one ``migrate_all`` invocation."""

    db_reports: list[DbReport] = field(default_factory=list)

    @property
    def all_clean(self) -> bool:
        return all(d.is_clean for d in self.db_reports)

    def add(self, db: DbReport) -> None:
        self.db_reports.append(db)

    def by_alias(self, alias: str) -> DbReport | None:
        for d in self.db_reports:
            if d.alias == alias:
                return d
        return None


# --- Repair plan ---


@dataclass(frozen=True, slots=True)
class RewindPlan:
    """A computed fake-rewind for a single app on a single DB.

    Captures: rewind history back to ``target_before``, then plain
    migrate will re-apply ``migrations_to_reapply`` forward.
    """

    alias: str
    app_label: str
    target_before: str
    """Migration name to rewind history to. ``"zero"`` means rewind the
    entire app history."""
    migrations_to_reapply: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class FakeApplyAction:
    """A computed fake-apply for a single migration on a single DB."""

    alias: str
    app_label: str
    migration_name: str


# --- Orchestrator settings ---


@dataclass(frozen=True, slots=True)
class MigratorOptions:
    """User-provided options that change orchestrator behavior."""

    repair: bool = False
    """Allow the orchestrator to auto-repair detected drift."""

    dry_run: bool = False
    """No DDL, no record changes — forensic check only."""

    interactive: bool = True
    """Prompt before applying repairs."""

    skip_makemigrations: bool = False
    """Don't run makemigrations before migrating."""

    verbosity: int = 1


# --- Loader-resolved migration ---


@dataclass(frozen=True, slots=True)
class LoadedMigration:
    """Migration object paired with its (app, name) key.

    Convenience tuple so callers don't have to unpack ``(key, migration)``
    pairs from ``MigrationLoader.disk_migrations``.
    """

    app_label: str
    name: str
    migration: "Migration"

    @property
    def key(self) -> MigrationKey:
        return (self.app_label, self.name)
