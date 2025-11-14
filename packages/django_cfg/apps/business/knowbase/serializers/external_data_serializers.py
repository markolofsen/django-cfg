"""
External Data serializers for API request/response validation.
"""

from typing import Any, Dict, List, Optional, TypedDict, Union

from pydantic import BaseModel, Field, validator

from ..models.external_data import ExternalDataType


# Type definitions for source configurations
class GitHubSourceConfig(TypedDict, total=False):
    """GitHub source configuration."""
    repository: str
    branch: str
    file_path: Optional[str]
    token: Optional[str]


class WebSourceConfig(TypedDict, total=False):
    """Web/URL source configuration."""
    url: str
    headers: Optional[Dict[str, str]]
    timeout: Optional[int]


class APISourceConfig(TypedDict, total=False):
    """API source configuration."""
    endpoint: str
    method: str
    headers: Optional[Dict[str, str]]
    params: Optional[Dict[str, str]]
    auth_token: Optional[str]


class FileSourceConfig(TypedDict, total=False):
    """File source configuration."""
    file_path: str
    encoding: str


# Union of all possible source configs
SourceConfig = Union[GitHubSourceConfig, WebSourceConfig, APISourceConfig, FileSourceConfig, Dict[str, Any]]


# Type definition for metadata
class SourceMetadata(TypedDict, total=False):
    """Source metadata."""
    author: Optional[str]
    created_date: Optional[str]
    modified_date: Optional[str]
    version: Optional[str]
    language: Optional[str]
    tags: Optional[List[str]]
    custom: Optional[Dict[str, Any]]


# Type definitions for stats breakdowns
SourceTypeBreakdown = Dict[str, int]
StatusBreakdown = Dict[str, int]


# Type definition for action parameters
class BulkActionParameters(TypedDict, total=False):
    """Bulk action parameters."""
    force: bool
    async_mode: bool
    notification: bool
    priority: Optional[str]


class ExternalDataCreateRequest(BaseModel):
    """Request model for creating external data."""

    title: str = Field(description="Human-readable title")
    description: str = Field(default="", description="Description of the data source")
    source_type: ExternalDataType = Field(description="Type of external data source")
    source_identifier: str = Field(description="Unique identifier for the source")
    content: str = Field(description="Text content to vectorize")
    source_config: SourceConfig = Field(default_factory=dict, description="Source configuration")
    metadata: SourceMetadata = Field(default_factory=dict, description="Additional metadata")
    chunk_size: int = Field(default=1000, ge=100, le=2000, description="Chunk size for vectorization")
    overlap_size: int = Field(default=200, ge=0, le=500, description="Overlap between chunks")
    embedding_model: str = Field(default="text-embedding-ada-002", description="Embedding model")
    is_active: bool = Field(default=True, description="Whether the source is active")
    is_public: bool = Field(default=False, description="Whether the source is public")
    tags: List[str] = Field(default_factory=list, description="Tags for categorization")

    @validator('overlap_size')
    def validate_overlap_size(cls, v, values):
        """Ensure overlap size is less than chunk size."""
        chunk_size = values.get('chunk_size', 1000)
        if v >= chunk_size:
            raise ValueError("Overlap size must be less than chunk size")
        return v


class ExternalDataResponse(BaseModel):
    """Response model for external data."""

    id: str = Field(description="External data ID")
    title: str = Field(description="Title")
    description: str = Field(description="Description")
    source_type: str = Field(description="Source type")
    source_identifier: str = Field(description="Source identifier")
    status: str = Field(description="Processing status")
    is_active: bool = Field(description="Whether active")
    is_public: bool = Field(description="Whether public")
    chunk_size: int = Field(description="Chunk size")
    overlap_size: int = Field(description="Overlap size")
    embedding_model: str = Field(description="Embedding model")
    total_chunks: int = Field(description="Total number of chunks")
    total_tokens: int = Field(description="Total tokens processed")
    processing_cost: float = Field(description="Processing cost in USD")
    processed_at: Optional[str] = Field(description="When processed")
    created_at: str = Field(description="When created")
    updated_at: str = Field(description="When last updated")
    tags: List[str] = Field(description="Tags")

    class Config:
        from_attributes = True


class ExternalDataListResponse(BaseModel):
    """Response model for external data list."""

    id: str = Field(description="External data ID")
    title: str = Field(description="Title")
    source_type: str = Field(description="Source type")
    source_identifier: str = Field(description="Source identifier")
    status: str = Field(description="Processing status")
    is_active: bool = Field(description="Whether active")
    total_chunks: int = Field(description="Total chunks")
    processing_cost: float = Field(description="Processing cost")
    processed_at: Optional[str] = Field(description="When processed")
    created_at: str = Field(description="When created")

    class Config:
        from_attributes = True


class ExternalDataChunkResponse(BaseModel):
    """Response model for external data chunk."""

    id: str = Field(description="Chunk ID")
    external_data_id: str = Field(description="External data ID")
    chunk_index: int = Field(description="Chunk index")
    content: str = Field(description="Chunk content")
    token_count: int = Field(description="Token count")
    character_count: int = Field(description="Character count")
    embedding_model: str = Field(description="Embedding model")
    embedding_cost: float = Field(description="Embedding cost")
    created_at: str = Field(description="When created")

    class Config:
        from_attributes = True


class ExternalDataSearchRequest(BaseModel):
    """Request model for external data search."""

    query: str = Field(description="Search query")
    limit: int = Field(default=5, ge=1, le=50, description="Maximum results")
    threshold: float = Field(default=0.7, ge=0.0, le=1.0, description="Similarity threshold")
    source_types: Optional[List[str]] = Field(default=None, description="Filter by source types")
    source_identifiers: Optional[List[str]] = Field(default=None, description="Filter by source identifiers")
    include_inactive: bool = Field(default=False, description="Include inactive sources")


class ExternalDataSearchResult(BaseModel):
    """Single search result."""

    type: str = Field(description="Result type")
    similarity: float = Field(description="Similarity score")
    source_title: str = Field(description="Source title")
    content: str = Field(description="Chunk content")
    metadata: SourceMetadata = Field(description="Additional metadata")

    chunk_id: str = Field(description="Chunk ID")
    chunk_index: int = Field(description="Chunk index")
    external_data_id: str = Field(description="External data ID")
    source_type: str = Field(description="Source type")
    source_identifier: str = Field(description="Source identifier")


class ExternalDataSearchResponse(BaseModel):
    """Response model for external data search."""

    query: str = Field(description="Original query")
    results: List[ExternalDataSearchResult] = Field(description="Search results")
    total_results: int = Field(description="Total number of results")
    search_time_ms: float = Field(description="Search time in milliseconds")


class ExternalDataVectorizeRequest(BaseModel):
    """Request model for vectorizing external data."""

    external_data_ids: List[str] = Field(description="List of external data IDs to vectorize")
    force_revectorize: bool = Field(default=False, description="Force re-vectorization")


class ExternalDataVectorizeResponse(BaseModel):
    """Response model for vectorization."""

    total_requested: int = Field(description="Total requested for vectorization")
    processed: int = Field(description="Successfully processed")
    failed: int = Field(description="Failed to process")
    skipped: int = Field(description="Skipped (already processed)")
    total_cost: float = Field(description="Total processing cost")
    processing_time_ms: float = Field(description="Total processing time")


class ExternalDataStatsResponse(BaseModel):
    """Response model for external data statistics."""

    total_sources: int = Field(description="Total number of sources")
    active_sources: int = Field(description="Active sources")
    processed_sources: int = Field(description="Successfully processed sources")
    failed_sources: int = Field(description="Failed sources")
    pending_sources: int = Field(description="Pending sources")

    total_chunks: int = Field(description="Total chunks")
    total_tokens: int = Field(description="Total tokens")
    total_cost: float = Field(description="Total cost")
    average_cost_per_source: float = Field(description="Average cost per source")

    source_type_breakdown: SourceTypeBreakdown = Field(description="Breakdown by source type")
    status_breakdown: StatusBreakdown = Field(description="Breakdown by status")

    last_processed_at: Optional[str] = Field(description="Last processing time")


class ExternalDataHealthResponse(BaseModel):
    """Response model for health check."""

    status: str = Field(description="Overall status")
    healthy: bool = Field(description="Whether system is healthy")

    database_healthy: bool = Field(description="Database health")
    embedding_service_healthy: bool = Field(description="Embedding service health")
    processing_healthy: bool = Field(description="Processing health")

    response_time_ms: float = Field(description="Response time")
    active_sources: int = Field(description="Active sources")
    pending_processing: int = Field(description="Pending processing")
    failed_processing: int = Field(description="Failed processing")

    issues: List[str] = Field(description="Current issues")
    warnings: List[str] = Field(description="Warnings")
    checked_at: str = Field(description="Check timestamp")


class ExternalDataUpdateRequest(BaseModel):
    """Request model for updating external data."""

    title: Optional[str] = Field(default=None, description="New title")
    description: Optional[str] = Field(default=None, description="New description")
    content: Optional[str] = Field(default=None, description="New content")
    is_active: Optional[bool] = Field(default=None, description="Active status")
    is_public: Optional[bool] = Field(default=None, description="Public status")
    tags: Optional[List[str]] = Field(default=None, description="Tags")
    source_config: Optional[SourceConfig] = Field(default=None, description="Source configuration")
    metadata: Optional[SourceMetadata] = Field(default=None, description="Metadata")
    auto_revectorize: bool = Field(default=True, description="Auto re-vectorize if content changed")


class ExternalDataBulkActionRequest(BaseModel):
    """Request model for bulk actions."""

    external_data_ids: List[str] = Field(description="List of external data IDs")
    action: str = Field(description="Action to perform")
    parameters: BulkActionParameters = Field(default_factory=dict, description="Action parameters")


class ExternalDataBulkActionResponse(BaseModel):
    """Response model for bulk actions."""

    action: str = Field(description="Action performed")
    total_requested: int = Field(description="Total items requested")
    successful: int = Field(description="Successfully processed")
    failed: int = Field(description="Failed to process")
    errors: List[str] = Field(description="Error messages")


class ExternalDataQuickAddRequest(BaseModel):
    """Request model for quickly adding external data."""

    title: str = Field(description="Title")
    content: str = Field(description="Content to vectorize")
    source_type: ExternalDataType = Field(default=ExternalDataType.CUSTOM, description="Source type")
    description: str = Field(default="", description="Description")
    tags: List[str] = Field(default_factory=list, description="Tags")
    auto_vectorize: bool = Field(default=True, description="Auto vectorize")


class ExternalDataImportRequest(BaseModel):
    """Request model for importing external data from various sources."""

    source_type: ExternalDataType = Field(description="Type of source to import")
    source_config: SourceConfig = Field(description="Configuration for import")
    title: str = Field(description="Title for imported data")
    description: str = Field(default="", description="Description")
    auto_vectorize: bool = Field(default=True, description="Auto vectorize after import")
    chunk_size: int = Field(default=1000, description="Chunk size")
    overlap_size: int = Field(default=200, description="Overlap size")


class ExternalDataImportResponse(BaseModel):
    """Response model for import operation."""

    external_data_id: str = Field(description="Created external data ID")
    title: str = Field(description="Title")
    source_type: str = Field(description="Source type")
    content_length: int = Field(description="Length of imported content")
    vectorization_started: bool = Field(description="Whether vectorization was started")
    import_time_ms: float = Field(description="Import time in milliseconds")
