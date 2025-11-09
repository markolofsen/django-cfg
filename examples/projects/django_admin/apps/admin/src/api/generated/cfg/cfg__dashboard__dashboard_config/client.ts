import * as Models from "./models";


/**
 * API endpoints for Dashboard - Config.
 */
export class CfgDashboardConfig {
  private client: any;

  constructor(client: any) {
    this.client = client;
  }

  /**
   * Get configuration data
   * 
   * Retrieve user's DjangoConfig settings and complete Django settings
   * (sanitized)
   */
  async dashboardApiConfigConfigRetrieve(): Promise<Models.ConfigData> {
    const response = await this.client.request('GET', "/cfg/dashboard/api/config/config/");
    return response;
  }

}