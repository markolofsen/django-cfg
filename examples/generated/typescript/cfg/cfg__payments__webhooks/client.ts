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
  async paymentsWebhooksRetrieve(provider: string): Promise<Models.WebhookResponse> {
    const response = await this.client.request('GET', `/payments/webhooks/${provider}/`);
    return response;
  }

  /**
   * Process Webhook
   * 
   * Process incoming webhook from payment provider
   */
  async paymentsWebhooksCreate(provider: string, data: Models.WebhookResponseRequest): Promise<Models.WebhookResponse> {
    const response = await this.client.request('POST', `/payments/webhooks/${provider}/`, { body: data });
    return response;
  }

  /**
   * Webhook Health Check
   * 
   * Check webhook service health status and recent activity metrics
   */
  async paymentsWebhooksHealthRetrieve(): Promise<Models.WebhookHealth> {
    const response = await this.client.request('GET', "/payments/webhooks/health/");
    return response;
  }

  /**
   * Supported Webhook Providers
   * 
   * Get list of supported webhook providers with configuration details
   */
  async paymentsWebhooksProvidersRetrieve(): Promise<Models.SupportedProviders> {
    const response = await this.client.request('GET', "/payments/webhooks/providers/");
    return response;
  }

  async paymentsWebhooksStatsRetrieve(days?: number): Promise<Models.WebhookStats>;
  async paymentsWebhooksStatsRetrieve(params?: { days?: number }): Promise<Models.WebhookStats>;

  /**
   * Webhook Statistics
   * 
   * Get webhook processing statistics for a given time period
   */
  async paymentsWebhooksStatsRetrieve(...args: any[]): Promise<Models.WebhookStats> {
    const isParamsObject = args.length === 1 && typeof args[0] === 'object' && args[0] !== null && !Array.isArray(args[0]);
    
    let params;
    if (isParamsObject) {
      params = args[0];
    } else {
      params = { days: args[0] };
    }
    const response = await this.client.request('GET', "/payments/webhooks/stats/", { params });
    return response;
  }

}