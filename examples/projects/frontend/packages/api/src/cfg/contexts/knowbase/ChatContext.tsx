/**
 * Knowbase Chat Context
 * Context for RAG-powered chat functionality
 */

'use client';

import React, { createContext, useContext, type ReactNode } from 'react';
import { api } from '../../BaseClient';
import {
  useKnowbaseAdminChatList,
  useKnowbaseAdminChatRetrieve,
  useCreateKnowbaseAdminChatCreate,
  useUpdateKnowbaseAdminChatUpdate,
  usePartialUpdateKnowbaseAdminChatPartialUpdate,
  useDeleteKnowbaseAdminChatDestroy,
  useKnowbaseAdminChatHistoryRetrieve,
  useCreateKnowbaseAdminChatQueryCreate,
} from '../../generated/_utils/hooks/cfg__knowbase';
import type { API } from '../../generated';
import type {
  PaginatedChatResponseList,
  ChatResponse,
  ChatResponseRequest,
  PatchedChatResponseRequest,
  ChatHistory,
  ChatQueryRequest,
} from '../../generated/cfg__knowbase/models';

// ─────────────────────────────────────────────────────────────────────────
// Context Type
// ─────────────────────────────────────────────────────────────────────────

export interface KnowbaseChatContextValue {
  // Chat list
  chats: PaginatedChatResponseList | undefined;
  isLoadingChats: boolean;
  chatsError: Error | undefined;
  refreshChats: () => Promise<void>;

  // Chat operations
  getChat: (id: string) => Promise<ChatResponse | undefined>;
  getChatHistory: (id: string) => Promise<ChatHistory | undefined>;
  createChat: (data: ChatResponseRequest) => Promise<ChatResponse>;
  updateChat: (id: string, data: ChatResponseRequest) => Promise<ChatResponse>;
  partialUpdateChat: (id: string, data: PatchedChatResponseRequest) => Promise<ChatResponse>;
  deleteChat: (id: string) => Promise<void>;

  // RAG Query
  sendQuery: (data: ChatQueryRequest) => Promise<ChatResponse>;
}

// ─────────────────────────────────────────────────────────────────────────
// Context
// ─────────────────────────────────────────────────────────────────────────

const KnowbaseChatContext = createContext<KnowbaseChatContextValue | undefined>(undefined);

// ─────────────────────────────────────────────────────────────────────────
// Provider
// ─────────────────────────────────────────────────────────────────────────

export function KnowbaseChatProvider({ children }: { children: ReactNode }) {
  // List chats
  const {
    data: chats,
    error: chatsError,
    isLoading: isLoadingChats,
    mutate: mutateChats,
  } = useKnowbaseAdminChatList({}, api as unknown as API);

  const refreshChats = async () => {
    await mutateChats();
  };

  // Mutations
  const createChatMutation = useCreateKnowbaseAdminChatCreate();
  const updateChatMutation = useUpdateKnowbaseAdminChatUpdate();
  const partialUpdateChatMutation = usePartialUpdateKnowbaseAdminChatPartialUpdate();
  const deleteChatMutation = useDeleteKnowbaseAdminChatDestroy();
  const sendQueryMutation = useCreateKnowbaseAdminChatQueryCreate();

  // Get single chat
  const getChat = async (id: string): Promise<ChatResponse | undefined> => {
    const { data } = useKnowbaseAdminChatRetrieve(id, api as unknown as API);
    return data;
  };

  // Get chat history
  const getChatHistory = async (id: string): Promise<ChatHistory | undefined> => {
    const { data } = useKnowbaseAdminChatHistoryRetrieve(id, api as unknown as API);
    return data;
  };

  // Create chat
  const createChat = async (data: ChatResponseRequest): Promise<ChatResponse> => {
    const result = await createChatMutation(data, api as unknown as API);
    await refreshChats();
    return result as ChatResponse;
  };

  // Update chat
  const updateChat = async (id: string, data: ChatResponseRequest): Promise<ChatResponse> => {
    const result = await updateChatMutation(id, data, api as unknown as API);
    await refreshChats();
    return result as ChatResponse;
  };

  // Partial update chat
  const partialUpdateChat = async (
    id: string,
    data: PatchedChatResponseRequest
  ): Promise<ChatResponse> => {
    const result = await partialUpdateChatMutation(id, data, api as unknown as API);
    await refreshChats();
    return result as ChatResponse;
  };

  // Delete chat
  const deleteChat = async (id: string): Promise<void> => {
    await deleteChatMutation(id, api as unknown as API);
    await refreshChats();
  };

  // Send RAG query
  const sendQuery = async (data: ChatQueryRequest): Promise<ChatResponse> => {
    const result = await sendQueryMutation(data, api as unknown as API);
    await refreshChats();
    return result as ChatResponse;
  };

  const value: KnowbaseChatContextValue = {
    chats,
    isLoadingChats,
    chatsError,
    refreshChats,
    getChat,
    getChatHistory,
    createChat,
    updateChat,
    partialUpdateChat,
    deleteChat,
    sendQuery,
  };

  return <KnowbaseChatContext.Provider value={value}>{children}</KnowbaseChatContext.Provider>;
}

// ─────────────────────────────────────────────────────────────────────────
// Hook
// ─────────────────────────────────────────────────────────────────────────

export function useKnowbaseChatContext(): KnowbaseChatContextValue {
  const context = useContext(KnowbaseChatContext);
  if (!context) {
    throw new Error('useKnowbaseChatContext must be used within KnowbaseChatProvider');
  }
  return context;
}

// ─────────────────────────────────────────────────────────────────────────
// Re-export types for external use
// ─────────────────────────────────────────────────────────────────────────

export type {
  ChatResponse,
  ChatResponseRequest,
  PatchedChatResponseRequest,
  ChatHistory,
  ChatQueryRequest,
  ChatMessage,
  ChatSource,
} from '../../generated/cfg__knowbase/models';

