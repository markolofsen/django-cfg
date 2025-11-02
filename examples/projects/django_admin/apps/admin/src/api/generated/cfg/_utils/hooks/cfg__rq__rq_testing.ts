/**
 * SWR Hooks for RQ Testing
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
import * as Fetchers from '../fetchers/cfg__rq__rq_testing'
import type { API } from '../../index'
import type { RunDemoRequestRequest } from '../schemas/RunDemoRequestRequest.schema'
import type { StressTestRequestRequest } from '../schemas/StressTestRequestRequest.schema'
import type { TestingActionResponse } from '../schemas/TestingActionResponse.schema'

/**
 * List test scenarios
 *
 * @method GET
 * @path /cfg/rq/testing/
 */
export function useRqTestingList(client?: API): ReturnType<typeof useSWR<any>> {
  return useSWR<any>(
    'cfg-rq-testing',
    () => Fetchers.getRqTestingList(client)
  )
}


/**
 * Cleanup test jobs
 *
 * @method DELETE
 * @path /cfg/rq/testing/cleanup/
 */
export function useDeleteRqTestingCleanupDestroy() {
  const { mutate } = useSWRConfig()

  return async (params?: { delete_demo_jobs_only?: boolean; queue?: string; registries?: string }, client?: API): Promise<TestingActionResponse> => {
    const result = await Fetchers.deleteRqTestingCleanupDestroy(params, client)
    // Revalidate related queries
    mutate('cfg-rq-testing-cleanup')
    return result
  }
}


/**
 * Get test results
 *
 * @method GET
 * @path /cfg/rq/testing/results/
 */
export function useRqTestingResultsRetrieve(params?: { queue?: string; scenario?: string }, client?: API): ReturnType<typeof useSWR<any>> {
  return useSWR<any>(
    params ? ['cfg-rq-testing-result', params] : 'cfg-rq-testing-result',
    () => Fetchers.getRqTestingResultsRetrieve(params, client)
  )
}


/**
 * Run demo task
 *
 * @method POST
 * @path /cfg/rq/testing/run-demo/
 */
export function useCreateRqTestingRunDemoCreate() {
  const { mutate } = useSWRConfig()

  return async (data: RunDemoRequestRequest, client?: API): Promise<TestingActionResponse> => {
    const result = await Fetchers.createRqTestingRunDemoCreate(data, client)
    // Revalidate related queries
    mutate('cfg-rq-testing-run-demo')
    return result
  }
}


/**
 * Schedule demo tasks
 *
 * @method POST
 * @path /cfg/rq/testing/schedule-demo/
 */
export function useCreateRqTestingScheduleDemoCreate() {
  const { mutate } = useSWRConfig()

  return async (data: any, client?: API): Promise<TestingActionResponse> => {
    const result = await Fetchers.createRqTestingScheduleDemoCreate(data, client)
    // Revalidate related queries
    mutate('cfg-rq-testing-schedule-demo')
    return result
  }
}


/**
 * Stress test
 *
 * @method POST
 * @path /cfg/rq/testing/stress-test/
 */
export function useCreateRqTestingStressTestCreate() {
  const { mutate } = useSWRConfig()

  return async (data: StressTestRequestRequest, client?: API): Promise<TestingActionResponse> => {
    const result = await Fetchers.createRqTestingStressTestCreate(data, client)
    // Revalidate related queries
    mutate('cfg-rq-testing-stress-test')
    return result
  }
}


