---
title: Payments Commands
description: Django-CFG CLI payments commands. Command-line interface for payments commands with examples, options, and production workflows.
sidebar_label: Payments
sidebar_position: 6
keywords:
  - django-cfg payments
  - django-cfg command payments
  - cli payments
---

# Payments Management Commands

Commands for managing payments, currencies, providers, and transactions.

## Currency Management

### `currency_stats`

Display currency statistics and usage metrics.

```bash
python manage.py currency_stats [OPTIONS]
```

**Options:**
- `--format [json|yaml|table]` - Output format (default: table)

**Examples:**

```bash
# Show currency stats
python manage.py currency_stats

# Export as JSON
python manage.py currency_stats --format json

# Export as YAML
python manage.py currency_stats --format yaml
```

---

### `manage_currencies`

Manage payment currencies.

```bash
python manage.py manage_currencies [ACTION] [OPTIONS]
```

**Actions:**
- `list` - List all currencies
- `add` - Add new currency
- `update` - Update currency
- `remove` - Remove currency

**Options:**
- `--code TEXT` - Currency code (BTC, ETH, USD, etc.)
- `--name TEXT` - Currency name
- `--network TEXT` - Network for crypto currencies

**Examples:**

```bash
# List all currencies
python manage.py manage_currencies list

# Add fiat currency
python manage.py manage_currencies add --code USD --name "US Dollar"

# Add crypto currency
python manage.py manage_currencies add --code BTC --name Bitcoin

# Add crypto with network
python manage.py manage_currencies add --code USDT --name "Tether" --network TRC20

# Update currency
python manage.py manage_currencies update --code BTC --name "Bitcoin (Updated)"

# Remove currency
python manage.py manage_currencies remove --code DOGE
```

---

## Provider Management

### `manage_providers`

Manage payment providers and their configurations.

```bash
python manage.py manage_providers [ACTION] [OPTIONS]
```

**Actions:**
- `list` - List all providers
- `add` - Add new provider
- `update` - Update provider
- `remove` - Remove provider

**Options:**
- `--name TEXT` - Provider name
- `--type TEXT` - Provider type (crypto, fiat)
- `--api-key TEXT` - API key

**Examples:**

```bash
# List all providers
python manage.py manage_providers list

# Add crypto provider
python manage.py manage_providers add \
  --name NowPayments \
  --type crypto

# Add fiat provider
python manage.py manage_providers add \
  --name Stripe \
  --type fiat

# Update provider API key
python manage.py manage_providers update \
  --name Stripe \
  --api-key sk_live_new_key

# Remove provider
python manage.py manage_providers remove --name PayPal
```

---

### `test_providers`

Test payment provider integrations.

```bash
python manage.py test_providers [OPTIONS]
```

**Options:**
- `--provider TEXT` - Specific provider to test

**Examples:**

```bash
# Test all providers
python manage.py test_providers

# Test specific provider
python manage.py test_providers --provider nowpayments

# Test Stripe
python manage.py test_providers --provider stripe
```

**Output:**
```
🚀 Testing payment providers...

✅ NowPayments - Connection successful
  API Status: Active
  Supported currencies: 150+

✅ Stripe - Connection successful
  API Status: Active
  Account: live_mode

❌ PayPal - Connection failed
  Error: Invalid API credentials
```

---

## Payment Processing

### `process_pending_payments`

Process pending payment transactions.

```bash
python manage.py process_pending_payments [OPTIONS]
```

**Options:**
- `--limit INTEGER` - Maximum payments to process

**Examples:**

```bash
# Process all pending payments
python manage.py process_pending_payments

# Process up to 100 payments
python manage.py process_pending_payments --limit 100

# Process up to 10 (testing)
python manage.py process_pending_payments --limit 10
```

**Cron Setup:**

```bash
# Process every 5 minutes
*/5 * * * * cd /path/to/project && python manage.py process_pending_payments

# Process every minute (high volume)
* * * * * cd /path/to/project && python manage.py process_pending_payments --limit 50
```

---

## Data Management

### `cleanup_expired_data`

Cleanup expired payment data and old records.

```bash
python manage.py cleanup_expired_data [OPTIONS]
```

**Options:**
- `--days INTEGER` - Days to keep (default: 90)
- `--dry-run` - Show what would be deleted

**Examples:**

```bash
# Cleanup data older than 90 days (default)
python manage.py cleanup_expired_data

# Keep only last 30 days
python manage.py cleanup_expired_data --days 30

# Keep last 180 days
python manage.py cleanup_expired_data --days 180

# Dry run to see what would be deleted
python manage.py cleanup_expired_data --dry-run

# Dry run for 30 days
python manage.py cleanup_expired_data --days 30 --dry-run
```

**Cron Setup:**

```bash
# Daily cleanup at 3 AM
0 3 * * * cd /path/to/project && python manage.py cleanup_expired_data

# Weekly cleanup (Sundays at 2 AM)
0 2 * * 0 cd /path/to/project && python manage.py cleanup_expired_data --days 60
```

---

## Common Workflows

### Initial Payment Setup

```bash
# 1. Add currencies
python manage.py manage_currencies add --code BTC --name Bitcoin
python manage.py manage_currencies add --code ETH --name Ethereum
python manage.py manage_currencies add --code USDT --name Tether --network TRC20

# 2. Add providers
python manage.py manage_providers add --name NowPayments --type crypto
python manage.py manage_providers add --name Stripe --type fiat

# 3. Test providers
python manage.py test_providers

# 4. Check stats
python manage.py currency_stats
```

### Add New Crypto Currency

```bash
# 1. Add currency with network
python manage.py manage_currencies add \
  --code USDC \
  --name "USD Coin" \
  --network ERC20

# 2. Verify addition
python manage.py manage_currencies list

# 3. Test payment flow
python manage.py test_providers --provider nowpayments
```

### Production Maintenance

```bash
# 1. Process pending payments
python manage.py process_pending_payments

# 2. Check currency stats
python manage.py currency_stats

# 3. Cleanup old data
python manage.py cleanup_expired_data --dry-run
python manage.py cleanup_expired_data
```

---

## Configuration

### Django Configuration

```python
# config.py
class MyConfig(DjangoConfig):
    # Enable payments app
    enable_payments: bool = True

    # Provider API keys
    nowpayments_api_key: str = env.payments.nowpayments_key
    stripe_api_key: str = env.payments.stripe_key
```

### Environment Variables

```yaml
# config.dev.yaml
payments:
  nowpayments_key: "your_nowpayments_api_key"
  stripe_key: "sk_test_..."
```

---

## Best Practices

### 1. Always Test Providers First

```bash
# Test before going live
python manage.py test_providers
```

### 2. Regular Payment Processing

```bash
# Setup cron for automatic processing
*/5 * * * * python manage.py process_pending_payments
```

### 3. Monitor Currency Stats

```bash
# Export stats for monitoring
python manage.py currency_stats --format json > /var/log/currency_stats.json
```

### 4. Use Dry Run for Cleanup

```bash
# Always check before deleting
python manage.py cleanup_expired_data --dry-run
```

### 5. Keep Reasonable Data Retention

```bash
# Balance between storage and audit needs
# 90 days for regular transactions
# 365 days for compliance requirements
python manage.py cleanup_expired_data --days 365
```

---

## Monitoring

### Payment Processing Metrics

```bash
# Check processing status
python manage.py currency_stats

# Export for monitoring
python manage.py currency_stats --format json | \
  jq '{total_payments, successful_payments, failed_payments}'
```

### Provider Health Check

```bash
# Regular provider testing
0 * * * * python manage.py test_providers > /var/log/provider_health.log
```

### Storage Monitoring

```bash
# Monitor data growth
python manage.py currency_stats --format json | \
  jq '.storage_used_mb'
```

---

## Troubleshooting

### Provider Connection Failed

```bash
# Test specific provider
python manage.py test_providers --provider stripe

# Check API keys in config
python manage.py show_config --section payments
```

### Pending Payments Not Processing

```bash
# Check payment status
python manage.py currency_stats

# Manually trigger processing
python manage.py process_pending_payments --limit 10
```

### Cleanup Issues

```bash
# Dry run first
python manage.py cleanup_expired_data --dry-run

# Check database space
python manage.py currency_stats
```

---

## Related Documentation

- **[Quick Reference](./quick-reference)** - Fast command lookup
- **[Payments App Guide](/features/built-in-apps/payments/overview)** - Complete documentation
- **[Currency Module](/features/modules/currency/overview)** - Currency conversion

---

**Payments made easy!** 💳
