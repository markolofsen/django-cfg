/**
 * Typed fetchers for Lead Submission
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
import { LeadSubmissionRequestSchema, type LeadSubmissionRequest } from '../schemas/LeadSubmissionRequest.schema'
import { LeadSubmissionResponseSchema, type LeadSubmissionResponse } from '../schemas/LeadSubmissionResponse.schema'
import { getAPIInstance } from '../../api-instance'
import type { API } from '../../index'

/**
 * Submit Lead Form
 *
 * Submit a new lead from frontend contact form with automatic Telegram notifications.
 *
 * @method POST
 * @path /cfg/leads/leads/submit/
 */
export async function createCfgLeadsLeadsSubmit(
  data: LeadSubmissionRequest,
  client?: API
): Promise<LeadSubmissionResponse> {
  const api = client || getAPIInstance()

  const response = await api.cfg_lead_submission.cfgLeadsLeadsSubmitCreate(data)
  return LeadSubmissionResponseSchema.parse(response)
}

