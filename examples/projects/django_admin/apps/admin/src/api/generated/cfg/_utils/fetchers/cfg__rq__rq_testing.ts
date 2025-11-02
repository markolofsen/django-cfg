/**
 * Typed fetchers for RQ Testing
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
import { RunDemoRequestRequestSchema, type RunDemoRequestRequest } from '../schemas/RunDemoRequestRequest.schema'
import { StressTestRequestRequestSchema, type StressTestRequestRequest } from '../schemas/StressTestRequestRequest.schema'
import { TestingActionResponseSchema, type TestingActionResponse } from '../schemas/TestingActionResponse.schema'
import { getAPIInstance } from '../../api-instance'

/**
 * List test scenarios
 *
 * @method GET
 * @path /cfg/rq/testing/
 */
export async function getRqTestingList(  client?: any
): Promise<any> {
  const api = client || getAPIInstance()
  const response = await api.cfg_rq_testing.list()
  return response
}


/**
 * Cleanup test jobs
 *
 * @method DELETE
 * @path /cfg/rq/testing/cleanup/
 */
export async function deleteRqTestingCleanupDestroy(  params?: { delete_demo_jobs_only?: boolean; queue?: string; registries?: string },  client?: any
): Promise<TestingActionResponse> {
  const api = client || getAPIInstance()
  const response = await api.cfg_rq_testing.cleanupDestroy(params?.delete_demo_jobs_only, params?.queue, params?.registries)
  return TestingActionResponseSchema.parse(response)
}


/**
 * Get test results
 *
 * @method GET
 * @path /cfg/rq/testing/results/
 */
export async function getRqTestingResultsRetrieve(  params?: { queue?: string; scenario?: string },  client?: any
): Promise<any> {
  const api = client || getAPIInstance()
  const response = await api.cfg_rq_testing.resultsRetrieve(params?.queue, params?.scenario)
  return response
}


/**
 * Run demo task
 *
 * @method POST
 * @path /cfg/rq/testing/run-demo/
 */
export async function createRqTestingRunDemoCreate(  data: RunDemoRequestRequest,  client?: any
): Promise<TestingActionResponse> {
  const api = client || getAPIInstance()
  const response = await api.cfg_rq_testing.runDemoCreate(data)
  return TestingActionResponseSchema.parse(response)
}


/**
 * Schedule demo tasks
 *
 * @method POST
 * @path /cfg/rq/testing/schedule-demo/
 */
export async function createRqTestingScheduleDemoCreate(  data: any,  client?: any
): Promise<TestingActionResponse> {
  const api = client || getAPIInstance()
  const response = await api.cfg_rq_testing.scheduleDemoCreate(data)
  return TestingActionResponseSchema.parse(response)
}


/**
 * Stress test
 *
 * @method POST
 * @path /cfg/rq/testing/stress-test/
 */
export async function createRqTestingStressTestCreate(  data: StressTestRequestRequest,  client?: any
): Promise<TestingActionResponse> {
  const api = client || getAPIInstance()
  const response = await api.cfg_rq_testing.stressTestCreate(data)
  return TestingActionResponseSchema.parse(response)
}


