/**
 * SWR Hooks for Knowbase
 *
 * React hooks powered by SWR for data fetching with automatic caching,
 * revalidation, and optimistic updates.
 *
 * Usage:
 * ```typescript
 * // Query hooks (GET)
 * const { data, error, isLoading } = useUsers({ page: 1 })
 *
 * // Mutation hooks (POST/PUT/PATCH/DELETE)
 * const createUser = useCreateUser()
 * await createUser({ name: 'John', email: 'john@example.com' })
 * ```
 */
import useSWR from 'swr'
import { useSWRConfig } from 'swr'
import * as Fetchers from '../fetchers/cfg__knowbase'
import type { API } from '../../index'
import type { ArchiveItem } from '../schemas/ArchiveItem.schema'
import type { ArchiveItemChunk } from '../schemas/ArchiveItemChunk.schema'
import type { ArchiveItemChunkDetail } from '../schemas/ArchiveItemChunkDetail.schema'
import type { ArchiveItemChunkRequest } from '../schemas/ArchiveItemChunkRequest.schema'
import type { ArchiveItemDetail } from '../schemas/ArchiveItemDetail.schema'
import type { ArchiveItemRequest } from '../schemas/ArchiveItemRequest.schema'
import type { ArchiveProcessingResult } from '../schemas/ArchiveProcessingResult.schema'
import type { ArchiveSearchRequestRequest } from '../schemas/ArchiveSearchRequestRequest.schema'
import type { ArchiveStatistics } from '../schemas/ArchiveStatistics.schema'
import type { ChatHistory } from '../schemas/ChatHistory.schema'
import type { ChatQueryRequest } from '../schemas/ChatQueryRequest.schema'
import type { ChatResponse } from '../schemas/ChatResponse.schema'
import type { ChatResponseRequest } from '../schemas/ChatResponseRequest.schema'
import type { ChatSession } from '../schemas/ChatSession.schema'
import type { ChatSessionCreateRequest } from '../schemas/ChatSessionCreateRequest.schema'
import type { ChatSessionRequest } from '../schemas/ChatSessionRequest.schema'
import type { ChunkRevectorizationRequestRequest } from '../schemas/ChunkRevectorizationRequestRequest.schema'
import type { Document } from '../schemas/Document.schema'
import type { DocumentArchive } from '../schemas/DocumentArchive.schema'
import type { DocumentArchiveDetail } from '../schemas/DocumentArchiveDetail.schema'
import type { DocumentArchiveRequest } from '../schemas/DocumentArchiveRequest.schema'
import type { DocumentCreateRequest } from '../schemas/DocumentCreateRequest.schema'
import type { DocumentProcessingStatus } from '../schemas/DocumentProcessingStatus.schema'
import type { DocumentRequest } from '../schemas/DocumentRequest.schema'
import type { DocumentStats } from '../schemas/DocumentStats.schema'
import type { PaginatedArchiveItemChunkList } from '../schemas/PaginatedArchiveItemChunkList.schema'
import type { PaginatedArchiveItemList } from '../schemas/PaginatedArchiveItemList.schema'
import type { PaginatedArchiveSearchResultList } from '../schemas/PaginatedArchiveSearchResultList.schema'
import type { PaginatedChatResponseList } from '../schemas/PaginatedChatResponseList.schema'
import type { PaginatedChatSessionList } from '../schemas/PaginatedChatSessionList.schema'
import type { PaginatedDocumentArchiveListList } from '../schemas/PaginatedDocumentArchiveListList.schema'
import type { PaginatedDocumentList } from '../schemas/PaginatedDocumentList.schema'
import type { PaginatedPublicCategoryList } from '../schemas/PaginatedPublicCategoryList.schema'
import type { PaginatedPublicDocumentListList } from '../schemas/PaginatedPublicDocumentListList.schema'
import type { PatchedArchiveItemChunkRequest } from '../schemas/PatchedArchiveItemChunkRequest.schema'
import type { PatchedArchiveItemRequest } from '../schemas/PatchedArchiveItemRequest.schema'
import type { PatchedChatResponseRequest } from '../schemas/PatchedChatResponseRequest.schema'
import type { PatchedChatSessionRequest } from '../schemas/PatchedChatSessionRequest.schema'
import type { PatchedDocumentArchiveRequest } from '../schemas/PatchedDocumentArchiveRequest.schema'
import type { PatchedDocumentRequest } from '../schemas/PatchedDocumentRequest.schema'
import type { PublicCategory } from '../schemas/PublicCategory.schema'
import type { PublicDocument } from '../schemas/PublicDocument.schema'
import type { VectorizationResult } from '../schemas/VectorizationResult.schema'
import type { VectorizationStatistics } from '../schemas/VectorizationStatistics.schema'

/**
 * API operation
 *
 * @method GET
 * @path /cfg/knowbase/admin/chat/
 */
export function useKnowbaseAdminChatList(params?: { page?: number; page_size?: number }, client?: API): ReturnType<typeof useSWR<PaginatedChatResponseList>> {
  return useSWR<PaginatedChatResponseList>(
    params ? ['cfg-knowbase-admin-chat', params] : 'cfg-knowbase-admin-chat',
    () => Fetchers.getKnowbaseAdminChatList(params, client)
  )
}


/**
 * API operation
 *
 * @method POST
 * @path /cfg/knowbase/admin/chat/
 */
export function useCreateKnowbaseAdminChatCreate() {
  const { mutate } = useSWRConfig()

  return async (data: ChatResponseRequest, client?: API): Promise<ChatResponse> => {
    const result = await Fetchers.createKnowbaseAdminChatCreate(data, client)
    // Revalidate related queries
    mutate('cfg-knowbase-admin-chat')
    return result
  }
}


/**
 * API operation
 *
 * @method GET
 * @path /cfg/knowbase/admin/chat/{id}/
 */
export function useKnowbaseAdminChatRetrieve(id: string, client?: API): ReturnType<typeof useSWR<ChatResponse>> {
  return useSWR<ChatResponse>(
    ['cfg-knowbase-admin-chat', id],
    () => Fetchers.getKnowbaseAdminChatRetrieve(id, client)
  )
}


/**
 * API operation
 *
 * @method PUT
 * @path /cfg/knowbase/admin/chat/{id}/
 */
export function useUpdateKnowbaseAdminChatUpdate() {
  const { mutate } = useSWRConfig()

  return async (id: string, data: ChatResponseRequest, client?: API): Promise<ChatResponse> => {
    const result = await Fetchers.updateKnowbaseAdminChatUpdate(id, data, client)
    // Revalidate related queries
    mutate('cfg-knowbase-admin-chat')
    return result
  }
}


/**
 * API operation
 *
 * @method PATCH
 * @path /cfg/knowbase/admin/chat/{id}/
 */
export function usePartialUpdateKnowbaseAdminChatPartialUpdate() {
  const { mutate } = useSWRConfig()

  return async (id: string, data?: PatchedChatResponseRequest, client?: API): Promise<ChatResponse> => {
    const result = await Fetchers.partialUpdateKnowbaseAdminChatPartialUpdate(id, data, client)
    // Revalidate related queries
    mutate('cfg-knowbase-admin-chat-partial')
    return result
  }
}


/**
 * API operation
 *
 * @method DELETE
 * @path /cfg/knowbase/admin/chat/{id}/
 */
export function useDeleteKnowbaseAdminChatDestroy() {
  const { mutate } = useSWRConfig()

  return async (id: string, client?: API): Promise<void> => {
    const result = await Fetchers.deleteKnowbaseAdminChatDestroy(id, client)
    // Revalidate related queries
    mutate('cfg-knowbase-admin-chat')
    return result
  }
}


/**
 * Get chat history
 *
 * @method GET
 * @path /cfg/knowbase/admin/chat/{id}/history/
 */
export function useKnowbaseAdminChatHistoryRetrieve(id: string, client?: API): ReturnType<typeof useSWR<ChatHistory>> {
  return useSWR<ChatHistory>(
    ['cfg-knowbase-admin-chat-history', id],
    () => Fetchers.getKnowbaseAdminChatHistoryRetrieve(id, client)
  )
}


/**
 * Process chat query with RAG
 *
 * @method POST
 * @path /cfg/knowbase/admin/chat/query/
 */
export function useCreateKnowbaseAdminChatQueryCreate() {
  const { mutate } = useSWRConfig()

  return async (data: ChatQueryRequest, client?: API): Promise<ChatResponse> => {
    const result = await Fetchers.createKnowbaseAdminChatQueryCreate(data, client)
    // Revalidate related queries
    mutate('cfg-knowbase-admin-chat-query')
    return result
  }
}


/**
 * List user documents
 *
 * @method GET
 * @path /cfg/knowbase/admin/documents/
 */
export function useKnowbaseAdminDocumentsList(params?: { page?: number; page_size?: number; status?: string }, client?: API): ReturnType<typeof useSWR<PaginatedDocumentList>> {
  return useSWR<PaginatedDocumentList>(
    params ? ['cfg-knowbase-admin-documents', params] : 'cfg-knowbase-admin-documents',
    () => Fetchers.getKnowbaseAdminDocumentsList(params, client)
  )
}


/**
 * Upload new document
 *
 * @method POST
 * @path /cfg/knowbase/admin/documents/
 */
export function useCreateKnowbaseAdminDocumentsCreate() {
  const { mutate } = useSWRConfig()

  return async (data: DocumentCreateRequest, client?: API): Promise<Document> => {
    const result = await Fetchers.createKnowbaseAdminDocumentsCreate(data, client)
    // Revalidate related queries
    mutate('cfg-knowbase-admin-documents')
    return result
  }
}


/**
 * Get document details
 *
 * @method GET
 * @path /cfg/knowbase/admin/documents/{id}/
 */
export function useKnowbaseAdminDocumentsRetrieve(id: string, client?: API): ReturnType<typeof useSWR<Document>> {
  return useSWR<Document>(
    ['cfg-knowbase-admin-document', id],
    () => Fetchers.getKnowbaseAdminDocumentsRetrieve(id, client)
  )
}


/**
 * API operation
 *
 * @method PUT
 * @path /cfg/knowbase/admin/documents/{id}/
 */
export function useUpdateKnowbaseAdminDocumentsUpdate() {
  const { mutate } = useSWRConfig()

  return async (id: string, data: DocumentRequest, client?: API): Promise<Document> => {
    const result = await Fetchers.updateKnowbaseAdminDocumentsUpdate(id, data, client)
    // Revalidate related queries
    mutate('cfg-knowbase-admin-documents')
    mutate('cfg-knowbase-admin-document')
    return result
  }
}


/**
 * API operation
 *
 * @method PATCH
 * @path /cfg/knowbase/admin/documents/{id}/
 */
export function usePartialUpdateKnowbaseAdminDocumentsPartialUpdate() {
  const { mutate } = useSWRConfig()

  return async (id: string, data?: PatchedDocumentRequest, client?: API): Promise<Document> => {
    const result = await Fetchers.partialUpdateKnowbaseAdminDocumentsPartialUpdate(id, data, client)
    // Revalidate related queries
    mutate('cfg-knowbase-admin-documents-partial')
    return result
  }
}


/**
 * Delete document
 *
 * @method DELETE
 * @path /cfg/knowbase/admin/documents/{id}/
 */
export function useDeleteKnowbaseAdminDocumentsDestroy() {
  const { mutate } = useSWRConfig()

  return async (id: string, client?: API): Promise<void> => {
    const result = await Fetchers.deleteKnowbaseAdminDocumentsDestroy(id, client)
    // Revalidate related queries
    mutate('cfg-knowbase-admin-documents')
    mutate('cfg-knowbase-admin-document')
    return result
  }
}


/**
 * Reprocess document
 *
 * @method POST
 * @path /cfg/knowbase/admin/documents/{id}/reprocess/
 */
export function useCreateKnowbaseAdminDocumentsReprocessCreate() {
  const { mutate } = useSWRConfig()

  return async (id: string, data: DocumentRequest, client?: API): Promise<Document> => {
    const result = await Fetchers.createKnowbaseAdminDocumentsReprocessCreate(id, data, client)
    // Revalidate related queries
    mutate('cfg-knowbase-admin-documents-reprocess')
    return result
  }
}


/**
 * Get document processing status
 *
 * @method GET
 * @path /cfg/knowbase/admin/documents/{id}/status/
 */
export function useKnowbaseAdminDocumentsStatusRetrieve(id: string, client?: API): ReturnType<typeof useSWR<DocumentProcessingStatus>> {
  return useSWR<DocumentProcessingStatus>(
    ['cfg-knowbase-admin-documents-statu', id],
    () => Fetchers.getKnowbaseAdminDocumentsStatusRetrieve(id, client)
  )
}


/**
 * Get processing statistics
 *
 * @method GET
 * @path /cfg/knowbase/admin/documents/stats/
 */
export function useKnowbaseAdminDocumentsStatsRetrieve(client?: API): ReturnType<typeof useSWR<DocumentStats>> {
  return useSWR<DocumentStats>(
    'cfg-knowbase-admin-documents-stat',
    () => Fetchers.getKnowbaseAdminDocumentsStatsRetrieve(client)
  )
}


/**
 * List user chat sessions
 *
 * @method GET
 * @path /cfg/knowbase/admin/sessions/
 */
export function useKnowbaseAdminSessionsList(params?: { page?: number; page_size?: number }, client?: API): ReturnType<typeof useSWR<PaginatedChatSessionList>> {
  return useSWR<PaginatedChatSessionList>(
    params ? ['cfg-knowbase-admin-sessions', params] : 'cfg-knowbase-admin-sessions',
    () => Fetchers.getKnowbaseAdminSessionsList(params, client)
  )
}


/**
 * Create new chat session
 *
 * @method POST
 * @path /cfg/knowbase/admin/sessions/
 */
export function useCreateKnowbaseAdminSessionsCreate() {
  const { mutate } = useSWRConfig()

  return async (data: ChatSessionCreateRequest, client?: API): Promise<ChatSession> => {
    const result = await Fetchers.createKnowbaseAdminSessionsCreate(data, client)
    // Revalidate related queries
    mutate('cfg-knowbase-admin-sessions')
    return result
  }
}


/**
 * API operation
 *
 * @method GET
 * @path /cfg/knowbase/admin/sessions/{id}/
 */
export function useKnowbaseAdminSessionsRetrieve(id: string, client?: API): ReturnType<typeof useSWR<ChatSession>> {
  return useSWR<ChatSession>(
    ['cfg-knowbase-admin-session', id],
    () => Fetchers.getKnowbaseAdminSessionsRetrieve(id, client)
  )
}


/**
 * API operation
 *
 * @method PUT
 * @path /cfg/knowbase/admin/sessions/{id}/
 */
export function useUpdateKnowbaseAdminSessionsUpdate() {
  const { mutate } = useSWRConfig()

  return async (id: string, data: ChatSessionRequest, client?: API): Promise<ChatSession> => {
    const result = await Fetchers.updateKnowbaseAdminSessionsUpdate(id, data, client)
    // Revalidate related queries
    mutate('cfg-knowbase-admin-sessions')
    mutate('cfg-knowbase-admin-session')
    return result
  }
}


/**
 * API operation
 *
 * @method PATCH
 * @path /cfg/knowbase/admin/sessions/{id}/
 */
export function usePartialUpdateKnowbaseAdminSessionsPartialUpdate() {
  const { mutate } = useSWRConfig()

  return async (id: string, data?: PatchedChatSessionRequest, client?: API): Promise<ChatSession> => {
    const result = await Fetchers.partialUpdateKnowbaseAdminSessionsPartialUpdate(id, data, client)
    // Revalidate related queries
    mutate('cfg-knowbase-admin-sessions-partial')
    return result
  }
}


/**
 * API operation
 *
 * @method DELETE
 * @path /cfg/knowbase/admin/sessions/{id}/
 */
export function useDeleteKnowbaseAdminSessionsDestroy() {
  const { mutate } = useSWRConfig()

  return async (id: string, client?: API): Promise<void> => {
    const result = await Fetchers.deleteKnowbaseAdminSessionsDestroy(id, client)
    // Revalidate related queries
    mutate('cfg-knowbase-admin-sessions')
    mutate('cfg-knowbase-admin-session')
    return result
  }
}


/**
 * Activate chat session
 *
 * @method POST
 * @path /cfg/knowbase/admin/sessions/{id}/activate/
 */
export function useCreateKnowbaseAdminSessionsActivateCreate() {
  const { mutate } = useSWRConfig()

  return async (id: string, data: ChatSessionRequest, client?: API): Promise<ChatSession> => {
    const result = await Fetchers.createKnowbaseAdminSessionsActivateCreate(id, data, client)
    // Revalidate related queries
    mutate('cfg-knowbase-admin-sessions-activate')
    return result
  }
}


/**
 * Archive chat session
 *
 * @method POST
 * @path /cfg/knowbase/admin/sessions/{id}/archive/
 */
export function useCreateKnowbaseAdminSessionsArchiveCreate() {
  const { mutate } = useSWRConfig()

  return async (id: string, data: ChatSessionRequest, client?: API): Promise<ChatSession> => {
    const result = await Fetchers.createKnowbaseAdminSessionsArchiveCreate(id, data, client)
    // Revalidate related queries
    mutate('cfg-knowbase-admin-sessions-archive')
    return result
  }
}


/**
 * List public categories
 *
 * @method GET
 * @path /cfg/knowbase/categories/
 */
export function useKnowbaseCategoriesList(params?: { page?: number; page_size?: number }, client?: API): ReturnType<typeof useSWR<PaginatedPublicCategoryList>> {
  return useSWR<PaginatedPublicCategoryList>(
    params ? ['cfg-knowbase-categories', params] : 'cfg-knowbase-categories',
    () => Fetchers.getKnowbaseCategoriesList(params, client)
  )
}


/**
 * Get public category details
 *
 * @method GET
 * @path /cfg/knowbase/categories/{id}/
 */
export function useKnowbaseCategoriesRetrieve(id: string, client?: API): ReturnType<typeof useSWR<PublicCategory>> {
  return useSWR<PublicCategory>(
    ['cfg-knowbase-categorie', id],
    () => Fetchers.getKnowbaseCategoriesRetrieve(id, client)
  )
}


/**
 * List public documents
 *
 * @method GET
 * @path /cfg/knowbase/documents/
 */
export function useKnowbaseDocumentsList(params?: { category?: string; page?: number; page_size?: number; search?: string }, client?: API): ReturnType<typeof useSWR<PaginatedPublicDocumentListList>> {
  return useSWR<PaginatedPublicDocumentListList>(
    params ? ['cfg-knowbase-documents', params] : 'cfg-knowbase-documents',
    () => Fetchers.getKnowbaseDocumentsList(params, client)
  )
}


/**
 * Get public document details
 *
 * @method GET
 * @path /cfg/knowbase/documents/{id}/
 */
export function useKnowbaseDocumentsRetrieve(id: string, client?: API): ReturnType<typeof useSWR<PublicDocument>> {
  return useSWR<PublicDocument>(
    ['cfg-knowbase-document', id],
    () => Fetchers.getKnowbaseDocumentsRetrieve(id, client)
  )
}


/**
 * API operation
 *
 * @method GET
 * @path /cfg/knowbase/system/archives/
 */
export function useKnowbaseSystemArchivesList(params?: { page?: number; page_size?: number }, client?: API): ReturnType<typeof useSWR<PaginatedDocumentArchiveListList>> {
  return useSWR<PaginatedDocumentArchiveListList>(
    params ? ['cfg-knowbase-system-archives', params] : 'cfg-knowbase-system-archives',
    () => Fetchers.getKnowbaseSystemArchivesList(params, client)
  )
}


/**
 * Upload and process archive
 *
 * @method POST
 * @path /cfg/knowbase/system/archives/
 */
export function useCreateKnowbaseSystemArchivesCreate() {
  const { mutate } = useSWRConfig()

  return async (data: any, client?: API): Promise<ArchiveProcessingResult> => {
    const result = await Fetchers.createKnowbaseSystemArchivesCreate(data, client)
    // Revalidate related queries
    mutate('cfg-knowbase-system-archives')
    return result
  }
}


/**
 * API operation
 *
 * @method GET
 * @path /cfg/knowbase/system/archives/{id}/
 */
export function useKnowbaseSystemArchivesRetrieve(id: string, client?: API): ReturnType<typeof useSWR<DocumentArchiveDetail>> {
  return useSWR<DocumentArchiveDetail>(
    ['cfg-knowbase-system-archive', id],
    () => Fetchers.getKnowbaseSystemArchivesRetrieve(id, client)
  )
}


/**
 * API operation
 *
 * @method PUT
 * @path /cfg/knowbase/system/archives/{id}/
 */
export function useUpdateKnowbaseSystemArchivesUpdate() {
  const { mutate } = useSWRConfig()

  return async (id: string, data: DocumentArchiveRequest, client?: API): Promise<DocumentArchive> => {
    const result = await Fetchers.updateKnowbaseSystemArchivesUpdate(id, data, client)
    // Revalidate related queries
    mutate('cfg-knowbase-system-archives')
    mutate('cfg-knowbase-system-archive')
    return result
  }
}


/**
 * API operation
 *
 * @method PATCH
 * @path /cfg/knowbase/system/archives/{id}/
 */
export function usePartialUpdateKnowbaseSystemArchivesPartialUpdate() {
  const { mutate } = useSWRConfig()

  return async (id: string, data?: PatchedDocumentArchiveRequest, client?: API): Promise<DocumentArchive> => {
    const result = await Fetchers.partialUpdateKnowbaseSystemArchivesPartialUpdate(id, data, client)
    // Revalidate related queries
    mutate('cfg-knowbase-system-archives-partial')
    return result
  }
}


/**
 * API operation
 *
 * @method DELETE
 * @path /cfg/knowbase/system/archives/{id}/
 */
export function useDeleteKnowbaseSystemArchivesDestroy() {
  const { mutate } = useSWRConfig()

  return async (id: string, client?: API): Promise<void> => {
    const result = await Fetchers.deleteKnowbaseSystemArchivesDestroy(id, client)
    // Revalidate related queries
    mutate('cfg-knowbase-system-archives')
    mutate('cfg-knowbase-system-archive')
    return result
  }
}


/**
 * Get archive file tree
 *
 * @method GET
 * @path /cfg/knowbase/system/archives/{id}/file_tree/
 */
export function useKnowbaseSystemArchivesFileTreeRetrieve(id: string, client?: API): ReturnType<typeof useSWR<any>> {
  return useSWR<any>(
    ['cfg-knowbase-system-archives-file-tree', id],
    () => Fetchers.getKnowbaseSystemArchivesFileTreeRetrieve(id, client)
  )
}


/**
 * Get archive items
 *
 * @method GET
 * @path /cfg/knowbase/system/archives/{id}/items/
 */
export function useKnowbaseSystemArchivesItemsList(id: string, params?: { page?: number; page_size?: number }, client?: API): ReturnType<typeof useSWR<PaginatedArchiveItemList>> {
  return useSWR<PaginatedArchiveItemList>(
    ['cfg-knowbase-system-archives-items', id],
    () => Fetchers.getKnowbaseSystemArchivesItemsList(id, params, client)
  )
}


/**
 * Search archive chunks
 *
 * @method POST
 * @path /cfg/knowbase/system/archives/{id}/search/
 */
export function useCreateKnowbaseSystemArchivesSearchCreate() {
  const { mutate } = useSWRConfig()

  return async (id: string, data: ArchiveSearchRequestRequest, params?: { page?: number; page_size?: number }, client?: API): Promise<PaginatedArchiveSearchResultList> => {
    const result = await Fetchers.createKnowbaseSystemArchivesSearchCreate(id, data, params, client)
    // Revalidate related queries
    mutate('cfg-knowbase-system-archives-search')
    return result
  }
}


/**
 * Re-vectorize chunks
 *
 * @method POST
 * @path /cfg/knowbase/system/archives/revectorize/
 */
export function useCreateKnowbaseSystemArchivesRevectorizeCreate() {
  const { mutate } = useSWRConfig()

  return async (data: ChunkRevectorizationRequestRequest, client?: API): Promise<VectorizationResult> => {
    const result = await Fetchers.createKnowbaseSystemArchivesRevectorizeCreate(data, client)
    // Revalidate related queries
    mutate('cfg-knowbase-system-archives-revectorize')
    return result
  }
}


/**
 * Get archive statistics
 *
 * @method GET
 * @path /cfg/knowbase/system/archives/statistics/
 */
export function useKnowbaseSystemArchivesStatisticsRetrieve(client?: API): ReturnType<typeof useSWR<ArchiveStatistics>> {
  return useSWR<ArchiveStatistics>(
    'cfg-knowbase-system-archives-statistic',
    () => Fetchers.getKnowbaseSystemArchivesStatisticsRetrieve(client)
  )
}


/**
 * Get vectorization statistics
 *
 * @method GET
 * @path /cfg/knowbase/system/archives/vectorization_stats/
 */
export function useKnowbaseSystemArchivesVectorizationStatsRetrieve(client?: API): ReturnType<typeof useSWR<VectorizationStatistics>> {
  return useSWR<VectorizationStatistics>(
    'cfg-knowbase-system-archives-vectorization-stat',
    () => Fetchers.getKnowbaseSystemArchivesVectorizationStatsRetrieve(client)
  )
}


/**
 * API operation
 *
 * @method GET
 * @path /cfg/knowbase/system/chunks/
 */
export function useKnowbaseSystemChunksList(params?: { page?: number; page_size?: number }, client?: API): ReturnType<typeof useSWR<PaginatedArchiveItemChunkList>> {
  return useSWR<PaginatedArchiveItemChunkList>(
    params ? ['cfg-knowbase-system-chunks', params] : 'cfg-knowbase-system-chunks',
    () => Fetchers.getKnowbaseSystemChunksList(params, client)
  )
}


/**
 * API operation
 *
 * @method POST
 * @path /cfg/knowbase/system/chunks/
 */
export function useCreateKnowbaseSystemChunksCreate() {
  const { mutate } = useSWRConfig()

  return async (data: ArchiveItemChunkRequest, client?: API): Promise<ArchiveItemChunk> => {
    const result = await Fetchers.createKnowbaseSystemChunksCreate(data, client)
    // Revalidate related queries
    mutate('cfg-knowbase-system-chunks')
    return result
  }
}


/**
 * API operation
 *
 * @method GET
 * @path /cfg/knowbase/system/chunks/{id}/
 */
export function useKnowbaseSystemChunksRetrieve(id: string, client?: API): ReturnType<typeof useSWR<ArchiveItemChunkDetail>> {
  return useSWR<ArchiveItemChunkDetail>(
    ['cfg-knowbase-system-chunk', id],
    () => Fetchers.getKnowbaseSystemChunksRetrieve(id, client)
  )
}


/**
 * API operation
 *
 * @method PUT
 * @path /cfg/knowbase/system/chunks/{id}/
 */
export function useUpdateKnowbaseSystemChunksUpdate() {
  const { mutate } = useSWRConfig()

  return async (id: string, data: ArchiveItemChunkRequest, client?: API): Promise<ArchiveItemChunk> => {
    const result = await Fetchers.updateKnowbaseSystemChunksUpdate(id, data, client)
    // Revalidate related queries
    mutate('cfg-knowbase-system-chunks')
    mutate('cfg-knowbase-system-chunk')
    return result
  }
}


/**
 * API operation
 *
 * @method PATCH
 * @path /cfg/knowbase/system/chunks/{id}/
 */
export function usePartialUpdateKnowbaseSystemChunksPartialUpdate() {
  const { mutate } = useSWRConfig()

  return async (id: string, data?: PatchedArchiveItemChunkRequest, client?: API): Promise<ArchiveItemChunk> => {
    const result = await Fetchers.partialUpdateKnowbaseSystemChunksPartialUpdate(id, data, client)
    // Revalidate related queries
    mutate('cfg-knowbase-system-chunks-partial')
    return result
  }
}


/**
 * API operation
 *
 * @method DELETE
 * @path /cfg/knowbase/system/chunks/{id}/
 */
export function useDeleteKnowbaseSystemChunksDestroy() {
  const { mutate } = useSWRConfig()

  return async (id: string, client?: API): Promise<void> => {
    const result = await Fetchers.deleteKnowbaseSystemChunksDestroy(id, client)
    // Revalidate related queries
    mutate('cfg-knowbase-system-chunks')
    mutate('cfg-knowbase-system-chunk')
    return result
  }
}


/**
 * Get chunk context
 *
 * @method GET
 * @path /cfg/knowbase/system/chunks/{id}/context/
 */
export function useKnowbaseSystemChunksContextRetrieve(id: string, client?: API): ReturnType<typeof useSWR<ArchiveItemChunkDetail>> {
  return useSWR<ArchiveItemChunkDetail>(
    ['cfg-knowbase-system-chunks-context', id],
    () => Fetchers.getKnowbaseSystemChunksContextRetrieve(id, client)
  )
}


/**
 * Vectorize chunk
 *
 * @method POST
 * @path /cfg/knowbase/system/chunks/{id}/vectorize/
 */
export function useCreateKnowbaseSystemChunksVectorizeCreate() {
  const { mutate } = useSWRConfig()

  return async (id: string, data: ArchiveItemChunkRequest, client?: API): Promise<any> => {
    const result = await Fetchers.createKnowbaseSystemChunksVectorizeCreate(id, data, client)
    // Revalidate related queries
    mutate('cfg-knowbase-system-chunks-vectorize')
    return result
  }
}


/**
 * API operation
 *
 * @method GET
 * @path /cfg/knowbase/system/items/
 */
export function useKnowbaseSystemItemsList(params?: { page?: number; page_size?: number }, client?: API): ReturnType<typeof useSWR<PaginatedArchiveItemList>> {
  return useSWR<PaginatedArchiveItemList>(
    params ? ['cfg-knowbase-system-items', params] : 'cfg-knowbase-system-items',
    () => Fetchers.getKnowbaseSystemItemsList(params, client)
  )
}


/**
 * API operation
 *
 * @method POST
 * @path /cfg/knowbase/system/items/
 */
export function useCreateKnowbaseSystemItemsCreate() {
  const { mutate } = useSWRConfig()

  return async (data: ArchiveItemRequest, client?: API): Promise<ArchiveItem> => {
    const result = await Fetchers.createKnowbaseSystemItemsCreate(data, client)
    // Revalidate related queries
    mutate('cfg-knowbase-system-items')
    return result
  }
}


/**
 * API operation
 *
 * @method GET
 * @path /cfg/knowbase/system/items/{id}/
 */
export function useKnowbaseSystemItemsRetrieve(id: string, client?: API): ReturnType<typeof useSWR<ArchiveItemDetail>> {
  return useSWR<ArchiveItemDetail>(
    ['cfg-knowbase-system-item', id],
    () => Fetchers.getKnowbaseSystemItemsRetrieve(id, client)
  )
}


/**
 * API operation
 *
 * @method PUT
 * @path /cfg/knowbase/system/items/{id}/
 */
export function useUpdateKnowbaseSystemItemsUpdate() {
  const { mutate } = useSWRConfig()

  return async (id: string, data: ArchiveItemRequest, client?: API): Promise<ArchiveItem> => {
    const result = await Fetchers.updateKnowbaseSystemItemsUpdate(id, data, client)
    // Revalidate related queries
    mutate('cfg-knowbase-system-items')
    mutate('cfg-knowbase-system-item')
    return result
  }
}


/**
 * API operation
 *
 * @method PATCH
 * @path /cfg/knowbase/system/items/{id}/
 */
export function usePartialUpdateKnowbaseSystemItemsPartialUpdate() {
  const { mutate } = useSWRConfig()

  return async (id: string, data?: PatchedArchiveItemRequest, client?: API): Promise<ArchiveItem> => {
    const result = await Fetchers.partialUpdateKnowbaseSystemItemsPartialUpdate(id, data, client)
    // Revalidate related queries
    mutate('cfg-knowbase-system-items-partial')
    return result
  }
}


/**
 * API operation
 *
 * @method DELETE
 * @path /cfg/knowbase/system/items/{id}/
 */
export function useDeleteKnowbaseSystemItemsDestroy() {
  const { mutate } = useSWRConfig()

  return async (id: string, client?: API): Promise<void> => {
    const result = await Fetchers.deleteKnowbaseSystemItemsDestroy(id, client)
    // Revalidate related queries
    mutate('cfg-knowbase-system-items')
    mutate('cfg-knowbase-system-item')
    return result
  }
}


/**
 * Get item chunks
 *
 * @method GET
 * @path /cfg/knowbase/system/items/{id}/chunks/
 */
export function useKnowbaseSystemItemsChunksList(id: string, params?: { page?: number; page_size?: number }, client?: API): ReturnType<typeof useSWR<PaginatedArchiveItemChunkList>> {
  return useSWR<PaginatedArchiveItemChunkList>(
    ['cfg-knowbase-system-items-chunks', id],
    () => Fetchers.getKnowbaseSystemItemsChunksList(id, params, client)
  )
}


/**
 * Get item content
 *
 * @method GET
 * @path /cfg/knowbase/system/items/{id}/content/
 */
export function useKnowbaseSystemItemsContentRetrieve(id: string, client?: API): ReturnType<typeof useSWR<ArchiveItemDetail>> {
  return useSWR<ArchiveItemDetail>(
    ['cfg-knowbase-system-items-content', id],
    () => Fetchers.getKnowbaseSystemItemsContentRetrieve(id, client)
  )
}


