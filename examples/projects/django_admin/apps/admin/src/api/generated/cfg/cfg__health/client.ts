import * as Models from "./models";


/**
 * API endpoints for Health.
 */
export class CfgHealth {
  private client: any;

  constructor(client: any) {
    this.client = client;
  }

  /**
   * Return comprehensive health check data.
   */
  async drfRetrieve(): Promise<Models.HealthCheck> {
    const response = await this.client.request('GET', "/cfg/health/drf/");
    return response;
  }

  /**
   * Return minimal health status.
   */
  async drfQuickRetrieve(): Promise<Models.QuickHealth> {
    const response = await this.client.request('GET', "/cfg/health/drf/quick/");
    return response;
  }

}