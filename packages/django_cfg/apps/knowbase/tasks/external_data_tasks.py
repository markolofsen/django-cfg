"""
External Data processing tasks with Dramatiq.
"""

import dramatiq
import logging
import time
from typing import Dict, List, Any, Tuple, Optional
from django.db import transaction
from django.utils import timezone

from ..models.external_data import ExternalData, ExternalDataChunk, ExternalDataStatus
from ..mixins.service import ExternalDataService

logger = logging.getLogger(__name__)


@dramatiq.actor(
    queue_name="knowbase",
    max_retries=3,
    min_backoff=1000,  # 1 second
    max_backoff=30000,  # 30 seconds
    priority=5
)
def process_external_data_async(
    external_data_id: str,
    force_reprocess: bool = False
) -> Dict[str, Any]:
    """
    Process external data asynchronously with full pipeline.
    
    Args:
        external_data_id: ExternalData UUID to process
        force_reprocess: Force reprocessing even if already completed
        
    Returns:
        Processing results with statistics
    """
    start_time = time.time()
    
    try:
        with transaction.atomic():
            # Get external data instance
            external_data = ExternalData.objects.select_for_update().get(id=external_data_id)
            
            # Check if already processing
            if external_data.status == ExternalDataStatus.PROCESSING:
                logger.warning(f"External data {external_data_id} is already being processed")
                return {
                    'success': False,
                    'error': 'Already processing',
                    'external_data_id': external_data_id
                }
            
            # Check if already completed and not forcing reprocess
            if external_data.status == ExternalDataStatus.COMPLETED and not force_reprocess:
                logger.info(f"External data {external_data_id} already completed, skipping")
                return {
                    'success': True,
                    'skipped': True,
                    'external_data_id': external_data_id,
                    'total_chunks': external_data.total_chunks,
                    'total_tokens': external_data.total_tokens,
                    'processing_cost': external_data.processing_cost
                }
            
            # Check if has content
            if not external_data.content or not external_data.content.strip():
                logger.warning(f"External data {external_data_id} has no content to process")
                external_data.status = ExternalDataStatus.COMPLETED
                external_data.processed_at = timezone.now()
                external_data.total_chunks = 0
                external_data.total_tokens = 0
                external_data.processing_cost = 0.0
                external_data.save(update_fields=[
                    'status', 'processed_at', 'total_chunks', 
                    'total_tokens', 'processing_cost'
                ])
                return {
                    'success': True,
                    'external_data_id': external_data_id,
                    'total_chunks': 0,
                    'total_tokens': 0,
                    'processing_cost': 0.0,
                    'processing_time': time.time() - start_time
                }
            
            logger.info(f"🚀 Starting external data processing: {external_data.title} (ID: {external_data_id})")
            
            # Update status to processing
            external_data.status = ExternalDataStatus.PROCESSING
            external_data.processing_error = ""
            external_data.save(update_fields=['status', 'processing_error'])
        
        # Process external data using service (outside transaction for long-running operations)
        service = ExternalDataService(external_data.user)
        success = service.vectorize_external_data(external_data)
        
        # Refresh from database to get updated statistics
        external_data.refresh_from_db()
        
        processing_time = time.time() - start_time
        
        if success:
            logger.info(
                f"✅ External data processing completed: {external_data.title} "
                f"({external_data.total_chunks} chunks, {external_data.total_tokens} tokens, "
                f"${external_data.processing_cost:.6f}, {processing_time:.2f}s)"
            )
            
            return {
                'success': True,
                'external_data_id': external_data_id,
                'title': external_data.title,
                'total_chunks': external_data.total_chunks,
                'total_tokens': external_data.total_tokens,
                'processing_cost': external_data.processing_cost,
                'processing_time': processing_time
            }
        else:
            logger.error(f"❌ External data processing failed: {external_data.title}")
            return {
                'success': False,
                'external_data_id': external_data_id,
                'error': external_data.processing_error or 'Unknown processing error',
                'processing_time': processing_time
            }
            
    except ExternalData.DoesNotExist:
        error_msg = f"External data {external_data_id} not found"
        logger.error(f"❌ {error_msg}")
        return {
            'success': False,
            'error': error_msg,
            'external_data_id': external_data_id
        }
        
    except Exception as e:
        processing_time = time.time() - start_time
        error_msg = f"Unexpected error processing external data {external_data_id}: {e}"
        logger.error(f"❌ {error_msg}", exc_info=True)
        
        # Try to update status to failed
        try:
            external_data = ExternalData.objects.get(id=external_data_id)
            external_data.status = ExternalDataStatus.FAILED
            external_data.processing_error = str(e)
            external_data.save(update_fields=['status', 'processing_error'])
        except Exception as save_error:
            logger.error(f"❌ Failed to update external data status: {save_error}")
        
        return {
            'success': False,
            'error': error_msg,
            'external_data_id': external_data_id,
            'processing_time': processing_time
        }


@dramatiq.actor(
    queue_name="knowbase",
    max_retries=2,
    min_backoff=5000,  # 5 seconds
    max_backoff=60000,  # 60 seconds
    priority=3
)
def bulk_process_external_data_async(
    user_id: int,
    external_data_ids: Optional[List[str]] = None,
    force_reprocess: bool = False
) -> Dict[str, Any]:
    """
    Process multiple external data sources asynchronously.
    
    Args:
        user_id: User ID to process external data for
        external_data_ids: Specific external data IDs to process (None for all pending)
        force_reprocess: Force reprocessing even if already completed
        
    Returns:
        Bulk processing results with statistics
    """
    start_time = time.time()
    
    try:
        from django.contrib.auth import get_user_model
        User = get_user_model()
        user = User.objects.get(id=user_id)
        
        # Get external data to process
        if external_data_ids:
            external_data_queryset = ExternalData.objects.filter(
                id__in=external_data_ids,
                user=user
            )
        else:
            # Process all pending external data for user
            external_data_queryset = ExternalData.objects.filter(
                user=user,
                status=ExternalDataStatus.PENDING
            )
        
        external_data_list = list(external_data_queryset)
        total_count = len(external_data_list)
        
        if total_count == 0:
            logger.info(f"No external data to process for user {user_id}")
            return {
                'success': True,
                'user_id': user_id,
                'total_count': 0,
                'processed_count': 0,
                'failed_count': 0,
                'skipped_count': 0,
                'processing_time': time.time() - start_time
            }
        
        logger.info(f"🚀 Starting bulk external data processing for user {user_id}: {total_count} items")
        
        # Process each external data
        processed_count = 0
        failed_count = 0
        skipped_count = 0
        results = []
        
        for external_data in external_data_list:
            try:
                result = process_external_data_async.send(
                    str(external_data.id),
                    force_reprocess=force_reprocess
                )
                
                if result.get('success'):
                    if result.get('skipped'):
                        skipped_count += 1
                    else:
                        processed_count += 1
                else:
                    failed_count += 1
                
                results.append(result)
                
            except Exception as e:
                logger.error(f"❌ Failed to queue external data {external_data.id}: {e}")
                failed_count += 1
                results.append({
                    'success': False,
                    'external_data_id': str(external_data.id),
                    'error': f'Failed to queue: {e}'
                })
        
        processing_time = time.time() - start_time
        
        logger.info(
            f"✅ Bulk external data processing queued for user {user_id}: "
            f"{processed_count} processed, {failed_count} failed, "
            f"{skipped_count} skipped out of {total_count} total ({processing_time:.2f}s)"
        )
        
        return {
            'success': True,
            'user_id': user_id,
            'total_count': total_count,
            'processed_count': processed_count,
            'failed_count': failed_count,
            'skipped_count': skipped_count,
            'processing_time': processing_time,
            'results': results
        }
        
    except Exception as e:
        processing_time = time.time() - start_time
        error_msg = f"Unexpected error in bulk external data processing for user {user_id}: {e}"
        logger.error(f"❌ {error_msg}", exc_info=True)
        
        return {
            'success': False,
            'error': error_msg,
            'user_id': user_id,
            'processing_time': processing_time
        }


@dramatiq.actor(
    queue_name="maintenance",
    max_retries=1,
    priority=1
)
def cleanup_failed_external_data_async(older_than_days: int = 7) -> Dict[str, Any]:
    """
    Clean up old failed external data processing attempts.
    
    Args:
        older_than_days: Remove failed external data older than this many days
        
    Returns:
        Cleanup results
    """
    start_time = time.time()
    
    try:
        from django.utils import timezone
        from datetime import timedelta
        
        cutoff_date = timezone.now() - timedelta(days=older_than_days)
        
        # Find failed external data older than cutoff
        failed_external_data = ExternalData.objects.filter(
            status=ExternalDataStatus.FAILED,
            updated_at__lt=cutoff_date
        )
        
        count = failed_external_data.count()
        
        if count > 0:
            logger.info(f"🧹 Cleaning up {count} failed external data older than {older_than_days} days")
            deleted_count, _ = failed_external_data.delete()
            logger.info(f"✅ Cleaned up {deleted_count} failed external data records")
        else:
            logger.info(f"No failed external data older than {older_than_days} days found")
            deleted_count = 0
        
        processing_time = time.time() - start_time
        
        return {
            'success': True,
            'deleted_count': deleted_count,
            'older_than_days': older_than_days,
            'processing_time': processing_time
        }
        
    except Exception as e:
        processing_time = time.time() - start_time
        error_msg = f"Error cleaning up failed external data: {e}"
        logger.error(f"❌ {error_msg}", exc_info=True)
        
        return {
            'success': False,
            'error': error_msg,
            'processing_time': processing_time
        }
