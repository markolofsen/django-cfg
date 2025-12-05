/**
 * Typed fetchers for Terminal
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
import { CommandHistoryDetailSchema, type CommandHistoryDetail } from '../schemas/CommandHistoryDetail.schema'
import { PaginatedCommandHistoryListListSchema, type PaginatedCommandHistoryListList } from '../schemas/PaginatedCommandHistoryListList.schema'
import { PaginatedTerminalSessionListListSchema, type PaginatedTerminalSessionListList } from '../schemas/PaginatedTerminalSessionListList.schema'
import { TerminalInputRequestSchema, type TerminalInputRequest } from '../schemas/TerminalInputRequest.schema'
import { TerminalResizeRequestSchema, type TerminalResizeRequest } from '../schemas/TerminalResizeRequest.schema'
import { TerminalSessionCreateSchema, type TerminalSessionCreate } from '../schemas/TerminalSessionCreate.schema'
import { TerminalSessionCreateRequestSchema, type TerminalSessionCreateRequest } from '../schemas/TerminalSessionCreateRequest.schema'
import { TerminalSessionDetailSchema, type TerminalSessionDetail } from '../schemas/TerminalSessionDetail.schema'
import { TerminalSignalRequestSchema, type TerminalSignalRequest } from '../schemas/TerminalSignalRequest.schema'
import { getAPIInstance } from '../../api-instance'

/**
 * List command history
 *
 * @method GET
 * @path /api/terminal/commands/
 */
export async function getTerminalCommandsList(  params?: { page?: number; page_size?: number; search?: string; session?: string; status?: string },  client?: any
): Promise<PaginatedCommandHistoryListList> {
  const api = client || getAPIInstance()
  const response = await api.terminal_terminal.commandsList(params?.page, params?.page_size, params?.search, params?.session, params?.status)
  try {
    return PaginatedCommandHistoryListListSchema.parse(response)
  } catch (error) {
    // Zod validation error - log detailed information
    consola.error('❌ Zod Validation Failed');
    consola.box(`getTerminalCommandsList\nPath: /api/terminal/commands/\nMethod: GET`);

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
            operation: 'getTerminalCommandsList',
            path: '/api/terminal/commands/',
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
 * Get command details
 *
 * @method GET
 * @path /api/terminal/commands/{id}/
 */
export async function getTerminalCommandsRetrieve(  id: string,  client?: any
): Promise<CommandHistoryDetail> {
  const api = client || getAPIInstance()
  const response = await api.terminal_terminal.commandsRetrieve(id)
  try {
    return CommandHistoryDetailSchema.parse(response)
  } catch (error) {
    // Zod validation error - log detailed information
    consola.error('❌ Zod Validation Failed');
    consola.box(`getTerminalCommandsRetrieve\nPath: /api/terminal/commands/{id}/\nMethod: GET`);

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
            operation: 'getTerminalCommandsRetrieve',
            path: '/api/terminal/commands/{id}/',
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
 * List user's terminal sessions
 *
 * @method GET
 * @path /api/terminal/sessions/
 */
export async function getTerminalSessionsList(  params?: { page?: number; page_size?: number },  client?: any
): Promise<PaginatedTerminalSessionListList> {
  const api = client || getAPIInstance()
  const response = await api.terminal_terminal.sessionsList(params?.page, params?.page_size)
  try {
    return PaginatedTerminalSessionListListSchema.parse(response)
  } catch (error) {
    // Zod validation error - log detailed information
    consola.error('❌ Zod Validation Failed');
    consola.box(`getTerminalSessionsList\nPath: /api/terminal/sessions/\nMethod: GET`);

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
            operation: 'getTerminalSessionsList',
            path: '/api/terminal/sessions/',
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
 * Create new terminal session
 *
 * @method POST
 * @path /api/terminal/sessions/
 */
export async function createTerminalSessionsCreate(  data: TerminalSessionCreateRequest,  client?: any
): Promise<TerminalSessionCreate> {
  const api = client || getAPIInstance()
  const response = await api.terminal_terminal.sessionsCreate(data)
  try {
    return TerminalSessionCreateSchema.parse(response)
  } catch (error) {
    // Zod validation error - log detailed information
    consola.error('❌ Zod Validation Failed');
    consola.box(`createTerminalSessionsCreate\nPath: /api/terminal/sessions/\nMethod: POST`);

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
            operation: 'createTerminalSessionsCreate',
            path: '/api/terminal/sessions/',
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
 * Get session details
 *
 * @method GET
 * @path /api/terminal/sessions/{id}/
 */
export async function getTerminalSessionsRetrieve(  id: string,  client?: any
): Promise<TerminalSessionDetail> {
  const api = client || getAPIInstance()
  const response = await api.terminal_terminal.sessionsRetrieve(id)
  try {
    return TerminalSessionDetailSchema.parse(response)
  } catch (error) {
    // Zod validation error - log detailed information
    consola.error('❌ Zod Validation Failed');
    consola.box(`getTerminalSessionsRetrieve\nPath: /api/terminal/sessions/{id}/\nMethod: GET`);

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
            operation: 'getTerminalSessionsRetrieve',
            path: '/api/terminal/sessions/{id}/',
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
 * Close terminal session
 *
 * @method DELETE
 * @path /api/terminal/sessions/{id}/
 */
export async function deleteTerminalSessionsDestroy(  id: string,  client?: any
): Promise<void> {
  const api = client || getAPIInstance()
  const response = await api.terminal_terminal.sessionsDestroy(id)
  return response
}


/**
 * Get command history for session
 *
 * @method GET
 * @path /api/terminal/sessions/{id}/history/
 */
export async function getTerminalSessionsHistoryList(  id: string, params?: { page?: number; page_size?: number },  client?: any
): Promise<PaginatedCommandHistoryListList> {
  const api = client || getAPIInstance()
  const response = await api.terminal_terminal.sessionsHistoryList(id, params?.page, params?.page_size)
  try {
    return PaginatedCommandHistoryListListSchema.parse(response)
  } catch (error) {
    // Zod validation error - log detailed information
    consola.error('❌ Zod Validation Failed');
    consola.box(`getTerminalSessionsHistoryList\nPath: /api/terminal/sessions/{id}/history/\nMethod: GET`);

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
            operation: 'getTerminalSessionsHistoryList',
            path: '/api/terminal/sessions/{id}/history/',
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
 * Send input to terminal
 *
 * @method POST
 * @path /api/terminal/sessions/{id}/input/
 */
export async function createTerminalSessionsInputCreate(  id: string, data: TerminalInputRequest,  client?: any
): Promise<any> {
  const api = client || getAPIInstance()
  const response = await api.terminal_terminal.sessionsInputCreate(id, data)
  return response
}


/**
 * Resize terminal
 *
 * @method POST
 * @path /api/terminal/sessions/{id}/resize/
 */
export async function createTerminalSessionsResizeCreate(  id: string, data: TerminalResizeRequest,  client?: any
): Promise<any> {
  const api = client || getAPIInstance()
  const response = await api.terminal_terminal.sessionsResizeCreate(id, data)
  return response
}


/**
 * Send signal to terminal
 *
 * @method POST
 * @path /api/terminal/sessions/{id}/signal/
 */
export async function createTerminalSessionsSignalCreate(  id: string, data: TerminalSignalRequest,  client?: any
): Promise<any> {
  const api = client || getAPIInstance()
  const response = await api.terminal_terminal.sessionsSignalCreate(id, data)
  return response
}


/**
 * Get active sessions only
 *
 * @method GET
 * @path /api/terminal/sessions/active/
 */
export async function getTerminalSessionsActiveList(  params?: { page?: number; page_size?: number },  client?: any
): Promise<PaginatedTerminalSessionListList> {
  const api = client || getAPIInstance()
  const response = await api.terminal_terminal.sessionsActiveList(params?.page, params?.page_size)
  try {
    return PaginatedTerminalSessionListListSchema.parse(response)
  } catch (error) {
    // Zod validation error - log detailed information
    consola.error('❌ Zod Validation Failed');
    consola.box(`getTerminalSessionsActiveList\nPath: /api/terminal/sessions/active/\nMethod: GET`);

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
            operation: 'getTerminalSessionsActiveList',
            path: '/api/terminal/sessions/active/',
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


