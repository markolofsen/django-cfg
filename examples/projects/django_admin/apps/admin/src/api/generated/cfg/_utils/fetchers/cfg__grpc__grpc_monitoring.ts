/**
 * Typed fetchers for Grpc Monitoring
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
import { GRPCHealthCheckSchema, type GRPCHealthCheck } from '../schemas/GRPCHealthCheck.schema'
import { GRPCOverviewStatsSchema, type GRPCOverviewStats } from '../schemas/GRPCOverviewStats.schema'
import { MethodListSchema, type MethodList } from '../schemas/MethodList.schema'
import { PaginatedRecentRequestListSchema, type PaginatedRecentRequestList } from '../schemas/PaginatedRecentRequestList.schema'
import { getAPIInstance } from '../../api-instance'

/**
 * Get gRPC health status
 *
 * @method GET
 * @path /cfg/grpc/monitor/health/
 */
export async function getGrpcMonitorHealthRetrieve(  client?: any
): Promise<GRPCHealthCheck> {
  const api = client || getAPIInstance()
  const response = await api.cfg_grpc_monitoring.grpcMonitorHealthRetrieve()
  try {
    return GRPCHealthCheckSchema.parse(response)
  } catch (error) {
    // Zod validation error - log detailed information
    consola.error('❌ Zod Validation Failed');
    consola.box({
      title: 'getGrpcMonitorHealthRetrieve',
      message: `Path: /cfg/grpc/monitor/health/\nMethod: GET`,
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
            operation: 'getGrpcMonitorHealthRetrieve',
            path: '/cfg/grpc/monitor/health/',
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


/**
 * Get method statistics
 *
 * @method GET
 * @path /cfg/grpc/monitor/methods/
 */
export async function getGrpcMonitorMethodsRetrieve(  params?: { hours?: number; service?: string },  client?: any
): Promise<MethodList> {
  const api = client || getAPIInstance()
  const response = await api.cfg_grpc_monitoring.grpcMonitorMethodsRetrieve(params?.hours, params?.service)
  try {
    return MethodListSchema.parse(response)
  } catch (error) {
    // Zod validation error - log detailed information
    consola.error('❌ Zod Validation Failed');
    consola.box({
      title: 'getGrpcMonitorMethodsRetrieve',
      message: `Path: /cfg/grpc/monitor/methods/\nMethod: GET`,
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
            operation: 'getGrpcMonitorMethodsRetrieve',
            path: '/cfg/grpc/monitor/methods/',
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


/**
 * Get overview statistics
 *
 * @method GET
 * @path /cfg/grpc/monitor/overview/
 */
export async function getGrpcMonitorOverviewRetrieve(  params?: { hours?: number },  client?: any
): Promise<GRPCOverviewStats> {
  const api = client || getAPIInstance()
  const response = await api.cfg_grpc_monitoring.grpcMonitorOverviewRetrieve(params?.hours)
  try {
    return GRPCOverviewStatsSchema.parse(response)
  } catch (error) {
    // Zod validation error - log detailed information
    consola.error('❌ Zod Validation Failed');
    consola.box({
      title: 'getGrpcMonitorOverviewRetrieve',
      message: `Path: /cfg/grpc/monitor/overview/\nMethod: GET`,
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
            operation: 'getGrpcMonitorOverviewRetrieve',
            path: '/cfg/grpc/monitor/overview/',
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


/**
 * Get recent requests
 *
 * @method GET
 * @path /cfg/grpc/monitor/requests/
 */
export async function getGrpcMonitorRequestsList(  params?: { method?: string; page?: number; page_size?: number; service?: string; status?: string },  client?: any
): Promise<PaginatedRecentRequestList> {
  const api = client || getAPIInstance()
  const response = await api.cfg_grpc_monitoring.grpcMonitorRequestsList(params?.method, params?.page, params?.page_size, params?.service, params?.status)
  try {
    return PaginatedRecentRequestListSchema.parse(response)
  } catch (error) {
    // Zod validation error - log detailed information
    consola.error('❌ Zod Validation Failed');
    consola.box({
      title: 'getGrpcMonitorRequestsList',
      message: `Path: /cfg/grpc/monitor/requests/\nMethod: GET`,
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
            operation: 'getGrpcMonitorRequestsList',
            path: '/cfg/grpc/monitor/requests/',
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


/**
 * Get request timeline
 *
 * @method GET
 * @path /cfg/grpc/monitor/timeline/
 */
export async function getGrpcMonitorTimelineRetrieve(  params?: { hours?: number; interval?: string },  client?: any
): Promise<any> {
  const api = client || getAPIInstance()
  const response = await api.cfg_grpc_monitoring.grpcMonitorTimelineRetrieve(params?.hours, params?.interval)
  return response
}


