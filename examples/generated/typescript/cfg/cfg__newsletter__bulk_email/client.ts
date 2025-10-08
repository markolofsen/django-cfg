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
  async bulkCreate(data: Models.BulkEmailRequest): Promise<Models.BulkEmailResponse> {
    const response = await this.client.request('POST', "/django_cfg_newsletter/bulk/", { body: data });
    return response;
  }

}