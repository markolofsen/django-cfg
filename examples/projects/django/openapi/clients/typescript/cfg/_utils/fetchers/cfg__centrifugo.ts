/**
 * Typed fetchers for Centrifugo
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
import { getAPIInstance } from '../../api-instance'

/**
 * API operation
 *
 * @method GET
 * @path /cfg/centrifugo/admin/api/monitor/channels/
 */
export async function getCentrifugoAdminApiMonitorChannelsRetrieve(  client?: any
): Promise<any> {
  const api = client || getAPIInstance()
  const response = await api.cfg_centrifugo.adminApiMonitorChannelsRetrieve()
  return response
}


/**
 * API operation
 *
 * @method GET
 * @path /cfg/centrifugo/monitor/channels/
 */
export async function getCentrifugoMonitorChannelsRetrieve(  client?: any
): Promise<any> {
  const api = client || getAPIInstance()
  const response = await api.cfg_centrifugo.monitorChannelsRetrieve()
  return response
}


