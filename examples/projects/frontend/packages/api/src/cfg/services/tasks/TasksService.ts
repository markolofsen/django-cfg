/**
 * Tasks Service
 *
 * Manages background tasks, queues, and workers
 */

import { BaseClient } from '../../BaseClient';
import { APIError, CfgTasksTypes } from '../../generated';

export class TasksService extends BaseClient {
  /**
   * Get queue status
   */
  static async getQueuesStatus(): Promise<{
    success: boolean;
    status?: CfgTasksTypes.QueueStatus;
    error?: string;
  }> {
    try {
      const status = await this.api.cfg_tasks.apiQueuesStatusRetrieve();
      return { success: true, status };
    } catch (error) {
      if (error instanceof APIError) {
        return { success: false, error: error.errorMessage };
      }
      return { success: false, error: 'Network error' };
    }
  }

  /**
   * Manage queue operations
   */
  static async manageQueue(
    data: CfgTasksTypes.QueueActionRequest
  ): Promise<{
    success: boolean;
    result?: CfgTasksTypes.QueueAction;
    error?: string;
  }> {
    try {
      const result = await this.api.cfg_tasks.apiQueuesManageCreate(data);
      return { success: true, result };
    } catch (error) {
      if (error instanceof APIError) {
        return { success: false, error: error.errorMessage };
      }
      return { success: false, error: 'Network error' };
    }
  }

  /**
   * Clear all queues
   */
  static async clearQueues(
    data: CfgTasksTypes.APIResponseRequest
  ): Promise<{
    success: boolean;
    response?: CfgTasksTypes.APIResponse;
    error?: string;
  }> {
    try {
      const response = await this.api.cfg_tasks.apiClearQueuesCreate(data);
      return { success: true, response };
    } catch (error) {
      if (error instanceof APIError) {
        return { success: false, error: error.errorMessage };
      }
      return { success: false, error: 'Network error' };
    }
  }

  /**
   * Purge failed tasks
   */
  static async purgeFailed(
    data: CfgTasksTypes.APIResponseRequest
  ): Promise<{
    success: boolean;
    response?: CfgTasksTypes.APIResponse;
    error?: string;
  }> {
    try {
      const response = await this.api.cfg_tasks.apiPurgeFailedCreate(data);
      return { success: true, response };
    } catch (error) {
      if (error instanceof APIError) {
        return { success: false, error: error.errorMessage };
      }
      return { success: false, error: 'Network error' };
    }
  }

  /**
   * Get task statistics
   */
  static async getTaskStats(): Promise<{
    success: boolean;
    stats?: CfgTasksTypes.TaskStatistics;
    error?: string;
  }> {
    try {
      const stats = await this.api.cfg_tasks.apiTasksStatsRetrieve();
      return { success: true, stats };
    } catch (error) {
      if (error instanceof APIError) {
        return { success: false, error: error.errorMessage };
      }
      return { success: false, error: 'Network error' };
    }
  }

  /**
   * Get tasks list
   */
  static async getTasksList(): Promise<{
    success: boolean;
    tasks?: CfgTasksTypes.APIResponse;
    error?: string;
  }> {
    try {
      const tasks = await this.api.cfg_tasks.apiTasksListRetrieve();
      return { success: true, tasks };
    } catch (error) {
      if (error instanceof APIError) {
        return { success: false, error: error.errorMessage };
      }
      return { success: false, error: 'Network error' };
    }
  }

  /**
   * Get workers list
   */
  static async getWorkersList(): Promise<{
    success: boolean;
    workers?: CfgTasksTypes.APIResponse;
    error?: string;
  }> {
    try {
      const workers = await this.api.cfg_tasks.apiWorkersListRetrieve();
      return { success: true, workers };
    } catch (error) {
      if (error instanceof APIError) {
        return { success: false, error: error.errorMessage };
      }
      return { success: false, error: 'Network error' };
    }
  }

  /**
   * Manage worker operations
   */
  static async manageWorker(
    data: CfgTasksTypes.WorkerActionRequest
  ): Promise<{
    success: boolean;
    result?: CfgTasksTypes.WorkerAction;
    error?: string;
  }> {
    try {
      const result = await this.api.cfg_tasks.apiWorkersManageCreate(data);
      return { success: true, result };
    } catch (error) {
      if (error instanceof APIError) {
        return { success: false, error: error.errorMessage };
      }
      return { success: false, error: 'Network error' };
    }
  }
}
