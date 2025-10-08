import * as Models from "./models";


/**
 * API endpoints for Logs.
 */
export class CfgLogsAPI {
  private client: any;

  constructor(client: any) {
    this.client = client;
  }

  /**
 * List Email Logs
 * 
 * Get a list of email sending logs.
 */
async list(page?: number | null, page_size?: number | null): Promise<Models.PaginatedEmailLogList[]> {
  const response = await this.client.request<Models.PaginatedEmailLogList[]>('GET', "/django_cfg_newsletter/logs/", { params: { page, page_size } });
  return (response as any).results || [];
}

}