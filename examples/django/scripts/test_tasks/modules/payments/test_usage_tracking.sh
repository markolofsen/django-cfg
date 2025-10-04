#!/bin/bash

# Usage Tracking Background Tasks Test
# Tests the new asynchronous usage tracking system for API middleware

# set -e  # Temporarily disabled for debugging

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "$0")/../.." && pwd)"

# Load shared configuration
export CLEANUP_ON_EXIT="false"  # Disable auto cleanup for debugging
source "$SCRIPT_DIR/core/shared.sh"

# --- Test Configuration ---
export QUEUE_NAME="payments"
export TEST_USER_EMAIL="usage_tracking_test@example.com"
export TEST_API_KEY_NAME="usage_tracking_test_key"
export TEST_SUBSCRIPTION_TIER="premium"
export TEST_REQUESTS_COUNT=5

# --- Logging ---
log_test() {
    echo -e "\033[1;36m[TEST]\033[0m $1"
}

log_step() {
    echo -e "\033[1;33m[STEP]\033[0m $1"
}

# --- Test Functions ---
create_test_api_key() {
    log_step "Creating test API key and subscription..."
    
    cd "$DJANGO_PROJECT_DIR"
    
    # Create API key via Django shell
    local result=$(poetry run python manage.py shell -c "
from django.contrib.auth import get_user_model
from django_cfg.apps.payments.models import APIKey, Subscription
import uuid

User = get_user_model()

# Clean up any existing test data
User.objects.filter(email='$TEST_USER_EMAIL').delete()

# Create test user
user, created = User.objects.get_or_create(
    email='$TEST_USER_EMAIL',
    defaults={'username': f'usage_tracking_test_user_{uuid.uuid4().hex[:8]}'}
)

# Create test API key
api_key = APIKey.objects.create(
    user=user,
    name='$TEST_API_KEY_NAME',
    key=f'test_key_{uuid.uuid4().hex[:16]}',
    total_requests=0,
    is_active=True
)

# Create test subscription
subscription = Subscription.objects.create(
    user=user,
    tier='$TEST_SUBSCRIPTION_TIER',
    total_requests=0,
    requests_per_day=1000,
    is_active=True
)

print(f'API_KEY_ID:{api_key.id}')
print(f'SUBSCRIPTION_ID:{subscription.id}')
print(f'USER_ID:{user.id}')
print(f'INITIAL_API_REQUESTS:{api_key.total_requests}')
print(f'INITIAL_SUB_REQUESTS:{subscription.total_requests}')
" 2>/dev/null)
    
    local api_key_id=$(echo "$result" | grep "API_KEY_ID:" | cut -d: -f2)
    local subscription_id=$(echo "$result" | grep "SUBSCRIPTION_ID:" | cut -d: -f2)
    local user_id=$(echo "$result" | grep "USER_ID:" | cut -d: -f2)
    local initial_api=$(echo "$result" | grep "INITIAL_API_REQUESTS:" | cut -d: -f2)
    local initial_sub=$(echo "$result" | grep "INITIAL_SUB_REQUESTS:" | cut -d: -f2)
    
    if [ -n "$api_key_id" ]; then
        log_success "Test data created - API Key: $api_key_id, Subscription: $subscription_id"
        log_info "Initial counters - API: $initial_api, Subscription: $initial_sub"
        echo "$api_key_id:$subscription_id:$user_id"
        return 0
    else
        log_error "Failed to create test data"
        return 1
    fi
}

trigger_usage_tracking_tasks() {
    local api_key_id="$1"
    local subscription_id="$2"
    
    log_step "Triggering $TEST_REQUESTS_COUNT usage tracking tasks..."
    
    cd "$DJANGO_PROJECT_DIR"
    
    # Trigger multiple usage tracking tasks
    local result=$(poetry run python manage.py shell -c "
from django_cfg.apps.payments.tasks.usage_tracking import update_api_key_usage_async, update_subscription_usage_async
import time

task_ids = []

# Send multiple API key usage updates
for i in range($TEST_REQUESTS_COUNT):
    task = update_api_key_usage_async.send(
        api_key_id='$api_key_id',
        ip_address=f'192.168.1.{i+1}'
    )
    task_ids.append(task.message_id)
    time.sleep(0.1)  # Small delay between tasks

# Send multiple subscription usage updates  
for i in range($TEST_REQUESTS_COUNT):
    task = update_subscription_usage_async.send(
        subscription_id='$subscription_id'
    )
    task_ids.append(task.message_id)
    time.sleep(0.1)

print(f'TASKS_SENT:{len(task_ids)}')
print(f'FIRST_TASK_ID:{task_ids[0] if task_ids else \"none\"}')
" 2>/dev/null)
    
    local tasks_sent=$(echo "$result" | grep "TASKS_SENT:" | cut -d: -f2)
    local first_task_id=$(echo "$result" | grep "FIRST_TASK_ID:" | cut -d: -f2)
    
    if [ -n "$tasks_sent" ] && [ "$tasks_sent" -gt 0 ]; then
        log_success "Sent $tasks_sent usage tracking tasks to queue"
        log_info "First task ID: $first_task_id"
        return 0
    else
        log_error "Failed to send usage tracking tasks"
        return 1
    fi
}

check_usage_counters() {
    local api_key_id="$1"
    local subscription_id="$2"
    local expected_count="$3"
    
    log_step "Checking usage counters after task processing..."
    
    cd "$DJANGO_PROJECT_DIR"
    
    # Check updated counters
    local result=$(poetry run python manage.py shell -c "
from django_cfg.apps.payments.models import APIKey, Subscription

try:
    api_key = APIKey.objects.get(id='$api_key_id')
    subscription = Subscription.objects.get(id='$subscription_id')
    
    print(f'API_REQUESTS:{api_key.total_requests}')
    print(f'SUB_REQUESTS:{subscription.total_requests}')
    print(f'API_LAST_USED:{api_key.last_used_at is not None}')
    print(f'SUB_LAST_REQUEST:{subscription.last_request_at is not None}')
except Exception as e:
    print(f'ERROR:{e}')
" 2>/dev/null)
    
    local api_requests=$(echo "$result" | grep "API_REQUESTS:" | cut -d: -f2)
    local sub_requests=$(echo "$result" | grep "SUB_REQUESTS:" | cut -d: -f2)
    local api_last_used=$(echo "$result" | grep "API_LAST_USED:" | cut -d: -f2)
    local sub_last_request=$(echo "$result" | grep "SUB_LAST_REQUEST:" | cut -d: -f2)
    
    log_info "Final counters - API: $api_requests, Subscription: $sub_requests"
    log_info "Timestamps updated - API: $api_last_used, Subscription: $sub_last_request"
    
    # Check if counters match expected values
    if [ "$api_requests" -eq "$expected_count" ] && [ "$sub_requests" -eq "$expected_count" ]; then
        log_success "Usage counters updated correctly!"
        return 0
    else
        log_error "Usage counters mismatch - Expected: $expected_count, Got API: $api_requests, Sub: $sub_requests"
        return 1
    fi
}

test_batch_processing() {
    log_step "Testing batch processing task..."
    
    cd "$DJANGO_PROJECT_DIR"
    
    # Trigger batch processing task
    local result=$(poetry run python manage.py shell -c "
from django_cfg.apps.payments.tasks.usage_tracking import batch_update_usage_counters
from django.core.cache import cache
import time

# Add some test data to cache
cache.set('usage_batch:api_key:test123', 5, timeout=3600)
cache.set('usage_batch:subscription:test456', 3, timeout=3600)

# Trigger batch processing
task = batch_update_usage_counters.send()

print(f'BATCH_TASK_ID:{task.message_id}')
" 2>/dev/null)
    
    local batch_task_id=$(echo "$result" | grep "BATCH_TASK_ID:" | cut -d: -f2)
    
    if [ -n "$batch_task_id" ]; then
        log_success "Batch processing task triggered: $batch_task_id"
        return 0
    else
        log_error "Failed to trigger batch processing task"
        return 1
    fi
}

cleanup_test_data() {
    local api_key_id="$1"
    local subscription_id="$2"
    
    if [ -n "$api_key_id" ]; then
        log_step "Cleaning up test data..."
        
        cd "$DJANGO_PROJECT_DIR"
        
        poetry run python manage.py shell -c "
from django_cfg.apps.payments.models import APIKey, Subscription
from django.contrib.auth import get_user_model

User = get_user_model()

try:
    # Clean up test data
    APIKey.objects.filter(id='$api_key_id').delete()
    Subscription.objects.filter(id='$subscription_id').delete()
    User.objects.filter(email='$TEST_USER_EMAIL').delete()
    
    print('Test data cleaned up')
except Exception as e:
    print(f'Cleanup error: {e}')
" >/dev/null 2>&1
        
        log_success "Test data cleanup completed"
    fi
}

# --- Main Test Function ---
run_usage_tracking_test() {
    log_test "🚀 Starting Usage Tracking Background Tasks Test"
    log_test "=============================================="
    
    # Validate environment
    if ! validate_environment; then
        log_error "Environment validation failed"
        return 1
    fi
    
    # Start worker
    if ! start_worker "$QUEUE_NAME"; then
        log_error "Failed to start payments worker"
        return 1
    fi
    
    # Wait for worker to be ready
    log_info "Waiting for worker to be ready..."
    sleep 3
    
    local test_data=""
    local api_key_id=""
    local subscription_id=""
    local user_id=""
    
    # Create test data
    test_data=$(create_test_api_key)
    if [ $? -ne 0 ]; then
        stop_worker "$QUEUE_NAME"
        return 1
    fi
    
    # Parse test data
    api_key_id=$(echo "$test_data" | cut -d: -f1)
    subscription_id=$(echo "$test_data" | cut -d: -f2)
    user_id=$(echo "$test_data" | cut -d: -f3)
    
    # Trigger usage tracking tasks
    if ! trigger_usage_tracking_tasks "$api_key_id" "$subscription_id"; then
        cleanup_test_data "$api_key_id" "$subscription_id"
        stop_worker "$QUEUE_NAME"
        return 1
    fi
    
    # Wait for tasks to process
    log_info "⏳ Waiting for tasks to process (timeout: ${TEST_TIMEOUT}s)..."
    sleep $((TEST_TIMEOUT / 2))
    
    # Check results
    if ! check_usage_counters "$api_key_id" "$subscription_id" "$TEST_REQUESTS_COUNT"; then
        cleanup_test_data "$api_key_id" "$subscription_id"
        stop_worker "$QUEUE_NAME"
        return 1
    fi
    
    # Test batch processing
    if ! test_batch_processing; then
        log_warning "Batch processing test failed, but continuing..."
    fi
    
    # Cleanup
    cleanup_test_data "$api_key_id" "$subscription_id"
    stop_worker "$QUEUE_NAME"
    
    log_success "✅ Usage Tracking Background Tasks Test PASSED!"
    return 0
}

# --- Usage ---
usage() {
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Test usage tracking background tasks"
    echo ""
    echo "OPTIONS:"
    echo "  -q, --quick    Quick test (reduced timeouts)"
    echo "  -v, --verbose  Verbose output"
    echo "  -h, --help     Show this help"
    echo ""
    echo "EXAMPLES:"
    echo "  $0              # Run full test"
    echo "  $0 --quick      # Run quick test"
    echo "  $0 --verbose    # Run with verbose output"
}

# --- Parse Arguments ---
QUICK_MODE=false
VERBOSE=false

while [[ $# -gt 0 ]]; do
    case $1 in
        -q|--quick)
            QUICK_MODE=true
            export TEST_TIMEOUT="30"
            export TEST_REQUESTS_COUNT=3
            shift
            ;;
        -v|--verbose)
            VERBOSE=true
            shift
            ;;
        -h|--help)
            usage
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            usage
            exit 1
            ;;
    esac
done

# Adjust for quick mode
if [ "$QUICK_MODE" = true ]; then
    log_info "Quick mode enabled (reduced timeouts and request count)"
fi

# --- Main Execution ---
if run_usage_tracking_test; then
    log_success "🎉 All tests passed!"
    exit 0
else
    log_error "❌ Tests failed!"
    exit 1
fi
