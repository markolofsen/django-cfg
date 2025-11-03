"""
Pydantic models for chunking context metadata.

Data structures for chunk data and context metadata.
"""

from typing import Any, Dict

from pydantic import BaseModel


class ChunkContextMetadata(BaseModel):
    """Rich context metadata for chunks."""

    # Parent hierarchy
    archive_info: Dict[str, Any]
    item_info: Dict[str, Any]

    # Position and structure
    position_info: Dict[str, Any]
    structure_info: Dict[str, Any]

    # Semantic context
    semantic_info: Dict[str, Any]

    # Relational context (optional)
    relationship_info: Dict[str, Any] = {}

    # Processing provenance
    processing_info: Dict[str, Any]


class ChunkData(BaseModel):
    """Data structure for created chunk."""

    content: str
    chunk_index: int
    chunk_type: str
    context_metadata: Dict[str, Any]
