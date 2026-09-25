"""Make a forking RQ worker safe for the database and for macOS.

RQ forks a work horse per job. Two things the parent holds do not survive that:

- **The psycopg pool.** django-cfg enables Django's pool for every PostgreSQL
  database. The child inherits the pool object but not the threads that open
  its connections, so once the inherited idle list is empty, ``getconn()``
  waits for a connection nothing will open and the job fails with
  "couldn't get a connection after N sec" — while PgBouncer shows no one
  waiting. MLS lost all four heavy workers to this on 2026-09-25 (0 of ~15
  jobs an hour). A worker therefore runs without the pool: PgBouncer or the
  server pools, and a job opening one direct connection costs milliseconds.
- **An open connection.** Whatever the parent opened (startup queries) is a
  socket the child shares with it. The child forgets it — never closes it, which
  would close it for the parent too — and opens its own.
"""

from __future__ import annotations

import os
import sys

_fork_hook_registered = False


def fix_macos_fork_safety() -> None:
    """Allow fork() after Objective-C initialisation on macOS.

    On macOS Big Sur+, fork() after ObjC initialisation crashes; numpy, httpx
    and ML frameworks trigger it. RQ workers share no ObjC state with their
    children, so the check is safe to disable. No-op elsewhere.
    """
    if sys.platform == "darwin":
        os.environ.setdefault("OBJC_DISABLE_INITIALIZE_FORK_SAFETY", "YES")


def detach_connection_pools() -> None:
    """Close any open psycopg pool and stop every alias from creating one."""
    from django.db import connections

    for alias in connections:
        conn = connections[alias]
        if not conn.settings_dict.get("OPTIONS", {}).get("pool"):
            continue
        # `pool` is a property that CREATES the pool on first access, so ask
        # the class-level registry whether one exists before closing it.
        if alias in getattr(conn, "_connection_pools", {}):
            conn.close_pool()
        conn.settings_dict["OPTIONS"].pop("pool", None)
        conn.close()


def forget_inherited_connections() -> None:
    """In a forked child: drop, without closing, every connection the parent held."""
    from django.db import connections

    for conn in connections.all(initialized_only=True):
        conn.connection = None


def prepare_forking_worker() -> None:
    """Everything a forking RQ worker needs before it starts. Idempotent."""
    global _fork_hook_registered

    detach_connection_pools()
    if not _fork_hook_registered:
        os.register_at_fork(after_in_child=forget_inherited_connections)
        _fork_hook_registered = True
