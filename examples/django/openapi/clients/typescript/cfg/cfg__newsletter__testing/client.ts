import * as Models from "./models";


/**
 * API endpoints for Testing.
 */
export class CfgTestingAPI {
  private client: any;

  constructor(client: any) {
    this.client = client;
  }

  /**
 * Test Email Sending
 * 
 * Send a test email to verify mailer configuration.
 */
async testCreate(data: Models.TestEmailRequest): Promise<Models.BulkEmailResponse> {
  const response = await this.client.request<Models.BulkEmailResponse>('POST', "/django_cfg_newsletter/test/", { body: data });
  return response;
}

}