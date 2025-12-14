# test_db Management Command

A powerful Django management command for managing test databases.

## Overview

The `test_db` command provides utilities for managing test databases:
- **cleanup**: Remove old test databases
- **info**: Show test database information
- **reset**: Drop and recreate test database
- **check-extensions**: Check PostgreSQL extensions

## Usage

### Show Test Database Info

```bash
# Info for default database
python manage.py test_db info

# Info for all databases
python manage.py test_db info --all

# JSON output
python manage.py test_db info --json
```

**Output:**
```
======================================================================
         TEST DATABASE INFORMATION
======================================================================

Database Alias: default
  Test DB Name:    test_cmdop
  Status:          ✅ EXISTS
  Size:            11 MB
  Extensions:      None
  Engine:          django.db.backends.postgresql

======================================================================
```

### Cleanup Test Databases

Remove old test databases (useful for cleaning up after failed test runs):

```bash
# Cleanup default database (with confirmation)
python manage.py test_db cleanup

# Cleanup all databases
python manage.py test_db cleanup --all

# Force cleanup without confirmation
python manage.py test_db cleanup --force

# Cleanup all databases without confirmation
python manage.py test_db cleanup --all --force
```

**Output:**
```
======================================================================
         TEST DATABASE CLEANUP
======================================================================

Found 2 test database(s):
  • test_cmdop (alias: default)
  • test_analytics (alias: analytics)

⚠️  Remove these databases? [y/N]: y

✅ Removed: test_cmdop
✅ Removed: test_analytics

======================================================================
✅ Cleanup complete: 2/2 databases removed
```

### Reset Test Database

Drop and recreate test database from scratch:

```bash
# Reset default database (with confirmation)
python manage.py test_db reset

# Reset specific database
python manage.py test_db reset --database=analytics

# Force reset without confirmation
python manage.py test_db reset --force
```

**Output:**
```
======================================================================
         RESET TEST DATABASE
======================================================================

Database: test_cmdop (alias: default)
Status:   EXISTS

⚠️  This will DROP and recreate the test database. Continue? [y/N]: y

✅ Dropped: test_cmdop
✅ Created: test_cmdop
✅ Installed extensions

======================================================================
✅ Test database reset complete
```

### Check PostgreSQL Extensions

Check which extensions are installed in test database:

```bash
# Check extensions for default database
python manage.py test_db check-extensions

# Check specific database
python manage.py test_db check-extensions --database=analytics

# JSON output
python manage.py test_db check-extensions --json
```

**Output:**
```
======================================================================
         TEST DATABASE EXTENSIONS
======================================================================

Database: test_cmdop

Installed Extensions:
  (none)

Required Extensions:
  ❌ vector (missing)
  ❌ pg_trgm (missing)
  ❌ unaccent (missing)

======================================================================
```

## Command Options

### Common Options

| Option | Description |
|--------|-------------|
| `--database DATABASE` | Database alias (default: `default`) |
| `--all` | Apply to all databases |
| `--force` | Force action without confirmation |
| `--json` | Output in JSON format |

### Actions

| Action | Description |
|--------|-------------|
| `cleanup` | Remove all test databases |
| `info` | Show test database information |
| `reset` | Drop and recreate test database |
| `check-extensions` | Check PostgreSQL extensions |

## Use Cases

### 1. Clean Up After Failed Tests

When tests fail and leave orphaned test databases:

```bash
python manage.py test_db cleanup --all --force
```

### 2. Fresh Start for Testing

Reset test database to clean state:

```bash
python manage.py test_db reset --force
```

### 3. Verify Extensions

Check if required extensions are installed:

```bash
python manage.py test_db check-extensions
```

If missing, run tests with SmartTestRunner to auto-install:

```bash
python manage.py test
```

### 4. CI/CD Integration

In CI/CD pipelines, cleanup before tests:

```yaml
# GitHub Actions example
- name: Cleanup Test Databases
  run: poetry run python manage.py test_db cleanup --all --force

- name: Run Tests
  run: poetry run python manage.py test
```

### 5. Development Workflow

Check test database status:

```bash
# Quick info
python manage.py test_db info

# Detailed check
python manage.py test_db check-extensions
```

## JSON Output

All commands support `--json` flag for programmatic use:

### Info JSON Output

```bash
python manage.py test_db info --json
```

```json
[
  {
    "alias": "default",
    "test_db_name": "test_cmdop",
    "exists": true,
    "engine": "django.db.backends.postgresql",
    "size": "11 MB",
    "extensions": []
  }
]
```

### Check Extensions JSON Output

```bash
python manage.py test_db check-extensions --json
```

```json
{
  "test_db_name": "test_cmdop",
  "installed_extensions": [],
  "needs_pgvector": true
}
```

## Integration with SmartTestRunner

The `test_db` command works seamlessly with django-cfg's SmartTestRunner:

1. **Before tests**: Use `test_db cleanup` to remove old databases
2. **During tests**: SmartTestRunner automatically creates and configures test DB
3. **After tests**: Use `test_db info` to inspect test database
4. **Troubleshooting**: Use `test_db check-extensions` to verify setup

## Examples

### Complete Test Workflow

```bash
# 1. Cleanup old test databases
python manage.py test_db cleanup --force

# 2. Run tests (SmartTestRunner handles everything)
python manage.py test

# 3. Check what was created
python manage.py test_db info

# 4. Verify extensions
python manage.py test_db check-extensions
```

### Multi-Database Setup

```bash
# Show info for all databases
python manage.py test_db info --all

# Cleanup all test databases
python manage.py test_db cleanup --all --force

# Reset specific database
python manage.py test_db reset --database=analytics
```

### Debugging Test Database Issues

```bash
# 1. Check current status
python manage.py test_db info

# 2. Check extensions
python manage.py test_db check-extensions

# 3. If issues found, reset
python manage.py test_db reset --force

# 4. Run tests again
python manage.py test
```

## Tips

1. **Always use `--force` in CI/CD** to avoid interactive prompts
2. **Use `--all` for cleanup** to remove all test databases at once
3. **Check JSON output** for programmatic parsing
4. **Reset on migration issues** when test migrations are inconsistent
5. **Cleanup regularly** to save disk space

## See Also

- [SmartTestRunner Documentation](TESTING_ZERO_CONFIG.md)
- [Zero-Config Test Database Management](TESTING_ZERO_CONFIG.md)
- Django Testing Documentation
