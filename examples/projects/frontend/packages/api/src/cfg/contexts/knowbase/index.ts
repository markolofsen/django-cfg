/**
 * Knowbase Contexts
 * 
 * Contexts for knowledge base functionality:
 * - ChatContext: RAG-powered chat
 * - DocumentsContext: Documents and archives management
 * - SessionsContext: Chat sessions management
 */

// Chat Context
export {
  KnowbaseChatProvider,
  useKnowbaseChatContext,
} from './ChatContext';
export type {
  KnowbaseChatContextValue,
  ChatResponse,
  ChatResponseRequest,
  PatchedChatResponseRequest,
  ChatHistory,
  ChatQueryRequest,
  ChatMessage,
  ChatSource,
} from './ChatContext';

// Documents Context
export {
  KnowbaseDocumentsProvider,
  useKnowbaseDocumentsContext,
} from './DocumentsContext';
export type {
  KnowbaseDocumentsContextValue,
  Document,
  DocumentCreateRequest,
  DocumentRequest,
  PatchedDocumentRequest,
  DocumentProcessingStatus,
  DocumentStats,
  DocumentArchive,
  DocumentArchiveDetail,
  PatchedDocumentArchiveRequest,
  ArchiveProcessingResult,
  ArchiveStatistics,
} from './DocumentsContext';

// Sessions Context
export {
  KnowbaseSessionsProvider,
  useKnowbaseSessionsContext,
} from './SessionsContext';
export type {
  KnowbaseSessionsContextValue,
  ChatSession,
  ChatSessionCreateRequest,
  ChatSessionRequest,
  PatchedChatSessionRequest,
} from './SessionsContext';

