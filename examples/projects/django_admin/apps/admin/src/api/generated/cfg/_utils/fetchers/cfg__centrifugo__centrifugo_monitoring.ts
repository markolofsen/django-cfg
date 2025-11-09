/**
 * Typed fetchers for Centrifugo Monitoring
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
import { CentrifugoOverviewStatsSchema, type CentrifugoOverviewStats } from '../schemas/CentrifugoOverviewStats.schema'
import { ChannelListSchema, type ChannelList } from '../schemas/ChannelList.schema'
import { HealthCheckSchema, type HealthCheck } from '../schemas/HealthCheck.schema'
import { PaginatedPublishListSchema, type PaginatedPublishList } from '../schemas/PaginatedPublishList.schema'
import { getAPIInstance } from '../../api-instance'

/**
 * Get Centrifugo health status
 *
 * @method GET
 * @path /cfg/centrifugo/monitor/health/
 */
export async function getCentrifugoMonitorHealthRetrieve(  client?: any
): Promise<HealthCheck> {
  const api = client || getAPIInstance()
  const response = await api.cfg_centrifugo_monitoring.centrifugoMonitorHealthRetrieve()
  try {
    return HealthCheckSchema.parse(response)
  } catch (error) {
    // Zod validation error - log detailed information
    consola.error('❌ Zod Validation Failed');
    consola.box({
      title: 'getCentrifugoMonitorHealthRetrieve',
      message: `Path: /cfg/centrifugo/monitor/health/\nMethod: GET`,
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
 * Get overview statistics
 *
 * @method GET
 * @path /cfg/centrifugo/monitor/overview/
 */
export async function getCentrifugoMonitorOverviewRetrieve(  params?: { hours?: number },  client?: any
): Promise<CentrifugoOverviewStats> {
  const api = client || getAPIInstance()
  const response = await api.cfg_centrifugo_monitoring.centrifugoMonitorOverviewRetrieve(params?.hours)
  try {
    return CentrifugoOverviewStatsSchema.parse(response)
  } catch (error) {
    // Zod validation error - log detailed information
    consola.error('❌ Zod Validation Failed');
    consola.box({
      title: 'getCentrifugoMonitorOverviewRetrieve',
      message: `Path: /cfg/centrifugo/monitor/overview/\nMethod: GET`,
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
 * Get recent publishes
 *
 * @method GET
 * @path /cfg/centrifugo/monitor/publishes/
 */
export async function getCentrifugoMonitorPublishesList(  params?: { channel?: string; page?: number; page_size?: number; status?: string },  client?: any
): Promise<PaginatedPublishList> {
  const api = client || getAPIInstance()
  const response = await api.cfg_centrifugo_monitoring.centrifugoMonitorPublishesList(params?.channel, params?.page, params?.page_size, params?.status)
  try {
    return PaginatedPublishListSchema.parse(response)
  } catch (error) {
    // Zod validation error - log detailed information
    consola.error('❌ Zod Validation Failed');
    consola.box({
      title: 'getCentrifugoMonitorPublishesList',
      message: `Path: /cfg/centrifugo/monitor/publishes/\nMethod: GET`,
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
 * Get channel statistics
 *
 * @method GET
 * @path /cfg/centrifugo/monitor/timeline/
 */
export async function getCentrifugoMonitorTimelineRetrieve(  params?: { hours?: number; interval?: string },  client?: any
): Promise<ChannelList> {
  const api = client || getAPIInstance()
  const response = await api.cfg_centrifugo_monitoring.centrifugoMonitorTimelineRetrieve(params?.hours, params?.interval)
  try {
    return ChannelListSchema.parse(response)
  } catch (error) {
    // Zod validation error - log detailed information
    consola.error('❌ Zod Validation Failed');
    consola.box({
      title: 'getCentrifugoMonitorTimelineRetrieve',
      message: `Path: /cfg/centrifugo/monitor/timeline/\nMethod: GET`,
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


