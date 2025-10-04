"""
External Data and ExternalDataChunk related signals.
"""

from django.db.models.signals import post_save, post_delete
from django.db import models
from django.dispatch import receiver
from django.core.cache import cache
import logging

from ..models.external_data import ExternalData, ExternalDataChunk, ExternalDataStatus

logger = logging.getLogger(__name__)


@receiver(post_save, sender=ExternalData)
def external_data_post_save(sender, instance, created, **kwargs):
    """Handle external data creation and updates."""
    
    # Clear user's external data cache on any change
    cache_key = f"user_external_data:{instance.user.id}"
    cache.delete(cache_key)
    
    if created:
        # New external data - process if has content
        logger.info(f"🔗 New external data created: {instance.title} (ID: {instance.id})")
        if instance.content and instance.content.strip():
            _start_external_data_processing(instance)
        else:
            logger.debug(f"📝 External data created without content: {instance.title}")
        
    else:
        # External data update - check what changed
        update_fields = kwargs.get('update_fields')
        
        # Define fields that, if updated alone, should NOT trigger reprocessing
        processing_fields = {
            'status', 'processed_at', 'source_updated_at', 'processing_error',
            'total_chunks', 'total_tokens', 'processing_cost'
        }
        
        # If specific fields were updated, check if they are only processing-related
        if update_fields is not None:
            update_fields_set = set(update_fields) if update_fields else set()
            
            if update_fields_set and update_fields_set.issubset(processing_fields):
                # This is just a processing status update - don't reprocess
                logger.debug(f"📊 External data stats updated: {instance.title}")
                return
            
            # Check if content actually changed
            content_fields = {'content', 'content_hash', 'source_config', 'chunk_size', 'overlap_size', 'embedding_model'}
            if content_fields.intersection(update_fields_set):
                logger.info(f"📝 External data content updated: {instance.title} (ID: {instance.id})")
                
                # Only reprocess if there's content
                if instance.content and instance.content.strip():
                    # Clear existing chunks and reset processing state
                    _reset_external_data_processing(instance)
                    
                    # Start new processing
                    _start_external_data_processing(instance)
                else:
                    logger.debug(f"📝 External data updated but no content: {instance.title}")
            else:
                logger.debug(f"📊 External data non-content update: {instance.title} (fields: {update_fields_set})")
        else:
            # Full save without update_fields - check if content exists and processing is needed
            if instance.content and instance.content.strip():
                # Check if content hash changed (indicating content update)
                if hasattr(instance, '_original_content_hash'):
                    if instance.content_hash != instance._original_content_hash:
                        logger.info(f"🔮 External data content changed (hash mismatch), reprocessing: {instance.title}")
                        _reset_external_data_processing(instance)
                        _start_external_data_processing(instance)
                    else:
                        logger.debug(f"📊 External data saved but content unchanged: {instance.title}")
                elif instance.status == ExternalDataStatus.PENDING:
                    logger.info(f"🔮 External data saved, checking if processing needed: {instance.title}")
                    _start_external_data_processing(instance)


def _reset_external_data_processing(external_data):
    """Reset external data processing state and clear chunks."""
    logger.debug(f"🧹 Clearing chunks for external data: {external_data.title}")
    
    # Delete existing chunks
    external_data.chunks.all().delete()
    
    # Reset processing fields
    external_data.status = ExternalDataStatus.PENDING
    external_data.processed_at = None
    external_data.processing_error = ""
    external_data.total_chunks = 0
    external_data.total_tokens = 0
    external_data.processing_cost = 0.0
    
    # Save with explicit update_fields to avoid triggering this signal again
    external_data.save(update_fields=[
        'status', 'processed_at', 'processing_error',
        'total_chunks', 'total_tokens', 'processing_cost'
    ])


def _start_external_data_processing(external_data):
    """Start async external data processing."""
    try:
        # Lazy import to avoid middleware initialization issues
        from ..tasks.external_data_tasks import process_external_data_async
        process_external_data_async.send(str(external_data.id))
        logger.info(f"🚀 Started async processing for external data: {external_data.id}")
        
    except Exception as e:
        logger.error(f"❌ Failed to start external data processing: {e}")
        
        # Update external data status to failed
        external_data.status = ExternalDataStatus.FAILED
        external_data.processing_error = f"Failed to start processing: {e}"
        external_data.save(update_fields=['status', 'processing_error'])


@receiver(post_save, sender=ExternalDataChunk)
def external_data_chunk_post_save(sender, instance, created, **kwargs):
    """Handle external data chunk creation."""
    if created:
        logger.debug(f"🧩 New external data chunk created: {instance.external_data.title} chunk {instance.chunk_index}")
        
        # Update external data chunk count (this will trigger external data save with update_fields)
        external_data = instance.external_data
        external_data.total_chunks = external_data.chunks.count()
        external_data.save(update_fields=['total_chunks'])


@receiver(post_delete, sender=ExternalDataChunk)
def external_data_chunk_post_delete(sender, instance, **kwargs):
    """Handle external data chunk deletion."""
    try:
        logger.debug(f"🗑️ External data chunk deleted: {instance.external_data.title} chunk {instance.chunk_index}")
        
        # Update external data chunk count
        external_data = instance.external_data
        external_data.total_chunks = external_data.chunks.count()
        external_data.save(update_fields=['total_chunks'])
        
    except ExternalData.DoesNotExist:
        # External data was already deleted
        logger.debug("External data already deleted, skipping chunk count update")


@receiver(post_delete, sender=ExternalData)
def external_data_post_delete(sender, instance, **kwargs):
    """Handle external data deletion cleanup."""
    # Clear user's external data cache
    cache_key = f"user_external_data:{instance.user.id}"
    cache.delete(cache_key)
    
    logger.info(f"🗑️ External data deleted: {instance.title} (ID: {instance.id})")
