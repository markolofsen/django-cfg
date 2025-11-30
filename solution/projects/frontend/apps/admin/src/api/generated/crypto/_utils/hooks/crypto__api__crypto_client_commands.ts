'use client';

/**
 * SWR Hooks for Crypto Client Commands
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
import * as Fetchers from '../fetchers/crypto__api__crypto_client_commands'
import type { API } from '../../index'
import type { ClientCommand } from '../schemas/ClientCommand.schema'

/**
 * List active crypto clients
 *
 * @method GET
 * @path /api/crypto/commands/
 */
export function useCryptoCommandsRetrieve(client?: API): ReturnType<typeof useSWR<any>> {
  return useSWR<any>(
    'crypto-command',
    () => Fetchers.getCryptoCommandsRetrieve(client)
  )
}


/**
 * Get crypto client details
 *
 * @method GET
 * @path /api/crypto/commands/{id}/
 */
export function useCryptoCommandsRetrieve2(id: string, client?: API): ReturnType<typeof useSWR<any>> {
  return useSWR<any>(
    ['crypto-commands-2', id],
    () => Fetchers.getCryptoCommandsRetrieve2(id, client)
  )
}


/**
 * Pause crypto client
 *
 * @method POST
 * @path /api/crypto/commands/{id}/pause/
 */
export function useCreateCryptoCommandsPauseCreate() {
  const { mutate } = useSWRConfig()

  return async (id: string, client?: API): Promise<ClientCommand> => {
    const result = await Fetchers.createCryptoCommandsPauseCreate(id, client)
    // Revalidate related queries
    mutate('crypto-commands-pause')
    return result
  }
}


/**
 * Ping crypto client
 *
 * @method POST
 * @path /api/crypto/commands/{id}/ping/
 */
export function useCreateCryptoCommandsPingCreate() {
  const { mutate } = useSWRConfig()

  return async (id: string, client?: API): Promise<any> => {
    const result = await Fetchers.createCryptoCommandsPingCreate(id, client)
    // Revalidate related queries
    mutate('crypto-commands-ping')
    return result
  }
}


/**
 * Request status from crypto client
 *
 * @method POST
 * @path /api/crypto/commands/{id}/request_status/
 */
export function useCreateCryptoCommandsRequestStatusCreate() {
  const { mutate } = useSWRConfig()

  return async (id: string, params?: { include_stats?: boolean }, client?: API): Promise<ClientCommand> => {
    const result = await Fetchers.createCryptoCommandsRequestStatusCreate(id, params, client)
    // Revalidate related queries
    mutate('crypto-commands-request-status')
    return result
  }
}


/**
 * Resume crypto client
 *
 * @method POST
 * @path /api/crypto/commands/{id}/resume/
 */
export function useCreateCryptoCommandsResumeCreate() {
  const { mutate } = useSWRConfig()

  return async (id: string, client?: API): Promise<ClientCommand> => {
    const result = await Fetchers.createCryptoCommandsResumeCreate(id, client)
    // Revalidate related queries
    mutate('crypto-commands-resume')
    return result
  }
}


/**
 * Sync wallets on crypto client
 *
 * @method POST
 * @path /api/crypto/commands/{id}/sync_wallets/
 */
export function useCreateCryptoCommandsSyncWalletsCreate() {
  const { mutate } = useSWRConfig()

  return async (id: string, params?: { symbols?: string }, client?: API): Promise<any> => {
    const result = await Fetchers.createCryptoCommandsSyncWalletsCreate(id, params, client)
    // Revalidate related queries
    mutate('crypto-commands-sync-wallets')
    return result
  }
}


/**
 * Pause all crypto clients
 *
 * @method POST
 * @path /api/crypto/commands/pause_all/
 */
export function useCreateCryptoCommandsPauseAllCreate() {
  const { mutate } = useSWRConfig()

  return async (client?: API): Promise<any> => {
    const result = await Fetchers.createCryptoCommandsPauseAllCreate(client)
    // Revalidate related queries
    mutate('crypto-commands-pause-all')
    return result
  }
}


/**
 * Resume all crypto clients
 *
 * @method POST
 * @path /api/crypto/commands/resume_all/
 */
export function useCreateCryptoCommandsResumeAllCreate() {
  const { mutate } = useSWRConfig()

  return async (client?: API): Promise<any> => {
    const result = await Fetchers.createCryptoCommandsResumeAllCreate(client)
    // Revalidate related queries
    mutate('crypto-commands-resume-all')
    return result
  }
}


/**
 * Sync wallets on all crypto clients
 *
 * @method POST
 * @path /api/crypto/commands/sync_all/
 */
export function useCreateCryptoCommandsSyncAllCreate() {
  const { mutate } = useSWRConfig()

  return async (params?: { symbols?: string }, client?: API): Promise<any> => {
    const result = await Fetchers.createCryptoCommandsSyncAllCreate(params, client)
    // Revalidate related queries
    mutate('crypto-commands-sync-all')
    return result
  }
}


