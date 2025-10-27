/**
 * Typed fetchers for Dashboard - Commands
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
import { CommandsSummarySchema, type CommandsSummary } from '../schemas/CommandsSummary.schema'
import { getAPIInstance } from '../../api-instance'

/**
 * Get all commands
 *
 * @method GET
 * @path /cfg/dashboard/api/commands/
 */
export async function getDashboardApiCommandsList(  client?: any
): Promise<any> {
  const api = client || getAPIInstance()
  const response = await api.cfg_dashboard_commands.dashboardApiCommandsList()
  return response
}


/**
 * Get commands summary
 *
 * @method GET
 * @path /cfg/dashboard/api/commands/summary/
 */
export async function getDashboardApiCommandsSummaryRetrieve(  client?: any
): Promise<CommandsSummary> {
  const api = client || getAPIInstance()
  const response = await api.cfg_dashboard_commands.dashboardApiCommandsSummaryRetrieve()
  return CommandsSummarySchema.parse(response)
}


