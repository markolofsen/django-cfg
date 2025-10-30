---
title: Logging System
description: Django-CFG logging module with zero-configuration setup, environment-aware logging, and structured output.
sidebar_label: Logging System
sidebar_position: 5
keywords:
  - django-cfg logging
  - django logging
  - structured logging
  - python logging
---

# 📝 Logging System

Django-CFG includes a built-in `django_logging` module that provides zero-configuration logging with environment-aware defaults.

---

## Zero Configuration

The logging module works out of the box—no setup needed:

```python
from django_cfg.modules.django_logging import logger

# That's it - start logging!
logger.info("Application started")
logger.warning("Cache miss detected")
logger.error("Database connection failed")
```

**Automatic configuration based on environment:**
- Development: Console output with colors, DEBUG level
- Production: File logging with rotation, WARNING level

---

## Basic Usage

### Standard Logging Methods

```python
from django_cfg.modules.django_logging import logger

# Debug messages (development only)
logger.debug("Processing user data: %s", user_data)

# Info messages
logger.info("User %s logged in successfully", username)

# Warnings
logger.warning("API rate limit approaching: %d/%d", current, limit)

# Errors
logger.error("Payment processing failed for order %s", order_id)

# Critical errors
logger.critical("Database connection lost", exc_info=True)
```

### Django-CFG Specific Methods

```python
# Configuration logging
logger.config_built("security")
logger.config_warning("database", "Using SQLite in production")
logger.config_error("redis", "Connection failed")

# Application events
logger.app_added("django_tasks", position="end")
logger.app_already_installed("corsheaders")

# Success messages
logger.success("Deployment completed successfully")
logger.init_complete(init_time_ms=245.5, environment="production")

# Errors with details
logger.error_with_details(
    "Payment processing failed",
    details="Gateway timeout after 3 retries"
)
```

### Structured Data Logging

```python
# Log structured data (auto-formatted as JSON/YAML)
logger.data({
    "user_id": 123,
    "action": "purchase",
    "amount": 99.99,
    "currency": "USD"
}, title="User Action")

# Log configuration details
logger.config_details("database", {
    "engine": "postgresql",
    "host": "localhost",
    "max_connections": 100
})
```

---

## Environment-Aware Configuration

Logging automatically adapts to your environment.

### Development Mode (`debug=True`)

**Automatic settings:**
- Console output with **Rich** formatting
- Colored log levels
- DEBUG level messages shown
- Beautiful tracebacks for errors
- No file logging (keeps dev environment clean)

**Example output:**
```
✅ Built security configuration
  ✅ Added corsheaders to middleware
🚀 Django-CFG initialized in 245.50ms
🌍 Environment: development
```

### Production Mode (`debug=False`)

**Automatic settings:**
- File logging with rotation (10MB max, 5 backups)
- WARNING level and above
- Structured log format
- Error logs separated to dedicated file
- Console output minimal

**Log files created:**
```bash
logs/
├── django.log              # All messages (INFO+)
├── django_rotating.log     # Rotating logs (10MB max)
├── django_errors.log       # Errors only (ERROR+)
└── django_rotating.log.1   # Backup files
```

**Log format:**
```
WARNING 2025-10-14 12:34:56 views 1234 MainProcess User login failed
```

---

## Logger Configuration

The logger is configured automatically on first use:

```python
from django_cfg.modules.django_logging import DjangoCfgLogger

# Singleton instance - same logger everywhere
logger = DjangoCfgLogger()

# Auto-detects debug mode from django_cfg config
# Falls back to DEBUG environment variable
# Configures Rich handler in dev, file handlers in prod
```

**Configuration sources (priority order):**
1. Django-CFG config (`config.debug`)
2. Environment variable (`DEBUG=true`)
3. Default (production mode)

---

## Logging Levels

### When to Use Each Level

**DEBUG** - Detailed diagnostic information:
```python
logger.debug("Query executed: %s", query)
logger.debug("Cache hit for key: %s", cache_key)
```

**INFO** - General informational messages:
```python
logger.info("User %s logged in from %s", username, ip_address)
logger.info("Task completed in %.2f seconds", duration)
```

**WARNING** - Unexpected but handled situations:
```python
logger.warning("Retry attempt %d/%d for API call", attempt, max_retries)
logger.warning("Using fallback value for missing config")
```

**ERROR** - Serious problems that need attention:
```python
logger.error("Failed to send email to %s", email, exc_info=True)
logger.error("Payment gateway returned error: %s", error_code)
```

**CRITICAL** - Very serious errors:
```python
logger.critical("Database connection lost", exc_info=True)
logger.critical("Unable to load required configuration")
```

---

## Best Practices

### 1. Include Context

```python
# Good - provides context
logger.error(
    "Order processing failed for order %s (user: %s)",
    order.id,
    order.user.id
)

# Bad - vague message
logger.error("Order failed")
```

### 2. Use Structured Logging

```python
# Good - structured data
logger.data({
    "event": "api_call",
    "endpoint": "/api/users/",
    "method": "GET",
    "status": 200,
    "duration_ms": 150
}, title="API Call")

# Bad - string formatting
logger.info("GET /api/users/ 200 150ms")
```

### 3. Log Exceptions Properly

```python
# Good - includes traceback
try:
    process_payment(order)
except PaymentError as e:
    logger.error("Payment failed for order %s", order.id, exc_info=True)
    raise

# Bad - loses stack trace
except PaymentError as e:
    logger.error(f"Payment failed: {str(e)}")
```

### 4. Avoid Logging Sensitive Data

```python
# Good - sanitized
logger.info("User logged in", extra={
    "user_id": user.id,
    "username": user.username
})

# Bad - includes password!
logger.debug("Login attempt: %s / %s", username, password)
```

---

## Integration with Monitoring

### Sentry Integration

Django-CFG logging works with Sentry handlers:

```python
import sentry_sdk

sentry_sdk.init(
    dsn="your-sentry-dsn",
    environment="production",
)

# Django-CFG logger automatically sends ERROR+ to Sentry
logger.error("Payment failed", exc_info=True)  # → Sent to Sentry
```

### Log Aggregation (ELK, Datadog, CloudWatch)

File logs work with standard log aggregation:

```bash
# Logs are in standard format
logs/django_rotating.log

# Ship to aggregation service
filebeat -c filebeat.yml  # ELK Stack
datadog-agent             # Datadog
aws cloudwatch            # AWS CloudWatch
```

---

## Advanced Usage

### Custom Logger Instance

```python
from django_cfg.modules.django_logging import get_logger

# Get named logger
my_logger = get_logger("myapp.payments")

# Use with module-specific settings
my_logger.info("Payment processed")
```

### Log Formatting Helpers

```python
from django_cfg.modules.django_logging import sanitize_extra, RESERVED_LOG_ATTRS

# Remove reserved attributes before logging
extra_data = {
    "user_id": 123,
    "name": "test",  # Reserved attr - will be removed
    "action": "login"
}

clean_data = sanitize_extra(extra_data)
logger.info("User action", extra=clean_data)
```

---

## Troubleshooting

### Logs Not Appearing

**Check debug mode:**
```python
from django_cfg.core.state import get_current_config

config = get_current_config()
print(f"Debug mode: {config.debug}")  # Should match expected environment
```

**Check log level:**
```python
import logging
logger = logging.getLogger('django_cfg')
print(f"Logger level: {logger.level}")  # 10=DEBUG, 30=WARNING
```

### File Logs Not Created

**Check directory permissions:**
```bash
# Ensure logs/ directory exists and is writable
mkdir -p logs
chmod 755 logs
```

**Production mode check:**
```python
# File logging only enabled in production (debug=False)
config.debug  # Should be False
```

### Colors Not Showing

**Check terminal support:**
```python
import sys
print(sys.stderr.isatty())  # Should be True for colors
```

**Rich library check:**
```bash
# Rich required for colored output
pip install rich
```

---

## See Also

- **[Monitoring Guide](/deployment/monitoring)** - Health checks and system monitoring
- **[Environment Setup](/deployment/environment-setup)** - Configure logging levels
- **[Production Config](/guides/production-config)** - Production logging best practices
- **[ReArq Tasks](/features/integrations/rearq/overview)** - Task execution logging

---

TAGS: logging, monitoring, debugging, structured-logging, django-cfg
DEPENDS_ON: [django-cfg, environment-detection]
USED_BY: [monitoring, production, debugging]
