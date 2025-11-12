import * as Models from "./models";


/**
 * API endpoints for Dashboard - Overview.
 */
export class CfgDashboardOverview {
  private client: any;

  constructor(client: any) {
    this.client = client;
  }

  /**
   * Get dashboard overview
   * 
   * Retrieve complete dashboard data including stats, health, actions, and
   * metrics
   */
  async dashboardApiOverviewOverviewRetrieve(): Promise<Models.DashboardOverview> {
    const response = await this.client.request('GET', "/cfg/dashboard/api/overview/overview/");
    return response;
  }

}