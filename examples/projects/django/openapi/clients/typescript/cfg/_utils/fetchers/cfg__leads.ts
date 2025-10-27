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
import { LeadSubmissionSchema, type LeadSubmission } from '../schemas/LeadSubmission.schema'
import { LeadSubmissionRequestSchema, type LeadSubmissionRequest } from '../schemas/LeadSubmissionRequest.schema'
import { PaginatedLeadSubmissionListSchema, type PaginatedLeadSubmissionList } from '../schemas/PaginatedLeadSubmissionList.schema'
import { PatchedLeadSubmissionRequestSchema, type PatchedLeadSubmissionRequest } from '../schemas/PatchedLeadSubmissionRequest.schema'
import { getAPIInstance } from '../../api-instance'
import type { API } from '../../index'

/**
 * API operation
 *
 * @method GET
 * @path /cfg/leads/
 */
export async function getLeadsList(  params?: { page?: number; page_size?: number },  client?: API
): Promise<PaginatedLeadSubmissionList> {
  const api = client || getAPIInstance()
  const response = await api.cfg_leads.list(params?.page, params?.page_size)
  return PaginatedLeadSubmissionListSchema.parse(response)
}


/**
 * API operation
 *
 * @method POST
 * @path /cfg/leads/
 */
export async function createLeadsCreate(  data: LeadSubmissionRequest,  client?: API
): Promise<LeadSubmission> {
  const api = client || getAPIInstance()
  const response = await api.cfg_leads.create(data)
  return LeadSubmissionSchema.parse(response)
}


/**
 * API operation
 *
 * @method GET
 * @path /cfg/leads/{id}/
 */
export async function getLeadsRetrieve(  id: number,  client?: API
): Promise<LeadSubmission> {
  const api = client || getAPIInstance()
  const response = await api.cfg_leads.retrieve(id)
  return LeadSubmissionSchema.parse(response)
}


/**
 * API operation
 *
 * @method PUT
 * @path /cfg/leads/{id}/
 */
export async function updateLeadsUpdate(  id: number, data: LeadSubmissionRequest,  client?: API
): Promise<LeadSubmission> {
  const api = client || getAPIInstance()
  const response = await api.cfg_leads.update(id, data)
  return LeadSubmissionSchema.parse(response)
}


/**
 * API operation
 *
 * @method PATCH
 * @path /cfg/leads/{id}/
 */
export async function partialUpdateLeadsPartialUpdate(  id: number, data?: PatchedLeadSubmissionRequest,  client?: API
): Promise<LeadSubmission> {
  const api = client || getAPIInstance()
  const response = await api.cfg_leads.partialUpdate(id, data)
  return LeadSubmissionSchema.parse(response)
}


/**
 * API operation
 *
 * @method DELETE
 * @path /cfg/leads/{id}/
 */
export async function deleteLeadsDestroy(  id: number,  client?: API
): Promise<void> {
  const api = client || getAPIInstance()
  const response = await api.cfg_leads.destroy(id)
  return response
}


