import * as Models from "./models";


/**
 * API endpoints for Dashboard - System.
 */
export class CfgDashboardSystem {
  private client: any;

  constructor(client: any) {
    this.client = client;
  }

  /**
   * Get system health status
   * 
   * Retrieve overall system health including all component checks
   */
  async dashboardApiSystemHealthRetrieve(): Promise<Models.SystemHealth> {
    const response = await this.client.request('GET', "/cfg/dashboard/api/system/health/");
    return response;
  }

  /**
   * Get system metrics
   * 
   * Retrieve system performance metrics (CPU, memory, disk, etc.)
   */
  async dashboardApiSystemMetricsRetrieve(): Promise<Models.SystemMetrics> {
    const response = await this.client.request('GET', "/cfg/dashboard/api/system/metrics/");
    return response;
  }

}