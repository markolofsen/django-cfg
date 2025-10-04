"""
Document and DocumentChunk managers.
"""

import logging
from typing import List, Dict, Any
from django.db import models
from django.db.models import Count, Q
from django.contrib.auth import get_user_model

logger = logging.getLogger(__name__)
User = get_user_model()


class DocumentManager(models.Manager):
    """Custom manager for Document model."""
    
    def for_user(self, user):
        """Explicitly filter by specific user."""
        return self.get_queryset().filter(user=user)
    
    def all_users(self):
        """Get unfiltered queryset (admin use)."""
        return self.get_queryset()
    
    def processed(self):
        """Get only processed documents."""
        from ..models.base import ProcessingStatus
        return self.get_queryset().filter(
            processing_status=ProcessingStatus.COMPLETED
        )
    
    def pending_processing(self):
        """Get documents pending processing."""
        from ..models.base import ProcessingStatus
        return self.get_queryset().filter(
            processing_status=ProcessingStatus.PENDING
        )
    
    def by_content_hash(self, content_hash: str):
        """Find documents by content hash."""
        return self.get_queryset().filter(content_hash=content_hash)
    
    def with_stats(self):
        """Get documents with chunk statistics."""
        return self.get_queryset().select_related().prefetch_related('chunks')
    
    def get_vectorization_progress(self, document_id):
        """Get vectorization progress for a document."""
        try:
            from ..models.document import DocumentChunk
            
            # Get all chunks for this document
            chunks_qs = DocumentChunk.objects.filter(document_id=document_id)
            
            total = chunks_qs.count()
            
            # Count vectorized chunks by checking if embedding has non-zero values
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
            logger.error(f"Error getting vectorization progress for document {document_id}: {e}")
            return {
                'total': 0,
                'vectorized': 0,
                'percentage': 0
            }
    
    def get_vectorization_status_display(self, document):
        """Get vectorization status display for admin."""
        try:
            # Check processing status first
            from ..models.document import ProcessingStatus
            
            if document.processing_status == ProcessingStatus.PENDING:
                return 'no_chunks', 'Pending'
            elif document.processing_status == ProcessingStatus.PROCESSING:
                return 'partial', 'Processing...'
            elif document.processing_status == ProcessingStatus.FAILED:
                return 'none', 'Failed'
            
            progress = self.get_vectorization_progress(document.id)
            total = progress['total']
            vectorized = progress['vectorized']
            percentage = progress['percentage']
            
            if total == 0:
                return 'no_chunks', 'No chunks'
            elif percentage == 100:
                return 'completed', f'{vectorized}/{total} (100%)'
            elif percentage > 0:
                return 'partial', f'{vectorized}/{total} ({percentage}%)'
            else:
                return 'none', f'{vectorized}/{total} (0%)'
        except Exception as e:
            logger.error(f"Error getting vectorization status for document {document.id}: {e}")
            
            # Try to provide more specific error information
            if document.processing_status == ProcessingStatus.COMPLETED and document.chunks_count > 0:
                return 'none', f'Error ({document.chunks_count} chunks)'
            else:
                return 'no_chunks', 'Error'
    
    def find_duplicates(self, document):
        """Find duplicate documents with same content hash."""
        if not document.content_hash:
            return self.none()
        
        return self.get_queryset().filter(
            user=document.user,
            content_hash=document.content_hash
        ).exclude(pk=document.pk)
    
    def get_duplicate_info(self, document):
        """Get duplicate information for admin display."""
        if not document.content_hash:
            return "No content hash"
        
        duplicates = self.find_duplicates(document)
        
        if not duplicates.exists():
            return "✅ No duplicates found"
        
        return {
            'count': duplicates.count(),
            'duplicates': list(duplicates[:3])  # Return first 3 for display
        }
    
    def check_duplicate_before_save(self, user, content, exclude_id=None):
        """Check for duplicate content before saving. Returns (is_duplicate, existing_doc)."""
        if not content:
            return False, None
        
        import hashlib
        content_hash = hashlib.sha256(content.encode()).hexdigest()
        
        # Use all_users() to bypass user filtering
        query = self.all_users().filter(user=user, content_hash=content_hash)
        
        if exclude_id:
            query = query.exclude(pk=exclude_id)
        
        existing_doc = query.first()
        return existing_doc is not None, existing_doc


class DocumentChunkManager(models.Manager):
    """Custom manager for DocumentChunk model."""
    
    def for_user(self, user):
        """Explicitly filter by specific user."""
        return self.get_queryset().filter(user=user)
    
    def all_users(self):
        """Get unfiltered queryset (admin use)."""
        return self.get_queryset()
    
    def for_document(self, document_id: str):
        """Get chunks for specific document."""
        return self.get_queryset().filter(document_id=document_id)
    
    def semantic_search(
        self,
        query_embedding: List[float],
        limit: int = 5,
        similarity_threshold: float = 0.7
    ):
        """Perform semantic search."""
        from pgvector.django import CosineDistance
        
        return self.get_queryset().annotate(
            similarity=1 - CosineDistance('embedding', query_embedding)
        ).filter(
            similarity__gte=similarity_threshold
        ).order_by('-similarity')[:limit]
    
    def with_document_info(self):
        """Get chunks with document information."""
        return self.get_queryset().select_related('document')
    
    def vectorized(self):
        """Get only vectorized chunks (with non-zero embeddings)."""
        # This is a simplified check - in practice you might want to check for non-zero vectors
        return self.get_queryset().exclude(embedding__isnull=True)
    
    def by_user_and_similarity(self, user, query_embedding: List[float], limit: int = 10):
        """Get chunks for specific user with similarity search."""
        from pgvector.django import CosineDistance
        
        return self.get_queryset().filter(
            user=user
        ).annotate(
            similarity=1 - CosineDistance('embedding', query_embedding)
        ).order_by('-similarity')[:limit]
