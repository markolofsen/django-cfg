import * as Enums from "../enums";

/**
 * 
 * Response model (includes read-only fields).
 */
export interface PaginatedChatResponseList {
  /** Total number of items across all pages */
  count: number;
  /** Current page number (1-based) */
  page: number;
  /** Total number of pages */
  pages: number;
  /** Number of items per page */
  page_size: number;
  /** Whether there is a next page */
  has_next: boolean;
  /** Whether there is a previous page */
  has_previous: boolean;
  /** Next page number (null if no next page) */
  next_page?: number | null;
  /** Previous page number (null if no previous page) */
  previous_page?: number | null;
  /** Array of items for current page */
  results: Array<ChatResponse>;
}

/**
 * Chat response serializer.
 * 
 * Request model (no read-only fields).
 */
export interface ChatResponseRequest {
  message_id: string;
  content: string;
  tokens_used: number;
  cost_usd: number;
  processing_time_ms: number;
  model_used: string;
  sources?: Array<ChatSourceRequest> | null;
}

/**
 * Chat response serializer.
 * 
 * Response model (includes read-only fields).
 */
export interface ChatResponse {
  message_id: string;
  content: string;
  tokens_used: number;
  cost_usd: number;
  processing_time_ms: number;
  model_used: string;
  sources?: Array<ChatSource> | null;
}

/**
 * Chat response serializer.
 * 
 * Request model (no read-only fields).
 */
export interface PatchedChatResponseRequest {
  message_id?: string;
  content?: string;
  tokens_used?: number;
  cost_usd?: number;
  processing_time_ms?: number;
  model_used?: string;
  sources?: Array<ChatSourceRequest> | null;
}

/**
 * Chat history response serializer.
 * 
 * Response model (includes read-only fields).
 */
export interface ChatHistory {
  session_id: string;
  messages: Array<ChatMessage>;
  total_messages: number;
}

/**
 * Chat query request serializer.
 * 
 * Request model (no read-only fields).
 */
export interface ChatQueryRequest {
  /** Chat session ID (creates new if not provided) */
  session_id?: string | null;
  /** User query */
  query: string;
  /** Maximum response tokens */
  max_tokens?: number;
  /** Include source documents in response */
  include_sources?: boolean;
}

/**
 * 
 * Response model (includes read-only fields).
 */
export interface PaginatedDocumentList {
  /** Total number of items across all pages */
  count: number;
  /** Current page number (1-based) */
  page: number;
  /** Total number of pages */
  pages: number;
  /** Number of items per page */
  page_size: number;
  /** Whether there is a next page */
  has_next: boolean;
  /** Whether there is a previous page */
  has_previous: boolean;
  /** Next page number (null if no next page) */
  next_page?: number | null;
  /** Previous page number (null if no previous page) */
  previous_page?: number | null;
  /** Array of items for current page */
  results: Array<Document>;
}

/**
 * Document creation request serializer.
 * 
 * Request model (no read-only fields).
 */
export interface DocumentCreateRequest {
  /** Document title */
  title: string;
  /** Document content */
  content: string;
  /** MIME type */
  file_type?: string;
  /** Additional metadata */
  metadata?: string;
}

/**
 * Document response serializer.
 * 
 * Response model (includes read-only fields).
 */
export interface Document {
  id: string;
  /** Document title */
  title: string;
  /** MIME type of original file */
  file_type?: string;
  /** Original file size in bytes */
  file_size?: number;
  processing_status: string;
  chunks_count: number;
  total_tokens: number;
  total_cost_usd: number;
  created_at: string;
  updated_at: string;
  processing_started_at: string;
  processing_completed_at: string;
  processing_error: string;
  /** Additional document metadata */
  metadata?: string | null;
}

/**
 * Document response serializer.
 * 
 * Request model (no read-only fields).
 */
export interface DocumentRequest {
  /** Document title */
  title: string;
  /** MIME type of original file */
  file_type?: string;
  /** Original file size in bytes */
  file_size?: number;
  /** Additional document metadata */
  metadata?: string | null;
}

/**
 * Document response serializer.
 * 
 * Request model (no read-only fields).
 */
export interface PatchedDocumentRequest {
  /** Document title */
  title?: string;
  /** MIME type of original file */
  file_type?: string;
  /** Original file size in bytes */
  file_size?: number;
  /** Additional document metadata */
  metadata?: string | null;
}

/**
 * Document processing status serializer.
 * 
 * Response model (includes read-only fields).
 */
export interface DocumentProcessingStatus {
  id: string;
  status: string;
  progress: string;
  error?: string | null;
  processing_time_seconds?: number | null;
}

/**
 * Document processing statistics serializer.
 * 
 * Response model (includes read-only fields).
 */
export interface DocumentStats {
  total_documents: number;
  completed_documents: number;
  processing_success_rate: number;
  total_chunks: number;
  total_tokens: number;
  total_cost_usd: number;
  avg_processing_time_seconds: number;
}

/**
 * 
 * Response model (includes read-only fields).
 */
export interface PaginatedChatSessionList {
  /** Total number of items across all pages */
  count: number;
  /** Current page number (1-based) */
  page: number;
  /** Total number of pages */
  pages: number;
  /** Number of items per page */
  page_size: number;
  /** Whether there is a next page */
  has_next: boolean;
  /** Whether there is a previous page */
  has_previous: boolean;
  /** Next page number (null if no next page) */
  next_page?: number | null;
  /** Previous page number (null if no previous page) */
  previous_page?: number | null;
  /** Array of items for current page */
  results: Array<ChatSession>;
}

/**
 * Chat session creation request serializer.
 * 
 * Request model (no read-only fields).
 */
export interface ChatSessionCreateRequest {
  /** Session title */
  title?: string;
  /** LLM model to use */
  model_name?: string;
  /** Response creativity */
  temperature?: number;
  /** Maximum context chunks */
  max_context_chunks?: number;
}

/**
 * Chat session response serializer.
 * 
 * Response model (includes read-only fields).
 */
export interface ChatSession {
  id: string;
  /** Session title (auto-generated if empty) */
  title?: string;
  /** Whether session accepts new messages */
  is_active?: boolean;
  messages_count?: number;
  total_tokens_used?: number;
  total_cost_usd: number;
  /** LLM model used for this session */
  model_name?: string;
  /** Temperature setting for LLM */
  temperature?: number;
  /** Maximum chunks to include in context */
  max_context_chunks?: number;
  created_at: string;
  updated_at: string;
}

/**
 * Chat session response serializer.
 * 
 * Request model (no read-only fields).
 */
export interface ChatSessionRequest {
  /** Session title (auto-generated if empty) */
  title?: string;
  /** Whether session accepts new messages */
  is_active?: boolean;
  messages_count?: number;
  total_tokens_used?: number;
  /** LLM model used for this session */
  model_name?: string;
  /** Temperature setting for LLM */
  temperature?: number;
  /** Maximum chunks to include in context */
  max_context_chunks?: number;
}

/**
 * Chat session response serializer.
 * 
 * Request model (no read-only fields).
 */
export interface PatchedChatSessionRequest {
  /** Session title (auto-generated if empty) */
  title?: string;
  /** Whether session accepts new messages */
  is_active?: boolean;
  messages_count?: number;
  total_tokens_used?: number;
  /** LLM model used for this session */
  model_name?: string;
  /** Temperature setting for LLM */
  temperature?: number;
  /** Maximum chunks to include in context */
  max_context_chunks?: number;
}

/**
 * 
 * Response model (includes read-only fields).
 */
export interface PaginatedPublicCategoryList {
  /** Total number of items across all pages */
  count: number;
  /** Current page number (1-based) */
  page: number;
  /** Total number of pages */
  pages: number;
  /** Number of items per page */
  page_size: number;
  /** Whether there is a next page */
  has_next: boolean;
  /** Whether there is a previous page */
  has_previous: boolean;
  /** Next page number (null if no next page) */
  next_page?: number | null;
  /** Previous page number (null if no previous page) */
  previous_page?: number | null;
  /** Array of items for current page */
  results: Array<PublicCategory>;
}

/**
 * Public category serializer.
 * 
 * Response model (includes read-only fields).
 */
export interface PublicCategory {
  id: string;
  /** Category name */
  name: string;
  /** Category description */
  description?: string;
}

/**
 * 
 * Response model (includes read-only fields).
 */
export interface PaginatedPublicDocumentListList {
  /** Total number of items across all pages */
  count: number;
  /** Current page number (1-based) */
  page: number;
  /** Total number of pages */
  pages: number;
  /** Number of items per page */
  page_size: number;
  /** Whether there is a next page */
  has_next: boolean;
  /** Whether there is a previous page */
  has_previous: boolean;
  /** Next page number (null if no next page) */
  next_page?: number | null;
  /** Previous page number (null if no previous page) */
  previous_page?: number | null;
  /** Array of items for current page */
  results: Array<PublicDocumentList>;
}

/**
 * Public document detail serializer - only essential data for clients.
 * 
 * Response model (includes read-only fields).
 */
export interface PublicDocument {
  id: string;
  /** Document title */
  title: string;
  /** Full document content */
  content: string;
  category: PublicCategory;
  created_at: string;
  updated_at: string;
}

/**
 * 
 * Response model (includes read-only fields).
 */
export interface PaginatedDocumentArchiveListList {
  /** Total number of items across all pages */
  count: number;
  /** Current page number (1-based) */
  page: number;
  /** Total number of pages */
  pages: number;
  /** Number of items per page */
  page_size: number;
  /** Whether there is a next page */
  has_next: boolean;
  /** Whether there is a previous page */
  has_previous: boolean;
  /** Next page number (null if no next page) */
  next_page?: number | null;
  /** Previous page number (null if no previous page) */
  previous_page?: number | null;
  /** Array of items for current page */
  results: Array<DocumentArchiveList>;
}

/**
 * Archive processing result serializer.
 * 
 * Response model (includes read-only fields).
 */
export interface ArchiveProcessingResult {
  archive_id: string;
  status: string;
  processing_time_ms: number;
  items_processed: number;
  chunks_created: number;
  vectorized_chunks: number;
  total_cost_usd: number;
  error_message: string;
}

/**
 * Detailed archive serializer with items.
 * 
 * Response model (includes read-only fields).
 */
export interface DocumentArchiveDetail {
  id: string;
  /** Archive title */
  title: string;
  /** Archive description */
  description?: string;
  categories: Array<DocumentCategory>;
  /** Whether this archive is publicly accessible */
  is_public?: boolean;
  /** Uploaded archive file */
  archive_file: string;
  /** Original uploaded filename */
  original_filename: string;
  /** Archive size in bytes */
  file_size: number;
  /** Archive format

  * `zip` - ZIP
  * `tar` - TAR
  * `tar.gz` - TAR GZ
  * `tar.bz2` - TAR BZ2 */
  archive_type: Enums.DocumentArchiveDetailArchiveType;
  /** * `pending` - Pending
  * `processing` - Processing
  * `completed` - Completed
  * `failed` - Failed
  * `cancelled` - Cancelled */
  processing_status: Enums.DocumentArchiveDetailProcessingStatus;
  /** When processing completed */
  processed_at?: string | null;
  /** Processing time in milliseconds */
  processing_duration_ms: number;
  /** Error message if processing failed */
  processing_error: string;
  /** Total items in archive */
  total_items: number;
  /** Successfully processed items */
  processed_items: number;
  /** Total chunks created */
  total_chunks: number;
  /** Chunks with embeddings */
  vectorized_chunks: number;
  /** Total tokens across all chunks */
  total_tokens: number;
  /** Total processing cost in USD */
  total_cost_usd: number;
  /** Calculate processing progress as percentage. */
  processing_progress: number;
  /** Calculate vectorization progress as percentage. */
  vectorization_progress: number;
  /** Check if archive processing is completed. */
  is_processed: boolean;
  created_at: string;
  updated_at: string;
  items: Array<ArchiveItem>;
  /** Get hierarchical file tree. */
  file_tree: Record<string, string>;
  /** Additional archive metadata */
  metadata?: string | null;
}

/**
 * Document archive serializer.
 * 
 * Request model (no read-only fields).
 */
export interface DocumentArchiveRequest {
  /** Archive title */
  title: string;
  /** Archive description */
  description?: string;
  /** Whether this archive is publicly accessible */
  is_public?: boolean;
}

/**
 * Document archive serializer.
 * 
 * Response model (includes read-only fields).
 */
export interface DocumentArchive {
  id: string;
  /** Archive title */
  title: string;
  /** Archive description */
  description?: string;
  categories: Array<DocumentCategory>;
  /** Whether this archive is publicly accessible */
  is_public?: boolean;
  /** Uploaded archive file */
  archive_file: string;
  /** Original uploaded filename */
  original_filename: string;
  /** Archive size in bytes */
  file_size: number;
  /** Archive format

  * `zip` - ZIP
  * `tar` - TAR
  * `tar.gz` - TAR GZ
  * `tar.bz2` - TAR BZ2 */
  archive_type: Enums.DocumentArchiveArchiveType;
  /** * `pending` - Pending
  * `processing` - Processing
  * `completed` - Completed
  * `failed` - Failed
  * `cancelled` - Cancelled */
  processing_status: Enums.DocumentArchiveProcessingStatus;
  /** When processing completed */
  processed_at?: string | null;
  /** Processing time in milliseconds */
  processing_duration_ms: number;
  /** Error message if processing failed */
  processing_error: string;
  /** Total items in archive */
  total_items: number;
  /** Successfully processed items */
  processed_items: number;
  /** Total chunks created */
  total_chunks: number;
  /** Chunks with embeddings */
  vectorized_chunks: number;
  /** Total tokens across all chunks */
  total_tokens: number;
  /** Total processing cost in USD */
  total_cost_usd: number;
  /** Calculate processing progress as percentage. */
  processing_progress: number;
  /** Calculate vectorization progress as percentage. */
  vectorization_progress: number;
  /** Check if archive processing is completed. */
  is_processed: boolean;
  created_at: string;
  updated_at: string;
}

/**
 * Document archive serializer.
 * 
 * Request model (no read-only fields).
 */
export interface PatchedDocumentArchiveRequest {
  /** Archive title */
  title?: string;
  /** Archive description */
  description?: string;
  /** Whether this archive is publicly accessible */
  is_public?: boolean;
}

/**
 * 
 * Response model (includes read-only fields).
 */
export interface PaginatedArchiveItemList {
  /** Total number of items across all pages */
  count: number;
  /** Current page number (1-based) */
  page: number;
  /** Total number of pages */
  pages: number;
  /** Number of items per page */
  page_size: number;
  /** Whether there is a next page */
  has_next: boolean;
  /** Whether there is a previous page */
  has_previous: boolean;
  /** Next page number (null if no next page) */
  next_page?: number | null;
  /** Previous page number (null if no previous page) */
  previous_page?: number | null;
  /** Array of items for current page */
  results: Array<ArchiveItem>;
}

/**
 * Archive search request serializer.
 * 
 * Request model (no read-only fields).
 */
export interface ArchiveSearchRequestRequest {
  /** Search query */
  query: string;
  /** Filter by content types */
  content_types?: Array<string>;
  /** Filter by programming languages */
  languages?: Array<string>;
  /** Filter by chunk types */
  chunk_types?: Array<string>;
  /** Search within specific archives */
  archive_ids?: Array<string>;
  /** Maximum number of results */
  limit?: number;
  /** Minimum similarity threshold */
  similarity_threshold?: number;
}

/**
 * 
 * Response model (includes read-only fields).
 */
export interface PaginatedArchiveSearchResultList {
  /** Total number of items across all pages */
  count: number;
  /** Current page number (1-based) */
  page: number;
  /** Total number of pages */
  pages: number;
  /** Number of items per page */
  page_size: number;
  /** Whether there is a next page */
  has_next: boolean;
  /** Whether there is a previous page */
  has_previous: boolean;
  /** Next page number (null if no next page) */
  next_page?: number | null;
  /** Previous page number (null if no previous page) */
  previous_page?: number | null;
  /** Array of items for current page */
  results: Array<ArchiveSearchResult>;
}

/**
 * Chunk re-vectorization request serializer.
 * 
 * Request model (no read-only fields).
 */
export interface ChunkRevectorizationRequestRequest {
  /** List of chunk IDs to re-vectorize */
  chunk_ids: Array<string>;
  /** Force re-vectorization even if already vectorized */
  force?: boolean;
}

/**
 * Vectorization result serializer.
 * 
 * Response model (includes read-only fields).
 */
export interface VectorizationResult {
  vectorized_count: number;
  failed_count: number;
  total_tokens: number;
  total_cost: number;
  success_rate: number;
  errors: Array<string>;
}

/**
 * Archive statistics serializer.
 * 
 * Response model (includes read-only fields).
 */
export interface ArchiveStatistics {
  total_archives: number;
  processed_archives: number;
  failed_archives: number;
  total_items: number;
  total_chunks: number;
  total_tokens: number;
  total_cost: number;
  avg_processing_time: number;
  avg_items_per_archive: number;
  avg_chunks_per_archive: number;
}

/**
 * Vectorization statistics serializer.
 * 
 * Response model (includes read-only fields).
 */
export interface VectorizationStatistics {
  total_chunks: number;
  vectorized_chunks: number;
  pending_chunks: number;
  vectorization_rate: number;
  total_tokens: number;
  total_cost: number;
  avg_tokens_per_chunk: number;
  avg_cost_per_chunk: number;
}

/**
 * 
 * Response model (includes read-only fields).
 */
export interface PaginatedArchiveItemChunkList {
  /** Total number of items across all pages */
  count: number;
  /** Current page number (1-based) */
  page: number;
  /** Total number of pages */
  pages: number;
  /** Number of items per page */
  page_size: number;
  /** Whether there is a next page */
  has_next: boolean;
  /** Whether there is a previous page */
  has_previous: boolean;
  /** Next page number (null if no next page) */
  next_page?: number | null;
  /** Previous page number (null if no previous page) */
  previous_page?: number | null;
  /** Array of items for current page */
  results: Array<ArchiveItemChunk>;
}

/**
 * Archive item chunk serializer.
 * 
 * Request model (no read-only fields).
 */
export interface ArchiveItemChunkRequest {
  /** Chunk text content */
  content: string;
  /** Sequential chunk number within item */
  chunk_index: number;
  /** Type of content in chunk

  * `text` - Text
  * `code` - Code
  * `heading` - Heading
  * `metadata` - Metadata
  * `table` - Table
  * `list` - List */
  chunk_type?: Enums.ArchiveItemChunkRequestChunkType;
}

/**
 * Archive item chunk serializer.
 * 
 * Response model (includes read-only fields).
 */
export interface ArchiveItemChunk {
  id: string;
  /** Chunk text content */
  content: string;
  /** Sequential chunk number within item */
  chunk_index: number;
  /** Type of content in chunk

  * `text` - Text
  * `code` - Code
  * `heading` - Heading
  * `metadata` - Metadata
  * `table` - Table
  * `list` - List */
  chunk_type?: Enums.ArchiveItemChunkChunkType;
  /** Number of tokens in chunk */
  token_count: number;
  /** Number of characters in chunk */
  character_count: number;
  /** Model used for embedding generation */
  embedding_model: string;
  /** Cost in USD for embedding generation */
  embedding_cost: number;
  /** Get context summary for display. */
  context_summary: Record<string, string>;
  created_at: string;
}

/**
 * Detailed chunk serializer with full context.
 * 
 * Response model (includes read-only fields).
 */
export interface ArchiveItemChunkDetail {
  id: string;
  /** Chunk text content */
  content: string;
  /** Sequential chunk number within item */
  chunk_index: number;
  /** Type of content in chunk

  * `text` - Text
  * `code` - Code
  * `heading` - Heading
  * `metadata` - Metadata
  * `table` - Table
  * `list` - List */
  chunk_type?: Enums.ArchiveItemChunkDetailChunkType;
  /** Number of tokens in chunk */
  token_count: number;
  /** Number of characters in chunk */
  character_count: number;
  /** Model used for embedding generation */
  embedding_model: string;
  /** Cost in USD for embedding generation */
  embedding_cost: number;
  /** Get context summary for display. */
  context_summary: Record<string, string>;
  created_at: string;
  context_metadata: string;
}

/**
 * Archive item chunk serializer.
 * 
 * Request model (no read-only fields).
 */
export interface PatchedArchiveItemChunkRequest {
  /** Chunk text content */
  content?: string;
  /** Sequential chunk number within item */
  chunk_index?: number;
  /** Type of content in chunk

  * `text` - Text
  * `code` - Code
  * `heading` - Heading
  * `metadata` - Metadata
  * `table` - Table
  * `list` - List */
  chunk_type?: Enums.PatchedArchiveItemChunkRequestChunkType;
}

/**
 * Archive item serializer.
 * 
 * Request model (no read-only fields).
 */
export interface ArchiveItemRequest {
  /** Path within archive */
  relative_path: string;
  /** Item name */
  item_name: string;
  /** MIME type */
  item_type: string;
  /** Item size in bytes */
  file_size?: number;
}

/**
 * Archive item serializer.
 * 
 * Response model (includes read-only fields).
 */
export interface ArchiveItem {
  id: string;
  /** Path within archive */
  relative_path: string;
  /** Item name */
  item_name: string;
  /** MIME type */
  item_type: string;
  /** Content classification

  * `document` - Document
  * `code` - Code
  * `image` - Image
  * `data` - Data
  * `archive` - Archive
  * `unknown` - Unknown */
  content_type: Enums.ArchiveItemContentType;
  /** Item size in bytes */
  file_size?: number;
  /** Whether item can be processed for chunks */
  is_processable: boolean;
  /** Programming language or document language */
  language: string;
  /** Character encoding */
  encoding: string;
  /** Number of chunks created */
  chunks_count: number;
  /** Total tokens in all chunks */
  total_tokens: number;
  /** Processing cost for this item */
  processing_cost: number;
  created_at: string;
  updated_at: string;
}

/**
 * Detailed archive item serializer with content.
 * 
 * Response model (includes read-only fields).
 */
export interface ArchiveItemDetail {
  id: string;
  /** Path within archive */
  relative_path: string;
  /** Item name */
  item_name: string;
  /** MIME type */
  item_type: string;
  /** Content classification

  * `document` - Document
  * `code` - Code
  * `image` - Image
  * `data` - Data
  * `archive` - Archive
  * `unknown` - Unknown */
  content_type: Enums.ArchiveItemDetailContentType;
  /** Item size in bytes */
  file_size?: number;
  /** Whether item can be processed for chunks */
  is_processable: boolean;
  /** Programming language or document language */
  language: string;
  /** Character encoding */
  encoding: string;
  /** Number of chunks created */
  chunks_count: number;
  /** Total tokens in all chunks */
  total_tokens: number;
  /** Processing cost for this item */
  processing_cost: number;
  created_at: string;
  updated_at: string;
  raw_content: string;
  metadata: string;
}

/**
 * Archive item serializer.
 * 
 * Request model (no read-only fields).
 */
export interface PatchedArchiveItemRequest {
  /** Path within archive */
  relative_path?: string;
  /** Item name */
  item_name?: string;
  /** MIME type */
  item_type?: string;
  /** Item size in bytes */
  file_size?: number;
}

/**
 * Chat source document information serializer.
 * 
 * Request model (no read-only fields).
 */
export interface ChatSourceRequest {
  document_title: string;
  chunk_content: string;
  similarity: number;
}

/**
 * Chat source document information serializer.
 * 
 * Response model (includes read-only fields).
 */
export interface ChatSource {
  document_title: string;
  chunk_content: string;
  similarity: number;
}

/**
 * Chat message response serializer.
 * 
 * Response model (includes read-only fields).
 */
export interface ChatMessage {
  id: string;
  /** Message sender role

  * `user` - User
  * `assistant` - Assistant
  * `system` - System */
  role: Enums.ChatMessageRole;
  /** Message content */
  content: string;
  /** Tokens used for this message */
  tokens_used?: number;
  cost_usd: number;
  /** Processing time in milliseconds */
  processing_time_ms?: number;
  created_at: string;
  /** IDs of chunks used for context */
  context_chunks?: string;
}

/**
 * Public document list serializer - minimal fields for listing.
 * 
 * Response model (includes read-only fields).
 */
export interface PublicDocumentList {
  id: string;
  /** Document title */
  title: string;
  category: PublicCategory;
  created_at: string;
  updated_at: string;
}

/**
 * Simplified archive serializer for list views.
 * 
 * Response model (includes read-only fields).
 */
export interface DocumentArchiveList {
  id: string;
  /** Archive title */
  title: string;
  /** Archive description */
  description: string;
  categories: Array<DocumentCategory>;
  /** Whether this archive is publicly accessible */
  is_public: boolean;
  /** Original uploaded filename */
  original_filename: string;
  /** Archive size in bytes */
  file_size: number;
  /** Archive format

  * `zip` - ZIP
  * `tar` - TAR
  * `tar.gz` - TAR GZ
  * `tar.bz2` - TAR BZ2 */
  archive_type: Enums.DocumentArchiveListArchiveType;
  /** * `pending` - Pending
  * `processing` - Processing
  * `completed` - Completed
  * `failed` - Failed
  * `cancelled` - Cancelled */
  processing_status: Enums.DocumentArchiveListProcessingStatus;
  /** When processing completed */
  processed_at?: string | null;
  /** Total items in archive */
  total_items: number;
  /** Total chunks created */
  total_chunks: number;
  /** Total processing cost in USD */
  total_cost_usd: number;
  /** Calculate processing progress as percentage. */
  processing_progress: number;
  created_at: string;
}

/**
 * Document category serializer.
 * 
 * Response model (includes read-only fields).
 */
export interface DocumentCategory {
  id: string;
  /** Category name */
  name: string;
  /** Category description */
  description?: string;
  /** Whether documents in this category are publicly accessible */
  is_public?: boolean;
  created_at: string;
}

/**
 * Archive search result serializer.
 * 
 * Response model (includes read-only fields).
 */
export interface ArchiveSearchResult {
  chunk: ArchiveItemChunk;
  similarity_score: number;
  context_summary: Record<string, string>;
  archive_info: Record<string, string>;
  item_info: Record<string, string>;
}

