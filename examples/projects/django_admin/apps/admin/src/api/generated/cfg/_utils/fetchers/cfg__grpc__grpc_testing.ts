/**
 * Typed fetchers for Grpc Testing
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
import { GRPCCallRequestRequestSchema, type GRPCCallRequestRequest } from '../schemas/GRPCCallRequestRequest.schema'
import { GRPCCallResponseSchema, type GRPCCallResponse } from '../schemas/GRPCCallResponse.schema'
import { GRPCExamplesListSchema, type GRPCExamplesList } from '../schemas/GRPCExamplesList.schema'
import { PaginatedGRPCTestLogListSchema, type PaginatedGRPCTestLogList } from '../schemas/PaginatedGRPCTestLogList.schema'
import { getAPIInstance } from '../../api-instance'

/**
 * Call gRPC method
 *
 * @method POST
 * @path /cfg/grpc/test/call/
 */
export async function createGrpcTestCallCreate(  data: GRPCCallRequestRequest,  client?: any
): Promise<GRPCCallResponse> {
  const api = client || getAPIInstance()
  const response = await api.cfg_grpc_testing.grpcTestCallCreate(data)
  try {
    return GRPCCallResponseSchema.parse(response)
  } catch (error) {
    // Zod validation error - log detailed information
    consola.error('❌ Zod Validation Failed');
    consola.box({
      title: 'createGrpcTestCallCreate',
      message: `Path: /cfg/grpc/test/call/\nMethod: POST`,
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
            operation: 'createGrpcTestCallCreate',
            path: '/cfg/grpc/test/call/',
            method: 'POST',
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
 * Get example payloads
 *
 * @method GET
 * @path /cfg/grpc/test/examples/
 */
export async function getGrpcTestExamplesRetrieve(  params?: { method?: string; service?: string },  client?: any
): Promise<GRPCExamplesList> {
  const api = client || getAPIInstance()
  const response = await api.cfg_grpc_testing.grpcTestExamplesRetrieve(params?.method, params?.service)
  try {
    return GRPCExamplesListSchema.parse(response)
  } catch (error) {
    // Zod validation error - log detailed information
    consola.error('❌ Zod Validation Failed');
    consola.box({
      title: 'getGrpcTestExamplesRetrieve',
      message: `Path: /cfg/grpc/test/examples/\nMethod: GET`,
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
            operation: 'getGrpcTestExamplesRetrieve',
            path: '/cfg/grpc/test/examples/',
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
 * Get test logs
 *
 * @method GET
 * @path /cfg/grpc/test/logs/
 */
export async function getGrpcTestLogsList(  params?: { method?: string; page?: number; page_size?: number; service?: string; status?: string },  client?: any
): Promise<PaginatedGRPCTestLogList> {
  const api = client || getAPIInstance()
  const response = await api.cfg_grpc_testing.grpcTestLogsList(params?.method, params?.page, params?.page_size, params?.service, params?.status)
  try {
    return PaginatedGRPCTestLogListSchema.parse(response)
  } catch (error) {
    // Zod validation error - log detailed information
    consola.error('❌ Zod Validation Failed');
    consola.box({
      title: 'getGrpcTestLogsList',
      message: `Path: /cfg/grpc/test/logs/\nMethod: GET`,
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
            operation: 'getGrpcTestLogsList',
            path: '/cfg/grpc/test/logs/',
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


