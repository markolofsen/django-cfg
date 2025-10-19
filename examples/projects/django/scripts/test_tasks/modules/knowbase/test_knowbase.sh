#!/bin/bash

# Knowbase Module Test
# Tests document processing and chunking functionality

set -e

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

# Load configurations
source "$SCRIPT_DIR/core/shared.sh"
source "$(dirname "${BASH_SOURCE[0]}")/config.sh"

# --- Main Test Function ---
run_knowbase_test() {
    log_info "🚀 Starting Knowbase Module Test"
    log_info "================================="
    
    # Validate environment
    if ! validate_environment; then
        log_error "Environment validation failed"
        return 1
    fi
    
    # Start worker
    if ! start_worker "$QUEUE_NAME"; then
        log_error "Failed to start knowbase worker"
        return 1
    fi
    
    # Wait for worker to be ready
    log_info "Waiting for worker to be ready..."
    sleep 3
    
    local document_id=""
    
    # Create test document
    document_id=$(create_test_document)
    if [ $? -ne 0 ]; then
        stop_worker "$QUEUE_NAME"
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
    stop_worker "$QUEUE_NAME"
    
    if [ "$success" = true ]; then
        log_success "✅ Knowbase module test PASSED!"
        return 0
    else
        log_error "❌ Knowbase module test FAILED (timeout)"
        return 1
    fi
}

# --- Usage ---
usage() {
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Test knowbase document processing"
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
if run_knowbase_test; then
    log_success "🎉 Knowbase test completed successfully!"
    exit 0
else
    log_error "❌ Knowbase test failed!"
    exit 1
fi
