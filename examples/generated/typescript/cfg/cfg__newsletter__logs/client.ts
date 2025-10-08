import * as Models from "./models";


/**
 * API endpoints for Logs.
 */
export class CfgLogsAPI {
  private client: any;

  constructor(client: any) {
    this.client = client;
  }

  async list(page?: number, page_size?: number): Promise<Models.PaginatedEmailLogList[]>;
  async list(params?: { page?: number; page_size?: number }): Promise<Models.PaginatedEmailLogList[]>;

  /**
   * List Email Logs
   * 
   * Get a list of email sending logs.
   */
  async list(...args: any[]): Promise<Models.PaginatedEmailLogList[]> {
    const isParamsObject = args.length === 1 && typeof args[0] === 'object' && args[0] !== null && !Array.isArray(args[0]);
    
    let params;
    if (isParamsObject) {
      params = args[0];
    } else {
      params = { page: args[0], page_size: args[1] };
    }
    const response = await this.client.request('GET', "/django_cfg_newsletter/logs/", { params });
    return (response as any).results || [];
  }

}