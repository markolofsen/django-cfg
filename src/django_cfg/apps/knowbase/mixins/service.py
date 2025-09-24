"""
Service wrapper for ExternalData operations using the mixin system.

This provides a service-like interface for backward compatibility while
using the new mixin-based architecture internally.
"""

import logging
from typing import List, Dict, Any, Optional
from django.db import models, transaction
from django.utils import timezone
from pgvector.django import CosineDistance

from django_cfg.modules.django_llm.llm.client import LLMClient
from ..config.settings import get_openai_api_key, get_cache_settings
from ..utils.validation import safe_float, validate_similarity_score
from ..models.external_data import ExternalData, ExternalDataChunk, ExternalDataStatus
from ..services.base import BaseService
from ..services.embedding import process_external_data_chunks_optimized
from .creator import ExternalDataCreator
from .config import ExternalDataConfig

logger = logging.getLogger(__name__)


class ExternalDataService(BaseService):
    """
    Service for managing external data sources within django_cfg.apps.knowbase.
    
    This service provides backward compatibility with the old ExternalDataService
    while using the new mixin-based architecture internally.
    """
    
    def __init__(self, user):
        super().__init__(user)
        cache_settings = get_cache_settings()
        self.llm_client = LLMClient(
            apikey_openai=get_openai_api_key(),
            cache_dir=cache_settings.cache_dir,
            cache_ttl=cache_settings.cache_ttl,
            max_cache_size=cache_settings.max_cache_size
        )
    
    def create_external_data(
        self,
        title: str,
        source_type: str,
        source_identifier: str,
        content: str,
        description: str = "",
        source_config: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        tags: Optional[List[str]] = None,
        similarity_threshold: float = 0.5,
        is_active: bool = True,
        is_public: bool = False
    ) -> Dict[str, Any]:
        """
        Create external data using the new mixin system.
        
        This method provides backward compatibility with the old service API.
        """
        try:
            # Create configuration
            config = ExternalDataConfig(
                title=title,
                description=description,
                source_type=source_type,
                source_identifier=source_identifier,
                content=content,
                similarity_threshold=similarity_threshold,
                is_active=is_active,
                is_public=is_public,
                metadata=metadata or {},
                source_config=source_config or {},
                tags=tags or []
            )
            
            # Create using the new creator
            creator = ExternalDataCreator(self.user)
            result = creator.create_from_config(config)
            
            if result['success']:
                return {
                    'success': True,
                    'external_data': result['external_data'],
                    'message': result['message']
                }
            else:
                return {
                    'success': False,
                    'error': result['error']
                }
                
        except Exception as e:
            logger.error(f"Error creating external data: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    @transaction.atomic
    def vectorize_external_data(self, external_data_id) -> Dict[str, Any]:
        """
        Vectorize external data content into chunks.
        
        Args:
            external_data_id: ExternalData ID or instance to vectorize
        
        Returns:
            dict: Result with success status, processed count, and cost.
        """
        try:
            # Get the external data object
            if hasattr(external_data_id, 'id'):
                # It's an ExternalData object
                external_data = external_data_id
                external_data.refresh_from_db()
            else:
                # It's an ID
                external_data = ExternalData.objects.get(id=external_data_id, user=self.user)
            
            # Mark as processing
            external_data.status = ExternalDataStatus.PROCESSING
            external_data.processing_error = ""
            external_data.save()
            
            # Clear existing chunks
            external_data.chunks.all().delete()
            
            # Generate chunks if content exists
            if not external_data.content.strip():
                external_data.status = ExternalDataStatus.COMPLETED
                external_data.processed_at = timezone.now()
                external_data.save()
                return {
                    'success': True,
                    'processed_count': 0,
                    'cost': 0.0
                }
            
            # Use the existing chunking and embedding logic
            result = process_external_data_chunks_optimized(
                external_data=external_data,
                llm_client=self.llm_client
            )
            
            if result.successful_chunks:
                external_data.status = ExternalDataStatus.COMPLETED
                external_data.processed_at = timezone.now()
                external_data.processing_error = ""
            else:
                external_data.status = ExternalDataStatus.FAILED
                external_data.processing_error = "No chunks were successfully processed"
            
            external_data.save()
            
            return {
                'success': True,
                'processed_count': len(result.successful_chunks),
                'cost': result.total_cost
            }
            
        except Exception as e:
            # Mark as failed
            if 'external_data' in locals():
                external_data.status = ExternalDataStatus.FAILED
                external_data.processing_error = str(e)
                external_data.save()
            logger.error(f"Failed to vectorize external data: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def search_external_data(
        self,
        query: str,
        limit: int = 5,
        threshold: Optional[float] = None,
        source_types: Optional[List[str]] = None,
        source_identifiers: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Search external data using semantic similarity.
        
        Args:
            query: Search query
            limit: Maximum number of results
            threshold: Similarity threshold (uses per-object thresholds if None)
            source_types: Filter by source types
            source_identifiers: Filter by source identifiers
        
        Returns:
            List of search results with similarity scores
        """
        try:
            # Generate query embedding
            query_embedding = self.llm_client.generate_embedding(query)
            
            # Build query
            chunks_query = ExternalDataChunk.objects.filter(
                external_data__user=self.user,
                external_data__is_active=True,
                embedding__isnull=False
            ).select_related('external_data')
            
            # Apply filters
            if source_types:
                chunks_query = chunks_query.filter(external_data__source_type__in=source_types)
            
            if source_identifiers:
                chunks_query = chunks_query.filter(external_data__source_identifier__in=source_identifiers)
            
            # Calculate similarity and order by it
            chunks_with_similarity = chunks_query.annotate(
                similarity=1 - CosineDistance('embedding', query_embedding.embedding)
            ).order_by('-similarity')[:limit * 2]  # Get more to filter by threshold
            
            # Filter by threshold and format results
            results = []
            for chunk in chunks_with_similarity:
                similarity_value = safe_float(chunk.similarity, 0.0)
                
                # Use per-object threshold if no global threshold provided
                object_threshold = threshold if threshold is not None else chunk.external_data.similarity_threshold
                if similarity_value < object_threshold:
                    continue
                
                results.append({
                    'type': 'external_data',
                    'chunk': chunk,
                    'similarity': similarity_value,
                    'source_title': chunk.external_data.title,
                    'content': chunk.content,
                    'metadata': {
                        'external_data_id': str(chunk.external_data.id),
                        'source_type': chunk.external_data.source_type,
                        'source_identifier': chunk.external_data.source_identifier,
                        'chunk_index': chunk.chunk_index,
                        **chunk.external_data.metadata
                    }
                })
                
                if len(results) >= limit:
                    break
            
            return results
            
        except Exception as e:
            logger.error(f"Error searching external data: {e}")
            return []
    
    def get_external_data_stats(self) -> Dict[str, Any]:
        """Get statistics about external data for the user."""
        try:
            queryset = ExternalData.objects.filter(user=self.user)
            
            stats = {
                'total_external_data': queryset.count(),
                'by_status': {},
                'by_source_type': {},
                'total_chunks': 0,
                'total_tokens': 0,
                'total_cost': 0.0
            }
            
            # Status breakdown
            for status in ExternalDataStatus:
                count = queryset.filter(status=status).count()
                stats['by_status'][status] = count
            
            # Source type breakdown
            source_types = queryset.values_list('source_type', flat=True).distinct()
            for source_type in source_types:
                count = queryset.filter(source_type=source_type).count()
                stats['by_source_type'][source_type] = count
            
            # Aggregate statistics
            aggregates = queryset.aggregate(
                total_chunks=models.Sum('total_chunks'),
                total_tokens=models.Sum('total_tokens'),
                total_cost=models.Sum('processing_cost')
            )
            
            stats.update({
                'total_chunks': aggregates['total_chunks'] or 0,
                'total_tokens': aggregates['total_tokens'] or 0,
                'total_cost': float(aggregates['total_cost'] or 0.0)
            })
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting external data stats: {e}")
            return {
                'total_external_data': 0,
                'by_status': {},
                'by_source_type': {},
                'total_chunks': 0,
                'total_tokens': 0,
                'total_cost': 0.0
            }
    
    def delete_external_data(self, external_data_id) -> Dict[str, Any]:
        """Delete external data and all associated chunks."""
        try:
            external_data = ExternalData.objects.get(id=external_data_id, user=self.user)
            title = external_data.title
            external_data.delete()
            
            return {
                'success': True,
                'message': f"External data '{title}' deleted successfully"
            }
            
        except ExternalData.DoesNotExist:
            return {
                'success': False,
                'error': "External data not found"
            }
        except Exception as e:
            logger.error(f"Error deleting external data: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def bulk_vectorize_pending(self) -> Dict[str, Any]:
        """Vectorize all pending external data for the user."""
        try:
            pending_data = ExternalData.objects.filter(
                user=self.user,
                status=ExternalDataStatus.PENDING
            )
            
            stats = {
                'total': pending_data.count(),
                'processed': 0,
                'failed': 0,
                'total_cost': 0.0
            }
            
            for external_data in pending_data:
                result = self.vectorize_external_data(external_data)
                if result.get('success', False):
                    stats['processed'] += 1
                    stats['total_cost'] += result.get('cost', 0.0)
                else:
                    stats['failed'] += 1
            
            return {
                'success': True,
                'stats': stats
            }
            
        except Exception as e:
            logger.error(f"Error in bulk vectorization: {e}")
            return {
                'success': False,
                'error': str(e)
            }
