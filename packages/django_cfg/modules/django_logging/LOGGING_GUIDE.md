# Django CFG Logging Strategy Guide

## Overview

Django CFG uses a sophisticated logging system that automatically adjusts based on the `debug` configuration setting. This guide explains the logging architecture, how to control logging output, and best practices.

## Core Principles

### 1. Debug-Aware Logging

Logging verbosity is controlled by the `config.debug` setting:

```python
# config.py
debug: bool = False  # Production
debug: bool = True   # Development
```

**Log Levels by Mode:**

| Mode | Level | What You See |
|------|-------|--------------|
| `debug=True` | DEBUG | Everything: DEBUG, INFO, WARNING, ERROR, CRITICAL |
| `debug=False` | WARNING | Only important: WARNING, ERROR, CRITICAL |

**Why This Matters:**
- **Production** (`debug=False`): Clean logs, only warnings and errors → easier monitoring
- **Development** (`debug=True`): Verbose logs → easier debugging

### 2. Modular File Structure

Logs are organized by module for easy troubleshooting:

```
logs/
├── django.log                    # All Django logs (root logger)
└── djangocfg/
    ├── core.log                  # Core django_cfg functionality
    ├── apps.log                  # Apps (payments, agents, etc.)
    ├── models.log                # Data models
    └── modules.log               # Modules (logging, tasks, etc.)
```

**Automatic Module Detection:**
The logging system automatically routes logs based on the logger name:
- `django_cfg.core.*` → `core.log`
- `django_cfg.apps.payments.*` → `apps.log`
- `django_cfg.modules.*` → `modules.log`

### 3. Dual Handler System

Each django-cfg logger has TWO handlers:

1. **Console Handler** (stdout/stderr)
   - Uses Rich formatting for pretty output
   - Respects debug level
   - Shows in terminal during development

2. **File Handler** (modular)
   - Plain text format for parsing
   - Module-specific files
   - Persists for analysis

## Configuration

### YAML Configuration

```yaml
# config.dev.yaml
debug: true  # Verbose logging

# config.prod.yaml
debug: false  # Only warnings/errors
```

### Environment Variable Fallback

If config is not available, uses `DEBUG` environment variable:

```bash
DEBUG=true python manage.py runserver  # Verbose
DEBUG=false python manage.py runserver # Quiet
```

## Usage Examples

### Basic Logging

```python
from django_cfg.modules.django_logging import get_logger

logger = get_logger(__name__)

# These only show when debug=True:
logger.debug("Detailed debugging information")
logger.info("General informational message")

# These ALWAYS show:
logger.warning("Something unexpected happened")
logger.error("An error occurred")
logger.critical("Critical system failure")
```

### Auto-Detected Module Names

The `get_logger()` function automatically detects the module:

```python
# In: /django_cfg/apps/payments/services/provider.py
logger = get_logger()  # Auto-detects as 'django_cfg.apps.payments'

# Manual override:
logger = get_logger('django_cfg.custom_module')
```

### Rich Console Output

When `debug=True`, you get beautifully formatted console output:

```
[10/02/25 17:52:00] INFO     🚀 Generated DRF settings
                    INFO     ✅ Dramatiq enabled with 7 queues
```

When `debug=False`, console is silent except for warnings/errors.

## Logger Types

### 1. Django Logger (`django_logger.py`)

**NEW Simple Auto-Configuring Logger**

```python
from django_cfg.modules.django_logging.django_logger import get_logger

logger = get_logger(__name__)
logger.info("This message respects debug mode")
```

**Features:**
- Automatically respects `config.debug`
- Modular file output
- Single source of truth for all django-cfg logging

**When to Use:** For all new django-cfg code (PREFERRED)

### 2. Legacy Rich Logger (`logger.py`)

**OLD Rich-Formatted Logger**

```python
from django_cfg.modules.django_logging.logger import DjangoCfgLogger

logger = DjangoCfgLogger()
logger.info("Rich formatted message")
```

**Features:**
- Fancy Rich console formatting
- NOW respects `config.debug` (recently fixed)
- Used in older code

**When to Use:** Existing code that hasn't been migrated yet

## How Debug Control Works

### Architecture Flow

```
┌─────────────────────────────────────────────────────┐
│ 1. config.debug = False                            │
│    (Set in config.dev.yaml / config.prod.yaml)     │
└────────────────────┬────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────┐
│ 2. Logger Setup Detects Debug Mode                 │
│    - Checks config.debug first                     │
│    - Falls back to DEBUG env var                   │
└────────────────────┬────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────┐
│ 3. Sets Log Level Based on Debug                   │
│    - debug=True  → logging.DEBUG (all messages)    │
│    - debug=False → logging.WARNING (warn+ only)    │
└────────────────────┬────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────┐
│ 4. Configures Handlers                             │
│    - Console Handler: level = log_level            │
│    - File Handler: level = log_level               │
│    - Both respect the same level                   │
└────────────────────┬────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────┐
│ 5. Runtime Filtering                               │
│    - logger.info() → Filtered out if debug=False   │
│    - logger.warning() → Always passes through       │
└─────────────────────────────────────────────────────┘
```

## Code Examples

### Example 1: Simple Usage

```python
from django_cfg.modules.django_logging import get_logger

logger = get_logger(__name__)

def process_payment(amount: float):
    logger.debug(f"Processing payment: ${amount}")  # Only in debug

    try:
        result = payment_gateway.charge(amount)
        logger.info(f"Payment processed: {result.id}")  # Only in debug
        return result
    except PaymentError as e:
        logger.error(f"Payment failed: {e}")  # Always shown
        raise
```

### Example 2: Module-Specific Logging

```python
# File: django_cfg/apps/payments/services/nowpayments.py
from django_cfg.modules.django_logging import get_logger

# Auto-detects as 'django_cfg.apps.payments'
logger = get_logger()

class NowPaymentsProvider:
    def __init__(self, api_key: str):
        logger.debug(f"Initializing NowPayments: {api_key[:10]}...")
        # Logs to: logs/djangocfg/apps.log
```

### Example 3: Conditional Debug Code

```python
from django_cfg.core.state import get_current_config

config = get_current_config()

if config and config.debug:
    # Expensive operation only in debug mode
    from django_cfg.modules.django_dashboard.debug import save_section_render
    save_section_render('overview', html_content)
else:
    # Skip debug rendering in production
    pass
```

## Troubleshooting

### Issue: Still Seeing INFO Logs When debug=False

**Possible Causes:**

1. **Server not restarted** after changing config
   ```bash
   # Solution: Restart server
   python manage.py runserver
   ```

2. **Wrong config file loaded**
   ```bash
   # Check which config is loaded
   Loading config file: config.dev.ignore.yaml
   [django-cfg] Modular logging configured successfully! Debug: False
   ```

3. **Using wrong logger**
   ```python
   # ❌ BAD: Standard logging (doesn't respect config)
   import logging
   logger = logging.getLogger(__name__)

   # ✅ GOOD: Django CFG logger (respects config)
   from django_cfg.modules.django_logging import get_logger
   logger = get_logger(__name__)
   ```

### Issue: Logs Not Going to Files

**Check:**

1. **Directory permissions**
   ```bash
   ls -la logs/
   # Should be writable
   ```

2. **Logger name prefix**
   ```python
   # Only 'django_cfg.*' loggers get modular files
   logger = get_logger('django_cfg.my_module')  # ✅ Gets file
   logger = get_logger('my_module')             # ❌ Console only
   ```

### Issue: No Console Output at All

**Check debug status:**

```python
from django_cfg.core.state import get_current_config

config = get_current_config()
print(f"Debug: {config.debug}")

# Expected output:
# debug=True  → You'll see INFO, DEBUG, WARNING, ERROR
# debug=False → You'll ONLY see WARNING, ERROR, CRITICAL
```

## Best Practices

### 1. Use Appropriate Log Levels

```python
# DEBUG: Detailed diagnostic info
logger.debug(f"SQL query: {query}")
logger.debug(f"Function called with args: {args}")

# INFO: Confirmation of expected behavior
logger.info(f"User {user.id} logged in successfully")
logger.info(f"Payment processor initialized")

# WARNING: Something unexpected but handled
logger.warning(f"API rate limit approaching: {count}/1000")
logger.warning(f"Deprecated function called: {func.__name__}")

# ERROR: Actual errors that need attention
logger.error(f"Payment failed: {error}")
logger.error(f"Database connection lost")

# CRITICAL: System-level failures
logger.critical(f"Redis connection failed - cache disabled")
logger.critical(f"Unable to load configuration")
```

### 2. Structured Logging for Production

```python
# Include context for easier troubleshooting
logger.error(
    f"Payment processing failed",
    extra={
        'user_id': user.id,
        'amount': amount,
        'provider': 'nowpayments',
        'error_code': error.code
    }
)
```

### 3. Performance Considerations

```python
# ❌ BAD: Expensive operation always runs
debug_data = expensive_debug_operation()
logger.debug(f"Debug data: {debug_data}")

# ✅ GOOD: Only run when needed
if logger.isEnabledFor(logging.DEBUG):
    debug_data = expensive_debug_operation()
    logger.debug(f"Debug data: {debug_data}")

# ✅ BETTER: Check config directly
config = get_current_config()
if config and config.debug:
    debug_data = expensive_debug_operation()
    logger.debug(f"Debug data: {debug_data}")
```

### 4. Migration from Old Logging

**Before (using standard logging):**
```python
import logging
logger = logging.getLogger(__name__)

logger.info("This always shows")  # Problem!
```

**After (using django-cfg logging):**
```python
from django_cfg.modules.django_logging import get_logger

logger = get_logger(__name__)
logger.info("This respects debug mode")  # Better!
```

## Quick Reference

### Log Levels Cheat Sheet

| Level | Numeric | When to Use | Shows in Production? |
|-------|---------|-------------|---------------------|
| DEBUG | 10 | Diagnostic details | ❌ No |
| INFO | 20 | Confirmation messages | ❌ No |
| WARNING | 30 | Unexpected but handled | ✅ Yes |
| ERROR | 40 | Errors requiring attention | ✅ Yes |
| CRITICAL | 50 | System-level failures | ✅ Yes |

### Configuration Quick Check

```python
# In Python shell
from django_cfg.core.state import get_current_config

config = get_current_config()
print(f"Debug mode: {config.debug}")
print(f"Environment: {config.env_mode}")

# Expected for production:
# Debug mode: False
# Environment: production
```

### File Location Quick Reference

```bash
# View recent logs
tail -f logs/django.log                    # All logs
tail -f logs/djangocfg/apps.log           # App-specific
tail -f logs/djangocfg/core.log           # Core functionality

# Search for errors
grep ERROR logs/django.log
grep CRITICAL logs/djangocfg/*.log
```

## Advanced Topics

### Custom Log Formatting

```python
from django_cfg.modules.django_logging import get_logger
import logging

logger = get_logger(__name__)

# Add custom formatter
handler = logging.FileHandler('custom.log')
formatter = logging.Formatter(
    '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
)
handler.setFormatter(formatter)
logger.addHandler(handler)
```

### Logging in Async Code

```python
import asyncio
from django_cfg.modules.django_logging import get_logger

logger = get_logger(__name__)

async def async_task():
    logger.debug("Starting async task")
    await asyncio.sleep(1)
    logger.info("Async task completed")
```

### Integration with External Services

```python
from django_cfg.modules.django_logging import get_logger
import sentry_sdk

logger = get_logger(__name__)

def process_with_sentry():
    try:
        result = risky_operation()
        logger.info(f"Operation succeeded: {result}")
    except Exception as e:
        logger.error(f"Operation failed: {e}")
        sentry_sdk.capture_exception(e)
        raise
```

## Summary

The Django CFG logging system provides:

✅ **Automatic debug-aware logging** - Respects `config.debug`
✅ **Modular file organization** - Easy to find relevant logs
✅ **Rich console formatting** - Beautiful development experience
✅ **Production-ready** - Clean, parseable logs in production
✅ **Easy migration** - Simple `get_logger()` function

**Remember:** When `debug=False`, only WARNING, ERROR, and CRITICAL messages appear. This keeps production logs clean and focused on what matters.

---

**Last Updated:** 2025-10-03
**Django CFG Version:** 1.3.13
**Python Version:** 3.10+
