"""
Utility functions for embedding processing.

This module provides convenient wrapper functions for common
embedding processing operations.
"""

import logging
from typing import List, Union

from django_cfg.apps.knowbase.models import DocumentChunk, ArchiveItemChunk, ExternalDataChunk

from .models import ChunkData, BatchProcessingResult, ChunkType
from .batch_processor import OptimizedEmbeddingProcessor
from .async_processor import AsyncOptimizedEmbeddingProcessor

logger = logging.getLogger(__name__)


def process_document_chunks_optimized(document_chunks: List[DocumentChunk]) -> BatchProcessingResult:
    """Process document chunks with optimized batch operations."""
    
    chunk_data = [
        ChunkData(
            id=str(chunk.id),
            content=chunk.content,
            parent_id=str(chunk.document_id),
            parent_type=ChunkType.DOCUMENT
        )
        for chunk in document_chunks
        if chunk.content and chunk.content.strip()
    ]
    
    processor = OptimizedEmbeddingProcessor()
    return processor.process_chunks_batch(chunk_data)


def process_archive_chunks_optimized(archive_chunks: List[ArchiveItemChunk]) -> BatchProcessingResult:
    """Process archive chunks with optimized batch operations."""
    
    chunk_data = [
        ChunkData(
            id=str(chunk.id),
            content=chunk.content,
            context_metadata=chunk.context_metadata,
            parent_id=str(chunk.item_id),
            parent_type=ChunkType.ARCHIVE
        )
        for chunk in archive_chunks
        if chunk.content and chunk.content.strip()
    ]
    
    processor = OptimizedEmbeddingProcessor()
    return processor.process_chunks_batch(chunk_data)


async def aprocess_document_chunks_optimized(document_chunks: List[DocumentChunk]) -> BatchProcessingResult:
    """Async version of document chunk processing."""
    
    chunk_data = [
        ChunkData(
            id=str(chunk.id),
            content=chunk.content,
            parent_id=str(chunk.document_id),
            parent_type=ChunkType.DOCUMENT
        )
        for chunk in document_chunks
        if chunk.content and chunk.content.strip()
    ]
    
    processor = AsyncOptimizedEmbeddingProcessor()
    return await processor.aprocess_chunks_batch(chunk_data)


async def aprocess_archive_chunks_optimized(archive_chunks: List[ArchiveItemChunk]) -> BatchProcessingResult:
    """Async version of archive chunk processing."""
    
    chunk_data = [
        ChunkData(
            id=str(chunk.id),
            content=chunk.content,
            context_metadata=chunk.context_metadata,
            parent_id=str(chunk.item_id),
            parent_type=ChunkType.ARCHIVE
        )
        for chunk in archive_chunks
        if chunk.content and chunk.content.strip()
    ]
    
    processor = AsyncOptimizedEmbeddingProcessor()
    return await processor.aprocess_chunks_batch(chunk_data)


def process_chunks_context_aware(chunks: Union[List[DocumentChunk], List[ArchiveItemChunk]]) -> BatchProcessingResult:
    """
    Context-aware chunk processing that works in both sync and async environments.
    
    This function automatically detects the execution context and uses appropriate methods.
    """
    if not chunks:
        return BatchProcessingResult(
            total_chunks=0,
            successful_chunks=0,
            failed_chunks=0,
            total_tokens=0,
            total_cost=0.0,
            processing_time=0.0,
            errors=[]
        )
    
    # Determine chunk type
    first_chunk = chunks[0]
    if isinstance(first_chunk, DocumentChunk):
        chunk_data = [
            ChunkData(
                id=str(chunk.id),
                content=chunk.content,
                parent_id=str(chunk.document_id),
                parent_type=ChunkType.DOCUMENT
            )
            for chunk in chunks
            if chunk.content and chunk.content.strip()
        ]
    elif isinstance(first_chunk, ArchiveItemChunk):
        chunk_data = [
            ChunkData(
                id=str(chunk.id),
                content=chunk.content,
                context_metadata=chunk.context_metadata,
                parent_id=str(chunk.item_id),
                parent_type=ChunkType.ARCHIVE
            )
            for chunk in chunks
            if chunk.content and chunk.content.strip()
        ]
    else:
        raise ValueError(f"Unsupported chunk type: {type(first_chunk)}")
    
    processor = AsyncOptimizedEmbeddingProcessor()
    return processor.process_chunks_batch_context_aware(chunk_data)


def process_external_data_chunks_optimized(external_data_chunks: List[ExternalDataChunk]) -> BatchProcessingResult:
    """Process external data chunks with optimized batch operations."""
    
    chunk_data = [
        ChunkData(
            id=str(chunk.id),
            content=chunk.content,
            context_metadata=chunk.chunk_metadata,
            parent_id=str(chunk.external_data.id),
            parent_type=ChunkType.EXTERNAL_DATA
        )
        for chunk in external_data_chunks
    ]
    
    processor = OptimizedEmbeddingProcessor()
    return processor.process_chunks_batch(chunk_data)


async def aprocess_external_data_chunks_optimized(external_data_chunks: List[ExternalDataChunk]) -> BatchProcessingResult:
    """Async version of external data chunk processing."""
    
    chunk_data = [
        ChunkData(
            id=str(chunk.id),
            content=chunk.content,
            context_metadata=chunk.chunk_metadata,
            parent_id=str(chunk.external_data.id),
            parent_type=ChunkType.EXTERNAL_DATA
        )
        for chunk in external_data_chunks
    ]
    
    processor = AsyncOptimizedEmbeddingProcessor()
    return await processor.aprocess_chunks_batch(chunk_data)
