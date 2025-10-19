/**
 * Knowbase Sessions Context
 * Context for managing chat sessions
 */

'use client';

import React, { createContext, useContext, type ReactNode } from 'react';
import { api } from '../../BaseClient';
import {
  useKnowbaseAdminSessionsList,
  useKnowbaseAdminSessionsRetrieve,
  useCreateKnowbaseAdminSessionsCreate,
  useUpdateKnowbaseAdminSessionsUpdate,
  usePartialUpdateKnowbaseAdminSessionsPartialUpdate,
  useDeleteKnowbaseAdminSessionsDestroy,
  useCreateKnowbaseAdminSessionsActivateCreate,
  useCreateKnowbaseAdminSessionsArchiveCreate,
} from '../../generated/_utils/hooks/cfg__knowbase';
import type { API } from '../../generated';
import type {
  PaginatedChatSessionList,
  ChatSession,
  ChatSessionCreateRequest,
  ChatSessionRequest,
  PatchedChatSessionRequest,
} from '../../generated/cfg__knowbase/models';

// ─────────────────────────────────────────────────────────────────────────
// Context Type
// ─────────────────────────────────────────────────────────────────────────

export interface KnowbaseSessionsContextValue {
  // Sessions list
  sessions: PaginatedChatSessionList | undefined;
  isLoadingSessions: boolean;
  sessionsError: Error | undefined;
  refreshSessions: () => Promise<void>;

  // Session operations
  getSession: (id: string) => Promise<ChatSession | undefined>;
  createSession: (data: ChatSessionCreateRequest) => Promise<ChatSession>;
  updateSession: (id: string, data: ChatSessionRequest) => Promise<ChatSession>;
  partialUpdateSession: (id: string, data: PatchedChatSessionRequest) => Promise<ChatSession>;
  deleteSession: (id: string) => Promise<void>;

  // Session actions
  activateSession: (id: string, data: ChatSessionRequest) => Promise<ChatSession>;
  archiveSession: (id: string, data: ChatSessionRequest) => Promise<ChatSession>;
}

// ─────────────────────────────────────────────────────────────────────────
// Context
// ─────────────────────────────────────────────────────────────────────────

const KnowbaseSessionsContext = createContext<KnowbaseSessionsContextValue | undefined>(undefined);

// ─────────────────────────────────────────────────────────────────────────
// Provider
// ─────────────────────────────────────────────────────────────────────────

export function KnowbaseSessionsProvider({ children }: { children: ReactNode }) {
  // List sessions
  const {
    data: sessions,
    error: sessionsError,
    isLoading: isLoadingSessions,
    mutate: mutateSessions,
  } = useKnowbaseAdminSessionsList({}, api as unknown as API);

  const refreshSessions = async () => {
    await mutateSessions();
  };

  // Mutations
  const createSessionMutation = useCreateKnowbaseAdminSessionsCreate();
  const updateSessionMutation = useUpdateKnowbaseAdminSessionsUpdate();
  const partialUpdateSessionMutation = usePartialUpdateKnowbaseAdminSessionsPartialUpdate();
  const deleteSessionMutation = useDeleteKnowbaseAdminSessionsDestroy();
  const activateSessionMutation = useCreateKnowbaseAdminSessionsActivateCreate();
  const archiveSessionMutation = useCreateKnowbaseAdminSessionsArchiveCreate();

  // Get single session
  const getSession = async (id: string): Promise<ChatSession | undefined> => {
    const { data } = useKnowbaseAdminSessionsRetrieve(id, api as unknown as API);
    return data;
  };

  // Create session
  const createSession = async (data: ChatSessionCreateRequest): Promise<ChatSession> => {
    const result = await createSessionMutation(data, api as unknown as API);
    await refreshSessions();
    return result as ChatSession;
  };

  // Update session
  const updateSession = async (id: string, data: ChatSessionRequest): Promise<ChatSession> => {
    const result = await updateSessionMutation(id, data, api as unknown as API);
    await refreshSessions();
    return result as ChatSession;
  };

  // Partial update session
  const partialUpdateSession = async (
    id: string,
    data: PatchedChatSessionRequest
  ): Promise<ChatSession> => {
    const result = await partialUpdateSessionMutation(id, data, api as unknown as API);
    await refreshSessions();
    return result as ChatSession;
  };

  // Delete session
  const deleteSession = async (id: string): Promise<void> => {
    await deleteSessionMutation(id, api as unknown as API);
    await refreshSessions();
  };

  // Activate session
  const activateSession = async (id: string, data: ChatSessionRequest): Promise<ChatSession> => {
    const result = await activateSessionMutation(id, data, api as unknown as API);
    await refreshSessions();
    return result as ChatSession;
  };

  // Archive session
  const archiveSession = async (id: string, data: ChatSessionRequest): Promise<ChatSession> => {
    const result = await archiveSessionMutation(id, data, api as unknown as API);
    await refreshSessions();
    return result as ChatSession;
  };

  const value: KnowbaseSessionsContextValue = {
    sessions,
    isLoadingSessions,
    sessionsError,
    refreshSessions,
    getSession,
    createSession,
    updateSession,
    partialUpdateSession,
    deleteSession,
    activateSession,
    archiveSession,
  };

  return (
    <KnowbaseSessionsContext.Provider value={value}>{children}</KnowbaseSessionsContext.Provider>
  );
}

// ─────────────────────────────────────────────────────────────────────────
// Hook
// ─────────────────────────────────────────────────────────────────────────

export function useKnowbaseSessionsContext(): KnowbaseSessionsContextValue {
  const context = useContext(KnowbaseSessionsContext);
  if (!context) {
    throw new Error('useKnowbaseSessionsContext must be used within KnowbaseSessionsProvider');
  }
  return context;
}

// ─────────────────────────────────────────────────────────────────────────
// Re-export types for external use
// ─────────────────────────────────────────────────────────────────────────

export type {
  ChatSession,
  ChatSessionCreateRequest,
  ChatSessionRequest,
  PatchedChatSessionRequest,
} from '../../generated/cfg__knowbase/models';

