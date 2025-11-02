import * as Models from "./models";


/**
 * API endpoints for RQ Registries.
 */
export class CfgRqRegistries {
  private client: any;

  constructor(client: any) {
    this.client = client;
  }

  async rqJobsRegistriesDeferredList(queue?: string): Promise<any>;
  async rqJobsRegistriesDeferredList(params?: { queue?: string }): Promise<any>;

  /**
   * List deferred jobs
   * 
   * Returns list of all deferred jobs from deferred job registry.
   */
  async rqJobsRegistriesDeferredList(...args: any[]): Promise<any> {
    const isParamsObject = args.length === 1 && typeof args[0] === 'object' && args[0] !== null && !Array.isArray(args[0]);
    
    let params;
    if (isParamsObject) {
      params = args[0];
    } else {
      params = { queue: args[0] };
    }
    const response = await this.client.request('GET', "/cfg/rq/jobs/registries/deferred/", { params });
    return response;
  }

  async rqJobsRegistriesFailedList(queue?: string): Promise<any>;
  async rqJobsRegistriesFailedList(params?: { queue?: string }): Promise<any>;

  /**
   * List failed jobs
   * 
   * Returns list of all failed jobs from failed job registry.
   */
  async rqJobsRegistriesFailedList(...args: any[]): Promise<any> {
    const isParamsObject = args.length === 1 && typeof args[0] === 'object' && args[0] !== null && !Array.isArray(args[0]);
    
    let params;
    if (isParamsObject) {
      params = args[0];
    } else {
      params = { queue: args[0] };
    }
    const response = await this.client.request('GET', "/cfg/rq/jobs/registries/failed/", { params });
    return response;
  }

  async rqJobsRegistriesFailedClearCreate(queue: string): Promise<Models.JobActionResponse>;
  async rqJobsRegistriesFailedClearCreate(params: { queue: string }): Promise<Models.JobActionResponse>;

  /**
   * Clear failed jobs registry
   * 
   * Removes all jobs from the failed job registry.
   */
  async rqJobsRegistriesFailedClearCreate(...args: any[]): Promise<Models.JobActionResponse> {
    const isParamsObject = args.length === 1 && typeof args[0] === 'object' && args[0] !== null && !Array.isArray(args[0]);
    
    let params;
    if (isParamsObject) {
      params = args[0];
    } else {
      params = { queue: args[0] };
    }
    const response = await this.client.request('POST', "/cfg/rq/jobs/registries/failed/clear/", { params });
    return response;
  }

  async rqJobsRegistriesFailedRequeueAllCreate(queue: string): Promise<Models.JobActionResponse>;
  async rqJobsRegistriesFailedRequeueAllCreate(params: { queue: string }): Promise<Models.JobActionResponse>;

  /**
   * Requeue all failed jobs
   * 
   * Requeues all failed jobs in the failed job registry.
   */
  async rqJobsRegistriesFailedRequeueAllCreate(...args: any[]): Promise<Models.JobActionResponse> {
    const isParamsObject = args.length === 1 && typeof args[0] === 'object' && args[0] !== null && !Array.isArray(args[0]);
    
    let params;
    if (isParamsObject) {
      params = args[0];
    } else {
      params = { queue: args[0] };
    }
    const response = await this.client.request('POST', "/cfg/rq/jobs/registries/failed/requeue-all/", { params });
    return response;
  }

  async rqJobsRegistriesFinishedList(queue?: string): Promise<any>;
  async rqJobsRegistriesFinishedList(params?: { queue?: string }): Promise<any>;

  /**
   * List finished jobs
   * 
   * Returns list of all finished jobs from finished job registry.
   */
  async rqJobsRegistriesFinishedList(...args: any[]): Promise<any> {
    const isParamsObject = args.length === 1 && typeof args[0] === 'object' && args[0] !== null && !Array.isArray(args[0]);
    
    let params;
    if (isParamsObject) {
      params = args[0];
    } else {
      params = { queue: args[0] };
    }
    const response = await this.client.request('GET', "/cfg/rq/jobs/registries/finished/", { params });
    return response;
  }

  async rqJobsRegistriesFinishedClearCreate(queue: string): Promise<Models.JobActionResponse>;
  async rqJobsRegistriesFinishedClearCreate(params: { queue: string }): Promise<Models.JobActionResponse>;

  /**
   * Clear finished jobs registry
   * 
   * Removes all jobs from the finished job registry.
   */
  async rqJobsRegistriesFinishedClearCreate(...args: any[]): Promise<Models.JobActionResponse> {
    const isParamsObject = args.length === 1 && typeof args[0] === 'object' && args[0] !== null && !Array.isArray(args[0]);
    
    let params;
    if (isParamsObject) {
      params = args[0];
    } else {
      params = { queue: args[0] };
    }
    const response = await this.client.request('POST', "/cfg/rq/jobs/registries/finished/clear/", { params });
    return response;
  }

  async rqJobsRegistriesStartedList(queue?: string): Promise<any>;
  async rqJobsRegistriesStartedList(params?: { queue?: string }): Promise<any>;

  /**
   * List started jobs
   * 
   * Returns list of all currently running jobs from started job registry.
   */
  async rqJobsRegistriesStartedList(...args: any[]): Promise<any> {
    const isParamsObject = args.length === 1 && typeof args[0] === 'object' && args[0] !== null && !Array.isArray(args[0]);
    
    let params;
    if (isParamsObject) {
      params = args[0];
    } else {
      params = { queue: args[0] };
    }
    const response = await this.client.request('GET', "/cfg/rq/jobs/registries/started/", { params });
    return response;
  }

}