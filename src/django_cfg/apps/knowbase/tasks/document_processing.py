"""
Document processing tasks with Dramatiq.
"""

import dramatiq
import logging
import time
from typing import Dict, List, Any, Tuple, Optional
from django.db import transaction
from django.utils import timezone
from django_cfg.modules.django_llm.llm.client import LLMClient
from django.conf import settings

from ..models import Document, DocumentChunk, ProcessingStatus
from ..utils.text_processing import TextProcessor, SemanticChunker
from ..services.embedding import process_document_chunks_optimized
from ..utils.chunk_settings import get_chunking_params_for_type, get_embedding_model

logger = logging.getLogger(__name__)


@dramatiq.actor(
    queue_name="knowbase",
    max_retries=3,
    min_backoff=1000,  # 1 second
    max_backoff=30000,  # 30 seconds
    priority=5
)
def process_document_async(
    document_id: str,
    chunk_size: Optional[int] = None,
    chunk_overlap: Optional[int] = None,
    embedding_model: Optional[str] = None
) -> Dict[str, Any]:
    """
    Process document asynchronously with full pipeline.
    
    Args:
        document_id: Document UUID to process
        chunk_size: Maximum chunk size in characters (uses Constance setting if None)
        chunk_overlap: Overlap between chunks (uses Constance setting if None)
        embedding_model: Model to use for embeddings (uses Constance setting if None)
        
    Returns:
        Processing results with statistics
    """
    start_time = time.time()
    
    try:
        with transaction.atomic():
            # Load document
            document = Document.objects.select_for_update().get(
                id=document_id
            )
            
            # Update processing status
            document.processing_status = ProcessingStatus.PROCESSING
            document.processing_started_at = timezone.now()
            document.save(update_fields=['processing_status', 'processing_started_at'])
            
            logger.info(f"Starting document processing: {document_id}")
            
            # Get dynamic settings from Constance
            chunking_params = get_chunking_params_for_type('document')
            final_chunk_size = chunk_size or chunking_params['chunk_size']
            final_chunk_overlap = chunk_overlap or chunking_params['overlap']
            final_embedding_model = embedding_model or get_embedding_model()
            
            logger.info(f"Using dynamic settings: chunk_size={final_chunk_size}, overlap={final_chunk_overlap}, model={final_embedding_model}")
            
            # Initialize services
            text_processor = TextProcessor()
            chunker = SemanticChunker(
                chunk_size=final_chunk_size,
                overlap=final_chunk_overlap
            )
            
            # Step 1: Clean and preprocess text
            cleaned_content = text_processor.clean_text(document.content)
            
            # Step 2: Create semantic chunks
            chunks = chunker.create_chunks(cleaned_content)
            
            logger.info(f"Created {len(chunks)} chunks for document {document_id}")
            
            # Step 3: Create chunks without embeddings first
            chunk_objects = []
            for idx, chunk_text in enumerate(chunks):
                chunk = DocumentChunk(
                    document=document,
                    user_id=document.user_id,
                    content=chunk_text,
                    chunk_index=idx,
                    character_count=len(chunk_text),
                    embedding_model=final_embedding_model,
                    embedding=[0.0] * 1536,  # Temporary zero vector, will be replaced
                    metadata={
                        "processed_at": timezone.now().isoformat(),
                        "chunk_size": len(chunk_text),
                        "overlap_size": final_chunk_overlap if idx > 0 else 0
                    }
                )
                chunk_objects.append(chunk)
            
            # Bulk create chunks for performance
            DocumentChunk.objects.bulk_create(
                chunk_objects,
                batch_size=100
            )
            
            # Step 4: Generate embeddings using optimized processor
            created_chunks = DocumentChunk.objects.filter(document=document).order_by('chunk_index')
            chunks_list = list(created_chunks)
            logger.info(f"🔍 About to process {len(chunks_list)} chunks for embeddings")
            
            embedding_result = process_document_chunks_optimized(chunks_list)
            
            logger.info(f"🔍 Embedding result: {embedding_result.successful_chunks}/{embedding_result.total_chunks}")
            
            total_tokens = embedding_result.total_tokens
            total_cost = embedding_result.total_cost
            
            logger.info(
                f"Optimized embedding processing: {embedding_result.successful_chunks}/{embedding_result.total_chunks} chunks, "
                f"{total_tokens} tokens, ${total_cost:.4f} cost, {embedding_result.processing_time:.2f}s"
            )
            
            # Step 5: Update document status
            processing_time = time.time() - start_time
            document.processing_status = ProcessingStatus.COMPLETED
            document.processing_completed_at = timezone.now()
            document.chunks_count = embedding_result.total_chunks
            document.total_tokens = total_tokens
            document.total_cost_usd = total_cost
            document.save(update_fields=[
                'processing_status', 'processing_completed_at', 'chunks_count',
                'total_tokens', 'total_cost_usd'
            ])
            
            return {
                "document_id": str(document.id),
                "status": document.processing_status.value,
                "chunks_count": document.chunks_count,
                "total_tokens": document.total_tokens,
                "total_cost_usd": document.total_cost_usd,
                "processing_time": processing_time,
                "errors": embedding_result.errors
            }
            
    except Document.DoesNotExist:
        logger.error(f"Document {document_id} not found.")
        return {
            "document_id": document_id,
            "status": ProcessingStatus.FAILED.value,
            "error": f"Document {document_id} not found."
        }
    except Exception as exc:
        document = Document.objects.filter(id=document_id).first()
        if document:
            document.processing_status = ProcessingStatus.FAILED
            document.processing_completed_at = timezone.now()
            document.processing_error = str(exc)
            document.save(update_fields=['processing_status', 'processing_completed_at', 'processing_error'])
        logger.error(f"Document processing failed for {document_id}: {exc}", exc_info=True)
        raise


def generate_embeddings_batch(
    chunks: List[str],
    document_id: str,
    embedding_model: str = "text-embedding-ada-002",
    batch_size: int = 50
) -> List[Tuple[str, List[float], int, float]]:
    """
    Generate embeddings for text chunks in batches.
    
    Args:
        chunks: List of text chunks
        document_id: Parent document ID
        embedding_model: Model to use for embeddings
        batch_size: Number of chunks per batch
        
    Returns:
        List of (chunk_text, embedding, tokens, cost) tuples
    """
    try:
        from django_cfg.apps.knowbase.config.settings import get_openai_api_key, get_openrouter_api_key, get_cache_settings
        cache_settings = get_cache_settings()
        llm_service = LLMClient(
            apikey_openai=get_openai_api_key(),
            apikey_openrouter=get_openrouter_api_key(),
            cache_dir=cache_settings.cache_dir,
            cache_ttl=cache_settings.cache_ttl,
            max_cache_size=cache_settings.max_cache_size
        )
        results = []
        
        # Process in batches to avoid rate limits
        for i in range(0, len(chunks), batch_size):
            batch = chunks[i:i + batch_size]
            
            for chunk_text in batch:
                # Generate embedding (sync call for simplicity)
                embedding_response = llm_service.generate_embedding(chunk_text, embedding_model)
                
                # Extract embedding vector from response
                embedding_vector = embedding_response.embedding if embedding_response else []
                
                # Use tokens and cost from embedding response if available
                tokens = embedding_response.tokens if embedding_response else 0
                cost = embedding_response.cost if embedding_response else 0.0
                
                # Fallback to manual calculation if needed
                if tokens == 0:
                    tokens = llm_service.count_tokens(chunk_text, embedding_model)
                if cost == 0.0:
                    cost = llm_service.estimate_cost(embedding_model, tokens, 0)
                
                results.append((
                    chunk_text,
                    embedding_vector,
                    tokens,
                    cost
                ))
                
                # Small delay between requests to respect rate limits
                time.sleep(0.1)
            
            # Longer delay between batches
            if i + batch_size < len(chunks):
                time.sleep(1.0)
        
        logger.info(f"Generated {len(results)} embeddings for document {document_id}")
        return results
        
    except Exception as exc:
        logger.error(f"Batch embedding generation failed: {exc}")
        raise


@dramatiq.actor(
    queue_name="knowbase",
    max_retries=2,
    priority=7  # Higher priority for reprocessing
)
def reprocess_document_chunks(
    document_id: str,
    new_chunk_size: int = None,
    new_embedding_model: str = None
) -> Dict[str, Any]:
    """
    Reprocess existing document with new parameters.
    
    Args:
        document_id: Document to reprocess
        new_chunk_size: New chunk size (optional)
        new_embedding_model: New embedding model (optional)
        
    Returns:
        Reprocessing results
    """
    try:
        with transaction.atomic():
            document = Document.objects.get(id=document_id)
            
            # Delete existing chunks
            DocumentChunk.objects.filter(
                document=document
            ).delete()
            
            # Reset document status
            document.processing_status = ProcessingStatus.PENDING
            document.chunks_count = 0
            document.total_tokens = 0
            document.processing_error = ""
            document.save(update_fields=[
                'processing_status', 'processing_started_at', 'processing_completed_at',
                'processing_error', 'chunks_count', 'total_tokens', 'total_cost_usd'
            ])
            
            # Trigger reprocessing
            return process_document_async(
                document_id=document_id,
                chunk_size=new_chunk_size or 1000,
                embedding_model=new_embedding_model or "text-embedding-ada-002"
            )
            
    except Exception as exc:
        logger.error(f"Reprocessing failed for {document_id}: {exc}")
        raise


@dramatiq.actor(
    queue_name="knowbase",
    max_retries=2,
    priority=4
)
def optimize_document_embeddings(document_id: str) -> Dict[str, Any]:
    """
    Post-processing optimization for document embeddings.
    
    Args:
        document_id: Document to optimize
        
    Returns:
        Optimization results
    """
    try:
        # Update vector index statistics
        from django.db import connection
        
        with connection.cursor() as cursor:
            # Always analyze the table
            cursor.execute("ANALYZE django_cfg_knowbase_document_chunks;")
            
            # Check if index exists before trying to reindex
            cursor.execute("""
                SELECT EXISTS (
                    SELECT FROM pg_indexes 
                    WHERE indexname = 'embedding_cosine_idx'
                );
            """)
            index_exists = cursor.fetchone()[0]
            
            if index_exists:
                cursor.execute("REINDEX INDEX embedding_cosine_idx;")
                logger.debug("Reindexed embedding_cosine_idx")
            else:
                logger.warning("embedding_cosine_idx index does not exist, skipping reindex")
        
        logger.info(f"Optimized embeddings for document {document_id}")
        
        return {
            "status": "optimized",
            "document_id": document_id,
            "timestamp": timezone.now().isoformat()
        }
        
    except Exception as exc:
        logger.error(f"Embedding optimization failed for {document_id}: {exc}")
        raise
