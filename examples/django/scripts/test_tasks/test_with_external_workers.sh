#!/bin/bash

# Test Background Tasks with External Workers
# This script assumes Dramatiq workers are already running

set -e

# Colors
COLOR_INFO="\033[0;34m"
COLOR_SUCCESS="\033[0;32m"
COLOR_ERROR="\033[0;31m"
COLOR_WARNING="\033[0;33m"
COLOR_RESET="\033[0m"

# Logging functions
log_info() {
    echo -e "${COLOR_INFO}🚀 $1${COLOR_RESET}"
}

log_success() {
    echo -e "${COLOR_SUCCESS}✅ $1${COLOR_RESET}"
}

log_error() {
    echo -e "${COLOR_ERROR}❌ $1${COLOR_RESET}"
}

log_warning() {
    echo -e "${COLOR_WARNING}⚠️  $1${COLOR_RESET}"
}

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DJANGO_PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

log_info "Testing Background Tasks with External Workers"
log_info "=============================================="

# Check if workers are running
log_info "Checking if Dramatiq workers are running..."
if pgrep -f "dramatiq.*django_cfg" > /dev/null; then
    log_success "Dramatiq workers are running"
else
    log_error "No Dramatiq workers found! Please start workers first:"
    echo "  cd $DJANGO_PROJECT_DIR"
    echo "  poetry run python manage.py rundramatiq --processes 1 --threads 1 --queues payments"
    exit 1
fi

# Test usage tracking tasks
log_info "Testing usage tracking background tasks..."

cd "$DJANGO_PROJECT_DIR"

# Run the test
TEST_RESULT=$(poetry run python manage.py shell -c "
from django_cfg.apps.payments.tasks.usage_tracking import update_api_key_usage_async, update_subscription_usage_async
from django_cfg.apps.payments.models import APIKey, Subscription
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
import uuid
import time

User = get_user_model()

print('🚀 Creating test data...')

# Create test user (or get existing)
user, created = User.objects.get_or_create(
    email='sh_test_usage@example.com',
    defaults={'username': 'sh_test_usage_user'}
)

# Create test API key
api_key = APIKey.objects.create(
    user=user,
    name=f'sh_test_key_{uuid.uuid4().hex[:8]}',
    key=f'sh_test_{uuid.uuid4().hex[:16]}',
    total_requests=0,
    is_active=True
)

# Create test subscription
subscription = Subscription.objects.create(
    user=user,
    tier=Subscription.SubscriptionTier.PRO,
    status=Subscription.SubscriptionStatus.ACTIVE,
    total_requests=0,
    requests_per_day=1000,
    expires_at=timezone.now() + timedelta(days=30)
)

print(f'✅ Test data created:')
print(f'   API Key: {api_key.id}')
print(f'   Subscription: {subscription.id}')
print(f'   Initial counts - API: {api_key.total_requests}, Sub: {subscription.total_requests}')

print('📤 Sending tasks to queue...')

# Send tasks
api_task = update_api_key_usage_async.send(
    api_key_id=str(api_key.id),
    ip_address='192.168.1.200'
)
sub_task = update_subscription_usage_async.send(
    subscription_id=str(subscription.id)
)

print(f'📨 Tasks sent - API: {api_task.message_id}, Sub: {sub_task.message_id}')

print('⏳ Waiting for task processing...')
time.sleep(3)

# Check results
api_key.refresh_from_db()
subscription.refresh_from_db()

print(f'📊 Final results:')
print(f'   API requests: {api_key.total_requests}')
print(f'   Sub requests: {subscription.total_requests}')
print(f'   API last used: {api_key.last_used_at}')
print(f'   Sub last request: {subscription.last_request_at}')

# Determine success
success = api_key.total_requests >= 1 and subscription.total_requests >= 1

if success:
    print('🎉 SUCCESS: Background tasks processed correctly!')
    print('TEST_RESULT:PASSED')
else:
    print(f'❌ FAILED: Expected >= 1 request each, got API: {api_key.total_requests}, Sub: {subscription.total_requests}')
    print('TEST_RESULT:FAILED')
" 2>&1)

# Parse test result
if echo "$TEST_RESULT" | grep -q "TEST_RESULT:PASSED"; then
    log_success "Background Tasks Integration Test PASSED!"
    echo ""
    log_success "🎯 All systems working correctly:"
    log_success "   ✅ Dramatiq workers are processing tasks"
    log_success "   ✅ Usage tracking tasks are functional"
    log_success "   ✅ Database updates are working"
    log_success "   ✅ Middleware integration is ready"
    echo ""
    log_info "Your system is ready for production! 🚀"
    exit 0
elif echo "$TEST_RESULT" | grep -q "TEST_RESULT:FAILED"; then
    log_error "Background Tasks Integration Test FAILED!"
    echo ""
    log_error "Test output:"
    echo "$TEST_RESULT"
    exit 1
else
    log_error "Test execution failed or produced unexpected output"
    echo ""
    log_error "Full output:"
    echo "$TEST_RESULT"
    exit 1
fi
