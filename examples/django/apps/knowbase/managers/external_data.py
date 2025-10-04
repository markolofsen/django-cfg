"""
External Data managers for advanced querying and operations.
"""

from django.db import models
from django.db.models import Count, Q, Avg, Sum
from django.utils import timezone
from typing import Optional, List, Dict, Any
from datetime import timedelta

from .base import BaseKnowbaseManager


class ExternalDataQuerySet(models.QuerySet):
    """Custom QuerySet for ExternalData with advanced filtering."""
    
    def active(self):
        """Filter to active external data sources."""
        return self.filter(is_active=True)
    
    def public(self):
        """Filter to public external data sources."""
        return self.filter(is_public=True)
    
    def processed(self):
        """Filter to successfully processed external data."""
        return self.filter(status='completed')
    
    def failed(self):
        """Filter to failed external data."""
        return self.filter(status='failed')
    
    def outdated(self):
        """Filter to outdated external data that needs reprocessing."""
        return self.filter(
            Q(status='outdated') |
            Q(source_updated_at__gt=models.F('processed_at'))
        )
    
    def by_source_type(self, source_type: str):
        """Filter by source type."""
        return self.filter(source_type=source_type)
    
    def by_status(self, status: str):
        """Filter by status."""
        return self.filter(status=status)
    
    def get_processing_statistics(self):
        """Get processing statistics for external data."""
        from django.db.models import Count, Q
        
        stats = self.aggregate(
            total=Count('id'),
            pending=Count('id', filter=Q(status='pending')),
            processing=Count('id', filter=Q(status='processing')),
            completed=Count('id', filter=Q(status='completed')),
            failed=Count('id', filter=Q(status='failed')),
        )
        
        return {
            'total_external_data': stats['total'],
            'pending_processing': stats['pending'],
            'currently_processing': stats['processing'],
            'completed_processing': stats['completed'],
            'failed_processing': stats['failed'],
        }
    
    def by_category(self, category):
        """Filter by category."""
        return self.filter(category=category)
    
    def with_tags(self, tags: List[str]):
        """Filter external data that contains any of the specified tags."""
        if not tags:
            return self
        
        q = Q()
        for tag in tags:
            q |= Q(tags__contains=[tag])
        return self.filter(q)
    
    def search_content(self, query: str):
        """Search in title, description, and content."""
        return self.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query) |
            Q(content__icontains=query)
        )
    
    def recent(self, days: int = 7):
        """Filter to recently processed external data."""
        cutoff = timezone.now() - timedelta(days=days)
        return self.filter(processed_at__gte=cutoff)
    
    def with_chunks(self):
        """Filter to external data that has chunks."""
        return self.filter(total_chunks__gt=0)
    
    def without_chunks(self):
        """Filter to external data without chunks."""
        return self.filter(total_chunks=0)
    
    def expensive(self, min_cost: float = 0.01):
        """Filter to external data with high processing costs."""
        return self.filter(processing_cost__gte=min_cost)
    
    def with_statistics(self):
        """Annotate with chunk and cost statistics."""
        return self.annotate(
            chunks_count=Count('chunks'),
            avg_chunk_tokens=Avg('chunks__token_count'),
            total_embedding_cost=Sum('chunks__embedding_cost')
        )


class ExternalDataManager(BaseKnowbaseManager):
    """Manager for ExternalData with user scoping and advanced queries."""
    
    def get_queryset(self):
        return ExternalDataQuerySet(self.model, using=self._db)
    
    def active(self):
        """Get active external data sources."""
        return self.get_queryset().active()
    
    def public(self):
        """Get public external data sources."""
        return self.get_queryset().public()
    
    def processed(self):
        """Get successfully processed external data."""
        return self.get_queryset().processed()
    
    def failed(self):
        """Get failed external data."""
        return self.get_queryset().failed()
    
    def outdated(self):
        """Get outdated external data that needs reprocessing."""
        return self.get_queryset().outdated()
    
    def by_source_type(self, source_type: str):
        """Get external data by source type."""
        return self.get_queryset().by_source_type(source_type)
    
    def by_status(self, status: str):
        """Get external data by status."""
        return self.get_queryset().by_status(status)
    
    def by_category(self, category):
        """Get external data by category."""
        return self.get_queryset().by_category(category)
    
    def with_tags(self, tags: List[str]):
        """Get external data with specified tags."""
        return self.get_queryset().with_tags(tags)
    
    def search_content(self, query: str):
        """Search external data content."""
        return self.get_queryset().search_content(query)
    
    def recent(self, days: int = 7):
        """Get recently processed external data."""
        return self.get_queryset().recent(days)
    
    def with_chunks(self):
        """Get external data that has chunks."""
        return self.get_queryset().with_chunks()
    
    def without_chunks(self):
        """Get external data without chunks."""
        return self.get_queryset().without_chunks()
    
    def expensive(self, min_cost: float = 0.01):
        """Get external data with high processing costs."""
        return self.get_queryset().expensive(min_cost)
    
    def with_statistics(self):
        """Get external data with statistics."""
        return self.get_queryset().with_statistics()
    
    def create_from_source(
        self,
        user,
        title: str,
        source_type: str,
        source_identifier: str,
        content: str,
        source_config: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        **kwargs
    ):
        """
        Create external data from a source.
        
        Args:
            user: User creating the external data
            title: Human-readable title
            source_type: Type of source (model, api, etc.)
            source_identifier: Unique identifier for the source
            content: Extracted content
            source_config: Configuration for data extraction
            metadata: Additional metadata
            **kwargs: Additional fields
        
        Returns:
            ExternalData instance
        """
        return self.create(
            user=user,
            title=title,
            source_type=source_type,
            source_identifier=source_identifier,
            content=content,
            source_config=source_config or {},
            metadata=metadata or {},
            **kwargs
        )
    
    def get_or_create_from_source(
        self,
        user,
        source_identifier: str,
        defaults: Optional[Dict[str, Any]] = None
    ):
        """
        Get or create external data for a source identifier.
        
        Args:
            user: User
            source_identifier: Unique identifier for the source
            defaults: Default values for creation
        
        Returns:
            Tuple of (ExternalData, created)
        """
        return self.get_or_create(
            user=user,
            source_identifier=source_identifier,
            defaults=defaults or {}
        )
    
    def bulk_update_status(self, external_data_ids: List[str], status: str):
        """
        Bulk update status for multiple external data sources.
        
        Args:
            external_data_ids: List of external data IDs
            status: New status
        
        Returns:
            Number of updated records
        """
        return self.filter(id__in=external_data_ids).update(
            status=status,
            updated_at=timezone.now()
        )
    
    def get_processing_statistics(self, user=None) -> Dict[str, Any]:
        """
        Get processing statistics for external data.
        
        Args:
            user: Optional user filter
        
        Returns:
            Dictionary with statistics
        """
        queryset = self.get_queryset()
        if user:
            queryset = queryset.filter(user=user)
        
        stats = queryset.aggregate(
            total_count=Count('id'),
            processed_count=Count('id', filter=Q(status='completed')),
            failed_count=Count('id', filter=Q(status='failed')),
            pending_count=Count('id', filter=Q(status='pending')),
            outdated_count=Count('id', filter=Q(status='outdated')),
            total_chunks=Sum('total_chunks'),
            total_tokens=Sum('total_tokens'),
            total_cost=Sum('processing_cost'),
            avg_chunk_size=Avg('chunk_size'),
        )
        
        # Calculate percentages
        total = stats['total_count'] or 0
        if total > 0:
            stats['processed_percentage'] = (stats['processed_count'] or 0) / total * 100
            stats['failed_percentage'] = (stats['failed_count'] or 0) / total * 100
            stats['pending_percentage'] = (stats['pending_count'] or 0) / total * 100
            stats['outdated_percentage'] = (stats['outdated_count'] or 0) / total * 100
        else:
            stats['processed_percentage'] = 0
            stats['failed_percentage'] = 0
            stats['pending_percentage'] = 0
            stats['outdated_percentage'] = 0
        
        return stats
    
    def cleanup_failed(self, older_than_days: int = 7) -> int:
        """
        Clean up old failed external data sources.
        
        Args:
            older_than_days: Remove failed sources older than this many days
        
        Returns:
            Number of deleted records
        """
        cutoff = timezone.now() - timedelta(days=older_than_days)
        failed_queryset = self.failed().filter(updated_at__lt=cutoff)
        count = failed_queryset.count()
        failed_queryset.delete()
        return count
    
    def regenerate_external_data(self, external_data_ids: List[str]) -> Dict[str, Any]:
        """
        Regenerate embeddings for specified external data sources.
        
        Args:
            external_data_ids: List of external data IDs to regenerate
        
        Returns:
            Dictionary with regeneration results
        """
        from ..models.external_data import ExternalDataStatus
        from ..tasks.external_data_tasks import process_external_data_async
        
        external_data_list = list(self.get_queryset().filter(id__in=external_data_ids))
        
        if not external_data_list:
            return {
                'success': False,
                'error': 'No external data found with provided IDs',
                'regenerated_count': 0,
                'failed_count': 0
            }
        
        regenerated_count = 0
        failed_count = 0
        errors = []
        
        for external_data in external_data_list:
            try:
                # Reset processing state
                external_data.status = ExternalDataStatus.PENDING
                external_data.processing_error = ""
                external_data.processed_at = None
                external_data.total_chunks = 0
                external_data.total_tokens = 0
                external_data.processing_cost = 0.0
                external_data.save(update_fields=[
                    'status', 'processing_error', 'processed_at',
                    'total_chunks', 'total_tokens', 'processing_cost'
                ])
                
                # Clear existing chunks
                external_data.chunks.all().delete()
                
                # Queue for reprocessing with force flag
                process_external_data_async.send(
                    str(external_data.id),
                    force_reprocess=True
                )
                
                regenerated_count += 1
                
            except Exception as e:
                failed_count += 1
                errors.append(f"Failed to regenerate {external_data.title}: {str(e)}")
        
        return {
            'success': regenerated_count > 0,
            'regenerated_count': regenerated_count,
            'failed_count': failed_count,
            'total_count': len(external_data_list),
            'errors': errors
        }


class ExternalDataChunkQuerySet(models.QuerySet):
    """Custom QuerySet for ExternalDataChunk."""
    
    def by_external_data(self, external_data):
        """Filter by external data."""
        return self.filter(external_data=external_data)
    
    def by_embedding_model(self, model: str):
        """Filter by embedding model."""
        return self.filter(embedding_model=model)
    
    def with_embeddings(self):
        """Filter to chunks that have embeddings."""
        return self.filter(embedding__isnull=False)
    
    def without_embeddings(self):
        """Filter to chunks without embeddings."""
        return self.filter(embedding__isnull=True)
    
    def large_chunks(self, min_tokens: int = 500):
        """Filter to large chunks."""
        return self.filter(token_count__gte=min_tokens)
    
    def small_chunks(self, max_tokens: int = 100):
        """Filter to small chunks."""
        return self.filter(token_count__lte=max_tokens)
    
    def expensive_chunks(self, min_cost: float = 0.001):
        """Filter to expensive chunks."""
        return self.filter(embedding_cost__gte=min_cost)


class ExternalDataChunkManager(models.Manager):
    """Manager for ExternalDataChunk."""
    
    def get_queryset(self):
        return ExternalDataChunkQuerySet(self.model, using=self._db)
    
    def by_external_data(self, external_data):
        """Get chunks for external data."""
        return self.get_queryset().by_external_data(external_data)
    
    def by_embedding_model(self, model: str):
        """Get chunks by embedding model."""
        return self.get_queryset().by_embedding_model(model)
    
    def with_embeddings(self):
        """Get chunks with embeddings."""
        return self.get_queryset().with_embeddings()
    
    def without_embeddings(self):
        """Get chunks without embeddings."""
        return self.get_queryset().without_embeddings()
    
    def large_chunks(self, min_tokens: int = 500):
        """Get large chunks."""
        return self.get_queryset().large_chunks(min_tokens)
    
    def small_chunks(self, max_tokens: int = 100):
        """Get small chunks."""
        return self.get_queryset().small_chunks(max_tokens)
    
    def expensive_chunks(self, min_cost: float = 0.001):
        """Get expensive chunks."""
        return self.get_queryset().expensive_chunks(min_cost)
    
    def get_chunk_statistics(self, user=None) -> Dict[str, Any]:
        """
        Get chunk statistics.
        
        Args:
            user: Optional user filter
        
        Returns:
            Dictionary with statistics
        """
        queryset = self.get_queryset()
        if user:
            queryset = queryset.filter(user=user)
        
        return queryset.aggregate(
            total_chunks=Count('id'),
            total_tokens=Sum('token_count'),
            total_characters=Sum('character_count'),
            total_cost=Sum('embedding_cost'),
            avg_tokens=Avg('token_count'),
            avg_characters=Avg('character_count'),
            avg_cost=Avg('embedding_cost'),
            max_tokens=models.Max('token_count'),
            min_tokens=models.Min('token_count'),
        )
