import * as Models from "./models";


/**
 * API endpoints for RQ Testing.
 */
export class CfgRqTesting {
  private client: any;

  constructor(client: any) {
    this.client = client;
  }

  /**
   * List test scenarios
   * 
   * Returns list of all available test scenarios with metadata.
   */
  async list(): Promise<any> {
    const response = await this.client.request('GET', "/cfg/rq/testing/");
    return response;
  }

  async cleanupDestroy(delete_demo_jobs_only?: boolean, queue?: string, registries?: string): Promise<Models.TestingActionResponse>;
  async cleanupDestroy(params?: { delete_demo_jobs_only?: boolean; queue?: string; registries?: string }): Promise<Models.TestingActionResponse>;

  /**
   * Cleanup test jobs
   * 
   * Clean demo jobs from registries.
   */
  async cleanupDestroy(...args: any[]): Promise<Models.TestingActionResponse> {
    const isParamsObject = args.length === 1 && typeof args[0] === 'object' && args[0] !== null && !Array.isArray(args[0]);
    
    let params;
    if (isParamsObject) {
      params = args[0];
    } else {
      params = { delete_demo_jobs_only: args[0], queue: args[1], registries: args[2] };
    }
    const response = await this.client.request('DELETE', "/cfg/rq/testing/cleanup/", { params });
    return response;
  }

  async resultsRetrieve(queue?: string, scenario?: string): Promise<any>;
  async resultsRetrieve(params?: { queue?: string; scenario?: string }): Promise<any>;

  /**
   * Get test results
   * 
   * Get aggregated results of test jobs execution.
   */
  async resultsRetrieve(...args: any[]): Promise<any> {
    const isParamsObject = args.length === 1 && typeof args[0] === 'object' && args[0] !== null && !Array.isArray(args[0]);
    
    let params;
    if (isParamsObject) {
      params = args[0];
    } else {
      params = { queue: args[0], scenario: args[1] };
    }
    const response = await this.client.request('GET', "/cfg/rq/testing/results/", { params });
    return response;
  }

  /**
   * Run demo task
   * 
   * Enqueue a single demo task for testing.
   */
  async runDemoCreate(data: Models.RunDemoRequestRequest): Promise<Models.TestingActionResponse> {
    const response = await this.client.request('POST', "/cfg/rq/testing/run-demo/", { body: data });
    return response;
  }

  /**
   * Schedule demo tasks
   * 
   * Register demo scheduled tasks using rq-scheduler.
   */
  async scheduleDemoCreate(data: any): Promise<Models.TestingActionResponse> {
    const response = await this.client.request('POST', "/cfg/rq/testing/schedule-demo/", { body: data });
    return response;
  }

  /**
   * Stress test
   * 
   * Generate N jobs for load testing and performance benchmarking.
   */
  async stressTestCreate(data: Models.StressTestRequestRequest): Promise<Models.TestingActionResponse> {
    const response = await this.client.request('POST', "/cfg/rq/testing/stress-test/", { body: data });
    return response;
  }

}