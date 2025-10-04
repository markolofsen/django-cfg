"""
Dynamic chunk settings using Pydantic configuration.

This module provides utilities for accessing and managing chunk processing
settings with type safety and validation.
"""

import logging
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field, validator
from ..config.constance_settings import ConstanceSettings

logger = logging.getLogger(__name__)


class ChunkSettings(BaseModel):
    """Pydantic model for chunk processing settings."""
    
    chunk_size: int = Field(
        ge=100,
        le=8000,
        description="Size of each chunk in characters"
    )
    
    chunk_overlap: int = Field(
        ge=0,
        description="Overlap between chunks in characters"
    )
    
    embedding_batch_size: int = Field(
        ge=1,
        le=100,
        description="Number of chunks to process in one embedding batch"
    )
    
    embedding_model: str = Field(
        min_length=1,
        description="OpenAI embedding model name"
    )
    
    @validator('chunk_overlap')
    def validate_overlap(cls, v, values):
        """Ensure overlap is less than chunk_size."""
        chunk_size = values.get('chunk_size')
        if chunk_size and v >= chunk_size:
            raise ValueError(f"Chunk overlap ({v}) must be less than chunk size ({chunk_size})")
        return v
    
    class Config:
        """Pydantic configuration."""
        validate_assignment = True


class ChunkSettingsManager:
    """Manager for dynamic chunk settings using Pydantic configuration."""
    
    @classmethod
    def get_document_settings(cls) -> ChunkSettings:
        """Get chunk settings for document processing."""
        from ..config.settings import get_config
        config = get_config()
        return ChunkSettings(
            chunk_size=ConstanceSettings.get_document_chunk_size(),
            chunk_overlap=config.chunking.document_chunk_overlap,
            embedding_batch_size=ConstanceSettings.get_embedding_batch_size(),
            embedding_model=ConstanceSettings.get_embedding_model()
        )
    
    @classmethod
    def get_archive_settings(cls) -> ChunkSettings:
        """Get chunk settings for archive processing."""
        from ..config.settings import get_config
        config = get_config()
        return ChunkSettings(
            chunk_size=ConstanceSettings.get_archive_chunk_size(),
            chunk_overlap=config.chunking.archive_chunk_overlap,
            embedding_batch_size=ConstanceSettings.get_embedding_batch_size(),
            embedding_model=ConstanceSettings.get_embedding_model()
        )
    
    @classmethod
    def get_settings_for_type(cls, content_type: str) -> ChunkSettings:
        """
        Get chunk settings for specific content type.
        
        Args:
            content_type: Either 'document' or 'archive'
            
        Returns:
            ChunkSettings object with appropriate settings
        """
        if content_type == 'document':
            return cls.get_document_settings()
        elif content_type == 'archive':
            return cls.get_archive_settings()
        else:
            logger.warning(f"Unknown content type: {content_type}, using document settings")
            return cls.get_document_settings()
    
    @classmethod
    def get_all_settings(cls) -> Dict[str, ChunkSettings]:
        """Get all chunk settings as dictionary."""
        return {
            'document': cls.get_document_settings(),
            'archive': cls.get_archive_settings()
        }
    
    @classmethod
    def validate_settings(cls, settings: ChunkSettings) -> bool:
        """
        Validate chunk settings.
        
        Args:
            settings: ChunkSettings to validate
            
        Returns:
            True if settings are valid, False otherwise
        """
        if settings.chunk_size <= 0:
            logger.error(f"Invalid chunk_size: {settings.chunk_size}")
            return False
        
        if settings.chunk_overlap < 0:
            logger.error(f"Invalid chunk_overlap: {settings.chunk_overlap}")
            return False
        
        if settings.chunk_overlap >= settings.chunk_size:
            logger.error(f"Chunk overlap ({settings.chunk_overlap}) must be less than chunk size ({settings.chunk_size})")
            return False
        
        if settings.embedding_batch_size <= 0 or settings.embedding_batch_size > 2048:
            logger.error(f"Invalid embedding_batch_size: {settings.embedding_batch_size} (must be 1-2048)")
            return False
        
        if not settings.embedding_model or not settings.embedding_model.strip():
            logger.error("Embedding model cannot be empty")
            return False
        
        return True
    
    @classmethod
    def log_current_settings(cls) -> None:
        """Log current settings for debugging."""
        try:
            doc_settings = cls.get_document_settings()
            archive_settings = cls.get_archive_settings()
            
            logger.info("📊 Current Chunk Settings:")
            logger.info(f"  📄 Documents: size={doc_settings.chunk_size}, overlap={doc_settings.chunk_overlap}")
            logger.info(f"  📦 Archives: size={archive_settings.chunk_size}, overlap={archive_settings.chunk_overlap}")
            logger.info(f"  🔮 Embedding: batch_size={doc_settings.embedding_batch_size}, model={doc_settings.embedding_model}")
            
        except Exception as e:
            logger.error(f"Failed to log current settings: {e}")


# Convenience functions for easy access (using new Pydantic config)
def get_document_chunk_size() -> int:
    """Get document chunk size."""
    from ..config.settings import get_document_chunk_size
    return get_document_chunk_size()


def get_document_chunk_overlap() -> int:
    """Get document chunk overlap."""
    from ..config.settings import get_document_chunk_overlap
    return get_document_chunk_overlap()


def get_archive_chunk_size() -> int:
    """Get archive chunk size."""
    from ..config.settings import get_archive_chunk_size
    return get_archive_chunk_size()


def get_archive_chunk_overlap() -> int:
    """Get archive chunk overlap."""
    from ..config.settings import get_archive_chunk_overlap
    return get_archive_chunk_overlap()


def get_embedding_batch_size() -> int:
    """Get embedding batch size."""
    from ..config.settings import get_embedding_batch_size
    return get_embedding_batch_size()


def get_embedding_model() -> str:
    """Get embedding model."""
    from ..config.settings import get_embedding_model
    return get_embedding_model()


# Additional convenience functions using new Pydantic config
def get_search_results_limit() -> int:
    """Get search results limit."""
    from ..config.settings import get_search_results_limit
    return get_search_results_limit()


def get_search_similarity_threshold() -> float:
    """Get search similarity threshold."""
    from ..config.settings import get_search_similarity_threshold
    return get_search_similarity_threshold()


def get_chat_context_chunks() -> int:
    """Get number of chunks for chat context."""
    from ..config.settings import get_chat_context_chunks
    return get_chat_context_chunks()


def get_chat_max_tokens() -> int:
    """Get maximum tokens for chat completion."""
    from ..config.settings import get_chat_max_tokens
    return get_chat_max_tokens()


def get_chat_temperature() -> float:
    """Get chat completion temperature."""
    from ..config.settings import get_chat_temperature
    return get_chat_temperature()


def get_max_archive_size_mb() -> int:
    """Get maximum archive size in MB."""
    from ..config.settings import get_max_archive_size_mb
    return get_max_archive_size_mb()


def get_max_document_size_mb() -> int:
    """Get maximum document size in MB."""
    from ..config.settings import get_max_document_size_mb
    return get_max_document_size_mb()


def get_processing_timeout_minutes() -> int:
    """Get processing timeout in minutes."""
    from ..config.settings import get_processing_timeout_minutes
    return get_processing_timeout_minutes()


def get_chunking_params_for_type(content_type: str) -> Dict[str, Any]:
    """
    Get chunking parameters for SemanticChunker.
    
    Args:
        content_type: Either 'document' or 'archive'
        
    Returns:
        Dictionary with chunk_size and overlap parameters
    """
    from ..config.settings import get_chunking_params_for_type
    return get_chunking_params_for_type(content_type)


# Initialize settings logging on module import
try:
    ChunkSettingsManager.log_current_settings()
except Exception as e:
    logger.debug(f"Could not log settings on import: {e}")
