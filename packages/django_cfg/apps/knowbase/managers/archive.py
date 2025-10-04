"""
Archive managers for document archive models.
"""

import logging
from django.db import models, transaction
from django.db.models import Count, Sum, Avg, Q
from typing import Optional, List, Dict, Any
from django.contrib.auth import get_user_model

User = get_user_model()


class DocumentArchiveManager(models.Manager):
    """Custom manager for DocumentArchive model."""
    
    def for_user(self, user):
        """Explicitly filter by specific user."""
        return self.get_queryset().filter(user=user)
    
    def all_users(self):
        """Get unfiltered queryset (admin use)."""
        return self.get_queryset()
    
    def processed(self):
        """Get only processed archives."""
        from ..models.base import ProcessingStatus
        return self.get_queryset().filter(
            processing_status=ProcessingStatus.COMPLETED
        )
    
    def pending_processing(self):
        """Get archives pending processing."""
        from ..models.base import ProcessingStatus
        return self.get_queryset().filter(
            processing_status=ProcessingStatus.PENDING
        )
    
    def failed_processing(self):
        """Get archives that failed processing."""
        from ..models.base import ProcessingStatus
        return self.get_queryset().filter(
            processing_status=ProcessingStatus.FAILED
        )
    
    def by_content_hash(self, content_hash: str):
        """Find archives by content hash."""
        return self.get_queryset().filter(content_hash=content_hash)
    
    def by_archive_type(self, archive_type: str):
        """Get archives by type (zip, tar, etc.)."""
        return self.get_queryset().filter(archive_type=archive_type)
    
    def with_stats(self):
        """Get archives with item and chunk statistics."""
        return self.get_queryset().select_related('user').prefetch_related(
            'items', 'chunks', 'categories'
        )
    
    def get_processing_statistics(self, user=None) -> Dict[str, Any]:
        """Get archive processing statistics."""
        queryset = self.for_user(user) if user else self.get_queryset()
        
        # Get basic statistics
        stats = queryset.aggregate(
            total_archives=Count('id'),
            processed_archives=Count('id', filter=Q(processing_status='completed')),
            failed_archives=Count('id', filter=Q(processing_status='failed')),
            total_items=Sum('total_items'),
            total_chunks=Sum('total_chunks'),
            total_tokens=Sum('total_tokens'),
            total_cost=Sum('total_cost_usd'),
            avg_processing_time=Avg('processing_duration_ms')
        )
        
        # Calculate averages manually to avoid aggregate on aggregate error
        if stats['total_archives'] and stats['total_archives'] > 0:
            stats['avg_items_per_archive'] = (stats['total_items'] or 0) / stats['total_archives']
            stats['avg_chunks_per_archive'] = (stats['total_chunks'] or 0) / stats['total_archives']
        else:
            stats['avg_items_per_archive'] = 0
            stats['avg_chunks_per_archive'] = 0
            
        return stats
    
    def check_duplicate_before_save(self, user, title, file_size, exclude_id=None):
        """Check for duplicate archive before saving. Returns (is_duplicate, existing_archive)."""
        if not title or not file_size:
            return False, None
        
        # Use all_users() to bypass user filtering
        query = self.all_users().filter(
            user=user, 
            title=title,
            file_size=file_size
        )
        
        if exclude_id:
            query = query.exclude(pk=exclude_id)
        
        existing_archive = query.first()
        return existing_archive is not None, existing_archive
    
    def reprocess(self, archive_id: str) -> bool:
        """
        Reset and reprocess an archive.
        
        Args:
            archive_id: ID of the archive to reprocess
            
        Returns:
            bool: True if reprocessing was initiated successfully
            
        Raises:
            ValueError: If archive not found or has no file
        """
        from ..models.base import ProcessingStatus
        from ..tasks.archive_tasks import process_archive_task
        
        logger = logging.getLogger(__name__)
        
        try:
            # Import the model directly to avoid queryset issues
            from ..models.archive import DocumentArchive
            # Use Django's default manager to avoid custom queryset issues
            archive = DocumentArchive.objects.get(pk=archive_id)
        except DocumentArchive.DoesNotExist:
            raise ValueError(f"Archive with ID {archive_id} not found")
        except Exception as e:
            raise
        
        # Check if archive has a file
        if not archive.archive_file:
            raise ValueError("Archive has no file to process")
        
        # Check if archive is already being processed
        if archive.processing_status == ProcessingStatus.PROCESSING:
            raise ValueError(f"Archive {archive.id} is already being processed")
        
        # Set processing status immediately to prevent concurrent reprocessing
        # Use select_for_update to prevent race conditions
        with transaction.atomic():
            archive = DocumentArchive.objects.select_for_update().get(pk=archive_id)
            if archive.processing_status == ProcessingStatus.PROCESSING:
                raise ValueError(f"Archive {archive.id} is already being processed by another process")
            
            archive.processing_status = ProcessingStatus.PROCESSING
            archive.save(update_fields=['processing_status'])
            logger.info(f"🔒 Locked archive {archive.id} for reprocessing")
        
        logger.info(f"🔄 Starting reprocessing for archive {archive.id} ({archive.title})")
        
        # Reset processing status and clear error
        archive.processing_status = ProcessingStatus.PENDING
        archive.processing_error = ""
        archive.processing_duration_ms = 0
        archive.processed_at = None
        
        # Clear existing items and chunks using Django ORM with proper transaction handling
        from ..models.archive import ArchiveItem, ArchiveItemChunk
        
        # Count existing records first
        items_count = ArchiveItem.objects.filter(archive=archive).count()
        chunks_count = ArchiveItemChunk.objects.filter(item__archive=archive).count()
        
        logger.info(f"🗑️ Found {items_count} items and {chunks_count} chunks to delete")
        
        if items_count > 0 or chunks_count > 0:
            # Delete in separate transaction to ensure complete removal before new processing
            try:
                with transaction.atomic():
                    # Delete chunks first (foreign key dependency)
                    chunks_deleted, _ = ArchiveItemChunk.objects.filter(item__archive=archive).delete()
                    
                    # Delete items
                    items_deleted, _ = ArchiveItem.objects.filter(archive=archive).delete()
                
                # Verify deletion outside transaction with retry logic
                import time
                max_retries = 3
                for retry in range(max_retries):
                    remaining_items = ArchiveItem.objects.filter(archive=archive).count()
                    remaining_chunks = ArchiveItemChunk.objects.filter(item__archive=archive).count()
                    
                    if remaining_items == 0 and remaining_chunks == 0:
                        break
                        
                    if retry < max_retries - 1:
                        logger.warning(f"⚠️ Retry {retry + 1}: Still {remaining_items} items and {remaining_chunks} chunks remaining, waiting...")
                        time.sleep(0.2)
                    else:
                        logger.error(f"❌ Failed to delete all records after {max_retries} retries! {remaining_items} items and {remaining_chunks} chunks still remain")
                        raise ValueError(f"Failed to clear existing archive data after {max_retries} retries. {remaining_items} items and {remaining_chunks} chunks still exist.")
                
                logger.info(f"🗑️ Successfully deleted {items_deleted} items and {chunks_deleted} chunks")
                
            except Exception as e:
                logger.error(f"❌ Error during deletion: {e}")
                # Reset processing status on error
                archive.processing_status = ProcessingStatus.FAILED
                archive.processing_error = f"Failed to clear existing data: {str(e)}"
                archive.save(update_fields=['processing_status', 'processing_error'])
                raise
        else:
            logger.info("🗑️ No existing records to delete")
        
        # Reset statistics
        archive.total_items = 0
        archive.processed_items = 0
        archive.total_chunks = 0
        archive.vectorized_chunks = 0
        archive.total_cost_usd = 0.0
        
        archive.save()
        logger.info(f"💾 Archive {archive.id} reset to PENDING status")
        
        # Trigger reprocessing directly via task
        process_archive_task.send(str(archive.id), str(archive.user.id))
        logger.info(f"🚀 Queued reprocessing task for archive {archive.id}")
        
        return True
    
    def get_vectorization_progress(self, archive_id):
        """Get vectorization progress for an archive."""
        try:
            from ..models.archive import ArchiveItemChunk
            from django.db.models import Count, Q
            
            # Count chunks using Django ORM
            
            # Get all chunks for this archive
            chunks_qs = ArchiveItemChunk.objects.filter(archive_id=archive_id)
            
            total = chunks_qs.count()
            
            # Count vectorized chunks by checking if embedding has non-zero values
            # We'll check if the first element is not 0.0 as a proxy for non-zero vector
            vectorized = 0
            if total > 0:
                for chunk in chunks_qs.only('embedding'):
                    if chunk.embedding is not None and len(chunk.embedding) > 0 and any(x != 0.0 for x in chunk.embedding):
                        vectorized += 1
            
            return {
                'total': total,
                'vectorized': vectorized,
                'percentage': round((vectorized / total * 100) if total > 0 else 0, 1)
            }
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error getting vectorization progress for archive {archive_id}: {e}")
            return {
                'total': 0,
                'vectorized': 0,
                'percentage': 0
            }


class ArchiveItemManager(models.Manager):
    """Custom manager for ArchiveItem model."""
    
    def for_user(self, user):
        """Explicitly filter by specific user."""
        return self.get_queryset().filter(user=user)
    
    def all_users(self):
        """Get unfiltered queryset (admin use)."""
        return self.get_queryset()
    
    def for_archive(self, archive_id: str):
        """Get items for specific archive."""
        return self.get_queryset().filter(archive_id=archive_id)
    
    def by_content_type(self, content_type: str):
        """Get items by content type."""
        return self.get_queryset().filter(content_type=content_type)
    
    def by_language(self, language: str):
        """Get items by programming language."""
        return self.get_queryset().filter(language=language)
    
    def processable(self):
        """Get only processable items."""
        return self.get_queryset().filter(is_processable=True)
    
    def code_files(self):
        """Get only code files."""
        return self.get_queryset().filter(content_type='code')
    
    def document_files(self):
        """Get only document files."""
        return self.get_queryset().filter(content_type='document')
    
    def data_files(self):
        """Get only data files."""
        return self.get_queryset().filter(content_type='data')
    
    def with_chunks(self):
        """Get items with their chunks."""
        return self.get_queryset().prefetch_related('chunks')
    
    def get_content_type_distribution(self, archive_id: Optional[str] = None) -> Dict[str, int]:
        """Get distribution of content types."""
        queryset = self.get_queryset()
        if archive_id:
            queryset = queryset.filter(archive_id=archive_id)
        
        return dict(
            queryset.values('content_type').annotate(
                count=Count('id')
            ).values_list('content_type', 'count')
        )
    
    def get_language_distribution(self, archive_id: Optional[str] = None) -> Dict[str, int]:
        """Get distribution of programming languages."""
        queryset = self.get_queryset().filter(language__isnull=False).exclude(language='')
        if archive_id:
            queryset = queryset.filter(archive_id=archive_id)
        
        return dict(
            queryset.values('language').annotate(
                count=Count('id')
            ).values_list('language', 'count')
        )


class ArchiveItemChunkManager(models.Manager):
    """Custom manager for ArchiveItemChunk model."""
    
    def for_user(self, user):
        """Explicitly filter by specific user."""
        return self.get_queryset().filter(user=user)
    
    def all_users(self):
        """Get unfiltered queryset (admin use)."""
        return self.get_queryset()
    
    def for_archive(self, archive_id: str):
        """Get chunks for specific archive."""
        return self.get_queryset().filter(archive_id=archive_id)
    
    def for_item(self, item_id: str):
        """Get chunks for specific item."""
        return self.get_queryset().filter(item_id=item_id)
    
    def by_chunk_type(self, chunk_type: str):
        """Get chunks by type."""
        return self.get_queryset().filter(chunk_type=chunk_type)
    
    def vectorized(self):
        """Get only vectorized chunks."""
        return self.get_queryset().filter(embedding__isnull=False)
    
    def pending_vectorization(self):
        """Get chunks pending vectorization."""
        return self.get_queryset().filter(embedding__isnull=True)
    
    def by_content_type(self, content_type: str):
        """Get chunks by parent item content type."""
        return self.get_queryset().filter(item__content_type=content_type)
    
    def by_language(self, language: str):
        """Get chunks by parent item language."""
        return self.get_queryset().filter(item__language=language)
    
    def semantic_search(
        self,
        query_embedding: List[float],
        limit: int = 5,
        similarity_threshold: float = 0.7,
        content_types: Optional[List[str]] = None,
        languages: Optional[List[str]] = None,
        chunk_types: Optional[List[str]] = None
    ):
        """Perform semantic search with advanced filtering."""
        from pgvector.django import CosineDistance
        
        queryset = self.get_queryset().filter(embedding__isnull=False)
        
        # Apply filters
        if content_types:
            queryset = queryset.filter(item__content_type__in=content_types)
        
        if languages:
            queryset = queryset.filter(item__language__in=languages)
        
        if chunk_types:
            queryset = queryset.filter(chunk_type__in=chunk_types)
        
        return queryset.annotate(
            similarity=1 - CosineDistance('embedding', query_embedding)
        ).filter(
            similarity__gte=similarity_threshold
        ).order_by('-similarity')[:limit]
    
    def with_context(self):
        """Get chunks with archive and item context."""
        return self.get_queryset().select_related('archive', 'item')
    
    def get_vectorization_statistics(self, archive_id: Optional[str] = None) -> Dict[str, Any]:
        """Get vectorization statistics."""
        queryset = self.get_queryset()
        if archive_id:
            queryset = queryset.filter(archive_id=archive_id)
        
        return queryset.aggregate(
            total_chunks=Count('id'),
            vectorized_chunks=Count('id', filter=Q(embedding__isnull=False)),
            total_tokens=Sum('token_count'),
            total_cost=Sum('embedding_cost'),
            avg_tokens_per_chunk=Avg('token_count'),
            avg_cost_per_chunk=Avg('embedding_cost')
        )
    
    def get_chunk_type_distribution(self, archive_id: Optional[str] = None) -> Dict[str, int]:
        """Get distribution of chunk types."""
        queryset = self.get_queryset()
        if archive_id:
            queryset = queryset.filter(archive_id=archive_id)
        
        return dict(
            queryset.values('chunk_type').annotate(
                count=Count('id')
            ).values_list('chunk_type', 'count')
        )
