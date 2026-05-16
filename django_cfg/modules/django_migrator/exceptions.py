"""Exceptions raised by django_migrator.

Caller (typically a management command) catches MigratorError to print
a clean message + exit non-zero. Internal failures bubble as-is.
"""

from __future__ import annotations


class MigratorError(Exception):
    """Base class for any migrator-specific failure."""


class GuardFailed(MigratorError):
    """A pre-flight guard refused to proceed.

    Raised when the orchestrator decides to abort one DB's lifecycle
    based on a fatal GuardResult.
    """


class DriftRequiresRepair(MigratorError):
    """Drift was detected and the user did not opt in to --repair."""


class RepairFailed(MigratorError):
    """A fake-apply or fake-rewind call_command raised."""


class ConcurrentMigrationDetected(MigratorError):
    """Another migrate process holds the Postgres advisory lock."""
