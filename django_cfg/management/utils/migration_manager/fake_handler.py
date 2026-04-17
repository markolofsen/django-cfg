"""
Generic fake-migration handler for companion fields.

Fields that auto-create companion DB columns via contribute_to_class()
can register a detector so MigrationManager knows when to fake-apply
a migration instead of running it (column already exists in the DB).

Registration (done once, e.g. in AppConfig.ready or field module level):

    from django_cfg.management.utils.migration_manager.fake_handler import (
        register_fake_detector,
    )

    register_fake_detector(lambda op: op.name.endswith("_currency"))

A detector is a callable(op: AddField) -> bool.
If ALL operations in an unapplied migration match ANY registered detector,
AND every matching column already exists in the DB, the migration is faked.
"""

from typing import Callable, List

from django.core.management import call_command
from django.db import migrations as dj_migrations

from .db_inspector import DbInspector
from .logger import MigrationLogger

OpDetector = Callable[[dj_migrations.AddField], bool]

_detectors: List[OpDetector] = []


def register_fake_detector(detector: OpDetector) -> None:
    """Register a detector for AddField operations that can be fake-applied."""
    if detector not in _detectors:
        _detectors.append(detector)


def _matches_any_detector(op: object) -> bool:
    if not isinstance(op, dj_migrations.AddField):
        return False
    return any(d(op) for d in _detectors)


class FakeMigrationHandler:
    def __init__(self, db_inspector: DbInspector, log: MigrationLogger):
        self._db = db_inspector
        self._log = log

    def fake_if_needed(self, db_name: str, unapplied) -> None:
        """
        For each unapplied migration whose every operation matches a registered
        detector AND whose columns already exist in the DB — fake-apply it.
        """
        if not _detectors:
            return

        for app_label, migration_name, migration in unapplied:
            ops = migration.operations
            if not ops:
                continue

            if not all(_matches_any_detector(op) for op in ops):
                continue

            all_exist = all(
                self._db.column_exists(db_name, app_label, op.model_name, op.name)
                for op in ops
            )

            if all_exist:
                self._log.warning(
                    f"  ⚡ Faking {app_label}.{migration_name} "
                    f"(columns already exist in DB)"
                )
                call_command(
                    "migrate", app_label, migration_name,
                    fake=True, database=db_name, verbosity=0,
                )
