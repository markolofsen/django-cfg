import * as Models from "./models";


/**
 * API endpoints for Newsletters.
 */
export class CfgNewslettersAPI {
  private client: any;

  constructor(client: any) {
    this.client = client;
  }

  async list(page?: number, page_size?: number): Promise<Models.PaginatedNewsletterList[]>;
  async list(params?: { page?: number; page_size?: number }): Promise<Models.PaginatedNewsletterList[]>;

  /**
   * List Active Newsletters
   * 
   * Get a list of all active newsletters available for subscription.
   */
  async list(...args: any[]): Promise<Models.PaginatedNewsletterList[]> {
    const isParamsObject = args.length === 1 && typeof args[0] === 'object' && args[0] !== null && !Array.isArray(args[0]);
    
    let params;
    if (isParamsObject) {
      params = args[0];
    } else {
      params = { page: args[0], page_size: args[1] };
    }
    const response = await this.client.request('GET', "/django_cfg_newsletter/newsletters/", { params });
    return (response as any).results || [];
  }

  /**
   * Get Newsletter Details
   * 
   * Retrieve details of a specific newsletter.
   */
  async retrieve(id: number): Promise<Models.Newsletter> {
    const response = await this.client.request('GET', `/django_cfg_newsletter/newsletters/${id}/`);
    return response;
  }

}