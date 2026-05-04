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
            # autoclobber=True: always drop any leftover test DB from a previous
            # interrupted run — no interactive prompt in CI.
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

    except Exception:
        # Never break test collection if the patch fails
        pass
