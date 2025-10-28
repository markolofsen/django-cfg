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
   * Get command help
   * 
   * Get detailed help text for a specific Django management command
   */
  async dashboardApiCommandsHelpRetrieve(id: string): Promise<Models.CommandHelpResponse> {
    const response = await this.client.request('GET', `/cfg/dashboard/api/commands/${id}/help/`);
    return response;
  }

  /**
   * Execute command
   * 
   * Execute a Django management command and stream output in Server-Sent
   * Events format
   */
  async dashboardApiCommandsExecuteCreate(data: Models.CommandExecuteRequestRequest): Promise<any> {
    const response = await this.client.request('POST', "/cfg/dashboard/api/commands/execute/", { body: data });
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