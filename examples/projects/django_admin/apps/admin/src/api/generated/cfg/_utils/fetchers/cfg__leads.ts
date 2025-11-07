/**
 * Typed fetchers for Leads
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
import { LeadSubmissionSchema, type LeadSubmission } from '../schemas/LeadSubmission.schema'
import { LeadSubmissionRequestSchema, type LeadSubmissionRequest } from '../schemas/LeadSubmissionRequest.schema'
import { PaginatedLeadSubmissionListSchema, type PaginatedLeadSubmissionList } from '../schemas/PaginatedLeadSubmissionList.schema'
import { PatchedLeadSubmissionRequestSchema, type PatchedLeadSubmissionRequest } from '../schemas/PatchedLeadSubmissionRequest.schema'
import { getAPIInstance } from '../../api-instance'

/**
 * API operation
 *
 * @method GET
 * @path /cfg/leads/
 */
export async function getLeadsList(  params?: { page?: number; page_size?: number },  client?: any
): Promise<PaginatedLeadSubmissionList> {
  const api = client || getAPIInstance()
  const response = await api.cfg_leads.list(params?.page, params?.page_size)
  try {
    return PaginatedLeadSubmissionListSchema.parse(response)
  } catch (error) {
    // Zod validation error - log detailed information
    consola.error('❌ Zod Validation Failed');
    consola.box({
      title: 'getLeadsList',
      message: `Path: /cfg/leads/\nMethod: GET`,
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
 * @method POST
 * @path /cfg/leads/
 */
export async function createLeadsCreate(  data: LeadSubmissionRequest,  client?: any
): Promise<LeadSubmission> {
  const api = client || getAPIInstance()
  const response = await api.cfg_leads.create(data)
  try {
    return LeadSubmissionSchema.parse(response)
  } catch (error) {
    // Zod validation error - log detailed information
    consola.error('❌ Zod Validation Failed');
    consola.box({
      title: 'createLeadsCreate',
      message: `Path: /cfg/leads/\nMethod: POST`,
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
 * @path /cfg/leads/{id}/
 */
export async function getLeadsRetrieve(  id: number,  client?: any
): Promise<LeadSubmission> {
  const api = client || getAPIInstance()
  const response = await api.cfg_leads.retrieve(id)
  try {
    return LeadSubmissionSchema.parse(response)
  } catch (error) {
    // Zod validation error - log detailed information
    consola.error('❌ Zod Validation Failed');
    consola.box({
      title: 'getLeadsRetrieve',
      message: `Path: /cfg/leads/{id}/\nMethod: GET`,
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
 * @method PUT
 * @path /cfg/leads/{id}/
 */
export async function updateLeadsUpdate(  id: number, data: LeadSubmissionRequest,  client?: any
): Promise<LeadSubmission> {
  const api = client || getAPIInstance()
  const response = await api.cfg_leads.update(id, data)
  try {
    return LeadSubmissionSchema.parse(response)
  } catch (error) {
    // Zod validation error - log detailed information
    consola.error('❌ Zod Validation Failed');
    consola.box({
      title: 'updateLeadsUpdate',
      message: `Path: /cfg/leads/{id}/\nMethod: PUT`,
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
 * @method PATCH
 * @path /cfg/leads/{id}/
 */
export async function partialUpdateLeadsPartialUpdate(  id: number, data?: PatchedLeadSubmissionRequest,  client?: any
): Promise<LeadSubmission> {
  const api = client || getAPIInstance()
  const response = await api.cfg_leads.partialUpdate(id, data)
  try {
    return LeadSubmissionSchema.parse(response)
  } catch (error) {
    // Zod validation error - log detailed information
    consola.error('❌ Zod Validation Failed');
    consola.box({
      title: 'partialUpdateLeadsPartialUpdate',
      message: `Path: /cfg/leads/{id}/\nMethod: PATCH`,
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
 * @method DELETE
 * @path /cfg/leads/{id}/
 */
export async function deleteLeadsDestroy(  id: number,  client?: any
): Promise<void> {
  const api = client || getAPIInstance()
  const response = await api.cfg_leads.destroy(id)
  return response
}


