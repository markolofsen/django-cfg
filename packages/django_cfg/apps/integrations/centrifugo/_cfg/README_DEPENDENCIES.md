# Centrifugo Dependency Checker

Automatic dependency checking for Centrifugo integration in django-cfg.

## 🎯 Purpose

Checks for all required libraries before using the Centrifugo integration and provides clear messages with installation instructions if anything is missing.

## 📦 Dependencies Checked

### Required
- `cent` - Python Centrifugo client library
- `httpx` - HTTP client for async requests *(included in django-cfg core)*

### Optional (Recommended)
- `redis` - Redis backend for real-time messaging
- `websockets` - WebSocket protocol implementation

**Note:** `httpx` is already included in django-cfg core dependencies, but we verify it's available for Centrifugo integration.

## 🚀 Usage

### Automatic check on import

The check happens automatically when you try to use Centrifugo features.

If dependencies are missing, you will see a detailed message:

```
================================================================================
❌ MISSING CENTRIFUGO DEPENDENCIES
================================================================================

Django-CFG's Centrifugo integration requires additional dependencies.

📦 REQUIRED (missing):

  ❌ cent                        - Python Centrifugo client library

================================================================================
🔧 HOW TO FIX
================================================================================

Install all Centrifugo dependencies at once (RECOMMENDED):

  pip install django-cfg[centrifugo]

  # or with poetry:
  poetry add django-cfg[centrifugo]

Or install manually:

  pip install cent

================================================================================
```

### Manual check

#### In Python code:

```python
from django_cfg.apps.centrifugo._cfg import check_centrifugo_dependencies

# Check with error on missing
try:
    check_centrifugo_dependencies()
    print("✅ All dependencies installed")
except Exception as e:
    print(f"❌ Error: {e}")

# Check without raising error
status = check_centrifugo_dependencies(raise_on_missing=False)
print(status)  # {'cent': True, 'httpx': True, 'redis': False, ...}
```

#### Print status of all dependencies:

```python
from django_cfg.apps.centrifugo._cfg import print_dependency_status

print_dependency_status()
```

Output:
```
Centrifugo Dependencies Status:
============================================================

Required:
  ✅ cent                     5.0.0           - Python Centrifugo client library
  ✅ httpx                    0.28.1          - HTTP client for async requests

Optional (recommended):
  ✅ redis                    6.4.0           - Redis backend for real-time messaging
  ⚠️  websockets              not installed   - WebSocket protocol implementation

============================================================
```

#### Standalone script:

```bash
# From project root
poetry run python -m django_cfg.apps.centrifugo._cfg.check_deps

# Or directly
poetry run python src/django_cfg/apps/centrifugo/_cfg/check_deps.py
```

### Get library versions

```python
from django_cfg.apps.centrifugo._cfg import DependencyChecker

versions = DependencyChecker.get_version_info()
print(f"Cent version: {versions['cent']}")
```

## ⚙️ Configuration

### Disable checking

If you need to temporarily disable checking (for example, for testing):

```bash
export DJANGO_SKIP_CENTRIFUGO_CHECK=1
```

Or in code:
```python
import os
os.environ['DJANGO_SKIP_CENTRIFUGO_CHECK'] = '1'
```

## 🔧 Integration in your code

### In Django AppConfig

```python
from django.apps import AppConfig
from django_cfg.apps.centrifugo._cfg import check_centrifugo_dependencies

class MyAppConfig(AppConfig):
    name = 'myapp'

    def ready(self):
        # Check dependencies on app startup
        try:
            check_centrifugo_dependencies(raise_on_missing=True)
        except Exception as e:
            print(e)
            import sys
            sys.exit(1)
```

## 🎯 Benefits

1. **Clear error messages** - user immediately sees what's missing and how to fix it
2. **Automatic checking** - no need to remember to check manually
3. **Flexibility** - can be disabled for tests or other scenarios
4. **Doesn't break other commands** - checking is performed only where needed
5. **Library versions** - can find out installed versions for debugging

## 📚 API Reference

### `check_centrifugo_dependencies(raise_on_missing=True)`
Checks all Centrifugo dependencies.

**Parameters:**
- `raise_on_missing` (bool): Raise `CentrifugoDependencyError` when dependencies are missing

**Returns:** `Dict[str, bool]` - status of each dependency

**Raises:** `CentrifugoDependencyError` if `raise_on_missing=True` and dependencies are missing

### `print_dependency_status()`
Prints a formatted report of all dependency statuses.

### `DependencyChecker.check_all(raise_on_missing=True)`
Checks all dependencies (static method).

### `DependencyChecker.get_version_info()`
Returns a dictionary with versions of all installed libraries.

### `CentrifugoDependencyError`
Exception that is raised when required dependencies are missing.

## 🧪 Testing

```python
import pytest
from django_cfg.apps.centrifugo._cfg import (
    check_centrifugo_dependencies,
    CentrifugoDependencyError
)

def test_centrifugo_dependencies_installed():
    """Test: all dependencies installed"""
    status = check_centrifugo_dependencies(raise_on_missing=False)
    assert status['cent'] is True
    assert status['httpx'] is True

def test_missing_dependencies_raises_error():
    """Test: error is raised when dependencies are missing"""
    # This test should run in an environment without centrifugo
    with pytest.raises(CentrifugoDependencyError):
        check_centrifugo_dependencies(raise_on_missing=True)
```

## 📖 Usage Examples

### Example 1: Check in CI/CD

```yaml
# .github/workflows/test.yml
- name: Check Centrifugo dependencies
  run: |
    poetry run python -m django_cfg.apps.centrifugo._cfg.check_deps
```

### Example 2: Pre-commit hook

```bash
#!/bin/bash
# .git/hooks/pre-commit

# Check dependencies before commit
poetry run python -m django_cfg.apps.centrifugo._cfg.check_deps
if [ $? -ne 0 ]; then
    echo "❌ Centrifugo dependencies missing. Run: pip install django-cfg[centrifugo]"
    exit 1
fi
```

## 🐛 Troubleshooting

### False positives

If the check shows libraries are missing but they are installed:

```bash
# Check current environment
which python
pip list | grep -E '(cent|httpx)'

# Make sure you're using the correct interpreter
poetry env info
```

### Check not triggering

Make sure that:
1. `django_cfg.apps.centrifugo` is added to `INSTALLED_APPS`
2. The `DJANGO_SKIP_CENTRIFUGO_CHECK` variable is not set

## 🔗 See also

- [Centrifugo Integration Overview](../../../@docs/overview.md)
- [Django-CFG Documentation](https://djangocfg.com/docs)
