#!/bin/bash

# Payments Module Test
# Tests webhook processing functionality

set -e

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

# Load configurations
source "$SCRIPT_DIR/core/shared.sh"
source "$(dirname "${BASH_SOURCE[0]}")/config.sh"

# --- Main Test Function ---
run_payments_test() {
    log_info "🚀 Starting Payments Module Test"
    log_info "================================="
    
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
    
    local payment_id=""
    
    # Create test payment
    payment_id=$(create_test_payment)
    if [ $? -ne 0 ]; then
        stop_worker "$QUEUE_NAME"
        return 1
    fi
    
    # Trigger webhook task
    local task_id=$(trigger_webhook_task "$payment_id")
    if [ $? -ne 0 ]; then
        cleanup_test_payment "$payment_id"
        stop_worker "$QUEUE_NAME"
        return 1
    fi
    
    # Wait for processing to complete
    log_info "⏳ Waiting for webhook processing (timeout: ${TEST_TIMEOUT}s)..."
    
    local count=0
    local success=false
    
    while [ $count -lt $TEST_TIMEOUT ]; do
        if check_payment_processing "$payment_id"; then
            success=true
            break
        fi
        
        sleep 2
        count=$((count + 2))
    done
    
    # Cleanup
    cleanup_test_payment "$payment_id"
    stop_worker "$QUEUE_NAME"
    
    if [ "$success" = true ]; then
        log_success "✅ Payments module test PASSED!"
        return 0
    else
        log_error "❌ Payments module test FAILED (timeout)"
        return 1
    fi
}

# --- Usage ---
usage() {
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Test payments webhook processing"
    echo ""
    echo "OPTIONS:"
    echo "  -q, --quick    Quick test (reduced timeouts)"
    echo "  -v, --verbose  Verbose output"
    echo "  -h, --help     Show this help"
}

# --- Parse Arguments ---
QUICK_MODE=false
VERBOSE=false

while [[ $# -gt 0 ]]; do
    case $1 in
        -q|--quick)
            QUICK_MODE=true
            export TEST_TIMEOUT="30"
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
    log_info "Quick mode enabled (reduced timeouts)"
fi

# --- Main Execution ---
if run_payments_test; then
    log_success "🎉 Payments test completed successfully!"
    exit 0
else
    log_error "❌ Payments test failed!"
    exit 1
fi
