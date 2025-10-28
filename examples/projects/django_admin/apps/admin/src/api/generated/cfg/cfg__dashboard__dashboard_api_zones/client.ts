import * as Models from "./models";


/**
 * API endpoints for Dashboard - API Zones.
 */
export class CfgDashboardApiZones {
  private client: any;

  constructor(client: any) {
    this.client = client;
  }

  /**
   * Get all API zones
   * 
   * Retrieve all OpenAPI zones/groups with their configuration
   */
  async list(): Promise<any> {
    const response = await this.client.request('GET', "/cfg/dashboard/api/zones/");
    return response;
  }

  /**
   * Get zones summary
   * 
   * Retrieve zones summary with statistics
   */
  async summaryRetrieve(): Promise<Models.APIZonesSummary> {
    const response = await this.client.request('GET', "/cfg/dashboard/api/zones/summary/");
    return response;
  }

}