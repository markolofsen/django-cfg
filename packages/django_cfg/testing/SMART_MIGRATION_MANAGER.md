# Smart Migration Manager

Automatic migration error detection and fixing for Django test databases.

## Overview

The Smart Migration Manager automatically fixes common Django migration issues:
- ✅ Inconsistent migration history
- ✅ Dependency order problems
- ✅ Missing PostgreSQL extensions
- ✅ Swappable dependency issues (AUTH_USER_MODEL)

## Features

### 1. Auto-Fix Inconsistent Migrations

**Problem:**
```
InconsistentMigrationHistory: Migration admin.0001_initial is applied
before its dependency django_cfg_accounts.0001_initial on database 'default'.
```

**Solution:**
```python
from django_cfg.management.utils.migration_manager import MigrationManager

manager = MigrationManager(stdout, style, logger)
manager.migrate_test_database('default', auto_fix=True)
```

**What it does:**
1. Detects migration order issues
2. Removes problematic migration records
3. Reapplies migrations in correct order
4. Bypasses consistency checks when needed

### 2. Smart Test Database Migration

**Usage:**
```python
manager = MigrationManager()
manager.migrate_test_database('default')
```

**Automatic fixes:**
- Checks migration consistency
- Fixes dependency order issues
- Installs PostgreSQL extensions (pgvector, pg_trgm, etc.)
- Bypasses swappable dependency bugs

### 3. Migration Consistency Check

**Check if migrations have issues:**
```python
manager = MigrationManager()
has_issues = manager.check_migration_consistency('default')

if has_issues:
    print("⚠️  Inconsistent migrations detected")
    manager.fix_inconsistent_migrations('default')
```

### 4. Manual Fix Inconsistent Migrations

**Manually fix migration order:**
```python
manager = MigrationManager()
manager.fix_inconsistent_migrations('default')
```

**What gets fixed:**
- admin migrations applied before AUTH_USER_MODEL migrations
- Swappable dependency order issues
- Custom user model dependency problems

## Integration with SmartTestRunner

The SmartTestRunner automatically uses the Smart Migration Manager:

```python
# In your tests - no configuration needed!
python manage.py test
```

**Automatic process:**
1. ✅ Removes old test database
2. ✅ Creates fresh test database
3. ✅ Detects migration issues
4. ✅ Auto-fixes inconsistencies
5. ✅ Installs PostgreSQL extensions
6. ✅ Runs migrations with bypass
7. ✅ Runs tests

## Manual Usage

### Command Line

Use the test_db command with the migration manager:

```bash
# Check test database migrations
python manage.py test_db info

# Reset and auto-fix migrations
python manage.py test_db reset --force
```

### Python Code

```python
from django_cfg.management.utils.migration_manager import MigrationManager

# Initialize manager
manager = MigrationManager(stdout=self.stdout, style=self.style)

# Migrate test database with auto-fix
manager.migrate_test_database('default', auto_fix=True)

# Or manually check and fix
if manager.check_migration_consistency('default'):
    manager.fix_inconsistent_migrations('default')
    manager._migrate_with_bypass('default')
```

## How It Works

### 1. Inconsistent Migration Detection

```python
def check_migration_consistency(self, db_name: str) -> bool:
    """
    Checks migration loader for inconsistency errors.
    Returns True if issues found.
    """
    try:
        loader.check_consistent_history(connection)
        return False  # No issues
    except InconsistentMigrationHistory:
        return True  # Has issues
```

### 2. Auto-Fix Algorithm

```python
def fix_inconsistent_migrations(self, db_name: str):
    """
    1. Get all applied migrations from database
    2. Find problematic migrations (e.g., admin before auth)
    3. Remove problematic migration records
    4. Let Django reapply them in correct order
    """
    # Example: admin before django_cfg_accounts
    if admin_min_id < auth_min_id:
        # Remove admin migration records
        recorder.migration_qs.filter(app='admin').delete()
        # Will be reapplied correctly during migration
```

### 3. Migration Bypass

```python
def _migrate_with_bypass(self, db_name: str):
    """
    Temporarily patch check_consistent_history to bypass errors.
    """
    # Patch Django's consistency check
    original_check = MigrationLoader.check_consistent_history

    def patched_check(self, connection):
        try:
            return original_check(self, connection)
        except InconsistentMigrationHistory:
            # Log warning but don't fail
            return

    MigrationLoader.check_consistent_history = patched_check

    try:
        call_command("migrate", database=db_name)
    finally:
        MigrationLoader.check_consistent_history = original_check
```

## Common Issues Fixed

### Issue 1: Admin Before Custom User Model

**Problem:**
```
Migration admin.0001_initial is applied before its dependency
django_cfg_accounts.0001_initial
```

**Cause:**
- admin.0001_initial depends on AUTH_USER_MODEL
- AUTH_USER_MODEL = 'django_cfg_accounts.CustomUser'
- Django applies admin migrations before custom user migrations

**Fix:**
```python
manager.fix_inconsistent_migrations('default')
# Removes admin migration records
# Django reapplies them after django_cfg_accounts
```

### Issue 2: Missing PostgreSQL Extensions

**Problem:**
```
type "vector" does not exist
```

**Fix:**
```python
manager.migrate_test_database('default')
# Automatically installs pgvector before migrations
```

### Issue 3: Swappable Dependency Order

**Problem:**
Django doesn't always respect swappable_dependency() order when creating test databases.

**Fix:**
```python
# SmartTestRunner automatically bypasses consistency check
# and reorders migrations correctly
```

## API Reference

### MigrationManager

```python
class MigrationManager:
    def __init__(self, stdout=None, style=None, logger=None):
        """Initialize migration manager."""

    def migrate_test_database(self, db_name: str, auto_fix: bool = True):
        """
        Migrate test database with automatic error fixing.

        Args:
            db_name: Database alias
            auto_fix: Automatically fix errors (default: True)
        """

    def check_migration_consistency(self, db_name: str) -> bool:
        """
        Check if migrations are consistent.

        Returns:
            True if issues found, False if consistent
        """

    def fix_inconsistent_migrations(self, db_name: str):
        """
        Automatically fix inconsistent migration history.
        """

    def _migrate_with_bypass(self, db_name: str):
        """
        Run migrations with consistency check bypass.
        """
```

## Examples

### Example 1: Fix Test Database Before Tests

```python
from django.test import TestCase
from django_cfg.management.utils.migration_manager import MigrationManager

class MyTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        # Ensure migrations are consistent
        manager = MigrationManager()
        if manager.check_migration_consistency('default'):
            manager.fix_inconsistent_migrations('default')
```

### Example 2: Custom Management Command

```python
from django.core.management.base import BaseCommand
from django_cfg.management.utils.migration_manager import MigrationManager

class Command(BaseCommand):
    def handle(self, *args, **options):
        manager = MigrationManager(self.stdout, self.style)

        # Migrate with auto-fix
        manager.migrate_test_database('default', auto_fix=True)
```

### Example 3: CI/CD Pipeline

```yaml
# GitHub Actions
- name: Setup Test Database
  run: |
    poetry run python manage.py test_db cleanup --force
    poetry run python manage.py test_db reset --force

- name: Run Tests
  run: poetry run python manage.py test
  # SmartTestRunner automatically handles any remaining issues
```

## Troubleshooting

### Migration Still Failing?

1. **Check migration files exist:**
   ```bash
   find . -name "0001_initial.py" -path "*/migrations/*"
   ```

2. **Verify AUTH_USER_MODEL:**
   ```python
   from django.conf import settings
   print(settings.AUTH_USER_MODEL)
   ```

3. **Manually fix:**
   ```bash
   python manage.py test_db reset --force
   ```

### Extensions Not Installing?

```bash
# Check if pgvector is needed
python manage.py test_db check-extensions

# Install system dependencies
sudo apt-get install postgresql-15-pgvector
```

### Still Getting InconsistentMigrationHistory?

The migration might be in the main database, not test database:

```bash
# Check main database migrations
python manage.py dbshell
SELECT id, app, name FROM django_migrations
WHERE app IN ('admin', 'django_cfg_accounts')
ORDER BY id;
```

## Configuration

### Enable/Disable Auto-Fix

```python
# Disable auto-fix (errors will fail)
manager.migrate_test_database('default', auto_fix=False)

# Enable auto-fix (default)
manager.migrate_test_database('default', auto_fix=True)
```

### Custom Error Handling

```python
from django_cfg.management.utils.migration_manager import MigrationManager

manager = MigrationManager()

try:
    manager.migrate_test_database('default')
except Exception as e:
    # Custom error handling
    print(f"Migration failed: {e}")
    # Try manual fix
    manager.fix_inconsistent_migrations('default')
```

## Best Practices

1. **Always use auto_fix=True in tests** (default)
2. **Run test_db cleanup regularly** to avoid stale databases
3. **Check consistency before important migrations**
4. **Use test_db reset for fresh start**
5. **Monitor migration order in CI/CD**

## See Also

- [SmartTestRunner Documentation](TESTING_ZERO_CONFIG.md)
- [test_db Command](TEST_DB_COMMAND.md)
- [Zero-Config Testing](TESTING_ZERO_CONFIG.md)
