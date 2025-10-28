import * as Models from "./models";


/**
 * API endpoints for Dashboard - Activity.
 */
export class CfgDashboardActivity {
  private client: any;

  constructor(client: any) {
    this.client = client;
  }

  /**
   * Get quick actions
   * 
   * Retrieve quick action buttons for dashboard
   */
  async dashboardApiActivityActionsList(): Promise<any> {
    const response = await this.client.request('GET', "/cfg/dashboard/api/activity/actions/");
    return response;
  }

  async dashboardApiActivityRecentList(limit?: number): Promise<any>;
  async dashboardApiActivityRecentList(params?: { limit?: number }): Promise<any>;

  /**
   * Get recent activity
   * 
   * Retrieve recent system activity entries
   */
  async dashboardApiActivityRecentList(...args: any[]): Promise<any> {
    const isParamsObject = args.length === 1 && typeof args[0] === 'object' && args[0] !== null && !Array.isArray(args[0]);
    
    let params;
    if (isParamsObject) {
      params = args[0];
    } else {
      params = { limit: args[0] };
    }
    const response = await this.client.request('GET', "/cfg/dashboard/api/activity/recent/", { params });
    return response;
  }

}