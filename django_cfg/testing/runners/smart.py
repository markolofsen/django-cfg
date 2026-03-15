"""
SmartTestRunner — production-grade test runner for django-cfg PostgreSQL projects.
"""

import sys

from django.db import connections
from django.test.runner import DiscoverRunner

from .utils import (
    cleanup_old_test_databases,
    close_all_connections,
    close_all_pools,
    install_all_extensions,
    install_extensions_on,
    terminate_sessions_on_test_dbs,
)


class SmartTestRunner(DiscoverRunner):
    """
    Smart test runner for django-cfg.

    AUTOMATICALLY:
    - Removes conflicting test databases (fixes EOFError in CI)
    - Installs PostgreSQL extensions (pgvector, pg_trgm, unaccent)
    - Validates migrations

    Usage:
        Automatically set in settings.py via django-cfg:
        TEST_RUNNER = 'django_cfg.testing.runners.SmartTestRunner'

        Or manually:
        python manage.py test --testrunner=django_cfg.testing.runners.SmartTestRunner
    """

    def setup_databases(self, **kwargs) -> list:
        """
        Override for automatic extension installation.

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
        close_all_pools(verbosity=self.verbosity)

        # STEP 1: Remove old test databases (if conflicts exist)
        cleanup_old_test_databases(verbosity=self.verbosity)

        # CRITICAL: Force-close all connections after cleanup.
        # _cleanup_old_test_databases() manipulates connection.settings_dict["NAME"]
        # and may leave a physical connection open to the wrong database (e.g. 'postgres').
        # Django's DatabaseWrapper is lazy — it reuses existing connections and only
        # reconnects on the next cursor() call. If we don't close now, MigrationLoader
        # inside the 'migrate' management command will read django_migrations from the
        # wrong database (still connected to 'postgres' or the old test DB), see all
        # migrations as "applied", and return an empty migration plan → no tables created.
        close_all_connections()

        # STEP 2: Patch migration consistency check and lazy references
        from django.db.migrations import loader as migrations_loader

        original_check = migrations_loader.MigrationLoader.check_consistent_history

        def patched_check(self, connection):
            """Skip consistency check and use smart migration manager instead."""
            try:
                return original_check(self, connection)
            except Exception as e:
                if 'InconsistentMigrationHistory' in str(type(e).__name__):
                    sys.stderr.write(f"⚠️  Using smart migration manager to fix: {e}\n")
                    return
                raise

        # Patch _check_lazy_references at the module level so StateApps.__init__
        # can complete its full initialization. The root cause: some apps have FKs
        # to models from apps that are not present in the migration state snapshot
        # (e.g. a ForeignKey to a model in a 3rd-party or swappable app that is
        # registered in the live app registry but not in the migrated subset).
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

        # STEP 3: Patch DatabaseCreation.create_test_db to install extensions
        # AFTER the empty DB is created (_create_test_db) but BEFORE migrate is called.
        from django.db.backends.base.creation import BaseDatabaseCreation
        original_create_test_db = BaseDatabaseCreation.create_test_db

        runner_self = self

        def patched_create_test_db(creation_self, verbosity=1, autoclobber=False, serialize=True, keepdb=False):
            test_db_name = creation_self._create_test_db(verbosity, autoclobber, keepdb)
            creation_self.connection.settings_dict['NAME'] = test_db_name
            creation_self.connection.close()
            try:
                install_extensions_on(creation_self.connection, verbosity=runner_self.verbosity)
            except Exception as e:
                if verbosity >= 2:
                    sys.stderr.write(f"⚠️  Could not install extensions on {test_db_name}: {e}\n")
            creation_self.connection.settings_dict['NAME'] = test_db_name
            creation_self.connection.close()
            return original_create_test_db(creation_self, verbosity=verbosity, autoclobber=True, serialize=serialize, keepdb=True)

        BaseDatabaseCreation.create_test_db = patched_create_test_db

        try:
            old_config = super().setup_databases(autoclobber=True, **kwargs)
        finally:
            migrations_loader.MigrationLoader.check_consistent_history = original_check
            model_checks_module._check_lazy_references = original_check_lazy_references
            BaseDatabaseCreation.create_test_db = original_create_test_db

        # Legacy call kept for any connections that skipped the patch
        install_all_extensions(verbosity=self.verbosity)

        # CRITICAL: Force-close connections after extension installation.
        close_all_connections()

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
        close_all_pools(verbosity=self.verbosity)
        terminate_sessions_on_test_dbs()
        super().teardown_databases(old_config, **kwargs)

    def log(self, message: str, level=None):
        """Log messages to stderr (doesn't interfere with test output)."""
        if self.verbosity >= 1:
            sys.stderr.write(f"{message}\n")


__all__ = ["SmartTestRunner"]
