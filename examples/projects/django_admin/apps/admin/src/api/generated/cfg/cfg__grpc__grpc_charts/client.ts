import * as Models from "./models";


/**
 * API endpoints for Grpc Charts.
 */
export class CfgGrpcCharts {
  private client: any;

  constructor(client: any) {
    this.client = client;
  }

  async dashboardRetrieve(hours?: number): Promise<Models.DashboardCharts>;
  async dashboardRetrieve(params?: { hours?: number }): Promise<Models.DashboardCharts>;

  /**
   * Get all dashboard charts data
   * 
   * Returns combined data for all charts in one request (optimized).
   */
  async dashboardRetrieve(...args: any[]): Promise<Models.DashboardCharts> {
    const isParamsObject = args.length === 1 && typeof args[0] === 'object' && args[0] !== null && !Array.isArray(args[0]);
    
    let params;
    if (isParamsObject) {
      params = args[0];
    } else {
      params = { hours: args[0] };
    }
    const response = await this.client.request('GET', "/cfg/grpc/charts/dashboard/", { params });
    return response;
  }

  async errorDistributionRetrieve(hours?: number): Promise<Models.ErrorDistributionChart>;
  async errorDistributionRetrieve(params?: { hours?: number }): Promise<Models.ErrorDistributionChart>;

  /**
   * Get error distribution chart data
   * 
   * Returns distribution of error types across services.
   */
  async errorDistributionRetrieve(...args: any[]): Promise<Models.ErrorDistributionChart> {
    const isParamsObject = args.length === 1 && typeof args[0] === 'object' && args[0] !== null && !Array.isArray(args[0]);
    
    let params;
    if (isParamsObject) {
      params = args[0];
    } else {
      params = { hours: args[0] };
    }
    const response = await this.client.request('GET', "/cfg/grpc/charts/error-distribution/", { params });
    return response;
  }

  async requestVolumeRetrieve(hours?: number): Promise<Models.RequestVolumeChart>;
  async requestVolumeRetrieve(params?: { hours?: number }): Promise<Models.RequestVolumeChart>;

  /**
   * Get request volume chart data
   * 
   * Returns time-series data showing request volume and success rates.
   */
  async requestVolumeRetrieve(...args: any[]): Promise<Models.RequestVolumeChart> {
    const isParamsObject = args.length === 1 && typeof args[0] === 'object' && args[0] !== null && !Array.isArray(args[0]);
    
    let params;
    if (isParamsObject) {
      params = args[0];
    } else {
      params = { hours: args[0] };
    }
    const response = await this.client.request('GET', "/cfg/grpc/charts/request-volume/", { params });
    return response;
  }

  async responseTimeRetrieve(hours?: number): Promise<Models.ResponseTimeChart>;
  async responseTimeRetrieve(params?: { hours?: number }): Promise<Models.ResponseTimeChart>;

  /**
   * Get response time chart data
   * 
   * Returns time-series data showing response time statistics (avg, P50,
   * P95, P99).
   */
  async responseTimeRetrieve(...args: any[]): Promise<Models.ResponseTimeChart> {
    const isParamsObject = args.length === 1 && typeof args[0] === 'object' && args[0] !== null && !Array.isArray(args[0]);
    
    let params;
    if (isParamsObject) {
      params = args[0];
    } else {
      params = { hours: args[0] };
    }
    const response = await this.client.request('GET', "/cfg/grpc/charts/response-time/", { params });
    return response;
  }

  async serverLifecycleRetrieve(hours?: number): Promise<Models.ServerLifecycleChart>;
  async serverLifecycleRetrieve(params?: { hours?: number }): Promise<Models.ServerLifecycleChart>;

  /**
   * Get server lifecycle events
   * 
   * Returns timeline of server start/stop/error events.
   */
  async serverLifecycleRetrieve(...args: any[]): Promise<Models.ServerLifecycleChart> {
    const isParamsObject = args.length === 1 && typeof args[0] === 'object' && args[0] !== null && !Array.isArray(args[0]);
    
    let params;
    if (isParamsObject) {
      params = args[0];
    } else {
      params = { hours: args[0] };
    }
    const response = await this.client.request('GET', "/cfg/grpc/charts/server-lifecycle/", { params });
    return response;
  }

  async serverUptimeRetrieve(hours?: number): Promise<Models.ServerUptimeChart>;
  async serverUptimeRetrieve(params?: { hours?: number }): Promise<Models.ServerUptimeChart>;

  /**
   * Get server uptime chart data
   * 
   * Returns time-series data showing number of running servers over time.
   */
  async serverUptimeRetrieve(...args: any[]): Promise<Models.ServerUptimeChart> {
    const isParamsObject = args.length === 1 && typeof args[0] === 'object' && args[0] !== null && !Array.isArray(args[0]);
    
    let params;
    if (isParamsObject) {
      params = args[0];
    } else {
      params = { hours: args[0] };
    }
    const response = await this.client.request('GET', "/cfg/grpc/charts/server-uptime/", { params });
    return response;
  }

  async serviceActivityRetrieve(hours?: number): Promise<Models.ServiceActivityChart>;
  async serviceActivityRetrieve(params?: { hours?: number }): Promise<Models.ServiceActivityChart>;

  /**
   * Get service activity chart data
   * 
   * Returns comparison data showing activity across all services.
   */
  async serviceActivityRetrieve(...args: any[]): Promise<Models.ServiceActivityChart> {
    const isParamsObject = args.length === 1 && typeof args[0] === 'object' && args[0] !== null && !Array.isArray(args[0]);
    
    let params;
    if (isParamsObject) {
      params = args[0];
    } else {
      params = { hours: args[0] };
    }
    const response = await this.client.request('GET', "/cfg/grpc/charts/service-activity/", { params });
    return response;
  }

}