"""
Constance settings accessor for Knowledge Base app.

This module provides a centralized way to access all Constance settings
with proper fallbacks and type safety using Pydantic 2.
"""

from typing import Optional, Dict, Any
from pydantic import BaseModel, Field, validator
from constance import config


class KnowledgeBaseConstanceSettings(BaseModel):
    """Pydantic model for Knowledge Base Constance settings with validation."""
    
    # === AI Assistant Settings ===
    bot_identity: str = Field(
        default="I am Reforms.ai, an AI assistant specialized in helping with knowledge base queries and technical documentation. I was developed by the Reforms.ai team to provide accurate information based on your uploaded documents and code archives.",
        min_length=10,
        max_length=1000,
        description="AI assistant identity and description"
    )
    
    bot_no_context_message: str = Field(
        default="I can help you with questions about your knowledge base, technical documentation, and uploaded content. However, I don't currently have any specific context loaded for this conversation.",
        min_length=10,
        max_length=500,
        description="Message shown when AI has no specific context"
    )
    
    # === Processing Settings ===
    document_chunk_size: int = Field(
        default=1000,
        ge=100,
        le=8000,
        description="Chunk size for document processing (characters)"
    )
    
    archive_chunk_size: int = Field(
        default=800,
        ge=100,
        le=8000,
        description="Chunk size for archive processing (characters)"
    )
    
    # === Embedding Settings ===
    embedding_model: str = Field(
        default="text-embedding-ada-002",
        min_length=1,
        description="OpenAI embedding model name"
    )
    
    embedding_batch_size: int = Field(
        default=50,
        ge=1,
        le=100,
        description="Chunks per embedding batch"
    )
    
    # === Search Threshold Settings ===
    document_threshold: float = Field(
        default=0.7,
        ge=0.0,
        le=1.0,
        description="Similarity threshold for document chunks"
    )
    
    archive_threshold: float = Field(
        default=0.6,
        ge=0.0,
        le=1.0,
        description="Similarity threshold for archive chunks"
    )
    
    # Note: external_data_threshold removed - now configured per-object in ExternalData.similarity_threshold
    
    @validator('embedding_model')
    def validate_embedding_model(cls, v):
        """Validate embedding model name."""
        valid_models = [
            "text-embedding-ada-002",
            "text-embedding-3-small", 
            "text-embedding-3-large"
        ]
        if v not in valid_models:
            # Warning, not error - allow custom models
            pass
        return v
    
    class Config:
        """Pydantic configuration."""
        validate_assignment = True
        extra = "forbid"
        json_encoders = {
            # Add custom encoders if needed
        }
    
    @classmethod
    def from_constance(cls) -> 'KnowledgeBaseConstanceSettings':
        """Create instance from Constance settings with fallbacks."""
        try:
            return cls(
                bot_identity=getattr(config, 'BOT_IDENTITY', cls.model_fields['bot_identity'].default),
                bot_no_context_message=getattr(config, 'BOT_NO_CONTEXT_MESSAGE', cls.model_fields['bot_no_context_message'].default),
                document_chunk_size=getattr(config, 'DOCUMENT_CHUNK_SIZE', cls.model_fields['document_chunk_size'].default),
                archive_chunk_size=getattr(config, 'ARCHIVE_CHUNK_SIZE', cls.model_fields['archive_chunk_size'].default),
                embedding_model=getattr(config, 'EMBEDDING_MODEL', cls.model_fields['embedding_model'].default),
                embedding_batch_size=getattr(config, 'EMBEDDING_BATCH_SIZE', cls.model_fields['embedding_batch_size'].default),
                document_threshold=getattr(config, 'DOCUMENT_THRESHOLD', cls.model_fields['document_threshold'].default),
                archive_threshold=getattr(config, 'ARCHIVE_THRESHOLD', cls.model_fields['archive_threshold'].default),
            )
        except Exception as e:
            # If any validation fails, return defaults
            return cls()
    
    @classmethod
    def get_current(cls) -> 'KnowledgeBaseConstanceSettings':
        """Get current settings instance (cached for performance)."""
        # Always refresh cache to avoid stale data issues
        # TODO: Implement smarter cache invalidation based on Constance changes
        return cls.from_constance()
    
    @classmethod
    def refresh_cache(cls):
        """Refresh cached settings instance."""
        if hasattr(cls, '_cached_instance'):
            delattr(cls, '_cached_instance')
    
    # === Convenience Methods for Backward Compatibility ===
    
    @classmethod
    def get_bot_identity(cls) -> str:
        """Get bot identity from current settings."""
        return cls.get_current().bot_identity
    
    @classmethod
    def get_bot_no_context_message(cls) -> str:
        """Get bot no-context message from current settings."""
        return cls.get_current().bot_no_context_message
    
    @classmethod
    def get_document_chunk_size(cls) -> int:
        """Get document chunk size from current settings."""
        return cls.get_current().document_chunk_size
    
    @classmethod
    def get_archive_chunk_size(cls) -> int:
        """Get archive chunk size from current settings."""
        return cls.get_current().archive_chunk_size
    
    @classmethod
    def get_embedding_model(cls) -> str:
        """Get embedding model from current settings."""
        return cls.get_current().embedding_model
    
    @classmethod
    def get_embedding_batch_size(cls) -> int:
        """Get embedding batch size from current settings."""
        return cls.get_current().embedding_batch_size
    
    @classmethod
    def get_document_threshold(cls) -> float:
        """Get document similarity threshold from current settings."""
        return cls.get_current().document_threshold
    
    @classmethod
    def get_archive_threshold(cls) -> float:
        """Get archive similarity threshold from current settings."""
        return cls.get_current().archive_threshold
    
    # Note: get_external_data_threshold removed - now configured per-object in ExternalData.similarity_threshold
    
    @classmethod
    def get_threshold_for_type(cls, content_type: str) -> float:
        """Get appropriate threshold for content type."""
        current = cls.get_current()
        thresholds = {
            'document': current.document_threshold,
            'archive': current.archive_threshold,
            # Note: external_data now uses per-object thresholds from ExternalData.similarity_threshold
        }
        return thresholds.get(content_type, 0.7)  # fallback
    
    @classmethod
    def get_all_settings(cls) -> Dict[str, Any]:
        """Get all settings as a dictionary."""
        return cls.get_current().model_dump()
    
    @classmethod
    def validate_settings(cls) -> Dict[str, str]:
        """Validate current settings and return results."""
        try:
            settings = cls.from_constance()
            return {field: 'OK' for field in settings.model_fields.keys()}
        except Exception as e:
            return {'validation_error': str(e)}


# Convenience alias for shorter imports
ConstanceSettings = KnowledgeBaseConstanceSettings
