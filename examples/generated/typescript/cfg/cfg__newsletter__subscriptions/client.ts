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
    const response = await this.client.request('POST', "/django_cfg_newsletter/subscribe/", { body: data });
    return response;
  }

  async list(page?: number, page_size?: number): Promise<Models.PaginatedNewsletterSubscriptionList[]>;
  async list(params?: { page?: number; page_size?: number }): Promise<Models.PaginatedNewsletterSubscriptionList[]>;

  /**
   * List User Subscriptions
   * 
   * Get a list of current user's active newsletter subscriptions.
   */
  async list(...args: any[]): Promise<Models.PaginatedNewsletterSubscriptionList[]> {
    const isParamsObject = args.length === 1 && typeof args[0] === 'object' && args[0] !== null && !Array.isArray(args[0]);
    
    let params;
    if (isParamsObject) {
      params = args[0];
    } else {
      params = { page: args[0], page_size: args[1] };
    }
    const response = await this.client.request('GET', "/django_cfg_newsletter/subscriptions/", { params });
    return (response as any).results || [];
  }

  /**
   * Unsubscribe from Newsletter
   * 
   * Unsubscribe from a newsletter using subscription ID.
   */
  async unsubscribeCreate(data: Models.UnsubscribeRequest): Promise<Models.SuccessResponse> {
    const response = await this.client.request('POST', "/django_cfg_newsletter/unsubscribe/", { body: data });
    return response;
  }

}