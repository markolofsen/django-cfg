"""
Document management service.
"""

from typing import List, Optional, Dict, Any
from django.db import transaction, models
from django.utils import timezone
from ..models import Document, DocumentChunk, ProcessingStatus
from .base import BaseService


class DocumentService(BaseService):
    """Service for document management and processing."""
    
    def create_document(
        self,
        title: str,
        content: str,
        file_type: str = "text/plain",
        metadata: Optional[Dict[str, Any]] = None
    ) -> Document:
        """Create document and trigger async processing."""
        
        # Generate content hash for duplicate detection
        content_hash = self._generate_content_hash(content)
        
        # Check for duplicates
        existing = Document.objects.filter(
            user=self.user,
            content_hash=content_hash
        ).first()
        
        if existing:
            raise ValueError(f"Document with same content already exists: {existing.title}")
        
        # Create document (async processing will be triggered by post_save signal)
        document = Document.objects.create(
            user=self.user,
            title=title,
            content=content,
            content_hash=content_hash,
            file_type=file_type,
            file_size=len(content.encode('utf-8')),
            metadata=metadata or {},
            processing_status=ProcessingStatus.PENDING
        )
        
        return document
    
    def get_document(self, document_id: str) -> Optional[Document]:
        """Get document by ID with user access check."""
        try:
            document = Document.objects.get(
                id=document_id,
                user=self.user
            )
            return document
        except Document.DoesNotExist:
            return None
    
    def get_user_documents(self, status: Optional[str] = None):
        """Get user documents queryset with filtering."""
        queryset = Document.objects.filter(user=self.user)
        
        if status:
            queryset = queryset.filter(processing_status=status)
        
        return queryset.order_by('-created_at')
    
    def list_documents(
        self,
        status: Optional[str] = None,
        limit: int = 20,
        offset: int = 0
    ) -> List[Document]:
        """List user documents with filtering."""
        queryset = self.get_user_documents(status)
        return list(queryset[offset:offset + limit])
    
    def delete_document(self, document_id: str) -> bool:
        """Delete document and all associated chunks."""
        try:
            with transaction.atomic():
                document = Document.objects.get(
                    id=document_id,
                    user=self.user
                )
                
                # Delete associated chunks first
                DocumentChunk.objects.filter(document=document).delete()
                
                # Delete document
                document.delete()
                
                return True
        except Document.DoesNotExist:
            return False
    
    def get_processing_stats(self) -> Dict[str, Any]:
        """Get user's document processing statistics."""
        
        from django.db.models import Count, Sum, Avg
        
        stats = Document.objects.filter(user=self.user).aggregate(
            total_documents=Count('id'),
            completed_documents=Count('id', filter=models.Q(processing_status=ProcessingStatus.COMPLETED)),
            total_chunks=Sum('chunks_count'),
            total_tokens=Sum('total_tokens'),
            total_cost=Sum('total_cost_usd'),
        )
        
        return {
            'total_documents': stats['total_documents'] or 0,
            'completed_documents': stats['completed_documents'] or 0,
            'processing_success_rate': (
                (stats['completed_documents'] / stats['total_documents'] * 100)
                if stats['total_documents'] > 0 else 0
            ),
            'total_chunks': stats['total_chunks'] or 0,
            'total_tokens': stats['total_tokens'] or 0,
            'total_cost_usd': float(stats['total_cost'] or 0),
            'avg_processing_time_seconds': 0.0  # Calculated separately if needed
        }
    
    def reprocess_document(self, document_id: str) -> bool:
        """Trigger document reprocessing."""
        try:
            document = Document.objects.get(
                id=document_id,
                user=self.user
            )
            
            # Reset processing status
            document.processing_status = ProcessingStatus.PENDING
            document.processing_error = ""
            document.save()
            
            # Trigger async reprocessing
            from ..tasks import reprocess_document_chunks
            reprocess_document_chunks.send(str(document.id))
            
            return True
        except Document.DoesNotExist:
            return False
