# Payments v2.0 Configuration Guide

This guide explains how to configure the Payments v2.0 app with django_cfg.

## Overview

Payments v2.0 uses `django_cfg.core` for centralized configuration management. All provider credentials and settings are stored in the django_cfg configuration system and accessed through helper functions.

## Configuration Structure

The configuration is accessed through:
```python
from django_cfg.core.state import get_current_config

config = get_current_config()
payments_config = config.payments
```

## NowPayments Configuration

### Required Fields

To enable NowPayments provider, configure the following in your django_cfg settings:

```yaml
payments:
  enabled: true
  nowpayments:
    enabled: true
    api_key: "your_nowpayments_api_key_here"
    sandbox: false  # true for sandbox mode
```

### Optional Fields

```yaml
payments:
  enabled: true
  nowpayments:
    enabled: true
    api_key: "your_api_key"
    sandbox: false
    timeout: 30  # Request timeout in seconds (default: 30)
    min_amount_usd: 1.0  # Minimum payment amount (default: 1.0)
    max_amount_usd: 50000.0  # Maximum payment amount (default: 50000.0)
    payment_expiration_minutes: 30  # Payment expiration time (default: 30)
```

## Using the Configuration

### In Application Code

Use the config helper functions:

```python
from django_cfg.apps.payments.config import (
    get_nowpayments_config,
    is_payments_enabled,
    is_provider_enabled
)

# Check if payments are enabled
if is_payments_enabled():
    print("Payments enabled!")

# Check if NowPayments is enabled
if is_provider_enabled('nowpayments'):
    print("NowPayments provider is enabled")

# Get NowPayments config (validated Pydantic model)
try:
    config = get_nowpayments_config()
    print(f"API URL: {config.api_url}")
    print(f"Sandbox: {config.sandbox}")
    print(f"Timeout: {config.timeout}")
except ValueError as e:
    print(f"Config error: {e}")
```

### In Provider Initialization

The provider is automatically initialized with the correct config:

```python
from django_cfg.apps.payments.api.views import get_nowpayments_provider

# This will read config from django_cfg automatically
provider = get_nowpayments_provider()
```

## Configuration Methods

### `get_payments_config()`

Returns the entire payments configuration from django_cfg.

```python
from django_cfg.apps.payments.config import get_payments_config

payments_config = get_payments_config()
# Returns None if not configured
```

### `get_provider_config(provider_name)`

Get configuration for a specific provider.

```python
from django_cfg.apps.payments.config import get_provider_config

nowpayments_dict = get_provider_config('nowpayments')
# Returns dict with provider config or None if not found
```

### `get_nowpayments_config()`

Get validated NowPayments configuration as Pydantic model.

```python
from django_cfg.apps.payments.config import get_nowpayments_config

config = get_nowpayments_config()
# Returns NowPaymentsConfig instance or None if not configured
# Raises ValueError if configuration is invalid
```

### `is_payments_enabled()`

Check if payments module is enabled.

```python
from django_cfg.apps.payments.config import is_payments_enabled

if is_payments_enabled():
    # Payments are enabled
    pass
```

### `is_provider_enabled(provider_name)`

Check if a specific provider is enabled.

```python
from django_cfg.apps.payments.config import is_provider_enabled

if is_provider_enabled('nowpayments'):
    # NowPayments is enabled
    pass
```

## Environment Variables

For production deployments, use environment variables in your django_cfg configuration:

```yaml
payments:
  enabled: true
  nowpayments:
    enabled: true
    api_key: ${NOWPAYMENTS_API_KEY}  # From environment
    sandbox: ${NOWPAYMENTS_SANDBOX:false}  # Default to false
    timeout: ${NOWPAYMENTS_TIMEOUT:30}
```

Then set in your environment:
```bash
export NOWPAYMENTS_API_KEY="your_production_api_key"
export NOWPAYMENTS_SANDBOX="false"
```

## Configuration Example

Complete example configuration file:

```yaml
# config.yaml
payments:
  enabled: true

  # Middleware settings (optional)
  middleware_enabled: true
  rate_limiting_enabled: true
  usage_tracking_enabled: true

  # Cache timeouts (optional)
  cache_timeouts:
    payment_status: 5  # seconds
    currency_list: 3600  # 1 hour
    api_key: 300  # 5 minutes

  # NowPayments provider
  nowpayments:
    enabled: true
    api_key: ${NOWPAYMENTS_API_KEY}
    sandbox: false
    timeout: 30
    min_amount_usd: 1.0
    max_amount_usd: 50000.0
    payment_expiration_minutes: 30
```

## Testing Configuration

For tests, mock the config getter:

```python
from unittest.mock import patch, Mock

@patch('django_cfg.apps.payments.api.views.get_nowpayments_provider')
def test_payment_creation(mock_get_provider):
    # Mock provider
    mock_provider = Mock()
    mock_provider.create_payment.return_value = ProviderResponse(
        success=True,
        provider_payment_id='test_123',
        status='pending'
    )
    mock_get_provider.return_value = mock_provider

    # Test your code
    # ...
```

## Migration from Django Settings

If you were previously using Django settings (`settings.NOWPAYMENTS_API_KEY`), you need to:

1. Move credentials to django_cfg configuration file
2. Remove from Django settings.py
3. Update environment variables if needed

**Before (Django settings):**
```python
# settings.py
NOWPAYMENTS_API_KEY = os.environ.get('NOWPAYMENTS_API_KEY')
NOWPAYMENTS_SANDBOX = False
```

**After (django_cfg):**
```yaml
# config.yaml
payments:
  nowpayments:
    api_key: ${NOWPAYMENTS_API_KEY}
    sandbox: false
```

## Troubleshooting

### "NowPayments configuration not found"

- Ensure `payments.nowpayments` is defined in your django_cfg configuration
- Check that `enabled: true` is set for both `payments` and `payments.nowpayments`
- Verify environment variables are set correctly

### "Invalid NowPayments configuration"

- Check that `api_key` is provided and not empty
- Verify all numeric values are valid (timeout >= 5, min_amount_usd > 0, etc.)
- Ensure API URL format is correct if customized

### Configuration not loading

- Verify django_cfg is properly initialized
- Check logs for config loading errors
- Ensure config file path is correct

## Security Best Practices

1. **Never commit API keys to version control**
2. **Use environment variables for sensitive data**
3. **Rotate API keys regularly**
4. **Use sandbox mode for development/testing**
5. **Monitor API key usage through NowPayments dashboard**

## Additional Resources

- [NowPayments API Documentation](https://documenter.getpostman.com/view/7907941/S1a32n38)
- [django_cfg Documentation](https://github.com/yourorg/django-cfg)
- [Payments v2.0 README](./README.md)
