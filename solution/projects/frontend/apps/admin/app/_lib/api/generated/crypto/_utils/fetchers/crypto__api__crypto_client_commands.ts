/**
 * Typed fetchers for Crypto Client Commands
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
import { ClientCommandSchema, type ClientCommand } from '../schemas/ClientCommand.schema'
import { getAPIInstance } from '../../api-instance'

/**
 * List active crypto clients
 *
 * @method GET
 * @path /api/crypto/commands/
 */
export async function getCryptoCommandsRetrieve(  client?: any
): Promise<any> {
  const api = client || getAPIInstance()
  const response = await api.crypto_client_commands.cryptoCommandsRetrieve()
  return response
}


/**
 * Get crypto client details
 *
 * @method GET
 * @path /api/crypto/commands/{id}/
 */
export async function getCryptoCommandsRetrieve2(  id: string,  client?: any
): Promise<any> {
  const api = client || getAPIInstance()
  const response = await api.crypto_client_commands.cryptoCommandsRetrieve2(id)
  return response
}


/**
 * Pause crypto client
 *
 * @method POST
 * @path /api/crypto/commands/{id}/pause/
 */
export async function createCryptoCommandsPauseCreate(  id: string,  client?: any
): Promise<ClientCommand> {
  const api = client || getAPIInstance()
  const response = await api.crypto_client_commands.cryptoCommandsPauseCreate(id)
  try {
    return ClientCommandSchema.parse(response)
  } catch (error) {
    // Zod validation error - log detailed information
    consola.error('❌ Zod Validation Failed');
    consola.box(`createCryptoCommandsPauseCreate\nPath: /api/crypto/commands/{id}/pause/\nMethod: POST`);

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
            operation: 'createCryptoCommandsPauseCreate',
            path: '/api/crypto/commands/{id}/pause/',
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
 * Ping crypto client
 *
 * @method POST
 * @path /api/crypto/commands/{id}/ping/
 */
export async function createCryptoCommandsPingCreate(  id: string,  client?: any
): Promise<any> {
  const api = client || getAPIInstance()
  const response = await api.crypto_client_commands.cryptoCommandsPingCreate(id)
  return response
}


/**
 * Request status from crypto client
 *
 * @method POST
 * @path /api/crypto/commands/{id}/request_status/
 */
export async function createCryptoCommandsRequestStatusCreate(  id: string, params?: { include_stats?: boolean },  client?: any
): Promise<ClientCommand> {
  const api = client || getAPIInstance()
  const response = await api.crypto_client_commands.cryptoCommandsRequestStatusCreate(id, params?.include_stats)
  try {
    return ClientCommandSchema.parse(response)
  } catch (error) {
    // Zod validation error - log detailed information
    consola.error('❌ Zod Validation Failed');
    consola.box(`createCryptoCommandsRequestStatusCreate\nPath: /api/crypto/commands/{id}/request_status/\nMethod: POST`);

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
            operation: 'createCryptoCommandsRequestStatusCreate',
            path: '/api/crypto/commands/{id}/request_status/',
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
 * Resume crypto client
 *
 * @method POST
 * @path /api/crypto/commands/{id}/resume/
 */
export async function createCryptoCommandsResumeCreate(  id: string,  client?: any
): Promise<ClientCommand> {
  const api = client || getAPIInstance()
  const response = await api.crypto_client_commands.cryptoCommandsResumeCreate(id)
  try {
    return ClientCommandSchema.parse(response)
  } catch (error) {
    // Zod validation error - log detailed information
    consola.error('❌ Zod Validation Failed');
    consola.box(`createCryptoCommandsResumeCreate\nPath: /api/crypto/commands/{id}/resume/\nMethod: POST`);

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
            operation: 'createCryptoCommandsResumeCreate',
            path: '/api/crypto/commands/{id}/resume/',
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
 * Sync wallets on crypto client
 *
 * @method POST
 * @path /api/crypto/commands/{id}/sync_wallets/
 */
export async function createCryptoCommandsSyncWalletsCreate(  id: string, params?: { symbols?: string },  client?: any
): Promise<any> {
  const api = client || getAPIInstance()
  const response = await api.crypto_client_commands.cryptoCommandsSyncWalletsCreate(id, params?.symbols)
  return response
}


/**
 * Pause all crypto clients
 *
 * @method POST
 * @path /api/crypto/commands/pause_all/
 */
export async function createCryptoCommandsPauseAllCreate(  client?: any
): Promise<any> {
  const api = client || getAPIInstance()
  const response = await api.crypto_client_commands.cryptoCommandsPauseAllCreate()
  return response
}


/**
 * Resume all crypto clients
 *
 * @method POST
 * @path /api/crypto/commands/resume_all/
 */
export async function createCryptoCommandsResumeAllCreate(  client?: any
): Promise<any> {
  const api = client || getAPIInstance()
  const response = await api.crypto_client_commands.cryptoCommandsResumeAllCreate()
  return response
}


/**
 * Sync wallets on all crypto clients
 *
 * @method POST
 * @path /api/crypto/commands/sync_all/
 */
export async function createCryptoCommandsSyncAllCreate(  params?: { symbols?: string },  client?: any
): Promise<any> {
  const api = client || getAPIInstance()
  const response = await api.crypto_client_commands.cryptoCommandsSyncAllCreate(params?.symbols)
  return response
}


