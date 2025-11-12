import * as Models from "./models";


/**
 * API endpoints for RQ Queues.
 */
export class CfgRqQueues {
  private client: any;

  constructor(client: any) {
    this.client = client;
  }

  async list(name?: string): Promise<any>;
  async list(params?: { name?: string }): Promise<any>;

  /**
   * List all queues
   * 
   * Returns list of all configured RQ queues with statistics. Supports
   * filtering by queue name.
   */
  async list(...args: any[]): Promise<any> {
    const isParamsObject = args.length === 1 && typeof args[0] === 'object' && args[0] !== null && !Array.isArray(args[0]);
    
    let params;
    if (isParamsObject) {
      params = args[0];
    } else {
      params = { name: args[0] };
    }
    const response = await this.client.request('GET', "/cfg/rq/queues/", { params });
    return response;
  }

  /**
   * Get queue details
   * 
   * Returns detailed information about a specific queue.
   */
  async retrieve(id: string): Promise<Models.QueueDetail> {
    const response = await this.client.request('GET', `/cfg/rq/queues/${id}/`);
    return response;
  }

  /**
   * Empty queue
   * 
   * Removes all jobs from the specified queue.
   */
  async emptyCreate(id: string): Promise<any> {
    const response = await this.client.request('POST', `/cfg/rq/queues/${id}/empty/`);
    return response;
  }

  async jobsRetrieve(id: string, limit?: number, offset?: number): Promise<any>;
  async jobsRetrieve(id: string, params?: { limit?: number; offset?: number }): Promise<any>;

  /**
   * Get queue jobs
   * 
   * Returns list of job IDs in the queue.
   */
  async jobsRetrieve(...args: any[]): Promise<any> {
    const id = args[0];
    const isParamsObject = args.length === 2 && typeof args[1] === 'object' && args[1] !== null && !Array.isArray(args[1]);
    
    let params;
    if (isParamsObject) {
      params = args[1];
    } else {
      params = { limit: args[1], offset: args[2] };
    }
    const response = await this.client.request('GET', `/cfg/rq/queues/${id}/jobs/`, { params });
    return response;
  }

}