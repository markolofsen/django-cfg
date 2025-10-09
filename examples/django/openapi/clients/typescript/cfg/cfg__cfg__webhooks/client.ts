import * as Models from "./models";


/**
 * API endpoints for Webhooks.
 */
export class CfgWebhooksAPI {
  private client: any;

  constructor(client: any) {
    this.client = client;
  }

  /**
   * Webhook Endpoint Info
   * 
   * Get webhook endpoint information for debugging and configuration
   */
  async cfgPaymentsWebhooksRetrieve(provider: string): Promise<Models.WebhookResponse> {
    const response = await this.client.request('GET', `/cfg/payments/webhooks/${provider}/`);
    return response;
  }

  /**
   * Process Webhook
   * 
   * Process incoming webhook from payment provider
   */
  async cfgPaymentsWebhooksCreate(provider: string, data: Models.WebhookResponseRequest): Promise<Models.WebhookResponse> {
    const response = await this.client.request('POST', `/cfg/payments/webhooks/${provider}/`, { body: data });
    return response;
  }

  /**
   * Webhook Health Check
   * 
   * Check webhook service health status and recent activity metrics
   */
  async cfgPaymentsWebhooksHealthRetrieve(): Promise<Models.WebhookHealth> {
    const response = await this.client.request('GET', "/cfg/payments/webhooks/health/");
    return response;
  }

  /**
   * Supported Webhook Providers
   * 
   * Get list of supported webhook providers with configuration details
   */
  async cfgPaymentsWebhooksProvidersRetrieve(): Promise<Models.SupportedProviders> {
    const response = await this.client.request('GET', "/cfg/payments/webhooks/providers/");
    return response;
  }

  async cfgPaymentsWebhooksStatsRetrieve(days?: number): Promise<Models.WebhookStats>;
  async cfgPaymentsWebhooksStatsRetrieve(params?: { days?: number }): Promise<Models.WebhookStats>;

  /**
   * Webhook Statistics
   * 
   * Get webhook processing statistics for a given time period
   */
  async cfgPaymentsWebhooksStatsRetrieve(...args: any[]): Promise<Models.WebhookStats> {
    const isParamsObject = args.length === 1 && typeof args[0] === 'object' && args[0] !== null && !Array.isArray(args[0]);
    
    let params;
    if (isParamsObject) {
      params = args[0];
    } else {
      params = { days: args[0] };
    }
    const response = await this.client.request('GET', "/cfg/payments/webhooks/stats/", { params });
    return response;
  }

}