'use client';

/**
 * SWR Hooks for Terminal
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
import * as Fetchers from '../fetchers/terminal__api__terminal'
import type { API } from '../../index'
import type { CommandHistoryDetail } from '../schemas/CommandHistoryDetail.schema'
import type { PaginatedCommandHistoryListList } from '../schemas/PaginatedCommandHistoryListList.schema'
import type { PaginatedTerminalSessionListList } from '../schemas/PaginatedTerminalSessionListList.schema'
import type { TerminalInputRequest } from '../schemas/TerminalInputRequest.schema'
import type { TerminalResizeRequest } from '../schemas/TerminalResizeRequest.schema'
import type { TerminalSessionCreate } from '../schemas/TerminalSessionCreate.schema'
import type { TerminalSessionCreateRequest } from '../schemas/TerminalSessionCreateRequest.schema'
import type { TerminalSessionDetail } from '../schemas/TerminalSessionDetail.schema'
import type { TerminalSignalRequest } from '../schemas/TerminalSignalRequest.schema'

/**
 * List command history
 *
 * @method GET
 * @path /api/terminal/commands/
 */
export function useTerminalCommandsList(params?: { page?: number; page_size?: number; search?: string; session?: string; status?: string }, client?: API): ReturnType<typeof useSWR<PaginatedCommandHistoryListList>> {
  return useSWR<PaginatedCommandHistoryListList>(
    params ? ['terminal-commands', params] : 'terminal-commands',
    () => Fetchers.getTerminalCommandsList(params, client)
  )
}


/**
 * Get command details
 *
 * @method GET
 * @path /api/terminal/commands/{id}/
 */
export function useTerminalCommandsRetrieve(id: string, client?: API): ReturnType<typeof useSWR<CommandHistoryDetail>> {
  return useSWR<CommandHistoryDetail>(
    ['terminal-command', id],
    () => Fetchers.getTerminalCommandsRetrieve(id, client)
  )
}


/**
 * List user's terminal sessions
 *
 * @method GET
 * @path /api/terminal/sessions/
 */
export function useTerminalSessionsList(params?: { page?: number; page_size?: number }, client?: API): ReturnType<typeof useSWR<PaginatedTerminalSessionListList>> {
  return useSWR<PaginatedTerminalSessionListList>(
    params ? ['terminal-sessions', params] : 'terminal-sessions',
    () => Fetchers.getTerminalSessionsList(params, client)
  )
}


/**
 * Create new terminal session
 *
 * @method POST
 * @path /api/terminal/sessions/
 */
export function useCreateTerminalSessionsCreate() {
  const { mutate } = useSWRConfig()

  return async (data: TerminalSessionCreateRequest, client?: API): Promise<TerminalSessionCreate> => {
    const result = await Fetchers.createTerminalSessionsCreate(data, client)
    // Revalidate related queries
    mutate('terminal-sessions')
    return result
  }
}


/**
 * Get session details
 *
 * @method GET
 * @path /api/terminal/sessions/{id}/
 */
export function useTerminalSessionsRetrieve(id: string, client?: API): ReturnType<typeof useSWR<TerminalSessionDetail>> {
  return useSWR<TerminalSessionDetail>(
    ['terminal-session', id],
    () => Fetchers.getTerminalSessionsRetrieve(id, client)
  )
}


/**
 * Close terminal session
 *
 * @method DELETE
 * @path /api/terminal/sessions/{id}/
 */
export function useDeleteTerminalSessionsDestroy() {
  const { mutate } = useSWRConfig()

  return async (id: string, client?: API): Promise<void> => {
    const result = await Fetchers.deleteTerminalSessionsDestroy(id, client)
    // Revalidate related queries
    mutate('terminal-sessions')
    mutate('terminal-session')
    return result
  }
}


/**
 * Get command history for session
 *
 * @method GET
 * @path /api/terminal/sessions/{id}/history/
 */
export function useTerminalSessionsHistoryList(id: string, params?: { page?: number; page_size?: number }, client?: API): ReturnType<typeof useSWR<PaginatedCommandHistoryListList>> {
  return useSWR<PaginatedCommandHistoryListList>(
    ['terminal-sessions-history', id],
    () => Fetchers.getTerminalSessionsHistoryList(id, params, client)
  )
}


/**
 * Send input to terminal
 *
 * @method POST
 * @path /api/terminal/sessions/{id}/input/
 */
export function useCreateTerminalSessionsInputCreate() {
  const { mutate } = useSWRConfig()

  return async (id: string, data: TerminalInputRequest, client?: API): Promise<any> => {
    const result = await Fetchers.createTerminalSessionsInputCreate(id, data, client)
    // Revalidate related queries
    mutate('terminal-sessions-input')
    return result
  }
}


/**
 * Resize terminal
 *
 * @method POST
 * @path /api/terminal/sessions/{id}/resize/
 */
export function useCreateTerminalSessionsResizeCreate() {
  const { mutate } = useSWRConfig()

  return async (id: string, data: TerminalResizeRequest, client?: API): Promise<any> => {
    const result = await Fetchers.createTerminalSessionsResizeCreate(id, data, client)
    // Revalidate related queries
    mutate('terminal-sessions-resize')
    return result
  }
}


/**
 * Send signal to terminal
 *
 * @method POST
 * @path /api/terminal/sessions/{id}/signal/
 */
export function useCreateTerminalSessionsSignalCreate() {
  const { mutate } = useSWRConfig()

  return async (id: string, data: TerminalSignalRequest, client?: API): Promise<any> => {
    const result = await Fetchers.createTerminalSessionsSignalCreate(id, data, client)
    // Revalidate related queries
    mutate('terminal-sessions-signal')
    return result
  }
}


/**
 * Get active sessions only
 *
 * @method GET
 * @path /api/terminal/sessions/active/
 */
export function useTerminalSessionsActiveList(params?: { page?: number; page_size?: number }, client?: API): ReturnType<typeof useSWR<PaginatedTerminalSessionListList>> {
  return useSWR<PaginatedTerminalSessionListList>(
    params ? ['terminal-sessions-active', params] : 'terminal-sessions-active',
    () => Fetchers.getTerminalSessionsActiveList(params, client)
  )
}


