"""
Semantic search service with pgvector.
"""

from typing import List, Optional, Dict, Any
from pgvector.django import CosineDistance
from django_cfg.modules.django_llm.llm.client import LLMClient
from ..models import DocumentChunk, Document, ArchiveItemChunk
from ..config.settings import get_openai_api_key, get_cache_settings, get_threshold_for_type
from ..utils.validation import validate_similarity_score
from ..utils.chunk_settings import get_embedding_model
from .base import BaseService


class SearchService(BaseService):
    """Semantic search service with pgvector."""
    
    def __init__(self, user):
        """Initialize with OpenAI-only client for embeddings."""
        super().__init__(user)
        
        # Override with auto-configured client with explicit OpenAI preference for embeddings
        cache_settings = get_cache_settings()
        self.llm_client = LLMClient(
            preferred_provider="openai",  # Force OpenAI for embeddings
            cache_dir=cache_settings.cache_dir,
            cache_ttl=cache_settings.cache_ttl,
            max_cache_size=cache_settings.max_cache_size
        )
    
    def semantic_search_universal(
        self,
        query: str,
        limit: int = 5,
        threshold: Optional[float] = None,  # Now optional, will use type-specific thresholds
        document_ids: Optional[List[str]] = None,
        archive_ids: Optional[List[str]] = None,
        include_documents: bool = True,
        include_archives: bool = True,
        include_external: bool = True,
        external_model_names: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """Perform semantic search across all user's content (documents + archives)."""
        
        # Generate query embedding with specified model
        embedding_model = get_embedding_model()
        embedding_result = self.llm_client.generate_embedding(
            text=query,
            model=embedding_model
        )
        query_embedding = embedding_result.embedding
        
        results = []
        
        # Search in document chunks
        if include_documents:
            doc_threshold = threshold if threshold is not None else get_threshold_for_type('document')
            
            doc_queryset = DocumentChunk.objects.filter(
                user=self.user,
                embedding__isnull=False  # Ensure embedding exists
            )
            
            if document_ids:
                doc_queryset = doc_queryset.filter(document_id__in=document_ids)
            
            doc_results = doc_queryset.annotate(
                similarity=1 - CosineDistance('embedding', query_embedding)
            ).filter(
                similarity__gte=doc_threshold
            ).select_related('document').order_by('-similarity')
            
            for chunk in doc_results:
                # Validate similarity score using utility function
                similarity_value = validate_similarity_score(chunk.similarity)
                if similarity_value is None:
                    continue  # Skip chunks with invalid similarity
                
                results.append({
                    'type': 'document',
                    'chunk': chunk,
                    'similarity': similarity_value,
                    'source_title': chunk.document.title,
                    'content': chunk.content,
                    'metadata': {
                        'document_id': str(chunk.document.id),
                        'chunk_index': chunk.chunk_index,
                        'token_count': chunk.token_count
                    }
                })
        
        # Search in archive chunks
        if include_archives:
            archive_threshold = threshold if threshold is not None else get_threshold_for_type('archive')
            
            archive_queryset = ArchiveItemChunk.objects.filter(
                user=self.user,
                embedding__isnull=False  # Ensure embedding exists
            )
            
            if archive_ids:
                archive_queryset = archive_queryset.filter(archive_id__in=archive_ids)
            
            archive_results = archive_queryset.annotate(
                similarity=1 - CosineDistance('embedding', query_embedding)
            ).filter(
                similarity__gte=archive_threshold
            ).select_related('archive', 'item').order_by('-similarity')
            
            for chunk in archive_results:
                # Validate similarity score using utility function
                similarity_value = validate_similarity_score(chunk.similarity)
                if similarity_value is None:
                    continue  # Skip chunks with invalid similarity
                
                results.append({
                    'type': 'archive',
                    'chunk': chunk,
                    'similarity': similarity_value,
                    'source_title': f"{chunk.archive.title} / {chunk.item.item_name}",
                    'content': chunk.content,
                    'metadata': {
                        'archive_id': str(chunk.archive.id),
                        'item_id': str(chunk.item.id),
                        'chunk_index': chunk.chunk_index,
                        'token_count': chunk.token_count,
                        'chunk_type': chunk.chunk_type,
                        'context_metadata': chunk.context_metadata
                    }
                })
        
        # Search in external data
        if include_external:
            from ..mixins.service import ExternalDataService
            external_service = ExternalDataService(self.user)
            
            # Pass threshold=None to use per-object thresholds, or explicit threshold if provided
            external_results = external_service.search_external_data(
                query=query,
                limit=limit,
                threshold=threshold,  # None = use per-object thresholds, explicit value = global override
                source_identifiers=external_model_names
            )
            
            results.extend(external_results)
        
        # Sort all results by similarity and limit
        results.sort(key=lambda x: x['similarity'], reverse=True)
        return results[:limit]
    
    def semantic_search(
        self,
        query: str,
        limit: int = 5,
        threshold: float = 0.7,
        document_ids: Optional[List[str]] = None
    ) -> List[DocumentChunk]:
        """Perform semantic search across user's documents (legacy method for backward compatibility)."""
        
        # Generate query embedding with specified model
        embedding_model = get_embedding_model()
        embedding_result = self.llm_client.generate_embedding(
            text=query,
            model=embedding_model
        )
        query_embedding = embedding_result.embedding  # Extract the actual embedding array
        
        # Build queryset
        queryset = DocumentChunk.objects.filter(user=self.user)
        
        if document_ids:
            queryset = queryset.filter(document_id__in=document_ids)
        
        # Perform similarity search
        results = queryset.annotate(
            similarity=1 - CosineDistance('embedding', query_embedding)
        ).filter(
            similarity__gte=threshold
        ).order_by('-similarity')[:limit]
        
        return list(results)
    
    def search_by_text_universal(
        self,
        query: str,
        limit: int = 10,
        include_documents: bool = True,
        include_archives: bool = True
    ) -> List[Dict[str, Any]]:
        """Universal text search across documents and archives."""
        
        results = []
        
        # Search in documents
        if include_documents:
            doc_results = DocumentChunk.objects.filter(
                user=self.user,
                content__icontains=query
            ).select_related('document')[:limit//2 if include_archives else limit]
            
            for chunk in doc_results:
                results.append({
                    'type': 'document',
                    'chunk': chunk,
                    'source_title': chunk.document.title,
                    'content': chunk.content,
                    'metadata': {
                        'document_id': str(chunk.document.id),
                        'chunk_index': chunk.chunk_index,
                        'token_count': chunk.token_count
                    }
                })
        
        # Search in archives
        if include_archives:
            archive_results = ArchiveItemChunk.objects.filter(
                user=self.user,
                content__icontains=query
            ).select_related('archive', 'item')[:limit//2 if include_documents else limit]
            
            for chunk in archive_results:
                results.append({
                    'type': 'archive',
                    'chunk': chunk,
                    'source_title': f"{chunk.archive.title} / {chunk.item.item_name}",
                    'content': chunk.content,
                    'metadata': {
                        'archive_id': str(chunk.archive.id),
                        'item_id': str(chunk.item.id),
                        'chunk_index': chunk.chunk_index,
                        'token_count': chunk.token_count,
                        'chunk_type': chunk.chunk_type,
                        'context_metadata': chunk.context_metadata
                    }
                })
        
        return results[:limit]
    
    def search_by_text(
        self,
        query: str,
        limit: int = 10
    ) -> List[DocumentChunk]:
        """Traditional text search as fallback (legacy method)."""
        
        results = DocumentChunk.objects.filter(
            user=self.user,
            content__icontains=query
        ).order_by('-created_at')[:limit]
        
        return list(results)
    
    def get_similar_documents(
        self,
        document_id: str,
        limit: int = 5
    ) -> List[DocumentChunk]:
        """Find similar documents to given document."""
        
        # Get document's first chunk as reference
        reference_chunk = DocumentChunk.objects.filter(
            document_id=document_id,
            user=self.user,
            chunk_index=0
        ).first()
        
        if not reference_chunk:
            return []
        
        # Find similar chunks
        results = DocumentChunk.objects.filter(
            user=self.user
        ).exclude(
            document_id=document_id
        ).annotate(
            similarity=1 - CosineDistance('embedding', reference_chunk.embedding)
        ).order_by('-similarity')[:limit]
        
        return list(results)
    
    def search_documents_by_title(
        self,
        query: str,
        limit: int = 10
    ) -> List[Document]:
        """Search documents by title."""
        
        results = Document.objects.filter(
            user=self.user,
            title__icontains=query
        ).order_by('-created_at')[:limit]
        
        return list(results)
