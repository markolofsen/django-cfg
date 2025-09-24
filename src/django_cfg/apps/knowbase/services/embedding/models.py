"""
Data models for embedding processing.

This module defines the core data structures used throughout
the embedding processing pipeline using Pydantic for type safety.
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field, validator
from enum import Enum


class ChunkType(str, Enum):
    """Supported chunk types."""
    DOCUMENT = "document"
    ARCHIVE = "archive"
    EXTERNAL_DATA = "external_data"
    UNKNOWN = "unknown"


class ChunkData(BaseModel):
    """Unified chunk data structure for processing."""
    id: str = Field(..., description="Unique chunk identifier")
    content: str = Field(..., min_length=1, description="Chunk content text")
    context_metadata: Optional[Dict[str, Any]] = Field(
        default=None, 
        description="Additional context metadata for the chunk"
    )
    parent_id: Optional[str] = Field(
        default=None, 
        description="ID of the parent document or archive"
    )
    parent_type: ChunkType = Field(
        default=ChunkType.UNKNOWN, 
        description="Type of parent content"
    )
    
    @validator('content')
    def content_must_not_be_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('Content cannot be empty')
        return v.strip()
    
    class Config:
        use_enum_values = True


class EmbeddingResult(BaseModel):
    """Result of embedding generation."""
    chunk_id: str = Field(..., description="ID of the processed chunk")
    embedding: List[float] = Field(
        default_factory=list, 
        description="Generated embedding vector"
    )
    tokens: int = Field(
        default=0, 
        ge=0, 
        description="Number of tokens used"
    )
    cost: float = Field(
        default=0.0, 
        ge=0.0, 
        description="Processing cost in USD"
    )
    success: bool = Field(
        default=True, 
        description="Whether embedding generation was successful"
    )
    error: Optional[str] = Field(
        default=None, 
        description="Error message if processing failed"
    )
    processing_time: Optional[float] = Field(
        default=None, 
        ge=0.0, 
        description="Time taken to process this chunk in seconds"
    )
    
    @validator('embedding')
    def validate_embedding_dimension(cls, v):
        if v is not None and len(v) > 0 and len(v) not in [1536, 3072]:  # Common OpenAI embedding dimensions
            # Warning, not error - allow different dimensions
            pass
        return v
    
    class Config:
        validate_assignment = True


class BatchProcessingResult(BaseModel):
    """Result of batch processing."""
    total_chunks: int = Field(
        ..., 
        ge=0, 
        description="Total number of chunks processed"
    )
    successful_chunks: int = Field(
        ..., 
        ge=0, 
        description="Number of successfully processed chunks"
    )
    failed_chunks: int = Field(
        ..., 
        ge=0, 
        description="Number of failed chunks"
    )
    total_tokens: int = Field(
        default=0, 
        ge=0, 
        description="Total tokens used across all chunks"
    )
    total_cost: float = Field(
        default=0.0, 
        ge=0.0, 
        description="Total processing cost in USD"
    )
    processing_time: float = Field(
        ..., 
        ge=0.0, 
        description="Total processing time in seconds"
    )
    errors: List[str] = Field(
        default_factory=list, 
        description="List of error messages"
    )
    
    # Computed properties
    @property
    def success_rate(self) -> float:
        """Calculate success rate as percentage."""
        if self.total_chunks == 0:
            return 0.0
        return (self.successful_chunks / self.total_chunks) * 100.0
    
    @property
    def chunks_per_second(self) -> float:
        """Calculate processing speed."""
        if self.processing_time == 0:
            return 0.0
        return self.total_chunks / self.processing_time
    
    @property
    def average_cost_per_chunk(self) -> float:
        """Calculate average cost per successfully processed chunk."""
        if self.successful_chunks == 0:
            return 0.0
        return self.total_cost / self.successful_chunks
    
    @property
    def average_tokens_per_chunk(self) -> float:
        """Calculate average tokens per successfully processed chunk."""
        if self.successful_chunks == 0:
            return 0.0
        return self.total_tokens / self.successful_chunks
    
    @validator('successful_chunks', 'failed_chunks')
    def validate_chunk_counts(cls, v, values):
        if 'total_chunks' in values:
            total = values['total_chunks']
            if v > total:
                raise ValueError(f'Chunk count cannot exceed total chunks ({total})')
        return v
    
    @validator('failed_chunks')
    def validate_total_consistency(cls, v, values):
        if 'total_chunks' in values and 'successful_chunks' in values:
            expected_failed = values['total_chunks'] - values['successful_chunks']
            if v != expected_failed:
                raise ValueError(
                    f'Failed chunks ({v}) + successful chunks ({values["successful_chunks"]}) '
                    f'must equal total chunks ({values["total_chunks"]})'
                )
        return v
    
    class Config:
        validate_assignment = True
        
    def model_dump_summary(self) -> Dict[str, Any]:
        """Get a summary dict for logging."""
        return {
            "total_chunks": self.total_chunks,
            "successful": self.successful_chunks,
            "failed": self.failed_chunks,
            "success_rate": f"{self.success_rate:.1f}%",
            "total_tokens": self.total_tokens,
            "total_cost": f"${self.total_cost:.4f}",
            "processing_time": f"{self.processing_time:.2f}s",
            "chunks_per_second": f"{self.chunks_per_second:.1f}",
            "avg_cost_per_chunk": f"${self.average_cost_per_chunk:.4f}",
            "error_count": len(self.errors)
        }


class ProcessingConfig(BaseModel):
    """Configuration for embedding processing."""
    batch_size: int = Field(
        default=100, 
        ge=1, 
        le=2048, 
        description="Number of chunks to process in one batch"
    )
    embedding_model: str = Field(
        default="text-embedding-ada-002",
        description="OpenAI embedding model to use"
    )
    max_retries: int = Field(
        default=3, 
        ge=0, 
        le=10, 
        description="Maximum number of retries for failed requests"
    )
    retry_delay: float = Field(
        default=1.0, 
        ge=0.0, 
        description="Delay between retries in seconds"
    )
    rate_limit_delay: float = Field(
        default=0.5, 
        ge=0.0, 
        description="Delay between batches to respect rate limits"
    )
    timeout_seconds: int = Field(
        default=60, 
        ge=1, 
        description="Timeout for API requests in seconds"
    )
    
    class Config:
        validate_assignment = True
