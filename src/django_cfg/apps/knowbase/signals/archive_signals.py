"""
Archive processing signals.
"""

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.cache import cache
import logging

from ..models import DocumentArchive, ArchiveItem, ArchiveItemChunk

logger = logging.getLogger(__name__)


@receiver(post_save, sender=DocumentArchive)
def archive_post_save(sender, instance, created, **kwargs):
    """Handle archive creation and updates."""
    
    # Clear user's archive cache on any archive change
    cache_key = f"user_archives:{instance.user.id}"
    cache.delete(cache_key)
    
    if created and instance.archive_file:
        # New archive with file - start processing
        logger.info(f"📦 New archive created: {instance.title} (ID: {instance.id})")
        _start_archive_processing(instance)
        
    elif not created:
        # Archive update - check what changed
        update_fields = kwargs.get('update_fields')
        
        # Define fields that, if updated alone, should NOT trigger reprocessing
        processing_fields = {
            'processing_status', 'processed_at', 'processing_duration_ms',
            'processing_error', 'total_items', 'processed_items', 'total_chunks',
            'vectorized_chunks', 'total_tokens', 'total_cost_usd'
        }
        
        # If specific fields were updated, check if they are only processing-related
        if update_fields is not None:
            update_fields_set = set(update_fields) if update_fields else set()
            
            if update_fields_set and update_fields_set.issubset(processing_fields):
                # This is just a processing status update - don't reprocess
                logger.debug(f"📊 Archive stats updated: {instance.title}")
                return
            
            # Check if archive file was updated
            if 'archive_file' in update_fields_set and instance.archive_file:
                logger.info(f"📦 Archive file updated: {instance.title} (ID: {instance.id})")
                
                # Clear existing items and reset processing state
                _reset_archive_processing(instance)
                
                # Start new processing
                _start_archive_processing(instance)
            else:
                logger.debug(f"📊 Archive non-file update: {instance.title} (fields: {update_fields_set})")
        else:
            # Full save without update_fields - check if file exists and process if needed
            if instance.archive_file and instance.processing_status == 'pending':
                logger.info(f"📦 Archive saved, checking if processing needed: {instance.title}")
                _start_archive_processing(instance)


def _reset_archive_processing(archive):
    """Reset archive processing state and clear items."""
    logger.debug(f"🧹 Clearing items for archive: {archive.title}")
    
    # Delete existing items (cascades to chunks)
    archive.items.all().delete()
    
    # Reset processing fields
    archive.processing_status = "pending"
    archive.processed_at = None
    archive.processing_duration_ms = 0
    archive.processing_error = ""
    archive.total_items = 0
    archive.processed_items = 0
    archive.total_chunks = 0
    archive.vectorized_chunks = 0
    archive.total_tokens = 0
    archive.total_cost_usd = 0
    
    # Save with explicit update_fields to avoid triggering this signal again
    archive.save(update_fields=[
        'processing_status', 'processed_at', 'processing_duration_ms',
        'processing_error', 'total_items', 'processed_items', 'total_chunks',
        'vectorized_chunks', 'total_tokens', 'total_cost_usd'
    ])


def _start_archive_processing(archive):
    """Start async archive processing."""
    try:
        # Lazy import to avoid middleware initialization issues
        from ..tasks.archive_tasks import process_archive_task
        process_archive_task.send(str(archive.id), str(archive.user.id))
        logger.info(f"🚀 Started async processing for archive: {archive.id}")
        
    except Exception as e:
        logger.error(f"❌ Failed to start archive processing: {e}")
        
        # Update archive status to failed
        archive.processing_status = "failed"
        archive.processing_error = f"Failed to start processing: {e}"
        archive.save(update_fields=['processing_status', 'processing_error'])


@receiver(post_save, sender=ArchiveItem)
def archive_item_post_save(sender, instance, created, **kwargs):
    """Handle archive item creation."""
    if created:
        logger.debug(f"📄 New archive item created: {instance.archive.title} - {instance.item_name}")
        
        # Update archive item count
        archive = instance.archive
        archive.total_items = archive.items.count()
        archive.save(update_fields=['total_items'])


@receiver(post_delete, sender=ArchiveItem)
def archive_item_post_delete(sender, instance, **kwargs):
    """Handle archive item deletion."""
    try:
        # Safely get archive - it might be deleted already due to cascade
        try:
            archive = instance.archive
            archive_title = archive.title
        except (AttributeError, DocumentArchive.DoesNotExist):
            logger.debug("⚠️ Archive already deleted, skipping item count update")
            return
            
        logger.debug(f"🗑️ Archive item deleted: {archive_title} - {instance.item_name}")
        
        # Update archive item count
        archive.total_items = archive.items.count()
        archive.save(update_fields=['total_items'])
        
    except DocumentArchive.DoesNotExist:
        # Archive was already deleted
        logger.debug("Archive already deleted, skipping item count update")
    except Exception as e:
        logger.error(f"❌ Error in archive item post-delete signal: {e}")
        # Don't re-raise to avoid breaking deletion


@receiver(post_save, sender=ArchiveItemChunk)
def archive_chunk_post_save(sender, instance, created, **kwargs):
    """Handle archive chunk creation."""
    if created:
        logger.debug(f"🧩 New archive chunk created: {instance.item.item_name} chunk {instance.chunk_index}")
        
        # Update archive chunk count
        archive = instance.archive
        archive.total_chunks = ArchiveItemChunk.objects.filter(archive=archive).count()
        
        # Update vectorized chunks count
        archive.vectorized_chunks = ArchiveItemChunk.objects.filter(
            archive=archive, 
            embedding__isnull=False
        ).count()
        
        archive.save(update_fields=['total_chunks', 'vectorized_chunks'])


@receiver(post_delete, sender=ArchiveItemChunk)
def archive_chunk_post_delete(sender, instance, **kwargs):
    """Handle archive chunk deletion."""
    try:
        # Safely get item name - item might be deleted already due to cascade
        try:
            item_name = instance.item.item_name if hasattr(instance, 'item') and instance.item else "unknown"
        except (AttributeError, ArchiveItem.DoesNotExist):
            item_name = "unknown"
            
        logger.debug(f"🗑️ Archive chunk deleted: {item_name} chunk {instance.chunk_index}")
        
        # Update archive chunk counts - get archive through item if available
        try:
            if hasattr(instance, 'item') and instance.item:
                archive = instance.item.archive
            else:
                # If item is already deleted, we can't update counts safely
                logger.debug("⚠️ Cannot update chunk counts - parent item already deleted")
                return
                
            archive.total_chunks = ArchiveItemChunk.objects.filter(item__archive=archive).count()
            archive.vectorized_chunks = ArchiveItemChunk.objects.filter(
                item__archive=archive, 
                embedding__isnull=False
            ).count()
            
            archive.save(update_fields=['total_chunks', 'vectorized_chunks'])
            
        except (AttributeError, ArchiveItem.DoesNotExist, DocumentArchive.DoesNotExist):
            logger.debug("⚠️ Cannot update chunk counts - related objects already deleted")
        
    except Exception as e:
        logger.error(f"❌ Error in archive chunk post-delete signal: {e}")
        # Don't re-raise to avoid breaking deletion


@receiver(post_delete, sender=DocumentArchive)
def archive_post_delete(sender, instance, **kwargs):
    """Handle archive deletion cleanup."""
    # Clear user's archive cache
    cache_key = f"user_archives:{instance.user.id}"
    cache.delete(cache_key)
    
    logger.info(f"🗑️ Archive deleted: {instance.title} (ID: {instance.id})")
