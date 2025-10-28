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

/**
 * API operation
 *
 * @method POST
 * @path /cfg/tasks/api/clear/
 */
export async function createTasksApiClearCreate(  data: APIResponseRequest,  client?: any
): Promise<APIResponse> {
  const api = client || getAPIInstance()
  const response = await api.cfg_tasks.apiClearCreate(data)
  return APIResponseSchema.parse(response)
}


/**
 * API operation
 *
 * @method POST
 * @path /cfg/tasks/api/clear-queues/
 */
export async function createTasksApiClearQueuesCreate(  data: APIResponseRequest,  client?: any
): Promise<APIResponse> {
  const api = client || getAPIInstance()
  const response = await api.cfg_tasks.apiClearQueuesCreate(data)
  return APIResponseSchema.parse(response)
}


/**
 * API operation
 *
 * @method POST
 * @path /cfg/tasks/api/purge-failed/
 */
export async function createTasksApiPurgeFailedCreate(  data: APIResponseRequest,  client?: any
): Promise<APIResponse> {
  const api = client || getAPIInstance()
  const response = await api.cfg_tasks.apiPurgeFailedCreate(data)
  return APIResponseSchema.parse(response)
}


/**
 * API operation
 *
 * @method POST
 * @path /cfg/tasks/api/queues/manage/
 */
export async function createTasksApiQueuesManageCreate(  data: QueueActionRequest,  client?: any
): Promise<QueueAction> {
  const api = client || getAPIInstance()
  const response = await api.cfg_tasks.apiQueuesManageCreate(data)
  return QueueActionSchema.parse(response)
}


/**
 * API operation
 *
 * @method GET
 * @path /cfg/tasks/api/queues/status/
 */
export async function getTasksApiQueuesStatusRetrieve(  client?: any
): Promise<QueueStatus> {
  const api = client || getAPIInstance()
  const response = await api.cfg_tasks.apiQueuesStatusRetrieve()
  return QueueStatusSchema.parse(response)
}


/**
 * API operation
 *
 * @method POST
 * @path /cfg/tasks/api/simulate/
 */
export async function createTasksApiSimulateCreate(  data: APIResponseRequest,  client?: any
): Promise<APIResponse> {
  const api = client || getAPIInstance()
  const response = await api.cfg_tasks.apiSimulateCreate(data)
  return APIResponseSchema.parse(response)
}


/**
 * API operation
 *
 * @method GET
 * @path /cfg/tasks/api/tasks/list/
 */
export async function getTasksApiTasksListRetrieve(  client?: any
): Promise<APIResponse> {
  const api = client || getAPIInstance()
  const response = await api.cfg_tasks.apiTasksListRetrieve()
  return APIResponseSchema.parse(response)
}


/**
 * API operation
 *
 * @method GET
 * @path /cfg/tasks/api/tasks/stats/
 */
export async function getTasksApiTasksStatsRetrieve(  client?: any
): Promise<TaskStatistics> {
  const api = client || getAPIInstance()
  const response = await api.cfg_tasks.apiTasksStatsRetrieve()
  return TaskStatisticsSchema.parse(response)
}


/**
 * API operation
 *
 * @method GET
 * @path /cfg/tasks/api/workers/list/
 */
export async function getTasksApiWorkersListRetrieve(  client?: any
): Promise<APIResponse> {
  const api = client || getAPIInstance()
  const response = await api.cfg_tasks.apiWorkersListRetrieve()
  return APIResponseSchema.parse(response)
}


/**
 * API operation
 *
 * @method POST
 * @path /cfg/tasks/api/workers/manage/
 */
export async function createTasksApiWorkersManageCreate(  data: WorkerActionRequest,  client?: any
): Promise<WorkerAction> {
  const api = client || getAPIInstance()
  const response = await api.cfg_tasks.apiWorkersManageCreate(data)
  return WorkerActionSchema.parse(response)
}


