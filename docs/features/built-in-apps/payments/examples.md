---
title: Real-World Examples & Usage
description: Django-CFG Payments v2.0 examples. Production-ready patterns for cryptocurrency deposits, balance management, and withdrawals.
sidebar_label: Examples & Usage
sidebar_position: 4
keywords:
  - django-cfg examples
  - django examples
  - payments examples
  - cryptocurrency payments
---

# Real-World Examples & Usage

This guide provides production-ready examples for using Payments v2.0 models in your Django application.

## Complete Payment Flow Example

### 1. User Deposits Cryptocurrency

```python
# views.py - User initiates deposit
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

        # Create payment
        payment = Payment.objects.create(
            user=request.user,
            amount_usd=amount,
            currency=Currency.objects.get(code=currency_code),
            description=f'Deposit by {request.user.username}'
        )

        # Show payment details to user
        return redirect('payment_detail', payment_id=payment.id)

    # Show deposit form with available currencies
    currencies = Currency.objects.filter(is_active=True)
    return render(request, 'payments/deposit_form.html', {
        'currencies': currencies
    })

@login_required
def payment_detail(request, payment_id):
    """Display payment details with QR code"""

    payment = Payment.objects.get(id=payment_id, user=request.user)

    context = {
        'payment': payment,
        'qr_code_url': payment.get_qr_code_url(size=300),
        'explorer_link': payment.get_explorer_link(),
        'status_color': payment.status_color,
    }

    return render(request, 'payments/payment_detail.html', context)
```

### 2. Check Payment Status (Polling)

```python
# views.py - Admin or cron job polls payment status
from django_cfg.apps.payments.services.providers.nowpayments.provider import NowPaymentsProvider
from django_cfg.apps.payments.config import get_nowpayments_config

def check_pending_payments():
    """Poll NowPayments for pending payment status"""

    # Get provider config
    config = get_nowpayments_config()
    provider = NowPaymentsProvider(config)

    # Get all pending payments
    pending_payments = Payment.objects.filter(
        status__in=[Payment.PaymentStatus.PENDING, Payment.PaymentStatus.CONFIRMING]
    )

    for payment in pending_payments:
        if payment.provider_payment_id:
            # Check status with provider
            status_data = provider.get_payment_status(payment.provider_payment_id)

            # Update payment if status changed
            if status_data['payment_status'] != payment.status:
                payment.status = status_data['payment_status']
                if status_data.get('actually_paid'):
                    payment.actual_amount = Decimal(str(status_data['actually_paid']))
                payment.save()
```

### 3. Update Balance on Payment Completion

```python
# management command or view - Update balance when payment completes
from django_cfg.apps.payments.models import Payment, UserBalance, Transaction
from django.db import transaction as db_transaction

@db_transaction.atomic
def process_completed_payment(payment: Payment):
    """Process completed payment and update user balance"""

    if payment.status != Payment.PaymentStatus.COMPLETED:
        return

    # Get or create user balance
    balance = UserBalance.objects.get_or_create_for_user(payment.user)

    # Create transaction record
    transaction_record = Transaction.objects.create(
        user=payment.user,
        transaction_type=Transaction.TransactionType.DEPOSIT,
        amount_usd=payment.actual_amount_usd or payment.amount_usd,
        balance_after=balance.balance_usd + (payment.actual_amount_usd or payment.amount_usd),
        payment_id=payment.internal_payment_id,
        description=f'Deposit completed - {payment.internal_payment_id}'
    )

    # Update balance
    balance.balance_usd = transaction_record.balance_after
    balance.total_deposited += transaction_record.amount_usd
    balance.last_transaction_at = timezone.now()
    balance.save()

    print(f"Balance updated: {balance.balance_display}")
```

### 4. Withdrawal Request Flow

```python
# views.py - User requests withdrawal
from django_cfg.apps.payments.models import WithdrawalRequest, UserBalance, Currency

@login_required
def request_withdrawal(request):
    """User creates withdrawal request"""

    balance = UserBalance.objects.get_or_create_for_user(request.user)

    if request.method == 'POST':
        amount = Decimal(request.POST['amount'])
        currency_code = request.POST['currency']
        wallet_address = request.POST['wallet_address']

        # Validate sufficient balance
        if balance.balance_usd < amount:
            messages.error(request, 'Insufficient balance')
            return redirect('request_withdrawal')

        # Calculate fees
        network_fee = Decimal('1.00')
        service_fee = Decimal('0.50')
        total_fee = network_fee + service_fee
        final_amount = amount - total_fee

        # Create withdrawal request
        withdrawal = WithdrawalRequest.objects.create(
            user=request.user,
            amount_usd=amount,
            currency=Currency.objects.get(code=currency_code),
            wallet_address=wallet_address,
            network_fee_usd=network_fee,
            service_fee_usd=service_fee,
            total_fee_usd=total_fee,
            final_amount_usd=final_amount
        )

        messages.success(request, f'Withdrawal request created: {withdrawal.internal_withdrawal_id}')
        return redirect('withdrawal_status', withdrawal_id=withdrawal.id)

    currencies = Currency.objects.filter(is_active=True)
    return render(request, 'payments/withdrawal_form.html', {
        'balance': balance,
        'currencies': currencies
    })

# Admin approves withdrawal via Django admin interface
# Then processes it off-platform and updates:
def mark_withdrawal_completed(withdrawal_id, tx_hash):
    """Admin marks withdrawal as completed"""

    withdrawal = WithdrawalRequest.objects.get(id=withdrawal_id)
    withdrawal.status = WithdrawalRequest.Status.COMPLETED
    withdrawal.transaction_hash = tx_hash
    withdrawal.completed_at = timezone.now()
    withdrawal.save()

    # Create transaction to debit balance
    balance = UserBalance.objects.get(user=withdrawal.user)

    transaction_record = Transaction.objects.create(
        user=withdrawal.user,
        transaction_type=Transaction.TransactionType.WITHDRAWAL,
        amount_usd=-withdrawal.amount_usd,  # Negative for debit
        balance_after=balance.balance_usd - withdrawal.amount_usd,
        withdrawal_request_id=withdrawal.internal_withdrawal_id,
        description=f'Withdrawal completed - {withdrawal.internal_withdrawal_id}'
    )

    # Update balance
    balance.balance_usd = transaction_record.balance_after
    balance.total_withdrawn += withdrawal.amount_usd
    balance.last_transaction_at = timezone.now()
    balance.save()
```

## Balance and Transaction Examples

### Display User Balance and History

```python
# views.py - Show user balance dashboard
from django_cfg.apps.payments.models import UserBalance, Transaction

@login_required
def balance_dashboard(request):
    """Display user balance and transaction history"""

    balance = UserBalance.objects.get_or_create_for_user(request.user)
    transactions = Transaction.objects.filter(user=request.user).order_by('-created_at')[:20]

    context = {
        'balance': balance,
        'transactions': transactions,
        'can_withdraw': balance.balance_usd >= Decimal('10.00')  # Minimum withdrawal
    }

    return render(request, 'payments/balance_dashboard.html', context)
```

**Template Example:**
```html
<!-- balance_dashboard.html -->
<div class="balance-card">
    <h2>Your Balance</h2>
    <div class="balance-amount">{{ balance.balance_display }}</div>

    <div class="balance-stats">
        <div>Total Deposited: ${{ balance.total_deposited }}</div>
        <div>Total Withdrawn: ${{ balance.total_withdrawn }}</div>
        <div>Last Transaction: {{ balance.last_transaction_at|date:"Y-m-d H:i" }}</div>
    </div>

    {% if can_withdraw %}
    <a href="{% url 'request_withdrawal' %}" class="btn btn-primary">Request Withdrawal</a>
    {% endif %}
</div>

<div class="transaction-history">
    <h3>Transaction History</h3>
    <table>
        <thead>
            <tr>
                <th>Date</th>
                <th>Type</th>
                <th>Amount</th>
                <th>Balance After</th>
                <th>Description</th>
            </tr>
        </thead>
        <tbody>
            {% for tx in transactions %}
            <tr class="{{ tx.type_color }}">
                <td>{{ tx.created_at|date:"Y-m-d H:i" }}</td>
                <td>{{ tx.get_transaction_type_display }}</td>
                <td>{{ tx.amount_display }}</td>
                <td>${{ tx.balance_after }}</td>
                <td>{{ tx.description }}</td>
            </tr>
            {% endfor %}
        </tbody>
    </table>
</div>
```

## Quick Start Checklist

### Development Setup
- ✅ **Configure PaymentsConfig** - Enable payments in config.py
- ✅ **Set API Keys** - Add NowPayments sandbox credentials
- ✅ **Run Migrations** - Run `python manage.py migrate`
- ✅ **Create Admin User** - Run `python manage.py createsuperuser`
- ✅ **Add Currencies** - Add supported currencies via admin interface
- ✅ **Access Admin** - Visit Django admin `/admin/payments/`

### First Payment Test
- ✅ **Create Payment** - Create deposit via admin interface
- ✅ **View Payment Details** - Check generated payment address and QR code
- ✅ **Monitor Status** - Poll NowPayments for status updates
- ✅ **Complete Payment** - Mark as completed when confirmed
- ✅ **Check Balance** - Verify user balance updated correctly

### Production Deployment
- ✅ **Production Config** - Switch to production API keys (`sandbox: false`)
- ✅ **Regular Polling** - Set up cron job to check pending payments
- ✅ **Monitoring** - Set up logging and alerting
- ✅ **Backup Strategy** - Ensure payment data is backed up
- ✅ **Admin Workflow** - Configure withdrawal approval process

---

**🔥 Examples Complete!**

*You now have comprehensive examples for using Django-CFG Payments v2.0 in production - from cryptocurrency deposits to balance management and withdrawals!*

## See Also

### Payment System

**Core Documentation:**
- [**Payments Overview**](./overview) - Complete payment system introduction
- [**Configuration Guide**](./configuration) - Payment provider configuration
- [**Integration Guide**](./integration) - Django ORM integration guide
- [**Admin Screenshots**](./screenshots) - Visual admin interface tour

### Practical Guides

**Example Projects:**
- [**Sample Project**](/guides/sample-project/overview) - Production payment example
- [**Examples Guide**](/guides/examples) - More real-world patterns
- [**Production Config**](/guides/production-config) - Production payment setup

### Configuration & Setup

**Getting Started:**
- [**Installation**](/getting-started/installation) - Install Django-CFG
- [**Configuration Guide**](/getting-started/configuration) - Enable payments
- [**First Project**](/getting-started/first-project) - Quick start

**Advanced:**
- [**Configuration Models**](/fundamentals/configuration) - PaymentsConfig API
- [**Environment Variables**](/fundamentals/configuration/environment) - API key management
- [**Type-Safe Configuration**](/fundamentals/core/type-safety) - Validation

### Tools & Deployment

**CLI & Management:**
- [**Payment Commands**](/cli/commands/payments) - Test payments via CLI
- [**CLI Tools**](/cli/introduction) - Command-line interface
- [**Troubleshooting**](/guides/troubleshooting) - Common issues

**Production:**
- [**Docker Deployment**](/guides/docker/production) - Deploy payments
- [**Logging**](/deployment/logging) - Payment logging
