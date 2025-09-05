# 🧪 Django-CFG Testing Guide

Simple testing system following KISS principles.

## Quick Start

```bash
# Run all tests
python run_tests.py

# Run specific categories
python run_tests.py --core        # Core configuration tests
python run_tests.py --apps        # App tests (accounts, support)
python run_tests.py --integration # Integration tests

# With options
python run_tests.py --fast        # Skip slow tests
python run_tests.py --coverage    # With coverage report
python run_tests.py --verbose     # Verbose output

# Using Make (if available)
make test                         # All tests
make test-core                    # Core tests only
make test-coverage               # With coverage
```

## Test Categories

### 🔧 Core Tests
- **Location**: `tests/test_basic_config.py`, `tests/test_limits_config.py`
- **Purpose**: Test core configuration functionality
- **Speed**: Fast (< 1 second)
- **Dependencies**: None

### 👤 Accounts App Tests
- **Location**: `src/django_cfg/apps/accounts/tests/`
- **Purpose**: Test user management, OTP, profiles
- **Speed**: Medium
- **Dependencies**: Django, database

### 🎫 Support App Tests
- **Location**: `src/django_cfg/apps/support/tests/`
- **Purpose**: Test ticket system, chat interface
- **Speed**: Medium
- **Dependencies**: Django, database

### 🔗 Integration Tests
- **Location**: `tests/test_django_integration.py`, `tests/test_django_cfg_integration.py`
- **Purpose**: Test Django integration and full workflows
- **Speed**: Slow
- **Dependencies**: Django, full environment

## Writing Tests

### Base Test Class

Use `BaseDjangoConfig` for configuration tests to avoid path resolution issues:

```python
from tests.conftest import BaseDjangoConfig

class MyTestConfig(BaseDjangoConfig):
    project_name: str = "Test Project"
    secret_key: str = "test-secret-key-that-is-definitely-long-enough"
    # ... other settings

def test_my_feature():
    config = MyTestConfig()
    settings = config.get_all_settings()
    assert "SECRET_KEY" in settings
```

### Test Markers

Use pytest markers to categorize tests:

```python
import pytest

@pytest.mark.unit
def test_fast_unit_test():
    """Fast, isolated test."""
    pass

@pytest.mark.integration
def test_django_integration():
    """Slower test with Django."""
    pass

@pytest.mark.slow
def test_performance():
    """Slow performance test."""
    pass

@pytest.mark.django_db
def test_database_feature():
    """Test requiring database access."""
    pass
```

## Test Structure

```
tests/
├── conftest.py              # Shared fixtures and base classes
├── test_basic_config.py     # Core configuration tests
├── test_limits_config.py    # Limits configuration tests
├── test_django_integration.py      # Django integration tests
├── test_django_cfg_integration.py  # Full integration tests
└── settings.py              # Test Django settings

src/django_cfg/apps/
├── accounts/tests/          # Accounts app tests
│   ├── test_models.py
│   ├── test_views.py
│   ├── test_services.py
│   └── test_serializers.py
└── support/tests/           # Support app tests
    └── test_models.py
```

## Configuration

### pytest.ini
Basic pytest configuration with markers and test paths.

### pyproject.toml
Coverage settings and test dependencies:
- `pytest>=7.0`
- `pytest-django>=4.5.0`
- `pytest-cov>=4.0.0`
- `pytest-mock>=3.10.0`

## CI/CD Integration

The test runner is designed for easy CI/CD integration:

```yaml
# GitHub Actions example
- name: Run tests
  run: |
    python run_tests.py --coverage
    
# Or with specific categories
- name: Run core tests
  run: python run_tests.py --core --verbose
```

## Performance

- **Core tests**: ~0.3 seconds (30 tests)
- **App tests**: ~1-2 seconds per app
- **Integration tests**: ~3-5 seconds
- **Full suite**: ~5-10 seconds

## Debugging

```bash
# Run single test with verbose output
python -m pytest tests/test_basic_config.py::TestBasicConfiguration::test_minimal_config_creation -v

# Run with debugger
python -m pytest --pdb tests/test_basic_config.py

# Show test coverage
python run_tests.py --coverage
```

## Best Practices

1. **Keep it simple** - Follow KISS principles
2. **Fast feedback** - Core tests should run in < 1 second
3. **Clear names** - Test names should describe what they test
4. **Isolated tests** - Each test should be independent
5. **Use markers** - Categorize tests for selective running
6. **Mock external deps** - Don't depend on external services

## Common Issues

### Path Resolution Errors
If you see `ConfigurationError: Failed to find project root`, use `BaseDjangoConfig` instead of `DjangoConfig` in tests.

### Cache Location Differences
Cache tests may fail due to dynamic location generation. Compare specific settings instead of full equality.

### Import Errors
Ensure all test dependencies are installed:
```bash
pip install -e ".[test]"
```

---

**Made with ❤️ following KISS principles**
