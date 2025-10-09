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
  async cfgNewsletterSubscribeCreate(data: Models.SubscribeRequest): Promise<Models.SubscribeResponse> {
    const response = await this.client.request('POST', "/cfg/newsletter/subscribe/", { body: data });
    return response;
  }

  async cfgNewsletterSubscriptionsList(page?: number, page_size?: number): Promise<Models.PaginatedNewsletterSubscriptionList[]>;
  async cfgNewsletterSubscriptionsList(params?: { page?: number; page_size?: number }): Promise<Models.PaginatedNewsletterSubscriptionList[]>;

  /**
   * List User Subscriptions
   * 
   * Get a list of current user's active newsletter subscriptions.
   */
  async cfgNewsletterSubscriptionsList(...args: any[]): Promise<Models.PaginatedNewsletterSubscriptionList[]> {
    const isParamsObject = args.length === 1 && typeof args[0] === 'object' && args[0] !== null && !Array.isArray(args[0]);
    
    let params;
    if (isParamsObject) {
      params = args[0];
    } else {
      params = { page: args[0], page_size: args[1] };
    }
    const response = await this.client.request('GET', "/cfg/newsletter/subscriptions/", { params });
    return (response as any).results || [];
  }

  /**
   * Unsubscribe from Newsletter
   * 
   * Unsubscribe from a newsletter using subscription ID.
   */
  async cfgNewsletterUnsubscribeCreate(data: Models.UnsubscribeRequest): Promise<Models.SuccessResponse> {
    const response = await this.client.request('POST', "/cfg/newsletter/unsubscribe/", { body: data });
    return response;
  }

}