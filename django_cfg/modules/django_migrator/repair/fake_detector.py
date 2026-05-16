"""Companion-field detector registry.

Some fields auto-create a companion DB column via
``contribute_to_class()`` — e.g. ``django_currency.fields.MoneyField``
adds a hidden ``_currency`` column when you declare a ``MoneyField``.
The migration recorded for adding that field expects to ALTER TABLE for
the companion column, but the column already exists from the parent
field's setup. Without detection the migration fails with "column
already exists".

Field implementations register a predicate; the orchestrator runs
through unapplied migrations once at the start and fake-applies any
whose ops all match.

Public API (kept stable from the previous module):
    register_fake_detector(detector)
"""

from __future__ import annotations

from typing import Callable

from django.db import migrations as dj_migrations

#: Predicate called with an AddField operation; returns True if the
#: operation refers to a companion column whose DDL is already implicit.
OpDetector = Callable[[dj_migrations.AddField], bool]

_detectors: list[OpDetector] = []


def register_fake_detector(detector: OpDetector) -> None:
    """Register a predicate for companion-field detection."""
    if detector not in _detectors:
        _detectors.append(detector)


def matches_any_detector(op: object) -> bool:
    """True iff at least one registered predicate accepts the op."""
    if not isinstance(op, dj_migrations.AddField):
        return False
    return any(d(op) for d in _detectors)


def reset_detectors_for_tests() -> None:
    """Clear the registry — only call from test fixtures."""
    _detectors.clear()


def detector_count() -> int:
    """How many detectors are registered (used by orchestrator gating)."""
    return len(_detectors)
