---
title: Payments v2.0 Configuration Guide
description: Django-CFG payments v2.0 configuration. Simple setup for NowPayments cryptocurrency deposits, balances, and withdrawals.
sidebar_label: Configuration
sidebar_position: 2
keywords:
  - django-cfg configuration
  - django configuration
  - configuration django-cfg
  - nowpayments configuration
---

# Payments v2.0 Configuration Guide

This guide covers everything you need to configure Payments v2.0, from basic setup to production deployment.

## Quick Start (3 minutes)

### Step 1: Get NowPayments API Key
Sign up at [NowPayments.io](https://nowpayments.io) and get your API key and IPN secret (for sandbox testing, use sandbox credentials).

### Step 2: Configure in YAML
```yaml
# config.dev.yaml - Environment-specific settings
nowpayments:
  api_key: "your_sandbox_api_key_here"
  ipn_secret: "your_ipn_secret_here" # Optional but recommended
  sandbox: true  # Use sandbox for testing
```

### Step 3: Enable in Python Config
```python
# config.py
from django_cfg import DjangoConfig
from django_cfg.models.payments import PaymentsConfig, NowPaymentsConfig

class MyConfig(DjangoConfig):
    project_name: str = "My App"

    # Enable payments with NowPayments
    payments: PaymentsConfig = PaymentsConfig(
        enabled=True,
        nowpayments=NowPaymentsConfig(
            api_key=env.nowpayments.api_key,
            ipn_secret=env.nowpayments.ipn_secret,
            sandbox=env.nowpayments.sandbox,
            enabled=True
        )
    )

config = MyConfig()
```

### Step 4: Run Migrations
```bash
# Apply database migrations for 5 payment models
python manage.py migrate

# Models created:
# - payments_payments (Payment records)
# - payments_currencies (Supported currencies)
# - payments_user_balances (User balance tracking)
# - payments_transactions (Transaction history)
# - payments_withdrawal_requests (Withdrawal management)
```

That's it! Payments system is now ready for cryptocurrency deposits and balance management.

## NowPayments Configuration

### Provider Setup
NowPayments is the only supported provider in v2.0, offering 300+ cryptocurrencies.

```python
# config.py - Full configuration example
from django_cfg import DjangoConfig
from django_cfg.models.payments import PaymentsConfig, NowPaymentsConfig

class MyConfig(DjangoConfig):
    payments: PaymentsConfig = PaymentsConfig(
        enabled=True,
        nowpayments=NowPaymentsConfig(
            api_key=env.nowpayments.api_key,
            ipn_secret=env.nowpayments.ipn_secret,  # Optional
            sandbox=True,  # Use sandbox for testing
            enabled=True
        )
    )
```

**YAML Configuration:**
```yaml
# config.dev.yaml - Development
nowpayments:
  api_key: "sandbox_api_key_here"
  ipn_secret: "sandbox_ipn_secret_here"
  sandbox: true

# config.prod.yaml - Production
nowpayments:
  api_key: "production_api_key_here"
  ipn_secret: "production_ipn_secret_here"
  sandbox: false
```

**Configuration Properties:**
- `api_key` - NowPayments API key (required)
- `ipn_secret` - IPN secret for API validation (optional)
- `sandbox` - Use sandbox API (true for testing, false for production)
- `enabled` - Enable/disable NowPayments integration

**API URLs:**
- Sandbox: `https://api-sandbox.nowpayments.io/v1/`
- Production: `https://api.nowpayments.io/v1/`

**Supported Features:**
- ✅ 300+ cryptocurrencies (BTC, ETH, USDT, LTC, etc.)
- ✅ Multiple networks (TRC20, ERC20, Bitcoin, Litecoin, etc.)
- ✅ Polling-based status updates
- ✅ Sandbox environment for safe testing
- ✅ Payment address generation with QR codes
- ✅ Blockchain transaction tracking

### Currency Management

After configuring NowPayments, you need to add supported currencies via the admin interface or programmatically:

```python
from django_cfg.apps.payments.models import Currency

# Add USDT on TRC20 network
Currency.objects.create(
    code='USDTTRC20',              # NowPayments currency code
    name='USDT (TRC20)',           # Display name
    token='USDT',                  # Token symbol
    network='TRC20',               # Network name
    decimal_places=6,              # Decimal precision
    is_active=True,                # Enable for payments
    provider='nowpayments',        # Always 'nowpayments' in v2.0
    min_amount_usd=Decimal('1.00'), # Minimum deposit
    sort_order=10                  # Display order
)

# Add Bitcoin
Currency.objects.create(
    code='BTC',
    name='Bitcoin',
    token='BTC',
    network='Bitcoin',
    decimal_places=8,
    is_active=True,
    provider='nowpayments',
    min_amount_usd=Decimal('10.00'),
    sort_order=1
)
```

**Common NowPayments Currency Codes:**
- `BTC` - Bitcoin
- `ETH` - Ethereum
- `USDTTRC20` - USDT on Tron network
- `USDTERC20` - USDT on Ethereum network
- `LTC` - Litecoin
- `MATIC` - Polygon
- `BNB` - Binance Coin
- And 300+ more...

## Admin Interface Configuration

### Accessing the Admin
The Django admin interface is automatically configured when payments are enabled:

```python
# Admin URLs (automatically registered):
# /admin/payments/payment/              - Payment management
# /admin/payments/currency/             - Currency configuration
# /admin/payments/userbalance/          - Balance monitoring
# /admin/payments/transaction/          - Transaction history
# /admin/payments/withdrawalrequest/    - Withdrawal approvals
```

### Admin Features

**5 Admin Interfaces Available:**

1. **PaymentAdmin** - Manage cryptocurrency deposits
   - Create new payments
   - View payment details and status
   - Poll NowPayments for status updates
   - View QR codes and payment addresses
   - Track blockchain confirmations

2. **CurrencyAdmin** - Configure supported currencies
   - Add/edit available currencies
   - Enable/disable currencies
   - Set minimum deposit amounts
   - Configure display order

3. **UserBalanceAdmin** - Monitor user balances
   - View current balances
   - Track total deposits/withdrawals
   - See last transaction timestamp
   - Export balance reports

4. **TransactionAdmin** - Browse transaction history
   - View all transaction records
   - Filter by type (deposit, withdrawal, etc.)
   - Search by user or payment ID
   - Immutable records for audit trail

5. **WithdrawalRequestAdmin** - Approve/reject withdrawals
   - Review withdrawal requests
   - Approve or reject with notes
   - Track withdrawal status
   - Add blockchain transaction hashes

### Admin Permissions

```python
# Create admin user (Django standard):
python manage.py createsuperuser

# Only staff users with appropriate permissions can:
# - View payment records
# - Approve withdrawals
# - Configure currencies
# - Monitor balances

# Admin access is secured via Django's standard permission system
# Users must be staff with appropriate model permissions
```

## Environment-Specific Configurations

### Development Configuration
```python
# config.dev.py
from django_cfg import DjangoConfig
from django_cfg.models.payments import PaymentsConfig, NowPaymentsConfig

class DevConfig(DjangoConfig):
    debug: bool = True

    payments: PaymentsConfig = PaymentsConfig(
        enabled=True,
        nowpayments=NowPaymentsConfig(
            api_key=env.nowpayments.api_key,
            ipn_secret=env.nowpayments.ipn_secret,
            sandbox=True,  # Always sandbox in dev
            enabled=True
        )
    )

config = DevConfig()
```

**Development YAML:**
```yaml
# config.dev.yaml
nowpayments:
  api_key: "sandbox_api_key_here"
  ipn_secret: "sandbox_ipn_secret_here"
  sandbox: true
```

### Production Configuration
```python
# config.prod.py
class ProdConfig(DjangoConfig):
    debug: bool = False

    payments: PaymentsConfig = PaymentsConfig(
        enabled=True,
        nowpayments=NowPaymentsConfig(
            api_key=env.nowpayments.api_key,
            ipn_secret=env.nowpayments.ipn_secret,
            sandbox=False,  # Production mode
            enabled=True
        )
    )

config = ProdConfig()
```

**Production YAML:**
```yaml
# config.prod.yaml
nowpayments:
  api_key: "production_api_key_here"
  ipn_secret: "production_ipn_secret_here"
  sandbox: false
```

### Configuration Best Practices

**Security:**
- ✅ Never commit API keys to version control
- ✅ Use environment-specific YAML files
- ✅ Add `config.*.yaml` to `.gitignore`
- ✅ Use sandbox mode for development/testing
- ✅ Rotate production keys regularly

**Testing:**
- ✅ Use NowPayments sandbox for development
- ✅ Create test currencies with low minimum amounts
- ✅ Test complete payment flow before production
- ✅ Verify balance calculations with test transactions
- ✅ Test withdrawal approval workflow

**Production:**
- ✅ Set `sandbox=false` for production
- ✅ Configure real payment addresses
- ✅ Monitor payment status regularly
- ✅ Set up admin approval workflow for withdrawals
- ✅ Implement proper backup strategy for transaction records

## Complete Setup Example

### Full Configuration
```python
# config.py - Complete example with all settings
from django_cfg import DjangoConfig
from django_cfg.models.payments import PaymentsConfig, NowPaymentsConfig

class MyConfig(DjangoConfig):
    project_name: str = "My Crypto Payment App"
    debug: bool = False

    payments: PaymentsConfig = PaymentsConfig(
        enabled=True,
        nowpayments=NowPaymentsConfig(
            api_key=env.nowpayments.api_key,
            ipn_secret=env.nowpayments.ipn_secret,
            sandbox=env.nowpayments.sandbox,
            enabled=True
        )
    )

config = MyConfig()
```

### Initial Data Setup

Use the built-in management command to sync currencies from NowPayments:

```bash
# Fetch and sync all available currencies from NowPayments
python manage.py sync_currencies

# Options:
python manage.py sync_currencies --dry-run              # Preview changes
python manage.py sync_currencies --deactivate-missing   # Deactivate removed currencies
python manage.py sync_currencies --skip-confirmation    # Auto-confirm sync
```

**What it does:**
- Fetches all 300+ available currencies from NowPayments API
- Creates or updates Currency records in database
- Sets all synced currencies as active
- Provides summary of created/updated currencies

**After syncing:**
1. Review currencies in admin: `/admin/payments/currency/`
2. Deactivate currencies you don't want to offer
3. Set `sort_order` for preferred currencies
4. Adjust `min_amount_usd` for each currency if needed

## Deployment Checklist

### Before Going Live
- ✅ **Configure NowPayments** - Set production API keys in YAML config
- ✅ **Run Migrations** - Ensure all database tables are created
- ✅ **Create Admin User** - Run `python manage.py createsuperuser`
- ✅ **Initialize Currencies** - Add supported currencies via admin or command
- ✅ **Test Payment Flow** - Create test deposit in sandbox mode
- ✅ **Test Balance Calculation** - Verify transaction aggregation works
- ✅ **Test Withdrawal Workflow** - Approve/reject test withdrawal
- ✅ **Switch to Production** - Set `sandbox: false` in production YAML
- ✅ **Monitor Payments** - Regularly check payment status via admin
- ✅ **Backup Strategy** - Ensure transaction records are backed up

### Environment Variables
```yaml
# config.prod.yaml - Production settings
nowpayments:
  api_key: "${NOWPAYMENTS_API_KEY}"  # From environment variable
  ipn_secret: "${NOWPAYMENTS_IPN_SECRET}"
  sandbox: false

# Set via environment:
# NOWPAYMENTS_API_KEY=your_production_api_key
# NOWPAYMENTS_IPN_SECRET=your_production_ipn_secret
```

### Docker Deployment
```yaml
# docker-compose.yml
version: '3.8'
services:
  web:
    build: .
    ports:
      - "8000:8000"
    environment:
      - NOWPAYMENTS_API_KEY=${NOWPAYMENTS_API_KEY}
      - NOWPAYMENTS_IPN_SECRET=${NOWPAYMENTS_IPN_SECRET}
    depends_on:
      - postgres
    volumes:
      - ./config.prod.yaml:/app/config.prod.yaml

  postgres:
    image: postgres:13
    environment:
      POSTGRES_DB: payments
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

## Next Steps

Ready to use the payment system?

👉 **[Integration Guide](./integration.md)** - Use models in your Django app

👉 **[Examples](./examples.md)** - Real-world usage patterns

---

**Configuration Complete!**

*Your Payments v2.0 system is now configured for cryptocurrency deposits, user balance tracking, and manual withdrawals. Start by adding currencies and creating your first payment!*
