"""Thin wrappers around Django's ``migrate`` for fake-apply / fake-rewind.

Every repair action funnels through here so:
- Logging is uniform.
- Errors get wrapped in ``RepairFailed`` for the orchestrator.
- Tests can mock ONE function (``call_command``) per primitive.
"""

from __future__ import annotations

from django.core.management import call_command

from ..exceptions import RepairFailed
from ..logger import MigratorLogger


def fake_apply(
    *,
    alias: str,
    app_label: str,
    migration_name: str,
    log: MigratorLogger,
) -> None:
    """Mark ``app.migration`` applied without running its DDL.

    Used when the schema effect already exists (legacy table, manual
    SQL). Equivalent to ``manage.py migrate <app> <name> --fake
    --database=<alias>``.
    """
    log.warning(
        f"⚡ fake-apply  {alias}:{app_label}.{migration_name} "
        f"(DDL already present)"
    )
    try:
        call_command(
            "migrate", app_label, migration_name,
            fake=True, database=alias, verbosity=0,
        )
    except Exception as exc:
        raise RepairFailed(
            f"fake-apply {alias}:{app_label}.{migration_name} failed: {exc}"
        ) from exc


def fake_rewind(
    *,
    alias: str,
    app_label: str,
    target_before: str,
    log: MigratorLogger,
) -> None:
    """Mark every migration after ``target_before`` as unapplied for ``app``.

    Schema is untouched — only ``django_migrations`` rows are removed.
    The next plain ``migrate`` will see the rewound migrations as
    pending and re-run their DDL forward.

    ``target_before == "zero"`` rewinds the whole app history.
    """
    log.warning(
        f"🩹 fake-rewind {alias}:{app_label} → {target_before}"
    )
    try:
        call_command(
            "migrate", app_label, target_before,
            fake=True, database=alias, verbosity=0,
        )
    except Exception as exc:
        raise RepairFailed(
            f"fake-rewind {alias}:{app_label} to {target_before} failed: {exc}"
        ) from exc
