/**
 * Typed fetchers for Tasks
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
import { APIResponseSchema, type APIResponse } from '../schemas/APIResponse.schema'
import { APIResponseRequestSchema, type APIResponseRequest } from '../schemas/APIResponseRequest.schema'
import { QueueActionSchema, type QueueAction } from '../schemas/QueueAction.schema'
import { QueueActionRequestSchema, type QueueActionRequest } from '../schemas/QueueActionRequest.schema'
import { QueueStatusSchema, type QueueStatus } from '../schemas/QueueStatus.schema'
import { TaskStatisticsSchema, type TaskStatistics } from '../schemas/TaskStatistics.schema'
import { WorkerActionSchema, type WorkerAction } from '../schemas/WorkerAction.schema'
import { WorkerActionRequestSchema, type WorkerActionRequest } from '../schemas/WorkerActionRequest.schema'
import { getAPIInstance } from '../../api-instance'
import type { API } from '../../index'

/**
 * createTasksApiClear
 *
 * Clear all test data from Redis.
 *
 * @method POST
 * @path /tasks/api/clear/
 */
export async function createTasksApiClear(
  data: APIResponseRequest,
  client?: API
): Promise<APIResponse> {
  const api = client || getAPIInstance()

  const response = await api.cfg_tasks.apiClearCreate(data)
  return APIResponseSchema.parse(response)
}

/**
 * createTasksApiClearQueues
 *
 * Clear all tasks from all Dramatiq queues.
 *
 * @method POST
 * @path /tasks/api/clear-queues/
 */
export async function createTasksApiClearQueues(
  data: APIResponseRequest,
  client?: API
): Promise<APIResponse> {
  const api = client || getAPIInstance()

  const response = await api.cfg_tasks.apiClearQueuesCreate(data)
  return APIResponseSchema.parse(response)
}

/**
 * createTasksApiPurgeFailed
 *
 * Purge all failed tasks from queues.
 *
 * @method POST
 * @path /tasks/api/purge-failed/
 */
export async function createTasksApiPurgeFailed(
  data: APIResponseRequest,
  client?: API
): Promise<APIResponse> {
  const api = client || getAPIInstance()

  const response = await api.cfg_tasks.apiPurgeFailedCreate(data)
  return APIResponseSchema.parse(response)
}

/**
 * createTasksApiQueuesManage
 *
 * Manage queue operations (clear, purge, etc.).
 *
 * @method POST
 * @path /tasks/api/queues/manage/
 */
export async function createTasksApiQueuesManage(
  data: QueueActionRequest,
  client?: API
): Promise<QueueAction> {
  const api = client || getAPIInstance()

  const response = await api.cfg_tasks.apiQueuesManageCreate(data)
  return QueueActionSchema.parse(response)
}

/**
 * getTasksApiQueuesStatu
 *
 * Get current status of all queues.
 *
 * @method GET
 * @path /tasks/api/queues/status/
 */
export async function getTasksApiQueuesStatu(
  client?: API
): Promise<QueueStatus> {
  const api = client || getAPIInstance()

  const response = await api.cfg_tasks.apiQueuesStatusRetrieve()
  return QueueStatusSchema.parse(response)
}

/**
 * createTasksApiSimulate
 *
 * Simulate test data for dashboard testing.
 *
 * @method POST
 * @path /tasks/api/simulate/
 */
export async function createTasksApiSimulate(
  data: APIResponseRequest,
  client?: API
): Promise<APIResponse> {
  const api = client || getAPIInstance()

  const response = await api.cfg_tasks.apiSimulateCreate(data)
  return APIResponseSchema.parse(response)
}

/**
 * getTasksApiTasksList
 *
 * Get paginated task list with filtering.
 *
 * @method GET
 * @path /tasks/api/tasks/list/
 */
export async function getTasksApiTasksList(
  client?: API
): Promise<APIResponse> {
  const api = client || getAPIInstance()

  const response = await api.cfg_tasks.apiTasksListRetrieve()
  return APIResponseSchema.parse(response)
}

/**
 * getTasksApiTasksStat
 *
 * Get task execution statistics.
 *
 * @method GET
 * @path /tasks/api/tasks/stats/
 */
export async function getTasksApiTasksStat(
  client?: API
): Promise<TaskStatistics> {
  const api = client || getAPIInstance()

  const response = await api.cfg_tasks.apiTasksStatsRetrieve()
  return TaskStatisticsSchema.parse(response)
}

/**
 * getTasksApiWorkersList
 *
 * Get detailed list of workers.
 *
 * @method GET
 * @path /tasks/api/workers/list/
 */
export async function getTasksApiWorkersList(
  client?: API
): Promise<APIResponse> {
  const api = client || getAPIInstance()

  const response = await api.cfg_tasks.apiWorkersListRetrieve()
  return APIResponseSchema.parse(response)
}

/**
 * createTasksApiWorkersManage
 *
 * Manage worker operations.
 *
 * @method POST
 * @path /tasks/api/workers/manage/
 */
export async function createTasksApiWorkersManage(
  data: WorkerActionRequest,
  client?: API
): Promise<WorkerAction> {
  const api = client || getAPIInstance()

  const response = await api.cfg_tasks.apiWorkersManageCreate(data)
  return WorkerActionSchema.parse(response)
}

