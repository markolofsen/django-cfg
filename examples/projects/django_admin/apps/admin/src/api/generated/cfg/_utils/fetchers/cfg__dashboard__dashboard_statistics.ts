/**
 * Typed fetchers for Dashboard - Statistics
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
import { UserStatisticsSchema, type UserStatistics } from '../schemas/UserStatistics.schema'
import { getAPIInstance } from '../../api-instance'

/**
 * Get application statistics
 *
 * @method GET
 * @path /cfg/dashboard/api/statistics/apps/
 */
export async function getDashboardApiStatisticsAppsList(  client?: any
): Promise<any> {
  const api = client || getAPIInstance()
  const response = await api.cfg_dashboard_statistics.dashboardApiStatisticsAppsList()
  return response
}


/**
 * Get statistics cards
 *
 * @method GET
 * @path /cfg/dashboard/api/statistics/cards/
 */
export async function getDashboardApiStatisticsCardsList(  client?: any
): Promise<any> {
  const api = client || getAPIInstance()
  const response = await api.cfg_dashboard_statistics.dashboardApiStatisticsCardsList()
  return response
}


/**
 * Get user statistics
 *
 * @method GET
 * @path /cfg/dashboard/api/statistics/users/
 */
export async function getDashboardApiStatisticsUsersRetrieve(  client?: any
): Promise<UserStatistics> {
  const api = client || getAPIInstance()
  const response = await api.cfg_dashboard_statistics.dashboardApiStatisticsUsersRetrieve()
  try {
    return UserStatisticsSchema.parse(response)
  } catch (error) {
    // Zod validation error - log detailed information
    consola.error('❌ Zod Validation Failed');
    consola.box({
      title: 'getDashboardApiStatisticsUsersRetrieve',
      message: `Path: /cfg/dashboard/api/statistics/users/\nMethod: GET`,
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

    // Dispatch browser CustomEvent (only if window is defined)
    if (typeof window !== 'undefined' && error instanceof Error && 'issues' in error) {
      try {
        const event = new CustomEvent('zod-validation-error', {
          detail: {
            operation: 'getDashboardApiStatisticsUsersRetrieve',
            path: '/cfg/dashboard/api/statistics/users/',
            method: 'GET',
            error: error,
            response: response,
            timestamp: new Date(),
          },
          bubbles: true,
          cancelable: false,
        });
        window.dispatchEvent(event);
      } catch (eventError) {
        // Silently fail - event dispatch should never crash the app
        consola.warn('Failed to dispatch validation error event:', eventError);
      }
    }

    // Re-throw the error
    throw error;
  }
}


