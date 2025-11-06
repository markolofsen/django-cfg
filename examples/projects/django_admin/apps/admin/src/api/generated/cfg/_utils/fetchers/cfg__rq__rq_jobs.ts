/**
 * Typed fetchers for RQ Jobs
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
import { JobActionResponseSchema, type JobActionResponse } from '../schemas/JobActionResponse.schema'
import { JobDetailSchema, type JobDetail } from '../schemas/JobDetail.schema'
import { JobListRequestSchema, type JobListRequest } from '../schemas/JobListRequest.schema'
import { PaginatedJobListListSchema, type PaginatedJobListList } from '../schemas/PaginatedJobListList.schema'
import { getAPIInstance } from '../../api-instance'

/**
 * List all jobs
 *
 * @method GET
 * @path /cfg/rq/jobs/
 */
export async function getRqJobsList(  params?: { page?: number; page_size?: number; queue?: string; status?: string },  client?: any
): Promise<PaginatedJobListList> {
  const api = client || getAPIInstance()
  const response = await api.cfg_rq_jobs.list(params?.page, params?.page_size, params?.queue, params?.status)
  return PaginatedJobListListSchema.parse(response)
}


/**
 * Get job details
 *
 * @method GET
 * @path /cfg/rq/jobs/{id}/
 */
export async function getRqJobsRetrieve(  id: string,  client?: any
): Promise<JobDetail> {
  const api = client || getAPIInstance()
  const response = await api.cfg_rq_jobs.retrieve(id)
  return JobDetailSchema.parse(response)
}


/**
 * Delete job
 *
 * @method DELETE
 * @path /cfg/rq/jobs/{id}/
 */
export async function deleteRqJobsDestroy(  id: string,  client?: any
): Promise<JobActionResponse> {
  const api = client || getAPIInstance()
  const response = await api.cfg_rq_jobs.destroy(id)
  return JobActionResponseSchema.parse(response)
}


/**
 * Cancel job
 *
 * @method POST
 * @path /cfg/rq/jobs/{id}/cancel/
 */
export async function createRqJobsCancelCreate(  id: string, data: JobListRequest,  client?: any
): Promise<JobActionResponse> {
  const api = client || getAPIInstance()
  const response = await api.cfg_rq_jobs.cancelCreate(id, data)
  return JobActionResponseSchema.parse(response)
}


/**
 * Requeue job
 *
 * @method POST
 * @path /cfg/rq/jobs/{id}/requeue/
 */
export async function createRqJobsRequeueCreate(  id: string, data: JobListRequest,  client?: any
): Promise<JobActionResponse> {
  const api = client || getAPIInstance()
  const response = await api.cfg_rq_jobs.requeueCreate(id, data)
  return JobActionResponseSchema.parse(response)
}


