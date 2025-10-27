import * as Models from "./models";


/**
 * API endpoints for Dashboard - Commands.
 */
export class CfgDashboardCommands {
  private client: any;

  constructor(client: any) {
    this.client = client;
  }

  /**
   * Get all commands
   * 
   * Retrieve all available Django management commands
   */
  async dashboardApiCommandsList(): Promise<any> {
    const response = await this.client.request('GET', "/cfg/dashboard/api/commands/");
    return response;
  }

  /**
   * Get commands summary
   * 
   * Retrieve commands summary with statistics and categorization
   */
  async dashboardApiCommandsSummaryRetrieve(): Promise<Models.CommandsSummary> {
    const response = await this.client.request('GET', "/cfg/dashboard/api/commands/summary/");
    return response;
  }

}