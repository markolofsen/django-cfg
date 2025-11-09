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
import { consola } from 'consola'
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
  try {
    return TestingActionResponseSchema.parse(response)
  } catch (error) {
    // Zod validation error - log detailed information
    consola.error('❌ Zod Validation Failed');
    consola.box({
      title: 'deleteRqTestingCleanupDestroy',
      message: `Path: /cfg/rq/testing/cleanup/\nMethod: DELETE`,
      style: {
        borderColor: 'red',
        borderStyle: 'rounded'
      }
    });

    if (error instanceof Error && 'issues' in error && Array.isArray((error as any).issues)) {
      consola.error('Validation Issues:');
      (error as any).issues.forEach((issue: any, index: number) => {
        consola.error(`  ${index + 1}. ${issue.path.join('.') || 'root'}`);
        consola.error(`     ├─ Message: ${issue.message}`);
        if (issue.expected) consola.error(`     ├─ Expected: ${issue.expected}`);
        if (issue.received) consola.error(`     └─ Received: ${issue.received}`);
      });
    }

    consola.error('Response data:', response);

    // Re-throw the error
    throw error;
  }
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
  try {
    return TestingActionResponseSchema.parse(response)
  } catch (error) {
    // Zod validation error - log detailed information
    consola.error('❌ Zod Validation Failed');
    consola.box({
      title: 'createRqTestingRunDemoCreate',
      message: `Path: /cfg/rq/testing/run-demo/\nMethod: POST`,
      style: {
        borderColor: 'red',
        borderStyle: 'rounded'
      }
    });

    if (error instanceof Error && 'issues' in error && Array.isArray((error as any).issues)) {
      consola.error('Validation Issues:');
      (error as any).issues.forEach((issue: any, index: number) => {
        consola.error(`  ${index + 1}. ${issue.path.join('.') || 'root'}`);
        consola.error(`     ├─ Message: ${issue.message}`);
        if (issue.expected) consola.error(`     ├─ Expected: ${issue.expected}`);
        if (issue.received) consola.error(`     └─ Received: ${issue.received}`);
      });
    }

    consola.error('Response data:', response);

    // Re-throw the error
    throw error;
  }
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
  try {
    return TestingActionResponseSchema.parse(response)
  } catch (error) {
    // Zod validation error - log detailed information
    consola.error('❌ Zod Validation Failed');
    consola.box({
      title: 'createRqTestingScheduleDemoCreate',
      message: `Path: /cfg/rq/testing/schedule-demo/\nMethod: POST`,
      style: {
        borderColor: 'red',
        borderStyle: 'rounded'
      }
    });

    if (error instanceof Error && 'issues' in error && Array.isArray((error as any).issues)) {
      consola.error('Validation Issues:');
      (error as any).issues.forEach((issue: any, index: number) => {
        consola.error(`  ${index + 1}. ${issue.path.join('.') || 'root'}`);
        consola.error(`     ├─ Message: ${issue.message}`);
        if (issue.expected) consola.error(`     ├─ Expected: ${issue.expected}`);
        if (issue.received) consola.error(`     └─ Received: ${issue.received}`);
      });
    }

    consola.error('Response data:', response);

    // Re-throw the error
    throw error;
  }
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
  try {
    return TestingActionResponseSchema.parse(response)
  } catch (error) {
    // Zod validation error - log detailed information
    consola.error('❌ Zod Validation Failed');
    consola.box({
      title: 'createRqTestingStressTestCreate',
      message: `Path: /cfg/rq/testing/stress-test/\nMethod: POST`,
      style: {
        borderColor: 'red',
        borderStyle: 'rounded'
      }
    });

    if (error instanceof Error && 'issues' in error && Array.isArray((error as any).issues)) {
      consola.error('Validation Issues:');
      (error as any).issues.forEach((issue: any, index: number) => {
        consola.error(`  ${index + 1}. ${issue.path.join('.') || 'root'}`);
        consola.error(`     ├─ Message: ${issue.message}`);
        if (issue.expected) consola.error(`     ├─ Expected: ${issue.expected}`);
        if (issue.received) consola.error(`     └─ Received: ${issue.received}`);
      });
    }

    consola.error('Response data:', response);

    // Re-throw the error
    throw error;
  }
}


