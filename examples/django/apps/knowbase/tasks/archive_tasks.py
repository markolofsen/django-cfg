"""
Archive processing tasks with Dramatiq.
"""

import dramatiq
import logging
import time
from typing import Dict, Any
from django.db import transaction
from django.utils import timezone
from django.contrib.auth import get_user_model

from ..models.archive import DocumentArchive, ArchiveItem, ArchiveItemChunk
from ..models.base import ProcessingStatus
from ..services.archive import (
    DocumentArchiveService,
    ArchiveVectorizationService,
    ArchiveProcessingError
)

logger = logging.getLogger(__name__)
User = get_user_model()


@dramatiq.actor(
    queue_name="knowbase",
    max_retries=3,
    min_backoff=1000,  # 1 second
    max_backoff=30000,  # 30 seconds
    priority=5
)
def process_archive_task(archive_id: str, user_id: str) -> bool:
    """
    Process a document archive asynchronously.
    
    Args:
        archive_id: ID of the archive to process
        user_id: ID of the user who owns the archive
        
    Returns:
        True if processing was successful
        
    Raises:
        ArchiveProcessingError: If processing fails
    """
    logger.info(f"Starting archive processing for archive {archive_id}")
    
    try:
        # Get archive and user
        archive = DocumentArchive.objects.all_users().get(pk=archive_id)
        user = User.objects.get(pk=user_id)
        
        # Debug logging
        logger.info(f"Retrieved archive: {archive}, type: {type(archive)}")
        logger.info(f"Archive ID: {archive.id if archive else 'None'}")
        logger.info(f"Archive file: {archive.archive_file if archive else 'None'}")
        
        if not archive:
            raise ArchiveProcessingError(
                message=f"Archive {archive_id} not found or is None",
                code="ARCHIVE_NOT_FOUND"
            )
        
        # Verify user owns the archive
        if archive.user_id != user.id:
            raise ArchiveProcessingError(
                message=f"User {user_id} does not own archive {archive_id}",
                code="UNAUTHORIZED_ACCESS"
            )
        
        # Initialize services
        service = DocumentArchiveService(user=user)
        
        # Process the archive (remove transaction.atomic to avoid nested transaction conflicts)
        success = service.process_archive(archive)
            
        if success:
            logger.info(f"Successfully processed archive {archive_id}")
            return True
        else:
            logger.error(f"Failed to process archive {archive_id}")
            return False
            
    except DocumentArchive.DoesNotExist:
        logger.error(f"Archive {archive_id} not found")
        raise
    except User.DoesNotExist:
        logger.error(f"User {user_id} not found")
        raise
    except Exception as e:
        logger.error(f"Error processing archive {archive_id}: {str(e)}")
        raise ArchiveProcessingError(
            message=f"Archive processing failed: {str(e)}",
            code="PROCESSING_FAILED"
        )


@dramatiq.actor(
    queue_name="knowbase",
    max_retries=2,
    min_backoff=2000,  # 2 seconds
    max_backoff=60000,  # 60 seconds
    priority=4
)
def vectorize_archive_items_task(archive_id: str, user_id: str) -> int:
    """
    Vectorize all items in a document archive.
    
    Args:
        archive_id: ID of the archive to vectorize
        user_id: ID of the user who owns the archive
        
    Returns:
        Number of items vectorized
        
    Raises:
        ArchiveProcessingError: If vectorization fails
    """
    logger.info(f"Starting vectorization for archive {archive_id}")
    
    try:
        # Get archive and user
        archive = DocumentArchive.objects.all_users().get(pk=archive_id)
        user = User.objects.get(pk=user_id)
        
        # Verify user owns the archive
        if archive.user_id != user.id:
            raise ArchiveProcessingError(
                message=f"User {user_id} does not own archive {archive_id}",
                code="UNAUTHORIZED_ACCESS"
            )
        
        # Initialize vectorization service
        service = ArchiveVectorizationService(user=user)
        
        # Vectorize archive items
        vectorized_count = service.vectorize_archive_items(archive)
        
        logger.info(f"Successfully vectorized {vectorized_count} items for archive {archive_id}")
        return vectorized_count
        
    except DocumentArchive.DoesNotExist:
        logger.error(f"Archive {archive_id} not found")
        raise
    except User.DoesNotExist:
        logger.error(f"User {user_id} not found")
        raise
    except Exception as e:
        logger.error(f"Error vectorizing archive {archive_id}: {str(e)}")
        raise ArchiveProcessingError(
            message=f"Archive vectorization failed: {str(e)}",
            code="VECTORIZATION_FAILED"
        )


@dramatiq.actor(
    queue_name="knowbase",
    max_retries=1,
    priority=2
)
def cleanup_failed_archives_task(days_old: int = 7) -> int:
    """
    Clean up failed archives older than specified days.
    
    Args:
        days_old: Age threshold for cleanup (default: 7 days)
        
    Returns:
        Number of archives cleaned up
    """
    logger.info(f"Starting cleanup of failed archives older than {days_old} days")
    
    try:
        cutoff_date = timezone.now() - timezone.timedelta(days=days_old)
        
        # Find failed archives older than cutoff
        failed_archives = DocumentArchive.objects.filter(
            processing_status=ProcessingStatus.FAILED,
            created_at__lt=cutoff_date
        )
        
        count = failed_archives.count()
        
        # Delete the archives (cascade will handle related objects)
        deleted_count, _ = failed_archives.delete()
        
        logger.info(f"Cleaned up {deleted_count} failed archives")
        return deleted_count
        
    except Exception as e:
        logger.error(f"Error during archive cleanup: {str(e)}")
        raise


@dramatiq.actor(
    queue_name="knowbase",
    max_retries=1,
    priority=1
)
def generate_archive_statistics_task(user_id: str) -> Dict[str, Any]:
    """
    Generate statistics for user's archives.
    
    Args:
        user_id: ID of the user
        
    Returns:
        Dictionary with archive statistics
    """
    logger.info(f"Generating archive statistics for user {user_id}")
    
    try:
        user = User.objects.get(pk=user_id)
        
        # Get user's archives
        archives = DocumentArchive.objects.filter(user=user)
        
        # Calculate statistics
        stats = {
            'total_archives': archives.count(),
            'completed_archives': archives.filter(processing_status=ProcessingStatus.COMPLETED).count(),
            'pending_archives': archives.filter(processing_status=ProcessingStatus.PENDING).count(),
            'processing_archives': archives.filter(processing_status=ProcessingStatus.PROCESSING).count(),
            'failed_archives': archives.filter(processing_status=ProcessingStatus.FAILED).count(),
            'total_items': sum(archive.total_items for archive in archives),
            'total_chunks': sum(archive.total_chunks for archive in archives),
            'total_cost': sum(archive.total_cost_usd for archive in archives),
        }
        
        logger.info(f"Generated statistics for user {user_id}: {stats}")
        return stats
        
    except User.DoesNotExist:
        logger.error(f"User {user_id} not found")
        raise
    except Exception as e:
        logger.error(f"Error generating statistics for user {user_id}: {str(e)}")
        raise


@dramatiq.actor(
    queue_name="knowbase",
    max_retries=1,
    priority=1
)
def archive_health_check_task() -> Dict[str, Any]:
    """
    Perform health check on archive system.
    
    Returns:
        Dictionary with health check results
    """
    logger.info("Starting archive system health check")
    
    try:
        # Check database connectivity
        total_archives = DocumentArchive.objects.count()
        
        # Check for orphaned items
        orphaned_items = ArchiveItem.objects.filter(archive__isnull=True).count()
        
        # Check for orphaned chunks
        orphaned_chunks = ArchiveItemChunk.objects.filter(item__isnull=True).count()
        
        # Check processing status distribution
        status_counts = {}
        for status in ProcessingStatus:
            count = DocumentArchive.objects.filter(processing_status=status).count()
            status_counts[status.value] = count
        
        # Check for archives with missing files
        archives_with_files = DocumentArchive.objects.exclude(file_path__isnull=True).exclude(file_path='')
        unhealthy_archives = 0
        
        for archive in archives_with_files:
            import os
            if not os.path.exists(archive.file_path):
                unhealthy_archives += 1
        
        health_data = {
            'total_checked': total_archives,
            'healthy_archives': total_archives - unhealthy_archives,
            'unhealthy_archives': unhealthy_archives,
            'orphaned_items': orphaned_items,
            'orphaned_chunks': orphaned_chunks,
            'status_distribution': status_counts,
            'timestamp': timezone.now().isoformat()
        }
        
        logger.info(f"Health check completed: {health_data}")
        return health_data
        
    except Exception as e:
        logger.error(f"Error during health check: {str(e)}")
        raise


# Test task for development
@dramatiq.actor(
    queue_name="knowbase",
    max_retries=0,
    priority=1
)
def test_archive_task(message: str = "Hello from archive tasks!") -> str:
    """
    Simple test task for archive system.
    
    Args:
        message: Test message to process
        
    Returns:
        Processed message
    """
    logger.info(f"Test archive task executed with message: {message}")
    time.sleep(1)  # Simulate some work
    return f"Processed: {message}"
