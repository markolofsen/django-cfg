import * as Models from "./models";


/**
 * API endpoints for Bulk Email.
 */
export class CfgBulkEmailAPI {
  private client: any;

  constructor(client: any) {
    this.client = client;
  }

  /**
   * Send Bulk Email
   * 
   * Send bulk emails to multiple recipients using base email template.
   */
  async cfgNewsletterBulkCreate(data: Models.BulkEmailRequest): Promise<Models.BulkEmailResponse> {
    const response = await this.client.request('POST', "/cfg/newsletter/bulk/", { body: data });
    return response;
  }

}