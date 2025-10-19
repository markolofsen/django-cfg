from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from ..enums import ArchiveItemChunkDetailchunk_type, ArchiveItemChunkRequestchunk_type, ArchiveItemChunkchunk_type, ArchiveItemDetailcontent_type, ArchiveItemcontent_type, DocumentArchiveDetailarchive_type, DocumentArchiveDetailprocessing_status, DocumentArchivearchive_type, DocumentArchiveprocessing_status, PatchedArchiveItemChunkRequestchunk_type


class PaginatedChatResponseList(BaseModel):
    """
    
    Response model (includes read-only fields).
    """

    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid",
        frozen=False,
    )

    count: int = Field(description='Total number of items across all pages')
    page: int = Field(description='Current page number (1-based)')
    pages: int = Field(description='Total number of pages')
    page_size: int = Field(description='Number of items per page')
    has_next: bool = Field(description='Whether there is a next page')
    has_previous: bool = Field(description='Whether there is a previous page')
    next_page: int | None = Field(None, description='Next page number (null if no next page)')
    previous_page: int | None = Field(None, description='Previous page number (null if no previous page)')
    results: list[dict[str, Any]] = Field(description='Array of items for current page')



class ChatResponse(BaseModel):
    """
    Chat response serializer.

    Response model (includes read-only fields).
    """

    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid",
        frozen=False,
    )

    message_id: str = ...
    content: str = ...
    tokens_used: int = ...
    cost_usd: float = ...
    processing_time_ms: int = ...
    model_used: str = ...
    sources: list[dict[str, Any]] | None = None



class ChatHistory(BaseModel):
    """
    Chat history response serializer.

    Response model (includes read-only fields).
    """

    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid",
        frozen=False,
    )

    session_id: str = ...
    messages: list[dict[str, Any]] = ...
    total_messages: int = ...



class PaginatedDocumentList(BaseModel):
    """
    
    Response model (includes read-only fields).
    """

    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid",
        frozen=False,
    )

    count: int = Field(description='Total number of items across all pages')
    page: int = Field(description='Current page number (1-based)')
    pages: int = Field(description='Total number of pages')
    page_size: int = Field(description='Number of items per page')
    has_next: bool = Field(description='Whether there is a next page')
    has_previous: bool = Field(description='Whether there is a previous page')
    next_page: int | None = Field(None, description='Next page number (null if no next page)')
    previous_page: int | None = Field(None, description='Previous page number (null if no previous page)')
    results: list[dict[str, Any]] = Field(description='Array of items for current page')



class Document(BaseModel):
    """
    Document response serializer.

    Response model (includes read-only fields).
    """

    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid",
        frozen=False,
    )

    id: str = ...
    title: str = Field(description='Document title', max_length=512)
    file_type: str = Field(None, description='MIME type of original file', max_length=100)
    file_size: int = Field(None, description='Original file size in bytes', ge=0.0, le=2147483647.0)
    processing_status: str = ...
    chunks_count: int = ...
    total_tokens: int = ...
    total_cost_usd: float = ...
    created_at: str = ...
    updated_at: str = ...
    processing_started_at: str = ...
    processing_completed_at: str = ...
    processing_error: str = ...
    metadata: str | None = Field(None, description='Additional document metadata')



class DocumentProcessingStatus(BaseModel):
    """
    Document processing status serializer.

    Response model (includes read-only fields).
    """

    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid",
        frozen=False,
    )

    id: str = ...
    status: str = ...
    progress: str = ...
    error: str | None = None
    processing_time_seconds: float | None = None



class DocumentStats(BaseModel):
    """
    Document processing statistics serializer.

    Response model (includes read-only fields).
    """

    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid",
        frozen=False,
    )

    total_documents: int = ...
    completed_documents: int = ...
    processing_success_rate: float = ...
    total_chunks: int = ...
    total_tokens: int = ...
    total_cost_usd: float = ...
    avg_processing_time_seconds: float = ...



class PaginatedChatSessionList(BaseModel):
    """
    
    Response model (includes read-only fields).
    """

    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid",
        frozen=False,
    )

    count: int = Field(description='Total number of items across all pages')
    page: int = Field(description='Current page number (1-based)')
    pages: int = Field(description='Total number of pages')
    page_size: int = Field(description='Number of items per page')
    has_next: bool = Field(description='Whether there is a next page')
    has_previous: bool = Field(description='Whether there is a previous page')
    next_page: int | None = Field(None, description='Next page number (null if no next page)')
    previous_page: int | None = Field(None, description='Previous page number (null if no previous page)')
    results: list[dict[str, Any]] = Field(description='Array of items for current page')



class ChatSession(BaseModel):
    """
    Chat session response serializer.

    Response model (includes read-only fields).
    """

    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid",
        frozen=False,
    )

    id: str = ...
    title: str = Field(None, description='Session title (auto-generated if empty)', max_length=255)
    is_active: bool = Field(None, description='Whether session accepts new messages')
    messages_count: int = Field(None, ge=0.0, le=2147483647.0)
    total_tokens_used: int = Field(None, ge=0.0, le=2147483647.0)
    total_cost_usd: float = ...
    model_name: str = Field(None, description='LLM model used for this session', max_length=100)
    temperature: float = Field(None, description='Temperature setting for LLM')
    max_context_chunks: int = Field(None, description='Maximum chunks to include in context', ge=0.0, le=2147483647.0)
    created_at: str = ...
    updated_at: str = ...



class PaginatedPublicCategoryList(BaseModel):
    """
    
    Response model (includes read-only fields).
    """

    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid",
        frozen=False,
    )

    count: int = Field(description='Total number of items across all pages')
    page: int = Field(description='Current page number (1-based)')
    pages: int = Field(description='Total number of pages')
    page_size: int = Field(description='Number of items per page')
    has_next: bool = Field(description='Whether there is a next page')
    has_previous: bool = Field(description='Whether there is a previous page')
    next_page: int | None = Field(None, description='Next page number (null if no next page)')
    previous_page: int | None = Field(None, description='Previous page number (null if no previous page)')
    results: list[dict[str, Any]] = Field(description='Array of items for current page')



class PublicCategory(BaseModel):
    """
    Public category serializer.

    Response model (includes read-only fields).
    """

    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid",
        frozen=False,
    )

    id: str = ...
    name: str = Field(description='Category name', max_length=255)
    description: str = Field(None, description='Category description')



class PaginatedPublicDocumentListList(BaseModel):
    """
    
    Response model (includes read-only fields).
    """

    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid",
        frozen=False,
    )

    count: int = Field(description='Total number of items across all pages')
    page: int = Field(description='Current page number (1-based)')
    pages: int = Field(description='Total number of pages')
    page_size: int = Field(description='Number of items per page')
    has_next: bool = Field(description='Whether there is a next page')
    has_previous: bool = Field(description='Whether there is a previous page')
    next_page: int | None = Field(None, description='Next page number (null if no next page)')
    previous_page: int | None = Field(None, description='Previous page number (null if no previous page)')
    results: list[dict[str, Any]] = Field(description='Array of items for current page')



class PublicDocument(BaseModel):
    """
    Public document detail serializer - only essential data for clients.

    Response model (includes read-only fields).
    """

    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid",
        frozen=False,
    )

    id: str = ...
    title: str = Field(description='Document title', max_length=512)
    content: str = Field(description='Full document content')
    category: dict[str, Any] = ...
    created_at: str = ...
    updated_at: str = ...



class PaginatedDocumentArchiveListList(BaseModel):
    """
    
    Response model (includes read-only fields).
    """

    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid",
        frozen=False,
    )

    count: int = Field(description='Total number of items across all pages')
    page: int = Field(description='Current page number (1-based)')
    pages: int = Field(description='Total number of pages')
    page_size: int = Field(description='Number of items per page')
    has_next: bool = Field(description='Whether there is a next page')
    has_previous: bool = Field(description='Whether there is a previous page')
    next_page: int | None = Field(None, description='Next page number (null if no next page)')
    previous_page: int | None = Field(None, description='Previous page number (null if no previous page)')
    results: list[dict[str, Any]] = Field(description='Array of items for current page')



class ArchiveProcessingResult(BaseModel):
    """
    Archive processing result serializer.

    Response model (includes read-only fields).
    """

    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid",
        frozen=False,
    )

    archive_id: str = ...
    status: str = ...
    processing_time_ms: int = ...
    items_processed: int = ...
    chunks_created: int = ...
    vectorized_chunks: int = ...
    total_cost_usd: float = ...
    error_message: str = ...



class DocumentArchiveDetail(BaseModel):
    """
    Detailed archive serializer with items.

    Response model (includes read-only fields).
    """

    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid",
        frozen=False,
    )

    id: str = ...
    title: str = Field(description='Archive title', max_length=512)
    description: str = Field(None, description='Archive description')
    categories: list[dict[str, Any]] = ...
    is_public: bool = Field(None, description='Whether this archive is publicly accessible')
    archive_file: str = Field(description='Uploaded archive file')
    original_filename: str = Field(description='Original uploaded filename')
    file_size: int = Field(description='Archive size in bytes')
    archive_type: DocumentArchiveDetailArchiveType = Field(description='Archive format\n\n* `zip` - ZIP\n* `tar` - TAR\n* `tar.gz` - TAR GZ\n* `tar.bz2` - TAR BZ2')
    processing_status: DocumentArchiveDetailProcessingStatus = Field(description='* `pending` - Pending\n* `processing` - Processing\n* `completed` - Completed\n* `failed` - Failed\n* `cancelled` - Cancelled')
    processed_at: str | None = Field(description='When processing completed')
    processing_duration_ms: int = Field(description='Processing time in milliseconds')
    processing_error: str = Field(description='Error message if processing failed')
    total_items: int = Field(description='Total items in archive')
    processed_items: int = Field(description='Successfully processed items')
    total_chunks: int = Field(description='Total chunks created')
    vectorized_chunks: int = Field(description='Chunks with embeddings')
    total_tokens: int = Field(description='Total tokens across all chunks')
    total_cost_usd: float = Field(description='Total processing cost in USD')
    processing_progress: float = Field(description='Calculate processing progress as percentage.')
    vectorization_progress: float = Field(description='Calculate vectorization progress as percentage.')
    is_processed: bool = Field(description='Check if archive processing is completed.')
    created_at: str = ...
    updated_at: str = ...
    items: list[dict[str, Any]] = ...
    file_tree: dict[str, Any] = Field(description='Get hierarchical file tree.')
    metadata: str | None = Field(None, description='Additional archive metadata')



class DocumentArchive(BaseModel):
    """
    Document archive serializer.

    Response model (includes read-only fields).
    """

    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid",
        frozen=False,
    )

    id: str = ...
    title: str = Field(description='Archive title', max_length=512)
    description: str = Field(None, description='Archive description')
    categories: list[dict[str, Any]] = ...
    is_public: bool = Field(None, description='Whether this archive is publicly accessible')
    archive_file: str = Field(description='Uploaded archive file')
    original_filename: str = Field(description='Original uploaded filename')
    file_size: int = Field(description='Archive size in bytes')
    archive_type: DocumentArchiveArchiveType = Field(description='Archive format\n\n* `zip` - ZIP\n* `tar` - TAR\n* `tar.gz` - TAR GZ\n* `tar.bz2` - TAR BZ2')
    processing_status: DocumentArchiveProcessingStatus = Field(description='* `pending` - Pending\n* `processing` - Processing\n* `completed` - Completed\n* `failed` - Failed\n* `cancelled` - Cancelled')
    processed_at: str | None = Field(description='When processing completed')
    processing_duration_ms: int = Field(description='Processing time in milliseconds')
    processing_error: str = Field(description='Error message if processing failed')
    total_items: int = Field(description='Total items in archive')
    processed_items: int = Field(description='Successfully processed items')
    total_chunks: int = Field(description='Total chunks created')
    vectorized_chunks: int = Field(description='Chunks with embeddings')
    total_tokens: int = Field(description='Total tokens across all chunks')
    total_cost_usd: float = Field(description='Total processing cost in USD')
    processing_progress: float = Field(description='Calculate processing progress as percentage.')
    vectorization_progress: float = Field(description='Calculate vectorization progress as percentage.')
    is_processed: bool = Field(description='Check if archive processing is completed.')
    created_at: str = ...
    updated_at: str = ...



class PaginatedArchiveItemList(BaseModel):
    """
    
    Response model (includes read-only fields).
    """

    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid",
        frozen=False,
    )

    count: int = Field(description='Total number of items across all pages')
    page: int = Field(description='Current page number (1-based)')
    pages: int = Field(description='Total number of pages')
    page_size: int = Field(description='Number of items per page')
    has_next: bool = Field(description='Whether there is a next page')
    has_previous: bool = Field(description='Whether there is a previous page')
    next_page: int | None = Field(None, description='Next page number (null if no next page)')
    previous_page: int | None = Field(None, description='Previous page number (null if no previous page)')
    results: list[dict[str, Any]] = Field(description='Array of items for current page')



class PaginatedArchiveSearchResultList(BaseModel):
    """
    
    Response model (includes read-only fields).
    """

    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid",
        frozen=False,
    )

    count: int = Field(description='Total number of items across all pages')
    page: int = Field(description='Current page number (1-based)')
    pages: int = Field(description='Total number of pages')
    page_size: int = Field(description='Number of items per page')
    has_next: bool = Field(description='Whether there is a next page')
    has_previous: bool = Field(description='Whether there is a previous page')
    next_page: int | None = Field(None, description='Next page number (null if no next page)')
    previous_page: int | None = Field(None, description='Previous page number (null if no previous page)')
    results: list[dict[str, Any]] = Field(description='Array of items for current page')



class VectorizationResult(BaseModel):
    """
    Vectorization result serializer.

    Response model (includes read-only fields).
    """

    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid",
        frozen=False,
    )

    vectorized_count: int = ...
    failed_count: int = ...
    total_tokens: int = ...
    total_cost: float = ...
    success_rate: float = ...
    errors: list[str] = ...



class ArchiveStatistics(BaseModel):
    """
    Archive statistics serializer.

    Response model (includes read-only fields).
    """

    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid",
        frozen=False,
    )

    total_archives: int = ...
    processed_archives: int = ...
    failed_archives: int = ...
    total_items: int = ...
    total_chunks: int = ...
    total_tokens: int = ...
    total_cost: float = ...
    avg_processing_time: float = ...
    avg_items_per_archive: float = ...
    avg_chunks_per_archive: float = ...



class VectorizationStatistics(BaseModel):
    """
    Vectorization statistics serializer.

    Response model (includes read-only fields).
    """

    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid",
        frozen=False,
    )

    total_chunks: int = ...
    vectorized_chunks: int = ...
    pending_chunks: int = ...
    vectorization_rate: float = ...
    total_tokens: int = ...
    total_cost: float = ...
    avg_tokens_per_chunk: float = ...
    avg_cost_per_chunk: float = ...



class PaginatedArchiveItemChunkList(BaseModel):
    """
    
    Response model (includes read-only fields).
    """

    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid",
        frozen=False,
    )

    count: int = Field(description='Total number of items across all pages')
    page: int = Field(description='Current page number (1-based)')
    pages: int = Field(description='Total number of pages')
    page_size: int = Field(description='Number of items per page')
    has_next: bool = Field(description='Whether there is a next page')
    has_previous: bool = Field(description='Whether there is a previous page')
    next_page: int | None = Field(None, description='Next page number (null if no next page)')
    previous_page: int | None = Field(None, description='Previous page number (null if no previous page)')
    results: list[dict[str, Any]] = Field(description='Array of items for current page')



class ArchiveItemChunk(BaseModel):
    """
    Archive item chunk serializer.

    Response model (includes read-only fields).
    """

    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid",
        frozen=False,
    )

    id: str = ...
    content: str = Field(description='Chunk text content')
    chunk_index: int = Field(description='Sequential chunk number within item', ge=0.0, le=2147483647.0)
    chunk_type: ArchiveItemChunkChunkType = Field(None, description='Type of content in chunk\n\n* `text` - Text\n* `code` - Code\n* `heading` - Heading\n* `metadata` - Metadata\n* `table` - Table\n* `list` - List')
    token_count: int = Field(description='Number of tokens in chunk')
    character_count: int = Field(description='Number of characters in chunk')
    embedding_model: str = Field(description='Model used for embedding generation')
    embedding_cost: float = Field(description='Cost in USD for embedding generation')
    context_summary: dict[str, Any] = Field(description='Get context summary for display.')
    created_at: str = ...



class ArchiveItemChunkDetail(BaseModel):
    """
    Detailed chunk serializer with full context.

    Response model (includes read-only fields).
    """

    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid",
        frozen=False,
    )

    id: str = ...
    content: str = Field(description='Chunk text content')
    chunk_index: int = Field(description='Sequential chunk number within item', ge=0.0, le=2147483647.0)
    chunk_type: ArchiveItemChunkDetailChunkType = Field(None, description='Type of content in chunk\n\n* `text` - Text\n* `code` - Code\n* `heading` - Heading\n* `metadata` - Metadata\n* `table` - Table\n* `list` - List')
    token_count: int = Field(description='Number of tokens in chunk')
    character_count: int = Field(description='Number of characters in chunk')
    embedding_model: str = Field(description='Model used for embedding generation')
    embedding_cost: float = Field(description='Cost in USD for embedding generation')
    context_summary: dict[str, Any] = Field(description='Get context summary for display.')
    created_at: str = ...
    context_metadata: str = ...



class ArchiveItem(BaseModel):
    """
    Archive item serializer.

    Response model (includes read-only fields).
    """

    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid",
        frozen=False,
    )

    id: str = ...
    relative_path: str = Field(description='Path within archive', max_length=1024)
    item_name: str = Field(description='Item name', max_length=255)
    item_type: str = Field(description='MIME type', max_length=100)
    content_type: ArchiveItemContentType = Field(description='Content classification\n\n* `document` - Document\n* `code` - Code\n* `image` - Image\n* `data` - Data\n* `archive` - Archive\n* `unknown` - Unknown')
    file_size: int = Field(None, description='Item size in bytes', ge=0.0, le=2147483647.0)
    is_processable: bool = Field(description='Whether item can be processed for chunks')
    language: str = Field(description='Programming language or document language')
    encoding: str = Field(description='Character encoding')
    chunks_count: int = Field(description='Number of chunks created')
    total_tokens: int = Field(description='Total tokens in all chunks')
    processing_cost: float = Field(description='Processing cost for this item')
    created_at: str = ...
    updated_at: str = ...



class ArchiveItemDetail(BaseModel):
    """
    Detailed archive item serializer with content.

    Response model (includes read-only fields).
    """

    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid",
        frozen=False,
    )

    id: str = ...
    relative_path: str = Field(description='Path within archive', max_length=1024)
    item_name: str = Field(description='Item name', max_length=255)
    item_type: str = Field(description='MIME type', max_length=100)
    content_type: ArchiveItemDetailContentType = Field(description='Content classification\n\n* `document` - Document\n* `code` - Code\n* `image` - Image\n* `data` - Data\n* `archive` - Archive\n* `unknown` - Unknown')
    file_size: int = Field(None, description='Item size in bytes', ge=0.0, le=2147483647.0)
    is_processable: bool = Field(description='Whether item can be processed for chunks')
    language: str = Field(description='Programming language or document language')
    encoding: str = Field(description='Character encoding')
    chunks_count: int = Field(description='Number of chunks created')
    total_tokens: int = Field(description='Total tokens in all chunks')
    processing_cost: float = Field(description='Processing cost for this item')
    created_at: str = ...
    updated_at: str = ...
    raw_content: str = ...
    metadata: str = ...



class ChatResponseRequest(BaseModel):
    """
    Chat response serializer.

    Request model (no read-only fields).
    """

    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid",
        frozen=False,
    )

    message_id: str = ...
    content: str = Field(min_length=1)
    tokens_used: int = ...
    cost_usd: float = ...
    processing_time_ms: int = ...
    model_used: str = Field(min_length=1)
    sources: list[dict[str, Any]] | None = None



class PatchedChatResponseRequest(BaseModel):
    """
    Chat response serializer.

    Request model (no read-only fields).
    """

    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid",
        frozen=False,
    )

    message_id: str = None
    content: str = Field(None, min_length=1)
    tokens_used: int = None
    cost_usd: float = None
    processing_time_ms: int = None
    model_used: str = Field(None, min_length=1)
    sources: list[dict[str, Any]] | None = None



class ChatQueryRequest(BaseModel):
    """
    Chat query request serializer.

    Request model (no read-only fields).
    """

    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid",
        frozen=False,
    )

    session_id: str | None = Field(None, description='Chat session ID (creates new if not provided)')
    query: str = Field(description='User query', min_length=1, max_length=2000)
    max_tokens: int = Field(None, description='Maximum response tokens', ge=1.0, le=4000.0)
    include_sources: bool = Field(None, description='Include source documents in response')



class DocumentCreateRequest(BaseModel):
    """
    Document creation request serializer.

    Request model (no read-only fields).
    """

    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid",
        frozen=False,
    )

    title: str = Field(description='Document title', min_length=1, max_length=512)
    content: str = Field(description='Document content', min_length=10, max_length=1000000)
    file_type: str = Field(None, description='MIME type', min_length=1, pattern='^[a-z]+/[a-z0-9\\-\\+\\.]+$')
    metadata: str = Field(None, description='Additional metadata')



class DocumentRequest(BaseModel):
    """
    Document response serializer.

    Request model (no read-only fields).
    """

    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid",
        frozen=False,
    )

    title: str = Field(description='Document title', min_length=1, max_length=512)
    file_type: str = Field(None, description='MIME type of original file', min_length=1, max_length=100)
    file_size: int = Field(None, description='Original file size in bytes', ge=0.0, le=2147483647.0)
    metadata: str | None = Field(None, description='Additional document metadata')



class PatchedDocumentRequest(BaseModel):
    """
    Document response serializer.

    Request model (no read-only fields).
    """

    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid",
        frozen=False,
    )

    title: str = Field(None, description='Document title', min_length=1, max_length=512)
    file_type: str = Field(None, description='MIME type of original file', min_length=1, max_length=100)
    file_size: int = Field(None, description='Original file size in bytes', ge=0.0, le=2147483647.0)
    metadata: str | None = Field(None, description='Additional document metadata')



class ChatSessionCreateRequest(BaseModel):
    """
    Chat session creation request serializer.

    Request model (no read-only fields).
    """

    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid",
        frozen=False,
    )

    title: str = Field(None, description='Session title', max_length=255)
    model_name: str = Field(None, description='LLM model to use', min_length=1, max_length=100)
    temperature: float = Field(None, description='Response creativity', ge=0.0, le=2.0)
    max_context_chunks: int = Field(None, description='Maximum context chunks', ge=1.0, le=10.0)



class ChatSessionRequest(BaseModel):
    """
    Chat session response serializer.

    Request model (no read-only fields).
    """

    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid",
        frozen=False,
    )

    title: str = Field(None, description='Session title (auto-generated if empty)', max_length=255)
    is_active: bool = Field(None, description='Whether session accepts new messages')
    messages_count: int = Field(None, ge=0.0, le=2147483647.0)
    total_tokens_used: int = Field(None, ge=0.0, le=2147483647.0)
    model_name: str = Field(None, description='LLM model used for this session', min_length=1, max_length=100)
    temperature: float = Field(None, description='Temperature setting for LLM')
    max_context_chunks: int = Field(None, description='Maximum chunks to include in context', ge=0.0, le=2147483647.0)



class PatchedChatSessionRequest(BaseModel):
    """
    Chat session response serializer.

    Request model (no read-only fields).
    """

    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid",
        frozen=False,
    )

    title: str = Field(None, description='Session title (auto-generated if empty)', max_length=255)
    is_active: bool = Field(None, description='Whether session accepts new messages')
    messages_count: int = Field(None, ge=0.0, le=2147483647.0)
    total_tokens_used: int = Field(None, ge=0.0, le=2147483647.0)
    model_name: str = Field(None, description='LLM model used for this session', min_length=1, max_length=100)
    temperature: float = Field(None, description='Temperature setting for LLM')
    max_context_chunks: int = Field(None, description='Maximum chunks to include in context', ge=0.0, le=2147483647.0)



class DocumentArchiveRequest(BaseModel):
    """
    Document archive serializer.

    Request model (no read-only fields).
    """

    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid",
        frozen=False,
    )

    title: str = Field(description='Archive title', min_length=1, max_length=512)
    description: str = Field(None, description='Archive description')
    is_public: bool = Field(None, description='Whether this archive is publicly accessible')



class PatchedDocumentArchiveRequest(BaseModel):
    """
    Document archive serializer.

    Request model (no read-only fields).
    """

    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid",
        frozen=False,
    )

    title: str = Field(None, description='Archive title', min_length=1, max_length=512)
    description: str = Field(None, description='Archive description')
    is_public: bool = Field(None, description='Whether this archive is publicly accessible')



class ArchiveSearchRequestRequest(BaseModel):
    """
    Archive search request serializer.

    Request model (no read-only fields).
    """

    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid",
        frozen=False,
    )

    query: str = Field(description='Search query', min_length=1, max_length=500)
    content_types: list[str] = Field(None, description='Filter by content types')
    languages: list[str] = Field(None, description='Filter by programming languages')
    chunk_types: list[str] = Field(None, description='Filter by chunk types')
    archive_ids: list[str] = Field(None, description='Search within specific archives')
    limit: int = Field(None, description='Maximum number of results', ge=1.0, le=50.0)
    similarity_threshold: float = Field(None, description='Minimum similarity threshold', ge=0.0, le=1.0)



class ChunkRevectorizationRequestRequest(BaseModel):
    """
    Chunk re-vectorization request serializer.

    Request model (no read-only fields).
    """

    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid",
        frozen=False,
    )

    chunk_ids: list[str] = Field(description='List of chunk IDs to re-vectorize')
    force: bool = Field(None, description='Force re-vectorization even if already vectorized')



class ArchiveItemChunkRequest(BaseModel):
    """
    Archive item chunk serializer.

    Request model (no read-only fields).
    """

    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid",
        frozen=False,
    )

    content: str = Field(description='Chunk text content', min_length=1)
    chunk_index: int = Field(description='Sequential chunk number within item', ge=0.0, le=2147483647.0)
    chunk_type: ArchiveItemChunkRequestChunkType = Field(None, description='Type of content in chunk\n\n* `text` - Text\n* `code` - Code\n* `heading` - Heading\n* `metadata` - Metadata\n* `table` - Table\n* `list` - List')



class PatchedArchiveItemChunkRequest(BaseModel):
    """
    Archive item chunk serializer.

    Request model (no read-only fields).
    """

    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid",
        frozen=False,
    )

    content: str = Field(None, description='Chunk text content', min_length=1)
    chunk_index: int = Field(None, description='Sequential chunk number within item', ge=0.0, le=2147483647.0)
    chunk_type: PatchedArchiveItemChunkRequestChunkType = Field(None, description='Type of content in chunk\n\n* `text` - Text\n* `code` - Code\n* `heading` - Heading\n* `metadata` - Metadata\n* `table` - Table\n* `list` - List')



class ArchiveItemRequest(BaseModel):
    """
    Archive item serializer.

    Request model (no read-only fields).
    """

    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid",
        frozen=False,
    )

    relative_path: str = Field(description='Path within archive', min_length=1, max_length=1024)
    item_name: str = Field(description='Item name', min_length=1, max_length=255)
    item_type: str = Field(description='MIME type', min_length=1, max_length=100)
    file_size: int = Field(None, description='Item size in bytes', ge=0.0, le=2147483647.0)



class PatchedArchiveItemRequest(BaseModel):
    """
    Archive item serializer.

    Request model (no read-only fields).
    """

    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid",
        frozen=False,
    )

    relative_path: str = Field(None, description='Path within archive', min_length=1, max_length=1024)
    item_name: str = Field(None, description='Item name', min_length=1, max_length=255)
    item_type: str = Field(None, description='MIME type', min_length=1, max_length=100)
    file_size: int = Field(None, description='Item size in bytes', ge=0.0, le=2147483647.0)



