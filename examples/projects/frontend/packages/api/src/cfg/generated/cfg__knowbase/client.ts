import * as Models from "./models";


/**
 * API endpoints for Knowbase.
 */
export class CfgKnowbase {
  private client: any;

  constructor(client: any) {
    this.client = client;
  }

  async adminChatList(page?: number, page_size?: number): Promise<Models.PaginatedChatResponseList>;
  async adminChatList(params?: { page?: number; page_size?: number }): Promise<Models.PaginatedChatResponseList>;

  /**
   * Chat query endpoints.
   */
  async adminChatList(...args: any[]): Promise<Models.PaginatedChatResponseList> {
    const isParamsObject = args.length === 1 && typeof args[0] === 'object' && args[0] !== null && !Array.isArray(args[0]);
    
    let params;
    if (isParamsObject) {
      params = args[0];
    } else {
      params = { page: args[0], page_size: args[1] };
    }
    const response = await this.client.request('GET', "/cfg/knowbase/admin/chat/", { params });
    return response;
  }

  /**
   * Chat query endpoints.
   */
  async adminChatCreate(data: Models.ChatResponseRequest): Promise<Models.ChatResponse> {
    const response = await this.client.request('POST', "/cfg/knowbase/admin/chat/", { body: data });
    return response;
  }

  /**
   * Chat query endpoints.
   */
  async adminChatRetrieve(id: string): Promise<Models.ChatResponse> {
    const response = await this.client.request('GET', `/cfg/knowbase/admin/chat/${id}/`);
    return response;
  }

  /**
   * Chat query endpoints.
   */
  async adminChatUpdate(id: string, data: Models.ChatResponseRequest): Promise<Models.ChatResponse> {
    const response = await this.client.request('PUT', `/cfg/knowbase/admin/chat/${id}/`, { body: data });
    return response;
  }

  /**
   * Chat query endpoints.
   */
  async adminChatPartialUpdate(id: string, data?: Models.PatchedChatResponseRequest): Promise<Models.ChatResponse> {
    const response = await this.client.request('PATCH', `/cfg/knowbase/admin/chat/${id}/`, { body: data });
    return response;
  }

  /**
   * Chat query endpoints.
   */
  async adminChatDestroy(id: string): Promise<void> {
    const response = await this.client.request('DELETE', `/cfg/knowbase/admin/chat/${id}/`);
    return;
  }

  /**
   * Get chat history
   * 
   * Get chat session history.
   */
  async adminChatHistoryRetrieve(id: string): Promise<Models.ChatHistory> {
    const response = await this.client.request('GET', `/cfg/knowbase/admin/chat/${id}/history/`);
    return response;
  }

  /**
   * Process chat query with RAG
   * 
   * Process chat query with RAG context.
   */
  async adminChatQueryCreate(data: Models.ChatQueryRequest): Promise<Models.ChatResponse> {
    const response = await this.client.request('POST', "/cfg/knowbase/admin/chat/query/", { body: data });
    return response;
  }

  async adminDocumentsList(page?: number, page_size?: number, status?: string): Promise<Models.PaginatedDocumentList>;
  async adminDocumentsList(params?: { page?: number; page_size?: number; status?: string }): Promise<Models.PaginatedDocumentList>;

  /**
   * List user documents
   * 
   * List user documents with filtering and pagination.
   */
  async adminDocumentsList(...args: any[]): Promise<Models.PaginatedDocumentList> {
    const isParamsObject = args.length === 1 && typeof args[0] === 'object' && args[0] !== null && !Array.isArray(args[0]);
    
    let params;
    if (isParamsObject) {
      params = args[0];
    } else {
      params = { page: args[0], page_size: args[1], status: args[2] };
    }
    const response = await this.client.request('GET', "/cfg/knowbase/admin/documents/", { params });
    return response;
  }

  /**
   * Upload new document
   * 
   * Upload and process a new knowledge document
   */
  async adminDocumentsCreate(data: Models.DocumentCreateRequest): Promise<Models.Document> {
    const response = await this.client.request('POST', "/cfg/knowbase/admin/documents/", { body: data });
    return response;
  }

  /**
   * Get document details
   * 
   * Get document by ID.
   */
  async adminDocumentsRetrieve(id: string): Promise<Models.Document> {
    const response = await this.client.request('GET', `/cfg/knowbase/admin/documents/${id}/`);
    return response;
  }

  /**
   * Document management endpoints - Admin only.
   */
  async adminDocumentsUpdate(id: string, data: Models.DocumentRequest): Promise<Models.Document> {
    const response = await this.client.request('PUT', `/cfg/knowbase/admin/documents/${id}/`, { body: data });
    return response;
  }

  /**
   * Document management endpoints - Admin only.
   */
  async adminDocumentsPartialUpdate(id: string, data?: Models.PatchedDocumentRequest): Promise<Models.Document> {
    const response = await this.client.request('PATCH', `/cfg/knowbase/admin/documents/${id}/`, { body: data });
    return response;
  }

  /**
   * Delete document
   * 
   * Delete document and all associated chunks.
   */
  async adminDocumentsDestroy(id: string): Promise<void> {
    const response = await this.client.request('DELETE', `/cfg/knowbase/admin/documents/${id}/`);
    return;
  }

  /**
   * Reprocess document
   * 
   * Trigger reprocessing of document chunks and embeddings
   */
  async adminDocumentsReprocessCreate(id: string, data: Models.DocumentRequest): Promise<Models.Document> {
    const response = await this.client.request('POST', `/cfg/knowbase/admin/documents/${id}/reprocess/`, { body: data });
    return response;
  }

  /**
   * Get document processing status
   * 
   * Get document processing status.
   */
  async adminDocumentsStatusRetrieve(id: string): Promise<Models.DocumentProcessingStatus> {
    const response = await this.client.request('GET', `/cfg/knowbase/admin/documents/${id}/status/`);
    return response;
  }

  /**
   * Get processing statistics
   * 
   * Get user's document processing statistics.
   */
  async adminDocumentsStatsRetrieve(): Promise<Models.DocumentStats> {
    const response = await this.client.request('GET', "/cfg/knowbase/admin/documents/stats/");
    return response;
  }

  async adminSessionsList(page?: number, page_size?: number): Promise<Models.PaginatedChatSessionList>;
  async adminSessionsList(params?: { page?: number; page_size?: number }): Promise<Models.PaginatedChatSessionList>;

  /**
   * List user chat sessions
   * 
   * List user chat sessions with filtering.
   */
  async adminSessionsList(...args: any[]): Promise<Models.PaginatedChatSessionList> {
    const isParamsObject = args.length === 1 && typeof args[0] === 'object' && args[0] !== null && !Array.isArray(args[0]);
    
    let params;
    if (isParamsObject) {
      params = args[0];
    } else {
      params = { page: args[0], page_size: args[1] };
    }
    const response = await this.client.request('GET', "/cfg/knowbase/admin/sessions/", { params });
    return response;
  }

  /**
   * Create new chat session
   * 
   * Create new chat session.
   */
  async adminSessionsCreate(data: Models.ChatSessionCreateRequest): Promise<Models.ChatSession> {
    const response = await this.client.request('POST', "/cfg/knowbase/admin/sessions/", { body: data });
    return response;
  }

  /**
   * Chat session management endpoints.
   */
  async adminSessionsRetrieve(id: string): Promise<Models.ChatSession> {
    const response = await this.client.request('GET', `/cfg/knowbase/admin/sessions/${id}/`);
    return response;
  }

  /**
   * Chat session management endpoints.
   */
  async adminSessionsUpdate(id: string, data: Models.ChatSessionRequest): Promise<Models.ChatSession> {
    const response = await this.client.request('PUT', `/cfg/knowbase/admin/sessions/${id}/`, { body: data });
    return response;
  }

  /**
   * Chat session management endpoints.
   */
  async adminSessionsPartialUpdate(id: string, data?: Models.PatchedChatSessionRequest): Promise<Models.ChatSession> {
    const response = await this.client.request('PATCH', `/cfg/knowbase/admin/sessions/${id}/`, { body: data });
    return response;
  }

  /**
   * Chat session management endpoints.
   */
  async adminSessionsDestroy(id: string): Promise<void> {
    const response = await this.client.request('DELETE', `/cfg/knowbase/admin/sessions/${id}/`);
    return;
  }

  /**
   * Activate chat session
   * 
   * Activate chat session.
   */
  async adminSessionsActivateCreate(id: string, data: Models.ChatSessionRequest): Promise<Models.ChatSession> {
    const response = await this.client.request('POST', `/cfg/knowbase/admin/sessions/${id}/activate/`, { body: data });
    return response;
  }

  /**
   * Archive chat session
   * 
   * Archive (deactivate) chat session.
   */
  async adminSessionsArchiveCreate(id: string, data: Models.ChatSessionRequest): Promise<Models.ChatSession> {
    const response = await this.client.request('POST', `/cfg/knowbase/admin/sessions/${id}/archive/`, { body: data });
    return response;
  }

  async categoriesList(page?: number, page_size?: number): Promise<Models.PaginatedPublicCategoryList>;
  async categoriesList(params?: { page?: number; page_size?: number }): Promise<Models.PaginatedPublicCategoryList>;

  /**
   * List public categories
   * 
   * Get list of all public categories
   */
  async categoriesList(...args: any[]): Promise<Models.PaginatedPublicCategoryList> {
    const isParamsObject = args.length === 1 && typeof args[0] === 'object' && args[0] !== null && !Array.isArray(args[0]);
    
    let params;
    if (isParamsObject) {
      params = args[0];
    } else {
      params = { page: args[0], page_size: args[1] };
    }
    const response = await this.client.request('GET', "/cfg/knowbase/categories/", { params });
    return response;
  }

  /**
   * Get public category details
   * 
   * Get category details by ID (public access)
   */
  async categoriesRetrieve(id: string): Promise<Models.PublicCategory> {
    const response = await this.client.request('GET', `/cfg/knowbase/categories/${id}/`);
    return response;
  }

  async documentsList(category?: string, page?: number, page_size?: number, search?: string): Promise<Models.PaginatedPublicDocumentListList>;
  async documentsList(params?: { category?: string; page?: number; page_size?: number; search?: string }): Promise<Models.PaginatedPublicDocumentListList>;

  /**
   * List public documents
   * 
   * Get list of all completed and publicly accessible documents
   */
  async documentsList(...args: any[]): Promise<Models.PaginatedPublicDocumentListList> {
    const isParamsObject = args.length === 1 && typeof args[0] === 'object' && args[0] !== null && !Array.isArray(args[0]);
    
    let params;
    if (isParamsObject) {
      params = args[0];
    } else {
      params = { category: args[0], page: args[1], page_size: args[2], search: args[3] };
    }
    const response = await this.client.request('GET', "/cfg/knowbase/documents/", { params });
    return response;
  }

  /**
   * Get public document details
   * 
   * Get document details by ID (public access)
   */
  async documentsRetrieve(id: string): Promise<Models.PublicDocument> {
    const response = await this.client.request('GET', `/cfg/knowbase/documents/${id}/`);
    return response;
  }

  async systemArchivesList(page?: number, page_size?: number): Promise<Models.PaginatedDocumentArchiveListList>;
  async systemArchivesList(params?: { page?: number; page_size?: number }): Promise<Models.PaginatedDocumentArchiveListList>;

  /**
   * Document archive management endpoints - Admin only.
   */
  async systemArchivesList(...args: any[]): Promise<Models.PaginatedDocumentArchiveListList> {
    const isParamsObject = args.length === 1 && typeof args[0] === 'object' && args[0] !== null && !Array.isArray(args[0]);
    
    let params;
    if (isParamsObject) {
      params = args[0];
    } else {
      params = { page: args[0], page_size: args[1] };
    }
    const response = await this.client.request('GET', "/cfg/knowbase/system/archives/", { params });
    return response;
  }

  /**
   * Upload and process archive
   * 
   * Upload archive file and process it synchronously
   */
  async systemArchivesCreate(data: FormData): Promise<Models.ArchiveProcessingResult> {
    const response = await this.client.request('POST', "/cfg/knowbase/system/archives/", { formData: data });
    return response;
  }

  /**
   * Document archive management endpoints - Admin only.
   */
  async systemArchivesRetrieve(id: string): Promise<Models.DocumentArchiveDetail> {
    const response = await this.client.request('GET', `/cfg/knowbase/system/archives/${id}/`);
    return response;
  }

  /**
   * Document archive management endpoints - Admin only.
   */
  async systemArchivesUpdate(id: string, data: Models.DocumentArchiveRequest): Promise<Models.DocumentArchive> {
    const formData = new FormData();
    formData.append('title', String(data.title));
    if (data.description !== undefined) formData.append('description', String(data.description));
    if (data.is_public !== undefined) formData.append('is_public', String(data.is_public));
    const response = await this.client.request('PUT', `/cfg/knowbase/system/archives/${id}/`, { formData });
    return response;
  }

  /**
   * Document archive management endpoints - Admin only.
   */
  async systemArchivesPartialUpdate(id: string, data?: Models.PatchedDocumentArchiveRequest): Promise<Models.DocumentArchive> {
    const response = await this.client.request('PATCH', `/cfg/knowbase/system/archives/${id}/`, { body: data });
    return response;
  }

  /**
   * Document archive management endpoints - Admin only.
   */
  async systemArchivesDestroy(id: string): Promise<void> {
    const response = await this.client.request('DELETE', `/cfg/knowbase/system/archives/${id}/`);
    return;
  }

  /**
   * Get archive file tree
   * 
   * Get hierarchical file tree structure
   */
  async systemArchivesFileTreeRetrieve(id: string): Promise<any> {
    const response = await this.client.request('GET', `/cfg/knowbase/system/archives/${id}/file_tree/`);
    return response;
  }

  async systemArchivesItemsList(id: string, page?: number, page_size?: number): Promise<Models.PaginatedArchiveItemList>;
  async systemArchivesItemsList(id: string, params?: { page?: number; page_size?: number }): Promise<Models.PaginatedArchiveItemList>;

  /**
   * Get archive items
   * 
   * Get all items in the archive
   */
  async systemArchivesItemsList(...args: any[]): Promise<Models.PaginatedArchiveItemList> {
    const id = args[0];
    const isParamsObject = args.length === 2 && typeof args[1] === 'object' && args[1] !== null && !Array.isArray(args[1]);
    
    let params;
    if (isParamsObject) {
      params = args[1];
    } else {
      params = { page: args[1], page_size: args[2] };
    }
    const response = await this.client.request('GET', `/cfg/knowbase/system/archives/${id}/items/`, { params });
    return response;
  }

  async systemArchivesSearchCreate(id: string, data: Models.ArchiveSearchRequestRequest, page?: number, page_size?: number): Promise<Models.PaginatedArchiveSearchResultList>;
  async systemArchivesSearchCreate(id: string, data: Models.ArchiveSearchRequestRequest, params?: { page?: number; page_size?: number }): Promise<Models.PaginatedArchiveSearchResultList>;

  /**
   * Search archive chunks
   * 
   * Semantic search within archive chunks
   */
  async systemArchivesSearchCreate(...args: any[]): Promise<Models.PaginatedArchiveSearchResultList> {
    const id = args[0];
    const data = args[1];
    const isParamsObject = args.length === 3 && typeof args[2] === 'object' && args[2] !== null && !Array.isArray(args[2]);
    
    let params;
    if (isParamsObject) {
      params = args[2];
    } else {
      params = { page: args[2], page_size: args[3] };
    }
    const formData = new FormData();
    formData.append('query', String(data.query));
    if (data.content_types !== undefined) formData.append('content_types', String(data.content_types));
    if (data.languages !== undefined) formData.append('languages', String(data.languages));
    if (data.chunk_types !== undefined) formData.append('chunk_types', String(data.chunk_types));
    if (data.archive_ids !== undefined) formData.append('archive_ids', String(data.archive_ids));
    if (data.limit !== undefined) formData.append('limit', String(data.limit));
    if (data.similarity_threshold !== undefined) formData.append('similarity_threshold', String(data.similarity_threshold));
    const response = await this.client.request('POST', `/cfg/knowbase/system/archives/${id}/search/`, { params, formData });
    return response;
  }

  /**
   * Re-vectorize chunks
   * 
   * Re-vectorize specific chunks
   */
  async systemArchivesRevectorizeCreate(data: Models.ChunkRevectorizationRequestRequest): Promise<Models.VectorizationResult> {
    const formData = new FormData();
    formData.append('chunk_ids', String(data.chunk_ids));
    if (data.force !== undefined) formData.append('force', String(data.force));
    const response = await this.client.request('POST', "/cfg/knowbase/system/archives/revectorize/", { formData });
    return response;
  }

  /**
   * Get archive statistics
   * 
   * Get processing and vectorization statistics
   */
  async systemArchivesStatisticsRetrieve(): Promise<Models.ArchiveStatistics> {
    const response = await this.client.request('GET', "/cfg/knowbase/system/archives/statistics/");
    return response;
  }

  /**
   * Get vectorization statistics
   * 
   * Get vectorization statistics for archives
   */
  async systemArchivesVectorizationStatsRetrieve(): Promise<Models.VectorizationStatistics> {
    const response = await this.client.request('GET', "/cfg/knowbase/system/archives/vectorization_stats/");
    return response;
  }

  async systemChunksList(page?: number, page_size?: number): Promise<Models.PaginatedArchiveItemChunkList>;
  async systemChunksList(params?: { page?: number; page_size?: number }): Promise<Models.PaginatedArchiveItemChunkList>;

  /**
   * Archive item chunk management endpoints - Admin only.
   */
  async systemChunksList(...args: any[]): Promise<Models.PaginatedArchiveItemChunkList> {
    const isParamsObject = args.length === 1 && typeof args[0] === 'object' && args[0] !== null && !Array.isArray(args[0]);
    
    let params;
    if (isParamsObject) {
      params = args[0];
    } else {
      params = { page: args[0], page_size: args[1] };
    }
    const response = await this.client.request('GET', "/cfg/knowbase/system/chunks/", { params });
    return response;
  }

  /**
   * Archive item chunk management endpoints - Admin only.
   */
  async systemChunksCreate(data: Models.ArchiveItemChunkRequest): Promise<Models.ArchiveItemChunk> {
    const response = await this.client.request('POST', "/cfg/knowbase/system/chunks/", { body: data });
    return response;
  }

  /**
   * Archive item chunk management endpoints - Admin only.
   */
  async systemChunksRetrieve(id: string): Promise<Models.ArchiveItemChunkDetail> {
    const response = await this.client.request('GET', `/cfg/knowbase/system/chunks/${id}/`);
    return response;
  }

  /**
   * Archive item chunk management endpoints - Admin only.
   */
  async systemChunksUpdate(id: string, data: Models.ArchiveItemChunkRequest): Promise<Models.ArchiveItemChunk> {
    const response = await this.client.request('PUT', `/cfg/knowbase/system/chunks/${id}/`, { body: data });
    return response;
  }

  /**
   * Archive item chunk management endpoints - Admin only.
   */
  async systemChunksPartialUpdate(id: string, data?: Models.PatchedArchiveItemChunkRequest): Promise<Models.ArchiveItemChunk> {
    const response = await this.client.request('PATCH', `/cfg/knowbase/system/chunks/${id}/`, { body: data });
    return response;
  }

  /**
   * Archive item chunk management endpoints - Admin only.
   */
  async systemChunksDestroy(id: string): Promise<void> {
    const response = await this.client.request('DELETE', `/cfg/knowbase/system/chunks/${id}/`);
    return;
  }

  /**
   * Get chunk context
   * 
   * Get full context metadata for chunk
   */
  async systemChunksContextRetrieve(id: string): Promise<Models.ArchiveItemChunkDetail> {
    const response = await this.client.request('GET', `/cfg/knowbase/system/chunks/${id}/context/`);
    return response;
  }

  /**
   * Vectorize chunk
   * 
   * Generate embedding for specific chunk
   */
  async systemChunksVectorizeCreate(id: string, data: Models.ArchiveItemChunkRequest): Promise<any> {
    const response = await this.client.request('POST', `/cfg/knowbase/system/chunks/${id}/vectorize/`, { body: data });
    return response;
  }

  async systemItemsList(page?: number, page_size?: number): Promise<Models.PaginatedArchiveItemList>;
  async systemItemsList(params?: { page?: number; page_size?: number }): Promise<Models.PaginatedArchiveItemList>;

  /**
   * Archive item management endpoints - Admin only.
   */
  async systemItemsList(...args: any[]): Promise<Models.PaginatedArchiveItemList> {
    const isParamsObject = args.length === 1 && typeof args[0] === 'object' && args[0] !== null && !Array.isArray(args[0]);
    
    let params;
    if (isParamsObject) {
      params = args[0];
    } else {
      params = { page: args[0], page_size: args[1] };
    }
    const response = await this.client.request('GET', "/cfg/knowbase/system/items/", { params });
    return response;
  }

  /**
   * Archive item management endpoints - Admin only.
   */
  async systemItemsCreate(data: Models.ArchiveItemRequest): Promise<Models.ArchiveItem> {
    const response = await this.client.request('POST', "/cfg/knowbase/system/items/", { body: data });
    return response;
  }

  /**
   * Archive item management endpoints - Admin only.
   */
  async systemItemsRetrieve(id: string): Promise<Models.ArchiveItemDetail> {
    const response = await this.client.request('GET', `/cfg/knowbase/system/items/${id}/`);
    return response;
  }

  /**
   * Archive item management endpoints - Admin only.
   */
  async systemItemsUpdate(id: string, data: Models.ArchiveItemRequest): Promise<Models.ArchiveItem> {
    const response = await this.client.request('PUT', `/cfg/knowbase/system/items/${id}/`, { body: data });
    return response;
  }

  /**
   * Archive item management endpoints - Admin only.
   */
  async systemItemsPartialUpdate(id: string, data?: Models.PatchedArchiveItemRequest): Promise<Models.ArchiveItem> {
    const response = await this.client.request('PATCH', `/cfg/knowbase/system/items/${id}/`, { body: data });
    return response;
  }

  /**
   * Archive item management endpoints - Admin only.
   */
  async systemItemsDestroy(id: string): Promise<void> {
    const response = await this.client.request('DELETE', `/cfg/knowbase/system/items/${id}/`);
    return;
  }

  async systemItemsChunksList(id: string, page?: number, page_size?: number): Promise<Models.PaginatedArchiveItemChunkList>;
  async systemItemsChunksList(id: string, params?: { page?: number; page_size?: number }): Promise<Models.PaginatedArchiveItemChunkList>;

  /**
   * Get item chunks
   * 
   * Get all chunks for this item
   */
  async systemItemsChunksList(...args: any[]): Promise<Models.PaginatedArchiveItemChunkList> {
    const id = args[0];
    const isParamsObject = args.length === 2 && typeof args[1] === 'object' && args[1] !== null && !Array.isArray(args[1]);
    
    let params;
    if (isParamsObject) {
      params = args[1];
    } else {
      params = { page: args[1], page_size: args[2] };
    }
    const response = await this.client.request('GET', `/cfg/knowbase/system/items/${id}/chunks/`, { params });
    return response;
  }

  /**
   * Get item content
   * 
   * Get full content of archive item
   */
  async systemItemsContentRetrieve(id: string): Promise<Models.ArchiveItemDetail> {
    const response = await this.client.request('GET', `/cfg/knowbase/system/items/${id}/content/`);
    return response;
  }

}