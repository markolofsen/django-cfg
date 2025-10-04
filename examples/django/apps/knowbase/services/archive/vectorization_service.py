"""
Archive vectorization service.

Handles embedding generation for archive chunks with batch processing.
"""

from typing import List, Dict, Any, Optional
from django.contrib.auth import get_user_model
from django.db import transaction, models
import logging
from ...models.archive import ArchiveItemChunk
from django_cfg.modules.django_llm.llm.models import EmbeddingResponse
from ..base import BaseService
from ..embedding import process_archive_chunks_optimized
from .exceptions import VectorizationError


User = get_user_model()
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

class VectorizationResult:
    """Result of vectorization operation."""
    
    def __init__(self):
        self.vectorized_count: int = 0
        self.failed_count: int = 0
        self.total_tokens: int = 0
        self.total_cost: float = 0.0
        self.errors: List[str] = []


class ArchiveVectorizationService(BaseService):
    """Service for vectorizing archive chunks."""
    
    def __init__(self, user: User):
        super().__init__(user)
        self.batch_size = 10  # Process chunks in batches
    
    def vectorize_chunks_batch(self, chunks: List[ArchiveItemChunk]) -> Dict[str, Any]:
        """Vectorize chunks using optimized batch processing."""
        
        if not chunks:
            logger.warning("🔮 No chunks provided for vectorization")
            return {
                'vectorized_count': 0,
                'failed_count': 0,
                'total_tokens': 0,
                'total_cost': 0.0,
                'success_rate': 0.0,
                'errors': []
            }
        
        logger.info(f"🔮 Starting optimized vectorization of {len(chunks)} chunks")
        
        try:
            # Use optimized batch processor
            result = process_archive_chunks_optimized(chunks)
            
            logger.info(
                f"🔮 Optimized vectorization completed: {result.successful_chunks}/{result.total_chunks} chunks, "
                f"{result.failed_chunks} failed, {result.total_tokens} tokens, ${result.total_cost:.4f} cost, "
                f"{result.processing_time:.2f}s"
            )
            
            return {
                'vectorized_count': result.successful_chunks,
                'failed_count': result.failed_chunks,
                'total_tokens': result.total_tokens,
                'total_cost': result.total_cost,
                'success_rate': result.successful_chunks / result.total_chunks if result.total_chunks > 0 else 0.0,
                'errors': result.errors
            }
            
        except Exception as e:
            logger.error(f"❌ Optimized vectorization failed: {e}")
            raise VectorizationError(
                message=f"Optimized vectorization failed: {str(e)}",
                code="OPTIMIZED_VECTORIZATION_FAILED",
                details={
                    "total_chunks": len(chunks),
                    "error": str(e)
                }
            ) from e
    
    def _vectorize_chunk_batch(self, chunks: List[ArchiveItemChunk]) -> VectorizationResult:
        """Vectorize a single batch of chunks."""
        
        result = VectorizationResult()
        
        for chunk in chunks:
            try:
                # Skip if already vectorized
                if chunk.embedding is not None and len(chunk.embedding) > 0:
                    logger.debug(f"🔮 Chunk {chunk.id} already vectorized, skipping")
                    continue
                
                logger.debug(f"🔮 Generating embedding for chunk {chunk.id} ({chunk.item.item_name})")
                
                # Generate embedding
                embedding_result = self._generate_chunk_embedding(chunk)
                
                if embedding_result:
                    # Update chunk with embedding
                    with transaction.atomic():
                        chunk.embedding = embedding_result.embedding
                        chunk.token_count = embedding_result.tokens
                        chunk.embedding_cost = embedding_result.cost
                        chunk.save()
                        
                        # Update item statistics
                        item = chunk.item
                        item.total_tokens += embedding_result.tokens
                        item.processing_cost += embedding_result.cost
                        item.save()
                    
                    result.vectorized_count += 1
                    result.total_tokens += embedding_result.tokens
                    logger.debug(f"✅ Chunk {chunk.id} vectorized successfully: {embedding_result.tokens} tokens, ${embedding_result.cost:.4f}")
                    result.total_cost += embedding_result.cost
                else:
                    result.failed_count += 1
                    error_msg = f"Failed to generate embedding for chunk {chunk.id}"
                    result.errors.append(error_msg)
                    logger.error(f"❌ {error_msg}")
            
            except Exception as e:
                result.failed_count += 1
                error_msg = f"Error processing chunk {chunk.id}: {str(e)}"
                result.errors.append(error_msg)
                logger.error(f"❌ {error_msg}")
                continue
        
        return result
    
    def _generate_chunk_embedding(self, chunk: ArchiveItemChunk) -> Optional[EmbeddingResponse]:
        """Generate embedding for a single chunk."""
        
        if not chunk.content or not chunk.content.strip():
            return None
        
        try:
            # Prepare content for embedding
            content_for_embedding = self._prepare_content_for_embedding(chunk)
            
            logger.debug(f"🔮 Prepared content for embedding: {len(content_for_embedding)} chars")
            
            # Generate embedding using LLM client with specified model
            from django_cfg.apps.knowbase.utils.chunk_settings import get_embedding_model
            embedding_model = get_embedding_model()
            embedding_result = self.llm_client.generate_embedding(
                text=content_for_embedding,
                model=embedding_model
            )
            
            if embedding_result:
                logger.debug(f"🔮 Embedding generated successfully for chunk {chunk.id}")
                logger.debug(f"🔮 Embedding result structure: {list(embedding_result.keys()) if isinstance(embedding_result, dict) else type(embedding_result)}")
            else:
                logger.warning(f"🔮 Embedding generation returned None for chunk {chunk.id}")
            
            return embedding_result
            
        except Exception as e:
            # Log error but don't raise - we want to continue with other chunks
            logger.error(f"🔮 Error generating embedding for chunk {chunk.id}: {str(e)}", exc_info=True)
            return None
    
    def _prepare_content_for_embedding(self, chunk: ArchiveItemChunk) -> str:
        """Prepare chunk content for embedding generation."""
        
        content = chunk.content
        context = chunk.context_metadata
        
        # Add context information to improve embedding quality
        context_prefix = self._build_context_prefix(context)
        
        # Combine context and content
        if context_prefix:
            enhanced_content = f"{context_prefix}\n\n{content}"
        else:
            enhanced_content = content
        
        # Ensure content is not too long for embedding model
        max_length = 8000  # Conservative limit for most embedding models
        if len(enhanced_content) > max_length:
            # Truncate but keep context prefix
            if context_prefix:
                available_length = max_length - len(context_prefix) - 4  # Account for separators
                truncated_content = content[:available_length] + "..."
                enhanced_content = f"{context_prefix}\n\n{truncated_content}"
            else:
                enhanced_content = content[:max_length] + "..."
        
        return enhanced_content
    
    def _build_context_prefix(self, context: Dict[str, Any]) -> str:
        """Build context prefix to enhance embedding quality."""
        
        prefix_parts = []
        
        # Archive context
        archive_info = context.get('archive_info', {})
        if archive_info.get('title'):
            prefix_parts.append(f"Archive: {archive_info['title']}")
        
        # Item context
        item_info = context.get('item_info', {})
        if item_info.get('relative_path'):
            prefix_parts.append(f"File: {item_info['relative_path']}")
        
        if item_info.get('content_type'):
            prefix_parts.append(f"Type: {item_info['content_type']}")
        
        if item_info.get('language'):
            prefix_parts.append(f"Language: {item_info['language']}")
        
        # Structure context
        structure_info = context.get('structure_info', {})
        if structure_info.get('element_name'):
            prefix_parts.append(f"Element: {structure_info['element_name']}")
        
        if structure_info.get('section_title'):
            prefix_parts.append(f"Section: {structure_info['section_title']}")
        
        # Semantic context
        semantic_info = context.get('semantic_info', {})
        if semantic_info.get('content_purpose'):
            prefix_parts.append(f"Purpose: {semantic_info['content_purpose']}")
        
        return " | ".join(prefix_parts) if prefix_parts else ""
    
    def vectorize_single_chunk(self, chunk_id: str) -> Dict[str, Any]:
        """Vectorize a single chunk by ID."""
        
        try:
            chunk = ArchiveItemChunk.objects.get(id=chunk_id, user=self.user)
        except ArchiveItemChunk.DoesNotExist:
            raise VectorizationError(
                message=f"Chunk not found: {chunk_id}",
                code="CHUNK_NOT_FOUND",
                details={"chunk_id": chunk_id}
            )
        
        # Check if already vectorized
        if chunk.embedding is not None and len(chunk.embedding) > 0:
            return {
                'status': 'already_vectorized',
                'chunk_id': chunk_id,
                'token_count': chunk.token_count,
                'cost': chunk.embedding_cost
            }
        
        # Generate embedding
        embedding_result = self._generate_chunk_embedding(chunk)
        
        if not embedding_result:
            raise VectorizationError(
                message=f"Failed to generate embedding for chunk {chunk_id}",
                code="EMBEDDING_GENERATION_FAILED",
                details={"chunk_id": chunk_id}
            )
        
        # Update chunk
        with transaction.atomic():
            chunk.embedding = embedding_result.embedding
            chunk.token_count = embedding_result.tokens
            chunk.embedding_cost = embedding_result.cost
            chunk.save()
            
            # Update item statistics
            item = chunk.item
            item.total_tokens += embedding_result.tokens
            item.processing_cost += embedding_result.cost
            item.save()
        
        return {
            'status': 'vectorized',
            'chunk_id': chunk_id,
            'token_count': embedding_result.tokens,
            'cost': embedding_result.cost
        }
    
    def get_vectorization_statistics(self, archive_id: Optional[str] = None) -> Dict[str, Any]:
        """Get vectorization statistics for user's chunks."""
        
        queryset = ArchiveItemChunk.objects.filter(user=self.user)
        
        if archive_id:
            queryset = queryset.filter(archive_id=archive_id)
        
        total_chunks = queryset.count()
        vectorized_chunks = queryset.filter(embedding__isnull=False).count()
        pending_chunks = total_chunks - vectorized_chunks
        
        # Aggregate statistics
        stats = queryset.aggregate(
            total_tokens=models.Sum('token_count'),
            total_cost=models.Sum('embedding_cost'),
            avg_tokens_per_chunk=models.Avg('token_count'),
            avg_cost_per_chunk=models.Avg('embedding_cost')
        )
        
        return {
            'total_chunks': total_chunks,
            'vectorized_chunks': vectorized_chunks,
            'pending_chunks': pending_chunks,
            'vectorization_rate': vectorized_chunks / total_chunks if total_chunks > 0 else 0.0,
            'total_tokens': stats['total_tokens'] or 0,
            'total_cost': stats['total_cost'] or 0.0,
            'avg_tokens_per_chunk': stats['avg_tokens_per_chunk'] or 0.0,
            'avg_cost_per_chunk': stats['avg_cost_per_chunk'] or 0.0
        }
    
    def revectorize_chunks(
        self, 
        chunk_ids: List[str], 
        force: bool = False
    ) -> Dict[str, Any]:
        """Re-vectorize specific chunks."""
        
        chunks = ArchiveItemChunk.objects.filter(
            id__in=chunk_ids,
            user=self.user
        )
        
        if not force:
            # Only re-vectorize chunks that don't have embeddings
            chunks = chunks.filter(embedding__isnull=True)
        
        return self.vectorize_chunks_batch(list(chunks))
    
    def cleanup_failed_vectorizations(self) -> Dict[str, Any]:
        """Clean up chunks that failed vectorization."""
        
        # Find chunks without embeddings that are older than 1 hour
        from django.utils import timezone
        from datetime import timedelta
        
        cutoff_time = timezone.now() - timedelta(hours=1)
        
        failed_chunks = ArchiveItemChunk.objects.filter(
            user=self.user,
            embedding__isnull=True,
            created_at__lt=cutoff_time
        )
        
        failed_count = failed_chunks.count()
        
        # Attempt to re-vectorize
        if failed_count > 0:
            result = self.vectorize_chunks_batch(list(failed_chunks))
            
            return {
                'found_failed_chunks': failed_count,
                'retry_result': result
            }
        
        return {
            'found_failed_chunks': 0,
            'retry_result': None
        }
