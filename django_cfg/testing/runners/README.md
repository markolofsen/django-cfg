# django-cfg Test Runners

Drop-in test runner replacements that handle PostgreSQL-specific setup automatically.

## Files

| File | Purpose |
|------|---------|
| `smart.py` | `SmartTestRunner` — full PostgreSQL runner with pool cleanup, extension install, migration patching |
| `fast.py` | `FastTestRunner` — switches all DBs to SQLite in-memory for fast unit tests |
| `utils.py` | Standalone helper functions (pool cleanup, extension install, DB cleanup) |
| `__init__.py` | Re-exports `SmartTestRunner` and `FastTestRunner` for backward-compatible imports |

## Usage

### SmartTestRunner (default for PostgreSQL projects)

Auto-configured by django-cfg. To use manually:

```python
# settings.py
TEST_RUNNER = 'django_cfg.testing.runners.SmartTestRunner'
```

```bash
python manage.py test --testrunner=django_cfg.testing.runners.SmartTestRunner
```

**What it does automatically:**
1. Destroys psycopg3 connection pools before test DB setup (prevents stale connections to wrong DB)
2. Drops old test databases without confirmation (fixes `EOFError` in CI)
3. Installs PostgreSQL extensions (`pgvector`, `pg_trgm`, `unaccent`) right after `CREATE DATABASE`, before `migrate`
4. Patches `MigrationLoader.check_consistent_history` to tolerate `InconsistentMigrationHistory`
5. Suppresses `StateApps` lazy-reference "isn't installed" errors during migration state snapshots
6. Terminates remaining PostgreSQL sessions before `DROP DATABASE` on teardown

### FastTestRunner (unit tests without PostgreSQL features)

```bash
python manage.py test --testrunner=django_cfg.testing.runners.FastTestRunner
```

Switches all database connections to SQLite `:memory:` before running tests. Useful when you only need Django ORM and don't care about PostgreSQL-specific behaviour.

---

## utils.py Reference

Standalone functions — can be used outside the runner classes:

```python
from django_cfg.testing.runners.utils import (
    close_all_pools,           # Destroy psycopg3 pools + clear OPTIONS['pool']
    close_all_connections,     # Force-close without destroying pools
    install_extensions_on,     # Install pgvector/pg_trgm/unaccent on one connection
    install_all_extensions,    # Same, for all connections
    cleanup_old_test_databases,  # Drop existing test DBs silently
    terminate_sessions_on_test_dbs,  # Kill PG sessions before teardown
    get_test_db_name,          # Resolve test DB name from connection settings
)
```
