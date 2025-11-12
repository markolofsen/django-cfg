/**
 * Typed fetchers for RQ Registries
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
import { JobActionResponseSchema, type JobActionResponse } from '../schemas/JobActionResponse.schema'
import { JobListRequestSchema, type JobListRequest } from '../schemas/JobListRequest.schema'
import { PaginatedJobListListSchema, type PaginatedJobListList } from '../schemas/PaginatedJobListList.schema'
import { getAPIInstance } from '../../api-instance'

/**
 * List deferred jobs
 *
 * @method GET
 * @path /cfg/rq/jobs/registries/deferred/
 */
export async function getRqJobsRegistriesDeferredList(  params?: { page?: number; page_size?: number; queue?: string },  client?: any
): Promise<PaginatedJobListList> {
  const api = client || getAPIInstance()
  const response = await api.cfg_rq_registries.rqJobsRegistriesDeferredList(params?.page, params?.page_size, params?.queue)
  try {
    return PaginatedJobListListSchema.parse(response)
  } catch (error) {
    // Zod validation error - log detailed information
    consola.error('❌ Zod Validation Failed');
    consola.box({
      title: 'getRqJobsRegistriesDeferredList',
      message: `Path: /cfg/rq/jobs/registries/deferred/\nMethod: GET`,
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
            operation: 'getRqJobsRegistriesDeferredList',
            path: '/cfg/rq/jobs/registries/deferred/',
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
 * List failed jobs
 *
 * @method GET
 * @path /cfg/rq/jobs/registries/failed/
 */
export async function getRqJobsRegistriesFailedList(  params?: { page?: number; page_size?: number; queue?: string },  client?: any
): Promise<PaginatedJobListList> {
  const api = client || getAPIInstance()
  const response = await api.cfg_rq_registries.rqJobsRegistriesFailedList(params?.page, params?.page_size, params?.queue)
  try {
    return PaginatedJobListListSchema.parse(response)
  } catch (error) {
    // Zod validation error - log detailed information
    consola.error('❌ Zod Validation Failed');
    consola.box({
      title: 'getRqJobsRegistriesFailedList',
      message: `Path: /cfg/rq/jobs/registries/failed/\nMethod: GET`,
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
            operation: 'getRqJobsRegistriesFailedList',
            path: '/cfg/rq/jobs/registries/failed/',
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
 * Clear failed jobs registry
 *
 * @method POST
 * @path /cfg/rq/jobs/registries/failed/clear/
 */
export async function createRqJobsRegistriesFailedClearCreate(  data: JobListRequest, params: { queue: string },  client?: any
): Promise<JobActionResponse> {
  const api = client || getAPIInstance()
  const response = await api.cfg_rq_registries.rqJobsRegistriesFailedClearCreate(data, params.queue)
  try {
    return JobActionResponseSchema.parse(response)
  } catch (error) {
    // Zod validation error - log detailed information
    consola.error('❌ Zod Validation Failed');
    consola.box({
      title: 'createRqJobsRegistriesFailedClearCreate',
      message: `Path: /cfg/rq/jobs/registries/failed/clear/\nMethod: POST`,
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
            operation: 'createRqJobsRegistriesFailedClearCreate',
            path: '/cfg/rq/jobs/registries/failed/clear/',
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
 * Requeue all failed jobs
 *
 * @method POST
 * @path /cfg/rq/jobs/registries/failed/requeue-all/
 */
export async function createRqJobsRegistriesFailedRequeueAllCreate(  data: JobListRequest, params: { queue: string },  client?: any
): Promise<JobActionResponse> {
  const api = client || getAPIInstance()
  const response = await api.cfg_rq_registries.rqJobsRegistriesFailedRequeueAllCreate(data, params.queue)
  try {
    return JobActionResponseSchema.parse(response)
  } catch (error) {
    // Zod validation error - log detailed information
    consola.error('❌ Zod Validation Failed');
    consola.box({
      title: 'createRqJobsRegistriesFailedRequeueAllCreate',
      message: `Path: /cfg/rq/jobs/registries/failed/requeue-all/\nMethod: POST`,
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
            operation: 'createRqJobsRegistriesFailedRequeueAllCreate',
            path: '/cfg/rq/jobs/registries/failed/requeue-all/',
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
 * List finished jobs
 *
 * @method GET
 * @path /cfg/rq/jobs/registries/finished/
 */
export async function getRqJobsRegistriesFinishedList(  params?: { page?: number; page_size?: number; queue?: string },  client?: any
): Promise<PaginatedJobListList> {
  const api = client || getAPIInstance()
  const response = await api.cfg_rq_registries.rqJobsRegistriesFinishedList(params?.page, params?.page_size, params?.queue)
  try {
    return PaginatedJobListListSchema.parse(response)
  } catch (error) {
    // Zod validation error - log detailed information
    consola.error('❌ Zod Validation Failed');
    consola.box({
      title: 'getRqJobsRegistriesFinishedList',
      message: `Path: /cfg/rq/jobs/registries/finished/\nMethod: GET`,
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
            operation: 'getRqJobsRegistriesFinishedList',
            path: '/cfg/rq/jobs/registries/finished/',
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
 * Clear finished jobs registry
 *
 * @method POST
 * @path /cfg/rq/jobs/registries/finished/clear/
 */
export async function createRqJobsRegistriesFinishedClearCreate(  data: JobListRequest, params: { queue: string },  client?: any
): Promise<JobActionResponse> {
  const api = client || getAPIInstance()
  const response = await api.cfg_rq_registries.rqJobsRegistriesFinishedClearCreate(data, params.queue)
  try {
    return JobActionResponseSchema.parse(response)
  } catch (error) {
    // Zod validation error - log detailed information
    consola.error('❌ Zod Validation Failed');
    consola.box({
      title: 'createRqJobsRegistriesFinishedClearCreate',
      message: `Path: /cfg/rq/jobs/registries/finished/clear/\nMethod: POST`,
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
            operation: 'createRqJobsRegistriesFinishedClearCreate',
            path: '/cfg/rq/jobs/registries/finished/clear/',
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
 * List started jobs
 *
 * @method GET
 * @path /cfg/rq/jobs/registries/started/
 */
export async function getRqJobsRegistriesStartedList(  params?: { page?: number; page_size?: number; queue?: string },  client?: any
): Promise<PaginatedJobListList> {
  const api = client || getAPIInstance()
  const response = await api.cfg_rq_registries.rqJobsRegistriesStartedList(params?.page, params?.page_size, params?.queue)
  try {
    return PaginatedJobListListSchema.parse(response)
  } catch (error) {
    // Zod validation error - log detailed information
    consola.error('❌ Zod Validation Failed');
    consola.box({
      title: 'getRqJobsRegistriesStartedList',
      message: `Path: /cfg/rq/jobs/registries/started/\nMethod: GET`,
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
            operation: 'getRqJobsRegistriesStartedList',
            path: '/cfg/rq/jobs/registries/started/',
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


