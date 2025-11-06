/**
 * Typed fetchers for Dashboard - Config
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
import { ConfigDataSchema, type ConfigData } from '../schemas/ConfigData.schema'
import { getAPIInstance } from '../../api-instance'

/**
 * Get configuration data
 *
 * @method GET
 * @path /cfg/dashboard/api/config/config/
 */
export async function getDashboardApiConfigConfigRetrieve(  client?: any
): Promise<ConfigData> {
  const api = client || getAPIInstance()
  const response = await api.cfg_dashboard_config.dashboardApiConfigConfigRetrieve()
  return ConfigDataSchema.parse(response)
}


