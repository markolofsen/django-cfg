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
  const response = await this.client.request<Models.WebhookResponse>('GET', `/payments/webhooks/${provider}/`);
  return response;
}

  /**
 * Process Webhook
 * 
 * Process incoming webhook from payment provider
 */
async paymentsWebhooksCreate(provider: string, data: Models.WebhookResponseRequest): Promise<Models.WebhookResponse> {
  const response = await this.client.request<Models.WebhookResponse>('POST', `/payments/webhooks/${provider}/`, { body: data });
  return response;
}

  /**
 * Webhook Health Check
 * 
 * Check webhook service health status and recent activity metrics
 */
async paymentsWebhooksHealthRetrieve(): Promise<Models.WebhookHealth> {
  const response = await this.client.request<Models.WebhookHealth>('GET', "/payments/webhooks/health/");
  return response;
}

  /**
 * Supported Webhook Providers
 * 
 * Get list of supported webhook providers with configuration details
 */
async paymentsWebhooksProvidersRetrieve(): Promise<Models.SupportedProviders> {
  const response = await this.client.request<Models.SupportedProviders>('GET', "/payments/webhooks/providers/");
  return response;
}

  /**
 * Webhook Statistics
 * 
 * Get webhook processing statistics for a given time period
 */
async paymentsWebhooksStatsRetrieve(days?: number | null): Promise<Models.WebhookStats> {
  const response = await this.client.request<Models.WebhookStats>('GET', "/payments/webhooks/stats/", { params: { days } });
  return response;
}

}