/**
 * Type definitions for django-cfg API
 * Auto-generated from OpenAPI schema
 * @module types
 */

// This file contains JSDoc type definitions generated from the OpenAPI schema
// These types can be used for better IDE support and documentation

/**
 * @typedef {Object} APIResponse * @description Standard API response serializer. * @property {boolean} success - Operation success status * @property {string} [message] - Success message * @property {string} [error] - Error message * @property {Record<string, any>} [data] - Response data */

/**
 * @typedef {Object} APIResponseRequest * @description Standard API response serializer. * @property {boolean} success - Operation success status * @property {string} [message] - Success message * @property {string} [error] - Error message * @property {Record<string, any>} [data] - Response data */

/**
 * @typedef {Object} ArchiveItem * @description Archive item serializer. * @property {string} id * @property {string} relative_path - Path within archive * @property {string} item_name - Item name * @property {string} item_type - MIME type * @property {"document" | "code" | "image" | "data" | "archive" | "unknown"} content_type - Content classification

* `document` - Document
* `code` - Code
* `image` - Image
* `data` - Data
* `archive` - Archive
* `unknown` - Unknown * @property {number} [file_size] - Item size in bytes * @property {boolean} is_processable - Whether item can be processed for chunks * @property {string} language - Programming language or document language * @property {string} encoding - Character encoding * @property {number} chunks_count - Number of chunks created * @property {number} total_tokens - Total tokens in all chunks * @property {number} processing_cost - Processing cost for this item * @property {string} created_at * @property {string} updated_at */

/**
 * @typedef {Object} ArchiveItemChunk * @description Archive item chunk serializer. * @property {string} id * @property {string} content - Chunk text content * @property {number} chunk_index - Sequential chunk number within item * @property {"text" | "code" | "heading" | "metadata" | "table" | "list"} [chunk_type] - Type of content in chunk

* `text` - Text
* `code` - Code
* `heading` - Heading
* `metadata` - Metadata
* `table` - Table
* `list` - List * @property {number} token_count - Number of tokens in chunk * @property {number} character_count - Number of characters in chunk * @property {string} embedding_model - Model used for embedding generation * @property {number} embedding_cost - Cost in USD for embedding generation * @property {Record<string, any>} context_summary - Get context summary for display. * @property {string} created_at */

/**
 * @typedef {Object} ArchiveItemChunkDetail * @description Detailed chunk serializer with full context. * @property {string} id * @property {string} content - Chunk text content * @property {number} chunk_index - Sequential chunk number within item * @property {"text" | "code" | "heading" | "metadata" | "table" | "list"} [chunk_type] - Type of content in chunk

* `text` - Text
* `code` - Code
* `heading` - Heading
* `metadata` - Metadata
* `table` - Table
* `list` - List * @property {number} token_count - Number of tokens in chunk * @property {number} character_count - Number of characters in chunk * @property {string} embedding_model - Model used for embedding generation * @property {number} embedding_cost - Cost in USD for embedding generation * @property {Record<string, any>} context_summary - Get context summary for display. * @property {string} created_at * @property {any} context_metadata */

/**
 * @typedef {Object} ArchiveItemChunkRequest * @description Archive item chunk serializer. * @property {string} content - Chunk text content * @property {number} chunk_index - Sequential chunk number within item * @property {"text" | "code" | "heading" | "metadata" | "table" | "list"} [chunk_type] - Type of content in chunk

* `text` - Text
* `code` - Code
* `heading` - Heading
* `metadata` - Metadata
* `table` - Table
* `list` - List */

/**
 * @typedef {Object} ArchiveItemDetail * @description Detailed archive item serializer with content. * @property {string} id * @property {string} relative_path - Path within archive * @property {string} item_name - Item name * @property {string} item_type - MIME type * @property {"document" | "code" | "image" | "data" | "archive" | "unknown"} content_type - Content classification

* `document` - Document
* `code` - Code
* `image` - Image
* `data` - Data
* `archive` - Archive
* `unknown` - Unknown * @property {number} [file_size] - Item size in bytes * @property {boolean} is_processable - Whether item can be processed for chunks * @property {string} language - Programming language or document language * @property {string} encoding - Character encoding * @property {number} chunks_count - Number of chunks created * @property {number} total_tokens - Total tokens in all chunks * @property {number} processing_cost - Processing cost for this item * @property {string} created_at * @property {string} updated_at * @property {string} raw_content * @property {any} metadata */

/**
 * @typedef {Object} ArchiveItemRequest * @description Archive item serializer. * @property {string} relative_path - Path within archive * @property {string} item_name - Item name * @property {string} item_type - MIME type * @property {number} [file_size] - Item size in bytes */

/**
 * @typedef {Object} ArchiveProcessingResult * @description Archive processing result serializer. * @property {string} archive_id * @property {string} status * @property {number} processing_time_ms * @property {number} items_processed * @property {number} chunks_created * @property {number} vectorized_chunks * @property {number} total_cost_usd * @property {string} error_message */

/**
 * @typedef {Object} ArchiveSearchRequestRequest * @description Archive search request serializer. * @property {string} query - Search query * @property {"document" | "code" | "image" | "data" | "archive" | "unknown"[]} [content_types] - Filter by content types * @property {string[]} [languages] - Filter by programming languages * @property {"text" | "code" | "heading" | "metadata" | "table" | "list"[]} [chunk_types] - Filter by chunk types * @property {string[]} [archive_ids] - Search within specific archives * @property {number} [limit] - Maximum number of results * @property {number} [similarity_threshold] - Minimum similarity threshold */

/**
 * @typedef {Object} ArchiveSearchResult * @description Archive search result serializer. * @property {any} chunk * @property {number} similarity_score * @property {Record<string, any>} context_summary * @property {Record<string, any>} archive_info * @property {Record<string, any>} item_info */

/**
 * @typedef {Object} ArchiveStatistics * @description Archive statistics serializer. * @property {number} total_archives * @property {number} processed_archives * @property {number} failed_archives * @property {number} total_items * @property {number} total_chunks * @property {number} total_tokens * @property {number} total_cost * @property {number} avg_processing_time * @property {number} avg_items_per_archive * @property {number} avg_chunks_per_archive */

/**
 * @typedef {Object} Balance * @description User balance serializer. * @property {string} balance_usd - Current balance in USD * @property {string} balance_display * @property {string} total_deposited - Total amount deposited (lifetime) * @property {string} total_withdrawn - Total amount withdrawn (lifetime) * @property {string} last_transaction_at - When the last transaction occurred */

/**
 * @typedef {Object} BulkEmailRequest * @description Simple serializer for bulk email. * @property {string[]} recipients * @property {string} subject * @property {string} email_title * @property {string} main_text * @property {string} [main_html_content] * @property {string} [button_text] * @property {string} [button_url] * @property {string} [secondary_text] */

/**
 * @typedef {Object} BulkEmailResponse * @description Response for bulk email sending. * @property {boolean} success * @property {number} sent_count * @property {number} failed_count * @property {number} total_recipients * @property {string} [error] */

/**
 * @typedef {Object} CentrifugoChannelInfo * @description Information about a single channel. * @property {number} num_clients - Number of connected clients in channel */

/**
 * @typedef {Object} CentrifugoChannelsRequestRequest * @description Request to list active channels. * @property {any} [pattern] - Pattern to filter channels (e.g., 'user:*') */

/**
 * @typedef {Object} CentrifugoChannelsResponse * @description List of active channels response. * @property {any} [error] - Error if any * @property {any} [result] - Result data */

/**
 * @typedef {Object} CentrifugoChannelsResult * @description Channels result wrapper. * @property {Record<string, CentrifugoChannelInfo>} channels - Map of channel names to channel info */

/**
 * @typedef {Object} CentrifugoClientInfo * @description Information about connected client. * @property {string} user - User ID * @property {string} client - Client UUID * @property {any} [conn_info] - Connection metadata * @property {any} [chan_info] - Channel-specific metadata */

/**
 * @typedef {Object} CentrifugoError * @description Centrifugo API error structure. * @property {number} [code] - Error code (0 = no error) * @property {string} [message] - Error message */

/**
 * @typedef {Object} CentrifugoHistoryRequestRequest * @description Request to get channel history. * @property {string} channel - Channel name * @property {any} [limit] - Maximum number of messages to return * @property {any} [since] - Stream position to get messages since * @property {any} [reverse] - Reverse message order (newest first) */

/**
 * @typedef {Object} CentrifugoHistoryResponse * @description Channel history response. * @property {any} [error] - Error if any * @property {any} [result] - Result data */

/**
 * @typedef {Object} CentrifugoHistoryResult * @description History result wrapper. * @property {CentrifugoPublication[]} publications - List of publications * @property {string} epoch - Current stream epoch * @property {number} offset - Latest stream offset */

/**
 * @typedef {Object} CentrifugoInfoResponse * @description Server info response. * @property {any} [error] - Error if any * @property {any} [result] - Result data */

/**
 * @typedef {Object} CentrifugoInfoResult * @description Info result wrapper. * @property {CentrifugoNodeInfo[]} nodes - List of Centrifugo nodes */

/**
 * @typedef {Object} CentrifugoMetrics * @description Server metrics. * @property {number} interval - Metrics collection interval * @property {Record<string, number>} items - Metric name to value mapping */

/**
 * @typedef {Object} CentrifugoNodeInfo * @description Information about a single Centrifugo node. * @property {string} uid - Unique node identifier * @property {string} name - Node name * @property {string} version - Centrifugo version * @property {number} num_clients - Number of connected clients * @property {number} num_users - Number of unique users * @property {number} num_channels - Number of active channels * @property {number} uptime - Node uptime in seconds * @property {number} num_subs - Total number of subscriptions * @property {any} [metrics] - Server metrics * @property {any} [process] - Process information */

/**
 * @typedef {Object} CentrifugoPresenceRequestRequest * @description Request to get channel presence. * @property {string} channel - Channel name */

/**
 * @typedef {Object} CentrifugoPresenceResponse * @description Channel presence response. * @property {any} [error] - Error if any * @property {any} [result] - Result data */

/**
 * @typedef {Object} CentrifugoPresenceResult * @description Presence result wrapper. * @property {Record<string, CentrifugoClientInfo>} presence - Map of client IDs to client info */

/**
 * @typedef {Object} CentrifugoPresenceStatsRequestRequest * @description Request to get channel presence statistics. * @property {string} channel - Channel name */

/**
 * @typedef {Object} CentrifugoPresenceStatsResponse * @description Channel presence stats response. * @property {any} [error] - Error if any * @property {any} [result] - Result data */

/**
 * @typedef {Object} CentrifugoPresenceStatsResult * @description Presence stats result. * @property {number} num_clients - Number of connected clients * @property {number} num_users - Number of unique users */

/**
 * @typedef {Object} CentrifugoProcess * @description Process information. * @property {number} cpu - CPU usage percentage * @property {number} rss - Resident set size in bytes */

/**
 * @typedef {Object} CentrifugoPublication * @description Single publication (message) in channel history. * @property {Record<string, any>} data - Message payload * @property {any} [info] - Publisher client info * @property {number} offset - Message offset in channel stream * @property {any} [tags] - Optional message tags */

/**
 * @typedef {Object} CentrifugoStreamPosition * @description Stream position for pagination. * @property {number} offset - Stream offset * @property {string} epoch - Stream epoch */

/**
 * @typedef {Object} ChannelList * @description List of channel statistics. * @property {ChannelStatsSerializer[]} channels - Channel statistics * @property {number} total_channels - Total number of channels */

/**
 * @typedef {Object} ChannelStatsSerializer * @description Statistics per channel. * @property {string} channel - Channel name * @property {number} total - Total publishes to this channel * @property {number} successful - Successful publishes * @property {number} failed - Failed publishes * @property {number} avg_duration_ms - Average duration * @property {number} avg_acks - Average ACKs received */

/**
 * @typedef {Object} ChatHistory * @description Chat history response serializer. * @property {string} session_id * @property {ChatMessage[]} messages * @property {number} total_messages */

/**
 * @typedef {Object} ChatMessage * @description Chat message response serializer. * @property {string} id * @property {"user" | "assistant" | "system"} role - Message sender role

* `user` - User
* `assistant` - Assistant
* `system` - System * @property {string} content - Message content * @property {number} [tokens_used] - Tokens used for this message * @property {number} cost_usd * @property {number} [processing_time_ms] - Processing time in milliseconds * @property {string} created_at * @property {any} [context_chunks] - IDs of chunks used for context */

/**
 * @typedef {Object} ChatQueryRequest * @description Chat query request serializer. * @property {string} [session_id] - Chat session ID (creates new if not provided) * @property {string} query - User query * @property {number} [max_tokens] - Maximum response tokens * @property {boolean} [include_sources] - Include source documents in response */

/**
 * @typedef {Object} ChatResponse * @description Chat response serializer. * @property {string} message_id * @property {string} content * @property {number} tokens_used * @property {number} cost_usd * @property {number} processing_time_ms * @property {string} model_used * @property {ChatSource[]} [sources] */

/**
 * @typedef {Object} ChatResponseRequest * @description Chat response serializer. * @property {string} message_id * @property {string} content * @property {number} tokens_used * @property {number} cost_usd * @property {number} processing_time_ms * @property {string} model_used * @property {ChatSourceRequest[]} [sources] */

/**
 * @typedef {Object} ChatSession * @description Chat session response serializer. * @property {string} id * @property {string} [title] - Session title (auto-generated if empty) * @property {boolean} [is_active] - Whether session accepts new messages * @property {number} [messages_count] * @property {number} [total_tokens_used] * @property {number} total_cost_usd * @property {string} [model_name] - LLM model used for this session * @property {number} [temperature] - Temperature setting for LLM * @property {number} [max_context_chunks] - Maximum chunks to include in context * @property {string} created_at * @property {string} updated_at */

/**
 * @typedef {Object} ChatSessionCreateRequest * @description Chat session creation request serializer. * @property {string} [title] - Session title * @property {string} [model_name] - LLM model to use * @property {number} [temperature] - Response creativity * @property {number} [max_context_chunks] - Maximum context chunks */

/**
 * @typedef {Object} ChatSessionRequest * @description Chat session response serializer. * @property {string} [title] - Session title (auto-generated if empty) * @property {boolean} [is_active] - Whether session accepts new messages * @property {number} [messages_count] * @property {number} [total_tokens_used] * @property {string} [model_name] - LLM model used for this session * @property {number} [temperature] - Temperature setting for LLM * @property {number} [max_context_chunks] - Maximum chunks to include in context */

/**
 * @typedef {Object} ChatSource * @description Chat source document information serializer. * @property {string} document_title * @property {string} chunk_content * @property {number} similarity */

/**
 * @typedef {Object} ChatSourceRequest * @description Chat source document information serializer. * @property {string} document_title * @property {string} chunk_content * @property {number} similarity */

/**
 * @typedef {Object} ChunkRevectorizationRequestRequest * @description Chunk re-vectorization request serializer. * @property {string[]} chunk_ids - List of chunk IDs to re-vectorize * @property {boolean} [force] - Force re-vectorization even if already vectorized */

/**
 * @typedef {Object} ConnectionTokenRequestRequest * @description Request model for connection token generation. * @property {string} user_id - User ID for the connection * @property {string[]} [channels] - List of channels to authorize */

/**
 * @typedef {Object} ConnectionTokenResponse * @description Response model for connection token. * @property {string} token - JWT token for WebSocket connection * @property {string} centrifugo_url - Centrifugo WebSocket URL * @property {string} expires_at - Token expiration time (ISO 8601) */

/**
 * @typedef {Object} Currency * @description Currency list serializer. * @property {string} code - Currency code from provider (e.g., USDTTRC20, BTC, ETH) * @property {string} name - Full currency name (e.g., USDT (TRC20), Bitcoin) * @property {string} token - Token symbol (e.g., USDT, BTC, ETH) * @property {string} network - Network name (e.g., TRC20, ERC20, Bitcoin) * @property {string} display_name * @property {string} symbol - Currency symbol (e.g., ₮, ₿, Ξ) * @property {number} decimal_places - Number of decimal places for this currency * @property {boolean} is_active - Whether this currency is available for payments * @property {string} min_amount_usd - Minimum payment amount in USD * @property {number} sort_order - Sort order for currency list (lower = higher priority) */

/**
 * @typedef {Object} Document * @description Document response serializer. * @property {string} id * @property {string} title - Document title * @property {string} [file_type] - MIME type of original file * @property {number} [file_size] - Original file size in bytes * @property {string} processing_status * @property {number} chunks_count * @property {number} total_tokens * @property {number} total_cost_usd * @property {string} created_at * @property {string} updated_at * @property {string} processing_started_at * @property {string} processing_completed_at * @property {string} processing_error * @property {any} [metadata] - Additional document metadata */

/**
 * @typedef {Object} DocumentArchive * @description Document archive serializer. * @property {string} id * @property {string} title - Archive title * @property {string} [description] - Archive description * @property {DocumentCategory[]} categories * @property {boolean} [is_public] - Whether this archive is publicly accessible * @property {string} archive_file - Uploaded archive file * @property {string} original_filename - Original uploaded filename * @property {number} file_size - Archive size in bytes * @property {"zip" | "tar" | "tar.gz" | "tar.bz2"} archive_type - Archive format

* `zip` - ZIP
* `tar` - TAR
* `tar.gz` - TAR GZ
* `tar.bz2` - TAR BZ2 * @property {"pending" | "processing" | "completed" | "failed" | "cancelled"} processing_status - * `pending` - Pending
* `processing` - Processing
* `completed` - Completed
* `failed` - Failed
* `cancelled` - Cancelled * @property {string} processed_at - When processing completed * @property {number} processing_duration_ms - Processing time in milliseconds * @property {string} processing_error - Error message if processing failed * @property {number} total_items - Total items in archive * @property {number} processed_items - Successfully processed items * @property {number} total_chunks - Total chunks created * @property {number} vectorized_chunks - Chunks with embeddings * @property {number} total_tokens - Total tokens across all chunks * @property {number} total_cost_usd - Total processing cost in USD * @property {number} processing_progress - Calculate processing progress as percentage. * @property {number} vectorization_progress - Calculate vectorization progress as percentage. * @property {boolean} is_processed - Check if archive processing is completed. * @property {string} created_at * @property {string} updated_at */

/**
 * @typedef {Object} DocumentArchiveDetail * @description Detailed archive serializer with items. * @property {string} id * @property {string} title - Archive title * @property {string} [description] - Archive description * @property {DocumentCategory[]} categories * @property {boolean} [is_public] - Whether this archive is publicly accessible * @property {string} archive_file - Uploaded archive file * @property {string} original_filename - Original uploaded filename * @property {number} file_size - Archive size in bytes * @property {"zip" | "tar" | "tar.gz" | "tar.bz2"} archive_type - Archive format

* `zip` - ZIP
* `tar` - TAR
* `tar.gz` - TAR GZ
* `tar.bz2` - TAR BZ2 * @property {"pending" | "processing" | "completed" | "failed" | "cancelled"} processing_status - * `pending` - Pending
* `processing` - Processing
* `completed` - Completed
* `failed` - Failed
* `cancelled` - Cancelled * @property {string} processed_at - When processing completed * @property {number} processing_duration_ms - Processing time in milliseconds * @property {string} processing_error - Error message if processing failed * @property {number} total_items - Total items in archive * @property {number} processed_items - Successfully processed items * @property {number} total_chunks - Total chunks created * @property {number} vectorized_chunks - Chunks with embeddings * @property {number} total_tokens - Total tokens across all chunks * @property {number} total_cost_usd - Total processing cost in USD * @property {number} processing_progress - Calculate processing progress as percentage. * @property {number} vectorization_progress - Calculate vectorization progress as percentage. * @property {boolean} is_processed - Check if archive processing is completed. * @property {string} created_at * @property {string} updated_at * @property {ArchiveItem[]} items * @property {Record<string, any>} file_tree - Get hierarchical file tree. * @property {any} [metadata] - Additional archive metadata */

/**
 * @typedef {Object} DocumentArchiveList * @description Simplified archive serializer for list views. * @property {string} id * @property {string} title - Archive title * @property {string} description - Archive description * @property {DocumentCategory[]} categories * @property {boolean} is_public - Whether this archive is publicly accessible * @property {string} original_filename - Original uploaded filename * @property {number} file_size - Archive size in bytes * @property {"zip" | "tar" | "tar.gz" | "tar.bz2"} archive_type - Archive format

* `zip` - ZIP
* `tar` - TAR
* `tar.gz` - TAR GZ
* `tar.bz2` - TAR BZ2 * @property {"pending" | "processing" | "completed" | "failed" | "cancelled"} processing_status - * `pending` - Pending
* `processing` - Processing
* `completed` - Completed
* `failed` - Failed
* `cancelled` - Cancelled * @property {string} processed_at - When processing completed * @property {number} total_items - Total items in archive * @property {number} total_chunks - Total chunks created * @property {number} total_cost_usd - Total processing cost in USD * @property {number} processing_progress - Calculate processing progress as percentage. * @property {string} created_at */

/**
 * @typedef {Object} DocumentArchiveRequest * @description Document archive serializer. * @property {string} title - Archive title * @property {string} [description] - Archive description * @property {boolean} [is_public] - Whether this archive is publicly accessible */

/**
 * @typedef {Object} DocumentCategory * @description Document category serializer. * @property {string} id * @property {string} name - Category name * @property {string} [description] - Category description * @property {boolean} [is_public] - Whether documents in this category are publicly accessible * @property {string} created_at */

/**
 * @typedef {Object} DocumentCategoryRequest * @description Document category serializer. * @property {string} name - Category name * @property {string} [description] - Category description * @property {boolean} [is_public] - Whether documents in this category are publicly accessible */

/**
 * @typedef {Object} DocumentCreateRequest * @description Document creation request serializer. * @property {string} title - Document title * @property {string} content - Document content * @property {string} [file_type] - MIME type * @property {any} [metadata] - Additional metadata */

/**
 * @typedef {Object} DocumentProcessingStatus * @description Document processing status serializer. * @property {string} id * @property {string} status * @property {any} progress * @property {string} [error] * @property {number} [processing_time_seconds] */

/**
 * @typedef {Object} DocumentRequest * @description Document response serializer. * @property {string} title - Document title * @property {string} [file_type] - MIME type of original file * @property {number} [file_size] - Original file size in bytes * @property {any} [metadata] - Additional document metadata */

/**
 * @typedef {Object} DocumentStats * @description Document processing statistics serializer. * @property {number} total_documents * @property {number} completed_documents * @property {number} processing_success_rate * @property {number} total_chunks * @property {number} total_tokens * @property {number} total_cost_usd * @property {number} avg_processing_time_seconds */

/**
 * @typedef {Object} EmailLog * @description Serializer for EmailLog model. * @property {string} id * @property {number} user * @property {string} user_email * @property {number} newsletter * @property {string} newsletter_title * @property {string} recipient - Comma-separated email addresses * @property {string} subject * @property {string} body * @property {"pending" | "sent" | "failed"} status - * `pending` - Pending
* `sent` - Sent
* `failed` - Failed * @property {string} created_at * @property {string} sent_at * @property {string} error_message */

/**
 * @typedef {Object} Endpoint * @description Serializer for single endpoint status. * @property {string} url - Resolved URL (for parametrized URLs) or URL pattern * @property {string} [url_pattern] - Original URL pattern (for parametrized URLs) * @property {string} [url_name] - Django URL name (if available) * @property {string} [namespace] - URL namespace * @property {string} group - URL group (up to 3 depth) * @property {string} [view] - View function/class name * @property {string} status - Status: healthy, unhealthy, warning, error, skipped, pending * @property {number} [status_code] - HTTP status code * @property {number} [response_time_ms] - Response time in milliseconds * @property {boolean} [is_healthy] - Whether endpoint is healthy * @property {string} [error] - Error message if check failed * @property {string} [error_type] - Error type: database, general, etc. * @property {string} [reason] - Reason for warning/skip * @property {string} [last_checked] - Timestamp of last check * @property {boolean} [has_parameters] - Whether URL has parameters that were resolved with test values * @property {boolean} [required_auth] - Whether endpoint required JWT authentication * @property {boolean} [rate_limited] - Whether endpoint returned 429 (rate limited) */

/**
 * @typedef {Object} EndpointsStatus * @description Serializer for overall endpoints status response. * @property {string} status - Overall status: healthy, degraded, or unhealthy * @property {string} timestamp - Timestamp of the check * @property {number} total_endpoints - Total number of endpoints checked * @property {number} healthy - Number of healthy endpoints * @property {number} unhealthy - Number of unhealthy endpoints * @property {number} warnings - Number of endpoints with warnings * @property {number} errors - Number of endpoints with errors * @property {number} skipped - Number of skipped endpoints * @property {Endpoint[]} endpoints - List of all endpoints with their status */

/**
 * @typedef {Object} ErrorResponse * @description Generic error response. * @property {boolean} [success] * @property {string} message */

/**
 * @typedef {Object} HealthCheck * @description Health check response. * @property {string} status - Health status: healthy or unhealthy * @property {string} wrapper_url - Configured wrapper URL * @property {boolean} has_api_key - Whether API key is configured * @property {string} timestamp - Current timestamp */

/**
 * @typedef {Object} LeadSubmission * @description Serializer for lead form submission from frontend. * @property {string} name * @property {string} email * @property {string} [company] * @property {string} [company_site] * @property {"email" | "whatsapp" | "telegram" | "phone" | "other"} [contact_type] - * `email` - Email
* `whatsapp` - WhatsApp
* `telegram` - Telegram
* `phone` - Phone
* `other` - Other * @property {string} [contact_value] * @property {string} [subject] * @property {string} message * @property {any} [extra] * @property {string} site_url - Frontend URL where form was submitted */

/**
 * @typedef {Object} LeadSubmissionError * @description Response serializer for lead submission errors. * @property {boolean} success * @property {string} error * @property {Record<string, any>} [details] */

/**
 * @typedef {Object} LeadSubmissionRequest * @description Serializer for lead form submission from frontend. * @property {string} name * @property {string} email * @property {string} [company] * @property {string} [company_site] * @property {"email" | "whatsapp" | "telegram" | "phone" | "other"} [contact_type] - * `email` - Email
* `whatsapp` - WhatsApp
* `telegram` - Telegram
* `phone` - Phone
* `other` - Other * @property {string} [contact_value] * @property {string} [subject] * @property {string} message * @property {any} [extra] * @property {string} site_url - Frontend URL where form was submitted */

/**
 * @typedef {Object} LeadSubmissionResponse * @description Response serializer for successful lead submission. * @property {boolean} success * @property {string} message * @property {number} lead_id */

/**
 * @typedef {Object} ManualAckRequestRequest * @description Request model for manual ACK sending. * @property {string} message_id - Message ID to acknowledge * @property {string} client_id - Client ID sending the ACK */

/**
 * @typedef {Object} ManualAckResponse * @description Response model for manual ACK. * @property {boolean} success - Whether ACK was sent successfully * @property {string} message_id - Message ID that was acknowledged * @property {any} [error] - Error message if failed */

/**
 * @typedef {Object} Message * @property {string} uuid * @property {string} ticket * @property {any} sender * @property {boolean} is_from_author - Check if this message is from the ticket author. * @property {string} text * @property {string} created_at */

/**
 * @typedef {Object} MessageCreate * @property {string} text */

/**
 * @typedef {Object} MessageCreateRequest * @property {string} text */

/**
 * @typedef {Object} MessageRequest * @property {string} text */

/**
 * @typedef {Object} Newsletter * @description Serializer for Newsletter model. * @property {number} id * @property {string} title * @property {string} [description] * @property {boolean} [is_active] * @property {boolean} [auto_subscribe] - Automatically subscribe new users to this newsletter * @property {string} created_at * @property {string} updated_at * @property {number} subscribers_count */

/**
 * @typedef {Object} NewsletterCampaign * @description Serializer for NewsletterCampaign model. * @property {number} id * @property {number} newsletter * @property {string} newsletter_title * @property {string} subject * @property {string} email_title * @property {string} main_text * @property {string} [main_html_content] * @property {string} [button_text] * @property {string} [button_url] * @property {string} [secondary_text] * @property {"draft" | "sending" | "sent" | "failed"} status - * `draft` - Draft
* `sending` - Sending
* `sent` - Sent
* `failed` - Failed * @property {string} created_at * @property {string} sent_at * @property {number} recipient_count */

/**
 * @typedef {Object} NewsletterCampaignRequest * @description Serializer for NewsletterCampaign model. * @property {number} newsletter * @property {string} subject * @property {string} email_title * @property {string} main_text * @property {string} [main_html_content] * @property {string} [button_text] * @property {string} [button_url] * @property {string} [secondary_text] */

/**
 * @typedef {Object} NewsletterSubscription * @description Serializer for NewsletterSubscription model. * @property {number} id * @property {number} newsletter * @property {string} newsletter_title * @property {number} [user] * @property {string} user_email * @property {string} email * @property {boolean} [is_active] * @property {string} subscribed_at * @property {string} unsubscribed_at */

/**
 * @typedef {Object} OTPErrorResponse * @description Error response for OTP operations. * @property {string} error - Error message */

/**
 * @typedef {Object} OTPRequestRequest * @description Serializer for OTP request. * @property {string} identifier - Email address or phone number for OTP delivery * @property {"email" | "phone"} [channel] - Delivery channel: 'email' or 'phone'. Auto-detected if not provided.

* `email` - Email
* `phone` - Phone * @property {string} [source_url] - Source URL for tracking registration (e.g., https://dashboard.unrealon.com) */

/**
 * @typedef {Object} OTPRequestResponse * @description OTP request response. * @property {string} message - Success message */

/**
 * @typedef {Object} OTPVerifyRequest * @description Serializer for OTP verification. * @property {string} identifier - Email address or phone number used for OTP request * @property {string} otp * @property {"email" | "phone"} [channel] - Delivery channel: 'email' or 'phone'. Auto-detected if not provided.

* `email` - Email
* `phone` - Phone * @property {string} [source_url] - Source URL for tracking login (e.g., https://dashboard.unrealon.com) */

/**
 * @typedef {Object} OTPVerifyResponse * @description OTP verification response. * @property {string} refresh - JWT refresh token * @property {string} access - JWT access token * @property {any} user - User information */

/**
 * @typedef {Object} OverviewStats * @description Overview statistics for Centrifugo publishes. * @property {number} total - Total publishes in period * @property {number} successful - Successful publishes * @property {number} failed - Failed publishes * @property {number} timeout - Timeout publishes * @property {number} success_rate - Success rate percentage * @property {number} avg_duration_ms - Average duration in milliseconds * @property {number} avg_acks_received - Average ACKs received * @property {number} period_hours - Statistics period in hours */

/**
 * @typedef {Object} PaginatedArchiveItemChunkList * @property {number} count - Total number of items across all pages * @property {number} page - Current page number (1-based) * @property {number} pages - Total number of pages * @property {number} page_size - Number of items per page * @property {boolean} has_next - Whether there is a next page * @property {boolean} has_previous - Whether there is a previous page * @property {number} [next_page] - Next page number (null if no next page) * @property {number} [previous_page] - Previous page number (null if no previous page) * @property {ArchiveItemChunk[]} results - Array of items for current page */

/**
 * @typedef {Object} PaginatedArchiveItemList * @property {number} count - Total number of items across all pages * @property {number} page - Current page number (1-based) * @property {number} pages - Total number of pages * @property {number} page_size - Number of items per page * @property {boolean} has_next - Whether there is a next page * @property {boolean} has_previous - Whether there is a previous page * @property {number} [next_page] - Next page number (null if no next page) * @property {number} [previous_page] - Previous page number (null if no previous page) * @property {ArchiveItem[]} results - Array of items for current page */

/**
 * @typedef {Object} PaginatedArchiveSearchResultList * @property {number} count - Total number of items across all pages * @property {number} page - Current page number (1-based) * @property {number} pages - Total number of pages * @property {number} page_size - Number of items per page * @property {boolean} has_next - Whether there is a next page * @property {boolean} has_previous - Whether there is a previous page * @property {number} [next_page] - Next page number (null if no next page) * @property {number} [previous_page] - Previous page number (null if no previous page) * @property {ArchiveSearchResult[]} results - Array of items for current page */

/**
 * @typedef {Object} PaginatedChatResponseList * @property {number} count - Total number of items across all pages * @property {number} page - Current page number (1-based) * @property {number} pages - Total number of pages * @property {number} page_size - Number of items per page * @property {boolean} has_next - Whether there is a next page * @property {boolean} has_previous - Whether there is a previous page * @property {number} [next_page] - Next page number (null if no next page) * @property {number} [previous_page] - Previous page number (null if no previous page) * @property {ChatResponse[]} results - Array of items for current page */

/**
 * @typedef {Object} PaginatedChatSessionList * @property {number} count - Total number of items across all pages * @property {number} page - Current page number (1-based) * @property {number} pages - Total number of pages * @property {number} page_size - Number of items per page * @property {boolean} has_next - Whether there is a next page * @property {boolean} has_previous - Whether there is a previous page * @property {number} [next_page] - Next page number (null if no next page) * @property {number} [previous_page] - Previous page number (null if no previous page) * @property {ChatSession[]} results - Array of items for current page */

/**
 * @typedef {Object} PaginatedDocumentArchiveListList * @property {number} count - Total number of items across all pages * @property {number} page - Current page number (1-based) * @property {number} pages - Total number of pages * @property {number} page_size - Number of items per page * @property {boolean} has_next - Whether there is a next page * @property {boolean} has_previous - Whether there is a previous page * @property {number} [next_page] - Next page number (null if no next page) * @property {number} [previous_page] - Previous page number (null if no previous page) * @property {DocumentArchiveList[]} results - Array of items for current page */

/**
 * @typedef {Object} PaginatedDocumentList * @property {number} count - Total number of items across all pages * @property {number} page - Current page number (1-based) * @property {number} pages - Total number of pages * @property {number} page_size - Number of items per page * @property {boolean} has_next - Whether there is a next page * @property {boolean} has_previous - Whether there is a previous page * @property {number} [next_page] - Next page number (null if no next page) * @property {number} [previous_page] - Previous page number (null if no previous page) * @property {Document[]} results - Array of items for current page */

/**
 * @typedef {Object} PaginatedEmailLogList * @property {number} count - Total number of items across all pages * @property {number} page - Current page number (1-based) * @property {number} pages - Total number of pages * @property {number} page_size - Number of items per page * @property {boolean} has_next - Whether there is a next page * @property {boolean} has_previous - Whether there is a previous page * @property {number} [next_page] - Next page number (null if no next page) * @property {number} [previous_page] - Previous page number (null if no previous page) * @property {EmailLog[]} results - Array of items for current page */

/**
 * @typedef {Object} PaginatedLeadSubmissionList * @property {number} count - Total number of items across all pages * @property {number} page - Current page number (1-based) * @property {number} pages - Total number of pages * @property {number} page_size - Number of items per page * @property {boolean} has_next - Whether there is a next page * @property {boolean} has_previous - Whether there is a previous page * @property {number} [next_page] - Next page number (null if no next page) * @property {number} [previous_page] - Previous page number (null if no previous page) * @property {LeadSubmission[]} results - Array of items for current page */

/**
 * @typedef {Object} PaginatedMessageList * @property {number} count - Total number of items across all pages * @property {number} page - Current page number (1-based) * @property {number} pages - Total number of pages * @property {number} page_size - Number of items per page * @property {boolean} has_next - Whether there is a next page * @property {boolean} has_previous - Whether there is a previous page * @property {number} [next_page] - Next page number (null if no next page) * @property {number} [previous_page] - Previous page number (null if no previous page) * @property {Message[]} results - Array of items for current page */

/**
 * @typedef {Object} PaginatedNewsletterCampaignList * @property {number} count - Total number of items across all pages * @property {number} page - Current page number (1-based) * @property {number} pages - Total number of pages * @property {number} page_size - Number of items per page * @property {boolean} has_next - Whether there is a next page * @property {boolean} has_previous - Whether there is a previous page * @property {number} [next_page] - Next page number (null if no next page) * @property {number} [previous_page] - Previous page number (null if no previous page) * @property {NewsletterCampaign[]} results - Array of items for current page */

/**
 * @typedef {Object} PaginatedNewsletterList * @property {number} count - Total number of items across all pages * @property {number} page - Current page number (1-based) * @property {number} pages - Total number of pages * @property {number} page_size - Number of items per page * @property {boolean} has_next - Whether there is a next page * @property {boolean} has_previous - Whether there is a previous page * @property {number} [next_page] - Next page number (null if no next page) * @property {number} [previous_page] - Previous page number (null if no previous page) * @property {Newsletter[]} results - Array of items for current page */

/**
 * @typedef {Object} PaginatedNewsletterSubscriptionList * @property {number} count - Total number of items across all pages * @property {number} page - Current page number (1-based) * @property {number} pages - Total number of pages * @property {number} page_size - Number of items per page * @property {boolean} has_next - Whether there is a next page * @property {boolean} has_previous - Whether there is a previous page * @property {number} [next_page] - Next page number (null if no next page) * @property {number} [previous_page] - Previous page number (null if no previous page) * @property {NewsletterSubscription[]} results - Array of items for current page */

/**
 * @typedef {Object} PaginatedPaymentListList * @property {number} count - Total number of items across all pages * @property {number} page - Current page number (1-based) * @property {number} pages - Total number of pages * @property {number} page_size - Number of items per page * @property {boolean} has_next - Whether there is a next page * @property {boolean} has_previous - Whether there is a previous page * @property {number} [next_page] - Next page number (null if no next page) * @property {number} [previous_page] - Previous page number (null if no previous page) * @property {PaymentList[]} results - Array of items for current page */

/**
 * @typedef {Object} PaginatedPublicCategoryList * @property {number} count - Total number of items across all pages * @property {number} page - Current page number (1-based) * @property {number} pages - Total number of pages * @property {number} page_size - Number of items per page * @property {boolean} has_next - Whether there is a next page * @property {boolean} has_previous - Whether there is a previous page * @property {number} [next_page] - Next page number (null if no next page) * @property {number} [previous_page] - Previous page number (null if no previous page) * @property {PublicCategory[]} results - Array of items for current page */

/**
 * @typedef {Object} PaginatedPublicDocumentListList * @property {number} count - Total number of items across all pages * @property {number} page - Current page number (1-based) * @property {number} pages - Total number of pages * @property {number} page_size - Number of items per page * @property {boolean} has_next - Whether there is a next page * @property {boolean} has_previous - Whether there is a previous page * @property {number} [next_page] - Next page number (null if no next page) * @property {number} [previous_page] - Previous page number (null if no previous page) * @property {PublicDocumentList[]} results - Array of items for current page */

/**
 * @typedef {Object} PaginatedTicketList * @property {number} count - Total number of items across all pages * @property {number} page - Current page number (1-based) * @property {number} pages - Total number of pages * @property {number} page_size - Number of items per page * @property {boolean} has_next - Whether there is a next page * @property {boolean} has_previous - Whether there is a previous page * @property {number} [next_page] - Next page number (null if no next page) * @property {number} [previous_page] - Previous page number (null if no previous page) * @property {Ticket[]} results - Array of items for current page */

/**
 * @typedef {Object} PatchedArchiveItemChunkRequest * @description Archive item chunk serializer. * @property {string} [content] - Chunk text content * @property {number} [chunk_index] - Sequential chunk number within item * @property {"text" | "code" | "heading" | "metadata" | "table" | "list"} [chunk_type] - Type of content in chunk

* `text` - Text
* `code` - Code
* `heading` - Heading
* `metadata` - Metadata
* `table` - Table
* `list` - List */

/**
 * @typedef {Object} PatchedArchiveItemRequest * @description Archive item serializer. * @property {string} [relative_path] - Path within archive * @property {string} [item_name] - Item name * @property {string} [item_type] - MIME type * @property {number} [file_size] - Item size in bytes */

/**
 * @typedef {Object} PatchedChatResponseRequest * @description Chat response serializer. * @property {string} [message_id] * @property {string} [content] * @property {number} [tokens_used] * @property {number} [cost_usd] * @property {number} [processing_time_ms] * @property {string} [model_used] * @property {ChatSourceRequest[]} [sources] */

/**
 * @typedef {Object} PatchedChatSessionRequest * @description Chat session response serializer. * @property {string} [title] - Session title (auto-generated if empty) * @property {boolean} [is_active] - Whether session accepts new messages * @property {number} [messages_count] * @property {number} [total_tokens_used] * @property {string} [model_name] - LLM model used for this session * @property {number} [temperature] - Temperature setting for LLM * @property {number} [max_context_chunks] - Maximum chunks to include in context */

/**
 * @typedef {Object} PatchedDocumentArchiveRequest * @description Document archive serializer. * @property {string} [title] - Archive title * @property {string} [description] - Archive description * @property {boolean} [is_public] - Whether this archive is publicly accessible */

/**
 * @typedef {Object} PatchedDocumentRequest * @description Document response serializer. * @property {string} [title] - Document title * @property {string} [file_type] - MIME type of original file * @property {number} [file_size] - Original file size in bytes * @property {any} [metadata] - Additional document metadata */

/**
 * @typedef {Object} PatchedLeadSubmissionRequest * @description Serializer for lead form submission from frontend. * @property {string} [name] * @property {string} [email] * @property {string} [company] * @property {string} [company_site] * @property {"email" | "whatsapp" | "telegram" | "phone" | "other"} [contact_type] - * `email` - Email
* `whatsapp` - WhatsApp
* `telegram` - Telegram
* `phone` - Phone
* `other` - Other * @property {string} [contact_value] * @property {string} [subject] * @property {string} [message] * @property {any} [extra] * @property {string} [site_url] - Frontend URL where form was submitted */

/**
 * @typedef {Object} PatchedMessageRequest * @property {string} [text] */

/**
 * @typedef {Object} PatchedNewsletterCampaignRequest * @description Serializer for NewsletterCampaign model. * @property {number} [newsletter] * @property {string} [subject] * @property {string} [email_title] * @property {string} [main_text] * @property {string} [main_html_content] * @property {string} [button_text] * @property {string} [button_url] * @property {string} [secondary_text] */

/**
 * @typedef {Object} PatchedTicketRequest * @property {number} [user] * @property {string} [subject] * @property {"open" | "waiting_for_user" | "waiting_for_admin" | "resolved" | "closed"} [status] - * `open` - Open
* `waiting_for_user` - Waiting for User
* `waiting_for_admin` - Waiting for Admin
* `resolved` - Resolved
* `closed` - Closed */

/**
 * @typedef {Object} PatchedUnsubscribeRequest * @description Simple serializer for unsubscribe. * @property {number} [subscription_id] */

/**
 * @typedef {Object} PatchedUserProfileUpdateRequest * @description Serializer for updating user profile. * @property {string} [first_name] * @property {string} [last_name] * @property {string} [company] * @property {string} [phone] * @property {string} [position] */

/**
 * @typedef {Object} PaymentDetail * @description Detailed payment information. * @property {string} id - Unique identifier for this record * @property {string} internal_payment_id - Internal payment identifier (PAY_YYYYMMDDHHMMSS_UUID) * @property {string} amount_usd - Payment amount in USD * @property {string} currency_code * @property {string} currency_name * @property {string} currency_token * @property {string} currency_network * @property {string} pay_amount - Amount to pay in cryptocurrency * @property {string} actual_amount - Actual amount received in cryptocurrency * @property {string} actual_amount_usd - Actual amount received in USD * @property {"pending" | "confirming" | "confirmed" | "completed" | "partially_paid" | "failed" | "expired" | "cancelled"} status - Current payment status

* `pending` - Pending
* `confirming` - Confirming
* `confirmed` - Confirmed
* `completed` - Completed
* `partially_paid` - Partially Paid
* `failed` - Failed
* `expired` - Expired
* `cancelled` - Cancelled * @property {string} status_display * @property {string} pay_address - Cryptocurrency payment address * @property {string} qr_code_url - Get QR code URL. * @property {string} payment_url - Payment page URL (if provided by provider) * @property {string} transaction_hash - Blockchain transaction hash * @property {string} explorer_link - Get blockchain explorer link. * @property {number} confirmations_count - Number of blockchain confirmations * @property {string} expires_at - When this payment expires (typically 30 minutes) * @property {string} completed_at - When this payment was completed * @property {string} created_at - When this record was created * @property {boolean} is_completed * @property {boolean} is_failed * @property {boolean} is_expired * @property {string} description - Payment description */

/**
 * @typedef {Object} PaymentList * @description Payment list item (lighter than detail). * @property {string} id - Unique identifier for this record * @property {string} internal_payment_id - Internal payment identifier (PAY_YYYYMMDDHHMMSS_UUID) * @property {string} amount_usd - Payment amount in USD * @property {string} currency_code * @property {string} currency_token * @property {"pending" | "confirming" | "confirmed" | "completed" | "partially_paid" | "failed" | "expired" | "cancelled"} status - Current payment status

* `pending` - Pending
* `confirming` - Confirming
* `confirmed` - Confirmed
* `completed` - Completed
* `partially_paid` - Partially Paid
* `failed` - Failed
* `expired` - Expired
* `cancelled` - Cancelled * @property {string} status_display * @property {string} created_at - When this record was created * @property {string} completed_at - When this payment was completed */

/**
 * @typedef {Object} PublicCategory * @description Public category serializer. * @property {string} id * @property {string} name - Category name * @property {string} [description] - Category description */

/**
 * @typedef {Object} PublicDocument * @description Public document detail serializer - only essential data for clients. * @property {string} id * @property {string} title - Document title * @property {string} content - Full document content * @property {any} category * @property {string} created_at * @property {string} updated_at */

/**
 * @typedef {Object} PublicDocumentList * @description Public document list serializer - minimal fields for listing. * @property {string} id * @property {string} title - Document title * @property {any} category * @property {string} created_at * @property {string} updated_at */

/**
 * @typedef {Object} PublishTestRequestRequest * @description Request model for test message publishing. * @property {string} channel - Target channel name * @property {Record<string, any>} data - Message data (any JSON object) * @property {boolean} [wait_for_ack] - Wait for client acknowledgment * @property {number} [ack_timeout] - ACK timeout in seconds */

/**
 * @typedef {Object} PublishTestResponse * @description Response model for test message publishing. * @property {boolean} success - Whether publish succeeded * @property {string} message_id - Unique message ID * @property {string} channel - Target channel * @property {number} [acks_received] - Number of ACKs received * @property {boolean} [delivered] - Whether message was delivered * @property {any} [error] - Error message if failed */

/**
 * @typedef {Object} QueueAction * @description Serializer for queue management actions. * @property {"clear" | "clear_all" | "purge" | "purge_failed" | "flush"} action - Action to perform on queues

* `clear` - clear
* `clear_all` - clear_all
* `purge` - purge
* `purge_failed` - purge_failed
* `flush` - flush * @property {string[]} [queue_names] - Specific queues to target (empty = all queues) */

/**
 * @typedef {Object} QueueActionRequest * @description Serializer for queue management actions. * @property {"clear" | "clear_all" | "purge" | "purge_failed" | "flush"} action - Action to perform on queues

* `clear` - clear
* `clear_all` - clear_all
* `purge` - purge
* `purge_failed` - purge_failed
* `flush` - flush * @property {string[]} [queue_names] - Specific queues to target (empty = all queues) */

/**
 * @typedef {Object} QueueStatus * @description Serializer for queue status data. * @property {Record<string, Record<string, number>>} queues - Queue information with pending/failed counts * @property {number} workers - Number of active workers * @property {boolean} redis_connected - Redis connection status * @property {string} timestamp - Current timestamp * @property {string} [error] - Error message if any */

/**
 * @typedef {Object} QuickHealth * @description Serializer for quick health check response. * @property {string} status - Quick health status: ok or error * @property {string} timestamp - Timestamp of the health check * @property {string} [error] - Error message if health check failed */

/**
 * @typedef {Object} RecentPublishes * @description Recent publishes list. * @property {Record<string, any>[]} publishes - List of recent publishes * @property {number} count - Number of publishes returned * @property {number} total_available - Total publishes available */

/**
 * @typedef {Object} SendCampaignRequest * @description Simple serializer for sending campaign. * @property {number} campaign_id */

/**
 * @typedef {Object} SendCampaignResponse * @description Response for sending campaign. * @property {boolean} success * @property {string} [message] * @property {number} [sent_count] * @property {string} [error] */

/**
 * @typedef {Object} Sender * @property {number} id * @property {string} display_username - Get formatted username for display. * @property {string} email * @property {string} avatar * @property {string} initials - Get user's initials for avatar fallback. * @property {boolean} is_staff - Designates whether the user can log into this admin site. * @property {boolean} is_superuser - Designates that this user has all permissions without explicitly assigning them. */

/**
 * @typedef {Object} SubscribeRequest * @description Simple serializer for newsletter subscription. * @property {number} newsletter_id * @property {string} email */

/**
 * @typedef {Object} SubscribeResponse * @description Response for subscription. * @property {boolean} success * @property {string} message * @property {number} [subscription_id] */

/**
 * @typedef {Object} SuccessResponse * @description Generic success response. * @property {boolean} success * @property {string} message */

/**
 * @typedef {Object} TaskStatistics * @description Serializer for task statistics data. * @property {Record<string, number>} statistics - Task count statistics * @property {Record<string, any>[]} recent_tasks - List of recent tasks * @property {string} timestamp - Current timestamp * @property {string} [error] - Error message if any */

/**
 * @typedef {Object} TestEmailRequest * @description Simple serializer for test email. * @property {string} email * @property {string} [subject] * @property {string} [message] */

/**
 * @typedef {Object} Ticket * @property {string} uuid * @property {number} user * @property {string} subject * @property {"open" | "waiting_for_user" | "waiting_for_admin" | "resolved" | "closed"} [status] - * `open` - Open
* `waiting_for_user` - Waiting for User
* `waiting_for_admin` - Waiting for Admin
* `resolved` - Resolved
* `closed` - Closed * @property {string} created_at * @property {number} unanswered_messages_count - Get count of unanswered messages for this specific ticket. */

/**
 * @typedef {Object} TicketRequest * @property {number} user * @property {string} subject * @property {"open" | "waiting_for_user" | "waiting_for_admin" | "resolved" | "closed"} [status] - * `open` - Open
* `waiting_for_user` - Waiting for User
* `waiting_for_admin` - Waiting for Admin
* `resolved` - Resolved
* `closed` - Closed */

/**
 * @typedef {Object} TokenRefresh * @property {string} access * @property {string} refresh */

/**
 * @typedef {Object} TokenRefreshRequest * @property {string} refresh */

/**
 * @typedef {Object} Transaction * @description Transaction serializer. * @property {string} id - Unique identifier for this record * @property {"deposit" | "withdrawal" | "payment" | "refund" | "fee" | "bonus" | "adjustment"} transaction_type - Type of transaction

* `deposit` - Deposit
* `withdrawal` - Withdrawal
* `payment` - Payment
* `refund` - Refund
* `fee` - Fee
* `bonus` - Bonus
* `adjustment` - Adjustment * @property {string} type_display * @property {string} amount_usd - Transaction amount in USD (positive=credit, negative=debit) * @property {string} amount_display * @property {string} balance_after - User balance after this transaction * @property {string} payment_id - Related payment ID (if applicable) * @property {string} description - Transaction description * @property {string} created_at - When this record was created */

/**
 * @typedef {Object} Unsubscribe * @description Simple serializer for unsubscribe. * @property {number} subscription_id */

/**
 * @typedef {Object} UnsubscribeRequest * @description Simple serializer for unsubscribe. * @property {number} subscription_id */

/**
 * @typedef {Object} User * @description Serializer for user details. * @property {number} id * @property {string} email * @property {string} [first_name] * @property {string} [last_name] * @property {string} full_name - Get user's full name. * @property {string} initials - Get user's initials for avatar fallback. * @property {string} display_username - Get formatted username for display. * @property {string} [company] * @property {string} [phone] * @property {string} [position] * @property {string} avatar * @property {boolean} is_staff - Designates whether the user can log into this admin site. * @property {boolean} is_superuser - Designates that this user has all permissions without explicitly assigning them. * @property {string} date_joined * @property {string} last_login * @property {number} unanswered_messages_count - Get count of unanswered messages for the user. */

/**
 * @typedef {Object} UserProfileUpdateRequest * @description Serializer for updating user profile. * @property {string} [first_name] * @property {string} [last_name] * @property {string} [company] * @property {string} [phone] * @property {string} [position] */

/**
 * @typedef {Object} VectorizationResult * @description Vectorization result serializer. * @property {number} vectorized_count * @property {number} failed_count * @property {number} total_tokens * @property {number} total_cost * @property {number} success_rate * @property {string[]} errors */

/**
 * @typedef {Object} VectorizationStatistics * @description Vectorization statistics serializer. * @property {number} total_chunks * @property {number} vectorized_chunks * @property {number} pending_chunks * @property {number} vectorization_rate * @property {number} total_tokens * @property {number} total_cost * @property {number} avg_tokens_per_chunk * @property {number} avg_cost_per_chunk */

/**
 * @typedef {Object} WorkerAction * @description Serializer for worker management actions. * @property {"start" | "stop" | "restart"} action - Action to perform on workers

* `start` - start
* `stop` - stop
* `restart` - restart * @property {number} [processes] - Number of worker processes * @property {number} [threads] - Number of threads per process */

/**
 * @typedef {Object} WorkerActionRequest * @description Serializer for worker management actions. * @property {"start" | "stop" | "restart"} action - Action to perform on workers

* `start` - start
* `stop` - stop
* `restart` - restart * @property {number} [processes] - Number of worker processes * @property {number} [threads] - Number of threads per process */


// Export empty object to make this a module
export {};