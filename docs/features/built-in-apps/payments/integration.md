---
title: Django Integration Guide
description: Django-CFG Payments v2.0 integration. Learn how to use payment models in your Django application with ORM-based balance tracking.
sidebar_label: Django Integration
sidebar_position: 3
keywords:
  - django-cfg integration
  - django integration
  - payments integration
  - django orm
---

# Django Integration Guide

This guide explains how to integrate Payments v2.0 models into your Django application, including payment creation, balance tracking, and withdrawal management.

## Database Models (ORM)

Payments v2.0 provides 5 core models that you can use directly in your Django application:

### Model Overview

```python
from django_cfg.apps.payments.models import (
    Payment,           # Cryptocurrency deposit records
    Currency,          # Supported payment currencies
    UserBalance,       # User balance tracking
    Transaction,       # Immutable transaction history
    WithdrawalRequest  # Manual withdrawal requests
)
```

**Model Relationships:**
- `Payment` → references `Currency` (ForeignKey) and `User`
- `UserBalance` → one-to-one with `User`
- `Transaction` → references `User` (many transactions per user)
- `WithdrawalRequest` → references `Currency` and `User`
- All models use standard Django ORM

**Key Features:**
- ✅ **Standard Django Models** - Use familiar ORM patterns
- ✅ **No Custom Signals** - v2.0 simplifies by removing signal complexity
- ✅ **Direct Database Access** - Query with standard Django ORM
- ✅ **Type-Safe** - Full type hints and validation

### Payment Model
Cryptocurrency deposit records via NowPayments:

```python
from django_cfg.apps.payments.models import Payment, Currency
from decimal import Decimal

# Create a payment
payment = Payment.objects.create(
    user=user,
    amount_usd=Decimal('99.99'),
    currency=Currency.objects.get(code='USDTTRC20'),
    description='Premium subscription deposit'
)

# Access payment properties
print(payment.internal_payment_id)  # PAY_20250114123456_abc12345
print(payment.status)                # 'pending'
print(payment.amount_display)        # '$99.99 USD'
print(payment.is_pending)            # True
print(payment.qr_data)              # Payment address for QR code
print(payment.get_explorer_link())  # Blockchain explorer URL

# Update status manually
payment.status = Payment.PaymentStatus.COMPLETED
payment.completed_at = timezone.now()
payment.save()
```

**Payment Model Fields:**
- `user` - User who created the payment
- `internal_payment_id` - Unique payment identifier (auto-generated)
- `amount_usd` - Payment amount in USD (Decimal)
- `currency` - ForeignKey to Currency model
- `pay_amount` - Amount in cryptocurrency (Decimal)
- `provider` - Always 'nowpayments' in v2.0
- `provider_payment_id` - NowPayments payment ID
- `status` - Payment status (pending, confirming, completed, etc.)
- `pay_address` - Cryptocurrency payment address
- `transaction_hash` - Blockchain transaction hash
- `description` - Payment description

### Currency Model
Supported payment currencies with token and network information:

```python
from django_cfg.apps.payments.models import Currency

# Get active currencies
currencies = Currency.objects.filter(is_active=True)

# Get specific currency
usdt = Currency.objects.get(code='USDTTRC20')
print(usdt.display_name)  # "USDT (TRC20)"
print(usdt.token)         # "USDT"
print(usdt.network)       # "TRC20"
print(usdt.min_amount_usd)  # Decimal('1.00')

# Check currency properties
print(usdt.is_active)     # True
print(usdt.provider)      # 'nowpayments'
```

**Currency Model Fields:**
- `code` - NowPayments currency code (e.g., USDTTRC20, BTC)
- `name` - Full currency name
- `token` - Token symbol (e.g., USDT, BTC)
- `network` - Network name (e.g., TRC20, ERC20, Bitcoin)
- `decimal_places` - Decimal precision for amounts
- `is_active` - Whether currency is available for payments
- `provider` - Always 'nowpayments' in v2.0
- `min_amount_usd` - Minimum payment amount
- `sort_order` - Display order in lists

### UserBalance Model
User balance tracking with ORM-based calculation:

```python
from django_cfg.apps.payments.models import UserBalance

# Get or create user balance
balance = UserBalance.objects.get_or_create_for_user(user)

# Access balance information
print(balance.balance_display)      # '$199.99 USD'
print(balance.balance_usd)          # Decimal('199.99')
print(balance.total_deposited)      # Decimal('250.00')
print(balance.total_withdrawn)      # Decimal('50.00')
print(balance.last_transaction_at)  # datetime

# Balance properties
print(balance.is_empty)             # False
print(balance.has_transactions)     # True

# Balance is calculated from Transaction records
# balance_usd = SUM(Transaction.amount_usd WHERE user=user)
```

**UserBalance Model Fields:**
- `user` - OneToOneField to User
- `balance_usd` - Current balance (Decimal, computed from transactions)
- `total_deposited` - Lifetime total deposits
- `total_withdrawn` - Lifetime total withdrawals
- `last_transaction_at` - Timestamp of last transaction
- `created_at` / `updated_at` - Timestamps

### Transaction Model
Immutable transaction records for audit trail:

```python
from django_cfg.apps.payments.models import Transaction

# Create a transaction (typically done automatically by payment system)
transaction = Transaction.objects.create(
    user=user,
    transaction_type=Transaction.TransactionType.DEPOSIT,
    amount_usd=Decimal('99.99'),  # Positive for credit
    balance_after=Decimal('199.99'),
    description='Payment completed - PAY_20250114_abc'
)

# Query transactions
transactions = Transaction.objects.filter(user=user).order_by('-created_at')

# Transaction properties
print(transaction.is_credit)       # True (amount > 0)
print(transaction.is_debit)        # False
print(transaction.amount_display)  # '+$99.99'
print(transaction.type_color)      # 'success' (for UI display)

# Transactions are IMMUTABLE - cannot be modified
# Attempting to modify will raise ValidationError
```

**Transaction Types:**
- `DEPOSIT` - Cryptocurrency deposit completed
- `WITHDRAWAL` - Withdrawal processed
- `PAYMENT` - Payment to service/product
- `REFUND` - Refund from payment
- `FEE` - Service or network fee
- `BONUS` - Promotional bonus credit
- `ADJUSTMENT` - Manual balance adjustment

**Transaction Model Fields:**
- `user` - ForeignKey to User
- `transaction_type` - Type of transaction (see above)
- `amount_usd` - Transaction amount (positive=credit, negative=debit)
- `balance_after` - User balance after this transaction
- `payment_id` - Related payment ID (optional)
- `withdrawal_request_id` - Related withdrawal ID (optional)
- `description` - Transaction description
- `metadata` - JSON field for additional data

### WithdrawalRequest Model
Manual withdrawal management with admin approval:

```python
from django_cfg.apps.payments.models import WithdrawalRequest

# User creates withdrawal request
withdrawal = WithdrawalRequest.objects.create(
    user=user,
    amount_usd=Decimal('50.00'),
    currency=Currency.objects.get(code='USDTTRC20'),
    wallet_address='TExampleAddress123...',
    network_fee_usd=Decimal('1.00'),
    service_fee_usd=Decimal('0.50')
)

# Check withdrawal status
print(withdrawal.status)            # 'pending'
print(withdrawal.is_pending)        # True
print(withdrawal.can_be_cancelled)  # True
print(withdrawal.amount_display)    # '$50.00 USD'
print(withdrawal.final_amount_usd)  # Decimal('48.50') after fees

# Admin approves withdrawal
withdrawal.status = WithdrawalRequest.Status.APPROVED
withdrawal.approved_at = timezone.now()
withdrawal.admin_user = admin_user
withdrawal.save()

# After processing, mark completed
withdrawal.status = WithdrawalRequest.Status.COMPLETED
withdrawal.transaction_hash = 'blockchain_tx_hash'
withdrawal.completed_at = timezone.now()
withdrawal.save()
```

**Withdrawal Status Flow:**
1. `PENDING` - Awaiting admin review
2. `APPROVED` - Approved by admin, ready to process
3. `PROCESSING` - Being processed off-platform
4. `COMPLETED` - Funds sent, tx_hash recorded
5. `REJECTED` - Rejected by admin
6. `CANCELLED` - Cancelled by user

**WithdrawalRequest Model Fields:**
- `user` - User requesting withdrawal
- `internal_withdrawal_id` - Unique ID (WD_YYYYMMDDHHMMSS_UUID)
- `amount_usd` - Withdrawal amount
- `currency` - Cryptocurrency to send
- `wallet_address` - Destination address
- `network_fee_usd` / `service_fee_usd` / `total_fee_usd` - Fee breakdown
- `final_amount_usd` - Amount after fees
- `status` - Withdrawal status
- `transaction_hash` - Blockchain tx hash (after sending)
- `admin_user` / `admin_notes` - Admin approval info

## Provider Integration

### Working with NowPayments Provider

```python
# Direct provider integration for status polling
from django_cfg.apps.payments.services.providers.nowpayments.provider import NowPaymentsProvider
from django_cfg.apps.payments.config import get_nowpayments_config

# Get provider config
config = get_nowpayments_config()
provider = NowPaymentsProvider(config)

# Check payment status
payment = Payment.objects.get(id=payment_id)
if payment.provider_payment_id:
    status_data = provider.get_payment_status(payment.provider_payment_id)

    # Update payment based on provider response
    payment.status = status_data['payment_status']
    if status_data.get('actually_paid'):
        payment.actual_amount = Decimal(str(status_data['actually_paid']))
    payment.save()
```

## Admin Interface Integration

### Admin Registration
The admin interface is automatically available for all 5 models:

```python
# Admin interfaces at:
# /admin/payments/payment/              - PaymentAdmin
# /admin/payments/currency/             - CurrencyAdmin
# /admin/payments/userbalance/          - UserBalanceAdmin
# /admin/payments/transaction/          - TransactionAdmin
# /admin/payments/withdrawalrequest/    - WithdrawalRequestAdmin

# Each admin provides:
# - List views with filtering and search
# - Detail views with all field display
# - Custom actions (approve withdrawal, mark completed, etc.)
# - Read-only fields for timestamps and calculated values
```

## Integration Examples

### Custom Django Views
Integrate payments into your Django views:

```python
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django_cfg.apps.payments.models import Payment, Currency
from decimal import Decimal

@login_required
def create_deposit(request):
    """Create cryptocurrency deposit payment"""

    if request.method == 'POST':
        amount = Decimal(request.POST['amount'])
        currency_code = request.POST['currency']

        # Create payment directly using ORM
        payment = Payment.objects.create(
            user=request.user,
            amount_usd=amount,
            currency=Currency.objects.get(code=currency_code),
            description=f'Deposit by {request.user.username}'
        )

        return redirect('payment_detail', payment_id=payment.id)

    currencies = Currency.objects.filter(is_active=True)
    return render(request, 'create_deposit.html', {
        'currencies': currencies
    })

@login_required
def payment_detail(request, payment_id):
    """Display payment details with QR code"""

    payment = Payment.objects.get(id=payment_id, user=request.user)

    return render(request, 'payment_detail.html', {
        'payment': payment,
        'qr_code_url': payment.get_qr_code_url(size=300),
        'explorer_link': payment.get_explorer_link(),
        'status_color': payment.status_color,
    })
```

### Django REST Framework Integration
Use with DRF serializers and viewsets:

```python
from rest_framework import serializers, viewsets
from django_cfg.apps.payments.models import Payment, UserBalance

class PaymentSerializer(serializers.ModelSerializer):
    currency_name = serializers.CharField(source='currency.display_name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Payment
        fields = [
            'id', 'internal_payment_id', 'amount_usd', 'currency', 'currency_name',
            'status', 'status_display', 'pay_address', 'transaction_hash',
            'created_at', 'completed_at'
        ]
        read_only_fields = ['internal_payment_id', 'pay_address', 'transaction_hash']

class BalanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserBalance
        fields = ['balance_usd', 'total_deposited', 'total_withdrawn', 'last_transaction_at']
        read_only_fields = ['__all__']

class PaymentViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = PaymentSerializer

    def get_queryset(self):
        return Payment.objects.filter(user=self.request.user)
```

## Key Integration Benefits

### Simple ORM Integration
- ✅ **Direct Database Access** - Use standard Django ORM
- ✅ **No Service Layer** - Work directly with models
- ✅ **Familiar Patterns** - Standard Django development
- ✅ **Type Safety** - Full type hints and validation

### Admin Interface
- ✅ **5 Admin Views** - Complete management interface
- ✅ **Withdrawal Approval** - Manual admin workflow
- ✅ **Balance Monitoring** - User balance tracking
- ✅ **Transaction History** - Complete audit trail

### Balance System
- ✅ **Immutable Transactions** - Cannot be modified after creation
- ✅ **ORM Calculation** - Balance computed from transactions
- ✅ **Audit Trail** - Complete financial history
- ✅ **Balance Validation** - Prevents negative balances

---

**🔥 Integration Complete!**

*Your Django application now has full cryptocurrency payment support with ORM-based balance tracking and a complete admin interface!*

## See Also

### Payment System

**Core Documentation:**
- [**Payments Overview**](./overview) - Complete payment system introduction
- [**Configuration Guide**](./configuration) - Payment provider configuration
- [**Payment Examples**](./examples) - Real-world payment flows
- [**Admin Screenshots**](./screenshots) - Visual admin interface tour

### Integration & Development

**Payment Integration:**
- [**User Management**](/features/built-in-apps/user-management/overview) - Link with users

### Configuration & Setup

**Getting Started:**
- [**Installation**](/getting-started/installation) - Install Django-CFG with payments
- [**Configuration Guide**](/getting-started/configuration) - Enable payment system
- [**First Project**](/getting-started/first-project) - Quick start tutorial

**Advanced:**
- [**Configuration Models**](/fundamentals/configuration) - PaymentsConfig API reference
- [**Environment Variables**](/fundamentals/configuration/environment) - Secure API key management
- [**Type-Safe Configuration**](/fundamentals/core/type-safety) - Pydantic validation

### Related Features

**User Management:**
- [**User Management Apps**](/features/built-in-apps/user-management/overview) - Customer integration
- [**Accounts App**](/features/built-in-apps/user-management/accounts) - User authentication

**Integrations:**
- [**Integrations Overview**](/features/integrations/overview) - All integrations
- [**Built-in Apps**](/features/built-in-apps/overview) - All production apps

### Tools & Deployment

**CLI & Testing:**
- [**Payment Commands**](/cli/commands/payments) - Test payments via CLI
- [**CLI Tools**](/cli/introduction) - Command-line interface
- [**Troubleshooting**](/guides/troubleshooting) - Common payment issues

**Production:**
- [**Docker Deployment**](/guides/docker/production) - Deploy payment system
- [**Production Config**](/guides/production-config) - Production payment setup
- [**Logging**](/deployment/logging) - Payment event logging
