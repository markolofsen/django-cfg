"""
Pydantic-based configuration for Knowledge Base app.

This module provides a clean, type-safe configuration system that replaces
the removed Constance settings with sensible defaults and validation.
"""

from typing import Dict, Any, Optional
from pydantic import BaseModel, Field, field_validator
from pathlib import Path
import os

# Import environment configuration for API keys
try:
    from django.conf import settings
except ImportError:
    # Fallback for tests or when environment is not available
    env = None


class CacheSettings(BaseModel):
    """Cache settings for LLMClient."""
    
    cache_dir: Path = Field(..., description="Cache directory path")
    cache_ttl: int = Field(..., description="Cache TTL in seconds")
    max_cache_size: int = Field(..., description="Maximum cache size")
    
    class Config:
        arbitrary_types_allowed = True  # Allow Path type


class EmbeddingConfig(BaseModel):
    """Configuration for embedding processing."""
    
    model: str = Field(
        default="text-embedding-ada-002",
        description="OpenAI embedding model to use"
    )
    batch_size: int = Field(
        default=50,
        ge=1,
        le=100,
        description="Number of chunks to process in one batch"
    )
    max_retries: int = Field(
        default=3,
        ge=0,
        le=10,
        description="Maximum number of retries for failed embeddings"
    )
    timeout_seconds: int = Field(
        default=30,
        ge=5,
        le=300,
        description="Timeout for embedding API calls"
    )
    cache_dir: str = Field(
        default=".cache/django_cfg_knowbase_llm",
        description="Directory for LLM cache files (relative to project root)"
    )
    cache_ttl: int = Field(
        default=3600,
        ge=60,
        le=86400,
        description="Cache TTL in seconds (1 hour to 24 hours)"
    )
    cache_max_size: int = Field(
        default=1000,
        ge=10,
        le=10000,
        description="Maximum number of items in memory cache"
    )
    
    # API Keys from environment
    @property
    def openai_api_key(self) -> Optional[str]:
        """Get OpenAI API key from environment configuration."""
        try:
            return settings.api_keys.openai
        except AttributeError:
            return os.getenv("OPENAI_API_KEY")
    
    @property
    def openrouter_api_key(self) -> Optional[str]:
        """Get OpenRouter API key from environment configuration."""
        try:
            return settings.api_keys.openrouter
        except AttributeError:
            return os.getenv("OPENROUTER_API_KEY")


class ChunkingConfig(BaseModel):
    """Configuration for text chunking."""
    
    document_chunk_size: int = Field(
        default=1000,
        ge=100,
        le=8000,
        description="Chunk size for document processing (characters)"
    )
    document_chunk_overlap: int = Field(
        default=200,
        ge=0,
        le=1000,
        description="Overlap between document chunks (characters)"
    )
    archive_chunk_size: int = Field(
        default=800,
        ge=100,
        le=8000,
        description="Chunk size for archive processing (characters)"
    )
    archive_chunk_overlap: int = Field(
        default=160,
        ge=0,
        le=1000,
        description="Overlap between archive chunks (characters)"
    )
    
    @field_validator('document_chunk_overlap')
    @classmethod
    def validate_document_overlap(cls, v, info):
        if info.data and 'document_chunk_size' in info.data and v >= info.data['document_chunk_size']:
            raise ValueError('Document chunk overlap must be less than chunk size')
        return v
    
    @field_validator('archive_chunk_overlap')
    @classmethod
    def validate_archive_overlap(cls, v, info):
        if info.data and 'archive_chunk_size' in info.data and v >= info.data['archive_chunk_size']:
            raise ValueError('Archive chunk overlap must be less than chunk size')
        return v


class SearchConfig(BaseModel):
    """Configuration for search functionality."""
    
    results_limit: int = Field(
        default=10,
        ge=1,
        le=100,
        description="Maximum number of search results to return"
    )
    
    # Type-specific similarity thresholds for better multilingual and content-type support
    document_threshold: float = Field(
        default=0.7,
        ge=0.0,
        le=1.0,
        description="Similarity threshold for document chunks (high precision)"
    )
    archive_threshold: float = Field(
        default=0.6,
        ge=0.0,
        le=1.0,
        description="Similarity threshold for archive chunks (medium precision for code)"
    )
    # Note: external_data_threshold removed - now configured per-object in ExternalData.similarity_threshold
    
    # Legacy field for backward compatibility
    similarity_threshold: float = Field(
        default=0.7,
        ge=0.0,
        le=1.0,
        description="Default similarity threshold (legacy, use type-specific thresholds)"
    )


class ChatConfig(BaseModel):
    """Configuration for chat functionality."""
    
    context_chunks: int = Field(
        default=5,
        ge=1,
        le=20,
        description="Number of chunks to include in chat context"
    )
    max_tokens: int = Field(
        default=4000,
        ge=100,
        le=32000,
        description="Maximum tokens for chat completion"
    )
    temperature: float = Field(
        default=0.7,
        ge=0.0,
        le=2.0,
        description="Temperature for chat completion (creativity level)"
    )


class ProcessingConfig(BaseModel):
    """Configuration for processing limits and timeouts."""
    
    max_document_size_mb: int = Field(
        default=10,
        ge=1,
        le=100,
        description="Maximum document size in MB"
    )
    max_archive_size_mb: int = Field(
        default=50,
        ge=1,
        le=500,
        description="Maximum archive size in MB"
    )
    timeout_minutes: int = Field(
        default=30,
        ge=1,
        le=180,
        description="Processing timeout in minutes"
    )


class KnowledgeBaseConfig(BaseModel):
    """Main configuration for the Knowledge Base app."""
    
    embedding: EmbeddingConfig = Field(default_factory=EmbeddingConfig)
    chunking: ChunkingConfig = Field(default_factory=ChunkingConfig)
    search: SearchConfig = Field(default_factory=SearchConfig)
    chat: ChatConfig = Field(default_factory=ChatConfig)
    processing: ProcessingConfig = Field(default_factory=ProcessingConfig)
    
    class Config:
        env_prefix = "KNOWBASE_"
        case_sensitive = False
        
    def get_chunking_params_for_type(self, content_type: str) -> Dict[str, Any]:
        """
        Get chunking parameters for SemanticChunker.
        
        Args:
            content_type: Either 'document' or 'archive'
            
        Returns:
            Dictionary with chunk_size and overlap parameters
        """
        if content_type == 'archive':
            return {
                'chunk_size': self.chunking.archive_chunk_size,
                'overlap': self.chunking.archive_chunk_overlap
            }
        else:  # default to document
            return {
                'chunk_size': self.chunking.document_chunk_size,
                'overlap': self.chunking.document_chunk_overlap
            }
    
    def get_embedding_model(self) -> str:
        """Get the configured embedding model."""
        return self.embedding.model
    
    def get_embedding_batch_size(self) -> int:
        """Get the configured embedding batch size."""
        return self.embedding.batch_size
    
    def get_openai_api_key(self) -> Optional[str]:
        """Get OpenAI API key from environment."""
        return self.embedding.openai_api_key
    
    def get_openrouter_api_key(self) -> Optional[str]:
        """Get OpenRouter API key from environment."""
        return self.embedding.openrouter_api_key
    
    def get_cache_dir(self) -> Path:
        """Get cache directory path and ensure it exists."""
        from pathlib import Path
        cache_path = Path(self.embedding.cache_dir)
        if not cache_path.is_absolute():
            cache_path = Path.cwd() / cache_path
        
        # Ensure cache directory exists
        cache_path.mkdir(parents=True, exist_ok=True)
        return cache_path
    
    def get_cache_settings(self) -> CacheSettings:
        """Get cache settings for LLMClient."""
        return CacheSettings(
            cache_dir=self.get_cache_dir(),
            cache_ttl=self.embedding.cache_ttl,
            max_cache_size=self.embedding.cache_max_size
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert config to dictionary for easy access."""
        return self.dict()


# Global configuration instance
_config: Optional[KnowledgeBaseConfig] = None


def get_config() -> KnowledgeBaseConfig:
    """
    Get the global configuration instance.
    
    This function implements a singleton pattern to ensure we only
    create one configuration instance per application run.
    """
    global _config
    if _config is None:
        _config = KnowledgeBaseConfig()
    return _config


def reload_config() -> KnowledgeBaseConfig:
    """
    Reload configuration from environment variables.
    
    Useful for testing or when configuration needs to be updated.
    """
    global _config
    _config = KnowledgeBaseConfig()
    return _config


# Convenience functions for easy access (backward compatibility)
def get_document_chunk_size() -> int:
    """Get document chunk size."""
    return get_config().chunking.document_chunk_size


def get_document_chunk_overlap() -> int:
    """Get document chunk overlap."""
    return get_config().chunking.document_chunk_overlap


def get_archive_chunk_size() -> int:
    """Get archive chunk size."""
    return get_config().chunking.archive_chunk_size


def get_archive_chunk_overlap() -> int:
    """Get archive chunk overlap."""
    return get_config().chunking.archive_chunk_overlap


def get_embedding_batch_size() -> int:
    """Get embedding batch size."""
    return get_config().embedding.batch_size


def get_embedding_model() -> str:
    """Get embedding model."""
    return get_config().embedding.model


def get_search_results_limit() -> int:
    """Get search results limit."""
    return get_config().search.results_limit


def get_search_similarity_threshold() -> float:
    """Get search similarity threshold (legacy)."""
    return get_config().search.similarity_threshold


def get_document_threshold() -> float:
    """Get similarity threshold for document chunks."""
    return get_config().search.document_threshold


def get_archive_threshold() -> float:
    """Get similarity threshold for archive chunks."""
    return get_config().search.archive_threshold


# Note: get_external_data_threshold removed - now configured per-object in ExternalData.similarity_threshold


def get_threshold_for_type(content_type: str) -> float:
    """
    Get appropriate similarity threshold for content type.
    
    Args:
        content_type: 'document', 'archive', or 'external_data'
        
    Returns:
        Appropriate similarity threshold for the content type
    """
    config = get_config()
    thresholds = {
        'document': config.search.document_threshold,
        'archive': config.search.archive_threshold,
        # Note: external_data now uses per-object thresholds from ExternalData.similarity_threshold
    }
    return thresholds.get(content_type, config.search.similarity_threshold)


def get_chat_context_chunks() -> int:
    """Get number of chunks for chat context."""
    return get_config().chat.context_chunks


def get_chat_max_tokens() -> int:
    """Get maximum tokens for chat completion."""
    return get_config().chat.max_tokens


def get_chat_temperature() -> float:
    """Get chat completion temperature."""
    return get_config().chat.temperature


def get_max_archive_size_mb() -> int:
    """Get maximum archive size in MB."""
    return get_config().processing.max_archive_size_mb


def get_max_document_size_mb() -> int:
    """Get maximum document size in MB."""
    return get_config().processing.max_document_size_mb


def get_processing_timeout_minutes() -> int:
    """Get processing timeout in minutes."""
    return get_config().processing.timeout_minutes


def get_chunking_params_for_type(content_type: str) -> Dict[str, Any]:
    """
    Get chunking parameters for SemanticChunker.
    
    Args:
        content_type: Either 'document' or 'archive'
        
    Returns:
        Dictionary with chunk_size and overlap parameters
    """
    return get_config().get_chunking_params_for_type(content_type)


def get_openai_api_key() -> Optional[str]:
    """Get OpenAI API key from environment."""
    return get_config().get_openai_api_key()


def get_openrouter_api_key() -> Optional[str]:
    """Get OpenRouter API key from environment."""
    return get_config().get_openrouter_api_key()


def get_cache_dir():
    """Get cache directory path."""
    return get_config().get_cache_dir()


def get_cache_settings() -> CacheSettings:
    """Get cache settings for LLMClient."""
    return get_config().get_cache_settings()
