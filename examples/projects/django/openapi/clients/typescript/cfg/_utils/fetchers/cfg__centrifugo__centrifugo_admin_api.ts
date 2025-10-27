/**
 * Typed fetchers for Centrifugo Admin API
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
import { CentrifugoChannelsRequestRequestSchema, type CentrifugoChannelsRequestRequest } from '../schemas/CentrifugoChannelsRequestRequest.schema'
import { CentrifugoChannelsResponseSchema, type CentrifugoChannelsResponse } from '../schemas/CentrifugoChannelsResponse.schema'
import { CentrifugoHistoryRequestRequestSchema, type CentrifugoHistoryRequestRequest } from '../schemas/CentrifugoHistoryRequestRequest.schema'
import { CentrifugoHistoryResponseSchema, type CentrifugoHistoryResponse } from '../schemas/CentrifugoHistoryResponse.schema'
import { CentrifugoInfoResponseSchema, type CentrifugoInfoResponse } from '../schemas/CentrifugoInfoResponse.schema'
import { CentrifugoPresenceRequestRequestSchema, type CentrifugoPresenceRequestRequest } from '../schemas/CentrifugoPresenceRequestRequest.schema'
import { CentrifugoPresenceResponseSchema, type CentrifugoPresenceResponse } from '../schemas/CentrifugoPresenceResponse.schema'
import { CentrifugoPresenceStatsRequestRequestSchema, type CentrifugoPresenceStatsRequestRequest } from '../schemas/CentrifugoPresenceStatsRequestRequest.schema'
import { CentrifugoPresenceStatsResponseSchema, type CentrifugoPresenceStatsResponse } from '../schemas/CentrifugoPresenceStatsResponse.schema'
import { getAPIInstance } from '../../api-instance'

/**
 * Get connection token for dashboard
 *
 * @method POST
 * @path /cfg/centrifugo/admin/api/server/auth/token/
 */
export async function createCentrifugoAdminApiServerAuthTokenCreate(  client?: any
): Promise<any> {
  const api = client || getAPIInstance()
  const response = await api.cfg_centrifugo_admin_api.serverAuthTokenCreate()
  return response
}


/**
 * List active channels
 *
 * @method POST
 * @path /cfg/centrifugo/admin/api/server/channels/
 */
export async function createCentrifugoAdminApiServerChannelsCreate(  data: CentrifugoChannelsRequestRequest,  client?: any
): Promise<CentrifugoChannelsResponse> {
  const api = client || getAPIInstance()
  const response = await api.cfg_centrifugo_admin_api.serverChannelsCreate(data)
  return CentrifugoChannelsResponseSchema.parse(response)
}


/**
 * Get channel history
 *
 * @method POST
 * @path /cfg/centrifugo/admin/api/server/history/
 */
export async function createCentrifugoAdminApiServerHistoryCreate(  data: CentrifugoHistoryRequestRequest,  client?: any
): Promise<CentrifugoHistoryResponse> {
  const api = client || getAPIInstance()
  const response = await api.cfg_centrifugo_admin_api.serverHistoryCreate(data)
  return CentrifugoHistoryResponseSchema.parse(response)
}


/**
 * Get Centrifugo server info
 *
 * @method POST
 * @path /cfg/centrifugo/admin/api/server/info/
 */
export async function createCentrifugoAdminApiServerInfoCreate(  client?: any
): Promise<CentrifugoInfoResponse> {
  const api = client || getAPIInstance()
  const response = await api.cfg_centrifugo_admin_api.serverInfoCreate()
  return CentrifugoInfoResponseSchema.parse(response)
}


/**
 * Get channel presence
 *
 * @method POST
 * @path /cfg/centrifugo/admin/api/server/presence/
 */
export async function createCentrifugoAdminApiServerPresenceCreate(  data: CentrifugoPresenceRequestRequest,  client?: any
): Promise<CentrifugoPresenceResponse> {
  const api = client || getAPIInstance()
  const response = await api.cfg_centrifugo_admin_api.serverPresenceCreate(data)
  return CentrifugoPresenceResponseSchema.parse(response)
}


/**
 * Get channel presence statistics
 *
 * @method POST
 * @path /cfg/centrifugo/admin/api/server/presence-stats/
 */
export async function createCentrifugoAdminApiServerPresenceStatsCreate(  data: CentrifugoPresenceStatsRequestRequest,  client?: any
): Promise<CentrifugoPresenceStatsResponse> {
  const api = client || getAPIInstance()
  const response = await api.cfg_centrifugo_admin_api.serverPresenceStatsCreate(data)
  return CentrifugoPresenceStatsResponseSchema.parse(response)
}


/**
 * Get connection token for dashboard
 *
 * @method POST
 * @path /cfg/centrifugo/server/auth/token/
 */
export async function createCentrifugoServerAuthTokenCreate(  client?: any
): Promise<any> {
  const api = client || getAPIInstance()
  const response = await api.cfg_centrifugo_admin_api.centrifugoServerAuthTokenCreate()
  return response
}


/**
 * List active channels
 *
 * @method POST
 * @path /cfg/centrifugo/server/channels/
 */
export async function createCentrifugoServerChannelsCreate(  data: CentrifugoChannelsRequestRequest,  client?: any
): Promise<CentrifugoChannelsResponse> {
  const api = client || getAPIInstance()
  const response = await api.cfg_centrifugo_admin_api.centrifugoServerChannelsCreate(data)
  return CentrifugoChannelsResponseSchema.parse(response)
}


/**
 * Get channel history
 *
 * @method POST
 * @path /cfg/centrifugo/server/history/
 */
export async function createCentrifugoServerHistoryCreate(  data: CentrifugoHistoryRequestRequest,  client?: any
): Promise<CentrifugoHistoryResponse> {
  const api = client || getAPIInstance()
  const response = await api.cfg_centrifugo_admin_api.centrifugoServerHistoryCreate(data)
  return CentrifugoHistoryResponseSchema.parse(response)
}


/**
 * Get Centrifugo server info
 *
 * @method POST
 * @path /cfg/centrifugo/server/info/
 */
export async function createCentrifugoServerInfoCreate(  client?: any
): Promise<CentrifugoInfoResponse> {
  const api = client || getAPIInstance()
  const response = await api.cfg_centrifugo_admin_api.centrifugoServerInfoCreate()
  return CentrifugoInfoResponseSchema.parse(response)
}


/**
 * Get channel presence
 *
 * @method POST
 * @path /cfg/centrifugo/server/presence/
 */
export async function createCentrifugoServerPresenceCreate(  data: CentrifugoPresenceRequestRequest,  client?: any
): Promise<CentrifugoPresenceResponse> {
  const api = client || getAPIInstance()
  const response = await api.cfg_centrifugo_admin_api.centrifugoServerPresenceCreate(data)
  return CentrifugoPresenceResponseSchema.parse(response)
}


/**
 * Get channel presence statistics
 *
 * @method POST
 * @path /cfg/centrifugo/server/presence-stats/
 */
export async function createCentrifugoServerPresenceStatsCreate(  data: CentrifugoPresenceStatsRequestRequest,  client?: any
): Promise<CentrifugoPresenceStatsResponse> {
  const api = client || getAPIInstance()
  const response = await api.cfg_centrifugo_admin_api.centrifugoServerPresenceStatsCreate(data)
  return CentrifugoPresenceStatsResponseSchema.parse(response)
}


