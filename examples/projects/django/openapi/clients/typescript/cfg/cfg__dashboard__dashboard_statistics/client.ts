import * as Models from "./models";


/**
 * API endpoints for Dashboard - Statistics.
 */
export class CfgDashboardStatistics {
  private client: any;

  constructor(client: any) {
    this.client = client;
  }

  /**
   * Get application statistics
   * 
   * Retrieve statistics for all enabled django-cfg applications
   */
  async dashboardApiStatisticsAppsList(): Promise<any> {
    const response = await this.client.request('GET', "/cfg/dashboard/api/statistics/apps/");
    return response;
  }

  /**
   * Get statistics cards
   * 
   * Retrieve dashboard statistics cards with key metrics
   */
  async dashboardApiStatisticsCardsList(): Promise<any> {
    const response = await this.client.request('GET', "/cfg/dashboard/api/statistics/cards/");
    return response;
  }

  /**
   * Get user statistics
   * 
   * Retrieve user-related statistics
   */
  async dashboardApiStatisticsUsersRetrieve(): Promise<Models.UserStatistics> {
    const response = await this.client.request('GET', "/cfg/dashboard/api/statistics/users/");
    return response;
  }

}