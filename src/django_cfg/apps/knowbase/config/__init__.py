"""
Knowledge Base configuration module.

This module provides configuration utilities for the knowledge base app,
including Pydantic-based settings and optional Constance field definitions.
"""

# Import the main Pydantic configuration
from .settings import (
    KnowledgeBaseConfig,
    get_config,
    reload_config,
    get_document_chunk_size,
    get_archive_chunk_size,
    get_embedding_model,
    get_embedding_batch_size,
    get_chunking_params_for_type,
)

# Constance-related imports are optional and only loaded when needed
# to avoid django_cfg dependency issues
def get_django_cfg_knowbase_constance_fields():
    """Lazy import of Constance fields to avoid dependency issues."""
    from .constance_fields import get_django_cfg_knowbase_constance_fields as _get_fields
    return _get_fields()

def get_django_cfg_knowbase_field_validation_rules():
    """Lazy import of Constance validation rules to avoid dependency issues."""
    from .constance_fields import get_django_cfg_knowbase_field_validation_rules as _get_rules
    return _get_rules()

def get_all_django_cfg_knowbase_constance_config():
    """Lazy import of complete Constance configuration to avoid dependency issues."""
    from .constance_fields import get_all_django_cfg_knowbase_constance_config as _get_config
    return _get_config()

__all__ = [
    # Pydantic configuration
    "KnowledgeBaseConfig",
    "get_config",
    "reload_config",
    "get_document_chunk_size",
    "get_archive_chunk_size", 
    "get_embedding_model",
    "get_embedding_batch_size",
    "get_chunking_params_for_type",
    # Constance configuration (lazy loaded)
    "get_django_cfg_knowbase_constance_fields",
    "get_django_cfg_knowbase_field_validation_rules", 
    "get_all_django_cfg_knowbase_constance_config",
]
