/**
 * Typed fetchers for Knowbase
 *
 * Universal functions that work in any environment:
 * - Next.js (App Router / Pages Router / Server Components)
 * - React Native
 * - Node.js backend
 *
 * These fetchers use Zod schemas for runtime validation.
 *
 * Usage:
 * ```typescript
 * // Configure API once (in your app entry point)
 * import { configureAPI } from '../../api-instance'
 * configureAPI({ baseUrl: 'https://api.example.com' })
 *
 * // Then use fetchers anywhere
 * const users = await getUsers({ page: 1 })
 *
 * // With SWR
 * const { data } = useSWR(['users', params], () => getUsers(params))
 *
 * // With React Query
 * const { data } = useQuery(['users', params], () => getUsers(params))
 *
 * // In Server Component or SSR (pass custom client)
 * import { API } from '../../index'
 * const api = new API('https://api.example.com')
 * const users = await getUsers({ page: 1 }, api)
 * ```
 */
import { ArchiveItemSchema, type ArchiveItem } from '../schemas/ArchiveItem.schema'
import { ArchiveItemChunkSchema, type ArchiveItemChunk } from '../schemas/ArchiveItemChunk.schema'
import { ArchiveItemChunkDetailSchema, type ArchiveItemChunkDetail } from '../schemas/ArchiveItemChunkDetail.schema'
import { ArchiveItemChunkRequestSchema, type ArchiveItemChunkRequest } from '../schemas/ArchiveItemChunkRequest.schema'
import { ArchiveItemDetailSchema, type ArchiveItemDetail } from '../schemas/ArchiveItemDetail.schema'
import { ArchiveItemRequestSchema, type ArchiveItemRequest } from '../schemas/ArchiveItemRequest.schema'
import { ArchiveProcessingResultSchema, type ArchiveProcessingResult } from '../schemas/ArchiveProcessingResult.schema'
import { ArchiveSearchRequestRequestSchema, type ArchiveSearchRequestRequest } from '../schemas/ArchiveSearchRequestRequest.schema'
import { ArchiveStatisticsSchema, type ArchiveStatistics } from '../schemas/ArchiveStatistics.schema'
import { ChatHistorySchema, type ChatHistory } from '../schemas/ChatHistory.schema'
import { ChatQueryRequestSchema, type ChatQueryRequest } from '../schemas/ChatQueryRequest.schema'
import { ChatResponseSchema, type ChatResponse } from '../schemas/ChatResponse.schema'
import { ChatResponseRequestSchema, type ChatResponseRequest } from '../schemas/ChatResponseRequest.schema'
import { ChatSessionSchema, type ChatSession } from '../schemas/ChatSession.schema'
import { ChatSessionCreateRequestSchema, type ChatSessionCreateRequest } from '../schemas/ChatSessionCreateRequest.schema'
import { ChatSessionRequestSchema, type ChatSessionRequest } from '../schemas/ChatSessionRequest.schema'
import { ChunkRevectorizationRequestRequestSchema, type ChunkRevectorizationRequestRequest } from '../schemas/ChunkRevectorizationRequestRequest.schema'
import { DocumentSchema, type Document } from '../schemas/Document.schema'
import { DocumentArchiveSchema, type DocumentArchive } from '../schemas/DocumentArchive.schema'
import { DocumentArchiveDetailSchema, type DocumentArchiveDetail } from '../schemas/DocumentArchiveDetail.schema'
import { DocumentArchiveRequestSchema, type DocumentArchiveRequest } from '../schemas/DocumentArchiveRequest.schema'
import { DocumentCreateRequestSchema, type DocumentCreateRequest } from '../schemas/DocumentCreateRequest.schema'
import { DocumentProcessingStatusSchema, type DocumentProcessingStatus } from '../schemas/DocumentProcessingStatus.schema'
import { DocumentRequestSchema, type DocumentRequest } from '../schemas/DocumentRequest.schema'
import { DocumentStatsSchema, type DocumentStats } from '../schemas/DocumentStats.schema'
import { PaginatedArchiveItemChunkListSchema, type PaginatedArchiveItemChunkList } from '../schemas/PaginatedArchiveItemChunkList.schema'
import { PaginatedArchiveItemListSchema, type PaginatedArchiveItemList } from '../schemas/PaginatedArchiveItemList.schema'
import { PaginatedArchiveSearchResultListSchema, type PaginatedArchiveSearchResultList } from '../schemas/PaginatedArchiveSearchResultList.schema'
import { PaginatedChatResponseListSchema, type PaginatedChatResponseList } from '../schemas/PaginatedChatResponseList.schema'
import { PaginatedChatSessionListSchema, type PaginatedChatSessionList } from '../schemas/PaginatedChatSessionList.schema'
import { PaginatedDocumentArchiveListListSchema, type PaginatedDocumentArchiveListList } from '../schemas/PaginatedDocumentArchiveListList.schema'
import { PaginatedDocumentListSchema, type PaginatedDocumentList } from '../schemas/PaginatedDocumentList.schema'
import { PaginatedPublicCategoryListSchema, type PaginatedPublicCategoryList } from '../schemas/PaginatedPublicCategoryList.schema'
import { PaginatedPublicDocumentListListSchema, type PaginatedPublicDocumentListList } from '../schemas/PaginatedPublicDocumentListList.schema'
import { PatchedArchiveItemChunkRequestSchema, type PatchedArchiveItemChunkRequest } from '../schemas/PatchedArchiveItemChunkRequest.schema'
import { PatchedArchiveItemRequestSchema, type PatchedArchiveItemRequest } from '../schemas/PatchedArchiveItemRequest.schema'
import { PatchedChatResponseRequestSchema, type PatchedChatResponseRequest } from '../schemas/PatchedChatResponseRequest.schema'
import { PatchedChatSessionRequestSchema, type PatchedChatSessionRequest } from '../schemas/PatchedChatSessionRequest.schema'
import { PatchedDocumentArchiveRequestSchema, type PatchedDocumentArchiveRequest } from '../schemas/PatchedDocumentArchiveRequest.schema'
import { PatchedDocumentRequestSchema, type PatchedDocumentRequest } from '../schemas/PatchedDocumentRequest.schema'
import { PublicCategorySchema, type PublicCategory } from '../schemas/PublicCategory.schema'
import { PublicDocumentSchema, type PublicDocument } from '../schemas/PublicDocument.schema'
import { VectorizationResultSchema, type VectorizationResult } from '../schemas/VectorizationResult.schema'
import { VectorizationStatisticsSchema, type VectorizationStatistics } from '../schemas/VectorizationStatistics.schema'
import { getAPIInstance } from '../../api-instance'
import type { API } from '../../index'

/**
 * API operation
 *
 * @method GET
 * @path /cfg/knowbase/admin/chat/
 */
export async function getKnowbaseAdminChatList(  params?: { page?: number; page_size?: number },  client?: API
): Promise<PaginatedChatResponseList> {
  const api = client || getAPIInstance()
  const response = await api.cfg_knowbase.adminChatList(params?.page, params?.page_size)
  return PaginatedChatResponseListSchema.parse(response)
}


/**
 * API operation
 *
 * @method POST
 * @path /cfg/knowbase/admin/chat/
 */
export async function createKnowbaseAdminChatCreate(  data: ChatResponseRequest,  client?: API
): Promise<ChatResponse> {
  const api = client || getAPIInstance()
  const response = await api.cfg_knowbase.adminChatCreate(data)
  return ChatResponseSchema.parse(response)
}


/**
 * API operation
 *
 * @method GET
 * @path /cfg/knowbase/admin/chat/{id}/
 */
export async function getKnowbaseAdminChatRetrieve(  id: string,  client?: API
): Promise<ChatResponse> {
  const api = client || getAPIInstance()
  const response = await api.cfg_knowbase.adminChatRetrieve(id)
  return ChatResponseSchema.parse(response)
}


/**
 * API operation
 *
 * @method PUT
 * @path /cfg/knowbase/admin/chat/{id}/
 */
export async function updateKnowbaseAdminChatUpdate(  id: string, data: ChatResponseRequest,  client?: API
): Promise<ChatResponse> {
  const api = client || getAPIInstance()
  const response = await api.cfg_knowbase.adminChatUpdate(id, data)
  return ChatResponseSchema.parse(response)
}


/**
 * API operation
 *
 * @method PATCH
 * @path /cfg/knowbase/admin/chat/{id}/
 */
export async function partialUpdateKnowbaseAdminChatPartialUpdate(  id: string, data?: PatchedChatResponseRequest,  client?: API
): Promise<ChatResponse> {
  const api = client || getAPIInstance()
  const response = await api.cfg_knowbase.adminChatPartialUpdate(id, data)
  return ChatResponseSchema.parse(response)
}


/**
 * API operation
 *
 * @method DELETE
 * @path /cfg/knowbase/admin/chat/{id}/
 */
export async function deleteKnowbaseAdminChatDestroy(  id: string,  client?: API
): Promise<void> {
  const api = client || getAPIInstance()
  const response = await api.cfg_knowbase.adminChatDestroy(id)
  return response
}


/**
 * Get chat history
 *
 * @method GET
 * @path /cfg/knowbase/admin/chat/{id}/history/
 */
export async function getKnowbaseAdminChatHistoryRetrieve(  id: string,  client?: API
): Promise<ChatHistory> {
  const api = client || getAPIInstance()
  const response = await api.cfg_knowbase.adminChatHistoryRetrieve(id)
  return ChatHistorySchema.parse(response)
}


/**
 * Process chat query with RAG
 *
 * @method POST
 * @path /cfg/knowbase/admin/chat/query/
 */
export async function createKnowbaseAdminChatQueryCreate(  data: ChatQueryRequest,  client?: API
): Promise<ChatResponse> {
  const api = client || getAPIInstance()
  const response = await api.cfg_knowbase.adminChatQueryCreate(data)
  return ChatResponseSchema.parse(response)
}


/**
 * List user documents
 *
 * @method GET
 * @path /cfg/knowbase/admin/documents/
 */
export async function getKnowbaseAdminDocumentsList(  params?: { page?: number; page_size?: number; status?: string },  client?: API
): Promise<PaginatedDocumentList> {
  const api = client || getAPIInstance()
  const response = await api.cfg_knowbase.adminDocumentsList(params?.page, params?.page_size, params?.status)
  return PaginatedDocumentListSchema.parse(response)
}


/**
 * Upload new document
 *
 * @method POST
 * @path /cfg/knowbase/admin/documents/
 */
export async function createKnowbaseAdminDocumentsCreate(  data: DocumentCreateRequest,  client?: API
): Promise<Document> {
  const api = client || getAPIInstance()
  const response = await api.cfg_knowbase.adminDocumentsCreate(data)
  return DocumentSchema.parse(response)
}


/**
 * Get document details
 *
 * @method GET
 * @path /cfg/knowbase/admin/documents/{id}/
 */
export async function getKnowbaseAdminDocumentsRetrieve(  id: string,  client?: API
): Promise<Document> {
  const api = client || getAPIInstance()
  const response = await api.cfg_knowbase.adminDocumentsRetrieve(id)
  return DocumentSchema.parse(response)
}


/**
 * API operation
 *
 * @method PUT
 * @path /cfg/knowbase/admin/documents/{id}/
 */
export async function updateKnowbaseAdminDocumentsUpdate(  id: string, data: DocumentRequest,  client?: API
): Promise<Document> {
  const api = client || getAPIInstance()
  const response = await api.cfg_knowbase.adminDocumentsUpdate(id, data)
  return DocumentSchema.parse(response)
}


/**
 * API operation
 *
 * @method PATCH
 * @path /cfg/knowbase/admin/documents/{id}/
 */
export async function partialUpdateKnowbaseAdminDocumentsPartialUpdate(  id: string, data?: PatchedDocumentRequest,  client?: API
): Promise<Document> {
  const api = client || getAPIInstance()
  const response = await api.cfg_knowbase.adminDocumentsPartialUpdate(id, data)
  return DocumentSchema.parse(response)
}


/**
 * Delete document
 *
 * @method DELETE
 * @path /cfg/knowbase/admin/documents/{id}/
 */
export async function deleteKnowbaseAdminDocumentsDestroy(  id: string,  client?: API
): Promise<void> {
  const api = client || getAPIInstance()
  const response = await api.cfg_knowbase.adminDocumentsDestroy(id)
  return response
}


/**
 * Reprocess document
 *
 * @method POST
 * @path /cfg/knowbase/admin/documents/{id}/reprocess/
 */
export async function createKnowbaseAdminDocumentsReprocessCreate(  id: string, data: DocumentRequest,  client?: API
): Promise<Document> {
  const api = client || getAPIInstance()
  const response = await api.cfg_knowbase.adminDocumentsReprocessCreate(id, data)
  return DocumentSchema.parse(response)
}


/**
 * Get document processing status
 *
 * @method GET
 * @path /cfg/knowbase/admin/documents/{id}/status/
 */
export async function getKnowbaseAdminDocumentsStatusRetrieve(  id: string,  client?: API
): Promise<DocumentProcessingStatus> {
  const api = client || getAPIInstance()
  const response = await api.cfg_knowbase.adminDocumentsStatusRetrieve(id)
  return DocumentProcessingStatusSchema.parse(response)
}


/**
 * Get processing statistics
 *
 * @method GET
 * @path /cfg/knowbase/admin/documents/stats/
 */
export async function getKnowbaseAdminDocumentsStatsRetrieve(  client?: API
): Promise<DocumentStats> {
  const api = client || getAPIInstance()
  const response = await api.cfg_knowbase.adminDocumentsStatsRetrieve()
  return DocumentStatsSchema.parse(response)
}


/**
 * List user chat sessions
 *
 * @method GET
 * @path /cfg/knowbase/admin/sessions/
 */
export async function getKnowbaseAdminSessionsList(  params?: { page?: number; page_size?: number },  client?: API
): Promise<PaginatedChatSessionList> {
  const api = client || getAPIInstance()
  const response = await api.cfg_knowbase.adminSessionsList(params?.page, params?.page_size)
  return PaginatedChatSessionListSchema.parse(response)
}


/**
 * Create new chat session
 *
 * @method POST
 * @path /cfg/knowbase/admin/sessions/
 */
export async function createKnowbaseAdminSessionsCreate(  data: ChatSessionCreateRequest,  client?: API
): Promise<ChatSession> {
  const api = client || getAPIInstance()
  const response = await api.cfg_knowbase.adminSessionsCreate(data)
  return ChatSessionSchema.parse(response)
}


/**
 * API operation
 *
 * @method GET
 * @path /cfg/knowbase/admin/sessions/{id}/
 */
export async function getKnowbaseAdminSessionsRetrieve(  id: string,  client?: API
): Promise<ChatSession> {
  const api = client || getAPIInstance()
  const response = await api.cfg_knowbase.adminSessionsRetrieve(id)
  return ChatSessionSchema.parse(response)
}


/**
 * API operation
 *
 * @method PUT
 * @path /cfg/knowbase/admin/sessions/{id}/
 */
export async function updateKnowbaseAdminSessionsUpdate(  id: string, data: ChatSessionRequest,  client?: API
): Promise<ChatSession> {
  const api = client || getAPIInstance()
  const response = await api.cfg_knowbase.adminSessionsUpdate(id, data)
  return ChatSessionSchema.parse(response)
}


/**
 * API operation
 *
 * @method PATCH
 * @path /cfg/knowbase/admin/sessions/{id}/
 */
export async function partialUpdateKnowbaseAdminSessionsPartialUpdate(  id: string, data?: PatchedChatSessionRequest,  client?: API
): Promise<ChatSession> {
  const api = client || getAPIInstance()
  const response = await api.cfg_knowbase.adminSessionsPartialUpdate(id, data)
  return ChatSessionSchema.parse(response)
}


/**
 * API operation
 *
 * @method DELETE
 * @path /cfg/knowbase/admin/sessions/{id}/
 */
export async function deleteKnowbaseAdminSessionsDestroy(  id: string,  client?: API
): Promise<void> {
  const api = client || getAPIInstance()
  const response = await api.cfg_knowbase.adminSessionsDestroy(id)
  return response
}


/**
 * Activate chat session
 *
 * @method POST
 * @path /cfg/knowbase/admin/sessions/{id}/activate/
 */
export async function createKnowbaseAdminSessionsActivateCreate(  id: string, data: ChatSessionRequest,  client?: API
): Promise<ChatSession> {
  const api = client || getAPIInstance()
  const response = await api.cfg_knowbase.adminSessionsActivateCreate(id, data)
  return ChatSessionSchema.parse(response)
}


/**
 * Archive chat session
 *
 * @method POST
 * @path /cfg/knowbase/admin/sessions/{id}/archive/
 */
export async function createKnowbaseAdminSessionsArchiveCreate(  id: string, data: ChatSessionRequest,  client?: API
): Promise<ChatSession> {
  const api = client || getAPIInstance()
  const response = await api.cfg_knowbase.adminSessionsArchiveCreate(id, data)
  return ChatSessionSchema.parse(response)
}


/**
 * List public categories
 *
 * @method GET
 * @path /cfg/knowbase/categories/
 */
export async function getKnowbaseCategoriesList(  params?: { page?: number; page_size?: number },  client?: API
): Promise<PaginatedPublicCategoryList> {
  const api = client || getAPIInstance()
  const response = await api.cfg_knowbase.categoriesList(params?.page, params?.page_size)
  return PaginatedPublicCategoryListSchema.parse(response)
}


/**
 * Get public category details
 *
 * @method GET
 * @path /cfg/knowbase/categories/{id}/
 */
export async function getKnowbaseCategoriesRetrieve(  id: string,  client?: API
): Promise<PublicCategory> {
  const api = client || getAPIInstance()
  const response = await api.cfg_knowbase.categoriesRetrieve(id)
  return PublicCategorySchema.parse(response)
}


/**
 * List public documents
 *
 * @method GET
 * @path /cfg/knowbase/documents/
 */
export async function getKnowbaseDocumentsList(  params?: { category?: string; page?: number; page_size?: number; search?: string },  client?: API
): Promise<PaginatedPublicDocumentListList> {
  const api = client || getAPIInstance()
  const response = await api.cfg_knowbase.documentsList(params?.category, params?.page, params?.page_size, params?.search)
  return PaginatedPublicDocumentListListSchema.parse(response)
}


/**
 * Get public document details
 *
 * @method GET
 * @path /cfg/knowbase/documents/{id}/
 */
export async function getKnowbaseDocumentsRetrieve(  id: string,  client?: API
): Promise<PublicDocument> {
  const api = client || getAPIInstance()
  const response = await api.cfg_knowbase.documentsRetrieve(id)
  return PublicDocumentSchema.parse(response)
}


/**
 * API operation
 *
 * @method GET
 * @path /cfg/knowbase/system/archives/
 */
export async function getKnowbaseSystemArchivesList(  params?: { page?: number; page_size?: number },  client?: API
): Promise<PaginatedDocumentArchiveListList> {
  const api = client || getAPIInstance()
  const response = await api.cfg_knowbase.systemArchivesList(params?.page, params?.page_size)
  return PaginatedDocumentArchiveListListSchema.parse(response)
}


/**
 * Upload and process archive
 *
 * @method POST
 * @path /cfg/knowbase/system/archives/
 */
export async function createKnowbaseSystemArchivesCreate(  data: any,  client?: API
): Promise<ArchiveProcessingResult> {
  const api = client || getAPIInstance()
  const response = await api.cfg_knowbase.systemArchivesCreate(data)
  return ArchiveProcessingResultSchema.parse(response)
}


/**
 * API operation
 *
 * @method GET
 * @path /cfg/knowbase/system/archives/{id}/
 */
export async function getKnowbaseSystemArchivesRetrieve(  id: string,  client?: API
): Promise<DocumentArchiveDetail> {
  const api = client || getAPIInstance()
  const response = await api.cfg_knowbase.systemArchivesRetrieve(id)
  return DocumentArchiveDetailSchema.parse(response)
}


/**
 * API operation
 *
 * @method PUT
 * @path /cfg/knowbase/system/archives/{id}/
 */
export async function updateKnowbaseSystemArchivesUpdate(  id: string, data: DocumentArchiveRequest,  client?: API
): Promise<DocumentArchive> {
  const api = client || getAPIInstance()
  const response = await api.cfg_knowbase.systemArchivesUpdate(id, data)
  return DocumentArchiveSchema.parse(response)
}


/**
 * API operation
 *
 * @method PATCH
 * @path /cfg/knowbase/system/archives/{id}/
 */
export async function partialUpdateKnowbaseSystemArchivesPartialUpdate(  id: string, data?: PatchedDocumentArchiveRequest,  client?: API
): Promise<DocumentArchive> {
  const api = client || getAPIInstance()
  const response = await api.cfg_knowbase.systemArchivesPartialUpdate(id, data)
  return DocumentArchiveSchema.parse(response)
}


/**
 * API operation
 *
 * @method DELETE
 * @path /cfg/knowbase/system/archives/{id}/
 */
export async function deleteKnowbaseSystemArchivesDestroy(  id: string,  client?: API
): Promise<void> {
  const api = client || getAPIInstance()
  const response = await api.cfg_knowbase.systemArchivesDestroy(id)
  return response
}


/**
 * Get archive file tree
 *
 * @method GET
 * @path /cfg/knowbase/system/archives/{id}/file_tree/
 */
export async function getKnowbaseSystemArchivesFileTreeRetrieve(  id: string,  client?: API
): Promise<any> {
  const api = client || getAPIInstance()
  const response = await api.cfg_knowbase.systemArchivesFileTreeRetrieve(id)
  return response
}


/**
 * Get archive items
 *
 * @method GET
 * @path /cfg/knowbase/system/archives/{id}/items/
 */
export async function getKnowbaseSystemArchivesItemsList(  id: string, params?: { page?: number; page_size?: number },  client?: API
): Promise<PaginatedArchiveItemList> {
  const api = client || getAPIInstance()
  const response = await api.cfg_knowbase.systemArchivesItemsList(id, params?.page, params?.page_size)
  return PaginatedArchiveItemListSchema.parse(response)
}


/**
 * Search archive chunks
 *
 * @method POST
 * @path /cfg/knowbase/system/archives/{id}/search/
 */
export async function createKnowbaseSystemArchivesSearchCreate(  id: string, data: ArchiveSearchRequestRequest, params?: { page?: number; page_size?: number },  client?: API
): Promise<PaginatedArchiveSearchResultList> {
  const api = client || getAPIInstance()
  const response = await api.cfg_knowbase.systemArchivesSearchCreate(id, data, params?.page, params?.page_size)
  return PaginatedArchiveSearchResultListSchema.parse(response)
}


/**
 * Re-vectorize chunks
 *
 * @method POST
 * @path /cfg/knowbase/system/archives/revectorize/
 */
export async function createKnowbaseSystemArchivesRevectorizeCreate(  data: ChunkRevectorizationRequestRequest,  client?: API
): Promise<VectorizationResult> {
  const api = client || getAPIInstance()
  const response = await api.cfg_knowbase.systemArchivesRevectorizeCreate(data)
  return VectorizationResultSchema.parse(response)
}


/**
 * Get archive statistics
 *
 * @method GET
 * @path /cfg/knowbase/system/archives/statistics/
 */
export async function getKnowbaseSystemArchivesStatisticsRetrieve(  client?: API
): Promise<ArchiveStatistics> {
  const api = client || getAPIInstance()
  const response = await api.cfg_knowbase.systemArchivesStatisticsRetrieve()
  return ArchiveStatisticsSchema.parse(response)
}


/**
 * Get vectorization statistics
 *
 * @method GET
 * @path /cfg/knowbase/system/archives/vectorization_stats/
 */
export async function getKnowbaseSystemArchivesVectorizationStatsRetrieve(  client?: API
): Promise<VectorizationStatistics> {
  const api = client || getAPIInstance()
  const response = await api.cfg_knowbase.systemArchivesVectorizationStatsRetrieve()
  return VectorizationStatisticsSchema.parse(response)
}


/**
 * API operation
 *
 * @method GET
 * @path /cfg/knowbase/system/chunks/
 */
export async function getKnowbaseSystemChunksList(  params?: { page?: number; page_size?: number },  client?: API
): Promise<PaginatedArchiveItemChunkList> {
  const api = client || getAPIInstance()
  const response = await api.cfg_knowbase.systemChunksList(params?.page, params?.page_size)
  return PaginatedArchiveItemChunkListSchema.parse(response)
}


/**
 * API operation
 *
 * @method POST
 * @path /cfg/knowbase/system/chunks/
 */
export async function createKnowbaseSystemChunksCreate(  data: ArchiveItemChunkRequest,  client?: API
): Promise<ArchiveItemChunk> {
  const api = client || getAPIInstance()
  const response = await api.cfg_knowbase.systemChunksCreate(data)
  return ArchiveItemChunkSchema.parse(response)
}


/**
 * API operation
 *
 * @method GET
 * @path /cfg/knowbase/system/chunks/{id}/
 */
export async function getKnowbaseSystemChunksRetrieve(  id: string,  client?: API
): Promise<ArchiveItemChunkDetail> {
  const api = client || getAPIInstance()
  const response = await api.cfg_knowbase.systemChunksRetrieve(id)
  return ArchiveItemChunkDetailSchema.parse(response)
}


/**
 * API operation
 *
 * @method PUT
 * @path /cfg/knowbase/system/chunks/{id}/
 */
export async function updateKnowbaseSystemChunksUpdate(  id: string, data: ArchiveItemChunkRequest,  client?: API
): Promise<ArchiveItemChunk> {
  const api = client || getAPIInstance()
  const response = await api.cfg_knowbase.systemChunksUpdate(id, data)
  return ArchiveItemChunkSchema.parse(response)
}


/**
 * API operation
 *
 * @method PATCH
 * @path /cfg/knowbase/system/chunks/{id}/
 */
export async function partialUpdateKnowbaseSystemChunksPartialUpdate(  id: string, data?: PatchedArchiveItemChunkRequest,  client?: API
): Promise<ArchiveItemChunk> {
  const api = client || getAPIInstance()
  const response = await api.cfg_knowbase.systemChunksPartialUpdate(id, data)
  return ArchiveItemChunkSchema.parse(response)
}


/**
 * API operation
 *
 * @method DELETE
 * @path /cfg/knowbase/system/chunks/{id}/
 */
export async function deleteKnowbaseSystemChunksDestroy(  id: string,  client?: API
): Promise<void> {
  const api = client || getAPIInstance()
  const response = await api.cfg_knowbase.systemChunksDestroy(id)
  return response
}


/**
 * Get chunk context
 *
 * @method GET
 * @path /cfg/knowbase/system/chunks/{id}/context/
 */
export async function getKnowbaseSystemChunksContextRetrieve(  id: string,  client?: API
): Promise<ArchiveItemChunkDetail> {
  const api = client || getAPIInstance()
  const response = await api.cfg_knowbase.systemChunksContextRetrieve(id)
  return ArchiveItemChunkDetailSchema.parse(response)
}


/**
 * Vectorize chunk
 *
 * @method POST
 * @path /cfg/knowbase/system/chunks/{id}/vectorize/
 */
export async function createKnowbaseSystemChunksVectorizeCreate(  id: string, data: ArchiveItemChunkRequest,  client?: API
): Promise<any> {
  const api = client || getAPIInstance()
  const response = await api.cfg_knowbase.systemChunksVectorizeCreate(id, data)
  return response
}


/**
 * API operation
 *
 * @method GET
 * @path /cfg/knowbase/system/items/
 */
export async function getKnowbaseSystemItemsList(  params?: { page?: number; page_size?: number },  client?: API
): Promise<PaginatedArchiveItemList> {
  const api = client || getAPIInstance()
  const response = await api.cfg_knowbase.systemItemsList(params?.page, params?.page_size)
  return PaginatedArchiveItemListSchema.parse(response)
}


/**
 * API operation
 *
 * @method POST
 * @path /cfg/knowbase/system/items/
 */
export async function createKnowbaseSystemItemsCreate(  data: ArchiveItemRequest,  client?: API
): Promise<ArchiveItem> {
  const api = client || getAPIInstance()
  const response = await api.cfg_knowbase.systemItemsCreate(data)
  return ArchiveItemSchema.parse(response)
}


/**
 * API operation
 *
 * @method GET
 * @path /cfg/knowbase/system/items/{id}/
 */
export async function getKnowbaseSystemItemsRetrieve(  id: string,  client?: API
): Promise<ArchiveItemDetail> {
  const api = client || getAPIInstance()
  const response = await api.cfg_knowbase.systemItemsRetrieve(id)
  return ArchiveItemDetailSchema.parse(response)
}


/**
 * API operation
 *
 * @method PUT
 * @path /cfg/knowbase/system/items/{id}/
 */
export async function updateKnowbaseSystemItemsUpdate(  id: string, data: ArchiveItemRequest,  client?: API
): Promise<ArchiveItem> {
  const api = client || getAPIInstance()
  const response = await api.cfg_knowbase.systemItemsUpdate(id, data)
  return ArchiveItemSchema.parse(response)
}


/**
 * API operation
 *
 * @method PATCH
 * @path /cfg/knowbase/system/items/{id}/
 */
export async function partialUpdateKnowbaseSystemItemsPartialUpdate(  id: string, data?: PatchedArchiveItemRequest,  client?: API
): Promise<ArchiveItem> {
  const api = client || getAPIInstance()
  const response = await api.cfg_knowbase.systemItemsPartialUpdate(id, data)
  return ArchiveItemSchema.parse(response)
}


/**
 * API operation
 *
 * @method DELETE
 * @path /cfg/knowbase/system/items/{id}/
 */
export async function deleteKnowbaseSystemItemsDestroy(  id: string,  client?: API
): Promise<void> {
  const api = client || getAPIInstance()
  const response = await api.cfg_knowbase.systemItemsDestroy(id)
  return response
}


/**
 * Get item chunks
 *
 * @method GET
 * @path /cfg/knowbase/system/items/{id}/chunks/
 */
export async function getKnowbaseSystemItemsChunksList(  id: string, params?: { page?: number; page_size?: number },  client?: API
): Promise<PaginatedArchiveItemChunkList> {
  const api = client || getAPIInstance()
  const response = await api.cfg_knowbase.systemItemsChunksList(id, params?.page, params?.page_size)
  return PaginatedArchiveItemChunkListSchema.parse(response)
}


/**
 * Get item content
 *
 * @method GET
 * @path /cfg/knowbase/system/items/{id}/content/
 */
export async function getKnowbaseSystemItemsContentRetrieve(  id: string,  client?: API
): Promise<ArchiveItemDetail> {
  const api = client || getAPIInstance()
  const response = await api.cfg_knowbase.systemItemsContentRetrieve(id)
  return ArchiveItemDetailSchema.parse(response)
}


