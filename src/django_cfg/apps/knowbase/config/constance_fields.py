"""
Constance fields configuration for Knowledge Base app.

This module defines all dynamic settings for the knowledge base system
that can be configured through Django admin at runtime.

Note: Default values are now sourced from the Pydantic configuration
to ensure consistency across the application.
"""

from typing import List
from django_cfg.models.constance import ConstanceField
from .settings import KnowledgeBaseConfig, get_openai_api_key, get_openrouter_api_key


def get_django_cfg_knowbase_constance_fields() -> List[ConstanceField]:
    """
    Get essential Constance fields for Knowledge Base app.
    
    Default values are automatically pulled from the Pydantic configuration
    to ensure consistency.
    
    Returns:
        List of ConstanceField objects for critical knowledge base settings
    """
    # Get default values from Pydantic config
    default_config = KnowledgeBaseConfig()
    
    return [
        # === Core Processing Settings ===
        ConstanceField(
            name="DOCUMENT_CHUNK_SIZE",
            default=default_config.chunking.document_chunk_size,
            help_text=f"Chunk size for document processing (characters). Default: {default_config.chunking.document_chunk_size}. Affects context quality vs memory usage.",
            field_type="int",
            group="Knowledge Base",
        ),
        ConstanceField(
            name="ARCHIVE_CHUNK_SIZE",
            default=default_config.chunking.archive_chunk_size,
            help_text=f"Chunk size for archive processing (characters). Default: {default_config.chunking.archive_chunk_size}. Smaller for code files.",
            field_type="int",
            group="Knowledge Base",
        ),
        
        # === Embedding Settings ===
        ConstanceField(
            name="EMBEDDING_MODEL",
            default=default_config.embedding.model,
            help_text=f"OpenAI embedding model. Default: {default_config.embedding.model}. Options: text-embedding-ada-002, text-embedding-3-small, text-embedding-3-large. API Key: {'✅ Available' if get_openai_api_key() else '❌ Missing'}",
            field_type="str",
            group="Knowledge Base",
        ),
        ConstanceField(
            name="EMBEDDING_BATCH_SIZE",
            default=default_config.embedding.batch_size,
            help_text=f"Chunks per embedding batch (1-100). Default: {default_config.embedding.batch_size}. Higher = faster but more memory. OpenRouter Key: {'✅ Available' if get_openrouter_api_key() else '❌ Missing'}",
            field_type="int",
            group="Knowledge Base",
        ),
        
        # === Search Threshold Settings ===
        ConstanceField(
            name="DOCUMENT_THRESHOLD",
            default=default_config.search.document_threshold,
            help_text=f"Similarity threshold for document chunks (0.0-1.0). Default: {default_config.search.document_threshold}. Higher = more precise, lower = more results.",
            field_type="float",
            group="Knowledge Base",
        ),
        ConstanceField(
            name="ARCHIVE_THRESHOLD", 
            default=default_config.search.archive_threshold,
            help_text=f"Similarity threshold for archive/code chunks (0.0-1.0). Default: {default_config.search.archive_threshold}. Medium precision for code similarity.",
            field_type="float",
            group="Knowledge Base",
        ),
        # Note: EXTERNAL_DATA_THRESHOLD removed - now configured per-object in ExternalData.similarity_threshold
        
        # === AI Assistant Settings ===
        ConstanceField(
            name="BOT_IDENTITY",
            default="I am Reforms.ai, an AI assistant specialized in helping with knowledge base queries and technical documentation. I was developed by the Reforms.ai team to provide accurate information based on your uploaded documents and code archives.",
            help_text="AI assistant identity and description. This text defines who the bot is and what it does. Used in system prompts for all conversations.",
            field_type="longtext",
            group="Knowledge Base",
        ),
        ConstanceField(
            name="BOT_NO_CONTEXT_MESSAGE",
            default="I can help you with questions about your knowledge base, technical documentation, and uploaded content. However, I don't currently have any specific context loaded for this conversation.",
            help_text="Message shown when AI assistant has no specific context loaded. Explains what the bot can help with when no documents are found.",
            field_type="longtext",
            group="Knowledge Base",
        ),
    ]


def get_django_cfg_knowbase_field_validation_rules() -> dict:
    """
    Get validation rules for essential knowledge base Constance fields.
    
    Validation rules are now consistent with Pydantic configuration constraints.
    
    Returns:
        Dictionary with field names as keys and validation functions as values
    """
    # Get constraints from Pydantic config
    default_config = KnowledgeBaseConfig()
    
    def validate_chunk_size(value):
        """Validate chunk size values using Pydantic constraints."""
        if not isinstance(value, int):
            return False, "Chunk size must be an integer"
        if value < 100:
            return False, "Chunk size must be at least 100 characters"
        if value > 8000:
            return False, "Chunk size should not exceed 8000 characters"
        return True, ""
    
    def validate_batch_size(value):
        """Validate embedding batch size using Pydantic constraints."""
        if not isinstance(value, int):
            return False, "Batch size must be an integer"
        if value < 1:
            return False, "Batch size must be at least 1"
        if value > 100:
            return False, "Batch size should not exceed 100 for stability"
        return True, ""
    
    def validate_embedding_model(value):
        """Validate embedding model name."""
        if not isinstance(value, str):
            return False, "Embedding model must be a string"
        if not value.strip():
            return False, "Embedding model cannot be empty"
        valid_models = [
            "text-embedding-ada-002",
            "text-embedding-3-small", 
            "text-embedding-3-large"
        ]
        if value not in valid_models:
            return True, f"Warning: '{value}' is not a standard OpenAI model. Valid options: {', '.join(valid_models)}"
        return True, ""
    
    def validate_bot_identity(value):
        """Validate bot identity text."""
        if not isinstance(value, str):
            return False, "Bot identity must be a string"
        if not value.strip():
            return False, "Bot identity cannot be empty"
        if len(value) < 10:
            return False, "Bot identity should be at least 10 characters"
        if len(value) > 1000:
            return False, "Bot identity should not exceed 1000 characters"
        return True, ""
    
    def validate_bot_message(value):
        """Validate bot message text."""
        if not isinstance(value, str):
            return False, "Bot message must be a string"
        if not value.strip():
            return False, "Bot message cannot be empty"
        if len(value) < 10:
            return False, "Bot message should be at least 10 characters"
        if len(value) > 500:
            return False, "Bot message should not exceed 500 characters"
        return True, ""
    
    return {
        "DOCUMENT_CHUNK_SIZE": validate_chunk_size,
        "ARCHIVE_CHUNK_SIZE": validate_chunk_size,
        "EMBEDDING_BATCH_SIZE": validate_batch_size,
        "EMBEDDING_MODEL": validate_embedding_model,
        "BOT_IDENTITY": validate_bot_identity,
        "BOT_NO_CONTEXT_MESSAGE": validate_bot_message,
    }


# Convenience function for easy import
def get_all_django_cfg_knowbase_constance_config():
    """
    Get complete Constance configuration for Knowledge Base.
    
    Returns:
        Tuple of (fields, validation_rules)
    """
    return get_django_cfg_knowbase_constance_fields(), get_django_cfg_knowbase_field_validation_rules()
