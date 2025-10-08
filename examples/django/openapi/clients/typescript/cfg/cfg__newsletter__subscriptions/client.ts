import * as Models from "./models";


/**
 * API endpoints for Subscriptions.
 */
export class CfgSubscriptionsAPI {
  private client: any;

  constructor(client: any) {
    this.client = client;
  }

  /**
 * Subscribe to Newsletter
 * 
 * Subscribe an email address to a newsletter.
 */
async subscribeCreate(data: Models.SubscribeRequest): Promise<Models.SubscribeResponse> {
  const response = await this.client.request<Models.SubscribeResponse>('POST', "/django_cfg_newsletter/subscribe/", { body: data });
  return response;
}

  /**
 * List User Subscriptions
 * 
 * Get a list of current user's active newsletter subscriptions.
 */
async list(page?: number | null, page_size?: number | null): Promise<Models.PaginatedNewsletterSubscriptionList[]> {
  const response = await this.client.request<Models.PaginatedNewsletterSubscriptionList[]>('GET', "/django_cfg_newsletter/subscriptions/", { params: { page, page_size } });
  return (response as any).results || [];
}

  /**
 * Unsubscribe from Newsletter
 * 
 * Unsubscribe from a newsletter using subscription ID.
 */
async unsubscribeCreate(data: Models.UnsubscribeRequest): Promise<Models.SuccessResponse> {
  const response = await this.client.request<Models.SuccessResponse>('POST', "/django_cfg_newsletter/unsubscribe/", { body: data });
  return response;
}

}