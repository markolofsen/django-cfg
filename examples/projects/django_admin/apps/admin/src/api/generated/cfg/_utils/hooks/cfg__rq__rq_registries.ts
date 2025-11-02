/**
 * SWR Hooks for RQ Registries
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
import * as Fetchers from '../fetchers/cfg__rq__rq_registries'
import type { API } from '../../index'
import type { JobActionResponse } from '../schemas/JobActionResponse.schema'

/**
 * List deferred jobs
 *
 * @method GET
 * @path /cfg/rq/jobs/registries/deferred/
 */
export function useRqJobsRegistriesDeferredList(params?: { queue?: string }, client?: API): ReturnType<typeof useSWR<any>> {
  return useSWR<any>(
    params ? ['cfg-rq-jobs-registries-deferred', params] : 'cfg-rq-jobs-registries-deferred',
    () => Fetchers.getRqJobsRegistriesDeferredList(params, client)
  )
}


/**
 * List failed jobs
 *
 * @method GET
 * @path /cfg/rq/jobs/registries/failed/
 */
export function useRqJobsRegistriesFailedList(params?: { queue?: string }, client?: API): ReturnType<typeof useSWR<any>> {
  return useSWR<any>(
    params ? ['cfg-rq-jobs-registries-failed', params] : 'cfg-rq-jobs-registries-failed',
    () => Fetchers.getRqJobsRegistriesFailedList(params, client)
  )
}


/**
 * Clear failed jobs registry
 *
 * @method POST
 * @path /cfg/rq/jobs/registries/failed/clear/
 */
export function useCreateRqJobsRegistriesFailedClearCreate() {
  const { mutate } = useSWRConfig()

  return async (params: { queue: string }, client?: API): Promise<JobActionResponse> => {
    const result = await Fetchers.createRqJobsRegistriesFailedClearCreate(params, client)
    // Revalidate related queries
    mutate('cfg-rq-jobs-registries-failed-clear')
    return result
  }
}


/**
 * Requeue all failed jobs
 *
 * @method POST
 * @path /cfg/rq/jobs/registries/failed/requeue-all/
 */
export function useCreateRqJobsRegistriesFailedRequeueAllCreate() {
  const { mutate } = useSWRConfig()

  return async (params: { queue: string }, client?: API): Promise<JobActionResponse> => {
    const result = await Fetchers.createRqJobsRegistriesFailedRequeueAllCreate(params, client)
    // Revalidate related queries
    mutate('cfg-rq-jobs-registries-failed-requeue-all')
    return result
  }
}


/**
 * List finished jobs
 *
 * @method GET
 * @path /cfg/rq/jobs/registries/finished/
 */
export function useRqJobsRegistriesFinishedList(params?: { queue?: string }, client?: API): ReturnType<typeof useSWR<any>> {
  return useSWR<any>(
    params ? ['cfg-rq-jobs-registries-finished', params] : 'cfg-rq-jobs-registries-finished',
    () => Fetchers.getRqJobsRegistriesFinishedList(params, client)
  )
}


/**
 * Clear finished jobs registry
 *
 * @method POST
 * @path /cfg/rq/jobs/registries/finished/clear/
 */
export function useCreateRqJobsRegistriesFinishedClearCreate() {
  const { mutate } = useSWRConfig()

  return async (params: { queue: string }, client?: API): Promise<JobActionResponse> => {
    const result = await Fetchers.createRqJobsRegistriesFinishedClearCreate(params, client)
    // Revalidate related queries
    mutate('cfg-rq-jobs-registries-finished-clear')
    return result
  }
}


/**
 * List started jobs
 *
 * @method GET
 * @path /cfg/rq/jobs/registries/started/
 */
export function useRqJobsRegistriesStartedList(params?: { queue?: string }, client?: API): ReturnType<typeof useSWR<any>> {
  return useSWR<any>(
    params ? ['cfg-rq-jobs-registries-started', params] : 'cfg-rq-jobs-registries-started',
    () => Fetchers.getRqJobsRegistriesStartedList(params, client)
  )
}


