"""Re-export of the PostgreSQL extension installer used at orchestrator start.

Lives in a separate module so the manager doesn't import from sibling
``utils.postgresql`` directly — keeps the dependency tree clean and
makes it easy to swap or mock in tests.
"""

from __future__ import annotations

from django_cfg.management.utils.postgresql import (
    ensure_postgresql_extensions as _ensure,
)


def ensure_postgresql_extensions(alias: str, log) -> None:
    """Install required PG extensions on the given alias.

    Adapter signature: takes our typed ``MigratorLogger`` instead of the
    legacy ``(stdout, style, logger)`` triple — keeps callers concise.
    """
    _ensure(alias, log.stdout, log.style, log.logger)
