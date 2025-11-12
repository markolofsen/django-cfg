/**
 * Typed fetchers for Centrifugo Admin API
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
import { CentrifugoChannelsRequestRequestSchema, type CentrifugoChannelsRequestRequest } from '../schemas/CentrifugoChannelsRequestRequest.schema'
import { CentrifugoChannelsResponseSchema, type CentrifugoChannelsResponse } from '../schemas/CentrifugoChannelsResponse.schema'
import { CentrifugoHistoryRequestRequestSchema, type CentrifugoHistoryRequestRequest } from '../schemas/CentrifugoHistoryRequestRequest.schema'
import { CentrifugoHistoryResponseSchema, type CentrifugoHistoryResponse } from '../schemas/CentrifugoHistoryResponse.schema'
import { CentrifugoInfoResponseSchema, type CentrifugoInfoResponse } from '../schemas/CentrifugoInfoResponse.schema'
import { CentrifugoPresenceRequestRequestSchema, type CentrifugoPresenceRequestRequest } from '../schemas/CentrifugoPresenceRequestRequest.schema'
import { CentrifugoPresenceResponseSchema, type CentrifugoPresenceResponse } from '../schemas/CentrifugoPresenceResponse.schema'
import { CentrifugoPresenceStatsRequestRequestSchema, type CentrifugoPresenceStatsRequestRequest } from '../schemas/CentrifugoPresenceStatsRequestRequest.schema'
import { CentrifugoPresenceStatsResponseSchema, type CentrifugoPresenceStatsResponse } from '../schemas/CentrifugoPresenceStatsResponse.schema'
import { getAPIInstance } from '../../api-instance'

/**
 * Get connection token for dashboard
 *
 * @method POST
 * @path /cfg/centrifugo/server/auth/token/
 */
export async function createCentrifugoServerAuthTokenCreate(  client?: any
): Promise<any> {
  const api = client || getAPIInstance()
  const response = await api.cfg_centrifugo_admin_api.centrifugoServerAuthTokenCreate()
  return response
}


/**
 * List active channels
 *
 * @method POST
 * @path /cfg/centrifugo/server/channels/
 */
export async function createCentrifugoServerChannelsCreate(  data: CentrifugoChannelsRequestRequest,  client?: any
): Promise<CentrifugoChannelsResponse> {
  const api = client || getAPIInstance()
  const response = await api.cfg_centrifugo_admin_api.centrifugoServerChannelsCreate(data)
  try {
    return CentrifugoChannelsResponseSchema.parse(response)
  } catch (error) {
    // Zod validation error - log detailed information
    consola.error('❌ Zod Validation Failed');
    consola.box({
      title: 'createCentrifugoServerChannelsCreate',
      message: `Path: /cfg/centrifugo/server/channels/\nMethod: POST`,
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
            operation: 'createCentrifugoServerChannelsCreate',
            path: '/cfg/centrifugo/server/channels/',
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
 * Get channel history
 *
 * @method POST
 * @path /cfg/centrifugo/server/history/
 */
export async function createCentrifugoServerHistoryCreate(  data: CentrifugoHistoryRequestRequest,  client?: any
): Promise<CentrifugoHistoryResponse> {
  const api = client || getAPIInstance()
  const response = await api.cfg_centrifugo_admin_api.centrifugoServerHistoryCreate(data)
  try {
    return CentrifugoHistoryResponseSchema.parse(response)
  } catch (error) {
    // Zod validation error - log detailed information
    consola.error('❌ Zod Validation Failed');
    consola.box({
      title: 'createCentrifugoServerHistoryCreate',
      message: `Path: /cfg/centrifugo/server/history/\nMethod: POST`,
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
            operation: 'createCentrifugoServerHistoryCreate',
            path: '/cfg/centrifugo/server/history/',
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
 * Get Centrifugo server info
 *
 * @method POST
 * @path /cfg/centrifugo/server/info/
 */
export async function createCentrifugoServerInfoCreate(  client?: any
): Promise<CentrifugoInfoResponse> {
  const api = client || getAPIInstance()
  const response = await api.cfg_centrifugo_admin_api.centrifugoServerInfoCreate()
  try {
    return CentrifugoInfoResponseSchema.parse(response)
  } catch (error) {
    // Zod validation error - log detailed information
    consola.error('❌ Zod Validation Failed');
    consola.box({
      title: 'createCentrifugoServerInfoCreate',
      message: `Path: /cfg/centrifugo/server/info/\nMethod: POST`,
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
            operation: 'createCentrifugoServerInfoCreate',
            path: '/cfg/centrifugo/server/info/',
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
 * Get channel presence
 *
 * @method POST
 * @path /cfg/centrifugo/server/presence/
 */
export async function createCentrifugoServerPresenceCreate(  data: CentrifugoPresenceRequestRequest,  client?: any
): Promise<CentrifugoPresenceResponse> {
  const api = client || getAPIInstance()
  const response = await api.cfg_centrifugo_admin_api.centrifugoServerPresenceCreate(data)
  try {
    return CentrifugoPresenceResponseSchema.parse(response)
  } catch (error) {
    // Zod validation error - log detailed information
    consola.error('❌ Zod Validation Failed');
    consola.box({
      title: 'createCentrifugoServerPresenceCreate',
      message: `Path: /cfg/centrifugo/server/presence/\nMethod: POST`,
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
            operation: 'createCentrifugoServerPresenceCreate',
            path: '/cfg/centrifugo/server/presence/',
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
 * Get channel presence statistics
 *
 * @method POST
 * @path /cfg/centrifugo/server/presence-stats/
 */
export async function createCentrifugoServerPresenceStatsCreate(  data: CentrifugoPresenceStatsRequestRequest,  client?: any
): Promise<CentrifugoPresenceStatsResponse> {
  const api = client || getAPIInstance()
  const response = await api.cfg_centrifugo_admin_api.centrifugoServerPresenceStatsCreate(data)
  try {
    return CentrifugoPresenceStatsResponseSchema.parse(response)
  } catch (error) {
    // Zod validation error - log detailed information
    consola.error('❌ Zod Validation Failed');
    consola.box({
      title: 'createCentrifugoServerPresenceStatsCreate',
      message: `Path: /cfg/centrifugo/server/presence-stats/\nMethod: POST`,
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
            operation: 'createCentrifugoServerPresenceStatsCreate',
            path: '/cfg/centrifugo/server/presence-stats/',
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


