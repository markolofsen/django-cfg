/**
 * Typed fetchers for Dashboard - API Zones
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
import { APIZonesSummarySchema, type APIZonesSummary } from '../schemas/APIZonesSummary.schema'
import { getAPIInstance } from '../../api-instance'
import type { API } from '../../index'

/**
 * Get all API zones
 *
 * @method GET
 * @path /cfg/dashboard/api/zones/
 */
export async function getDashboardApiZonesList(  client?: API
): Promise<any> {
  const api = client || getAPIInstance()
  const response = await api.cfg_dashboard_api_zones.list()
  return response
}


/**
 * Get zones summary
 *
 * @method GET
 * @path /cfg/dashboard/api/zones/summary/
 */
export async function getDashboardApiZonesSummaryRetrieve(  client?: API
): Promise<APIZonesSummary> {
  const api = client || getAPIInstance()
  const response = await api.cfg_dashboard_api_zones.summaryRetrieve()
  return APIZonesSummarySchema.parse(response)
}


