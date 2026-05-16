"""Pre-flight guards that run before any DDL on a database alias."""

from __future__ import annotations

import os
import sys
from typing import Callable

from django.db import connections

from ..logger import MigratorLogger
from ..types import GuardResult


#: A guard is a function (alias) -> GuardResult.
Guard = Callable[[str], GuardResult]


# --- Individual guards ---


def check_connection_live(alias: str) -> GuardResult:
    """Catch typos in DATABASES dict, dead hosts, wrong creds early."""
    try:
        with connections[alias].cursor() as cur:
            cur.execute("SELECT 1")
        return GuardResult("connection_live", True)
    except Exception as exc:
        return GuardResult(
            "connection_live",
            False,
            f"Cannot connect to {alias}: {exc}",
        )


def check_test_mirror_isolation(alias: str) -> GuardResult:
    """Refuse to migrate if TEST.MIRROR is actively redirecting writes.

    TEST.MIRROR is a Django test-runner config that collapses one alias
    onto another's physical DB during tests. The setting persists in
    DATABASES outside tests, but is HARMLESS as long as the two aliases
    point at different physical NAMEs — the router only follows the
    mirror when both connections share the same NAME (which only happens
    during ``manage.py test``).

    This guard fires only when both:
      - TEST.MIRROR is set on this alias
      - The mirror is ACTIVE — i.e. the two connections share a NAME

    In that combination, we either are in test mode (legitimate) or have
    a real misconfiguration (e.g. someone manually set both DATABASE
    URLs to the same value while leaving test_mirror in DatabaseConfig).
    """
    cfg = connections[alias].settings_dict
    mirror = cfg.get("TEST", {}).get("MIRROR")
    if not mirror:
        return GuardResult("test_mirror_isolation", True)

    if not _physical_dbs_merged(alias, mirror):
        # Mirror is configured but inactive — distinct NAMEs mean the
        # router routes normally to this alias. No risk of silent write
        # redirection. Pass silently.
        return GuardResult("test_mirror_isolation", True)

    # NAMEs match — mirror IS active.
    in_test_mode = (
        "test" in sys.argv
        or os.environ.get("DJANGO_TEST_DB") == "1"
    )
    if in_test_mode:
        return GuardResult("test_mirror_isolation", True)

    return GuardResult(
        "test_mirror_isolation",
        False,
        f"Alias '{alias}' has TEST.MIRROR='{mirror}' AND both connections "
        f"share NAME='{cfg.get('NAME')}'. The router will redirect writes "
        f"to '{mirror}'. If this is intentional (test mode), set "
        f"DJANGO_TEST_DB=1. Otherwise fix the DATABASES NAMEs or drop "
        f"test_mirror from DatabaseConfig.",
    )


def check_no_concurrent_migration(alias: str) -> GuardResult:
    """Detect another migrate process holding Postgres advisory locks.

    A locked-out migrate would hang for the duration of the other
    process — failing loudly is friendlier.
    """
    try:
        with connections[alias].cursor() as cur:
            cur.execute(
                "SELECT count(*) FROM pg_locks "
                "WHERE locktype = 'advisory' "
                "  AND objid != 0 "
                "  AND pid != pg_backend_pid()"
            )
            row = cur.fetchone()
            count = row[0] if row else 0
        if count == 0:
            return GuardResult("no_concurrent_migration", True)
        return GuardResult(
            "no_concurrent_migration",
            False,
            f"Found {count} advisory lock(s) on '{alias}' — another "
            f"migration may be in progress. Wait and retry.",
        )
    except Exception:
        # Non-Postgres backend or query failure → don't block migrate.
        return GuardResult(
            "no_concurrent_migration",
            False,
            "Could not check advisory locks (non-Postgres backend?)",
            fatal=False,
        )


# --- Composition ---


DEFAULT_GUARDS: tuple[Guard, ...] = (
    check_connection_live,
    check_test_mirror_isolation,
    check_no_concurrent_migration,
)


class GuardSet:
    """Run a sequence of guards on a database alias."""

    def __init__(
        self,
        log: MigratorLogger,
        guards: tuple[Guard, ...] = DEFAULT_GUARDS,
    ) -> None:
        self._log = log
        self._guards = guards

    def run(self, alias: str) -> list[GuardResult]:
        """Run every guard and return the full sequence of results.

        Caller decides what to do with failures based on ``fatal``.
        Stops at the first fatal failure to avoid noisy follow-up errors.
        """
        results: list[GuardResult] = []
        for guard in self._guards:
            result = guard(alias)
            results.append(result)
            if not result.passed:
                if result.fatal:
                    self._log.error(f"{result.name}: {result.message}")
                    break
                else:
                    self._log.warning(f"{result.name}: {result.message}")
        return results


# --- Helpers ---


def _physical_dbs_merged(alias: str, mirror: str) -> bool:
    try:
        return (
            connections[alias].settings_dict.get("NAME")
            == connections[mirror].settings_dict.get("NAME")
        )
    except Exception:
        return False
