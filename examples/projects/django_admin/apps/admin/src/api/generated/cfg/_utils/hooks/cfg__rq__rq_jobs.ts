/**
 * SWR Hooks for RQ Jobs
 *
 * React hooks powered by SWR for data fetching with automatic caching,
 * revalidation, and optimistic updates.
 *
 * Usage:
 * ```typescript
 * // Query hooks (GET)
 * const { data, error, isLoading } = useUsers({ page: 1 })
 *
 * // Mutation hooks (POST/PUT/PATCH/DELETE)
 * const createUser = useCreateUser()
 * await createUser({ name: 'John', email: 'john@example.com' })
 * ```
 */
import useSWR from 'swr'
import { useSWRConfig } from 'swr'
import * as Fetchers from '../fetchers/cfg__rq__rq_jobs'
import type { API } from '../../index'
import type { JobActionResponse } from '../schemas/JobActionResponse.schema'
import type { JobDetail } from '../schemas/JobDetail.schema'

/**
 * List all jobs
 *
 * @method GET
 * @path /cfg/rq/jobs/
 */
export function useRqJobsList(params?: { queue?: string; status?: string }, client?: API): ReturnType<typeof useSWR<any>> {
  return useSWR<any>(
    params ? ['cfg-rq-jobs', params] : 'cfg-rq-jobs',
    () => Fetchers.getRqJobsList(params, client)
  )
}


/**
 * Get job details
 *
 * @method GET
 * @path /cfg/rq/jobs/{id}/
 */
export function useRqJobsRetrieve(id: string, client?: API): ReturnType<typeof useSWR<JobDetail>> {
  return useSWR<JobDetail>(
    ['cfg-rq-job', id],
    () => Fetchers.getRqJobsRetrieve(id, client)
  )
}


/**
 * Delete job
 *
 * @method DELETE
 * @path /cfg/rq/jobs/{id}/
 */
export function useDeleteRqJobsDestroy() {
  const { mutate } = useSWRConfig()

  return async (id: string, client?: API): Promise<JobActionResponse> => {
    const result = await Fetchers.deleteRqJobsDestroy(id, client)
    // Revalidate related queries
    mutate('cfg-rq-jobs')
    mutate('cfg-rq-job')
    return result
  }
}


/**
 * Cancel job
 *
 * @method POST
 * @path /cfg/rq/jobs/{id}/cancel/
 */
export function useCreateRqJobsCancelCreate() {
  const { mutate } = useSWRConfig()

  return async (id: string, client?: API): Promise<JobActionResponse> => {
    const result = await Fetchers.createRqJobsCancelCreate(id, client)
    // Revalidate related queries
    mutate('cfg-rq-jobs-cancel')
    return result
  }
}


/**
 * Requeue job
 *
 * @method POST
 * @path /cfg/rq/jobs/{id}/requeue/
 */
export function useCreateRqJobsRequeueCreate() {
  const { mutate } = useSWRConfig()

  return async (id: string, client?: API): Promise<JobActionResponse> => {
    const result = await Fetchers.createRqJobsRequeueCreate(id, client)
    // Revalidate related queries
    mutate('cfg-rq-jobs-requeue')
    return result
  }
}


