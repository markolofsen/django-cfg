/**
 * Typed fetchers for Dashboard - Overview
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
import { DashboardOverviewSchema, type DashboardOverview } from '../schemas/DashboardOverview.schema'
import { getAPIInstance } from '../../api-instance'

/**
 * Get dashboard overview
 *
 * @method GET
 * @path /cfg/dashboard/api/overview/overview/
 */
export async function getDashboardApiOverviewOverviewRetrieve(  client?: any
): Promise<DashboardOverview> {
  const api = client || getAPIInstance()
  const response = await api.cfg_dashboard_overview.dashboardApiOverviewOverviewRetrieve()
  return DashboardOverviewSchema.parse(response)
}


