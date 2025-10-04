#!/bin/bash

# Knowbase Task Testing Configuration

# Load shared configuration
source "$(dirname "${BASH_SOURCE[0]}")/../../core/shared.sh"

# --- Knowbase-specific Configuration ---
export QUEUE_NAME="knowbase"
export TEST_USER_EMAIL="knowbase_test@example.com"
export TEST_DOCUMENT_TITLE="Knowbase Test Document"

# --- Test Content ---
export TEST_DOCUMENT_CONTENT="This is a comprehensive test document to verify the complete end-to-end functionality of the Knowbase task processing pipeline within the Django-CFG framework. It includes multiple sentences and paragraphs to ensure proper chunking and embedding generation. The system should handle this document, break it into smaller chunks, generate vector embeddings for each chunk, and store them in the database. This process is triggered automatically via Django signals upon document creation. We will monitor the logs to confirm each step of the asynchronous processing. Additional content to ensure multiple chunks are created during processing. This helps test the batch processing capabilities and ensures the system can handle documents of various sizes effectively."

# --- Knowbase-specific Functions ---
create_test_document() {
    log_info "Creating test document for knowbase..."
    
    cd "$DJANGO_PROJECT_DIR"
    
    # Create document via Django shell
    local result=$(poetry run python manage.py shell -c "
from django.contrib.auth import get_user_model
from django_cfg.apps.knowbase.models import Document
import uuid

User = get_user_model()

# Get or create test user
user, created = User.objects.get_or_create(
    email='$TEST_USER_EMAIL',
    defaults={'username': 'knowbase_test_user'}
)

# Create test document
document = Document.objects.create(
    title='$TEST_DOCUMENT_TITLE',
    content='$TEST_DOCUMENT_CONTENT',
    user=user,
    content_type='text/plain'
)

print(f'DOCUMENT_ID:{document.id}')
" 2>/dev/null)
    
    local document_id=$(echo "$result" | grep "DOCUMENT_ID:" | cut -d: -f2)
    
    if [ -n "$document_id" ]; then
        log_success "Test document created with ID: $document_id"
        echo "$document_id"
        return 0
    else
        log_error "Failed to create test document"
        return 1
    fi
}

check_document_processing() {
    local document_id="$1"
    
    log_info "Checking document processing status..."
    
    cd "$DJANGO_PROJECT_DIR"
    
    # Check document status via Django shell
    local result=$(poetry run python manage.py shell -c "
from django_cfg.apps.knowbase.models import Document, DocumentChunk

try:
    document = Document.objects.get(id='$document_id')
    chunks = DocumentChunk.objects.filter(document=document)
    
    print(f'STATUS:{document.status}')
    print(f'CHUNKS:{chunks.count()}')
    print(f'PROCESSED:{document.status == \"completed\"}')
except Document.DoesNotExist:
    print('STATUS:not_found')
    print('CHUNKS:0')
    print('PROCESSED:false')
" 2>/dev/null)
    
    local status=$(echo "$result" | grep "STATUS:" | cut -d: -f2)
    local chunks=$(echo "$result" | grep "CHUNKS:" | cut -d: -f2)
    local processed=$(echo "$result" | grep "PROCESSED:" | cut -d: -f2)
    
    log_info "Document status: $status"
    log_info "Document chunks: $chunks"
    
    if [ "$processed" = "True" ] && [ "$chunks" -gt 0 ]; then
        log_success "Document processing completed successfully"
        return 0
    else
        return 1
    fi
}

cleanup_test_document() {
    local document_id="$1"
    
    if [ -n "$document_id" ]; then
        log_info "Cleaning up test document..."
        
        cd "$DJANGO_PROJECT_DIR"
        
        poetry run python manage.py shell -c "
from django_cfg.apps.knowbase.models import Document

try:
    document = Document.objects.get(id='$document_id')
    document.delete()
    print('Document deleted')
except Document.DoesNotExist:
    print('Document not found')
" >/dev/null 2>&1
        
        log_success "Test document cleanup completed"
    fi
}

# Export knowbase-specific functions
export -f create_test_document check_document_processing cleanup_test_document
