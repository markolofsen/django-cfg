/**
 * Typed fetchers for Cfg Leads
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
import { getAPIInstance } from '../../api-instance'
import type { API } from '../../index'

/**
 * getCfgLeadsLeadsList
 *
 * ViewSet for Lead model.
 * 
 * Provides only submission functionality for leads from frontend forms.
 *
 * @method GET
 * @path /cfg/leads/leads/
 */
export async function getCfgLeadsLeadsList(
  params?: { page?: number; page_size?: number },
  client?: API
): Promise<PaginatedLeadSubmissionList> {
  const api = client || getAPIInstance()

  const response = await api.cfg__leads.cfgLeadsLeadsList(params?.page, params?.page_size)
  return PaginatedLeadSubmissionListSchema.parse(response)
}

/**
 * createCfgLeadsLeads
 *
 * ViewSet for Lead model.
 * 
 * Provides only submission functionality for leads from frontend forms.
 *
 * @method POST
 * @path /cfg/leads/leads/
 */
export async function createCfgLeadsLeads(
  data: LeadSubmissionRequest,
  client?: API
): Promise<LeadSubmission> {
  const api = client || getAPIInstance()

  const response = await api.cfg__leads.cfgLeadsLeadsCreate(data)
  return LeadSubmissionSchema.parse(response)
}

/**
 * getCfgLeadsLeadsById
 *
 * ViewSet for Lead model.
 * 
 * Provides only submission functionality for leads from frontend forms.
 *
 * @method GET
 * @path /cfg/leads/leads/{id}/
 */
export async function getCfgLeadsLeadsById(
  id: number,
  client?: API
): Promise<LeadSubmission> {
  const api = client || getAPIInstance()

  const response = await api.cfg__leads.cfgLeadsLeadsRetrieve(id)
  return LeadSubmissionSchema.parse(response)
}

/**
 * updateCfgLeadsLeads
 *
 * ViewSet for Lead model.
 * 
 * Provides only submission functionality for leads from frontend forms.
 *
 * @method PUT
 * @path /cfg/leads/leads/{id}/
 */
export async function updateCfgLeadsLeads(
  id: number, data: LeadSubmissionRequest,
  client?: API
): Promise<LeadSubmission> {
  const api = client || getAPIInstance()

  const response = await api.cfg__leads.cfgLeadsLeadsUpdate(id, data)
  return LeadSubmissionSchema.parse(response)
}

/**
 * partialUpdateCfgLeadsLeads
 *
 * ViewSet for Lead model.
 * 
 * Provides only submission functionality for leads from frontend forms.
 *
 * @method PATCH
 * @path /cfg/leads/leads/{id}/
 */
export async function partialUpdateCfgLeadsLeads(
  id: number,
  client?: API
): Promise<LeadSubmission> {
  const api = client || getAPIInstance()

  const response = await api.cfg__leads.cfgLeadsLeadsPartialUpdate(id)
  return LeadSubmissionSchema.parse(response)
}

/**
 * deleteCfgLeadsLeads
 *
 * ViewSet for Lead model.
 * 
 * Provides only submission functionality for leads from frontend forms.
 *
 * @method DELETE
 * @path /cfg/leads/leads/{id}/
 */
export async function deleteCfgLeadsLeads(
  id: number,
  client?: API
): Promise<void> {
  const api = client || getAPIInstance()

  const response = await api.cfg__leads.cfgLeadsLeadsDestroy(id)
  return response
}

