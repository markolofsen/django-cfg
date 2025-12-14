# Zero-Config Test Database Management

## Overview

Django-cfg now provides **zero-configuration** test database management. No setup needed - everything works automatically!

## Features

### ✅ Automatic Test Database Cleanup
- Automatically removes conflicting test databases
- No more `EOFError` in CI/CD pipelines
- No interactive prompts during testing

### ✅ PostgreSQL Extension Auto-Installation
- Automatically installs `pgvector`, `pg_trgm`, `unaccent`
- Detects extensions needed by scanning migrations
- Works in test databases without manual configuration

### ✅ Smart Database Selection
- PostgreSQL for integration tests
- SQLite for fast unit tests (optional)
- Automatic TEST settings for all databases

## Usage

### Zero Configuration (Recommended)

Just run your tests - everything is automatic:

```bash
python manage.py test
```

**That's it!** Django-cfg automatically:
1. ✅ Detects you're running tests
2. ✅ Removes old test database (`test_cmdop`) without confirmation
3. ✅ Creates fresh test database
4. ✅ Installs PostgreSQL extensions (pgvector, pg_trgm, etc.)
5. ✅ Applies migrations in correct order
6. ✅ Runs your tests
7. ✅ Cleans up afterward

### Fast Testing with SQLite

For faster unit tests, use the FastTestRunner:

```bash
python manage.py test --testrunner=django_cfg.testing.runners.FastTestRunner
```

This automatically switches all databases to SQLite in-memory for maximum speed.

## How It Works

### 1. Automatic TEST Settings

Django-cfg automatically generates TEST settings for each database:

```python
# In your config.py - NO changes needed!
class MyConfig(DjangoConfig):
    project_name = "cmdop"
    databases = {
        "default": DatabaseConfig.from_url(
            "postgresql://user:pass@localhost/cmdop"
        )
    }
    # That's all! Testing configuration is automatic.
```

Behind the scenes, django-cfg generates:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'cmdop',
        # ... connection settings ...

        # 🔥 Automatically added by django-cfg
        'TEST': {
            'NAME': 'test_cmdop',
            'TEMPLATE': 'template0',  # Clean template without old data
            'CHARSET': 'UTF8',
            'CREATE_DB': True,
            'MIGRATE': True,
        }
    }
}

# 🔥 Automatically set by django-cfg
TEST_RUNNER = 'django_cfg.testing.runners.SmartTestRunner'
```

### 2. SmartTestRunner

The `SmartTestRunner` automatically:

#### Step 1: Cleanup Old Test Databases
```python
# Automatically executed before creating test database
def _cleanup_old_test_databases(self):
    # Check if test database exists
    if test_database_exists('test_cmdop'):
        # Terminate all connections
        # Drop database WITHOUT confirmation
        drop_database('test_cmdop')  # No EOFError!
```

#### Step 2: Install PostgreSQL Extensions
```python
# Automatically executed after creating test database
def _install_extensions(self):
    # Scan migrations for extension usage
    if needs_pgvector():
        # Install extensions in test database
        CREATE EXTENSION IF NOT EXISTS vector;
        CREATE EXTENSION IF NOT EXISTS pg_trgm;
        CREATE EXTENSION IF NOT EXISTS unaccent;
```

### 3. What Gets Fixed

#### Problem 1: EOFError in CI
**Before:**
```
Got an error creating the test database: database "test_cmdop" already exists

Type 'yes' if you would like to try deleting the test database 'test_cmdop', or 'no' to cancel:
EOFError  # ← Fails in CI because no stdin!
```

**After:**
```
✅ Removed old test database: test_cmdop
Creating test database for alias 'default'...
```

#### Problem 2: Missing Extensions
**Before:**
```
django.db.utils.ProgrammingError: type "vector" does not exist
```

**After:**
```
✅ Installed PostgreSQL extensions for test database 'default'
```

#### Problem 3: Inconsistent Migration History
**Before:**
```
Inconsistent migration history
ai_chat.0001_initial applied before workspaces.0002_alter_workspacemember_options
```

**After:**
```
✅ Removed old test database: test_cmdop  # Fresh start!
Running migrations...
  Applying workspaces.0002_alter_workspacemember_options... OK
  Applying ai_chat.0001_initial... OK
```

## Advanced Usage

### Manual Test Runner Selection

#### Smart Test Runner (Default)
```bash
python manage.py test --testrunner=django_cfg.testing.runners.SmartTestRunner
```
- Auto-cleanup old test databases
- PostgreSQL extension installation
- Full database feature support

#### Fast Test Runner
```bash
python manage.py test --testrunner=django_cfg.testing.runners.FastTestRunner
```
- Switches all databases to SQLite in-memory
- 10x faster for unit tests
- No PostgreSQL features

### Importing Test Runners

```python
# Lazy import (recommended)
from django_cfg import SmartTestRunner, FastTestRunner

# Direct import
from django_cfg.testing.runners import SmartTestRunner, FastTestRunner

# In settings.py (if not using django-cfg config)
TEST_RUNNER = 'django_cfg.testing.runners.SmartTestRunner'
```

## CI/CD Integration

### GitHub Actions
```yaml
- name: Run Tests
  run: python manage.py test
  # No special configuration needed!
  # SmartTestRunner handles everything automatically
```

### GitLab CI
```yaml
test:
  script:
    - python manage.py test
  # Works out of the box!
```

### Docker
```dockerfile
# No changes needed to Dockerfile
RUN python manage.py test
```

## Troubleshooting

### Extensions Not Installing?

Check if pgvector is installed on your system:

```bash
# Ubuntu/Debian
sudo apt-get install postgresql-15-pgvector

# macOS
brew install pgvector
```

### Want More Verbosity?

```bash
python manage.py test --verbosity=2
```

Output:
```
✅ Removed old test database: test_cmdop
Creating test database for alias 'default'...
✅ Installed PostgreSQL extensions for test database 'default'
...
```

### Disable Auto-Cleanup (Not Recommended)

If you really need to keep the test database:

```python
# Custom test runner
from django_cfg.testing.runners import SmartTestRunner

class MyTestRunner(SmartTestRunner):
    def _cleanup_old_test_databases(self):
        pass  # Skip cleanup
```

## Summary

**User does:**
```bash
python manage.py test
```

**Django-cfg does automatically:**
1. ✅ Remove old test database (no confirmation)
2. ✅ Create fresh test database
3. ✅ Install PostgreSQL extensions
4. ✅ Apply migrations correctly
5. ✅ Run tests
6. ✅ Clean up

**Zero configuration. Just works.** 🚀
