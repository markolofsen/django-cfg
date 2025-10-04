"""
Async-compatible embedding processor for Django 5.2.

This module provides async/sync compatibility for embedding generation,
following Django 5.2 async best practices.
"""

import asyncio
import time
import logging
from typing import List, Dict, Any, Optional, Union

from asgiref.sync import sync_to_async, async_to_sync
from django.db import transaction

from django_cfg.apps.knowbase.models import DocumentChunk, ArchiveItemChunk
from django_cfg.apps.knowbase.utils.chunk_settings import get_embedding_batch_size, get_embedding_model

from .models import ChunkData, BatchProcessingResult, EmbeddingResult
from .batch_processor import OptimizedEmbeddingProcessor

logger = logging.getLogger(__name__)


def is_async_context() -> bool:
    """Detect current execution context."""
    try:
        asyncio.get_running_loop()
        return True
    except RuntimeError:
        return False


class AsyncOptimizedEmbeddingProcessor(OptimizedEmbeddingProcessor):
    """
    Async-compatible embedding processor that works in both sync and async contexts.
    
    Based on Django 5.2 async patterns:
    - Context-aware operations
    - Proper async/sync method selection
    - Compatible with both WSGI and ASGI
    """
    
    def __init__(self, batch_size: Optional[int] = None, embedding_model: Optional[str] = None):
        """Initialize async-compatible processor."""
        super().__init__(batch_size, embedding_model)
        logger.info(f"🚀 AsyncOptimizedEmbeddingProcessor initialized: async_context={is_async_context()}")
    
    async def aprocess_chunks_batch(self, chunks: List[ChunkData]) -> BatchProcessingResult:
        """
        Async version of batch processing.
        
        Uses Django 5.2 async ORM methods (a-prefixed) for database operations.
        """
        start_time = time.time()
        total_chunks = len(chunks)
        successful_chunks = 0
        failed_chunks = 0
        total_tokens = 0
        total_cost = 0.0
        errors = []
        
        logger.info(f"🔮 Starting async batch processing of {total_chunks} chunks")
        
        # Process in batches
        for i in range(0, total_chunks, self.batch_size):
            batch = chunks[i:i + self.batch_size]
            batch_num = (i // self.batch_size) + 1
            total_batches = (total_chunks + self.batch_size - 1) // self.batch_size
            
            logger.info(f"🔮 Processing async batch {batch_num}/{total_batches} ({len(batch)} chunks)")
            
            try:
                batch_result = await self._aprocess_single_batch(batch)
                
                successful_chunks += batch_result['successful']
                failed_chunks += batch_result['failed']
                total_tokens += batch_result['tokens']
                total_cost += batch_result['cost']
                errors.extend(batch_result['errors'])
                
                # Small async delay between batches
                if i + self.batch_size < total_chunks:
                    await asyncio.sleep(0.5)
                    
            except Exception as e:
                error_msg = f"Async batch {batch_num} failed: {str(e)}"
                logger.error(f"❌ {error_msg}")
                errors.append(error_msg)
                failed_chunks += len(batch)
        
        processing_time = time.time() - start_time
        
        result = BatchProcessingResult(
            total_chunks=total_chunks,
            successful_chunks=successful_chunks,
            failed_chunks=failed_chunks,
            total_tokens=total_tokens,
            total_cost=total_cost,
            processing_time=processing_time,
            errors=errors
        )
        
        logger.info(
            f"🎉 Async batch processing completed: {successful_chunks}/{total_chunks} successful, "
            f"{total_tokens} tokens, ${total_cost:.4f} cost, {processing_time:.2f}s"
        )
        
        return result
    
    async def _aprocess_single_batch(self, batch: List[ChunkData]) -> Dict[str, Any]:
        """Async version of single batch processing."""
        
        # Prepare content for all chunks (sync operation)
        prepared_contents = []
        chunk_mapping = {}
        
        for idx, chunk in enumerate(batch):
            processor = self.processors.get(chunk.parent_type)
            if not processor:
                logger.warning(f"⚠️ Unknown chunk type: {chunk.parent_type}")
                continue
            
            try:
                content = processor.prepare_content_for_embedding(chunk)
                if content and content.strip():
                    prepared_contents.append(content)
                    chunk_mapping[len(prepared_contents) - 1] = chunk
                else:
                    logger.warning(f"⚠️ Empty content for chunk {chunk.id}")
            except Exception as e:
                logger.error(f"❌ Failed to prepare content for chunk {chunk.id}: {e}")
        
        if not prepared_contents:
            return {
                'successful': 0,
                'failed': len(batch),
                'tokens': 0,
                'cost': 0.0,
                'errors': ['No valid content to process']
            }
        
        # Generate embeddings (sync operation - OpenAI client is sync)
        try:
            embedding_results = self._generate_batch_embeddings(prepared_contents)
            
            # Save results using async database operations
            successful = 0
            failed = 0
            total_tokens = 0
            total_cost = 0.0
            errors = []
            
            for idx, embedding_result in enumerate(embedding_results):
                if idx not in chunk_mapping:
                    continue
                
                chunk = chunk_mapping[idx]
                
                if embedding_result.success:
                    try:
                        await self._asave_embedding_result(chunk, embedding_result)
                        successful += 1
                        total_tokens += embedding_result.tokens
                        total_cost += embedding_result.cost
                    except Exception as e:
                        error_msg = f"Failed to save async embedding for chunk {chunk.id}: {e}"
                        logger.error(f"❌ {error_msg}")
                        errors.append(error_msg)
                        failed += 1
                else:
                    errors.append(embedding_result.error or f"Failed to generate embedding for chunk {chunk.id}")
                    failed += 1
            
            return {
                'successful': successful,
                'failed': failed,
                'tokens': total_tokens,
                'cost': total_cost,
                'errors': errors
            }
            
        except Exception as e:
            error_msg = f"Async batch embedding generation failed: {e}"
            logger.error(f"❌ {error_msg}")
            return {
                'successful': 0,
                'failed': len(batch),
                'tokens': 0,
                'cost': 0.0,
                'errors': [error_msg]
            }
    
    async def _asave_embedding_result(self, chunk: ChunkData, result: EmbeddingResult) -> None:
        """Save embedding result using async database operations."""
        
        try:
            if chunk.parent_type == "document":
                # Use Django 5.2 async ORM methods
                chunk_obj = await DocumentChunk.objects.aget(id=chunk.id)
                chunk_obj.embedding = result.embedding
                chunk_obj.token_count = result.tokens
                chunk_obj.embedding_cost = result.cost
                await chunk_obj.asave(update_fields=['embedding', 'token_count', 'embedding_cost'])
                
                logger.debug(f"✅ Async document chunk {chunk.id} embedding saved: {result.tokens} tokens, ${result.cost:.4f}")
                
            elif chunk.parent_type == "archive":
                # Use async ORM with select_related
                chunk_obj = await ArchiveItemChunk.objects.select_related('item').aget(id=chunk.id)
                chunk_obj.embedding = result.embedding
                chunk_obj.token_count = result.tokens
                chunk_obj.embedding_cost = result.cost
                await chunk_obj.asave(update_fields=['embedding', 'token_count', 'embedding_cost'])
                
                # Update parent item statistics
                item = chunk_obj.item
                item.total_tokens += result.tokens
                item.processing_cost += result.cost
                await item.asave(update_fields=['total_tokens', 'processing_cost'])
                
                logger.debug(f"✅ Async archive chunk {chunk.id} embedding saved: {result.tokens} tokens, ${result.cost:.4f}")
            else:
                raise ValueError(f"Unknown chunk type: {chunk.parent_type}")
                
        except Exception as e:
            logger.error(f"❌ Failed to save async embedding for chunk {chunk.id}: {e}")
            raise
    
    def process_chunks_batch_context_aware(self, chunks: List[ChunkData]) -> BatchProcessingResult:
        """
        Context-aware processing that works in both sync and async contexts.
        
        Based on Django 5.2 async patterns.
        """
        if is_async_context():
            # We're in async context - use async methods
            logger.info("🔮 Detected async context - using async processing")
            # Convert async method to sync for compatibility
            return async_to_sync(self.aprocess_chunks_batch)(chunks)
        else:
            # We're in sync context - use sync methods
            logger.info("🔮 Detected sync context - using sync processing")
            return super().process_chunks_batch(chunks)
