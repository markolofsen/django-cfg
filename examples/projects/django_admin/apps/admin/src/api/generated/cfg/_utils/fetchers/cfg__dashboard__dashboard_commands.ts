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
import { consola } from 'consola'
import { CommandExecuteRequestRequestSchema, type CommandExecuteRequestRequest } from '../schemas/CommandExecuteRequestRequest.schema'
import { CommandHelpResponseSchema, type CommandHelpResponse } from '../schemas/CommandHelpResponse.schema'
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
 * Get command help
 *
 * @method GET
 * @path /cfg/dashboard/api/commands/{id}/help/
 */
export async function getDashboardApiCommandsHelpRetrieve(  id: string,  client?: any
): Promise<CommandHelpResponse> {
  const api = client || getAPIInstance()
  const response = await api.cfg_dashboard_commands.dashboardApiCommandsHelpRetrieve(id)
  try {
    return CommandHelpResponseSchema.parse(response)
  } catch (error) {
    // Zod validation error - log detailed information
    consola.error('❌ Zod Validation Failed');
    consola.box({
      title: 'getDashboardApiCommandsHelpRetrieve',
      message: `Path: /cfg/dashboard/api/commands/{id}/help/\nMethod: GET`,
      style: {
        borderColor: 'red',
        borderStyle: 'rounded'
      }
    });

    if (error instanceof Error && 'issues' in error && Array.isArray((error as any).issues)) {
      consola.error('Validation Issues:');
      (error as any).issues.forEach((issue: any, index: number) => {
        consola.error(`  ${index + 1}. ${issue.path.join('.') || 'root'}`);
        consola.error(`     ├─ Message: ${issue.message}`);
        if (issue.expected) consola.error(`     ├─ Expected: ${issue.expected}`);
        if (issue.received) consola.error(`     └─ Received: ${issue.received}`);
      });
    }

    consola.error('Response data:', response);

    // Re-throw the error
    throw error;
  }
}


/**
 * Execute command
 *
 * @method POST
 * @path /cfg/dashboard/api/commands/execute/
 */
export async function createDashboardApiCommandsExecuteCreate(  data: CommandExecuteRequestRequest,  client?: any
): Promise<any> {
  const api = client || getAPIInstance()
  const response = await api.cfg_dashboard_commands.dashboardApiCommandsExecuteCreate(data)
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
  try {
    return CommandsSummarySchema.parse(response)
  } catch (error) {
    // Zod validation error - log detailed information
    consola.error('❌ Zod Validation Failed');
    consola.box({
      title: 'getDashboardApiCommandsSummaryRetrieve',
      message: `Path: /cfg/dashboard/api/commands/summary/\nMethod: GET`,
      style: {
        borderColor: 'red',
        borderStyle: 'rounded'
      }
    });

    if (error instanceof Error && 'issues' in error && Array.isArray((error as any).issues)) {
      consola.error('Validation Issues:');
      (error as any).issues.forEach((issue: any, index: number) => {
        consola.error(`  ${index + 1}. ${issue.path.join('.') || 'root'}`);
        consola.error(`     ├─ Message: ${issue.message}`);
        if (issue.expected) consola.error(`     ├─ Expected: ${issue.expected}`);
        if (issue.received) consola.error(`     └─ Received: ${issue.received}`);
      });
    }

    consola.error('Response data:', response);

    // Re-throw the error
    throw error;
  }
}


