"""
Embedding processing services.

This package provides high-performance embedding generation services
for documents and archives with batch processing and async support.
"""

from .async_processor import AsyncOptimizedEmbeddingProcessor
from .batch_processor import OptimizedEmbeddingProcessor
from .batch_result import BatchResultBuilder
from .models import BatchProcessingResult, ChunkData, ChunkType, EmbeddingResult, ProcessingConfig
from .processors import ArchiveChunkProcessor, DocumentChunkProcessor, ExternalDataChunkProcessor
from .utils import (
    process_archive_chunks_optimized,
    process_chunks_context_aware,
    process_document_chunks_optimized,
    process_external_data_chunks_optimized,
)

__all__ = [
    # Data models
    "ChunkData",
    "EmbeddingResult",
    "BatchProcessingResult",
    "ProcessingConfig",
    "ChunkType",

    # Processors
    "DocumentChunkProcessor",
    "ArchiveChunkProcessor",
    "ExternalDataChunkProcessor",
    "OptimizedEmbeddingProcessor",
    "AsyncOptimizedEmbeddingProcessor",

    # Utilities
    "BatchResultBuilder",

    # Convenience functions
    "process_document_chunks_optimized",
    "process_archive_chunks_optimized",
    "process_external_data_chunks_optimized",
    "process_chunks_context_aware",
]
