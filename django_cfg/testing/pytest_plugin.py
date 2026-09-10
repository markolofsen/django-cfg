"""
pytest plugin for django-cfg.

Installs the PostgreSQL extensions (pgvector, pg_trgm, unaccent) that models
may depend on, on the empty test database, BEFORE migrations run — the same
thing SmartTestRunner does for `python manage.py test`.

Activated by adding to conftest.py:
    pytest_plugins = ["django_cfg.testing.pytest_plugin"]
"""

import sys


def pytest_configure(config):  # noqa: ARG001
    """
    Hook the extension install onto `pre_migrate`.

    This used to wrap `BaseDatabaseCreation.create_test_db` and re-implement
    its body around the extension step. That method is load-bearing for two
    things the wrapper broke, both found 2026-09-10:

    - It DROPs the test database. The wrapper closed only the alias being set
      up, so a second alias still held a session and `--create-db` failed
      against its own process with `is being accessed by other users`.
    - `setup_databases` calls it with `serialize=False` and then serializes the
      result itself, afterwards (`django/test/utils.py`). The wrapper's
      `close()` calls invalidated the connection that pass depends on, so
      `_test_serialized_contents` came out absent — and every
      `serialized_rollback=True` test silently restored nothing. A
      `transaction=True` test TRUNCATEs the data-migration rows, and nothing
      put them back.

    `pre_migrate` fires with a usable connection before any migration is
    applied, which is all the extension step ever needed. Django keeps
    ownership of creating, dropping and serializing the database.
    """
    try:
        from django.db.models.signals import pre_migrate

        pre_migrate.connect(_install_extensions, dispatch_uid="django_cfg.test_extensions")
    except Exception as e:
        # Never break collection — but say so. Silently skipping leaves the
        # extensions uninstalled, and the run then fails later somewhere that
        # looks unrelated to this plugin.
        sys.stderr.write(f"⚠️  django-cfg pytest plugin not applied: {e!r}\n")


def _install_extensions(sender, **kwargs):
    """Install extensions on the database about to be migrated.

    `pre_migrate` fires once per app; the SQL is `IF NOT EXISTS` and the
    underlying check is cached, so repeats are cheap and idempotent.
    """
    using = kwargs.get("using")
    if not using:
        return

    from django.db import connections

    from .runners.utils import install_extensions_on

    install_extensions_on(connections[using], verbosity=kwargs.get("verbosity", 0))
