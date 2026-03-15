"""
Test runner utilities: PostgreSQL cleanup, extension installation, helper methods.
"""

import sys

from django.db import connections

from ...management.utils.postgresql import PostgreSQLExtensionManager


def get_test_db_name(connection) -> str:
    """Return the test database name for a given connection."""
    test_db_name = connection.settings_dict.get('TEST', {}).get('NAME')
    if not test_db_name:
        db_name = connection.settings_dict['NAME']
        test_db_name = f'test_{db_name}'
    return test_db_name


def close_all_pools(verbosity: int = 0) -> None:
    """
    Disable connection pooling for all aliases.

    psycopg3 connection pools keep physical connections alive and reuse them even
    after close() is called. During test DB setup the pool may return a connection
    to 'postgres' or the old test DB, causing MigrationLoader to read
    django_migrations from the wrong database. Destroying pools forces a fresh TCP
    connection on every cursor() call, ensuring settings_dict['NAME'] is honoured.
    """
    for alias in connections:
        c = connections[alias]
        if hasattr(c, 'close_pool'):
            c.close_pool()
        c.settings_dict.get('OPTIONS', {}).pop('pool', None)
        c.__dict__.pop('pool', None)
        if hasattr(c, '_connection_pools'):
            c._connection_pools.pop(alias, None)
        c.close()


def close_all_connections() -> None:
    """Force-close all database connections (without destroying pools)."""
    for alias in connections:
        c = connections[alias]
        if hasattr(c, 'close_pool'):
            c.close_pool()
        c.close()


def install_extensions_on(connection, verbosity: int = 1) -> None:
    """Install PostgreSQL extensions (pgvector, pg_trgm, unaccent) on a connection."""
    db_engine = connection.settings_dict.get('ENGINE', '')
    if 'postgresql' not in db_engine.lower():
        return
    manager = PostgreSQLExtensionManager()
    try:
        needs_pgvector = manager.check_if_pgvector_needed()
        if needs_pgvector:
            with connection.cursor() as cursor:
                cursor.execute("CREATE EXTENSION IF NOT EXISTS vector;")
                cursor.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm;")
                cursor.execute("CREATE EXTENSION IF NOT EXISTS unaccent;")
            if verbosity >= 1:
                sys.stderr.write(
                    f"✅ Installed PostgreSQL extensions for test database '{connection.alias}'\n"
                )
    except Exception as e:
        if verbosity >= 2:
            sys.stderr.write(f"⚠️  Could not install extensions for {connection.alias}: {e}\n")


def install_all_extensions(verbosity: int = 1) -> None:
    """Install PostgreSQL extensions on all configured database connections."""
    for alias in connections:
        install_extensions_on(connections[alias], verbosity=verbosity)


def cleanup_old_test_databases(verbosity: int = 0) -> None:
    """
    Silently drop existing test databases before creating new ones.

    Prevents EOFError in CI when Django would otherwise prompt for confirmation,
    and avoids InconsistentMigrationHistory errors from stale test DBs.
    """
    for alias in connections:
        connection = connections[alias]
        if 'postgresql' not in connection.settings_dict.get('ENGINE', '').lower():
            continue
        test_db_name = get_test_db_name(connection)
        try:
            if _test_database_exists(connection, test_db_name):
                _drop_test_database(connection, test_db_name, verbosity=verbosity)
        except Exception as e:
            if verbosity >= 2:
                sys.stderr.write(
                    f"⚠️  Could not check/cleanup test database {test_db_name}: {e}\n"
                )


def terminate_sessions_on_test_dbs() -> None:
    """
    Forcibly terminate all PostgreSQL sessions on test databases.

    Called before teardown so Django can DROP the test databases without hitting
    "database is being accessed by other users".
    """
    for alias in connections:
        connection = connections[alias]
        if 'postgresql' not in connection.settings_dict.get('ENGINE', '').lower():
            continue
        test_db_name = get_test_db_name(connection)
        try:
            original_db = connection.settings_dict['NAME']
            connection.settings_dict['NAME'] = 'postgres'
            connection.close()
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT pg_terminate_backend(pg_stat_activity.pid)
                    FROM pg_stat_activity
                    WHERE pg_stat_activity.datname = %s
                    AND pid <> pg_backend_pid()
                    """,
                    [test_db_name],
                )
            connection.settings_dict['NAME'] = original_db
            connection.close()
        except Exception:
            pass


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _test_database_exists(connection, test_db_name: str) -> bool:
    try:
        original_db = connection.settings_dict['NAME']
        connection.settings_dict['NAME'] = 'postgres'
        connection.close()
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1 FROM pg_database WHERE datname = %s", [test_db_name])
            exists = cursor.fetchone() is not None
        connection.settings_dict['NAME'] = original_db
        connection.close()
        return exists
    except Exception:
        return False


def _drop_test_database(connection, test_db_name: str, verbosity: int = 0) -> None:
    try:
        original_db = connection.settings_dict['NAME']
        connection.settings_dict['NAME'] = 'postgres'
        connection.close()
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT pg_terminate_backend(pg_stat_activity.pid)
                FROM pg_stat_activity
                WHERE pg_stat_activity.datname = %s
                AND pid <> pg_backend_pid()
                """,
                [test_db_name],
            )
            cursor.execute(f'DROP DATABASE IF EXISTS "{test_db_name}"')
        connection.settings_dict['NAME'] = original_db
        connection.close()
        if verbosity >= 1:
            sys.stderr.write(f"✅ Removed old test database: {test_db_name}\n")
    except Exception as e:
        if verbosity >= 2:
            sys.stderr.write(f"⚠️  Could not remove old test database {test_db_name}: {e}\n")
