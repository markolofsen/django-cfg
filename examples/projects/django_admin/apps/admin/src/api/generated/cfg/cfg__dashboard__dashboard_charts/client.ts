import * as Models from "./models";


/**
 * API endpoints for Dashboard - Charts.
 */
export class CfgDashboardCharts {
  private client: any;

  constructor(client: any) {
    this.client = client;
  }

  async dashboardApiChartsActivityRetrieve(days?: number): Promise<Models.ChartData>;
  async dashboardApiChartsActivityRetrieve(params?: { days?: number }): Promise<Models.ChartData>;

  /**
   * Get user activity chart
   * 
   * Retrieve user activity data for chart visualization
   */
  async dashboardApiChartsActivityRetrieve(...args: any[]): Promise<Models.ChartData> {
    const isParamsObject = args.length === 1 && typeof args[0] === 'object' && args[0] !== null && !Array.isArray(args[0]);
    
    let params;
    if (isParamsObject) {
      params = args[0];
    } else {
      params = { days: args[0] };
    }
    const response = await this.client.request('GET', "/cfg/dashboard/api/charts/activity/", { params });
    return response;
  }

  async dashboardApiChartsRecentUsersList(limit?: number): Promise<any>;
  async dashboardApiChartsRecentUsersList(params?: { limit?: number }): Promise<any>;

  /**
   * Get recent users
   * 
   * Retrieve list of recently registered users
   */
  async dashboardApiChartsRecentUsersList(...args: any[]): Promise<any> {
    const isParamsObject = args.length === 1 && typeof args[0] === 'object' && args[0] !== null && !Array.isArray(args[0]);
    
    let params;
    if (isParamsObject) {
      params = args[0];
    } else {
      params = { limit: args[0] };
    }
    const response = await this.client.request('GET', "/cfg/dashboard/api/charts/recent-users/", { params });
    return response;
  }

  async dashboardApiChartsRegistrationsRetrieve(days?: number): Promise<Models.ChartData>;
  async dashboardApiChartsRegistrationsRetrieve(params?: { days?: number }): Promise<Models.ChartData>;

  /**
   * Get user registration chart
   * 
   * Retrieve user registration data for chart visualization
   */
  async dashboardApiChartsRegistrationsRetrieve(...args: any[]): Promise<Models.ChartData> {
    const isParamsObject = args.length === 1 && typeof args[0] === 'object' && args[0] !== null && !Array.isArray(args[0]);
    
    let params;
    if (isParamsObject) {
      params = args[0];
    } else {
      params = { days: args[0] };
    }
    const response = await this.client.request('GET', "/cfg/dashboard/api/charts/registrations/", { params });
    return response;
  }

  async dashboardApiChartsTrackerList(weeks?: number): Promise<any>;
  async dashboardApiChartsTrackerList(params?: { weeks?: number }): Promise<any>;

  /**
   * Get activity tracker
   * 
   * Retrieve activity tracker data (GitHub-style contribution graph)
   */
  async dashboardApiChartsTrackerList(...args: any[]): Promise<any> {
    const isParamsObject = args.length === 1 && typeof args[0] === 'object' && args[0] !== null && !Array.isArray(args[0]);
    
    let params;
    if (isParamsObject) {
      params = args[0];
    } else {
      params = { weeks: args[0] };
    }
    const response = await this.client.request('GET', "/cfg/dashboard/api/charts/tracker/", { params });
    return response;
  }

}