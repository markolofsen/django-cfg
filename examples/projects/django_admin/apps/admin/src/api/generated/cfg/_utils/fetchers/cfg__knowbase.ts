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
import { consola } from 'consola'
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

/**
 * API operation
 *
 * @method GET
 * @path /cfg/knowbase/admin/chat/
 */
export async function getKnowbaseAdminChatList(  params?: { page?: number; page_size?: number },  client?: any
): Promise<PaginatedChatResponseList> {
  const api = client || getAPIInstance()
  const response = await api.cfg_knowbase.adminChatList(params?.page, params?.page_size)
  try {
    return PaginatedChatResponseListSchema.parse(response)
  } catch (error) {
    // Zod validation error - log detailed information
    consola.error('❌ Zod Validation Failed');
    consola.box({
      title: 'getKnowbaseAdminChatList',
      message: `Path: /cfg/knowbase/admin/chat/\nMethod: GET`,
      style: {
        borderColor: 'red',
        borderStyle: 'rounded'
      }
    });

    if (error instanceof Error && 'issues' in error && Array.isArray((error as any).issues)) {
      consola.error('Validation Issues:');
      (error as any).issues.forEach((issue: any, index: number) => {
        consola.error(`  ${index + 1}. ${issue.path.join('.') || 'root'}`);
        consola.error(`     ├─ Message: ${issue.message}`);
        if (issue.expected) consola.error(`     ├─ Expected: ${issue.expected}`);
        if (issue.received) consola.error(`     └─ Received: ${issue.received}`);
      });
    }

    consola.error('Response data:', response);

    // Re-throw the error
    throw error;
  }
}


/**
 * API operation
 *
 * @method POST
 * @path /cfg/knowbase/admin/chat/
 */
export async function createKnowbaseAdminChatCreate(  data: ChatResponseRequest,  client?: any
): Promise<ChatResponse> {
  const api = client || getAPIInstance()
  const response = await api.cfg_knowbase.adminChatCreate(data)
  try {
    return ChatResponseSchema.parse(response)
  } catch (error) {
    // Zod validation error - log detailed information
    consola.error('❌ Zod Validation Failed');
    consola.box({
      title: 'createKnowbaseAdminChatCreate',
      message: `Path: /cfg/knowbase/admin/chat/\nMethod: POST`,
      style: {
        borderColor: 'red',
        borderStyle: 'rounded'
      }
    });

    if (error instanceof Error && 'issues' in error && Array.isArray((error as any).issues)) {
      consola.error('Validation Issues:');
      (error as any).issues.forEach((issue: any, index: number) => {
        consola.error(`  ${index + 1}. ${issue.path.join('.') || 'root'}`);
        consola.error(`     ├─ Message: ${issue.message}`);
        if (issue.expected) consola.error(`     ├─ Expected: ${issue.expected}`);
        if (issue.received) consola.error(`     └─ Received: ${issue.received}`);
      });
    }

    consola.error('Response data:', response);

    // Re-throw the error
    throw error;
  }
}


/**
 * API operation
 *
 * @method GET
 * @path /cfg/knowbase/admin/chat/{id}/
 */
export async function getKnowbaseAdminChatRetrieve(  id: string,  client?: any
): Promise<ChatResponse> {
  const api = client || getAPIInstance()
  const response = await api.cfg_knowbase.adminChatRetrieve(id)
  try {
    return ChatResponseSchema.parse(response)
  } catch (error) {
    // Zod validation error - log detailed information
    consola.error('❌ Zod Validation Failed');
    consola.box({
      title: 'getKnowbaseAdminChatRetrieve',
      message: `Path: /cfg/knowbase/admin/chat/{id}/\nMethod: GET`,
      style: {
        borderColor: 'red',
        borderStyle: 'rounded'
      }
    });

    if (error instanceof Error && 'issues' in error && Array.isArray((error as any).issues)) {
      consola.error('Validation Issues:');
      (error as any).issues.forEach((issue: any, index: number) => {
        consola.error(`  ${index + 1}. ${issue.path.join('.') || 'root'}`);
        consola.error(`     ├─ Message: ${issue.message}`);
        if (issue.expected) consola.error(`     ├─ Expected: ${issue.expected}`);
        if (issue.received) consola.error(`     └─ Received: ${issue.received}`);
      });
    }

    consola.error('Response data:', response);

    // Re-throw the error
    throw error;
  }
}


/**
 * API operation
 *
 * @method PUT
 * @path /cfg/knowbase/admin/chat/{id}/
 */
export async function updateKnowbaseAdminChatUpdate(  id: string, data: ChatResponseRequest,  client?: any
): Promise<ChatResponse> {
  const api = client || getAPIInstance()
  const response = await api.cfg_knowbase.adminChatUpdate(id, data)
  try {
    return ChatResponseSchema.parse(response)
  } catch (error) {
    // Zod validation error - log detailed information
    consola.error('❌ Zod Validation Failed');
    consola.box({
      title: 'updateKnowbaseAdminChatUpdate',
      message: `Path: /cfg/knowbase/admin/chat/{id}/\nMethod: PUT`,
      style: {
        borderColor: 'red',
        borderStyle: 'rounded'
      }
    });

    if (error instanceof Error && 'issues' in error && Array.isArray((error as any).issues)) {
      consola.error('Validation Issues:');
      (error as any).issues.forEach((issue: any, index: number) => {
        consola.error(`  ${index + 1}. ${issue.path.join('.') || 'root'}`);
        consola.error(`     ├─ Message: ${issue.message}`);
        if (issue.expected) consola.error(`     ├─ Expected: ${issue.expected}`);
        if (issue.received) consola.error(`     └─ Received: ${issue.received}`);
      });
    }

    consola.error('Response data:', response);

    // Re-throw the error
    throw error;
  }
}


/**
 * API operation
 *
 * @method PATCH
 * @path /cfg/knowbase/admin/chat/{id}/
 */
export async function partialUpdateKnowbaseAdminChatPartialUpdate(  id: string, data?: PatchedChatResponseRequest,  client?: any
): Promise<ChatResponse> {
  const api = client || getAPIInstance()
  const response = await api.cfg_knowbase.adminChatPartialUpdate(id, data)
  try {
    return ChatResponseSchema.parse(response)
  } catch (error) {
    // Zod validation error - log detailed information
    consola.error('❌ Zod Validation Failed');
    consola.box({
      title: 'partialUpdateKnowbaseAdminChatPartialUpdate',
      message: `Path: /cfg/knowbase/admin/chat/{id}/\nMethod: PATCH`,
      style: {
        borderColor: 'red',
        borderStyle: 'rounded'
      }
    });

    if (error instanceof Error && 'issues' in error && Array.isArray((error as any).issues)) {
      consola.error('Validation Issues:');
      (error as any).issues.forEach((issue: any, index: number) => {
        consola.error(`  ${index + 1}. ${issue.path.join('.') || 'root'}`);
        consola.error(`     ├─ Message: ${issue.message}`);
        if (issue.expected) consola.error(`     ├─ Expected: ${issue.expected}`);
        if (issue.received) consola.error(`     └─ Received: ${issue.received}`);
      });
    }

    consola.error('Response data:', response);

    // Re-throw the error
    throw error;
  }
}


/**
 * API operation
 *
 * @method DELETE
 * @path /cfg/knowbase/admin/chat/{id}/
 */
export async function deleteKnowbaseAdminChatDestroy(  id: string,  client?: any
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
export async function getKnowbaseAdminChatHistoryRetrieve(  id: string,  client?: any
): Promise<ChatHistory> {
  const api = client || getAPIInstance()
  const response = await api.cfg_knowbase.adminChatHistoryRetrieve(id)
  try {
    return ChatHistorySchema.parse(response)
  } catch (error) {
    // Zod validation error - log detailed information
    consola.error('❌ Zod Validation Failed');
    consola.box({
      title: 'getKnowbaseAdminChatHistoryRetrieve',
      message: `Path: /cfg/knowbase/admin/chat/{id}/history/\nMethod: GET`,
      style: {
        borderColor: 'red',
        borderStyle: 'rounded'
      }
    });

    if (error instanceof Error && 'issues' in error && Array.isArray((error as any).issues)) {
      consola.error('Validation Issues:');
      (error as any).issues.forEach((issue: any, index: number) => {
        consola.error(`  ${index + 1}. ${issue.path.join('.') || 'root'}`);
        consola.error(`     ├─ Message: ${issue.message}`);
        if (issue.expected) consola.error(`     ├─ Expected: ${issue.expected}`);
        if (issue.received) consola.error(`     └─ Received: ${issue.received}`);
      });
    }

    consola.error('Response data:', response);

    // Re-throw the error
    throw error;
  }
}


/**
 * Process chat query with RAG
 *
 * @method POST
 * @path /cfg/knowbase/admin/chat/query/
 */
export async function createKnowbaseAdminChatQueryCreate(  data: ChatQueryRequest,  client?: any
): Promise<ChatResponse> {
  const api = client || getAPIInstance()
  const response = await api.cfg_knowbase.adminChatQueryCreate(data)
  try {
    return ChatResponseSchema.parse(response)
  } catch (error) {
    // Zod validation error - log detailed information
    consola.error('❌ Zod Validation Failed');
    consola.box({
      title: 'createKnowbaseAdminChatQueryCreate',
      message: `Path: /cfg/knowbase/admin/chat/query/\nMethod: POST`,
      style: {
        borderColor: 'red',
        borderStyle: 'rounded'
      }
    });

    if (error instanceof Error && 'issues' in error && Array.isArray((error as any).issues)) {
      consola.error('Validation Issues:');
      (error as any).issues.forEach((issue: any, index: number) => {
        consola.error(`  ${index + 1}. ${issue.path.join('.') || 'root'}`);
        consola.error(`     ├─ Message: ${issue.message}`);
        if (issue.expected) consola.error(`     ├─ Expected: ${issue.expected}`);
        if (issue.received) consola.error(`     └─ Received: ${issue.received}`);
      });
    }

    consola.error('Response data:', response);

    // Re-throw the error
    throw error;
  }
}


/**
 * List user documents
 *
 * @method GET
 * @path /cfg/knowbase/admin/documents/
 */
export async function getKnowbaseAdminDocumentsList(  params?: { page?: number; page_size?: number; status?: string },  client?: any
): Promise<PaginatedDocumentList> {
  const api = client || getAPIInstance()
  const response = await api.cfg_knowbase.adminDocumentsList(params?.page, params?.page_size, params?.status)
  try {
    return PaginatedDocumentListSchema.parse(response)
  } catch (error) {
    // Zod validation error - log detailed information
    consola.error('❌ Zod Validation Failed');
    consola.box({
      title: 'getKnowbaseAdminDocumentsList',
      message: `Path: /cfg/knowbase/admin/documents/\nMethod: GET`,
      style: {
        borderColor: 'red',
        borderStyle: 'rounded'
      }
    });

    if (error instanceof Error && 'issues' in error && Array.isArray((error as any).issues)) {
      consola.error('Validation Issues:');
      (error as any).issues.forEach((issue: any, index: number) => {
        consola.error(`  ${index + 1}. ${issue.path.join('.') || 'root'}`);
        consola.error(`     ├─ Message: ${issue.message}`);
        if (issue.expected) consola.error(`     ├─ Expected: ${issue.expected}`);
        if (issue.received) consola.error(`     └─ Received: ${issue.received}`);
      });
    }

    consola.error('Response data:', response);

    // Re-throw the error
    throw error;
  }
}


/**
 * Upload new document
 *
 * @method POST
 * @path /cfg/knowbase/admin/documents/
 */
export async function createKnowbaseAdminDocumentsCreate(  data: DocumentCreateRequest,  client?: any
): Promise<Document> {
  const api = client || getAPIInstance()
  const response = await api.cfg_knowbase.adminDocumentsCreate(data)
  try {
    return DocumentSchema.parse(response)
  } catch (error) {
    // Zod validation error - log detailed information
    consola.error('❌ Zod Validation Failed');
    consola.box({
      title: 'createKnowbaseAdminDocumentsCreate',
      message: `Path: /cfg/knowbase/admin/documents/\nMethod: POST`,
      style: {
        borderColor: 'red',
        borderStyle: 'rounded'
      }
    });

    if (error instanceof Error && 'issues' in error && Array.isArray((error as any).issues)) {
      consola.error('Validation Issues:');
      (error as any).issues.forEach((issue: any, index: number) => {
        consola.error(`  ${index + 1}. ${issue.path.join('.') || 'root'}`);
        consola.error(`     ├─ Message: ${issue.message}`);
        if (issue.expected) consola.error(`     ├─ Expected: ${issue.expected}`);
        if (issue.received) consola.error(`     └─ Received: ${issue.received}`);
      });
    }

    consola.error('Response data:', response);

    // Re-throw the error
    throw error;
  }
}


/**
 * Get document details
 *
 * @method GET
 * @path /cfg/knowbase/admin/documents/{id}/
 */
export async function getKnowbaseAdminDocumentsRetrieve(  id: string,  client?: any
): Promise<Document> {
  const api = client || getAPIInstance()
  const response = await api.cfg_knowbase.adminDocumentsRetrieve(id)
  try {
    return DocumentSchema.parse(response)
  } catch (error) {
    // Zod validation error - log detailed information
    consola.error('❌ Zod Validation Failed');
    consola.box({
      title: 'getKnowbaseAdminDocumentsRetrieve',
      message: `Path: /cfg/knowbase/admin/documents/{id}/\nMethod: GET`,
      style: {
        borderColor: 'red',
        borderStyle: 'rounded'
      }
    });

    if (error instanceof Error && 'issues' in error && Array.isArray((error as any).issues)) {
      consola.error('Validation Issues:');
      (error as any).issues.forEach((issue: any, index: number) => {
        consola.error(`  ${index + 1}. ${issue.path.join('.') || 'root'}`);
        consola.error(`     ├─ Message: ${issue.message}`);
        if (issue.expected) consola.error(`     ├─ Expected: ${issue.expected}`);
        if (issue.received) consola.error(`     └─ Received: ${issue.received}`);
      });
    }

    consola.error('Response data:', response);

    // Re-throw the error
    throw error;
  }
}


/**
 * API operation
 *
 * @method PUT
 * @path /cfg/knowbase/admin/documents/{id}/
 */
export async function updateKnowbaseAdminDocumentsUpdate(  id: string, data: DocumentRequest,  client?: any
): Promise<Document> {
  const api = client || getAPIInstance()
  const response = await api.cfg_knowbase.adminDocumentsUpdate(id, data)
  try {
    return DocumentSchema.parse(response)
  } catch (error) {
    // Zod validation error - log detailed information
    consola.error('❌ Zod Validation Failed');
    consola.box({
      title: 'updateKnowbaseAdminDocumentsUpdate',
      message: `Path: /cfg/knowbase/admin/documents/{id}/\nMethod: PUT`,
      style: {
        borderColor: 'red',
        borderStyle: 'rounded'
      }
    });

    if (error instanceof Error && 'issues' in error && Array.isArray((error as any).issues)) {
      consola.error('Validation Issues:');
      (error as any).issues.forEach((issue: any, index: number) => {
        consola.error(`  ${index + 1}. ${issue.path.join('.') || 'root'}`);
        consola.error(`     ├─ Message: ${issue.message}`);
        if (issue.expected) consola.error(`     ├─ Expected: ${issue.expected}`);
        if (issue.received) consola.error(`     └─ Received: ${issue.received}`);
      });
    }

    consola.error('Response data:', response);

    // Re-throw the error
    throw error;
  }
}


/**
 * API operation
 *
 * @method PATCH
 * @path /cfg/knowbase/admin/documents/{id}/
 */
export async function partialUpdateKnowbaseAdminDocumentsPartialUpdate(  id: string, data?: PatchedDocumentRequest,  client?: any
): Promise<Document> {
  const api = client || getAPIInstance()
  const response = await api.cfg_knowbase.adminDocumentsPartialUpdate(id, data)
  try {
    return DocumentSchema.parse(response)
  } catch (error) {
    // Zod validation error - log detailed information
    consola.error('❌ Zod Validation Failed');
    consola.box({
      title: 'partialUpdateKnowbaseAdminDocumentsPartialUpdate',
      message: `Path: /cfg/knowbase/admin/documents/{id}/\nMethod: PATCH`,
      style: {
        borderColor: 'red',
        borderStyle: 'rounded'
      }
    });

    if (error instanceof Error && 'issues' in error && Array.isArray((error as any).issues)) {
      consola.error('Validation Issues:');
      (error as any).issues.forEach((issue: any, index: number) => {
        consola.error(`  ${index + 1}. ${issue.path.join('.') || 'root'}`);
        consola.error(`     ├─ Message: ${issue.message}`);
        if (issue.expected) consola.error(`     ├─ Expected: ${issue.expected}`);
        if (issue.received) consola.error(`     └─ Received: ${issue.received}`);
      });
    }

    consola.error('Response data:', response);

    // Re-throw the error
    throw error;
  }
}


/**
 * Delete document
 *
 * @method DELETE
 * @path /cfg/knowbase/admin/documents/{id}/
 */
export async function deleteKnowbaseAdminDocumentsDestroy(  id: string,  client?: any
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
export async function createKnowbaseAdminDocumentsReprocessCreate(  id: string, data: DocumentRequest,  client?: any
): Promise<Document> {
  const api = client || getAPIInstance()
  const response = await api.cfg_knowbase.adminDocumentsReprocessCreate(id, data)
  try {
    return DocumentSchema.parse(response)
  } catch (error) {
    // Zod validation error - log detailed information
    consola.error('❌ Zod Validation Failed');
    consola.box({
      title: 'createKnowbaseAdminDocumentsReprocessCreate',
      message: `Path: /cfg/knowbase/admin/documents/{id}/reprocess/\nMethod: POST`,
      style: {
        borderColor: 'red',
        borderStyle: 'rounded'
      }
    });

    if (error instanceof Error && 'issues' in error && Array.isArray((error as any).issues)) {
      consola.error('Validation Issues:');
      (error as any).issues.forEach((issue: any, index: number) => {
        consola.error(`  ${index + 1}. ${issue.path.join('.') || 'root'}`);
        consola.error(`     ├─ Message: ${issue.message}`);
        if (issue.expected) consola.error(`     ├─ Expected: ${issue.expected}`);
        if (issue.received) consola.error(`     └─ Received: ${issue.received}`);
      });
    }

    consola.error('Response data:', response);

    // Re-throw the error
    throw error;
  }
}


/**
 * Get document processing status
 *
 * @method GET
 * @path /cfg/knowbase/admin/documents/{id}/status/
 */
export async function getKnowbaseAdminDocumentsStatusRetrieve(  id: string,  client?: any
): Promise<DocumentProcessingStatus> {
  const api = client || getAPIInstance()
  const response = await api.cfg_knowbase.adminDocumentsStatusRetrieve(id)
  try {
    return DocumentProcessingStatusSchema.parse(response)
  } catch (error) {
    // Zod validation error - log detailed information
    consola.error('❌ Zod Validation Failed');
    consola.box({
      title: 'getKnowbaseAdminDocumentsStatusRetrieve',
      message: `Path: /cfg/knowbase/admin/documents/{id}/status/\nMethod: GET`,
      style: {
        borderColor: 'red',
        borderStyle: 'rounded'
      }
    });

    if (error instanceof Error && 'issues' in error && Array.isArray((error as any).issues)) {
      consola.error('Validation Issues:');
      (error as any).issues.forEach((issue: any, index: number) => {
        consola.error(`  ${index + 1}. ${issue.path.join('.') || 'root'}`);
        consola.error(`     ├─ Message: ${issue.message}`);
        if (issue.expected) consola.error(`     ├─ Expected: ${issue.expected}`);
        if (issue.received) consola.error(`     └─ Received: ${issue.received}`);
      });
    }

    consola.error('Response data:', response);

    // Re-throw the error
    throw error;
  }
}


/**
 * Get processing statistics
 *
 * @method GET
 * @path /cfg/knowbase/admin/documents/stats/
 */
export async function getKnowbaseAdminDocumentsStatsRetrieve(  client?: any
): Promise<DocumentStats> {
  const api = client || getAPIInstance()
  const response = await api.cfg_knowbase.adminDocumentsStatsRetrieve()
  try {
    return DocumentStatsSchema.parse(response)
  } catch (error) {
    // Zod validation error - log detailed information
    consola.error('❌ Zod Validation Failed');
    consola.box({
      title: 'getKnowbaseAdminDocumentsStatsRetrieve',
      message: `Path: /cfg/knowbase/admin/documents/stats/\nMethod: GET`,
      style: {
        borderColor: 'red',
        borderStyle: 'rounded'
      }
    });

    if (error instanceof Error && 'issues' in error && Array.isArray((error as any).issues)) {
      consola.error('Validation Issues:');
      (error as any).issues.forEach((issue: any, index: number) => {
        consola.error(`  ${index + 1}. ${issue.path.join('.') || 'root'}`);
        consola.error(`     ├─ Message: ${issue.message}`);
        if (issue.expected) consola.error(`     ├─ Expected: ${issue.expected}`);
        if (issue.received) consola.error(`     └─ Received: ${issue.received}`);
      });
    }

    consola.error('Response data:', response);

    // Re-throw the error
    throw error;
  }
}


/**
 * List user chat sessions
 *
 * @method GET
 * @path /cfg/knowbase/admin/sessions/
 */
export async function getKnowbaseAdminSessionsList(  params?: { page?: number; page_size?: number },  client?: any
): Promise<PaginatedChatSessionList> {
  const api = client || getAPIInstance()
  const response = await api.cfg_knowbase.adminSessionsList(params?.page, params?.page_size)
  try {
    return PaginatedChatSessionListSchema.parse(response)
  } catch (error) {
    // Zod validation error - log detailed information
    consola.error('❌ Zod Validation Failed');
    consola.box({
      title: 'getKnowbaseAdminSessionsList',
      message: `Path: /cfg/knowbase/admin/sessions/\nMethod: GET`,
      style: {
        borderColor: 'red',
        borderStyle: 'rounded'
      }
    });

    if (error instanceof Error && 'issues' in error && Array.isArray((error as any).issues)) {
      consola.error('Validation Issues:');
      (error as any).issues.forEach((issue: any, index: number) => {
        consola.error(`  ${index + 1}. ${issue.path.join('.') || 'root'}`);
        consola.error(`     ├─ Message: ${issue.message}`);
        if (issue.expected) consola.error(`     ├─ Expected: ${issue.expected}`);
        if (issue.received) consola.error(`     └─ Received: ${issue.received}`);
      });
    }

    consola.error('Response data:', response);

    // Re-throw the error
    throw error;
  }
}


/**
 * Create new chat session
 *
 * @method POST
 * @path /cfg/knowbase/admin/sessions/
 */
export async function createKnowbaseAdminSessionsCreate(  data: ChatSessionCreateRequest,  client?: any
): Promise<ChatSession> {
  const api = client || getAPIInstance()
  const response = await api.cfg_knowbase.adminSessionsCreate(data)
  try {
    return ChatSessionSchema.parse(response)
  } catch (error) {
    // Zod validation error - log detailed information
    consola.error('❌ Zod Validation Failed');
    consola.box({
      title: 'createKnowbaseAdminSessionsCreate',
      message: `Path: /cfg/knowbase/admin/sessions/\nMethod: POST`,
      style: {
        borderColor: 'red',
        borderStyle: 'rounded'
      }
    });

    if (error instanceof Error && 'issues' in error && Array.isArray((error as any).issues)) {
      consola.error('Validation Issues:');
      (error as any).issues.forEach((issue: any, index: number) => {
        consola.error(`  ${index + 1}. ${issue.path.join('.') || 'root'}`);
        consola.error(`     ├─ Message: ${issue.message}`);
        if (issue.expected) consola.error(`     ├─ Expected: ${issue.expected}`);
        if (issue.received) consola.error(`     └─ Received: ${issue.received}`);
      });
    }

    consola.error('Response data:', response);

    // Re-throw the error
    throw error;
  }
}


/**
 * API operation
 *
 * @method GET
 * @path /cfg/knowbase/admin/sessions/{id}/
 */
export async function getKnowbaseAdminSessionsRetrieve(  id: string,  client?: any
): Promise<ChatSession> {
  const api = client || getAPIInstance()
  const response = await api.cfg_knowbase.adminSessionsRetrieve(id)
  try {
    return ChatSessionSchema.parse(response)
  } catch (error) {
    // Zod validation error - log detailed information
    consola.error('❌ Zod Validation Failed');
    consola.box({
      title: 'getKnowbaseAdminSessionsRetrieve',
      message: `Path: /cfg/knowbase/admin/sessions/{id}/\nMethod: GET`,
      style: {
        borderColor: 'red',
        borderStyle: 'rounded'
      }
    });

    if (error instanceof Error && 'issues' in error && Array.isArray((error as any).issues)) {
      consola.error('Validation Issues:');
      (error as any).issues.forEach((issue: any, index: number) => {
        consola.error(`  ${index + 1}. ${issue.path.join('.') || 'root'}`);
        consola.error(`     ├─ Message: ${issue.message}`);
        if (issue.expected) consola.error(`     ├─ Expected: ${issue.expected}`);
        if (issue.received) consola.error(`     └─ Received: ${issue.received}`);
      });
    }

    consola.error('Response data:', response);

    // Re-throw the error
    throw error;
  }
}


/**
 * API operation
 *
 * @method PUT
 * @path /cfg/knowbase/admin/sessions/{id}/
 */
export async function updateKnowbaseAdminSessionsUpdate(  id: string, data: ChatSessionRequest,  client?: any
): Promise<ChatSession> {
  const api = client || getAPIInstance()
  const response = await api.cfg_knowbase.adminSessionsUpdate(id, data)
  try {
    return ChatSessionSchema.parse(response)
  } catch (error) {
    // Zod validation error - log detailed information
    consola.error('❌ Zod Validation Failed');
    consola.box({
      title: 'updateKnowbaseAdminSessionsUpdate',
      message: `Path: /cfg/knowbase/admin/sessions/{id}/\nMethod: PUT`,
      style: {
        borderColor: 'red',
        borderStyle: 'rounded'
      }
    });

    if (error instanceof Error && 'issues' in error && Array.isArray((error as any).issues)) {
      consola.error('Validation Issues:');
      (error as any).issues.forEach((issue: any, index: number) => {
        consola.error(`  ${index + 1}. ${issue.path.join('.') || 'root'}`);
        consola.error(`     ├─ Message: ${issue.message}`);
        if (issue.expected) consola.error(`     ├─ Expected: ${issue.expected}`);
        if (issue.received) consola.error(`     └─ Received: ${issue.received}`);
      });
    }

    consola.error('Response data:', response);

    // Re-throw the error
    throw error;
  }
}


/**
 * API operation
 *
 * @method PATCH
 * @path /cfg/knowbase/admin/sessions/{id}/
 */
export async function partialUpdateKnowbaseAdminSessionsPartialUpdate(  id: string, data?: PatchedChatSessionRequest,  client?: any
): Promise<ChatSession> {
  const api = client || getAPIInstance()
  const response = await api.cfg_knowbase.adminSessionsPartialUpdate(id, data)
  try {
    return ChatSessionSchema.parse(response)
  } catch (error) {
    // Zod validation error - log detailed information
    consola.error('❌ Zod Validation Failed');
    consola.box({
      title: 'partialUpdateKnowbaseAdminSessionsPartialUpdate',
      message: `Path: /cfg/knowbase/admin/sessions/{id}/\nMethod: PATCH`,
      style: {
        borderColor: 'red',
        borderStyle: 'rounded'
      }
    });

    if (error instanceof Error && 'issues' in error && Array.isArray((error as any).issues)) {
      consola.error('Validation Issues:');
      (error as any).issues.forEach((issue: any, index: number) => {
        consola.error(`  ${index + 1}. ${issue.path.join('.') || 'root'}`);
        consola.error(`     ├─ Message: ${issue.message}`);
        if (issue.expected) consola.error(`     ├─ Expected: ${issue.expected}`);
        if (issue.received) consola.error(`     └─ Received: ${issue.received}`);
      });
    }

    consola.error('Response data:', response);

    // Re-throw the error
    throw error;
  }
}


/**
 * API operation
 *
 * @method DELETE
 * @path /cfg/knowbase/admin/sessions/{id}/
 */
export async function deleteKnowbaseAdminSessionsDestroy(  id: string,  client?: any
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
export async function createKnowbaseAdminSessionsActivateCreate(  id: string, data: ChatSessionRequest,  client?: any
): Promise<ChatSession> {
  const api = client || getAPIInstance()
  const response = await api.cfg_knowbase.adminSessionsActivateCreate(id, data)
  try {
    return ChatSessionSchema.parse(response)
  } catch (error) {
    // Zod validation error - log detailed information
    consola.error('❌ Zod Validation Failed');
    consola.box({
      title: 'createKnowbaseAdminSessionsActivateCreate',
      message: `Path: /cfg/knowbase/admin/sessions/{id}/activate/\nMethod: POST`,
      style: {
        borderColor: 'red',
        borderStyle: 'rounded'
      }
    });

    if (error instanceof Error && 'issues' in error && Array.isArray((error as any).issues)) {
      consola.error('Validation Issues:');
      (error as any).issues.forEach((issue: any, index: number) => {
        consola.error(`  ${index + 1}. ${issue.path.join('.') || 'root'}`);
        consola.error(`     ├─ Message: ${issue.message}`);
        if (issue.expected) consola.error(`     ├─ Expected: ${issue.expected}`);
        if (issue.received) consola.error(`     └─ Received: ${issue.received}`);
      });
    }

    consola.error('Response data:', response);

    // Re-throw the error
    throw error;
  }
}


/**
 * Archive chat session
 *
 * @method POST
 * @path /cfg/knowbase/admin/sessions/{id}/archive/
 */
export async function createKnowbaseAdminSessionsArchiveCreate(  id: string, data: ChatSessionRequest,  client?: any
): Promise<ChatSession> {
  const api = client || getAPIInstance()
  const response = await api.cfg_knowbase.adminSessionsArchiveCreate(id, data)
  try {
    return ChatSessionSchema.parse(response)
  } catch (error) {
    // Zod validation error - log detailed information
    consola.error('❌ Zod Validation Failed');
    consola.box({
      title: 'createKnowbaseAdminSessionsArchiveCreate',
      message: `Path: /cfg/knowbase/admin/sessions/{id}/archive/\nMethod: POST`,
      style: {
        borderColor: 'red',
        borderStyle: 'rounded'
      }
    });

    if (error instanceof Error && 'issues' in error && Array.isArray((error as any).issues)) {
      consola.error('Validation Issues:');
      (error as any).issues.forEach((issue: any, index: number) => {
        consola.error(`  ${index + 1}. ${issue.path.join('.') || 'root'}`);
        consola.error(`     ├─ Message: ${issue.message}`);
        if (issue.expected) consola.error(`     ├─ Expected: ${issue.expected}`);
        if (issue.received) consola.error(`     └─ Received: ${issue.received}`);
      });
    }

    consola.error('Response data:', response);

    // Re-throw the error
    throw error;
  }
}


/**
 * List public categories
 *
 * @method GET
 * @path /cfg/knowbase/categories/
 */
export async function getKnowbaseCategoriesList(  params?: { page?: number; page_size?: number },  client?: any
): Promise<PaginatedPublicCategoryList> {
  const api = client || getAPIInstance()
  const response = await api.cfg_knowbase.categoriesList(params?.page, params?.page_size)
  try {
    return PaginatedPublicCategoryListSchema.parse(response)
  } catch (error) {
    // Zod validation error - log detailed information
    consola.error('❌ Zod Validation Failed');
    consola.box({
      title: 'getKnowbaseCategoriesList',
      message: `Path: /cfg/knowbase/categories/\nMethod: GET`,
      style: {
        borderColor: 'red',
        borderStyle: 'rounded'
      }
    });

    if (error instanceof Error && 'issues' in error && Array.isArray((error as any).issues)) {
      consola.error('Validation Issues:');
      (error as any).issues.forEach((issue: any, index: number) => {
        consola.error(`  ${index + 1}. ${issue.path.join('.') || 'root'}`);
        consola.error(`     ├─ Message: ${issue.message}`);
        if (issue.expected) consola.error(`     ├─ Expected: ${issue.expected}`);
        if (issue.received) consola.error(`     └─ Received: ${issue.received}`);
      });
    }

    consola.error('Response data:', response);

    // Re-throw the error
    throw error;
  }
}


/**
 * Get public category details
 *
 * @method GET
 * @path /cfg/knowbase/categories/{id}/
 */
export async function getKnowbaseCategoriesRetrieve(  id: string,  client?: any
): Promise<PublicCategory> {
  const api = client || getAPIInstance()
  const response = await api.cfg_knowbase.categoriesRetrieve(id)
  try {
    return PublicCategorySchema.parse(response)
  } catch (error) {
    // Zod validation error - log detailed information
    consola.error('❌ Zod Validation Failed');
    consola.box({
      title: 'getKnowbaseCategoriesRetrieve',
      message: `Path: /cfg/knowbase/categories/{id}/\nMethod: GET`,
      style: {
        borderColor: 'red',
        borderStyle: 'rounded'
      }
    });

    if (error instanceof Error && 'issues' in error && Array.isArray((error as any).issues)) {
      consola.error('Validation Issues:');
      (error as any).issues.forEach((issue: any, index: number) => {
        consola.error(`  ${index + 1}. ${issue.path.join('.') || 'root'}`);
        consola.error(`     ├─ Message: ${issue.message}`);
        if (issue.expected) consola.error(`     ├─ Expected: ${issue.expected}`);
        if (issue.received) consola.error(`     └─ Received: ${issue.received}`);
      });
    }

    consola.error('Response data:', response);

    // Re-throw the error
    throw error;
  }
}


/**
 * List public documents
 *
 * @method GET
 * @path /cfg/knowbase/documents/
 */
export async function getKnowbaseDocumentsList(  params?: { category?: string; page?: number; page_size?: number; search?: string },  client?: any
): Promise<PaginatedPublicDocumentListList> {
  const api = client || getAPIInstance()
  const response = await api.cfg_knowbase.documentsList(params?.category, params?.page, params?.page_size, params?.search)
  try {
    return PaginatedPublicDocumentListListSchema.parse(response)
  } catch (error) {
    // Zod validation error - log detailed information
    consola.error('❌ Zod Validation Failed');
    consola.box({
      title: 'getKnowbaseDocumentsList',
      message: `Path: /cfg/knowbase/documents/\nMethod: GET`,
      style: {
        borderColor: 'red',
        borderStyle: 'rounded'
      }
    });

    if (error instanceof Error && 'issues' in error && Array.isArray((error as any).issues)) {
      consola.error('Validation Issues:');
      (error as any).issues.forEach((issue: any, index: number) => {
        consola.error(`  ${index + 1}. ${issue.path.join('.') || 'root'}`);
        consola.error(`     ├─ Message: ${issue.message}`);
        if (issue.expected) consola.error(`     ├─ Expected: ${issue.expected}`);
        if (issue.received) consola.error(`     └─ Received: ${issue.received}`);
      });
    }

    consola.error('Response data:', response);

    // Re-throw the error
    throw error;
  }
}


/**
 * Get public document details
 *
 * @method GET
 * @path /cfg/knowbase/documents/{id}/
 */
export async function getKnowbaseDocumentsRetrieve(  id: string,  client?: any
): Promise<PublicDocument> {
  const api = client || getAPIInstance()
  const response = await api.cfg_knowbase.documentsRetrieve(id)
  try {
    return PublicDocumentSchema.parse(response)
  } catch (error) {
    // Zod validation error - log detailed information
    consola.error('❌ Zod Validation Failed');
    consola.box({
      title: 'getKnowbaseDocumentsRetrieve',
      message: `Path: /cfg/knowbase/documents/{id}/\nMethod: GET`,
      style: {
        borderColor: 'red',
        borderStyle: 'rounded'
      }
    });

    if (error instanceof Error && 'issues' in error && Array.isArray((error as any).issues)) {
      consola.error('Validation Issues:');
      (error as any).issues.forEach((issue: any, index: number) => {
        consola.error(`  ${index + 1}. ${issue.path.join('.') || 'root'}`);
        consola.error(`     ├─ Message: ${issue.message}`);
        if (issue.expected) consola.error(`     ├─ Expected: ${issue.expected}`);
        if (issue.received) consola.error(`     └─ Received: ${issue.received}`);
      });
    }

    consola.error('Response data:', response);

    // Re-throw the error
    throw error;
  }
}


/**
 * API operation
 *
 * @method GET
 * @path /cfg/knowbase/system/archives/
 */
export async function getKnowbaseSystemArchivesList(  params?: { page?: number; page_size?: number },  client?: any
): Promise<PaginatedDocumentArchiveListList> {
  const api = client || getAPIInstance()
  const response = await api.cfg_knowbase.systemArchivesList(params?.page, params?.page_size)
  try {
    return PaginatedDocumentArchiveListListSchema.parse(response)
  } catch (error) {
    // Zod validation error - log detailed information
    consola.error('❌ Zod Validation Failed');
    consola.box({
      title: 'getKnowbaseSystemArchivesList',
      message: `Path: /cfg/knowbase/system/archives/\nMethod: GET`,
      style: {
        borderColor: 'red',
        borderStyle: 'rounded'
      }
    });

    if (error instanceof Error && 'issues' in error && Array.isArray((error as any).issues)) {
      consola.error('Validation Issues:');
      (error as any).issues.forEach((issue: any, index: number) => {
        consola.error(`  ${index + 1}. ${issue.path.join('.') || 'root'}`);
        consola.error(`     ├─ Message: ${issue.message}`);
        if (issue.expected) consola.error(`     ├─ Expected: ${issue.expected}`);
        if (issue.received) consola.error(`     └─ Received: ${issue.received}`);
      });
    }

    consola.error('Response data:', response);

    // Re-throw the error
    throw error;
  }
}


/**
 * Upload and process archive
 *
 * @method POST
 * @path /cfg/knowbase/system/archives/
 */
export async function createKnowbaseSystemArchivesCreate(  data: any,  client?: any
): Promise<ArchiveProcessingResult> {
  const api = client || getAPIInstance()
  const response = await api.cfg_knowbase.systemArchivesCreate(data)
  try {
    return ArchiveProcessingResultSchema.parse(response)
  } catch (error) {
    // Zod validation error - log detailed information
    consola.error('❌ Zod Validation Failed');
    consola.box({
      title: 'createKnowbaseSystemArchivesCreate',
      message: `Path: /cfg/knowbase/system/archives/\nMethod: POST`,
      style: {
        borderColor: 'red',
        borderStyle: 'rounded'
      }
    });

    if (error instanceof Error && 'issues' in error && Array.isArray((error as any).issues)) {
      consola.error('Validation Issues:');
      (error as any).issues.forEach((issue: any, index: number) => {
        consola.error(`  ${index + 1}. ${issue.path.join('.') || 'root'}`);
        consola.error(`     ├─ Message: ${issue.message}`);
        if (issue.expected) consola.error(`     ├─ Expected: ${issue.expected}`);
        if (issue.received) consola.error(`     └─ Received: ${issue.received}`);
      });
    }

    consola.error('Response data:', response);

    // Re-throw the error
    throw error;
  }
}


/**
 * API operation
 *
 * @method GET
 * @path /cfg/knowbase/system/archives/{id}/
 */
export async function getKnowbaseSystemArchivesRetrieve(  id: string,  client?: any
): Promise<DocumentArchiveDetail> {
  const api = client || getAPIInstance()
  const response = await api.cfg_knowbase.systemArchivesRetrieve(id)
  try {
    return DocumentArchiveDetailSchema.parse(response)
  } catch (error) {
    // Zod validation error - log detailed information
    consola.error('❌ Zod Validation Failed');
    consola.box({
      title: 'getKnowbaseSystemArchivesRetrieve',
      message: `Path: /cfg/knowbase/system/archives/{id}/\nMethod: GET`,
      style: {
        borderColor: 'red',
        borderStyle: 'rounded'
      }
    });

    if (error instanceof Error && 'issues' in error && Array.isArray((error as any).issues)) {
      consola.error('Validation Issues:');
      (error as any).issues.forEach((issue: any, index: number) => {
        consola.error(`  ${index + 1}. ${issue.path.join('.') || 'root'}`);
        consola.error(`     ├─ Message: ${issue.message}`);
        if (issue.expected) consola.error(`     ├─ Expected: ${issue.expected}`);
        if (issue.received) consola.error(`     └─ Received: ${issue.received}`);
      });
    }

    consola.error('Response data:', response);

    // Re-throw the error
    throw error;
  }
}


/**
 * API operation
 *
 * @method PUT
 * @path /cfg/knowbase/system/archives/{id}/
 */
export async function updateKnowbaseSystemArchivesUpdate(  id: string, data: DocumentArchiveRequest,  client?: any
): Promise<DocumentArchive> {
  const api = client || getAPIInstance()
  const response = await api.cfg_knowbase.systemArchivesUpdate(id, data)
  try {
    return DocumentArchiveSchema.parse(response)
  } catch (error) {
    // Zod validation error - log detailed information
    consola.error('❌ Zod Validation Failed');
    consola.box({
      title: 'updateKnowbaseSystemArchivesUpdate',
      message: `Path: /cfg/knowbase/system/archives/{id}/\nMethod: PUT`,
      style: {
        borderColor: 'red',
        borderStyle: 'rounded'
      }
    });

    if (error instanceof Error && 'issues' in error && Array.isArray((error as any).issues)) {
      consola.error('Validation Issues:');
      (error as any).issues.forEach((issue: any, index: number) => {
        consola.error(`  ${index + 1}. ${issue.path.join('.') || 'root'}`);
        consola.error(`     ├─ Message: ${issue.message}`);
        if (issue.expected) consola.error(`     ├─ Expected: ${issue.expected}`);
        if (issue.received) consola.error(`     └─ Received: ${issue.received}`);
      });
    }

    consola.error('Response data:', response);

    // Re-throw the error
    throw error;
  }
}


/**
 * API operation
 *
 * @method PATCH
 * @path /cfg/knowbase/system/archives/{id}/
 */
export async function partialUpdateKnowbaseSystemArchivesPartialUpdate(  id: string, data?: PatchedDocumentArchiveRequest,  client?: any
): Promise<DocumentArchive> {
  const api = client || getAPIInstance()
  const response = await api.cfg_knowbase.systemArchivesPartialUpdate(id, data)
  try {
    return DocumentArchiveSchema.parse(response)
  } catch (error) {
    // Zod validation error - log detailed information
    consola.error('❌ Zod Validation Failed');
    consola.box({
      title: 'partialUpdateKnowbaseSystemArchivesPartialUpdate',
      message: `Path: /cfg/knowbase/system/archives/{id}/\nMethod: PATCH`,
      style: {
        borderColor: 'red',
        borderStyle: 'rounded'
      }
    });

    if (error instanceof Error && 'issues' in error && Array.isArray((error as any).issues)) {
      consola.error('Validation Issues:');
      (error as any).issues.forEach((issue: any, index: number) => {
        consola.error(`  ${index + 1}. ${issue.path.join('.') || 'root'}`);
        consola.error(`     ├─ Message: ${issue.message}`);
        if (issue.expected) consola.error(`     ├─ Expected: ${issue.expected}`);
        if (issue.received) consola.error(`     └─ Received: ${issue.received}`);
      });
    }

    consola.error('Response data:', response);

    // Re-throw the error
    throw error;
  }
}


/**
 * API operation
 *
 * @method DELETE
 * @path /cfg/knowbase/system/archives/{id}/
 */
export async function deleteKnowbaseSystemArchivesDestroy(  id: string,  client?: any
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
export async function getKnowbaseSystemArchivesFileTreeRetrieve(  id: string,  client?: any
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
export async function getKnowbaseSystemArchivesItemsList(  id: string, params?: { page?: number; page_size?: number },  client?: any
): Promise<PaginatedArchiveItemList> {
  const api = client || getAPIInstance()
  const response = await api.cfg_knowbase.systemArchivesItemsList(id, params?.page, params?.page_size)
  try {
    return PaginatedArchiveItemListSchema.parse(response)
  } catch (error) {
    // Zod validation error - log detailed information
    consola.error('❌ Zod Validation Failed');
    consola.box({
      title: 'getKnowbaseSystemArchivesItemsList',
      message: `Path: /cfg/knowbase/system/archives/{id}/items/\nMethod: GET`,
      style: {
        borderColor: 'red',
        borderStyle: 'rounded'
      }
    });

    if (error instanceof Error && 'issues' in error && Array.isArray((error as any).issues)) {
      consola.error('Validation Issues:');
      (error as any).issues.forEach((issue: any, index: number) => {
        consola.error(`  ${index + 1}. ${issue.path.join('.') || 'root'}`);
        consola.error(`     ├─ Message: ${issue.message}`);
        if (issue.expected) consola.error(`     ├─ Expected: ${issue.expected}`);
        if (issue.received) consola.error(`     └─ Received: ${issue.received}`);
      });
    }

    consola.error('Response data:', response);

    // Re-throw the error
    throw error;
  }
}


/**
 * Search archive chunks
 *
 * @method POST
 * @path /cfg/knowbase/system/archives/{id}/search/
 */
export async function createKnowbaseSystemArchivesSearchCreate(  id: string, data: ArchiveSearchRequestRequest, params?: { page?: number; page_size?: number },  client?: any
): Promise<PaginatedArchiveSearchResultList> {
  const api = client || getAPIInstance()
  const response = await api.cfg_knowbase.systemArchivesSearchCreate(id, data, params?.page, params?.page_size)
  try {
    return PaginatedArchiveSearchResultListSchema.parse(response)
  } catch (error) {
    // Zod validation error - log detailed information
    consola.error('❌ Zod Validation Failed');
    consola.box({
      title: 'createKnowbaseSystemArchivesSearchCreate',
      message: `Path: /cfg/knowbase/system/archives/{id}/search/\nMethod: POST`,
      style: {
        borderColor: 'red',
        borderStyle: 'rounded'
      }
    });

    if (error instanceof Error && 'issues' in error && Array.isArray((error as any).issues)) {
      consola.error('Validation Issues:');
      (error as any).issues.forEach((issue: any, index: number) => {
        consola.error(`  ${index + 1}. ${issue.path.join('.') || 'root'}`);
        consola.error(`     ├─ Message: ${issue.message}`);
        if (issue.expected) consola.error(`     ├─ Expected: ${issue.expected}`);
        if (issue.received) consola.error(`     └─ Received: ${issue.received}`);
      });
    }

    consola.error('Response data:', response);

    // Re-throw the error
    throw error;
  }
}


/**
 * Re-vectorize chunks
 *
 * @method POST
 * @path /cfg/knowbase/system/archives/revectorize/
 */
export async function createKnowbaseSystemArchivesRevectorizeCreate(  data: ChunkRevectorizationRequestRequest,  client?: any
): Promise<VectorizationResult> {
  const api = client || getAPIInstance()
  const response = await api.cfg_knowbase.systemArchivesRevectorizeCreate(data)
  try {
    return VectorizationResultSchema.parse(response)
  } catch (error) {
    // Zod validation error - log detailed information
    consola.error('❌ Zod Validation Failed');
    consola.box({
      title: 'createKnowbaseSystemArchivesRevectorizeCreate',
      message: `Path: /cfg/knowbase/system/archives/revectorize/\nMethod: POST`,
      style: {
        borderColor: 'red',
        borderStyle: 'rounded'
      }
    });

    if (error instanceof Error && 'issues' in error && Array.isArray((error as any).issues)) {
      consola.error('Validation Issues:');
      (error as any).issues.forEach((issue: any, index: number) => {
        consola.error(`  ${index + 1}. ${issue.path.join('.') || 'root'}`);
        consola.error(`     ├─ Message: ${issue.message}`);
        if (issue.expected) consola.error(`     ├─ Expected: ${issue.expected}`);
        if (issue.received) consola.error(`     └─ Received: ${issue.received}`);
      });
    }

    consola.error('Response data:', response);

    // Re-throw the error
    throw error;
  }
}


/**
 * Get archive statistics
 *
 * @method GET
 * @path /cfg/knowbase/system/archives/statistics/
 */
export async function getKnowbaseSystemArchivesStatisticsRetrieve(  client?: any
): Promise<ArchiveStatistics> {
  const api = client || getAPIInstance()
  const response = await api.cfg_knowbase.systemArchivesStatisticsRetrieve()
  try {
    return ArchiveStatisticsSchema.parse(response)
  } catch (error) {
    // Zod validation error - log detailed information
    consola.error('❌ Zod Validation Failed');
    consola.box({
      title: 'getKnowbaseSystemArchivesStatisticsRetrieve',
      message: `Path: /cfg/knowbase/system/archives/statistics/\nMethod: GET`,
      style: {
        borderColor: 'red',
        borderStyle: 'rounded'
      }
    });

    if (error instanceof Error && 'issues' in error && Array.isArray((error as any).issues)) {
      consola.error('Validation Issues:');
      (error as any).issues.forEach((issue: any, index: number) => {
        consola.error(`  ${index + 1}. ${issue.path.join('.') || 'root'}`);
        consola.error(`     ├─ Message: ${issue.message}`);
        if (issue.expected) consola.error(`     ├─ Expected: ${issue.expected}`);
        if (issue.received) consola.error(`     └─ Received: ${issue.received}`);
      });
    }

    consola.error('Response data:', response);

    // Re-throw the error
    throw error;
  }
}


/**
 * Get vectorization statistics
 *
 * @method GET
 * @path /cfg/knowbase/system/archives/vectorization_stats/
 */
export async function getKnowbaseSystemArchivesVectorizationStatsRetrieve(  client?: any
): Promise<VectorizationStatistics> {
  const api = client || getAPIInstance()
  const response = await api.cfg_knowbase.systemArchivesVectorizationStatsRetrieve()
  try {
    return VectorizationStatisticsSchema.parse(response)
  } catch (error) {
    // Zod validation error - log detailed information
    consola.error('❌ Zod Validation Failed');
    consola.box({
      title: 'getKnowbaseSystemArchivesVectorizationStatsRetrieve',
      message: `Path: /cfg/knowbase/system/archives/vectorization_stats/\nMethod: GET`,
      style: {
        borderColor: 'red',
        borderStyle: 'rounded'
      }
    });

    if (error instanceof Error && 'issues' in error && Array.isArray((error as any).issues)) {
      consola.error('Validation Issues:');
      (error as any).issues.forEach((issue: any, index: number) => {
        consola.error(`  ${index + 1}. ${issue.path.join('.') || 'root'}`);
        consola.error(`     ├─ Message: ${issue.message}`);
        if (issue.expected) consola.error(`     ├─ Expected: ${issue.expected}`);
        if (issue.received) consola.error(`     └─ Received: ${issue.received}`);
      });
    }

    consola.error('Response data:', response);

    // Re-throw the error
    throw error;
  }
}


/**
 * API operation
 *
 * @method GET
 * @path /cfg/knowbase/system/chunks/
 */
export async function getKnowbaseSystemChunksList(  params?: { page?: number; page_size?: number },  client?: any
): Promise<PaginatedArchiveItemChunkList> {
  const api = client || getAPIInstance()
  const response = await api.cfg_knowbase.systemChunksList(params?.page, params?.page_size)
  try {
    return PaginatedArchiveItemChunkListSchema.parse(response)
  } catch (error) {
    // Zod validation error - log detailed information
    consola.error('❌ Zod Validation Failed');
    consola.box({
      title: 'getKnowbaseSystemChunksList',
      message: `Path: /cfg/knowbase/system/chunks/\nMethod: GET`,
      style: {
        borderColor: 'red',
        borderStyle: 'rounded'
      }
    });

    if (error instanceof Error && 'issues' in error && Array.isArray((error as any).issues)) {
      consola.error('Validation Issues:');
      (error as any).issues.forEach((issue: any, index: number) => {
        consola.error(`  ${index + 1}. ${issue.path.join('.') || 'root'}`);
        consola.error(`     ├─ Message: ${issue.message}`);
        if (issue.expected) consola.error(`     ├─ Expected: ${issue.expected}`);
        if (issue.received) consola.error(`     └─ Received: ${issue.received}`);
      });
    }

    consola.error('Response data:', response);

    // Re-throw the error
    throw error;
  }
}


/**
 * API operation
 *
 * @method POST
 * @path /cfg/knowbase/system/chunks/
 */
export async function createKnowbaseSystemChunksCreate(  data: ArchiveItemChunkRequest,  client?: any
): Promise<ArchiveItemChunk> {
  const api = client || getAPIInstance()
  const response = await api.cfg_knowbase.systemChunksCreate(data)
  try {
    return ArchiveItemChunkSchema.parse(response)
  } catch (error) {
    // Zod validation error - log detailed information
    consola.error('❌ Zod Validation Failed');
    consola.box({
      title: 'createKnowbaseSystemChunksCreate',
      message: `Path: /cfg/knowbase/system/chunks/\nMethod: POST`,
      style: {
        borderColor: 'red',
        borderStyle: 'rounded'
      }
    });

    if (error instanceof Error && 'issues' in error && Array.isArray((error as any).issues)) {
      consola.error('Validation Issues:');
      (error as any).issues.forEach((issue: any, index: number) => {
        consola.error(`  ${index + 1}. ${issue.path.join('.') || 'root'}`);
        consola.error(`     ├─ Message: ${issue.message}`);
        if (issue.expected) consola.error(`     ├─ Expected: ${issue.expected}`);
        if (issue.received) consola.error(`     └─ Received: ${issue.received}`);
      });
    }

    consola.error('Response data:', response);

    // Re-throw the error
    throw error;
  }
}


/**
 * API operation
 *
 * @method GET
 * @path /cfg/knowbase/system/chunks/{id}/
 */
export async function getKnowbaseSystemChunksRetrieve(  id: string,  client?: any
): Promise<ArchiveItemChunkDetail> {
  const api = client || getAPIInstance()
  const response = await api.cfg_knowbase.systemChunksRetrieve(id)
  try {
    return ArchiveItemChunkDetailSchema.parse(response)
  } catch (error) {
    // Zod validation error - log detailed information
    consola.error('❌ Zod Validation Failed');
    consola.box({
      title: 'getKnowbaseSystemChunksRetrieve',
      message: `Path: /cfg/knowbase/system/chunks/{id}/\nMethod: GET`,
      style: {
        borderColor: 'red',
        borderStyle: 'rounded'
      }
    });

    if (error instanceof Error && 'issues' in error && Array.isArray((error as any).issues)) {
      consola.error('Validation Issues:');
      (error as any).issues.forEach((issue: any, index: number) => {
        consola.error(`  ${index + 1}. ${issue.path.join('.') || 'root'}`);
        consola.error(`     ├─ Message: ${issue.message}`);
        if (issue.expected) consola.error(`     ├─ Expected: ${issue.expected}`);
        if (issue.received) consola.error(`     └─ Received: ${issue.received}`);
      });
    }

    consola.error('Response data:', response);

    // Re-throw the error
    throw error;
  }
}


/**
 * API operation
 *
 * @method PUT
 * @path /cfg/knowbase/system/chunks/{id}/
 */
export async function updateKnowbaseSystemChunksUpdate(  id: string, data: ArchiveItemChunkRequest,  client?: any
): Promise<ArchiveItemChunk> {
  const api = client || getAPIInstance()
  const response = await api.cfg_knowbase.systemChunksUpdate(id, data)
  try {
    return ArchiveItemChunkSchema.parse(response)
  } catch (error) {
    // Zod validation error - log detailed information
    consola.error('❌ Zod Validation Failed');
    consola.box({
      title: 'updateKnowbaseSystemChunksUpdate',
      message: `Path: /cfg/knowbase/system/chunks/{id}/\nMethod: PUT`,
      style: {
        borderColor: 'red',
        borderStyle: 'rounded'
      }
    });

    if (error instanceof Error && 'issues' in error && Array.isArray((error as any).issues)) {
      consola.error('Validation Issues:');
      (error as any).issues.forEach((issue: any, index: number) => {
        consola.error(`  ${index + 1}. ${issue.path.join('.') || 'root'}`);
        consola.error(`     ├─ Message: ${issue.message}`);
        if (issue.expected) consola.error(`     ├─ Expected: ${issue.expected}`);
        if (issue.received) consola.error(`     └─ Received: ${issue.received}`);
      });
    }

    consola.error('Response data:', response);

    // Re-throw the error
    throw error;
  }
}


/**
 * API operation
 *
 * @method PATCH
 * @path /cfg/knowbase/system/chunks/{id}/
 */
export async function partialUpdateKnowbaseSystemChunksPartialUpdate(  id: string, data?: PatchedArchiveItemChunkRequest,  client?: any
): Promise<ArchiveItemChunk> {
  const api = client || getAPIInstance()
  const response = await api.cfg_knowbase.systemChunksPartialUpdate(id, data)
  try {
    return ArchiveItemChunkSchema.parse(response)
  } catch (error) {
    // Zod validation error - log detailed information
    consola.error('❌ Zod Validation Failed');
    consola.box({
      title: 'partialUpdateKnowbaseSystemChunksPartialUpdate',
      message: `Path: /cfg/knowbase/system/chunks/{id}/\nMethod: PATCH`,
      style: {
        borderColor: 'red',
        borderStyle: 'rounded'
      }
    });

    if (error instanceof Error && 'issues' in error && Array.isArray((error as any).issues)) {
      consola.error('Validation Issues:');
      (error as any).issues.forEach((issue: any, index: number) => {
        consola.error(`  ${index + 1}. ${issue.path.join('.') || 'root'}`);
        consola.error(`     ├─ Message: ${issue.message}`);
        if (issue.expected) consola.error(`     ├─ Expected: ${issue.expected}`);
        if (issue.received) consola.error(`     └─ Received: ${issue.received}`);
      });
    }

    consola.error('Response data:', response);

    // Re-throw the error
    throw error;
  }
}


/**
 * API operation
 *
 * @method DELETE
 * @path /cfg/knowbase/system/chunks/{id}/
 */
export async function deleteKnowbaseSystemChunksDestroy(  id: string,  client?: any
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
export async function getKnowbaseSystemChunksContextRetrieve(  id: string,  client?: any
): Promise<ArchiveItemChunkDetail> {
  const api = client || getAPIInstance()
  const response = await api.cfg_knowbase.systemChunksContextRetrieve(id)
  try {
    return ArchiveItemChunkDetailSchema.parse(response)
  } catch (error) {
    // Zod validation error - log detailed information
    consola.error('❌ Zod Validation Failed');
    consola.box({
      title: 'getKnowbaseSystemChunksContextRetrieve',
      message: `Path: /cfg/knowbase/system/chunks/{id}/context/\nMethod: GET`,
      style: {
        borderColor: 'red',
        borderStyle: 'rounded'
      }
    });

    if (error instanceof Error && 'issues' in error && Array.isArray((error as any).issues)) {
      consola.error('Validation Issues:');
      (error as any).issues.forEach((issue: any, index: number) => {
        consola.error(`  ${index + 1}. ${issue.path.join('.') || 'root'}`);
        consola.error(`     ├─ Message: ${issue.message}`);
        if (issue.expected) consola.error(`     ├─ Expected: ${issue.expected}`);
        if (issue.received) consola.error(`     └─ Received: ${issue.received}`);
      });
    }

    consola.error('Response data:', response);

    // Re-throw the error
    throw error;
  }
}


/**
 * Vectorize chunk
 *
 * @method POST
 * @path /cfg/knowbase/system/chunks/{id}/vectorize/
 */
export async function createKnowbaseSystemChunksVectorizeCreate(  id: string, data: ArchiveItemChunkRequest,  client?: any
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
export async function getKnowbaseSystemItemsList(  params?: { page?: number; page_size?: number },  client?: any
): Promise<PaginatedArchiveItemList> {
  const api = client || getAPIInstance()
  const response = await api.cfg_knowbase.systemItemsList(params?.page, params?.page_size)
  try {
    return PaginatedArchiveItemListSchema.parse(response)
  } catch (error) {
    // Zod validation error - log detailed information
    consola.error('❌ Zod Validation Failed');
    consola.box({
      title: 'getKnowbaseSystemItemsList',
      message: `Path: /cfg/knowbase/system/items/\nMethod: GET`,
      style: {
        borderColor: 'red',
        borderStyle: 'rounded'
      }
    });

    if (error instanceof Error && 'issues' in error && Array.isArray((error as any).issues)) {
      consola.error('Validation Issues:');
      (error as any).issues.forEach((issue: any, index: number) => {
        consola.error(`  ${index + 1}. ${issue.path.join('.') || 'root'}`);
        consola.error(`     ├─ Message: ${issue.message}`);
        if (issue.expected) consola.error(`     ├─ Expected: ${issue.expected}`);
        if (issue.received) consola.error(`     └─ Received: ${issue.received}`);
      });
    }

    consola.error('Response data:', response);

    // Re-throw the error
    throw error;
  }
}


/**
 * API operation
 *
 * @method POST
 * @path /cfg/knowbase/system/items/
 */
export async function createKnowbaseSystemItemsCreate(  data: ArchiveItemRequest,  client?: any
): Promise<ArchiveItem> {
  const api = client || getAPIInstance()
  const response = await api.cfg_knowbase.systemItemsCreate(data)
  try {
    return ArchiveItemSchema.parse(response)
  } catch (error) {
    // Zod validation error - log detailed information
    consola.error('❌ Zod Validation Failed');
    consola.box({
      title: 'createKnowbaseSystemItemsCreate',
      message: `Path: /cfg/knowbase/system/items/\nMethod: POST`,
      style: {
        borderColor: 'red',
        borderStyle: 'rounded'
      }
    });

    if (error instanceof Error && 'issues' in error && Array.isArray((error as any).issues)) {
      consola.error('Validation Issues:');
      (error as any).issues.forEach((issue: any, index: number) => {
        consola.error(`  ${index + 1}. ${issue.path.join('.') || 'root'}`);
        consola.error(`     ├─ Message: ${issue.message}`);
        if (issue.expected) consola.error(`     ├─ Expected: ${issue.expected}`);
        if (issue.received) consola.error(`     └─ Received: ${issue.received}`);
      });
    }

    consola.error('Response data:', response);

    // Re-throw the error
    throw error;
  }
}


/**
 * API operation
 *
 * @method GET
 * @path /cfg/knowbase/system/items/{id}/
 */
export async function getKnowbaseSystemItemsRetrieve(  id: string,  client?: any
): Promise<ArchiveItemDetail> {
  const api = client || getAPIInstance()
  const response = await api.cfg_knowbase.systemItemsRetrieve(id)
  try {
    return ArchiveItemDetailSchema.parse(response)
  } catch (error) {
    // Zod validation error - log detailed information
    consola.error('❌ Zod Validation Failed');
    consola.box({
      title: 'getKnowbaseSystemItemsRetrieve',
      message: `Path: /cfg/knowbase/system/items/{id}/\nMethod: GET`,
      style: {
        borderColor: 'red',
        borderStyle: 'rounded'
      }
    });

    if (error instanceof Error && 'issues' in error && Array.isArray((error as any).issues)) {
      consola.error('Validation Issues:');
      (error as any).issues.forEach((issue: any, index: number) => {
        consola.error(`  ${index + 1}. ${issue.path.join('.') || 'root'}`);
        consola.error(`     ├─ Message: ${issue.message}`);
        if (issue.expected) consola.error(`     ├─ Expected: ${issue.expected}`);
        if (issue.received) consola.error(`     └─ Received: ${issue.received}`);
      });
    }

    consola.error('Response data:', response);

    // Re-throw the error
    throw error;
  }
}


/**
 * API operation
 *
 * @method PUT
 * @path /cfg/knowbase/system/items/{id}/
 */
export async function updateKnowbaseSystemItemsUpdate(  id: string, data: ArchiveItemRequest,  client?: any
): Promise<ArchiveItem> {
  const api = client || getAPIInstance()
  const response = await api.cfg_knowbase.systemItemsUpdate(id, data)
  try {
    return ArchiveItemSchema.parse(response)
  } catch (error) {
    // Zod validation error - log detailed information
    consola.error('❌ Zod Validation Failed');
    consola.box({
      title: 'updateKnowbaseSystemItemsUpdate',
      message: `Path: /cfg/knowbase/system/items/{id}/\nMethod: PUT`,
      style: {
        borderColor: 'red',
        borderStyle: 'rounded'
      }
    });

    if (error instanceof Error && 'issues' in error && Array.isArray((error as any).issues)) {
      consola.error('Validation Issues:');
      (error as any).issues.forEach((issue: any, index: number) => {
        consola.error(`  ${index + 1}. ${issue.path.join('.') || 'root'}`);
        consola.error(`     ├─ Message: ${issue.message}`);
        if (issue.expected) consola.error(`     ├─ Expected: ${issue.expected}`);
        if (issue.received) consola.error(`     └─ Received: ${issue.received}`);
      });
    }

    consola.error('Response data:', response);

    // Re-throw the error
    throw error;
  }
}


/**
 * API operation
 *
 * @method PATCH
 * @path /cfg/knowbase/system/items/{id}/
 */
export async function partialUpdateKnowbaseSystemItemsPartialUpdate(  id: string, data?: PatchedArchiveItemRequest,  client?: any
): Promise<ArchiveItem> {
  const api = client || getAPIInstance()
  const response = await api.cfg_knowbase.systemItemsPartialUpdate(id, data)
  try {
    return ArchiveItemSchema.parse(response)
  } catch (error) {
    // Zod validation error - log detailed information
    consola.error('❌ Zod Validation Failed');
    consola.box({
      title: 'partialUpdateKnowbaseSystemItemsPartialUpdate',
      message: `Path: /cfg/knowbase/system/items/{id}/\nMethod: PATCH`,
      style: {
        borderColor: 'red',
        borderStyle: 'rounded'
      }
    });

    if (error instanceof Error && 'issues' in error && Array.isArray((error as any).issues)) {
      consola.error('Validation Issues:');
      (error as any).issues.forEach((issue: any, index: number) => {
        consola.error(`  ${index + 1}. ${issue.path.join('.') || 'root'}`);
        consola.error(`     ├─ Message: ${issue.message}`);
        if (issue.expected) consola.error(`     ├─ Expected: ${issue.expected}`);
        if (issue.received) consola.error(`     └─ Received: ${issue.received}`);
      });
    }

    consola.error('Response data:', response);

    // Re-throw the error
    throw error;
  }
}


/**
 * API operation
 *
 * @method DELETE
 * @path /cfg/knowbase/system/items/{id}/
 */
export async function deleteKnowbaseSystemItemsDestroy(  id: string,  client?: any
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
export async function getKnowbaseSystemItemsChunksList(  id: string, params?: { page?: number; page_size?: number },  client?: any
): Promise<PaginatedArchiveItemChunkList> {
  const api = client || getAPIInstance()
  const response = await api.cfg_knowbase.systemItemsChunksList(id, params?.page, params?.page_size)
  try {
    return PaginatedArchiveItemChunkListSchema.parse(response)
  } catch (error) {
    // Zod validation error - log detailed information
    consola.error('❌ Zod Validation Failed');
    consola.box({
      title: 'getKnowbaseSystemItemsChunksList',
      message: `Path: /cfg/knowbase/system/items/{id}/chunks/\nMethod: GET`,
      style: {
        borderColor: 'red',
        borderStyle: 'rounded'
      }
    });

    if (error instanceof Error && 'issues' in error && Array.isArray((error as any).issues)) {
      consola.error('Validation Issues:');
      (error as any).issues.forEach((issue: any, index: number) => {
        consola.error(`  ${index + 1}. ${issue.path.join('.') || 'root'}`);
        consola.error(`     ├─ Message: ${issue.message}`);
        if (issue.expected) consola.error(`     ├─ Expected: ${issue.expected}`);
        if (issue.received) consola.error(`     └─ Received: ${issue.received}`);
      });
    }

    consola.error('Response data:', response);

    // Re-throw the error
    throw error;
  }
}


/**
 * Get item content
 *
 * @method GET
 * @path /cfg/knowbase/system/items/{id}/content/
 */
export async function getKnowbaseSystemItemsContentRetrieve(  id: string,  client?: any
): Promise<ArchiveItemDetail> {
  const api = client || getAPIInstance()
  const response = await api.cfg_knowbase.systemItemsContentRetrieve(id)
  try {
    return ArchiveItemDetailSchema.parse(response)
  } catch (error) {
    // Zod validation error - log detailed information
    consola.error('❌ Zod Validation Failed');
    consola.box({
      title: 'getKnowbaseSystemItemsContentRetrieve',
      message: `Path: /cfg/knowbase/system/items/{id}/content/\nMethod: GET`,
      style: {
        borderColor: 'red',
        borderStyle: 'rounded'
      }
    });

    if (error instanceof Error && 'issues' in error && Array.isArray((error as any).issues)) {
      consola.error('Validation Issues:');
      (error as any).issues.forEach((issue: any, index: number) => {
        consola.error(`  ${index + 1}. ${issue.path.join('.') || 'root'}`);
        consola.error(`     ├─ Message: ${issue.message}`);
        if (issue.expected) consola.error(`     ├─ Expected: ${issue.expected}`);
        if (issue.received) consola.error(`     └─ Received: ${issue.received}`);
      });
    }

    consola.error('Response data:', response);

    // Re-throw the error
    throw error;
  }
}


