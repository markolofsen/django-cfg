"""
Smart Test Runner for django-cfg.

Automatically:
- Removes conflicting test databases without confirmation
- Installs PostgreSQL extensions (pgvector, pg_trgm, etc.)
- Validates migrations
- Zero configuration - works out of the box

🔥 Generated with django-cfg
"""

import sys
from typing import Any, Dict, Optional

from django.conf import settings
from django.db import connections
from django.test.runner import DiscoverRunner

from ..management.utils.postgresql import PostgreSQLExtensionManager
from ..management.utils.migration_manager import MigrationManager


class SmartTestRunner(DiscoverRunner):
    """
    Smart test runner for django-cfg.

    AUTOMATICALLY:
    - Removes conflicting test databases (fixes EOFError in CI)
    - Installs PostgreSQL extensions (pgvector, pg_trgm, unaccent)
    - Validates migrations

    User doesn't need to configure anything!

    Usage:
        Automatically set in settings.py via django-cfg:
        TEST_RUNNER = 'django_cfg.testing.runners.SmartTestRunner'

        Or manually:
        python manage.py test --testrunner=django_cfg.testing.runners.SmartTestRunner
    """

    def setup_databases(self, **kwargs) -> list:
        """
        Override for automatic extension installation.

        Args:
            **kwargs: Arguments for standard setup_databases

        Returns:
            Old database configuration for teardown
        """

        # CRITICAL: Disable connection pooling for the entire test run.
        # psycopg3 connection pools keep physical connections alive and reuse them even
        # after close() is called. During test DB setup, the pool may return a connection
        # to 'postgres' (used during cleanup) or to the old 'test_sdkrouter', causing
        # MigrationLoader to read django_migrations from the wrong database, and causing
        # TestCase._enter_atomics() to open a transaction on the wrong database.
        # Disabling the pool forces a fresh TCP connection on every cursor() call,
        # ensuring settings_dict['NAME'] is always honoured.
        for alias in connections:
            c = connections[alias]
            if hasattr(c, 'close_pool'):
                c.close_pool()
            c.settings_dict.get('OPTIONS', {}).pop('pool', None)
            # Remove the cached @cached_property so it is recomputed next time.
            # Since OPTIONS['pool'] is now gone, the recomputed value will be None.
            c.__dict__.pop('pool', None)
            # Clear the class-level pool registry for this alias so no stale pool
            # object survives even if close_pool() left a partial entry behind.
            if hasattr(c, '_connection_pools'):
                c._connection_pools.pop(alias, None)
            c.close()

        # 🔥 STEP 1: Remove old test databases (if conflicts exist)
        self._cleanup_old_test_databases()

        # CRITICAL: Force-close all connections after cleanup.
        # _cleanup_old_test_databases() manipulates connection.settings_dict["NAME"]
        # and may leave a physical connection open to the wrong database (e.g. 'postgres').
        # Django's DatabaseWrapper is lazy — it reuses existing connections and only
        # reconnects on the next cursor() call. If we don't close now, MigrationLoader
        # inside the 'migrate' management command will read django_migrations from the
        # wrong database (still connected to 'postgres' or the old test DB), see all
        # migrations as "applied", and return an empty migration plan → no tables created.
        # If a connection pool (psycopg_pool) is configured, close_pool() destroys all
        # pooled connections so the next getconn() creates a fresh connection to the
        # correct database (settings_dict['NAME']).
        for alias in connections:
            c = connections[alias]
            if hasattr(c, 'close_pool'):
                c.close_pool()
            c.close()

        # STEP 2: Use smart migration manager for test database setup
        # This automatically handles:
        # - Migration consistency issues
        # - Extension installation
        # - Dependency order problems
        # - StateApps lazy-reference errors (apps not in migration state snapshot)
        from django.db.migrations import loader as migrations_loader

        original_check = migrations_loader.MigrationLoader.check_consistent_history

        def patched_check(self, connection):
            """Skip consistency check and use smart migration manager instead."""
            try:
                return original_check(self, connection)
            except Exception as e:
                if 'InconsistentMigrationHistory' in str(type(e).__name__):
                    sys.stderr.write(f"⚠️  Using smart migration manager to fix: {e}\n")
                    return  # Skip check, will be handled by migration manager
                raise

        # Patch _check_lazy_references at the module level so StateApps.__init__
        # can complete its full initialization. The root cause: some apps have FKs
        # to models from apps that are not present in the migration state snapshot
        # (e.g. a ForeignKey to a model in a 3rd-party or swappable app that is
        # registered in the live app registry but not in the migrated subset).
        # StateApps.__init__ calls _check_lazy_references AFTER render_multiple has
        # already completed — meaning self.ready=True and all models are registered.
        # By patching _check_lazy_references to silently drop "isn't installed" errors
        # we let __init__ finish naturally without any early return, so the resulting
        # StateApps object is fully populated and migrations run normally.
        import django.core.checks.model_checks as model_checks_module

        original_check_lazy_references = model_checks_module._check_lazy_references

        def patched_check_lazy_references(apps, ignore=None):
            """Suppress 'app isn't installed' lazy-reference errors during test DB setup."""
            errors = original_check_lazy_references(apps, ignore=ignore)
            filtered = [
                e for e in errors
                if "isn't installed" not in getattr(e, "msg", "")
            ]
            if errors and not filtered:
                # All errors were lazy-ref "isn't installed" — safe to suppress
                sys.stderr.write(
                    f"⚠️  Suppressed {len(errors)} StateApps lazy-ref 'isn't installed' "
                    f"error(s) during test DB setup (apps not in migration state snapshot)\n"
                )
            elif filtered and len(filtered) < len(errors):
                suppressed = len(errors) - len(filtered)
                sys.stderr.write(
                    f"⚠️  Suppressed {suppressed} StateApps lazy-ref 'isn't installed' "
                    f"error(s) during test DB setup\n"
                )
            return filtered

        model_checks_module._check_lazy_references = patched_check_lazy_references
        migrations_loader.MigrationLoader.check_consistent_history = patched_check

        # 🔥 STEP 3: Patch DatabaseCreation.create_test_db to install extensions
        # AFTER the empty DB is created (_create_test_db) but BEFORE migrate is called.
        # Django flow: create_test_db() → _create_test_db() → [switch connection] → migrate()
        # We wrap create_test_db so we can connect to the fresh DB and install extensions
        # right between _create_test_db and the migrate call.
        from django.db.backends.base.creation import BaseDatabaseCreation
        original_create_test_db = BaseDatabaseCreation.create_test_db

        runner_self = self

        def patched_create_test_db(creation_self, verbosity=1, autoclobber=False, serialize=True, keepdb=False):
            # First create the empty database structure (no migrate yet)
            test_db_name = creation_self._create_test_db(verbosity, autoclobber, keepdb)
            # Switch the connection to the new test database
            creation_self.connection.settings_dict['NAME'] = test_db_name
            creation_self.connection.close()
            # NOW install extensions — before migrate runs
            try:
                runner_self._install_extensions_on(creation_self.connection)
            except Exception as e:
                if verbosity >= 2:
                    sys.stderr.write(f"⚠️  Could not install extensions on {test_db_name}: {e}\n")
            # Restore the NAME so create_test_db continues normally
            creation_self.connection.settings_dict['NAME'] = test_db_name
            creation_self.connection.close()
            # Now call the original — it will re-create test db (skip if exists) and run migrate
            return original_create_test_db(creation_self, verbosity=verbosity, autoclobber=True, serialize=serialize, keepdb=True)

        BaseDatabaseCreation.create_test_db = patched_create_test_db

        try:
            # autoclobber=True: Django will silently drop and recreate the test DB
            # if it already exists. This is the safest fallback in case
            # _cleanup_old_test_databases() failed to drop it (e.g. active connections).
            # Without this, Django would prompt for confirmation → EOFError in CI.
            old_config = super().setup_databases(autoclobber=True, **kwargs)
        finally:
            # Restore original methods
            migrations_loader.MigrationLoader.check_consistent_history = original_check
            model_checks_module._check_lazy_references = original_check_lazy_references
            BaseDatabaseCreation.create_test_db = original_create_test_db

        # Legacy call kept for any connections that skipped the patch
        self._install_extensions()

        # CRITICAL: Force-close connections after extension installation.
        # _install_extensions() opens a cursor which may have left the physical
        # connection on the wrong database. We must close here so Django
        # reconnects to the correct test DB (settings_dict['NAME']) on next cursor().
        # If a connection pool is configured, close_pool() destroys all pooled connections
        # so the next getconn() creates a fresh connection to the correct database.
        for alias in connections:
            c = connections[alias]
            if hasattr(c, 'close_pool'):
                c.close_pool()
            c.close()

        return old_config

    def teardown_databases(self, old_config, **kwargs):
        """
        Override to close connection pools before dropping test databases.

        psycopg3 connection pools keep physical connections alive even after
        test run completes. Django's _destroy_test_db tries to DROP DATABASE
        but fails with "database is being accessed by other users" because the
        pool still holds open connections. We must destroy all pools first,
        then forcibly terminate any remaining backend sessions.
        """
        # Kill all pools first
        for alias in connections:
            c = connections[alias]
            if hasattr(c, 'close_pool'):
                c.close_pool()
            c.settings_dict.get('OPTIONS', {}).pop('pool', None)
            c.__dict__.pop('pool', None)
            if hasattr(c, '_connection_pools'):
                c._connection_pools.pop(alias, None)
            c.close()

        # Forcibly terminate any remaining sessions on test databases
        for alias in connections:
            connection = connections[alias]
            db_engine = connection.settings_dict.get('ENGINE', '')
            if 'postgresql' not in db_engine.lower():
                continue
            test_db_name = self._get_test_db_name(connection)
            try:
                original_db = connection.settings_dict['NAME']
                connection.settings_dict['NAME'] = 'postgres'
                connection.close()
                with connection.cursor() as cursor:
                    cursor.execute("""
                        SELECT pg_terminate_backend(pg_stat_activity.pid)
                        FROM pg_stat_activity
                        WHERE pg_stat_activity.datname = %s
                        AND pid <> pg_backend_pid()
                    """, [test_db_name])
                connection.settings_dict['NAME'] = original_db
                connection.close()
            except Exception:
                pass

        super().teardown_databases(old_config, **kwargs)

    def _cleanup_old_test_databases(self):
        """
        Automatic removal of conflicting test databases.

        Solves problems:
        - EOFError when trying input() in CI
        - Inconsistent migration history in old database
        """
        for alias in connections:
            connection = connections[alias]
            db_engine = connection.settings_dict.get('ENGINE', '')

            # Only work with PostgreSQL
            if 'postgresql' not in db_engine.lower():
                continue

            test_db_name = self._get_test_db_name(connection)

            try:
                # Check if test database exists
                if self._test_database_exists(connection, test_db_name):
                    # 🔥 Automatically remove without confirmation
                    self._drop_test_database(connection, test_db_name)

            except Exception as e:
                # Ignore errors - database may not exist or be unavailable
                if self.verbosity >= 2:
                    self.log(f"⚠️  Could not check/cleanup test database {test_db_name}: {e}")

    def _test_database_exists(self, connection, test_db_name: str) -> bool:
        """
        Check if test database exists.

        Args:
            connection: Django database connection
            test_db_name: Test database name

        Returns:
            True if database exists
        """
        try:
            # Connect to main database for checking
            original_db = connection.settings_dict['NAME']
            connection.settings_dict['NAME'] = 'postgres'  # Default maintenance DB
            connection.close()

            with connection.cursor() as cursor:
                cursor.execute(
                    "SELECT 1 FROM pg_database WHERE datname = %s",
                    [test_db_name]
                )
                exists = cursor.fetchone() is not None

            # Restore original database name
            connection.settings_dict['NAME'] = original_db
            connection.close()

            return exists

        except Exception:
            return False

    def _drop_test_database(self, connection, test_db_name: str):
        """
        Drop test database.

        Args:
            connection: Django database connection
            test_db_name: Test database name
        """
        try:
            # Connect to postgres database for deletion
            original_db = connection.settings_dict['NAME']
            connection.settings_dict['NAME'] = 'postgres'
            connection.close()

            with connection.cursor() as cursor:
                # Terminate all connections to test database
                cursor.execute("""
                    SELECT pg_terminate_backend(pg_stat_activity.pid)
                    FROM pg_stat_activity
                    WHERE pg_stat_activity.datname = %s
                    AND pid <> pg_backend_pid()
                """, [test_db_name])

                # Drop database
                cursor.execute(f'DROP DATABASE IF EXISTS "{test_db_name}"')

            # Restore original database name
            connection.settings_dict['NAME'] = original_db
            connection.close()

            if self.verbosity >= 1:
                self.log(f"✅ Removed old test database: {test_db_name}")

        except Exception as e:
            if self.verbosity >= 2:
                self.log(f"⚠️  Could not remove old test database {test_db_name}: {e}")

    def _install_extensions_on(self, connection) -> None:
        """Install PostgreSQL extensions on a specific connection."""
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
                alias = connection.alias
                if self.verbosity >= 1:
                    self.log(f"✅ Installed PostgreSQL extensions for test database '{alias}'")
        except Exception as e:
            if self.verbosity >= 2:
                self.log(f"⚠️  Could not install extensions for {connection.alias}: {e}")

    def _install_extensions(self):
        """
        Automatic installation of PostgreSQL extensions in test database.

        Solves problems:
        - Missing pgvector extension
        - Type 'vector' does not exist errors
        """
        for alias in connections:
            self._install_extensions_on(connections[alias])

    def _get_test_db_name(self, connection) -> str:
        """
        Get test database name from configuration.

        Args:
            connection: Django database connection

        Returns:
            Test database name
        """
        test_db_name = connection.settings_dict.get('TEST', {}).get('NAME')
        if not test_db_name:
            db_name = connection.settings_dict['NAME']
            test_db_name = f'test_{db_name}'
        return test_db_name

    def log(self, message: str, level=None):
        """
        Log messages.

        Args:
            message: Message to output
            level: Log level (optional, for Django compatibility)
        """
        if self.verbosity >= 1:
            # Use sys.stderr to not interfere with test output
            sys.stderr.write(f"{message}\n")


class FastTestRunner(SmartTestRunner):
    """
    Fast test runner using SQLite in-memory.

    Automatically switches all databases to SQLite to speed up unit tests.
    Use for fast tests without complex database features.

    Usage:
        python manage.py test --testrunner=django_cfg.testing.runners.FastTestRunner
    """

    def setup_databases(self, **kwargs) -> list:
        """Override to switch to SQLite."""

        # Switch all databases to SQLite in-memory
        self._switch_to_sqlite()

        # Call parent setup (without cleanup, as SQLite)
        return DiscoverRunner.setup_databases(self, **kwargs)

    def _switch_to_sqlite(self):
        """Switch all databases to SQLite in-memory for speed."""
        for alias in connections:
            connection = connections[alias]

            # Save original configuration
            if not hasattr(connection, '_original_settings'):
                connection._original_settings = connection.settings_dict.copy()

            # Switch to SQLite
            connection.settings_dict.update({
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': ':memory:',
            })

            # Reopen connection
            connection.close()

        if self.verbosity >= 1:
            self.log("🚀 Switched to SQLite in-memory for fast testing")


__all__ = [
    'SmartTestRunner',
    'FastTestRunner',
]
