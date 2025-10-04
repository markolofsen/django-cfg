#!/bin/bash

# Quick Task Test - Simple and reliable

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log_info() { echo -e "${BLUE}🚀 $1${NC}"; }
log_success() { echo -e "${GREEN}✅ $1${NC}"; }
log_error() { echo -e "${RED}❌ $1${NC}"; }

# Get project directory
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$PROJECT_DIR"

log_info "Quick Task Test Starting..."

# Test 1: Check TaskConfig auto-initialization
log_info "Testing TaskConfig auto-initialization..."
QUEUES=$(poetry run python manage.py shell -c "
from django_cfg.modules.django_tasks import get_task_service
service = get_task_service()
if service.config:
    print(','.join(service.config.dramatiq.queues))
else:
    print('no-config')
" 2>/dev/null)

if [[ "$QUEUES" == *"payments"* ]]; then
    log_success "Smart queue detection working: $QUEUES"
    if [[ "$QUEUES" == *"knowbase"* ]]; then
        log_success "Both knowbase and payments queues detected"
    else
        log_info "Only payments queue detected (knowbase disabled for SQLite)"
    fi
else
    log_error "Queue detection failed: $QUEUES"
    exit 1
fi

# Test 2: Skip knowbase tests (disabled for SQLite)
log_info "Skipping knowbase tests (module disabled for SQLite)"

# Test 2: Test payments task creation (without worker)
log_info "Testing payments task creation..."
RESULT=$(poetry run python manage.py shell -c "
from django.contrib.auth import get_user_model
from django_cfg.apps.payments.models import UniversalPayment, PaymentProvider
from decimal import Decimal

User = get_user_model()
user, created = User.objects.get_or_create(
    email='test@example.com',
    defaults={'username': 'test_user'}
)

provider, created = PaymentProvider.objects.get_or_create(
    name='test_provider',
    defaults={
        'display_name': 'Test Provider',
        'is_active': True,
        'provider_type': 'crypto'
    }
)

payment = UniversalPayment.objects.create(
    user=user,
    provider=provider,
    amount_usd=Decimal('50.0'),
    currency_code='USD',
    status='pending'
)

print(f'SUCCESS:{payment.id}')
" 2>/dev/null)

if [[ "$RESULT" == *"SUCCESS:"* ]]; then
    PAYMENT_ID=$(echo "$RESULT" | grep "SUCCESS:" | cut -d: -f2)
    log_success "Payment created: $PAYMENT_ID"
else
    log_error "Payment creation failed"
    exit 1
fi

# Test 4: Check if rundramatiq command is available
log_info "Testing rundramatiq command availability..."
COMMAND_HELP=$(poetry run python manage.py help rundramatiq 2>/dev/null | head -n 1 || echo "FAILED")

if [[ "$COMMAND_HELP" != "FAILED" ]]; then
    log_success "rundramatiq command is available"
else
    log_error "rundramatiq command not found"
    exit 1
fi

# Cleanup
log_info "Cleaning up test data..."
poetry run python manage.py shell -c "
from django_cfg.apps.knowbase.models import Document
from django_cfg.apps.payments.models import UniversalPayment

Document.objects.filter(title='Test Document').delete()
UniversalPayment.objects.filter(currency_code='USD').delete()
print('Cleanup completed')
" >/dev/null 2>&1

log_success "All tests passed! 🎉"
log_info "Ready to test with workers:"
log_info "  • Start worker: poetry run python manage.py rundramatiq --queues knowbase"
log_info "  • Start worker: poetry run python manage.py rundramatiq --queues payments"
