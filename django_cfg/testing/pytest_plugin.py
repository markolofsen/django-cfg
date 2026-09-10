"""
pytest plugin for django-cfg.

Patches Django's BaseDatabaseCreation.create_test_db to install PostgreSQL
extensions (pgvector, pg_trgm, unaccent) AFTER the empty DB is created but
BEFORE migrations run — identical to what SmartTestRunner does for
`python manage.py test`.

Activated by adding to conftest.py:
    pytest_plugins = ["django_cfg.testing.pytest_plugin"]
"""

import sys


def pytest_configure(config):  # noqa: ARG001
    """
    Patch BaseDatabaseCreation as early as possible.

    pytest_configure runs before any test collection or DB setup,
    so the patch is in place when pytest-django calls create_test_db.
    """
    try:
        from django.db.backends.base.creation import BaseDatabaseCreation
        from .runners.utils import install_extensions_on

        original_create_test_db = BaseDatabaseCreation.create_test_db

        def patched_create_test_db(
            self, verbosity=1, autoclobber=False, serialize=True, keepdb=False
        ):
            # Step 1: create the empty DB (no migrations yet).
            #
            # Close EVERY connection first, not just this alias'. Dropping a
            # database Postgres still has sessions on fails with `is being
            # accessed by other users`, and a project with two aliases holds a
            # connection on the other one while this alias is being set up — so
            # `--create-db` conflicted with the very process running it.
            # `self.connection.close()` below cannot help: it runs after the
            # drop, and only for this alias.
            from django.db import connections as _all_connections

            for _alias in _all_connections:
                _all_connections[_alias].close()

            # autoclobber=True: always drop any leftover test DB from a previous
            # interrupted run rather than prompting. A prompt here would hang
            # any non-interactive run.
            test_db_name = self._create_test_db(verbosity, True, keepdb)
            self.connection.settings_dict["NAME"] = test_db_name
            self.connection.close()

            # Step 2: install extensions while DB is empty
            try:
                install_extensions_on(self.connection, verbosity=verbosity)
            except Exception as e:
                if verbosity >= 2:
                    sys.stderr.write(
                        f"⚠️  Could not install extensions on {test_db_name}: {e}\n"
                    )

            self.connection.settings_dict["NAME"] = test_db_name
            self.connection.close()

            # Step 3: run the original create_test_db (migrations etc.)
            # _create_test_db already ran above — replace it with a no-op so
            # original_create_test_db skips DB creation but still runs migrations.
            original_inner = self._create_test_db
            self._create_test_db = lambda *_, **__: test_db_name
            try:
                return original_create_test_db(
                    self,
                    verbosity=verbosity,
                    autoclobber=autoclobber,
                    serialize=serialize,
                    keepdb=keepdb,
                )
            finally:
                self._create_test_db = original_inner

        BaseDatabaseCreation.create_test_db = patched_create_test_db

    except Exception as e:
        # Never break test collection if the patch fails — but say so. Silently
        # skipping leaves the extensions uninstalled, and the run then fails
        # later somewhere that looks unrelated to this patch.
        sys.stderr.write(f"⚠️  django-cfg pytest patch not applied: {e!r}\n")
