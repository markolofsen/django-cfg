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
import { getAPIInstance } from '../../api-instance'
import type { API } from '../../index'

/**
 * getDjangoCfgLeadsLeadsList
 *
 * ViewSet for Lead model.
 * 
 * Provides only submission functionality for leads from frontend forms.
 *
 * @method GET
 * @path /django_cfg_leads/leads/
 */
export async function getDjangoCfgLeadsLeadsList(
  params?: { page?: number; page_size?: number },
  client?: API
): Promise<PaginatedLeadSubmissionList> {
  const api = client || getAPIInstance()

  const response = await api.cfg_leads.list(params?.page, params?.page_size)
  return PaginatedLeadSubmissionListSchema.parse(response)
}

/**
 * createDjangoCfgLeadsLeads
 *
 * ViewSet for Lead model.
 * 
 * Provides only submission functionality for leads from frontend forms.
 *
 * @method POST
 * @path /django_cfg_leads/leads/
 */
export async function createDjangoCfgLeadsLeads(
  data: LeadSubmissionRequest,
  client?: API
): Promise<LeadSubmission> {
  const api = client || getAPIInstance()

  const response = await api.cfg_leads.create(data)
  return LeadSubmissionSchema.parse(response)
}

/**
 * getDjangoCfgLeadsLeadsById
 *
 * ViewSet for Lead model.
 * 
 * Provides only submission functionality for leads from frontend forms.
 *
 * @method GET
 * @path /django_cfg_leads/leads/{id}/
 */
export async function getDjangoCfgLeadsLeadsById(
  id: number,
  client?: API
): Promise<LeadSubmission> {
  const api = client || getAPIInstance()

  const response = await api.cfg_leads.retrieve(id)
  return LeadSubmissionSchema.parse(response)
}

/**
 * updateDjangoCfgLeadsLeads
 *
 * ViewSet for Lead model.
 * 
 * Provides only submission functionality for leads from frontend forms.
 *
 * @method PUT
 * @path /django_cfg_leads/leads/{id}/
 */
export async function updateDjangoCfgLeadsLeads(
  id: number, data: LeadSubmissionRequest,
  client?: API
): Promise<LeadSubmission> {
  const api = client || getAPIInstance()

  const response = await api.cfg_leads.update(id, data)
  return LeadSubmissionSchema.parse(response)
}

/**
 * partialUpdateDjangoCfgLeadsLeads
 *
 * ViewSet for Lead model.
 * 
 * Provides only submission functionality for leads from frontend forms.
 *
 * @method PATCH
 * @path /django_cfg_leads/leads/{id}/
 */
export async function partialUpdateDjangoCfgLeadsLeads(
  id: number,
  client?: API
): Promise<LeadSubmission> {
  const api = client || getAPIInstance()

  const response = await api.cfg_leads.partialUpdate(id)
  return LeadSubmissionSchema.parse(response)
}

/**
 * deleteDjangoCfgLeadsLeads
 *
 * ViewSet for Lead model.
 * 
 * Provides only submission functionality for leads from frontend forms.
 *
 * @method DELETE
 * @path /django_cfg_leads/leads/{id}/
 */
export async function deleteDjangoCfgLeadsLeads(
  id: number,
  client?: API
): Promise<void> {
  const api = client || getAPIInstance()

  const response = await api.cfg_leads.destroy(id)
  return response
}

