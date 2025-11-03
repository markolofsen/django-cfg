# Knowledge Base Configuration

This directory contains the new Pydantic-based configuration system that replaces the removed Constance settings.

## Overview

The configuration system provides:
- **Type safety** with Pydantic models
- **Validation** of configuration values
- **Environment variable support** with `KNOWBASE_` prefix
- **Backward compatibility** with existing code

## Files

- `settings.py` - **Main Pydantic configuration models** (single source of truth)
- `constance_fields.py` - **Constance configuration** (automatically synchronized with `settings.py`)
- `SYNCHRONIZATION.md` - **Detailed explanation** of how synchronization works
- `README.md` - This file

## Usage

### Basic Usage

```python
from apps.knowbase.config.settings import get_config

# Get the global configuration
config = get_config()

# Access settings
chunk_size = config.chunking.document_chunk_size  # 1000
embedding_model = config.embedding.model  # "text-embedding-ada-002"
```

### Convenience Functions

```python
from apps.knowbase.config.settings import (
    get_document_chunk_size,
    get_embedding_model,
    get_chunking_params_for_type
)

# Direct access to common settings
chunk_size = get_document_chunk_size()  # 1000
model = get_embedding_model()  # "text-embedding-ada-002"

# Get chunking parameters for SemanticChunker
doc_params = get_chunking_params_for_type('document')
# Returns: {'chunk_size': 1000, 'overlap': 200}

archive_params = get_chunking_params_for_type('archive')
# Returns: {'chunk_size': 800, 'overlap': 160}
```

## Configuration Sections

### EmbeddingConfig
- `model`: OpenAI embedding model (default: "text-embedding-ada-002")
- `batch_size`: Chunks per batch (default: 50, range: 1-100)
- `max_retries`: Max retries for failed embeddings (default: 3)
- `timeout_seconds`: API timeout (default: 30)

### ChunkingConfig
- `document_chunk_size`: Document chunk size (default: 1000, range: 100-8000)
- `document_chunk_overlap`: Document overlap (default: 200)
- `archive_chunk_size`: Archive chunk size (default: 800, range: 100-8000)
- `archive_chunk_overlap`: Archive overlap (default: 160)

### SearchConfig
- `results_limit`: Max search results (default: 10, range: 1-100)
- `similarity_threshold`: Min similarity score (default: 0.7, range: 0.0-1.0)

### ChatConfig
- `context_chunks`: Chunks in chat context (default: 5, range: 1-20)
- `max_tokens`: Max tokens for completion (default: 4000, range: 100-32000)
- `temperature`: Creativity level (default: 0.7, range: 0.0-2.0)

### ProcessingConfig
- `max_document_size_mb`: Max document size (default: 10MB, range: 1-100)
- `max_archive_size_mb`: Max archive size (default: 50MB, range: 1-500)
- `timeout_minutes`: Processing timeout (default: 30, range: 1-180)

## Environment Variables

You can override any setting using environment variables with the `KNOWBASE_` prefix:

```bash
# Override document chunk size
export KNOWBASE_CHUNKING__DOCUMENT_CHUNK_SIZE=1500

# Override embedding model
export KNOWBASE_EMBEDDING__MODEL=text-embedding-3-small

# Override search results limit
export KNOWBASE_SEARCH__RESULTS_LIMIT=20
```

Note the double underscore `__` to separate nested configuration sections.

## Validation

The configuration system automatically validates all values:

```python
# This will raise a validation error
config = KnowledgeBaseConfig(
    chunking={
        "document_chunk_size": -100  # Must be >= 100
    }
)

# This will also raise an error
config = KnowledgeBaseConfig(
    chunking={
        "document_chunk_size": 100,
        "document_chunk_overlap": 200  # Must be < chunk_size
    }
)
```

## Synchronization with Constance

**Important**: `settings.py` is the **single source of truth**. The `constance_fields.py` automatically pulls default values from the Pydantic configuration to ensure consistency.

```python
# settings.py (MASTER)
class ChunkingConfig(BaseModel):
    document_chunk_size: int = Field(default=1000, ge=100, le=8000)

# constance_fields.py (SYNCHRONIZED)
def get_knowbase_constance_fields():
    default_config = KnowledgeBaseConfig()  # ← Pulls from settings.py
    return [
        ConstanceField(
            name="DOCUMENT_CHUNK_SIZE",
            default=default_config.chunking.document_chunk_size,  # ← Always in sync!
        )
    ]
```

This eliminates duplicate default values and ensures consistency across the application.

## Migration from Constance

The new system is backward compatible. Existing code using:

```python
from apps.knowbase.utils.chunk_settings import get_document_chunk_size
```

Will continue to work without changes. The `chunk_settings.py` module now internally uses the new Pydantic configuration.

## Benefits

1. **Type Safety**: All configuration values are properly typed
2. **Validation**: Invalid values are caught at startup
3. **Documentation**: Each setting has clear descriptions and ranges
4. **Environment Support**: Easy deployment configuration
5. **Performance**: No database queries for configuration access
6. **Testing**: Easy to mock and test different configurations

## Testing

```python
from apps.knowbase.config.settings import KnowledgeBaseConfig

# Create test configuration
test_config = KnowledgeBaseConfig(
    chunking={"document_chunk_size": 500},
    embedding={"batch_size": 10}
)

# Use in tests
assert test_config.chunking.document_chunk_size == 500
```
