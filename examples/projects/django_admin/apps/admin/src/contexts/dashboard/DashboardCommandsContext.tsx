/**
 * Dashboard Commands Context
 *
 * Manages Django management commands data
 *
 * Features:
 * - List all available Django management commands
 * - Commands summary with statistics
 * - Commands categorization (Core/Custom/Third Party)
 * - Pagination support
 *
 * Usage:
 * ```tsx
 * import { DashboardCommandsProvider, useDashboardCommandsContext } from '@/contexts/dashboard';
 *
 * function App() {
 *   return (
 *     <DashboardCommandsProvider>
 *       <CommandsView />
 *     </DashboardCommandsProvider>
 *   );
 * }
 *
 * function CommandsView() {
 *   const { commands, summary, isLoadingCommands } = useDashboardCommandsContext();
 *
 *   return (
 *     <div>
 *       <CommandsSummary data={summary} />
 *       <CommandsList commands={commands?.results} />
 *     </div>
 *   );
 * }
 * ```
 */

'use client';

import React, { createContext, useContext, useState, type ReactNode } from 'react';
import { api } from '@/api/BaseClient';
import {
  useDashboardApiCommandsList,
  useDashboardApiCommandsSummaryRetrieve,
} from '@/api/generated/cfg/_utils/hooks/cfg__dashboard__dashboard_commands';

import type { CommandsSummary } from '@/api/generated/cfg/_utils/schemas/CommandsSummary.schema';
import type { Command } from '@/api/generated/cfg/_utils/schemas/Command.schema';
import type { CommandExecuteRequestRequest } from '@/api/generated/cfg/_utils/schemas/CommandExecuteRequestRequest.schema';
import type { CommandHelpResponse } from '@/api/generated/cfg/_utils/schemas/CommandHelpResponse.schema';

// ─────────────────────────────────────────────────────────────────────────
// Context Type
// ─────────────────────────────────────────────────────────────────────────

// Command execution event types
export type CommandExecutionEvent =
  | { type: 'start'; command: string; args: string[] }
  | { type: 'output'; line: string }
  | { type: 'complete'; return_code: number; execution_time: number }
  | { type: 'error'; error: string; execution_time?: number };

export type CommandExecutionCallback = (event: CommandExecutionEvent) => void;

export interface DashboardCommandsContextValue {
  // Commands list (simple array, no pagination)
  commands?: Command[];
  isLoadingCommands: boolean;
  commandsError: Error | undefined;
  refreshCommands: () => Promise<void>;

  // Commands summary
  summary?: CommandsSummary;
  isLoadingSummary: boolean;
  summaryError: Error | undefined;
  refreshSummary: () => Promise<void>;

  // Command execution (SSE streaming)
  executeCommand: (
    request: CommandExecuteRequestRequest,
    onEvent: CommandExecutionCallback
  ) => Promise<void>;

  // Get command help
  getCommandHelp: (commandName: string) => Promise<CommandHelpResponse>;

  // Refresh all
  refreshAll: () => Promise<void>;
}

// ─────────────────────────────────────────────────────────────────────────
// Context
// ─────────────────────────────────────────────────────────────────────────

const DashboardCommandsContext = createContext<DashboardCommandsContextValue | undefined>(undefined);

// ─────────────────────────────────────────────────────────────────────────
// Provider
// ─────────────────────────────────────────────────────────────────────────

export function DashboardCommandsProvider({ children }: { children: ReactNode }) {
  // Commands list (returns array directly, no pagination)
  const {
    data: commands,
    error: commandsError,
    isLoading: isLoadingCommands,
    mutate: mutateCommands,
  } = useDashboardApiCommandsList(api);

  // Commands summary
  const {
    data: summary,
    error: summaryError,
    isLoading: isLoadingSummary,
    mutate: mutateSummary,
  } = useDashboardApiCommandsSummaryRetrieve(api);

  // Refresh functions
  const refreshCommands = async () => {
    await mutateCommands();
  };

  const refreshSummary = async () => {
    await mutateSummary();
  };

  const refreshAll = async () => {
    await Promise.all([mutateCommands(), mutateSummary()]);
  };

  // Execute command with SSE streaming
  const executeCommand = async (
    request: CommandExecuteRequestRequest,
    onEvent: CommandExecutionCallback
  ) => {
    // Use fetch for SSE streaming
    const baseUrl = api.getBaseUrl() || '';
    const token = api.getToken();

    const response = await fetch(`${baseUrl}/cfg/dashboard/api/commands/execute/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...(token ? { 'Authorization': `Bearer ${token}` } : {}),
      },
      credentials: 'include',
      body: JSON.stringify(request),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    // Read SSE stream
    const reader = response.body?.getReader();
    const decoder = new TextDecoder();

    if (!reader) {
      throw new Error('Response body is null');
    }

    try {
      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value);
        const lines = chunk.split('\n');

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            try {
              const event = JSON.parse(line.slice(6));
              onEvent(event);
            } catch (e) {
              console.error('Error parsing SSE event:', e);
            }
          }
        }
      }
    } finally {
      reader.releaseLock();
    }
  };

  // Get command help
  const getCommandHelp = async (commandName: string): Promise<CommandHelpResponse> => {
    return await api.cfg_dashboard_commands.dashboardApiCommandsHelpRetrieve(commandName);
  };

  const value: DashboardCommandsContextValue = {
    commands,
    isLoadingCommands,
    commandsError,
    refreshCommands,

    summary,
    isLoadingSummary,
    summaryError,
    refreshSummary,

    executeCommand,
    getCommandHelp,

    refreshAll,
  };

  return (
    <DashboardCommandsContext.Provider value={value}>
      {children}
    </DashboardCommandsContext.Provider>
  );
}

// ─────────────────────────────────────────────────────────────────────────
// Hook
// ─────────────────────────────────────────────────────────────────────────

export function useDashboardCommandsContext(): DashboardCommandsContextValue {
  const context = useContext(DashboardCommandsContext);
  if (!context) {
    throw new Error('useDashboardCommandsContext must be used within DashboardCommandsProvider');
  }
  return context;
}

// ─────────────────────────────────────────────────────────────────────────
// Re-export types
// ─────────────────────────────────────────────────────────────────────────

export type {
  CommandsSummary,
  Command,
  CommandExecuteRequestRequest,
  CommandHelpResponse,
};
