#!/bin/bash

# Unified Django-CFG Task Testing System
# Tests all task queues (knowbase, payments) in a unified way

set -e

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Load shared configuration
source "$SCRIPT_DIR/../core/shared.sh"

# --- Usage function ---
usage() {
    echo "Usage: $0 [OPTIONS] [MODULES...]"
    echo ""
    echo "Test django-cfg task queues"
    echo ""
    echo "MODULES:"
    echo "  knowbase   Test knowbase document processing tasks"
    echo "  payments   Test payments webhook processing tasks"
    echo "  all        Test all modules (default)"
    echo ""
    echo "OPTIONS:"
    echo "  -q, --quick    Quick test (reduced timeouts)"
    echo "  -v, --verbose  Verbose output"
    echo "  -c, --cleanup  Clean up test data and exit"
    echo "  -h, --help     Show this help"
    echo ""
    echo "EXAMPLES:"
    echo "  $0                    # Test all modules"
    echo "  $0 knowbase           # Test only knowbase"
    echo "  $0 payments           # Test only payments"
    echo "  $0 knowbase payments  # Test both modules"
    echo "  $0 --quick all        # Quick test of all modules"
    echo "  $0 --cleanup          # Clean up and exit"
}

# --- Parse arguments ---
MODULES=()
QUICK_MODE=false
VERBOSE=false
CLEANUP_ONLY=false

while [[ $# -gt 0 ]]; do
    case $1 in
        -q|--quick)
            QUICK_MODE=true
            shift
            ;;
        -v|--verbose)
            VERBOSE=true
            shift
            ;;
        -c|--cleanup)
            CLEANUP_ONLY=true
            shift
            ;;
        -h|--help)
            usage
            exit 0
            ;;
        knowbase|payments|all)
            MODULES+=("$1")
            shift
            ;;
        *)
            echo "Unknown option: $1"
            usage
            exit 1
            ;;
    esac
done

# Default to all modules if none specified
if [ ${#MODULES[@]} -eq 0 ] || [[ " ${MODULES[@]} " =~ " all " ]]; then
    MODULES=(knowbase payments)
fi

# Handle cleanup only
if [ "$CLEANUP_ONLY" = true ]; then
    log_info "Cleanup mode - stopping all workers and cleaning up..."
    cleanup_all
    exit 0
fi

# Adjust timeouts for quick mode
if [ "$QUICK_MODE" = true ]; then
    export TEST_TIMEOUT="30"
    export DRAMATIQ_TIMEOUT="30"
    log_info "Quick mode enabled (timeouts reduced to 30s)"
fi

# --- Main test function ---
test_module() {
    local module="$1"
    
    log_info "===================="
    log_info "Testing $module module"
    log_info "===================="
    
    # Load module-specific configuration
    source "$SCRIPT_DIR/../modules/$module/config.sh"
    
    # Start worker for this module
    if ! start_worker "$QUEUE_NAME"; then
        log_error "Failed to start $module worker"
        return 1
    fi
    
    # Wait for worker to be ready
    sleep 3
    
    # Run module-specific tests
    case $module in
        knowbase)
            test_knowbase_module
            ;;
        payments)
            test_payments_module
            ;;
        *)
            log_error "Unknown module: $module"
            return 1
            ;;
    esac
    
    local result=$?
    
    # Stop worker
    stop_worker "$QUEUE_NAME"
    
    return $result
}

# --- Knowbase testing function ---
test_knowbase_module() {
    log_info "🔧 Testing knowbase document processing..."
    
    # Create test document
    local document_id=$(create_test_document)
    if [ $? -ne 0 ]; then
        log_error "Failed to create test document"
        return 1
    fi
    
    # Wait for processing to complete
    log_info "⏳ Waiting for document processing (timeout: ${TEST_TIMEOUT}s)..."
    
    local count=0
    local success=false
    
    while [ $count -lt $TEST_TIMEOUT ]; do
        if check_document_processing "$document_id"; then
            success=true
            break
        fi
        
        sleep 2
        count=$((count + 2))
    done
    
    # Cleanup
    cleanup_test_document "$document_id"
    
    if [ "$success" = true ]; then
        log_success "Knowbase module test PASSED"
        return 0
    else
        log_error "Knowbase module test FAILED (timeout)"
        return 1
    fi
}

# --- Payments testing function ---
test_payments_module() {
    log_info "🔧 Testing payments webhook processing..."
    
    # Create test payment
    local payment_id=$(create_test_payment)
    if [ $? -ne 0 ]; then
        log_error "Failed to create test payment"
        return 1
    fi
    
    # Trigger webhook task
    local task_id=$(trigger_webhook_task "$payment_id")
    if [ $? -ne 0 ]; then
        log_error "Failed to trigger webhook task"
        cleanup_test_payment "$payment_id"
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
    
    if [ "$success" = true ]; then
        log_success "Payments module test PASSED"
        return 0
    else
        log_error "Payments module test FAILED (timeout)"
        return 1
    fi
}

# --- Main execution ---
main() {
    log_info "🚀 Django-CFG Unified Task Testing System"
    log_info "==========================================="
    
    # Validate environment
    if ! validate_environment; then
        log_error "Environment validation failed"
        exit 1
    fi
    
    log_info "Testing modules: ${MODULES[*]}"
    
    local total_tests=${#MODULES[@]}
    local passed_tests=0
    local failed_tests=0
    
    # Run tests for each module
    for module in "${MODULES[@]}"; do
        if test_module "$module"; then
            passed_tests=$((passed_tests + 1))
        else
            failed_tests=$((failed_tests + 1))
        fi
        
        # Small delay between modules
        sleep 2
    done
    
    # Summary
    log_info "========================================="
    log_info "Test Summary"
    log_info "========================================="
    log_info "Total tests: $total_tests"
    log_success "Passed: $passed_tests"
    
    if [ $failed_tests -gt 0 ]; then
        log_error "Failed: $failed_tests"
        log_error "Overall result: FAILED"
        exit 1
    else
        log_success "Failed: $failed_tests"
        log_success "Overall result: ALL TESTS PASSED! 🎉"
        exit 0
    fi
}

# Run main function
main "$@"
