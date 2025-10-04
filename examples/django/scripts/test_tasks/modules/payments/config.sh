#!/bin/bash

# Payments Task Testing Configuration

# Load shared configuration
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
source "$SCRIPT_DIR/../../core/shared.sh"

# --- Payments-specific Configuration ---
export QUEUE_NAME="payments"
export TEST_USER_EMAIL="payments_test@example.com"
export TEST_PAYMENT_AMOUNT="75.0"
export TEST_CURRENCY="USD"
export TEST_PROVIDER="nowpayments"

# --- Payments-specific Functions ---
create_test_payment() {
    log_info "Creating test payment for webhook processing..."
    
    cd "$DJANGO_PROJECT_DIR"
    
    # Create payment via Django shell
    local result=$(poetry run python manage.py shell -c "
from django.contrib.auth import get_user_model
from django_cfg.apps.payments.models import UniversalPayment, PaymentProvider
from decimal import Decimal
import uuid

User = get_user_model()

# Get or create test user
user, created = User.objects.get_or_create(
    email='$TEST_USER_EMAIL',
    defaults={'username': 'payments_test_user'}
)

# Get or create payment provider
provider, created = PaymentProvider.objects.get_or_create(
    name='$TEST_PROVIDER',
    defaults={
        'display_name': 'Test NowPayments',
        'is_active': True,
        'provider_type': 'crypto'
    }
)

# Create test payment
payment = UniversalPayment.objects.create(
    user=user,
    provider=provider,
    amount_usd=Decimal('$TEST_PAYMENT_AMOUNT'),
    currency_code='$TEST_CURRENCY',
    status='pending',
    provider_payment_id=f'test_{uuid.uuid4().hex[:8]}',
    metadata={'test': True, 'source': 'task_test'}
)

print(f'PAYMENT_ID:{payment.id}')
print(f'PROVIDER_PAYMENT_ID:{payment.provider_payment_id}')
" 2>/dev/null)
    
    local payment_id=$(echo "$result" | grep "PAYMENT_ID:" | cut -d: -f2)
    local provider_payment_id=$(echo "$result" | grep "PROVIDER_PAYMENT_ID:" | cut -d: -f2)
    
    if [ -n "$payment_id" ]; then
        log_success "Test payment created with ID: $payment_id"
        echo "$payment_id"
        return 0
    else
        log_error "Failed to create test payment"
        return 1
    fi
}

trigger_webhook_task() {
    local payment_id="$1"
    
    log_info "Triggering webhook processing task..."
    
    cd "$DJANGO_PROJECT_DIR"
    
    # Trigger webhook task via Django shell
    local result=$(poetry run python manage.py shell -c "
from django_cfg.apps.payments.tasks.webhook_processing import process_webhook_async
import uuid

# Create mock webhook data
webhook_data = {
    'payment_id': '$payment_id',
    'status': 'confirmed',
    'amount': '$TEST_PAYMENT_AMOUNT',
    'currency': '$TEST_CURRENCY',
    'provider': '$TEST_PROVIDER'
}

# Generate idempotency key
idempotency_key = f'test_webhook_{uuid.uuid4().hex[:8]}'

# Send task
task = process_webhook_async.send(
    provider='$TEST_PROVIDER',
    webhook_data=webhook_data,
    idempotency_key=idempotency_key
)

print(f'TASK_ID:{task.message_id}')
print(f'IDEMPOTENCY_KEY:{idempotency_key}')
" 2>/dev/null)
    
    local task_id=$(echo "$result" | grep "TASK_ID:" | cut -d: -f2)
    local idempotency_key=$(echo "$result" | grep "IDEMPOTENCY_KEY:" | cut -d: -f2)
    
    if [ -n "$task_id" ]; then
        log_success "Webhook task triggered with ID: $task_id"
        echo "$task_id"
        return 0
    else
        log_error "Failed to trigger webhook task"
        return 1
    fi
}

check_payment_processing() {
    local payment_id="$1"
    
    log_info "Checking payment processing status..."
    
    cd "$DJANGO_PROJECT_DIR"
    
    # Check payment status via Django shell
    local result=$(poetry run python manage.py shell -c "
from django_cfg.apps.payments.models import UniversalPayment, PaymentEvent

try:
    payment = UniversalPayment.objects.get(id='$payment_id')
    events = PaymentEvent.objects.filter(payment_id='$payment_id')
    
    print(f'STATUS:{payment.status}')
    print(f'EVENTS:{events.count()}')
    print(f'PROCESSED:{events.filter(event_type=\"webhook_processed\").exists()}')
except UniversalPayment.DoesNotExist:
    print('STATUS:not_found')
    print('EVENTS:0')
    print('PROCESSED:false')
" 2>/dev/null)
    
    local status=$(echo "$result" | grep "STATUS:" | cut -d: -f2)
    local events=$(echo "$result" | grep "EVENTS:" | cut -d: -f2)
    local processed=$(echo "$result" | grep "PROCESSED:" | cut -d: -f2)
    
    log_info "Payment status: $status"
    log_info "Payment events: $events"
    
    if [ "$processed" = "True" ]; then
        log_success "Payment webhook processing completed successfully"
        return 0
    else
        return 1
    fi
}

cleanup_test_payment() {
    local payment_id="$1"
    
    if [ -n "$payment_id" ]; then
        log_info "Cleaning up test payment..."
        
        cd "$DJANGO_PROJECT_DIR"
        
        poetry run python manage.py shell -c "
from django_cfg.apps.payments.models import UniversalPayment, PaymentEvent

try:
    # Clean up events first
    PaymentEvent.objects.filter(payment_id='$payment_id').delete()
    
    # Clean up payment
    payment = UniversalPayment.objects.get(id='$payment_id')
    payment.delete()
    
    print('Payment and events deleted')
except UniversalPayment.DoesNotExist:
    print('Payment not found')
" >/dev/null 2>&1
        
        log_success "Test payment cleanup completed"
    fi
}

# Export payments-specific functions
export -f create_test_payment trigger_webhook_task check_payment_processing cleanup_test_payment
