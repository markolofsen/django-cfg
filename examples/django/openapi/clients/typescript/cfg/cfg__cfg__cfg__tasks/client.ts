import * as Models from "./models";


/**
 * API endpoints for Cfg Tasks.
 */
export class CfgTasksAPI {
  private client: any;

  constructor(client: any) {
    this.client = client;
  }

  /**
   * Clear all test data from Redis.
   */
  async cfgTasksApiClearCreate(data: Models.APIResponseRequest): Promise<Models.APIResponse> {
    const response = await this.client.request('POST', "/cfg/tasks/api/clear/", { body: data });
    return response;
  }

  /**
   * Clear all tasks from all Dramatiq queues.
   */
  async cfgTasksApiClearQueuesCreate(data: Models.APIResponseRequest): Promise<Models.APIResponse> {
    const response = await this.client.request('POST', "/cfg/tasks/api/clear-queues/", { body: data });
    return response;
  }

  /**
   * Purge all failed tasks from queues.
   */
  async cfgTasksApiPurgeFailedCreate(data: Models.APIResponseRequest): Promise<Models.APIResponse> {
    const response = await this.client.request('POST', "/cfg/tasks/api/purge-failed/", { body: data });
    return response;
  }

  /**
   * Manage queue operations (clear, purge, etc.).
   */
  async cfgTasksApiQueuesManageCreate(data: Models.QueueActionRequest): Promise<Models.QueueAction> {
    const response = await this.client.request('POST', "/cfg/tasks/api/queues/manage/", { body: data });
    return response;
  }

  /**
   * Get current status of all queues.
   */
  async cfgTasksApiQueuesStatusRetrieve(): Promise<Models.QueueStatus> {
    const response = await this.client.request('GET', "/cfg/tasks/api/queues/status/");
    return response;
  }

  /**
   * Simulate test data for dashboard testing.
   */
  async cfgTasksApiSimulateCreate(data: Models.APIResponseRequest): Promise<Models.APIResponse> {
    const response = await this.client.request('POST', "/cfg/tasks/api/simulate/", { body: data });
    return response;
  }

  /**
   * Get paginated task list with filtering.
   */
  async cfgTasksApiTasksListRetrieve(): Promise<Models.APIResponse> {
    const response = await this.client.request('GET', "/cfg/tasks/api/tasks/list/");
    return response;
  }

  /**
   * Get task execution statistics.
   */
  async cfgTasksApiTasksStatsRetrieve(): Promise<Models.TaskStatistics> {
    const response = await this.client.request('GET', "/cfg/tasks/api/tasks/stats/");
    return response;
  }

  /**
   * Get detailed list of workers.
   */
  async cfgTasksApiWorkersListRetrieve(): Promise<Models.APIResponse> {
    const response = await this.client.request('GET', "/cfg/tasks/api/workers/list/");
    return response;
  }

  /**
   * Manage worker operations.
   */
  async cfgTasksApiWorkersManageCreate(data: Models.WorkerActionRequest): Promise<Models.WorkerAction> {
    const response = await this.client.request('POST', "/cfg/tasks/api/workers/manage/", { body: data });
    return response;
  }

}