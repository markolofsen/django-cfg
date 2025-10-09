import * as Models from "./models";


/**
 * API endpoints for Cfg Health.
 */
export class CfgHealthAPI {
  private client: any;

  constructor(client: any) {
    this.client = client;
  }

  /**
   * Return comprehensive health check data.
   */
  async cfgHealthDrfRetrieve(): Promise<Models.HealthCheck> {
    const response = await this.client.request('GET', "/cfg/health/drf/");
    return response;
  }

  /**
   * Return minimal health status.
   */
  async cfgHealthDrfQuickRetrieve(): Promise<Models.QuickHealth> {
    const response = await this.client.request('GET', "/cfg/health/drf/quick/");
    return response;
  }

}