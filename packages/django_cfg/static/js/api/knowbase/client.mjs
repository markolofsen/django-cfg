import { BaseAPIClient } from '../base.mjs';

/**
 * Knowbase API Client
 * Auto-generated from OpenAPI schema
 * @module knowbase
 * @extends BaseAPIClient
 */
export class KnowbaseAPI extends BaseAPIClient {
    /**
     * Initialize knowbase API client
     * @param {string} [baseURL] - Optional base URL
     */
    constructor(baseURL) {
        super(baseURL);
    }

    /**
     * knowbaseAdminChatList     * Chat query endpoints.     * @param {Object} [params={}] - Query parameters     * @param {number} [params.page] - A page number within the paginated result set.     * @param {number} [params.page_size] - Number of results to return per page.     * @returns {Promise<PaginatedChatResponseList>} Response data
     */
    async knowbaseAdminChatList(params = {}) {
        const path = `/cfg/knowbase/admin/chat/`;        return this.get(path, params);    }
    /**
     * knowbaseAdminChatCreate     * Chat query endpoints.     * @param {ChatResponseRequest} data - Request body     * @returns {Promise<ChatResponse>} Response data
     */
    async knowbaseAdminChatCreate(data) {
        const path = `/cfg/knowbase/admin/chat/`;        return this.post(path, data);    }
    /**
     * knowbaseAdminChatRetrieve     * Chat query endpoints.     * @param {string} id - A UUID string identifying this chat session.     * @returns {Promise<ChatResponse>} Response data
     */
    async knowbaseAdminChatRetrieve(id) {
        const path = `/cfg/knowbase/admin/chat/${id}/`;        return this.get(path);    }
    /**
     * knowbaseAdminChatUpdate     * Chat query endpoints.     * @param {string} id - A UUID string identifying this chat session.     * @param {ChatResponseRequest} data - Request body     * @returns {Promise<ChatResponse>} Response data
     */
    async knowbaseAdminChatUpdate(id, data) {
        const path = `/cfg/knowbase/admin/chat/${id}/`;        return this.put(path, data);    }
    /**
     * knowbaseAdminChatPartialUpdate     * Chat query endpoints.     * @param {string} id - A UUID string identifying this chat session.     * @param {PatchedChatResponseRequest} data - Request body     * @returns {Promise<ChatResponse>} Response data
     */
    async knowbaseAdminChatPartialUpdate(id, data) {
        const path = `/cfg/knowbase/admin/chat/${id}/`;        return this.patch(path, data);    }
    /**
     * knowbaseAdminChatDestroy     * Chat query endpoints.     * @param {string} id - A UUID string identifying this chat session.     * @returns {Promise<void>} No content
     */
    async knowbaseAdminChatDestroy(id) {
        const path = `/cfg/knowbase/admin/chat/${id}/`;        return this.delete(path);    }
    /**
     * Get chat history     * Get chat session history.     * @param {string} id - A UUID string identifying this chat session.     * @returns {Promise<ChatHistory>} Response data
     */
    async knowbaseAdminChatHistoryRetrieve(id) {
        const path = `/cfg/knowbase/admin/chat/${id}/history/`;        return this.get(path);    }
    /**
     * Process chat query with RAG     * Process chat query with RAG context.     * @param {ChatQueryRequest} data - Request body     * @returns {Promise<ChatResponse>} Response data
     */
    async knowbaseAdminChatQueryCreate(data) {
        const path = `/cfg/knowbase/admin/chat/query/`;        return this.post(path, data);    }
    /**
     * List user documents     * List user documents with filtering and pagination.     * @param {Object} [params={}] - Query parameters     * @param {number} [params.page] - A page number within the paginated result set.     * @param {number} [params.page_size] - Number of results to return per page.     * @param {string} [params.status] - Filter by processing status     * @returns {Promise<PaginatedDocumentList>} Response data
     */
    async knowbaseAdminDocumentsList(params = {}) {
        const path = `/cfg/knowbase/admin/documents/`;        return this.get(path, params);    }
    /**
     * Upload new document     * Upload and process a new knowledge document     * @param {DocumentCreateRequest} data - Request body     * @returns {Promise<Document>} Response data
     */
    async knowbaseAdminDocumentsCreate(data) {
        const path = `/cfg/knowbase/admin/documents/`;        return this.post(path, data);    }
    /**
     * Get document details     * Get document by ID.     * @param {string} id - A UUID string identifying this document.     * @returns {Promise<Document>} Response data
     */
    async knowbaseAdminDocumentsRetrieve(id) {
        const path = `/cfg/knowbase/admin/documents/${id}/`;        return this.get(path);    }
    /**
     * knowbaseAdminDocumentsUpdate     * Document management endpoints - Admin only.     * @param {string} id - A UUID string identifying this document.     * @param {DocumentRequest} data - Request body     * @returns {Promise<Document>} Response data
     */
    async knowbaseAdminDocumentsUpdate(id, data) {
        const path = `/cfg/knowbase/admin/documents/${id}/`;        return this.put(path, data);    }
    /**
     * knowbaseAdminDocumentsPartialUpdate     * Document management endpoints - Admin only.     * @param {string} id - A UUID string identifying this document.     * @param {PatchedDocumentRequest} data - Request body     * @returns {Promise<Document>} Response data
     */
    async knowbaseAdminDocumentsPartialUpdate(id, data) {
        const path = `/cfg/knowbase/admin/documents/${id}/`;        return this.patch(path, data);    }
    /**
     * Delete document     * Delete document and all associated chunks.     * @param {string} id - A UUID string identifying this document.     * @returns {Promise<void>} No content
     */
    async knowbaseAdminDocumentsDestroy(id) {
        const path = `/cfg/knowbase/admin/documents/${id}/`;        return this.delete(path);    }
    /**
     * Reprocess document     * Trigger reprocessing of document chunks and embeddings     * @param {string} id - A UUID string identifying this document.     * @param {DocumentRequest} data - Request body     * @returns {Promise<Document>} Response data
     */
    async knowbaseAdminDocumentsReprocessCreate(id, data) {
        const path = `/cfg/knowbase/admin/documents/${id}/reprocess/`;        return this.post(path, data);    }
    /**
     * Get document processing status     * Get document processing status.     * @param {string} id - A UUID string identifying this document.     * @returns {Promise<DocumentProcessingStatus>} Response data
     */
    async knowbaseAdminDocumentsStatusRetrieve(id) {
        const path = `/cfg/knowbase/admin/documents/${id}/status/`;        return this.get(path);    }
    /**
     * Get processing statistics     * Get user's document processing statistics.     * @returns {Promise<DocumentStats>} Response data
     */
    async knowbaseAdminDocumentsStatsRetrieve() {
        const path = `/cfg/knowbase/admin/documents/stats/`;        return this.get(path);    }
    /**
     * List user chat sessions     * List user chat sessions with filtering.     * @param {Object} [params={}] - Query parameters     * @param {number} [params.page] - A page number within the paginated result set.     * @param {number} [params.page_size] - Number of results to return per page.     * @returns {Promise<PaginatedChatSessionList>} Response data
     */
    async knowbaseAdminSessionsList(params = {}) {
        const path = `/cfg/knowbase/admin/sessions/`;        return this.get(path, params);    }
    /**
     * Create new chat session     * Create new chat session.     * @param {ChatSessionCreateRequest} data - Request body     * @returns {Promise<ChatSession>} Response data
     */
    async knowbaseAdminSessionsCreate(data) {
        const path = `/cfg/knowbase/admin/sessions/`;        return this.post(path, data);    }
    /**
     * knowbaseAdminSessionsRetrieve     * Chat session management endpoints.     * @param {string} id - A UUID string identifying this chat session.     * @returns {Promise<ChatSession>} Response data
     */
    async knowbaseAdminSessionsRetrieve(id) {
        const path = `/cfg/knowbase/admin/sessions/${id}/`;        return this.get(path);    }
    /**
     * knowbaseAdminSessionsUpdate     * Chat session management endpoints.     * @param {string} id - A UUID string identifying this chat session.     * @param {ChatSessionRequest} data - Request body     * @returns {Promise<ChatSession>} Response data
     */
    async knowbaseAdminSessionsUpdate(id, data) {
        const path = `/cfg/knowbase/admin/sessions/${id}/`;        return this.put(path, data);    }
    /**
     * knowbaseAdminSessionsPartialUpdate     * Chat session management endpoints.     * @param {string} id - A UUID string identifying this chat session.     * @param {PatchedChatSessionRequest} data - Request body     * @returns {Promise<ChatSession>} Response data
     */
    async knowbaseAdminSessionsPartialUpdate(id, data) {
        const path = `/cfg/knowbase/admin/sessions/${id}/`;        return this.patch(path, data);    }
    /**
     * knowbaseAdminSessionsDestroy     * Chat session management endpoints.     * @param {string} id - A UUID string identifying this chat session.     * @returns {Promise<void>} No content
     */
    async knowbaseAdminSessionsDestroy(id) {
        const path = `/cfg/knowbase/admin/sessions/${id}/`;        return this.delete(path);    }
    /**
     * Activate chat session     * Activate chat session.     * @param {string} id - A UUID string identifying this chat session.     * @param {ChatSessionRequest} data - Request body     * @returns {Promise<ChatSession>} Response data
     */
    async knowbaseAdminSessionsActivateCreate(id, data) {
        const path = `/cfg/knowbase/admin/sessions/${id}/activate/`;        return this.post(path, data);    }
    /**
     * Archive chat session     * Archive (deactivate) chat session.     * @param {string} id - A UUID string identifying this chat session.     * @param {ChatSessionRequest} data - Request body     * @returns {Promise<ChatSession>} Response data
     */
    async knowbaseAdminSessionsArchiveCreate(id, data) {
        const path = `/cfg/knowbase/admin/sessions/${id}/archive/`;        return this.post(path, data);    }
    /**
     * List public categories     * Get list of all public categories     * @param {Object} [params={}] - Query parameters     * @param {number} [params.page] - A page number within the paginated result set.     * @param {number} [params.page_size] - Number of results to return per page.     * @returns {Promise<PaginatedPublicCategoryList>} Response data
     */
    async knowbaseCategoriesList(params = {}) {
        const path = `/cfg/knowbase/categories/`;        return this.get(path, params);    }
    /**
     * Get public category details     * Get category details by ID (public access)     * @param {string} id - A UUID string identifying this Document Category.     * @returns {Promise<PublicCategory>} Response data
     */
    async knowbaseCategoriesRetrieve(id) {
        const path = `/cfg/knowbase/categories/${id}/`;        return this.get(path);    }
    /**
     * List public documents     * Get list of all completed and publicly accessible documents     * @param {Object} [params={}] - Query parameters     * @param {string} [params.category] - Filter by category name     * @param {number} [params.page] - A page number within the paginated result set.     * @param {number} [params.page_size] - Number of results to return per page.     * @param {string} [params.search] - Search in title and content     * @returns {Promise<PaginatedPublicDocumentListList>} Response data
     */
    async knowbaseDocumentsList(params = {}) {
        const path = `/cfg/knowbase/documents/`;        return this.get(path, params);    }
    /**
     * Get public document details     * Get document details by ID (public access)     * @param {string} id - A UUID string identifying this document.     * @returns {Promise<PublicDocument>} Response data
     */
    async knowbaseDocumentsRetrieve(id) {
        const path = `/cfg/knowbase/documents/${id}/`;        return this.get(path);    }
    /**
     * knowbaseSystemArchivesList     * Document archive management endpoints - Admin only.     * @param {Object} [params={}] - Query parameters     * @param {number} [params.page] - A page number within the paginated result set.     * @param {number} [params.page_size] - Number of results to return per page.     * @returns {Promise<PaginatedDocumentArchiveListList>} Response data
     */
    async knowbaseSystemArchivesList(params = {}) {
        const path = `/cfg/knowbase/system/archives/`;        return this.get(path, params);    }
    /**
     * Upload and process archive     * Upload archive file and process it synchronously     * @param {any} data - Request body     * @returns {Promise<ArchiveProcessingResult>} Response data
     */
    async knowbaseSystemArchivesCreate(data) {
        const path = `/cfg/knowbase/system/archives/`;        return this.post(path, data);    }
    /**
     * knowbaseSystemArchivesRetrieve     * Document archive management endpoints - Admin only.     * @param {string} id - A UUID string identifying this Document Archive.     * @returns {Promise<DocumentArchiveDetail>} Response data
     */
    async knowbaseSystemArchivesRetrieve(id) {
        const path = `/cfg/knowbase/system/archives/${id}/`;        return this.get(path);    }
    /**
     * knowbaseSystemArchivesUpdate     * Document archive management endpoints - Admin only.     * @param {string} id - A UUID string identifying this Document Archive.     * @param {DocumentArchiveRequest} data - Request body     * @returns {Promise<DocumentArchive>} Response data
     */
    async knowbaseSystemArchivesUpdate(id, data) {
        const path = `/cfg/knowbase/system/archives/${id}/`;        return this.put(path, data);    }
    /**
     * knowbaseSystemArchivesPartialUpdate     * Document archive management endpoints - Admin only.     * @param {string} id - A UUID string identifying this Document Archive.     * @param {PatchedDocumentArchiveRequest} data - Request body     * @returns {Promise<DocumentArchive>} Response data
     */
    async knowbaseSystemArchivesPartialUpdate(id, data) {
        const path = `/cfg/knowbase/system/archives/${id}/`;        return this.patch(path, data);    }
    /**
     * knowbaseSystemArchivesDestroy     * Document archive management endpoints - Admin only.     * @param {string} id - A UUID string identifying this Document Archive.     * @returns {Promise<void>} No content
     */
    async knowbaseSystemArchivesDestroy(id) {
        const path = `/cfg/knowbase/system/archives/${id}/`;        return this.delete(path);    }
    /**
     * Get archive file tree     * Get hierarchical file tree structure     * @param {string} id - A UUID string identifying this Document Archive.     * @returns {Promise<Object>} Response data
     */
    async knowbaseSystemArchivesFileTreeRetrieve(id) {
        const path = `/cfg/knowbase/system/archives/${id}/file_tree/`;        return this.get(path);    }
    /**
     * Get archive items     * Get all items in the archive     * @param {string} id - A UUID string identifying this Document Archive.     * @param {Object} [params={}] - Query parameters     * @param {number} [params.page] - A page number within the paginated result set.     * @param {number} [params.page_size] - Number of results to return per page.     * @returns {Promise<PaginatedArchiveItemList>} Response data
     */
    async knowbaseSystemArchivesItemsList(id, params = {}) {
        const path = `/cfg/knowbase/system/archives/${id}/items/`;        return this.get(path, params);    }
    /**
     * Search archive chunks     * Semantic search within archive chunks     * @param {string} id - A UUID string identifying this Document Archive.     * @param {ArchiveSearchRequestRequest} data - Request body     * @param {Object} [params={}] - Query parameters     * @param {number} [params.page] - A page number within the paginated result set.     * @param {number} [params.page_size] - Number of results to return per page.     * @returns {Promise<PaginatedArchiveSearchResultList>} Response data
     */
    async knowbaseSystemArchivesSearchCreate(id, data, params = {}) {
        const path = `/cfg/knowbase/system/archives/${id}/search/`;        return this.post(path, data);    }
    /**
     * Re-vectorize chunks     * Re-vectorize specific chunks     * @param {ChunkRevectorizationRequestRequest} data - Request body     * @returns {Promise<VectorizationResult>} Response data
     */
    async knowbaseSystemArchivesRevectorizeCreate(data) {
        const path = `/cfg/knowbase/system/archives/revectorize/`;        return this.post(path, data);    }
    /**
     * Get archive statistics     * Get processing and vectorization statistics     * @returns {Promise<ArchiveStatistics>} Response data
     */
    async knowbaseSystemArchivesStatisticsRetrieve() {
        const path = `/cfg/knowbase/system/archives/statistics/`;        return this.get(path);    }
    /**
     * Get vectorization statistics     * Get vectorization statistics for archives     * @returns {Promise<VectorizationStatistics>} Response data
     */
    async knowbaseSystemArchivesVectorizationStatsRetrieve() {
        const path = `/cfg/knowbase/system/archives/vectorization_stats/`;        return this.get(path);    }
    /**
     * knowbaseSystemChunksList     * Archive item chunk management endpoints - Admin only.     * @param {Object} [params={}] - Query parameters     * @param {number} [params.page] - A page number within the paginated result set.     * @param {number} [params.page_size] - Number of results to return per page.     * @returns {Promise<PaginatedArchiveItemChunkList>} Response data
     */
    async knowbaseSystemChunksList(params = {}) {
        const path = `/cfg/knowbase/system/chunks/`;        return this.get(path, params);    }
    /**
     * knowbaseSystemChunksCreate     * Archive item chunk management endpoints - Admin only.     * @param {ArchiveItemChunkRequest} data - Request body     * @returns {Promise<ArchiveItemChunk>} Response data
     */
    async knowbaseSystemChunksCreate(data) {
        const path = `/cfg/knowbase/system/chunks/`;        return this.post(path, data);    }
    /**
     * knowbaseSystemChunksRetrieve     * Archive item chunk management endpoints - Admin only.     * @param {string} id - A UUID string identifying this Archive Item Chunk.     * @returns {Promise<ArchiveItemChunkDetail>} Response data
     */
    async knowbaseSystemChunksRetrieve(id) {
        const path = `/cfg/knowbase/system/chunks/${id}/`;        return this.get(path);    }
    /**
     * knowbaseSystemChunksUpdate     * Archive item chunk management endpoints - Admin only.     * @param {string} id - A UUID string identifying this Archive Item Chunk.     * @param {ArchiveItemChunkRequest} data - Request body     * @returns {Promise<ArchiveItemChunk>} Response data
     */
    async knowbaseSystemChunksUpdate(id, data) {
        const path = `/cfg/knowbase/system/chunks/${id}/`;        return this.put(path, data);    }
    /**
     * knowbaseSystemChunksPartialUpdate     * Archive item chunk management endpoints - Admin only.     * @param {string} id - A UUID string identifying this Archive Item Chunk.     * @param {PatchedArchiveItemChunkRequest} data - Request body     * @returns {Promise<ArchiveItemChunk>} Response data
     */
    async knowbaseSystemChunksPartialUpdate(id, data) {
        const path = `/cfg/knowbase/system/chunks/${id}/`;        return this.patch(path, data);    }
    /**
     * knowbaseSystemChunksDestroy     * Archive item chunk management endpoints - Admin only.     * @param {string} id - A UUID string identifying this Archive Item Chunk.     * @returns {Promise<void>} No content
     */
    async knowbaseSystemChunksDestroy(id) {
        const path = `/cfg/knowbase/system/chunks/${id}/`;        return this.delete(path);    }
    /**
     * Get chunk context     * Get full context metadata for chunk     * @param {string} id - A UUID string identifying this Archive Item Chunk.     * @returns {Promise<ArchiveItemChunkDetail>} Response data
     */
    async knowbaseSystemChunksContextRetrieve(id) {
        const path = `/cfg/knowbase/system/chunks/${id}/context/`;        return this.get(path);    }
    /**
     * Vectorize chunk     * Generate embedding for specific chunk     * @param {string} id - A UUID string identifying this Archive Item Chunk.     * @param {ArchiveItemChunkRequest} data - Request body     * @returns {Promise<Object>} Response data
     */
    async knowbaseSystemChunksVectorizeCreate(id, data) {
        const path = `/cfg/knowbase/system/chunks/${id}/vectorize/`;        return this.post(path, data);    }
    /**
     * knowbaseSystemItemsList     * Archive item management endpoints - Admin only.     * @param {Object} [params={}] - Query parameters     * @param {number} [params.page] - A page number within the paginated result set.     * @param {number} [params.page_size] - Number of results to return per page.     * @returns {Promise<PaginatedArchiveItemList>} Response data
     */
    async knowbaseSystemItemsList(params = {}) {
        const path = `/cfg/knowbase/system/items/`;        return this.get(path, params);    }
    /**
     * knowbaseSystemItemsCreate     * Archive item management endpoints - Admin only.     * @param {ArchiveItemRequest} data - Request body     * @returns {Promise<ArchiveItem>} Response data
     */
    async knowbaseSystemItemsCreate(data) {
        const path = `/cfg/knowbase/system/items/`;        return this.post(path, data);    }
    /**
     * knowbaseSystemItemsRetrieve     * Archive item management endpoints - Admin only.     * @param {string} id - A UUID string identifying this Archive Item.     * @returns {Promise<ArchiveItemDetail>} Response data
     */
    async knowbaseSystemItemsRetrieve(id) {
        const path = `/cfg/knowbase/system/items/${id}/`;        return this.get(path);    }
    /**
     * knowbaseSystemItemsUpdate     * Archive item management endpoints - Admin only.     * @param {string} id - A UUID string identifying this Archive Item.     * @param {ArchiveItemRequest} data - Request body     * @returns {Promise<ArchiveItem>} Response data
     */
    async knowbaseSystemItemsUpdate(id, data) {
        const path = `/cfg/knowbase/system/items/${id}/`;        return this.put(path, data);    }
    /**
     * knowbaseSystemItemsPartialUpdate     * Archive item management endpoints - Admin only.     * @param {string} id - A UUID string identifying this Archive Item.     * @param {PatchedArchiveItemRequest} data - Request body     * @returns {Promise<ArchiveItem>} Response data
     */
    async knowbaseSystemItemsPartialUpdate(id, data) {
        const path = `/cfg/knowbase/system/items/${id}/`;        return this.patch(path, data);    }
    /**
     * knowbaseSystemItemsDestroy     * Archive item management endpoints - Admin only.     * @param {string} id - A UUID string identifying this Archive Item.     * @returns {Promise<void>} No content
     */
    async knowbaseSystemItemsDestroy(id) {
        const path = `/cfg/knowbase/system/items/${id}/`;        return this.delete(path);    }
    /**
     * Get item chunks     * Get all chunks for this item     * @param {string} id - A UUID string identifying this Archive Item.     * @param {Object} [params={}] - Query parameters     * @param {number} [params.page] - A page number within the paginated result set.     * @param {number} [params.page_size] - Number of results to return per page.     * @returns {Promise<PaginatedArchiveItemChunkList>} Response data
     */
    async knowbaseSystemItemsChunksList(id, params = {}) {
        const path = `/cfg/knowbase/system/items/${id}/chunks/`;        return this.get(path, params);    }
    /**
     * Get item content     * Get full content of archive item     * @param {string} id - A UUID string identifying this Archive Item.     * @returns {Promise<ArchiveItemDetail>} Response data
     */
    async knowbaseSystemItemsContentRetrieve(id) {
        const path = `/cfg/knowbase/system/items/${id}/content/`;        return this.get(path);    }
}

// Default instance for convenience
export const knowbaseAPI = new KnowbaseAPI();

// Default export
export default KnowbaseAPI;