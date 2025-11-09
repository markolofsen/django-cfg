import * as Models from "./models";


/**
 * API endpoints for RQ Workers.
 */
export class CfgRqWorkers {
  private client: any;

  constructor(client: any) {
    this.client = client;
  }

  async list(queue?: string, state?: string): Promise<any>;
  async list(params?: { queue?: string; state?: string }): Promise<any>;

  /**
   * List all workers
   * 
   * Returns list of all RQ workers with their current state. Supports
   * filtering by state and queue.
   */
  async list(...args: any[]): Promise<any> {
    const isParamsObject = args.length === 1 && typeof args[0] === 'object' && args[0] !== null && !Array.isArray(args[0]);
    
    let params;
    if (isParamsObject) {
      params = args[0];
    } else {
      params = { queue: args[0], state: args[1] };
    }
    const response = await this.client.request('GET', "/cfg/rq/workers/", { params });
    return response;
  }

  /**
   * Get worker statistics
   * 
   * Returns aggregated statistics for all workers.
   */
  async statsRetrieve(): Promise<Models.WorkerStats> {
    const response = await this.client.request('GET', "/cfg/rq/workers/stats/");
    return response;
  }

}