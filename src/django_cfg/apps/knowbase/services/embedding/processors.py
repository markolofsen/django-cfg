"""
Chunk processors for different content types.

This module provides specialized processors for handling
document and archive chunks with their specific requirements.
"""

import logging
from typing import Protocol

from django_cfg.apps.knowbase.models import DocumentChunk, ArchiveItemChunk, ExternalDataChunk
from .models import ChunkData, EmbeddingResult

logger = logging.getLogger(__name__)


class ChunkProcessor(Protocol):
    """Protocol for chunk processors."""
    
    def prepare_content_for_embedding(self, chunk: ChunkData) -> str:
        """Prepare chunk content for embedding generation."""
        ...
    
    def save_embedding_result(self, chunk_id: str, result: EmbeddingResult) -> None:
        """Save embedding result to database."""
        ...


class DocumentChunkProcessor:
    """Processor for document chunks."""
    
    def prepare_content_for_embedding(self, chunk: ChunkData) -> str:
        """Prepare document chunk content for embedding."""
        return chunk.content.strip()
    
    def save_embedding_result(self, chunk_id: str, result: EmbeddingResult) -> None:
        """Save embedding result for document chunk."""
        try:
            logger.debug(f"🔍 Looking for document chunk with id: {chunk_id}")
            chunk = DocumentChunk.objects.get(id=chunk_id)
            logger.debug(f"📄 Found document chunk: {chunk.id}, current embedding length: {len(chunk.embedding) if chunk.embedding is not None and len(chunk.embedding) > 0 else 0}")
            
            chunk.embedding = result.embedding
            chunk.token_count = result.tokens
            chunk.embedding_cost = result.cost
            chunk.save(update_fields=['embedding', 'token_count', 'embedding_cost'])
            
            logger.info(f"✅ Document chunk {chunk_id} embedding saved: {result.tokens} tokens, ${result.cost:.4f}, embedding_len={len(result.embedding)}")
            
        except DocumentChunk.DoesNotExist:
            logger.error(f"❌ Document chunk {chunk_id} not found")
            raise
        except Exception as e:
            logger.error(f"❌ Error saving document chunk {chunk_id}: {e}")
            raise


class ArchiveChunkProcessor:
    """Processor for archive chunks."""
    
    def prepare_content_for_embedding(self, chunk: ChunkData) -> str:
        """Prepare archive chunk content for embedding with context."""
        content = chunk.content
        context = chunk.context_metadata or {}
        
        # Build context prefix for better embeddings
        context_parts = []
        
        if context.get('file_path'):
            context_parts.append(f"File: {context['file_path']}")
        if context.get('function_name'):
            context_parts.append(f"Function: {context['function_name']}")
        if context.get('class_name'):
            context_parts.append(f"Class: {context['class_name']}")
        if context.get('language'):
            context_parts.append(f"Language: {context['language']}")
        
        if context_parts:
            context_prefix = " | ".join(context_parts)
            enhanced_content = f"{context_prefix}\n\n{content}"
        else:
            enhanced_content = content
        
        # Ensure content is not too long for embedding model
        max_length = 8000  # Conservative limit
        if len(enhanced_content) > max_length:
            if context_parts:
                context_prefix_len = len(context_prefix) + 2  # +2 for \n\n
                available_content_len = max_length - context_prefix_len
                if available_content_len > 100:  # Ensure we have meaningful content
                    truncated_content = content[:available_content_len] + "..."
                    enhanced_content = f"{context_prefix}\n\n{truncated_content}"
                else:
                    enhanced_content = content[:max_length] + "..."
            else:
                enhanced_content = content[:max_length] + "..."
        
        return enhanced_content.strip()
    
    def save_embedding_result(self, chunk_id: str, result: EmbeddingResult) -> None:
        """Save embedding result for archive chunk."""
        try:
            chunk = ArchiveItemChunk.objects.select_related('item').get(id=chunk_id)
            chunk.embedding = result.embedding
            chunk.token_count = result.tokens
            chunk.embedding_cost = result.cost
            chunk.save(update_fields=['embedding', 'token_count', 'embedding_cost'])
            
            # Update parent item statistics
            item = chunk.item
            item.total_tokens += result.tokens
            item.processing_cost += result.cost
            item.save(update_fields=['total_tokens', 'processing_cost'])
            
            logger.debug(f"✅ Archive chunk {chunk_id} embedding saved: {result.tokens} tokens, ${result.cost:.4f}")
            
        except ArchiveItemChunk.DoesNotExist:
            logger.error(f"❌ Archive chunk {chunk_id} not found")
            raise


class ExternalDataChunkProcessor:
    """Processor for external data chunks."""
    
    def prepare_content_for_embedding(self, chunk: ChunkData) -> str:
        """Prepare external data chunk content for embedding."""
        return chunk.content.strip()
    
    def save_embedding_result(self, chunk_id: str, result: EmbeddingResult) -> None:
        """Save embedding result for external data chunk."""
        try:
            logger.debug(f"🔍 Looking for external data chunk with id: {chunk_id}")
            chunk = ExternalDataChunk.objects.get(id=chunk_id)
            logger.debug(f"🔗 Found external data chunk: {chunk.id}, current embedding length: {len(chunk.embedding) if chunk.embedding is not None and len(chunk.embedding) > 0 else 0}")
            
            chunk.embedding = result.embedding
            chunk.token_count = result.tokens
            chunk.embedding_cost = result.cost
            chunk.save(update_fields=['embedding', 'token_count', 'embedding_cost'])
            
            logger.info(f"✅ External data chunk {chunk_id} embedding saved: {result.tokens} tokens, ${result.cost:.4f}, embedding_len={len(result.embedding)}")
            
        except ExternalDataChunk.DoesNotExist:
            logger.error(f"❌ External data chunk {chunk_id} not found")
            raise
        except Exception as e:
            logger.error(f"❌ Error saving external data chunk {chunk_id}: {e}")
            raise
