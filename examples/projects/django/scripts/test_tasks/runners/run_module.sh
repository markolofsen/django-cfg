#!/bin/bash

# Module Test Runner
# Runs tests for specific modules

set -e

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Load shared configuration
source "$SCRIPT_DIR/../core/shared.sh"

# --- Usage function ---
usage() {
    echo "Usage: $0 [OPTIONS] MODULE [TEST]"
    echo ""
    echo "Run tests for specific modules"
    echo ""
    echo "MODULES:"
    echo "  knowbase       Test knowbase document processing"
    echo "  payments       Test payments webhook processing"
    echo "  usage          Test payments usage tracking (Background Tasks)"
    echo ""
    echo "TESTS (optional):"
    echo "  full           Run full module test (default)"
    echo "  usage          Run usage tracking test (payments only)"
    echo ""
    echo "OPTIONS:"
    echo "  -q, --quick    Quick test (reduced timeouts)"
    echo "  -v, --verbose  Verbose output"
    echo "  -h, --help     Show this help"
    echo ""
    echo "EXAMPLES:"
    echo "  $0 knowbase              # Test knowbase module"
    echo "  $0 payments              # Test payments webhooks"
    echo "  $0 payments usage        # Test usage tracking"
    echo "  $0 --quick knowbase      # Quick knowbase test"
}

# --- Parse arguments ---
MODULE=""
TEST_TYPE="full"
QUICK_MODE=false
VERBOSE=false

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
        -h|--help)
            usage
            exit 0
            ;;
        knowbase|payments)
            MODULE="$1"
            shift
            ;;
        usage|full)
            TEST_TYPE="$1"
            shift
            ;;
        *)
            echo "Unknown option: $1"
            usage
            exit 1
            ;;
    esac
done

# Validate module
if [ -z "$MODULE" ]; then
    echo "Error: Module is required"
    usage
    exit 1
fi

# --- Main execution ---
main() {
    log_info "🚀 Running $MODULE module test ($TEST_TYPE)"
    log_info "=========================================="
    
    local test_script=""
    local quick_flag=""
    local verbose_flag=""
    
    # Set flags
    if [ "$QUICK_MODE" = true ]; then
        quick_flag="--quick"
    fi
    
    if [ "$VERBOSE" = true ]; then
        verbose_flag="--verbose"
    fi
    
    # Determine test script
    case "$MODULE" in
        knowbase)
            test_script="$SCRIPT_DIR/../modules/knowbase/test_knowbase.sh"
            ;;
        payments)
            if [ "$TEST_TYPE" = "usage" ]; then
                test_script="$SCRIPT_DIR/../modules/payments/test_usage_tracking.sh"
            else
                test_script="$SCRIPT_DIR/../modules/payments/test_payments.sh"
            fi
            ;;
        *)
            log_error "Unknown module: $MODULE"
            exit 1
            ;;
    esac
    
    # Check if test script exists
    if [ ! -f "$test_script" ]; then
        log_error "Test script not found: $test_script"
        exit 1
    fi
    
    # Make script executable
    chmod +x "$test_script"
    
    # Run test
    log_info "Executing: $test_script $quick_flag $verbose_flag"
    
    if "$test_script" $quick_flag $verbose_flag; then
        log_success "🎉 $MODULE test completed successfully!"
        exit 0
    else
        log_error "❌ $MODULE test failed!"
        exit 1
    fi
}

# Run main function
main "$@"
