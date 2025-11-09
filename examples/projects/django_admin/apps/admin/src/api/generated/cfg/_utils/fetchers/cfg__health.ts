/**
 * Typed fetchers for Health
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
import { HealthCheckSchema, type HealthCheck } from '../schemas/HealthCheck.schema'
import { QuickHealthSchema, type QuickHealth } from '../schemas/QuickHealth.schema'
import { getAPIInstance } from '../../api-instance'

/**
 * API operation
 *
 * @method GET
 * @path /cfg/health/drf/
 */
export async function getHealthDrfRetrieve(  client?: any
): Promise<HealthCheck> {
  const api = client || getAPIInstance()
  const response = await api.cfg_health.drfRetrieve()
  try {
    return HealthCheckSchema.parse(response)
  } catch (error) {
    // Zod validation error - log detailed information
    consola.error('❌ Zod Validation Failed');
    consola.box({
      title: 'getHealthDrfRetrieve',
      message: `Path: /cfg/health/drf/\nMethod: GET`,
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
 * API operation
 *
 * @method GET
 * @path /cfg/health/drf/quick/
 */
export async function getHealthDrfQuickRetrieve(  client?: any
): Promise<QuickHealth> {
  const api = client || getAPIInstance()
  const response = await api.cfg_health.drfQuickRetrieve()
  try {
    return QuickHealthSchema.parse(response)
  } catch (error) {
    // Zod validation error - log detailed information
    consola.error('❌ Zod Validation Failed');
    consola.box({
      title: 'getHealthDrfQuickRetrieve',
      message: `Path: /cfg/health/drf/quick/\nMethod: GET`,
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


