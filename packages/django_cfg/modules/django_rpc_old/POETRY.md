# Poetry Setup & Dependencies - Django RPC Module

**Status:** ✅ Ready to Use
**All Dependencies:** ✅ Already Installed
**Test Framework:** ✅ Working via Poetry

---

## Dependency Analysis

### ✅ Required Dependencies (Already Installed)

All dependencies for WebSocket RPC module are **already present** in `pyproject.toml`:

```toml
# Redis client (line 98-99)
"redis>=6.4.0,<7.0"           # ✅ Redis Python client
"hiredis>=2.0.0,<4.0"         # ✅ High-performance Redis protocol

# Pydantic models (line 57-58)
"pydantic>=2.11.0,<3.0"       # ✅ Pydantic 2 core
"pydantic[email]>=2.11.0,<3.0" # ✅ Email validation extras

# Testing (dev group)
"pytest>=8.4,<9.0"            # ✅ Test framework
"pytest-mock>=3.15,<4.0"      # ✅ Mock support
```

### 📦 No Additional Dependencies Needed

**Important:** Do NOT add any new dependencies!

The WebSocket RPC module uses:
- ✅ Redis (already in core dependencies)
- ✅ Pydantic 2 (already in core dependencies)
- ✅ Standard library only (json, uuid, logging, threading)

---

## Running Tests via Poetry

### Basic Commands

```bash
# Navigate to django-cfg directory
cd libs/django_cfg

# Run all WebSocket RPC tests
poetry run pytest src/django_cfg/tests/websocket/ -v

# Run with concise output
poetry run pytest src/django_cfg/tests/websocket/ -q

# Run specific test file
poetry run pytest src/django_cfg/tests/websocket/test_models.py -v

# Run specific test class
poetry run pytest src/django_cfg/tests/websocket/test_client.py::TestRPCClientCall -v
```

### Using Test Markers

```bash
# Run only unit tests
poetry run pytest src/django_cfg/tests/websocket/ -m "unit"

# Run only model tests
poetry run pytest src/django_cfg/tests/websocket/ -m "unit and models"

# Run only client tests
poetry run pytest src/django_cfg/tests/websocket/ -m "unit and client"
```

### Test Collection (Dry Run)

```bash
# Show what tests would run
poetry run pytest src/django_cfg/tests/websocket/ --co -q

# Show with markers filter
poetry run pytest src/django_cfg/tests/websocket/ -m "models" --co -q
```

---

## Poetry vs Direct Python

### ❌ Don't Use PYTHONPATH Manually

```bash
# ❌ Old way (manual PYTHONPATH)
PYTHONPATH=src:$PYTHONPATH pytest src/django_cfg/tests/websocket/

# ✅ Better way (poetry handles paths)
poetry run pytest src/django_cfg/tests/websocket/
```

### Why Poetry?

Poetry automatically:
- ✅ Sets correct PYTHONPATH
- ✅ Uses virtual environment (.venv)
- ✅ Manages dependencies
- ✅ Isolates from system Python

---

## Current Test Results

### Via Poetry

```bash
$ poetry run pytest src/django_cfg/tests/websocket/ -q

src/django_cfg/tests/websocket/test_client.py ..................    [ 40%]
src/django_cfg/tests/websocket/test_models.py ..........................  [100%]

======================== 44 passed in 0.20s ========================
```

### Test Breakdown

| Category | Count | Marker | Status |
|----------|-------|--------|--------|
| Model tests | 26 | `unit and models` | ✅ PASS |
| Client tests | 18 | `unit and client` | ✅ PASS |
| **Total** | **44** | `unit` | **✅ PASS** |

### Performance

- **Single test:** ~0.005s
- **Full suite:** ~0.20s
- **Meets target:** < 0.1s per test ✅

---

## Warnings Analysis

Current warnings (from libraries, not our code):

```
1. PydanticDeprecatedSince20: `min_items` → `min_length`
   Source: Pydantic library internal
   Action: Ignore (library will fix)

2. RemovedInDjango60Warning: URLField scheme change
   Source: Django core
   Action: Ignore (Django-specific)

3. DeprecationWarning: datetime.utcnow()
   Source: Pydantic library internal
   Action: Ignore (our code uses datetime.now(timezone.utc) ✅)
```

**Our code is clean** - all warnings come from dependencies, not from WebSocket RPC module.

---

## Development Workflow

### Install Development Dependencies

```bash
cd libs/django_cfg

# Install all dev dependencies
poetry install --with dev

# Or specific groups
poetry install --with dev,test,docs
```

### Add New Dependency (If Needed)

```bash
# Add to main dependencies
poetry add package-name

# Add to dev dependencies
poetry add --group dev package-name

# Add to test dependencies
poetry add --group test package-name
```

**For WebSocket RPC:** No new dependencies needed!

### Update Dependencies

```bash
# Update all dependencies
poetry update

# Update specific package
poetry update redis

# Show outdated packages
poetry show --outdated
```

---

## Project Structure

```
libs/django_cfg/
├── pyproject.toml              # ✅ Poetry configuration
├── poetry.lock                 # ✅ Locked versions
├── .venv/                      # ✅ Virtual environment
├── src/django_cfg/
│   ├── models/websocket/       # Pydantic models
│   ├── modules/django_rpc/     # RPC client
│   └── tests/websocket/        # Unit tests
└── tests/                      # Integration tests
```

---

## pyproject.toml Key Sections

### Build System

```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
```

Uses **hatchling** but supports Poetry for development.

### Core Dependencies

```toml
[project]
dependencies = [
    "redis>=6.4.0,<7.0",        # WebSocket RPC ✅
    "pydantic>=2.11.0,<3.0",    # WebSocket RPC ✅
    # ... other dependencies
]
```

### Poetry Dev Group

```toml
[tool.poetry.group.dev.dependencies]
pytest = "^8.4.2"
pytest-django = "^4.11.1"
pytest-mock = "^3.14.1"
# ... other dev tools
```

---

## Common Issues

### Issue: `poetry: command not found`

**Solution:** Install Poetry

```bash
curl -sSL https://install.python-poetry.org | python3 -
```

### Issue: Virtual environment not found

**Solution:** Create virtual environment

```bash
cd libs/django_cfg
poetry install
```

### Issue: Tests can't import django_cfg

**Solution:** Always use `poetry run`

```bash
# ❌ Wrong
pytest src/django_cfg/tests/websocket/

# ✅ Correct
poetry run pytest src/django_cfg/tests/websocket/
```

### Issue: Module 'redis' not found

**Solution:** Install dependencies

```bash
poetry install --with dev,test
```

---

## CI/CD Integration

### GitHub Actions

```yaml
- name: Install dependencies
  run: |
    cd libs/django_cfg
    poetry install --with dev,test

- name: Run WebSocket RPC tests
  run: |
    cd libs/django_cfg
    poetry run pytest src/django_cfg/tests/websocket/ -v
```

### Pre-commit Hook

```yaml
# .pre-commit-config.yaml
- repo: local
  hooks:
    - id: pytest-websocket
      name: WebSocket RPC Tests
      entry: bash -c 'cd libs/django_cfg && poetry run pytest src/django_cfg/tests/websocket/ -q'
      language: system
      pass_filenames: false
```

---

## Summary

✅ **All dependencies installed**
✅ **Tests working via Poetry**
✅ **44/44 tests passing**
✅ **Performance excellent (~0.2s)**
✅ **No manual PYTHONPATH needed**
✅ **Ready for production**

**Next Steps:**
- Continue development using `poetry run`
- No new dependencies needed
- All tools ready to use

---

**Last Updated:** 2025-10-03
**Maintainer:** Django-CFG Team
**Status:** ✅ Production Ready
