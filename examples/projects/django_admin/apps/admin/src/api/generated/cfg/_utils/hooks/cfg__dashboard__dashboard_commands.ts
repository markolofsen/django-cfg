/**
 * SWR Hooks for Dashboard - Commands
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
import * as Fetchers from '../fetchers/cfg__dashboard__dashboard_commands'
import type { API } from '../../index'
import type { CommandExecuteRequestRequest } from '../schemas/CommandExecuteRequestRequest.schema'
import type { CommandHelpResponse } from '../schemas/CommandHelpResponse.schema'
import type { CommandsSummary } from '../schemas/CommandsSummary.schema'

/**
 * Get all commands
 *
 * @method GET
 * @path /cfg/dashboard/api/commands/
 */
export function useDashboardApiCommandsList(client?: API): ReturnType<typeof useSWR<any>> {
  return useSWR<any>(
    'cfg-dashboard-api-commands',
    () => Fetchers.getDashboardApiCommandsList(client)
  )
}


/**
 * Get command help
 *
 * @method GET
 * @path /cfg/dashboard/api/commands/{id}/help/
 */
export function useDashboardApiCommandsHelpRetrieve(id: string, client?: API): ReturnType<typeof useSWR<CommandHelpResponse>> {
  return useSWR<CommandHelpResponse>(
    ['cfg-dashboard-api-commands-help', id],
    () => Fetchers.getDashboardApiCommandsHelpRetrieve(id, client)
  )
}


/**
 * Execute command
 *
 * @method POST
 * @path /cfg/dashboard/api/commands/execute/
 */
export function useCreateDashboardApiCommandsExecuteCreate() {
  const { mutate } = useSWRConfig()

  return async (data: CommandExecuteRequestRequest, client?: API): Promise<any> => {
    const result = await Fetchers.createDashboardApiCommandsExecuteCreate(data, client)
    // Revalidate related queries
    mutate('cfg-dashboard-api-commands-execute')
    return result
  }
}


/**
 * Get commands summary
 *
 * @method GET
 * @path /cfg/dashboard/api/commands/summary/
 */
export function useDashboardApiCommandsSummaryRetrieve(client?: API): ReturnType<typeof useSWR<CommandsSummary>> {
  return useSWR<CommandsSummary>(
    'cfg-dashboard-api-commands-summary',
    () => Fetchers.getDashboardApiCommandsSummaryRetrieve(client)
  )
}


