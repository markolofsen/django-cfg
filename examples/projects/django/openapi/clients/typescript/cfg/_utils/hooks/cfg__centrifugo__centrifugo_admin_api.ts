/**
 * SWR Hooks for Centrifugo Admin API
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
import * as Fetchers from '../fetchers/cfg__centrifugo__centrifugo_admin_api'
import type { API } from '../../index'
import type { CentrifugoChannelsRequestRequest } from '../schemas/CentrifugoChannelsRequestRequest.schema'
import type { CentrifugoChannelsResponse } from '../schemas/CentrifugoChannelsResponse.schema'
import type { CentrifugoHistoryRequestRequest } from '../schemas/CentrifugoHistoryRequestRequest.schema'
import type { CentrifugoHistoryResponse } from '../schemas/CentrifugoHistoryResponse.schema'
import type { CentrifugoInfoResponse } from '../schemas/CentrifugoInfoResponse.schema'
import type { CentrifugoPresenceRequestRequest } from '../schemas/CentrifugoPresenceRequestRequest.schema'
import type { CentrifugoPresenceResponse } from '../schemas/CentrifugoPresenceResponse.schema'
import type { CentrifugoPresenceStatsRequestRequest } from '../schemas/CentrifugoPresenceStatsRequestRequest.schema'
import type { CentrifugoPresenceStatsResponse } from '../schemas/CentrifugoPresenceStatsResponse.schema'

/**
 * Get connection token for dashboard
 *
 * @method POST
 * @path /cfg/centrifugo/admin/api/server/auth/token/
 */
export function useCreateCentrifugoAdminApiServerAuthTokenCreate() {
  const { mutate } = useSWRConfig()

  return async (client?: API): Promise<any> => {
    const result = await Fetchers.createCentrifugoAdminApiServerAuthTokenCreate(client)
    // Revalidate related queries
    mutate('cfg-centrifugo-admin-api-server-auth-token')
    return result
  }
}


/**
 * List active channels
 *
 * @method POST
 * @path /cfg/centrifugo/admin/api/server/channels/
 */
export function useCreateCentrifugoAdminApiServerChannelsCreate() {
  const { mutate } = useSWRConfig()

  return async (data: CentrifugoChannelsRequestRequest, client?: API): Promise<CentrifugoChannelsResponse> => {
    const result = await Fetchers.createCentrifugoAdminApiServerChannelsCreate(data, client)
    // Revalidate related queries
    mutate('cfg-centrifugo-admin-api-server-channels')
    return result
  }
}


/**
 * Get channel history
 *
 * @method POST
 * @path /cfg/centrifugo/admin/api/server/history/
 */
export function useCreateCentrifugoAdminApiServerHistoryCreate() {
  const { mutate } = useSWRConfig()

  return async (data: CentrifugoHistoryRequestRequest, client?: API): Promise<CentrifugoHistoryResponse> => {
    const result = await Fetchers.createCentrifugoAdminApiServerHistoryCreate(data, client)
    // Revalidate related queries
    mutate('cfg-centrifugo-admin-api-server-history')
    return result
  }
}


/**
 * Get Centrifugo server info
 *
 * @method POST
 * @path /cfg/centrifugo/admin/api/server/info/
 */
export function useCreateCentrifugoAdminApiServerInfoCreate() {
  const { mutate } = useSWRConfig()

  return async (client?: API): Promise<CentrifugoInfoResponse> => {
    const result = await Fetchers.createCentrifugoAdminApiServerInfoCreate(client)
    // Revalidate related queries
    mutate('cfg-centrifugo-admin-api-server-info')
    return result
  }
}


/**
 * Get channel presence
 *
 * @method POST
 * @path /cfg/centrifugo/admin/api/server/presence/
 */
export function useCreateCentrifugoAdminApiServerPresenceCreate() {
  const { mutate } = useSWRConfig()

  return async (data: CentrifugoPresenceRequestRequest, client?: API): Promise<CentrifugoPresenceResponse> => {
    const result = await Fetchers.createCentrifugoAdminApiServerPresenceCreate(data, client)
    // Revalidate related queries
    mutate('cfg-centrifugo-admin-api-server-presence')
    return result
  }
}


/**
 * Get channel presence statistics
 *
 * @method POST
 * @path /cfg/centrifugo/admin/api/server/presence-stats/
 */
export function useCreateCentrifugoAdminApiServerPresenceStatsCreate() {
  const { mutate } = useSWRConfig()

  return async (data: CentrifugoPresenceStatsRequestRequest, client?: API): Promise<CentrifugoPresenceStatsResponse> => {
    const result = await Fetchers.createCentrifugoAdminApiServerPresenceStatsCreate(data, client)
    // Revalidate related queries
    mutate('cfg-centrifugo-admin-api-server-presence-stats')
    return result
  }
}


/**
 * Get connection token for dashboard
 *
 * @method POST
 * @path /cfg/centrifugo/server/auth/token/
 */
export function useCreateCentrifugoServerAuthTokenCreate() {
  const { mutate } = useSWRConfig()

  return async (client?: API): Promise<any> => {
    const result = await Fetchers.createCentrifugoServerAuthTokenCreate(client)
    // Revalidate related queries
    mutate('cfg-centrifugo-server-auth-token')
    return result
  }
}


/**
 * List active channels
 *
 * @method POST
 * @path /cfg/centrifugo/server/channels/
 */
export function useCreateCentrifugoServerChannelsCreate() {
  const { mutate } = useSWRConfig()

  return async (data: CentrifugoChannelsRequestRequest, client?: API): Promise<CentrifugoChannelsResponse> => {
    const result = await Fetchers.createCentrifugoServerChannelsCreate(data, client)
    // Revalidate related queries
    mutate('cfg-centrifugo-server-channels')
    return result
  }
}


/**
 * Get channel history
 *
 * @method POST
 * @path /cfg/centrifugo/server/history/
 */
export function useCreateCentrifugoServerHistoryCreate() {
  const { mutate } = useSWRConfig()

  return async (data: CentrifugoHistoryRequestRequest, client?: API): Promise<CentrifugoHistoryResponse> => {
    const result = await Fetchers.createCentrifugoServerHistoryCreate(data, client)
    // Revalidate related queries
    mutate('cfg-centrifugo-server-history')
    return result
  }
}


/**
 * Get Centrifugo server info
 *
 * @method POST
 * @path /cfg/centrifugo/server/info/
 */
export function useCreateCentrifugoServerInfoCreate() {
  const { mutate } = useSWRConfig()

  return async (client?: API): Promise<CentrifugoInfoResponse> => {
    const result = await Fetchers.createCentrifugoServerInfoCreate(client)
    // Revalidate related queries
    mutate('cfg-centrifugo-server-info')
    return result
  }
}


/**
 * Get channel presence
 *
 * @method POST
 * @path /cfg/centrifugo/server/presence/
 */
export function useCreateCentrifugoServerPresenceCreate() {
  const { mutate } = useSWRConfig()

  return async (data: CentrifugoPresenceRequestRequest, client?: API): Promise<CentrifugoPresenceResponse> => {
    const result = await Fetchers.createCentrifugoServerPresenceCreate(data, client)
    // Revalidate related queries
    mutate('cfg-centrifugo-server-presence')
    return result
  }
}


/**
 * Get channel presence statistics
 *
 * @method POST
 * @path /cfg/centrifugo/server/presence-stats/
 */
export function useCreateCentrifugoServerPresenceStatsCreate() {
  const { mutate } = useSWRConfig()

  return async (data: CentrifugoPresenceStatsRequestRequest, client?: API): Promise<CentrifugoPresenceStatsResponse> => {
    const result = await Fetchers.createCentrifugoServerPresenceStatsCreate(data, client)
    // Revalidate related queries
    mutate('cfg-centrifugo-server-presence-stats')
    return result
  }
}


