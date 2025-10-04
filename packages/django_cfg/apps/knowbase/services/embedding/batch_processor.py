"""
High-performance batch embedding processor.

This module provides the main batch processing engine for generating
embeddings with optimized API calls and database operations.
"""

import time
import logging
from typing import List, Dict, Any, Optional

from django_cfg.apps.knowbase.utils.chunk_settings import get_embedding_batch_size, get_embedding_model
from django_cfg.apps.knowbase.config.settings import get_openai_api_key, get_cache_settings
from django_cfg.modules.django_llm.llm.client import LLMClient

from .models import ChunkData, EmbeddingResult, BatchProcessingResult, ProcessingConfig, ChunkType
from .processors import DocumentChunkProcessor, ArchiveChunkProcessor, ExternalDataChunkProcessor
from .batch_result import BatchResultBuilder

logger = logging.getLogger(__name__)


class OptimizedEmbeddingProcessor:
    """High-performance embedding processor with batch operations."""
    
    def __init__(self, batch_size: Optional[int] = None, embedding_model: Optional[str] = None):
        """
        Initialize the processor.
        
        Args:
            batch_size: Number of chunks to process in one API call (uses Constance setting if None)
            embedding_model: Embedding model to use (uses Constance setting if None)
        """
        # Use Constance settings if not provided
        self.batch_size = min(batch_size or get_embedding_batch_size(), 100)  # Conservative limit for stability
        self.embedding_model = embedding_model or get_embedding_model()
        
        # Initialize LLM client with OpenAI only for embeddings
        # OpenRouter doesn't support embedding models, so we use OpenAI directly
        # Use auto-configured LLMClient with explicit OpenAI preference for embeddings
        # Get cache settings from configuration (directory is auto-created)
        cache_settings = get_cache_settings()
        self.llm_client = LLMClient(
            preferred_provider="openai",  # Force OpenAI for embeddings
            cache_dir=cache_settings.cache_dir,
            cache_ttl=cache_settings.cache_ttl,
            max_cache_size=cache_settings.max_cache_size
        )
        
        # Processors for different chunk types
        self.processors = {
            ChunkType.DOCUMENT: DocumentChunkProcessor(),
            ChunkType.ARCHIVE: ArchiveChunkProcessor(),
            ChunkType.EXTERNAL_DATA: ExternalDataChunkProcessor()
        }
        
        logger.info(f"🚀 OptimizedEmbeddingProcessor initialized: batch_size={self.batch_size}, model={self.embedding_model}")
    
    def process_chunks_batch(self, chunks: List[ChunkData]) -> BatchProcessingResult:
        """
        Process multiple chunks with optimized batch operations.
        
        Args:
            chunks: List of chunks to process
            
        Returns:
            BatchProcessingResult with processing statistics
        """
        start_time = time.time()
        total_chunks = len(chunks)
        result_builder = BatchResultBuilder(total_chunks)
        
        logger.info(f"🔮 Starting batch processing of {total_chunks} chunks")
        
        # Process in batches
        for i in range(0, total_chunks, self.batch_size):
            batch = chunks[i:i + self.batch_size]
            batch_num = (i // self.batch_size) + 1
            total_batches = (total_chunks + self.batch_size - 1) // self.batch_size
            
            logger.info(f"🔮 Processing batch {batch_num}/{total_batches} ({len(batch)} chunks)")
            
            try:
                batch_results = self._process_single_batch(batch)
                result_builder.add_batch_results(batch_results)
                
                # Small delay between batches to respect rate limits
                if i + self.batch_size < total_chunks:
                    time.sleep(0.5)
                    
            except Exception as e:
                error_msg = f"Batch {batch_num} failed: {str(e)}"
                logger.error(f"❌ {error_msg}")
                result_builder.add_batch_error(error_msg, len(batch))
        
        processing_time = time.time() - start_time
        result = result_builder.build(processing_time)
        
        # Log using Pydantic model's summary
        summary = result.model_dump_summary()
        logger.info(f"🎉 Batch processing completed: {summary}")
        logger.info(f"📊 Performance: {summary['chunks_per_second']} chunks/sec, {summary['avg_cost_per_chunk']} per chunk")
        
        return result
    
    def _process_single_batch(self, batch: List[ChunkData]) -> List[EmbeddingResult]:
        """Process a single batch of chunks and return list of EmbeddingResult."""
        
        # Prepare content for all chunks
        prepared_contents = []
        chunk_mapping = {}  # Map index to chunk
        
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
            # Return failed results for all chunks
            return [
                EmbeddingResult(
                    chunk_id=chunk.id,
                    success=False,
                    error="No valid content to process"
                )
                for chunk in batch
            ]
        
        # Generate embeddings in batch
        try:
            embedding_results = self._generate_batch_embeddings(prepared_contents)
            
            # Process and save results
            final_results = []
            
            for idx, embedding_result in enumerate(embedding_results):
                if idx not in chunk_mapping:
                    continue
                
                chunk = chunk_mapping[idx]
                processor = self.processors[chunk.parent_type]
                
                # Set the chunk_id in the result
                embedding_result.chunk_id = chunk.id
                
                if embedding_result.success:
                    try:
                        logger.debug(f"🔄 Attempting to save embedding for chunk {chunk.id} (type: {chunk.parent_type})")
                        processor.save_embedding_result(chunk.id, embedding_result)
                        logger.info(f"✅ Successfully saved embedding for chunk {chunk.id}")
                        final_results.append(embedding_result)
                    except Exception as e:
                        error_msg = f"Failed to save embedding for chunk {chunk.id}: {e}"
                        logger.error(f"❌ {error_msg}")
                        failed_result = EmbeddingResult(
                            chunk_id=chunk.id,
                            success=False,
                            error=error_msg
                        )
                        final_results.append(failed_result)
                else:
                    final_results.append(embedding_result)
            
            return final_results
            
        except Exception as e:
            error_msg = f"Batch embedding generation failed: {e}"
            logger.error(f"❌ {error_msg}")
            # Return failed results for all chunks
            return [
                EmbeddingResult(
                    chunk_id=chunk.id,
                    success=False,
                    error=error_msg
                )
                for chunk in batch
            ]
    
    def _generate_batch_embeddings(self, contents: List[str]) -> List[EmbeddingResult]:
        """Generate embeddings for multiple contents using LLMClient."""
        
        results = []
        
        try:
            # Use LLMClient's generate_embedding method for each content
            # This handles both OpenAI and OpenRouter properly
            for idx, content in enumerate(contents):
                try:
                    # Use LLMClient's method which handles provider differences
                    embedding_response = self.llm_client.generate_embedding(
                        text=content,
                        model=self.embedding_model
                    )
                    
                    results.append(EmbeddingResult(
                        chunk_id="",  # Will be set by caller
                        embedding=embedding_response.embedding,
                        tokens=embedding_response.tokens,
                        cost=embedding_response.cost,
                        success=True
                    ))
                    
                except Exception as e:
                    logger.error(f"❌ Failed to generate embedding for content {idx}: {e}")
                    results.append(EmbeddingResult(
                        chunk_id="",
                        embedding=[],
                        tokens=0,
                        cost=0.0,
                        success=False,
                        error=str(e)
                    ))
            
            successful_count = len([r for r in results if r.success])
            logger.info(f"🎯 Generated {successful_count}/{len(results)} embeddings successfully")
            
            # Log details of each result
            for i, result in enumerate(results):
                if result.success:
                    logger.debug(f"  ✅ Result {i}: {result.tokens} tokens, ${result.cost:.4f}, embedding_len={len(result.embedding)}")
                else:
                    logger.debug(f"  ❌ Result {i}: {result.error}")
            
            return results
            
        except Exception as e:
            logger.error(f"❌ Batch embedding generation failed: {e}")
            # Return failed results for all contents
            return [
                EmbeddingResult(
                    chunk_id="",
                    embedding=[],
                    tokens=0,
                    cost=0.0,
                    success=False,
                    error=str(e)
                )
                for _ in contents
            ]
