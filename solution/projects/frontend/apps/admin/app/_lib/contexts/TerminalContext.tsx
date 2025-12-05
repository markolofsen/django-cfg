/**
 * Terminal Context
 *
 * Provides terminal session management functionality.
 */

import React, { createContext, useContext, ReactNode } from 'react';
import { terminalClient } from '@/api/BaseClient';
import {
  useTerminalSessionsList,
  useTerminalSessionsActiveList,
  useTerminalCommandsList,
  useCreateTerminalSessionsCreate,
  useDeleteTerminalSessionsDestroy,
  useCreateTerminalSessionsInputCreate,
  useCreateTerminalSessionsResizeCreate,
  useCreateTerminalSessionsSignalCreate,
} from '../api/generated/terminal/_utils/hooks';
import type { API } from '../api/generated/terminal';
import type { TerminalSessionList } from '../api/generated/terminal/_utils/schemas/TerminalSessionList.schema';
import type { CommandHistoryList } from '../api/generated/terminal/_utils/schemas/CommandHistoryList.schema';
import type { TerminalSessionCreateRequest } from '../api/generated/terminal/_utils/schemas/TerminalSessionCreateRequest.schema';
import type { TerminalInputRequest } from '../api/generated/terminal/_utils/schemas/TerminalInputRequest.schema';
import type { TerminalResizeRequest } from '../api/generated/terminal/_utils/schemas/TerminalResizeRequest.schema';
import type { TerminalSignalRequest } from '../api/generated/terminal/_utils/schemas/TerminalSignalRequest.schema';

interface TerminalContextType {
  // Sessions data
  sessions: TerminalSessionList[];
  sessionsLoading: boolean;
  sessionsError: Error | null;

  // Active sessions
  activeSessions: TerminalSessionList[];
  activeSessionsLoading: boolean;

  // Commands history
  commands: CommandHistoryList[];
  commandsLoading: boolean;
  commandsError: Error | null;

  // Actions
  refreshSessions: () => Promise<void>;
  refreshActiveSessions: () => Promise<void>;
  refreshCommands: () => Promise<void>;
  createSession: (data: TerminalSessionCreateRequest) => Promise<void>;
  closeSession: (id: string) => Promise<void>;
  sendInput: (id: string, data: TerminalInputRequest) => Promise<void>;
  resizeTerminal: (id: string, data: TerminalResizeRequest) => Promise<void>;
  sendSignal: (id: string, data: TerminalSignalRequest) => Promise<void>;
}

const TerminalContext = createContext<TerminalContextType | undefined>(undefined);

export function TerminalProvider({ children }: { children: ReactNode }) {
  // Get sessions list (SWR)
  const {
    data: sessionsData,
    error: sessionsError,
    isLoading: sessionsLoading,
    mutate: mutateSessions
  } = useTerminalSessionsList({ page: 1, page_size: 100 }, terminalClient as unknown as API);

  // Get active sessions (SWR)
  const {
    data: activeSessionsData,
    isLoading: activeSessionsLoading,
    mutate: mutateActiveSessions
  } = useTerminalSessionsActiveList({ page: 1, page_size: 100 }, terminalClient as unknown as API);

  // Get commands list (SWR)
  const {
    data: commandsData,
    error: commandsError,
    isLoading: commandsLoading,
    mutate: mutateCommands
  } = useTerminalCommandsList({ page: 1, page_size: 100 }, terminalClient as unknown as API);

  // Mutation hooks
  const createSessionMutation = useCreateTerminalSessionsCreate();
  const deleteSessionMutation = useDeleteTerminalSessionsDestroy();
  const sendInputMutation = useCreateTerminalSessionsInputCreate();
  const resizeMutation = useCreateTerminalSessionsResizeCreate();
  const signalMutation = useCreateTerminalSessionsSignalCreate();

  const sessions = sessionsData?.results || [];
  const activeSessions = activeSessionsData?.results || [];
  const commands = commandsData?.results || [];

  const value: TerminalContextType = {
    sessions,
    sessionsLoading,
    sessionsError: sessionsError as Error | null,
    activeSessions,
    activeSessionsLoading,
    commands,
    commandsLoading,
    commandsError: commandsError as Error | null,
    refreshSessions: async () => {
      await mutateSessions();
    },
    refreshActiveSessions: async () => {
      await mutateActiveSessions();
    },
    refreshCommands: async () => {
      await mutateCommands();
    },
    createSession: async (data: TerminalSessionCreateRequest) => {
      await createSessionMutation(data, terminalClient as unknown as API);
      await mutateSessions();
      await mutateActiveSessions();
    },
    closeSession: async (id: string) => {
      await deleteSessionMutation(id, terminalClient as unknown as API);
      await mutateSessions();
      await mutateActiveSessions();
    },
    sendInput: async (id: string, data: TerminalInputRequest) => {
      await sendInputMutation(id, data, terminalClient as unknown as API);
    },
    resizeTerminal: async (id: string, data: TerminalResizeRequest) => {
      await resizeMutation(id, data, terminalClient as unknown as API);
    },
    sendSignal: async (id: string, data: TerminalSignalRequest) => {
      await signalMutation(id, data, terminalClient as unknown as API);
    },
  };

  return (
    <TerminalContext.Provider value={value}>
      {children}
    </TerminalContext.Provider>
  );
}

export function useTerminal() {
  const context = useContext(TerminalContext);
  if (context === undefined) {
    throw new Error('useTerminal must be used within a TerminalProvider');
  }
  return context;
}
