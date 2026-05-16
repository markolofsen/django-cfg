"""Read django_migrations + disk migrations via Django's loader."""

from __future__ import annotations

from collections.abc import Iterable

from django.db import connections
from django.db.migrations.loader import MigrationLoader

from ..types import LoadedMigration, MigrationKey


class MigrationHistoryReader:
    """Single source of truth for "what does Django think is applied".

    Hides the ``MigrationLoader`` API behind a typed wrapper that returns
    ``LoadedMigration`` records instead of raw tuples.
    """

    def __init__(self, alias: str) -> None:
        self._alias = alias
        self._loader: MigrationLoader | None = None

    @property
    def loader(self) -> MigrationLoader:
        if self._loader is None:
            self._loader = MigrationLoader(connections[self._alias])
        return self._loader

    def refresh(self) -> None:
        """Re-read after migrate / fake operations changed state."""
        self._loader = MigrationLoader(connections[self._alias])

    # --- Applied / recorded ---

    def applied_keys(self) -> set[MigrationKey]:
        """``django_migrations`` rows on this alias."""
        return set(self.loader.applied_migrations or {})

    def is_applied(self, app_label: str, name: str) -> bool:
        return (app_label, name) in self.applied_keys()

    # --- Disk migrations ---

    def disk_migrations(
        self, app_labels: Iterable[str] | None = None
    ) -> list[LoadedMigration]:
        """All migration files on disk, optionally filtered by app."""
        wanted: set[str] | None = set(app_labels) if app_labels is not None else None
        out: list[LoadedMigration] = []
        for (app, name), migration in (self.loader.disk_migrations or {}).items():
            if wanted is not None and app not in wanted:
                continue
            out.append(LoadedMigration(app_label=app, name=name, migration=migration))
        return out

    # --- Plan utilities ---

    def forwards_plan_for_app(self, app_label: str) -> list[str]:
        """Migration names for ``app_label`` in application order.

        Used by repair planning to compute rewind targets.
        """
        graph = self.loader.graph
        # Find leaf node for this app, then walk the plan back to root.
        leaves = [(a, n) for a, n in graph.leaf_nodes() if a == app_label]
        if not leaves:
            return []
        result: list[str] = []
        seen: set[str] = set()
        for leaf in leaves:
            for a, n in graph.forwards_plan(leaf):
                if a == app_label and n not in seen:
                    seen.add(n)
                    result.append(n)
        return result

    def previous_migration(self, app_label: str, name: str) -> str:
        """Name of the migration immediately before ``name``, or ``"zero"``."""
        plan = self.forwards_plan_for_app(app_label)
        try:
            idx = plan.index(name)
        except ValueError:
            return "zero"
        return plan[idx - 1] if idx > 0 else "zero"
