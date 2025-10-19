---
title: Admin Interface Guide
description: Django-CFG Payments v2.0 admin interface. Manage cryptocurrency deposits, user balances, withdrawals, and transactions through Django admin.
sidebar_label: Admin Interface
sidebar_position: 5
keywords:
  - django-cfg admin
  - django admin interface
  - payments admin
  - cryptocurrency admin
---

# Admin Interface Guide

Django-CFG Payments v2.0 provides 5 comprehensive Django admin interfaces for managing your cryptocurrency payment system.

## Overview

The Payments v2.0 admin interface is built on Django's standard admin with modern styling from Django Unfold. All admin functionality is automatically registered when payments are enabled.

**Admin URL**: `http://localhost:8000/admin/payments/`

**5 Admin Interfaces Available:**
1. **PaymentAdmin** - Manage cryptocurrency deposits
2. **CurrencyAdmin** - Configure supported currencies
3. **UserBalanceAdmin** - Monitor user balances
4. **TransactionAdmin** - View transaction history
5. **WithdrawalRequestAdmin** - Approve/reject withdrawals

## Payment Management

### PaymentAdmin (`/admin/payments/payment/`)

Manage cryptocurrency deposits from NowPayments.

**List View Features:**
- Payment ID with status badge
- User information
- Amount in USD and cryptocurrency
- Currency with token/network display
- Payment status with color coding
- Payment address for deposits
- Creation date
- Advanced filtering by status, currency, user, date range
- Search by payment ID, user, address

**Detail View Features:**
- Complete payment information
- QR code for payment address
- Blockchain explorer link
- Provider payment ID
- Transaction hash (when confirmed)
- Status tracking with timestamps
- Payment amount in USD and crypto

**Admin Actions:**
- Poll NowPayments for status updates
- View payment details
- Copy payment address
- Filter by status (pending, confirming, completed, failed)

**Payment Status Flow:**
1. `pending` - Payment created, awaiting deposit
2. `confirming` - Deposit detected, awaiting confirmations
3. `completed` - Payment confirmed and processed
4. `failed` - Payment failed or expired

## Currency Configuration

### CurrencyAdmin (`/admin/payments/currency/`)

Configure which cryptocurrencies are available for deposits.

**List View Features:**
- Currency code with badge (e.g., USDTTRC20, BTC)
- Currency name (e.g., "USDT (TRC20)", "Bitcoin")
- Token symbol with icon
- Network name with badge
- Active status
- Sort order for display
- Last updated timestamp

**Detail View Features:**
- Currency code (NowPayments identifier)
- Display name
- Token symbol (e.g., USDT, BTC)
- Network (e.g., TRC20, ERC20, Bitcoin)
- Symbol for UI display
- Provider (always 'nowpayments' in v2.0)
- Minimum deposit amount in USD
- Decimal places for amounts
- Active status
- Sort order

**Admin Actions:**
- Activate selected currencies
- Deactivate selected currencies
- Bulk edit currency settings

**Adding Currencies:**
```python
# Common NowPayments currency codes:
USDTTRC20  # USDT on Tron network
USDTERC20  # USDT on Ethereum network
BTC        # Bitcoin
ETH        # Ethereum
LTC        # Litecoin
MATIC      # Polygon
BNB        # Binance Coin
```

## Balance Monitoring

### UserBalanceAdmin (`/admin/payments/userbalance/`)

Monitor user balance tracking across the platform.

**List View Features:**
- User information with link
- Current balance in USD
- Total deposited (lifetime)
- Total withdrawn (lifetime)
- Last transaction timestamp
- Balance status indicator
- Search by username, email

**Detail View Features:**
- User account link
- Current balance (read-only, computed from transactions)
- Total deposits (lifetime sum)
- Total withdrawals (lifetime sum)
- Last transaction date
- Created/updated timestamps

**Balance Calculation:**
Balance is computed from Transaction records:
```python
balance_usd = SUM(Transaction.amount_usd WHERE user=user)
```

**Admin Actions:**
- View transaction history
- Export balance report
- Filter by balance range
- Search by user

## Transaction History

### TransactionAdmin (`/admin/payments/transaction/`)

View immutable transaction history for audit trail.

**List View Features:**
- User information
- Transaction type badge (deposit, withdrawal, payment, etc.)
- Amount with +/- indicator
- Balance after transaction
- Related payment/withdrawal ID
- Creation timestamp
- Color coding by type

**Detail View Features:**
- User account
- Transaction type
- Amount (positive=credit, negative=debit)
- Balance after this transaction
- Related payment ID (if deposit)
- Related withdrawal ID (if withdrawal)
- Description
- Metadata (JSON field)
- Immutable warning

**Transaction Types:**
- `DEPOSIT` - Cryptocurrency deposit completed
- `WITHDRAWAL` - Withdrawal processed
- `PAYMENT` - Payment to service/product
- `REFUND` - Refund from payment
- `FEE` - Service or network fee
- `BONUS` - Promotional bonus credit
- `ADJUSTMENT` - Manual balance adjustment

**Important:**
Transactions are IMMUTABLE - they cannot be modified or deleted after creation. This ensures audit trail integrity.

## Withdrawal Management

### WithdrawalRequestAdmin (`/admin/payments/withdrawalrequest/`)

Approve and manage user withdrawal requests.

**List View Features:**
- Withdrawal ID with status badge
- User information
- Amount in USD
- Currency with network
- Destination wallet address
- Fee breakdown
- Final amount after fees
- Status with color coding
- Creation and completion dates

**Detail View Features:**
- User account
- Internal withdrawal ID
- Amount in USD
- Currency selection
- Destination wallet address
- Fee calculation:
  - Network fee (blockchain)
  - Service fee (platform)
  - Total fee
  - Final amount (amount - fees)
- Cryptocurrency amount
- Status tracking
- Admin approval:
  - Admin user who approved
  - Admin notes
  - Approval timestamp
- Transaction hash (after sending)
- Status timestamps

**Admin Actions:**
- **Approve Withdrawal** - Approve pending requests
- **Reject Withdrawal** - Reject pending requests with notes
- **Mark Completed** - Mark as completed after sending funds
- Filter by status, user, currency, date range
- Search by withdrawal ID, user, wallet address

**Withdrawal Status Flow:**
1. `pending` - User created request, awaiting admin review
2. `approved` - Admin approved, ready to process
3. `processing` - Being processed off-platform
4. `completed` - Funds sent, transaction hash recorded
5. `rejected` - Rejected by admin with notes
6. `cancelled` - Cancelled by user

**Admin Workflow:**
1. User creates withdrawal request via frontend
2. Admin reviews in WithdrawalRequestAdmin
3. Admin approves or rejects with notes
4. For approved: Admin processes withdrawal off-platform (manually sends crypto)
5. Admin marks as completed and adds transaction hash
6. System creates Transaction record to debit user balance

## Quick Setup

### Initial Configuration

```bash
# 1. Run migrations
python manage.py migrate

# 2. Create admin user
python manage.py createsuperuser

# 3. Start development server
python manage.py runserver

# 4. Access admin interface
# http://localhost:8000/admin/payments/
```

### Adding Currencies

After setup, add supported currencies via CurrencyAdmin:

1. Go to `/admin/payments/currency/add/`
2. Fill in currency details:
   - Code: `USDTTRC20` (NowPayments code)
   - Name: `USDT (TRC20)`
   - Token: `USDT`
   - Network: `TRC20`
   - Min amount: `1.00` USD
   - Decimal places: `6`
   - Active: ✓
   - Sort order: `10`
3. Save and repeat for other currencies

### Testing Payment Flow

1. **Create Payment** (via frontend or admin):
   - Go to `/admin/payments/payment/add/`
   - Select user, amount, currency
   - Save to generate payment address

2. **Monitor Payment**:
   - View in PaymentAdmin
   - Use "Poll NowPayments" action to check status
   - Watch status change: pending → confirming → completed

3. **Check Balance**:
   - Go to `/admin/payments/userbalance/`
   - Verify balance updated after payment completion

4. **View Transactions**:
   - Go to `/admin/payments/transaction/`
   - See immutable transaction record

## Admin URLs Reference

```bash
# Main admin dashboard
http://localhost:8000/admin/

# Payment management
http://localhost:8000/admin/payments/payment/              # List payments
http://localhost:8000/admin/payments/payment/add/          # Create payment
http://localhost:8000/admin/payments/payment/<id>/change/  # Edit payment

# Currency configuration
http://localhost:8000/admin/payments/currency/             # List currencies
http://localhost:8000/admin/payments/currency/add/         # Add currency

# Balance monitoring
http://localhost:8000/admin/payments/userbalance/          # View balances

# Transaction history
http://localhost:8000/admin/payments/transaction/          # View transactions

# Withdrawal management
http://localhost:8000/admin/payments/withdrawalrequest/    # Manage withdrawals
```

## Admin Features

### Security & Permissions
- ✅ Standard Django admin authentication
- ✅ Staff-only access
- ✅ Model-level permissions
- ✅ Action-level permissions
- ✅ Secure API key handling

### User Experience
- ✅ Modern UI with Django Unfold styling
- ✅ Responsive design
- ✅ Advanced filtering and search
- ✅ Bulk actions
- ✅ Color-coded status badges
- ✅ Readonly fields for computed values

### Data Management
- ✅ Complete CRUD operations
- ✅ Immutable transaction records
- ✅ Audit trail maintenance
- ✅ Balance recalculation from transactions
- ✅ Export functionality

### Workflow Management
- ✅ Payment status polling
- ✅ Withdrawal approval workflow
- ✅ Admin notes and comments
- ✅ Status change tracking
- ✅ Timestamp audit trail

## Best Practices

### Security
- ✅ Never expose admin URLs publicly
- ✅ Use strong admin passwords
- ✅ Limit staff user permissions
- ✅ Review withdrawal requests carefully
- ✅ Verify wallet addresses before approval

### Operations
- ✅ Regularly poll pending payments for status updates
- ✅ Monitor user balances for anomalies
- ✅ Review transaction history for audit
- ✅ Process withdrawals promptly after approval
- ✅ Keep admin notes detailed for tracking

### Maintenance
- ✅ Backup transaction records regularly
- ✅ Monitor failed payments
- ✅ Update currency configurations as needed
- ✅ Review and adjust minimum deposit amounts
- ✅ Keep NowPayments API keys secure

## Production Deployment

### Admin Security Checklist
- ✅ Change default admin URL (`ADMIN_URL` setting)
- ✅ Enable HTTPS for all admin access
- ✅ Set up admin IP whitelist
- ✅ Enable two-factor authentication
- ✅ Use strong session security
- ✅ Configure admin logging
- ✅ Set up admin activity monitoring

### Performance Optimization
- ✅ Enable Django admin caching
- ✅ Use select_related/prefetch_related in admin
- ✅ Configure appropriate list_per_page
- ✅ Add database indexes for filtered fields
- ✅ Enable admin query optimization

---

**🎯 Admin Interface Complete!**

*Django-CFG Payments v2.0 provides a comprehensive, production-ready admin interface for managing cryptocurrency payments, user balances, and withdrawals. All features are built on standard Django admin with modern styling and optimized performance.*

## See Also

### Payment System

**Core Documentation:**
- [**Payments Overview**](./overview) - Complete payment system introduction
- [**Configuration Guide**](./configuration) - Payment provider setup
- [**Integration Guide**](./integration) - Django ORM integration
- [**Payment Examples**](./examples) - Real-world usage patterns

### Admin Customization

**Admin Interface:**
- [**Django Unfold Module**](/features/modules/unfold/overview) - Modern admin styling
- [**Built-in Apps**](/features/built-in-apps/overview) - All admin-enabled apps
- [**User Management**](/features/built-in-apps/user-management/overview) - User admin interfaces

### Configuration & Setup

**Getting Started:**
- [**Installation**](/getting-started/installation) - Install Django-CFG
- [**Configuration Guide**](/getting-started/configuration) - Enable payments
- [**First Project**](/getting-started/first-project) - Quick start tutorial

**Production:**
- [**Production Config**](/guides/production-config) - Production admin setup
- [**Deployment Guide**](/deployment/overview) - Deploy with admin interface
