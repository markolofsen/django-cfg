# gRPC Dependency Checker

Automatic dependency checking for gRPC integration in django-cfg.

## 🎯 Purpose

Checks for all required libraries before starting the gRPC server and provides a clear message with installation instructions if anything is missing.

## 📦 Dependencies Checked

### Required
- `grpcio` - Core gRPC framework
- `grpcio-tools` - Protocol Buffer compiler and tools
- `protobuf` - Protocol Buffers runtime

### Optional (Recommended)
- `grpcio-reflection` - Server reflection API (for grpcurl/grpcui)
- `grpcio-health-checking` - Health check service

## 🚀 Usage

### Automatic check on startup

The check happens automatically when running the command:

```bash
python manage.py rungrpc
```

If dependencies are missing, you will see a detailed message:

```
================================================================================
❌ MISSING gRPC DEPENDENCIES
================================================================================

Django-CFG's gRPC integration requires additional dependencies that are not installed.

📦 REQUIRED (missing):

  ❌ grpcio                        - Core gRPC framework
  ❌ grpcio-tools                  - Protocol Buffer compiler and tools
  ❌ protobuf                      - Protocol Buffers runtime

================================================================================
🔧 HOW TO FIX
================================================================================

Option 1: Install all gRPC dependencies at once (RECOMMENDED):

  pip install django-cfg[grpc]

  # or with poetry:
  poetry add django-cfg[grpc]

Option 2: Install dependencies manually:

  pip install grpcio grpcio-tools protobuf

================================================================================
```

### Manual check

#### In Python code:

```python
from django_cfg.apps.grpc.utils.dependencies import check_grpc_dependencies

# Check with error on missing
try:
    check_grpc_dependencies(raise_on_missing=True)
    print("✅ All dependencies installed")
except Exception as e:
    print(f"❌ Error: {e}")

# Check without raising error
status = check_grpc_dependencies(raise_on_missing=False)
print(status)  # {'grpcio': True, 'grpcio-tools': True, ...}
```

#### Print status of all dependencies:

```python
from django_cfg.apps.grpc.utils.dependencies import print_dependency_status

print_dependency_status()
```

Output:
```
gRPC Dependencies Status:
============================================================

Required:
  ✅ grpcio                     1.60.0          - Core gRPC framework
  ✅ grpcio-tools               1.60.0          - Protocol Buffer compiler and tools
  ✅ protobuf                   5.27.0          - Protocol Buffers runtime

Optional (recommended):
  ✅ grpcio-reflection          1.60.0          - Server reflection API (for grpcurl/grpcui)
  ✅ grpcio-health-checking     1.60.0          - Health check service

============================================================
```

#### Standalone script:

```bash
# From project root
poetry run python -m django_cfg.apps.grpc.utils.check_deps

# Or directly
poetry run python src/django_cfg/apps/grpc/utils/check_deps.py
```

### Get library versions

```python
from django_cfg.apps.grpc.utils.dependencies import DependencyChecker

versions = DependencyChecker.get_version_info()
print(f"gRPC version: {versions['grpcio']}")
```

## ⚙️ Configuration

### Disable checking

If you need to temporarily disable checking (for example, for testing):

```bash
export DJANGO_SKIP_GRPC_CHECK=1
python manage.py rungrpc
```

Or in code:
```python
import os
os.environ['DJANGO_SKIP_GRPC_CHECK'] = '1'
```

### Commands where checking is NOT performed

Checking is automatically skipped for:
- `makemigrations`, `migrate`
- `shell`, `shell_plus`
- `test`
- `check`
- `help`
- `collectstatic`
- `createsuperuser`
- And other administrative commands

For the `rungrpc` command, checking is **always** performed (strict check).

## 🔧 Integration in your code

### In Django AppConfig

```python
from django.apps import AppConfig
from django_cfg.apps.grpc.utils.dependencies import check_grpc_dependencies

class MyAppConfig(AppConfig):
    name = 'myapp'

    def ready(self):
        # Check dependencies on app startup
        try:
            check_grpc_dependencies(raise_on_missing=True)
        except Exception as e:
            print(e)
            import sys
            sys.exit(1)
```

### In management command

```python
from django.core.management.base import BaseCommand
from django_cfg.apps.grpc.utils.dependencies import check_grpc_dependencies

class Command(BaseCommand):
    def handle(self, *args, **options):
        # Check before running command
        check_grpc_dependencies(raise_on_missing=True)

        # Your code
        ...
```

## 🎯 Benefits

1. **Clear error messages** - user immediately sees what's missing and how to fix it
2. **Automatic checking** - no need to remember to check manually
3. **Flexibility** - can be disabled for tests or other scenarios
4. **Doesn't break other commands** - checking is performed only where needed
5. **Library versions** - can find out installed versions for debugging

## 📚 API Reference

### `check_grpc_dependencies(raise_on_missing=True)`
Checks all gRPC dependencies.

**Parameters:**
- `raise_on_missing` (bool): Raise `GRPCDependencyError` when dependencies are missing

**Returns:** `Dict[str, bool]` - status of each dependency

**Raises:** `GRPCDependencyError` if `raise_on_missing=True` and dependencies are missing

### `print_dependency_status()`
Prints a formatted report of all dependency statuses.

### `DependencyChecker.check_all(raise_on_missing=True)`
Checks all dependencies (static method).

### `DependencyChecker.get_version_info()`
Returns a dictionary with versions of all installed libraries.

### `GRPCDependencyError`
Exception that is raised when required dependencies are missing.

## 🧪 Testing

```python
import pytest
from django_cfg.apps.grpc.utils.dependencies import (
    check_grpc_dependencies,
    GRPCDependencyError
)

def test_grpc_dependencies_installed():
    """Test: all dependencies installed"""
    status = check_grpc_dependencies(raise_on_missing=False)
    assert status['grpcio'] is True
    assert status['grpcio-tools'] is True
    assert status['protobuf'] is True

def test_missing_dependencies_raises_error():
    """Test: error is raised when dependencies are missing"""
    # This test should run in an environment without grpc
    with pytest.raises(GRPCDependencyError):
        check_grpc_dependencies(raise_on_missing=True)
```

## 📖 Usage Examples

### Example 1: Check in CI/CD

```yaml
# .github/workflows/test.yml
- name: Check gRPC dependencies
  run: |
    poetry run python -m django_cfg.apps.grpc.utils.check_deps
```

### Example 2: Pre-commit hook

```bash
#!/bin/bash
# .git/hooks/pre-commit

# Check dependencies before commit
poetry run python -m django_cfg.apps.grpc.utils.check_deps
if [ $? -ne 0 ]; then
    echo "❌ gRPC dependencies missing. Run: pip install django-cfg[grpc]"
    exit 1
fi
```

### Example 3: Docker healthcheck

```dockerfile
# Dockerfile
HEALTHCHECK --interval=30s --timeout=3s \
  CMD python -m django_cfg.apps.grpc.utils.check_deps || exit 1
```

## 🐛 Troubleshooting

### False positives

If the check shows libraries are missing but they are installed:

```bash
# Check current environment
which python
pip list | grep grpc

# Make sure you're using the correct interpreter
poetry env info
```

### Check not triggering

Make sure that:
1. `django_cfg.apps.grpc` is added to `INSTALLED_APPS`
2. You are running the `rungrpc` command
3. The `DJANGO_SKIP_GRPC_CHECK` variable is not set

## 🔗 See also

- [gRPC Integration Overview](../../../@docs/architecture/integration-overview.md)
- [Getting Started with gRPC](../../../@docs/guides/getting-started.md)
- [Troubleshooting Guide](../../../@docs/guides/troubleshooting.md)
