"""django_migrator — state-validated multi-database migration orchestrator.

Public API:

    from django_cfg.modules.django_migrator import (
        Migrator,
        MigratorOptions,
        MigratorLogger,
        TextReportFormatter,
        register_fake_detector,
    )

    manager = Migrator(options=MigratorOptions(repair=True))
    report = manager.migrate_all()
    print(TextReportFormatter().render(report))

See ``modules/django_migrator/tests/`` for full lifecycle examples and
``@dev/@refactoring10-multidb/`` for the design rationale.
"""

from .exceptions import (
    ConcurrentMigrationDetected,
    DriftRequiresRepair,
    GuardFailed,
    MigratorError,
    RepairFailed,
)
from .introspection import (
    AppInspector,
    DriftDetector,
    MigrationHistoryReader,
    PostgresSchemaInspector,
)
from .logger import MigratorLogger
from .orchestration import (
    DEFAULT_GUARDS,
    Guard,
    GuardSet,
    Migrator,
    check_connection_live,
    check_no_concurrent_migration,
    check_test_mirror_isolation,
)
from .repair import (
    OpDetector,
    RepairEngine,
    detector_count,
    fake_apply,
    fake_rewind,
    matches_any_detector,
    register_fake_detector,
    reset_detectors_for_tests,
)
from .reporting import TextReportFormatter
from .types import (
    DbReport,
    DriftDirection,
    DriftIncident,
    DriftReport,
    FakeApplyAction,
    GuardResult,
    LoadedMigration,
    MigrationKey,
    MigrationReport,
    MigratorOptions,
    RewindPlan,
)

__all__ = [
    # Main entry points
    "Migrator",
    "MigratorOptions",
    "MigratorLogger",
    # Reporting
    "TextReportFormatter",
    "MigrationReport",
    "DbReport",
    "DriftReport",
    "DriftIncident",
    "DriftDirection",
    "GuardResult",
    "RewindPlan",
    "FakeApplyAction",
    "LoadedMigration",
    "MigrationKey",
    # Introspection
    "AppInspector",
    "DriftDetector",
    "MigrationHistoryReader",
    "PostgresSchemaInspector",
    # Repair primitives
    "RepairEngine",
    "fake_apply",
    "fake_rewind",
    # Companion-field detector registry
    "OpDetector",
    "register_fake_detector",
    "matches_any_detector",
    "detector_count",
    "reset_detectors_for_tests",
    # Guards
    "GuardSet",
    "Guard",
    "DEFAULT_GUARDS",
    "check_connection_live",
    "check_test_mirror_isolation",
    "check_no_concurrent_migration",
    # Exceptions
    "MigratorError",
    "DriftRequiresRepair",
    "RepairFailed",
    "GuardFailed",
    "ConcurrentMigrationDetected",
]
