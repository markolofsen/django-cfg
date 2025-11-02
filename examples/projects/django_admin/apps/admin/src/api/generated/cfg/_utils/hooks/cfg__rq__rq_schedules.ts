/**
 * SWR Hooks for RQ Schedules
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
import * as Fetchers from '../fetchers/cfg__rq__rq_schedules'
import type { API } from '../../index'
import type { ScheduleActionResponse } from '../schemas/ScheduleActionResponse.schema'
import type { ScheduleCreateRequest } from '../schemas/ScheduleCreateRequest.schema'
import type { ScheduledJob } from '../schemas/ScheduledJob.schema'

/**
 * List scheduled jobs
 *
 * @method GET
 * @path /cfg/rq/schedules/
 */
export function useRqSchedulesList(params?: { queue?: string }, client?: API): ReturnType<typeof useSWR<any>> {
  return useSWR<any>(
    params ? ['cfg-rq-schedules', params] : 'cfg-rq-schedules',
    () => Fetchers.getRqSchedulesList(params, client)
  )
}


/**
 * Create scheduled job
 *
 * @method POST
 * @path /cfg/rq/schedules/
 */
export function useCreateRqSchedulesCreate() {
  const { mutate } = useSWRConfig()

  return async (data: ScheduleCreateRequest, client?: API): Promise<ScheduleActionResponse> => {
    const result = await Fetchers.createRqSchedulesCreate(data, client)
    // Revalidate related queries
    mutate('cfg-rq-schedules')
    return result
  }
}


/**
 * Get scheduled job details
 *
 * @method GET
 * @path /cfg/rq/schedules/{id}/
 */
export function useRqSchedulesRetrieve(id: string, pk: string, params?: { queue?: string }, client?: API): ReturnType<typeof useSWR<ScheduledJob>> {
  return useSWR<ScheduledJob>(
    ['cfg-rq-schedule', id],
    () => Fetchers.getRqSchedulesRetrieve(id, pk, params, client)
  )
}


/**
 * Cancel scheduled job
 *
 * @method DELETE
 * @path /cfg/rq/schedules/{id}/
 */
export function useDeleteRqSchedulesDestroy() {
  const { mutate } = useSWRConfig()

  return async (id: string, pk: string, params?: { queue?: string }, client?: API): Promise<ScheduleActionResponse> => {
    const result = await Fetchers.deleteRqSchedulesDestroy(id, pk, params, client)
    // Revalidate related queries
    mutate('cfg-rq-schedules')
    mutate('cfg-rq-schedule')
    return result
  }
}


