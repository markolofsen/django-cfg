"""
Document and DocumentChunk related signals.
"""

from django.db.models.signals import post_save, post_delete
from django.db import models
from django.dispatch import receiver
from django.core.cache import cache
import logging

from ..models import Document, DocumentChunk, ProcessingStatus

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Document)
def document_post_save(sender, instance, created, **kwargs):
    """Handle document creation and updates."""
    
    # Clear user's document cache on any document change
    cache_key = f"user_documents:{instance.user.id}"
    cache.delete(cache_key)
    
    if created:
        # New document - always process
        logger.info(f"📄 New document created: {instance.title} (ID: {instance.id})")
        _start_document_processing(instance)
        
    else:
        # Document update - check what changed
        update_fields = kwargs.get('update_fields')
        
        # Define fields that, if updated alone, should NOT trigger reprocessing
        processing_fields = {
            'processing_status', 'processing_started_at', 'processing_completed_at',
            'processing_error', 'chunks_count', 'total_tokens', 'total_cost_usd'
        }
        
        # If specific fields were updated, check if they are only processing-related
        if update_fields is not None:
            update_fields_set = set(update_fields) if update_fields else set()
            
            if update_fields_set and update_fields_set.issubset(processing_fields):
                # This is just a processing status update - don't reprocess
                logger.debug(f"📊 Document stats updated: {instance.title}")
                return
            
            # Check if content actually changed
            content_fields = {'content', 'content_hash'}
            if content_fields.intersection(update_fields_set):
                logger.info(f"📝 Document content updated: {instance.title} (ID: {instance.id})")
                
                # Clear existing chunks and reset processing state
                _reset_document_processing(instance)
                
                # Start new processing
                _start_document_processing(instance)
            else:
                logger.debug(f"📊 Document non-content update: {instance.title} (fields: {update_fields_set})")
        else:
            # Full save without update_fields specified (e.g., from admin save button or manual save())
            # Assume content might have changed and reprocess
            logger.info(f"📝 Document saved without specific fields, assuming content update: {instance.title} (ID: {instance.id})")
            _reset_document_processing(instance)
            _start_document_processing(instance)


def _reset_document_processing(document):
    """Reset document processing state and clear chunks."""
    logger.debug(f"🧹 Clearing chunks for document: {document.title}")
    
    # Delete existing chunks
    document.chunks.all().delete()
    
    # Reset processing fields
    document.processing_status = "pending"
    document.processing_started_at = None
    document.processing_completed_at = None
    document.processing_error = ""
    document.chunks_count = 0
    document.total_tokens = 0
    document.total_cost_usd = 0
    
    # Save with explicit update_fields to avoid triggering this signal again
    document.save(update_fields=[
        'processing_status', 'processing_started_at', 'processing_completed_at',
        'processing_error', 'chunks_count', 'total_tokens', 'total_cost_usd'
    ])


def _start_document_processing(document):
    """Start async document processing."""
    try:
        # Lazy import to avoid middleware initialization issues
        from ..tasks.document_processing import process_document_async
        process_document_async.send(str(document.id))
        logger.info(f"🚀 Started async processing for document: {document.id}")
        
    except Exception as e:
        logger.error(f"❌ Failed to start document processing: {e}")
        
        # Update document status to failed
        document.processing_status = ProcessingStatus.FAILED
        document.processing_error = f"Failed to start processing: {e}"
        document.save(update_fields=['processing_status', 'processing_error'])


@receiver(post_save, sender=DocumentChunk)
def chunk_post_save(sender, instance, created, **kwargs):
    """Handle chunk creation."""
    if created:
        logger.debug(f"🧩 New chunk created: {instance.document.title} chunk {instance.chunk_index}")
        
        # Update document chunk count (this will trigger document save with update_fields)
        document = instance.document
        document.chunks_count = document.chunks.count()
        document.save(update_fields=['chunks_count'])


@receiver(post_delete, sender=DocumentChunk)
def chunk_post_delete(sender, instance, **kwargs):
    """Handle chunk deletion."""
    try:
        logger.debug(f"🗑️ Chunk deleted: {instance.document.title} chunk {instance.chunk_index}")
        
        # Update document chunk count
        document = instance.document
        document.chunks_count = document.chunks.count()
        document.save(update_fields=['chunks_count'])
        
    except Document.DoesNotExist:
        # Document was already deleted
        logger.debug("Document already deleted, skipping chunk count update")


@receiver(post_delete, sender=Document)
def document_post_delete(sender, instance, **kwargs):
    """Handle document deletion cleanup."""
    # Clear user's document cache
    cache_key = f"user_documents:{instance.user.id}"
    cache.delete(cache_key)
    
    logger.info(f"🗑️ Document deleted: {instance.title} (ID: {instance.id})")
